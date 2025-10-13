use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::io::{self, Read};

#[derive(Debug, Deserialize)]
struct Request {
    operation: Option<String>,
    text: String,
    _parameters: Option<serde_json::Value>,
}

#[derive(Debug, Serialize)]
struct Response {
    result: String,
    stats: Stats,
}

#[derive(Debug, Serialize)]
struct Stats {
    char_count: usize,
    word_count: usize,
}

fn main() -> Result<()> {
    let mut buffer = String::new();
    io::stdin()
        .read_to_string(&mut buffer)
        .context("failed to read stdin")?;

    let request: Request = serde_json::from_str(&buffer).context("invalid request payload")?;
    let response = handle_request(request);
    let json = serde_json::to_string(&response).context("failed to serialize response")?;
    println!("{}", json);
    Ok(())
}

fn handle_request(request: Request) -> Response {
    let operation = request.operation.unwrap_or_else(|| "general".to_string());
    let text = request.text;
    let _parameters = request._parameters;
    let stats = Stats {
        char_count: text.chars().count(),
        word_count: text.split_whitespace().count(),
    };

    let result = match operation.as_str() {
        "summarize" => summarize(&text),
        "preprocess" => preprocess(&text),
        "embedding" | "tokenize" => format!("tokens:{}", stats.word_count),
        _ => default_transform(&text),
    };

    Response { result, stats }
}

fn summarize(text: &str) -> String {
    let max_len = 120;
    if text.len() <= max_len {
        text.to_string()
    } else {
        format!("{}…", &text[..max_len])
    }
}

fn preprocess(text: &str) -> String {
    text.replace('\n', " ").to_lowercase()
}

fn default_transform(text: &str) -> String {
    text.to_string()
}
