use std::io::{self, Read, Write};

pub const FLAG_SOCKET: &str = "/run/my-avatar-flag/S.flag";
pub const REQUEST_MAGIC: &[u8; 4] = b"MAF1";
pub const MAX_FLAG_BYTES: usize = 4096;

pub fn write_request(stream: &mut impl Write) -> io::Result<()> {
    stream.write_all(REQUEST_MAGIC)?;
    stream.flush()
}

pub fn read_request(stream: &mut impl Read) -> io::Result<()> {
    let mut request = [0_u8; REQUEST_MAGIC.len()];
    stream.read_exact(&mut request)?;
    if &request != REQUEST_MAGIC {
        return Err(io::Error::new(
            io::ErrorKind::InvalidData,
            "invalid flag request magic",
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::{read_request, write_request};

    #[test]
    fn request_round_trip() {
        let mut request = Vec::new();
        write_request(&mut request).unwrap();
        assert!(read_request(&mut request.as_slice()).is_ok());
    }

    #[test]
    fn rejects_invalid_magic() {
        let mut request = b"NOPE".as_slice();
        assert!(read_request(&mut request).is_err());
    }
}
