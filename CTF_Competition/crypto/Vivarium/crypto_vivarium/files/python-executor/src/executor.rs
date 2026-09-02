use std::{io, os::unix::process::ExitStatusExt, process::Stdio, time::Instant};

use tokio::{io::AsyncWriteExt, process::Command};

use crate::RunResponse;

const PYTHON_TASK_EXECUTOR: &str = concat!(
    include_str!("../sandbox/n8n_security.py"),
    "\n",
    include_str!("../sandbox/task_executor.py")
);

pub(crate) async fn execute_python(source: String) -> io::Result<RunResponse> {
    let python = std::env::var("PYTHON_BIN").unwrap_or_else(|_| "python3".into());
    let started = Instant::now();

    let mut child = Command::new(python)
        .args(["-I", "-S", "-B", "-c", PYTHON_TASK_EXECUTOR])
        .current_dir("/tmp")
        .env("PYTHONDONTWRITEBYTECODE", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;

    let mut stdin = child.stdin.take().expect("stdin was piped");
    let input_task = tokio::spawn(async move {
        stdin.write_all(source.as_bytes()).await?;
        stdin.shutdown().await
    });
    let output = child.wait_with_output().await?;
    input_task.await.map_err(io::Error::other)??;

    Ok(RunResponse {
        stdout: String::from_utf8_lossy(&output.stdout).into_owned(),
        stderr: String::from_utf8_lossy(&output.stderr).into_owned(),
        exit_code: output.status.code(),
        signal: output.status.signal(),
        timed_out: false,
        truncated: false,
        duration_ms: started.elapsed().as_millis(),
    })
}

#[cfg(test)]
mod tests {
    use super::execute_python;

    #[tokio::test]
    async fn executes_allowed_python() {
        let result = execute_python("print([n * n for n in range(1, 4)])".into())
            .await
            .expect("executor should start");
        assert_eq!(result.exit_code, Some(0), "{result:?}");
        assert_eq!(result.stdout, "[1, 4, 9]\n");
    }

    #[tokio::test]
    async fn blocks_standard_library_imports() {
        let result = execute_python("import math\nprint(math.sqrt(4))".into())
            .await
            .expect("executor should start");
        assert_ne!(result.exit_code, Some(0), "{result:?}");
        assert!(result.stderr.contains("SecurityViolationError"));
    }
}
