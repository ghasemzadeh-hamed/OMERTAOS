use regex::Regex;
use serde::{Deserialize, Serialize};
use std::io::{self, Read};

#[derive(Deserialize)]
struct InvoicePayload {
    text: String,
}

#[derive(Serialize)]
struct InvoiceResult {
    vendor: Option<String>,
    total: Option<String>,
    invoice_number: Option<String>,
}

fn main() {
    if let Err(err) = run() {
        eprintln!("{err}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut buffer = String::new();
    io::stdin().read_to_string(&mut buffer).map_err(|e| e.to_string())?;
    let payload: InvoicePayload = serde_json::from_str(&buffer).map_err(|e| e.to_string())?;
    let vendor = Regex::new(r"Vendor[:\s]+([A-Za-z0-9 &.-]+)").unwrap()
        .captures(&payload.text)
        .and_then(|cap| cap.get(1).map(|m| m.as_str().trim().to_string()));
    let total = Regex::new(r"Total[:\s]+\$?([0-9,.]+)").unwrap()
        .captures(&payload.text)
        .and_then(|cap| cap.get(1).map(|m| m.as_str().trim().to_string()));
    let invoice_number = Regex::new(r"Invoice[#\s]+([A-Za-z0-9-]+)").unwrap()
        .captures(&payload.text)
        .and_then(|cap| cap.get(1).map(|m| m.as_str().trim().to_string()));
    let result = InvoiceResult {
        vendor,
        total,
        invoice_number,
    };
    println!("{}", serde_json::to_string(&result).unwrap());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_invoice_parsing() {
        let text = "Vendor: Example Corp\nInvoice # INV-100\nTotal: $123.45";
        let payload = InvoicePayload {
            text: text.to_string(),
        };
        let vendor = Regex::new(r"Vendor[:\s]+([A-Za-z0-9 &.-]+)").unwrap()
            .captures(&payload.text)
            .and_then(|cap| cap.get(1).map(|m| m.as_str().trim().to_string()));
        assert_eq!(vendor.as_deref(), Some("Example Corp"));
    }
}
