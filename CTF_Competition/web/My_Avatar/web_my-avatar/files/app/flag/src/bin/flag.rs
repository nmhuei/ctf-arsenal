use std::{
    error::Error,
    io::{self, Read, Write},
    os::unix::net::UnixStream,
    process,
    time::Duration,
};

use my_avatar_flag_protocol::{write_request, FLAG_SOCKET, MAX_FLAG_BYTES};

fn request_flag() -> Result<(), Box<dyn Error>> {
    let mut stream = UnixStream::connect(FLAG_SOCKET)?;
    stream.set_read_timeout(Some(Duration::from_secs(4)))?;
    stream.set_write_timeout(Some(Duration::from_secs(4)))?;
    write_request(&mut stream)?;

    let mut response = Vec::new();
    stream
        .take(MAX_FLAG_BYTES as u64 + 1)
        .read_to_end(&mut response)?;
    if response.is_empty() {
        return Err("flag service returned an empty response".into());
    }
    if response.len() > MAX_FLAG_BYTES {
        return Err("flag service response exceeded its limit".into());
    }
    io::stdout().lock().write_all(&response)?;
    Ok(())
}

fn main() {
    if request_flag().is_err() {
        process::exit(1);
    }
}
