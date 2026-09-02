use std::{io, sync::Arc};

use tokio::{
    io::{AsyncReadExt, AsyncWriteExt},
    net::TcpStream,
};

const RUN_REQUEST_MAGIC: &[u8; 4] = b"MIR2";
const RUN_RESPONSE_MAGIC: &[u8; 4] = b"MIO2";
const NO_EXIT_CODE: i32 = i32::MIN;

#[derive(Debug)]
pub(crate) struct RunResponse {
    pub(crate) stdout: Vec<u8>,
    pub(crate) stderr: Vec<u8>,
    pub(crate) exit_code: Option<i32>,
    pub(crate) duration_ms: u64,
}

#[derive(Clone)]
pub(crate) struct RunnerClient {
    address: Arc<str>,
}

impl RunnerClient {
    pub(crate) fn new(address: String) -> Self {
        Self {
            address: Arc::from(address),
        }
    }

    pub(crate) async fn run(&self, code: String) -> io::Result<RunResponse> {
        let code = code.into_bytes();
        let code_length =
            u64::try_from(code.len()).map_err(|_| io::Error::other("source cannot be framed"))?;

        let mut stream = TcpStream::connect(self.address.as_ref()).await?;
        stream.write_all(RUN_REQUEST_MAGIC).await?;
        stream.write_all(&code_length.to_be_bytes()).await?;
        stream.write_all(&code).await?;

        let mut header = [0_u8; 32];
        stream.read_exact(&mut header).await?;
        if &header[..4] != RUN_RESPONSE_MAGIC {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                "invalid runner response",
            ));
        }

        let exit_code = i32::from_be_bytes(header[4..8].try_into().expect("fixed-width slice"));
        let duration_ms = u64::from_be_bytes(header[8..16].try_into().expect("fixed-width slice"));
        let stdout_length = frame_length(&header[16..24])?;
        let stderr_length = frame_length(&header[24..32])?;

        let mut stdout = vec![0_u8; stdout_length];
        let mut stderr = vec![0_u8; stderr_length];
        stream.read_exact(&mut stdout).await?;
        stream.read_exact(&mut stderr).await?;

        Ok(RunResponse {
            stdout,
            stderr,
            exit_code: (exit_code != NO_EXIT_CODE).then_some(exit_code),
            duration_ms,
        })
    }
}

fn frame_length(bytes: &[u8]) -> io::Result<usize> {
    usize::try_from(u64::from_be_bytes(
        bytes.try_into().expect("fixed-width slice"),
    ))
    .map_err(|_| io::Error::new(io::ErrorKind::InvalidData, "frame is too large"))
}
