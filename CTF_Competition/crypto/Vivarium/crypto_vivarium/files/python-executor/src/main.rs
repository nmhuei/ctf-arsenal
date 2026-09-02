mod executor;

use axum::{
    Json, Router,
    extract::DefaultBodyLimit,
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
};
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
struct RunRequest {
    code: String,
}

#[derive(Debug, Serialize)]
pub(crate) struct RunResponse {
    stdout: String,
    stderr: String,
    exit_code: Option<i32>,
    signal: Option<i32>,
    timed_out: bool,
    truncated: bool,
    duration_ms: u128,
}

#[derive(Serialize)]
struct ApiError {
    error: String,
}

#[tokio::main]
async fn main() {
    let router = Router::new()
        .route("/health", get(health))
        .route("/api/run", post(run_python))
        .layer(DefaultBodyLimit::disable());
    let listener = tokio::net::TcpListener::bind("0.0.0.0:8081")
        .await
        .expect("could not bind executor HTTP listener");
    axum::serve(listener, router)
        .await
        .expect("executor HTTP server stopped unexpectedly");
}

async fn health() -> impl IntoResponse {
    (StatusCode::OK, "ok")
}

async fn run_python(
    Json(request): Json<RunRequest>,
) -> Result<Json<RunResponse>, (StatusCode, Json<ApiError>)> {
    executor::execute_python(request.code)
        .await
        .map(Json)
        .map_err(|error| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(ApiError {
                    error: error.to_string(),
                }),
            )
        })
}
