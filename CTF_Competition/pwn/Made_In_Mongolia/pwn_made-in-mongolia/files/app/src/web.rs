use std::{
    io,
    net::{IpAddr, SocketAddr},
};

use axum::{
    Json, Router,
    body::Body,
    extract::{ConnectInfo, DefaultBodyLimit, State},
    http::{HeaderMap, StatusCode, header},
    response::{IntoResponse, Response},
    routing::{get, post},
};
use serde::{Deserialize, Serialize};
use tokio::net::{TcpListener, TcpStream};

use crate::{
    runner::{RunResponse, RunnerClient},
    waf,
};

const MAX_SOURCE_BYTES: usize = 12 * 1024;

#[derive(Clone)]
struct WebState {
    runner: RunnerClient,
    trusted_proxy_count: usize,
}

#[derive(Deserialize)]
struct ApiRunRequest {
    code: String,
}

#[derive(Serialize)]
struct ApiRunResponse {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
    duration_ms: u64,
}

#[derive(Serialize)]
struct ErrorResponse {
    error: String,
}

pub(crate) async fn serve(
    http_address: SocketAddr,
    runner: RunnerClient,
    trusted_proxy_count: usize,
) -> io::Result<()> {
    let state = WebState {
        runner,
        trusted_proxy_count,
    };
    let app = Router::new()
        .route("/", get(index))
        .route("/assets/app.css", get(styles))
        .route("/assets/app.js", get(script))
        .route("/healthz", get(health))
        .route("/api/run", post(run))
        .layer(DefaultBodyLimit::max(MAX_SOURCE_BYTES + 1024))
        .with_state(state);

    let listener = TcpListener::bind(http_address).await?;
    tracing::info!(
        event = "server_started",
        http_address = %http_address,
        trusted_proxy_count,
    );
    axum::serve(
        listener,
        app.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .await
}

pub(crate) async fn healthcheck(address: &str) -> io::Result<()> {
    TcpStream::connect(address).await.map(|_| ())
}

async fn index() -> Response {
    static_response(
        "text/html; charset=utf-8",
        include_str!("../static/index.html"),
    )
}

async fn styles() -> Response {
    static_response("text/css; charset=utf-8", include_str!("../static/app.css"))
}

async fn script() -> Response {
    static_response(
        "application/javascript; charset=utf-8",
        include_str!("../static/app.js"),
    )
}

async fn health() -> &'static str {
    "ok"
}

fn static_response(content_type: &'static str, content: &'static str) -> Response {
    ([(header::CONTENT_TYPE, content_type)], Body::from(content)).into_response()
}

async fn run(
    ConnectInfo(peer_address): ConnectInfo<SocketAddr>,
    State(state): State<WebState>,
    headers: HeaderMap,
    Json(request): Json<ApiRunRequest>,
) -> Result<Json<ApiRunResponse>, (StatusCode, Json<ErrorResponse>)> {
    validate_request(&request)?;

    let caller_ip = match resolve_caller_ip(peer_address.ip(), &headers, state.trusted_proxy_count)
    {
        Ok(caller_ip) => caller_ip,
        Err(error) => {
            tracing::warn!(
                event = "caller_ip_resolution_failed",
                peer_ip = %peer_address.ip(),
                trusted_proxy_count = state.trusted_proxy_count,
                error,
            );
            peer_address.ip()
        }
    };

    log_run_started(caller_ip, &request.code);
    match state.runner.run(request.code).await {
        Ok(result) => {
            log_run_finished(&result);
            Ok(Json(ApiRunResponse::from(result)))
        }
        Err(error) => {
            tracing::error!(event = "runner_failed", error = %error);
            Err(api_error(
                StatusCode::BAD_GATEWAY,
                "The runner could not complete the execution.",
            ))
        }
    }
}

fn validate_request(request: &ApiRunRequest) -> Result<(), (StatusCode, Json<ErrorResponse>)> {
    if request.code.trim().is_empty() {
        return Err(api_error(StatusCode::BAD_REQUEST, "Code cannot be empty."));
    }
    if request.code.len() > MAX_SOURCE_BYTES {
        return Err(api_error(
            StatusCode::PAYLOAD_TOO_LARGE,
            "Code exceeds the 12 KiB limit.",
        ));
    }
    if let Err(violation) = waf::inspect(&request.code) {
        return Err(api_error(
            StatusCode::UNPROCESSABLE_ENTITY,
            &violation.to_string(),
        ));
    }
    Ok(())
}

fn api_error(status: StatusCode, message: &str) -> (StatusCode, Json<ErrorResponse>) {
    (
        status,
        Json(ErrorResponse {
            error: message.to_owned(),
        }),
    )
}

fn log_run_started(caller_ip: IpAddr, code: &str) {
    tracing::info!(
        event = "run_started",
        caller_ip = %caller_ip,
        source_bytes = code.len(),
        code,
    );
}

fn log_run_finished(result: &RunResponse) {
    tracing::info!(
        event = "run_finished",
        exit_code = result.exit_code.unwrap_or(-1),
        duration_ms = result.duration_ms,
        stdout = %String::from_utf8_lossy(&result.stdout),
        stderr = %String::from_utf8_lossy(&result.stderr),
    );
}

