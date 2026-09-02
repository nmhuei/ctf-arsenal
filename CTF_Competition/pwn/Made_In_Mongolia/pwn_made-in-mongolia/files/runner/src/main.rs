use std::{
    fs::{self, OpenOptions},
    io::{self, Read, Write},
    path::{Path, PathBuf},
    process::{Command, ExitStatus, Stdio},
    thread,
    time::Instant,
};

const SFEX_BINARY: &str = "/usr/local/bin/sfex";
const RUN_REQUEST_MAGIC: &[u8; 4] = b"MIR2";
const RUN_RESPONSE_MAGIC: &[u8; 4] = b"MIO2";
const NO_EXIT_CODE: i32 = i32::MIN;
const MAX_SOURCE_BYTES: usize = 12 * 1024;

struct RunResponse {
    stdout: Vec<u8>,
    stderr: Vec<u8>,
    exit_code: Option<i32>,
    duration_ms: u64,
}

fn main() {
    let response = match run(io::stdin()) {
        Ok(response) => response,
        Err(error) => RunResponse {
            stdout: Vec::new(),
            stderr: format!("[runner] {error}\n").into_bytes(),
            exit_code: None,
            duration_ms: 0,
        },
    };
    let _ = write_response(io::stdout().lock(), &response);
}

fn run(mut input: impl Read) -> io::Result<RunResponse> {
    let mut header = [0_u8; 12];
    input.read_exact(&mut header)?;
    if &header[..4] != RUN_REQUEST_MAGIC {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "invalid run request",
        ));
    }

    let source_length = usize::try_from(u64::from_be_bytes(
        header[4..12].try_into().expect("fixed-width slice"),
    ))
    .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "source is too large"))?;
    if source_length == 0 || source_length > MAX_SOURCE_BYTES {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "invalid source length",
        ));
    }

    let mut source = vec![0_u8; source_length];
    input.read_exact(&mut source)?;
    let source_file = SourceFile::create(&source)?;
    execute(source_file.path())
}

fn execute(source_path: &Path) -> io::Result<RunResponse> {
    let started = Instant::now();
    let mut child = Command::new(SFEX_BINARY)
        .arg("run")
        .arg(source_path)
        .current_dir("/tmp")
        .stdin(Stdio::null())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;

    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| io::Error::other("stdout pipe unavailable"))?;
    let stderr = child
        .stderr
        .take()
        .ok_or_else(|| io::Error::other("stderr pipe unavailable"))?;
    let stdout_thread = thread::spawn(move || read_stream(stdout));
    let stderr_thread = thread::spawn(move || read_stream(stderr));

    let status = child.wait()?;
    let stdout = join_reader(stdout_thread)?;
    let stderr = join_reader(stderr_thread)?;

    Ok(RunResponse {
        stdout: strip_sfex_banner(stdout),
        stderr,
        exit_code: exit_code(status),
        duration_ms: started.elapsed().as_millis().try_into().unwrap_or(u64::MAX),
    })
}

fn write_response(mut output: impl Write, response: &RunResponse) -> io::Result<()> {
    let stdout_length =
        u64::try_from(response.stdout.len()).map_err(|_| io::Error::other("stdout too large"))?;
    let stderr_length =
        u64::try_from(response.stderr.len()).map_err(|_| io::Error::other("stderr too large"))?;

    output.write_all(RUN_RESPONSE_MAGIC)?;
    output.write_all(&response.exit_code.unwrap_or(NO_EXIT_CODE).to_be_bytes())?;
    output.write_all(&response.duration_ms.to_be_bytes())?;
    output.write_all(&stdout_length.to_be_bytes())?;
    output.write_all(&stderr_length.to_be_bytes())?;
    output.write_all(&response.stdout)?;
    output.write_all(&response.stderr)?;
    output.flush()
}

fn read_stream(mut stream: impl Read) -> io::Result<Vec<u8>> {
    let mut captured = Vec::new();
    stream.read_to_end(&mut captured)?;
    Ok(captured)
}

fn join_reader(handle: thread::JoinHandle<io::Result<Vec<u8>>>) -> io::Result<Vec<u8>> {
    handle
        .join()
        .map_err(|_| io::Error::other("output reader panicked"))?
}

fn strip_sfex_banner(stdout: Vec<u8>) -> Vec<u8> {
    const PREFIX: &[u8] = b"Running SFX script: ";
    let Some(remainder) = stdout.strip_prefix(PREFIX) else {
        return stdout;
    };
    let Some(line_end) = remainder.iter().position(|byte| *byte == b'\n') else {
        return stdout;
    };
    let output = &remainder[line_end + 1..];
    output.strip_prefix(b"\n").unwrap_or(output).to_vec()
}

fn exit_code(status: ExitStatus) -> Option<i32> {
    use std::os::unix::process::ExitStatusExt;
    status
        .code()
        .or_else(|| status.signal().map(|signal| 128 + signal))
}

struct SourceFile(PathBuf);

impl SourceFile {
    fn create(code: &[u8]) -> io::Result<Self> {
        let path = PathBuf::from(format!("/tmp/source-{}.sfex", std::process::id()));
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .open(&path)?;
        file.write_all(code)?;
        file.flush()?;
        Ok(Self(path))
    }

    fn path(&self) -> &Path {
        &self.0
    }
}

impl Drop for SourceFile {
    fn drop(&mut self) {
        let _ = fs::remove_file(&self.0);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn removes_sfex_path_banner_and_blank_line() {
        let stdout = b"Running SFX script: /tmp/source.sfex\n\nhello\n".to_vec();
        assert_eq!(strip_sfex_banner(stdout), b"hello\n");
    }

    #[test]
    fn rejects_source_over_limit_before_reading_body() {
        let mut frame = RUN_REQUEST_MAGIC.to_vec();
        frame.extend_from_slice(&((MAX_SOURCE_BYTES + 1) as u64).to_be_bytes());

        let error = match run(frame.as_slice()) {
            Ok(_) => panic!("oversized source was accepted"),
            Err(error) => error,
        };
        assert_eq!(error.kind(), io::ErrorKind::InvalidData);
    }
}
