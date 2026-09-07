use impossible_player::*;
use std::io::{Read, Write};
use std::net::{Shutdown, TcpStream};

const REMOTE: &str = "127.0.0.1:31337";

fn submit(proof: Proof) -> std::io::Result<String> {
    let payload = encode_proof(&proof);
    let mut stream = TcpStream::connect(REMOTE)?;
    stream.write_all(payload.as_bytes())?;
    stream.write_all(b"\n")?;
    stream.shutdown(Shutdown::Write)?;
    let mut response = String::new();
    stream.read_to_string(&mut response)?;
    Ok(response)
}

fn main() {
    let _target_claim = CLAIM;
    let _submit = submit;
}
