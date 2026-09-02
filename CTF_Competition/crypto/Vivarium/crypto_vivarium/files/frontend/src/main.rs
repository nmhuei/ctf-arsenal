use axum::{
    Json, Router,
    extract::{DefaultBodyLimit, State},
    http::{HeaderMap, HeaderValue, StatusCode, header},
    response::{Html, IntoResponse, Response},
    routing::{get, post},
};
use serde::{Deserialize, Serialize};

#[derive(Clone)]
struct AppState {
    client: reqwest::Client,
    executor_url: String,
}

#[derive(Deserialize, Serialize)]
struct RunRequest {
    code: String,
}

#[derive(Serialize)]
struct ApiError {
    error: String,
}

#[tokio::main]
async fn main() {
    let bind_addr = std::env::var("BIND_ADDR").unwrap_or_else(|_| "0.0.0.0:8080".into());
    let state = AppState {
        client: reqwest::Client::new(),
        executor_url: std::env::var("EXECUTOR_URL")
            .unwrap_or_else(|_| "http://python-executor:8081/api/run".into()),
    };
    let router = Router::new()
        .route("/", get(index))
        .route("/styles.css", get(styles))
        .route("/app.js", get(javascript))
        .route("/health", get(health))
        .route("/api/run", post(run_python))
        .layer(DefaultBodyLimit::disable())
        .with_state(state);

    let listener = tokio::net::TcpListener::bind(&bind_addr)
        .await
        .unwrap_or_else(|error| panic!("could not bind to {bind_addr}: {error}"));

    axum::serve(listener, router)
        .with_graceful_shutdown(shutdown_signal())
        .await
        .expect("HTTP server stopped unexpectedly");
}

async fn shutdown_signal() {
    let ctrl_c = async {
        tokio::signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };
    let terminate = async {
        tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())
            .expect("failed to install SIGTERM handler")
            .recv()
            .await;
    };

    tokio::select! {
        _ = ctrl_c => {}
        _ = terminate => {}
    }
}

async fn index() -> Response {
    with_security_headers(Html(include_str!("../web/index.html")).into_response())
}

async fn styles() -> Response {
    with_security_headers(
        (
            [(header::CONTENT_TYPE, "text/css; charset=utf-8")],
            include_str!("../web/styles.css"),
        )
            .into_response(),
    )
}

async fn javascript() -> Response {
    with_security_headers(
        (
            [(header::CONTENT_TYPE, "text/javascript; charset=utf-8")],
            include_str!("../web/app.js"),
        )
            .into_response(),
    )
}

async fn health() -> impl IntoResponse {
    (StatusCode::OK, "ok")
}

async fn run_python(State(state): State<AppState>, Json(request): Json<RunRequest>) -> Response {
    if request.code.trim().is_empty() {
        return api_error(StatusCode::BAD_REQUEST, "Python source is empty");
    }

    let executor_response = match state
        .client
        .post(&state.executor_url)
        .json(&request)
        .send()
        .await
    {
        Ok(response) => response,
        Err(_) => {
            return api_error(
                StatusCode::SERVICE_UNAVAILABLE,
                "The Python executor is unavailable",
            );
        }
    };

    let status = executor_response.status();
    let payload = match executor_response.bytes().await {
        Ok(payload) => payload,
        Err(_) => {
            return api_error(
                StatusCode::BAD_GATEWAY,
                "The Python executor returned an incomplete response",
            );
        }
    };

    with_security_headers(
        (
            status,
            [(header::CONTENT_TYPE, "application/json")],
            payload,
        )
            .into_response(),
    )
}

fn api_error(status: StatusCode, message: &str) -> Response {
    with_security_headers(
        (
            status,
            Json(ApiError {
                error: message.into(),
            }),
        )
            .into_response(),
    )
}

fn with_security_headers(mut response: Response) -> Response {
    let headers: &mut HeaderMap = response.headers_mut();
    headers.insert(
        header::CONTENT_SECURITY_POLICY,
        HeaderValue::from_static(
            "default-src 'none'; style-src 'self'; script-src 'self'; \
             connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'",
        ),
    );
    headers.insert(
        header::X_CONTENT_TYPE_OPTIONS,
        HeaderValue::from_static("nosniff"),
    );
    headers.insert(
        header::REFERRER_POLICY,
        HeaderValue::from_static("no-referrer"),
    );
    response
}
