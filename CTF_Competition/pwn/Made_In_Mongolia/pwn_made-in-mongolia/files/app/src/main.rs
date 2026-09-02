use std::net::SocketAddr;

use runner::RunnerClient;

mod runner;
mod waf;
mod web;

#[tokio::main]
async fn main() {
    init_logging();

    if std::env::args().any(|argument| argument == "--healthcheck") {
        match web::healthcheck("127.0.0.1:3000").await {
            Ok(()) => return,
            Err(error) => {
                eprintln!("healthcheck failed: {error}");
                std::process::exit(1);
            }
        }
    }

    let runner_address =
        std::env::var("RUNNER_ADDRESS").unwrap_or_else(|_| "runner:5000".to_owned());
    let runner = RunnerClient::new(runner_address);

    let http_address = env_address("HTTP_LISTEN_ADDRESS", "0.0.0.0:3000");
    let trusted_proxy_count = env_usize("TRUSTED_PROXY_COUNT", 0);
    web::serve(http_address, runner, trusted_proxy_count)
        .await
        .expect("HTTP server stopped unexpectedly");
}

fn init_logging() {
    let subscriber = tracing_logfmt::builder()
        .with_target(false)
        .with_span_name(false)
        .with_span_path(false)
        .subscriber_builder()
        .finish();
    tracing::subscriber::set_global_default(subscriber)
        .expect("global logging subscriber has already been set");
}

fn env_address(name: &str, default: &str) -> SocketAddr {
    std::env::var(name)
        .unwrap_or_else(|_| default.to_owned())
        .parse()
        .unwrap_or_else(|_| panic!("{name} must be a numeric socket address"))
}

fn env_usize(name: &str, default: usize) -> usize {
    match std::env::var(name) {
        Ok(value) => value
            .parse()
            .unwrap_or_else(|_| panic!("{name} must be a non-negative integer")),
        Err(std::env::VarError::NotPresent) => default,
        Err(std::env::VarError::NotUnicode(_)) => panic!("{name} must be valid UTF-8"),
    }
}
