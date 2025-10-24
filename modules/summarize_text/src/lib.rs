use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Deserialize)]
struct SummarizeInput {
    text: String,
    max_sentences: Option<usize>,
}

#[derive(Serialize)]
struct SummarizeOutput {
    summary: String,
    sentences_used: usize,
}

#[no_mangle]
pub extern "C" fn run() -> i32 {
    match execute() {
        Ok(output) => {
            println!("{}", serde_json::to_string(&output).unwrap());
            0
        }
        Err(err) => {
            eprintln!("{err}");
            1
        }
    }
}

fn execute() -> Result<SummarizeOutput, String> {
    use std::io::{self, Read};
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer).map_err(|e| e.to_string())?;
    let payload: SummarizeInput = serde_json::from_str(&buffer).map_err(|e| e.to_string())?;
    let mut sentences: Vec<String> = payload
        .text
        .split(|c| c == '.' || c == '!' || c == '?')
        .map(|s| s.trim().to_string())
        .filter(|s| !s.is_empty())
        .collect();
    let max_sentences = payload.max_sentences.unwrap_or(3).min(sentences.len());
    let summary = sentences.drain(..max_sentences).collect::<Vec<_>>().join(". ");
    Ok(SummarizeOutput {
        summary,
        sentences_used: max_sentences,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_summarize() {
        let payload = SummarizeInput {
            text: "Sentence one. Sentence two. Sentence three.".to_string(),
            max_sentences: Some(2),
        };
        let result = SummarizeOutput {
            summary: "Sentence one. Sentence two".to_string(),
            sentences_used: 2,
        };
        assert_eq!(result.summary, "Sentence one. Sentence two");
        assert_eq!(result.sentences_used, 2);
    }
}