fn resolve_caller_ip(
    peer_ip: IpAddr,
    headers: &HeaderMap,
    trusted_proxy_count: usize,
) -> Result<IpAddr, &'static str> {
    if trusted_proxy_count == 0 {
        return Ok(peer_ip);
    }

    let forwarded_values = headers
        .get_all("x-forwarded-for")
        .iter()
        .map(|value| {
            value
                .to_str()
                .map_err(|_| "X-Forwarded-For is not valid ASCII")
        })
        .collect::<Result<Vec<_>, _>>()?;
    let forwarded_hops = forwarded_values
        .iter()
        .flat_map(|value| value.split(',').map(str::trim))
        .collect::<Vec<_>>();
    let caller = forwarded_hops
        .iter()
        .rev()
        .nth(trusted_proxy_count - 1)
        .ok_or("X-Forwarded-For has fewer entries than TRUSTED_PROXY_COUNT")?;

    caller
        .parse()
        .map_err(|_| "selected X-Forwarded-For entry is not an IP address")
}

impl From<RunResponse> for ApiRunResponse {
    fn from(result: RunResponse) -> Self {
        Self {
            stdout: String::from_utf8_lossy(&result.stdout).into_owned(),
            stderr: String::from_utf8_lossy(&result.stderr).into_owned(),
            exit_code: result.exit_code,
            duration_ms: result.duration_ms,
        }
    }
}

#[cfg(test)]
mod tests {
    use std::{
        io::{self, Write},
        sync::{Arc, Mutex},
    };

    use super::*;

    struct SharedWriter(Arc<Mutex<Vec<u8>>>);

    impl Write for SharedWriter {
        fn write(&mut self, buffer: &[u8]) -> io::Result<usize> {
            std::io::Write::write(&mut *self.0.lock().unwrap(), buffer)
        }

        fn flush(&mut self) -> io::Result<()> {
            Ok(())
        }
    }

    fn capture_logs(action: impl FnOnce()) -> String {
        let output = Arc::new(Mutex::new(Vec::new()));
        let writer = Arc::clone(&output);
        let subscriber = tracing_logfmt::builder()
            .with_timestamp(false)
            .with_target(false)
            .with_span_name(false)
            .with_span_path(false)
            .subscriber_builder()
            .with_writer(move || SharedWriter(Arc::clone(&writer)))
            .finish();

        tracing::subscriber::with_default(subscriber, action);
        let bytes = output.lock().unwrap().clone();
        String::from_utf8(bytes).unwrap()
    }

    #[test]
    fn run_started_log_includes_caller_ip_and_newline_safe_source_code() {
        let code = "Story:\n    Print \"hello\"";
        let caller_ip = "192.0.2.42".parse().unwrap();
        let log = capture_logs(|| log_run_started(caller_ip, code));

        assert!(log.contains("event=run_started"));
        assert!(log.contains("caller_ip=192.0.2.42"));
        assert!(log.contains(&format!("source_bytes={}", code.len())));
        assert!(log.contains(r#"code="Story:\n    Print \"hello\"""#));
        assert_eq!(log.lines().count(), 1);
    }

    #[test]
    fn rejects_source_over_limit() {
        let request = ApiRunRequest {
            code: "x".repeat(MAX_SOURCE_BYTES + 1),
        };
        let (status, Json(error)) = validate_request(&request).unwrap_err();

        assert_eq!(status, StatusCode::PAYLOAD_TOO_LARGE);
        assert_eq!(error.error, "Code exceeds the 12 KiB limit.");
    }

    #[test]
    fn run_finished_log_includes_newline_safe_stdout_and_stderr() {
        let result = RunResponse {
            stdout: b"hello\nworld\n".to_vec(),
            stderr: b"warning: \"example\"\n".to_vec(),
            exit_code: Some(3),
            duration_ms: 42,
        };
        let log = capture_logs(|| log_run_finished(&result));

        assert!(log.contains("event=run_finished"));
        assert!(log.contains("exit_code=3"));
        assert!(log.contains(r#"stdout="hello\nworld\n""#));
        assert!(log.contains(r#"stderr="warning: \"example\"\n""#));
        assert_eq!(log.lines().count(), 1);
    }

    #[test]
    fn caller_ip_ignores_forwarding_headers_without_trusted_proxies() {
        let peer_ip = "192.0.2.10".parse().unwrap();
        let mut headers = HeaderMap::new();
        headers.insert("x-forwarded-for", "198.51.100.99".parse().unwrap());

        assert_eq!(resolve_caller_ip(peer_ip, &headers, 0), Ok(peer_ip));
    }

    #[test]
    fn caller_ip_walks_trusted_proxy_hops_from_the_right() {
        let peer_ip = "192.0.2.10".parse().unwrap();
        let mut headers = HeaderMap::new();
        headers.insert(
            "x-forwarded-for",
            "203.0.113.77, 198.51.100.20, 198.51.100.30"
                .parse()
                .unwrap(),
        );

        assert_eq!(
            resolve_caller_ip(peer_ip, &headers, 1),
            Ok("198.51.100.30".parse().unwrap())
        );
        assert_eq!(
            resolve_caller_ip(peer_ip, &headers, 2),
            Ok("198.51.100.20".parse().unwrap())
        );
        assert_eq!(
            resolve_caller_ip(peer_ip, &headers, 3),
            Ok("203.0.113.77".parse().unwrap())
        );
    }

    #[test]
    fn caller_ip_rejects_short_or_malformed_forwarding_chains() {
        let peer_ip = "192.0.2.10".parse().unwrap();
        let mut headers = HeaderMap::new();
        headers.insert("x-forwarded-for", "not-an-ip".parse().unwrap());

        assert!(resolve_caller_ip(peer_ip, &headers, 1).is_err());
        assert!(resolve_caller_ip(peer_ip, &headers, 2).is_err());
    }
}
