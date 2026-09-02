use std::{
    env,
    error::Error,
    fs::{self, File, OpenOptions},
    io::{self, Read, Write},
    os::unix::{
        fs::{FileTypeExt, OpenOptionsExt, PermissionsExt},
        net::{UnixListener, UnixStream},
    },
    path::Path,
    process, thread,
    time::Duration,
};

use my_avatar_flag_protocol::{read_request, FLAG_SOCKET, MAX_FLAG_BYTES};

const FLAG_TEMPLATE_PATH: &str = "/run/flag-service/template";
const ALPHABET: &[u8; 64] = b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_-";

fn store_flag_template(template: &str) -> Result<(), Box<dyn Error>> {
    if template.is_empty() {
        return Err("FLAG is empty".into());
    }
    if template.len() >= MAX_FLAG_BYTES {
        return Err("FLAG template exceeds its limit".into());
    }

    if fs::symlink_metadata(FLAG_TEMPLATE_PATH)
        .map(|metadata| metadata.file_type().is_symlink())
        .unwrap_or(false)
    {
        return Err("flag template path is a symbolic link".into());
    }

    let mut output = OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(true)
        .mode(0o400)
        .open(FLAG_TEMPLATE_PATH)?;
    output.set_permissions(fs::Permissions::from_mode(0o400))?;
    output.write_all(template.as_bytes())?;
    output.sync_all()?;
    Ok(())
}

fn random_token(random: &mut File) -> io::Result<String> {
    let mut bytes = [0_u8; 8];
    random.read_exact(&mut bytes)?;
    Ok(bytes
        .iter()
        .map(|byte| ALPHABET[(byte & 63) as usize] as char)
        .collect())
}

fn render_flag(template: &str) -> io::Result<String> {
    let mut random = File::open("/dev/urandom")?;
    let first = random_token(&mut random)?;
    let second = random_token(&mut random)?;
    Ok(template.replace("$1", &first).replace("$2", &second))
}

fn bind_flag_socket() -> Result<UnixListener, Box<dyn Error>> {
    let socket_directory = Path::new(FLAG_SOCKET)
        .parent()
        .expect("flag socket has a parent directory");
    fs::create_dir_all(socket_directory)?;
    fs::set_permissions(socket_directory, fs::Permissions::from_mode(0o755))?;

    match fs::symlink_metadata(FLAG_SOCKET) {
        Ok(metadata) if metadata.file_type().is_socket() => fs::remove_file(FLAG_SOCKET)?,
        Ok(_) => return Err("flag socket path is not a Unix socket".into()),
        Err(error) if error.kind() == io::ErrorKind::NotFound => {}
        Err(error) => return Err(error.into()),
    }

    let listener = UnixListener::bind(FLAG_SOCKET)?;
    fs::set_permissions(FLAG_SOCKET, fs::Permissions::from_mode(0o666))?;
    Ok(listener)
}

fn serve_connection(mut stream: UnixStream) -> Result<(), Box<dyn Error>> {
    stream.set_read_timeout(Some(Duration::from_secs(4)))?;
    stream.set_write_timeout(Some(Duration::from_secs(4)))?;

    read_request(&mut stream)?;
    let template = fs::read_to_string(FLAG_TEMPLATE_PATH)?;
    let flag = render_flag(&template)?;
    if flag.len() + 1 > MAX_FLAG_BYTES {
        return Err("rendered flag exceeds its limit".into());
    }

    writeln!(stream, "{flag}")?;
    Ok(())
}

fn run() -> Result<(), Box<dyn Error>> {
    let template = env::var("FLAG").map_err(|_| "FLAG is not set or is not valid UTF-8")?;
    store_flag_template(&template)?;
    env::remove_var("FLAG");
    drop(template);

    let listener = bind_flag_socket()?;
    for stream in listener.incoming().flatten() {
        thread::spawn(move || {
            let _ = serve_connection(stream);
        });
    }
    Ok(())
}

fn main() {
    if run().is_err() {
        process::exit(1);
    }
}
