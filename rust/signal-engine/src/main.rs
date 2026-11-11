use chrono::{Duration, NaiveDate};
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::io::{self, BufRead};

#[derive(Debug, Clone, Deserialize, Serialize)]
struct Signal {
    signal_id: String,
    entity_id: String,
    entity_name: String,
    kind: String,
    direction: String,
    observed_on: NaiveDate,
    summary: String,
    source_name: String,
    source_url: String,
    #[serde(default)]
    metric_name: Option<String>,
    #[serde(default)]
    metric_value: Option<f64>,
    #[serde(default)]
    unit: Option<String>,
    #[serde(default)]
    baseline: Option<String>,
    #[serde(default)]
    confidence: Option<f64>,
}

#[derive(Debug, Serialize)]
struct Finding {
    entity_id: String,
    entity_name: String,
    window_start: NaiveDate,
    window_end: NaiveDate,
    positive_signal_count: usize,
    negative_signal_count: usize,
    signals: Vec<Signal>,
    interpretation: &'static str,
}

fn find_divergences(signals: Vec<Signal>, as_of: NaiveDate, window_days: i64, min_kinds: usize) -> Result<Vec<Finding>, String> {
    if window_days < 1 { return Err("window_days must be positive".into()); }
    if min_kinds < 2 { return Err("minimum distinct kinds must be at least 2".into()); }
    let start = as_of - Duration::days(window_days);
    let mut groups: BTreeMap<String, Vec<Signal>> = BTreeMap::new();
    for signal in signals {
        if signal.signal_id.trim().is_empty() || signal.entity_id.trim().is_empty() || signal.summary.trim().is_empty() {
            return Err("signal_id, entity_id, and summary must be non-empty".into());
        }
        if !signal.source_url.starts_with("https://") {
            return Err(format!("signal {} has no HTTPS source citation", signal.signal_id));
        }
        if !matches!(signal.direction.as_str(), "positive" | "negative" | "mixed" | "unknown") {
            return Err(format!("signal {} has unsupported direction", signal.signal_id));
        }
        if signal.observed_on >= start && signal.observed_on <= as_of {
            groups.entry(signal.entity_id.clone()).or_default().push(signal);
        }
    }

    let mut findings = Vec::new();
    for (entity_id, mut rows) in groups {
        let directions: BTreeSet<&str> = rows.iter().map(|row| row.direction.as_str()).collect();
        let kinds: BTreeSet<&str> = rows.iter().map(|row| row.kind.as_str()).collect();
        if !(directions.contains("positive") && directions.contains("negative") && kinds.len() >= min_kinds) { continue; }
        rows.sort_by(|a, b| a.observed_on.cmp(&b.observed_on).then(a.signal_id.cmp(&b.signal_id)));
        let positive_signal_count = rows.iter().filter(|row| row.direction == "positive").count();
        let negative_signal_count = rows.iter().filter(|row| row.direction == "negative").count();
        let entity_name = rows.first().map(|row| row.entity_name.clone()).unwrap_or_default();
        findings.push(Finding {
            entity_id, entity_name, window_start: start, window_end: as_of,
            positive_signal_count, negative_signal_count, signals: rows,
            interpretation: "Mixed public observations require source verification. This is not evidence of deception, causation, future performance, or investment merit.",
        });
    }
    Ok(findings)
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 4 {
        eprintln!("Usage: signal-engine <YYYY-MM-DD> <window-days> <minimum-distinct-kinds> < signals.jsonl",);
        std::process::exit(2);
    }
    let as_of = NaiveDate::parse_from_str(&args[1], "%Y-%m-%d")?;
    let window_days: i64 = args[2].parse()?;
    let min_kinds: usize = args[3].parse()?;
    let stdin = io::stdin();
    let mut signals = Vec::new();
    for (line_number, line) in stdin.lock().lines().enumerate() {
        let line = line?;
        if line.trim().is_empty() { continue; }
        let signal: Signal = serde_json::from_str(&line).map_err(|error| format!("invalid JSON on line {}: {error}", line_number + 1))?;
        signals.push(signal);
    }
    let findings = find_divergences(signals, as_of, window_days, min_kinds)?;
    println!("{}", serde_json::to_string_pretty(&findings)?);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn signal(id: &str, kind: &str, direction: &str, day: &str) -> Signal {
        Signal {
            signal_id: id.into(), entity_id: "CIK1".into(), entity_name: "Example".into(),
            kind: kind.into(), direction: direction.into(), observed_on: NaiveDate::parse_from_str(day, "%Y-%m-%d").unwrap(),
            summary: "Public observation".into(), source_name: "Official source".into(), source_url: "https://example.org/source".into(),
            metric_name: None, metric_value: None, unit: None, baseline: None, confidence: None,
        }
    }

    #[test]
    fn flags_mixed_evidence_and_keeps_citations() {
        let rows = vec![signal("a", "demand", "negative", "2026-01-01"), signal("b", "hiring", "positive", "2026-01-02")];
        let result = find_divergences(rows, NaiveDate::parse_from_str("2026-02-01", "%Y-%m-%d").unwrap(), 60, 2).unwrap();
        assert_eq!(result.len(), 1);
        assert_eq!(result[0].positive_signal_count, 1);
        assert!(result[0].signals.iter().all(|row| row.source_url.starts_with("https://")));
    }

    #[test]
    fn excludes_out_of_window_and_single_signal_kind() {
        let rows = vec![signal("a", "demand", "negative", "2025-01-01"), signal("b", "demand", "positive", "2026-01-02")];
        let result = find_divergences(rows, NaiveDate::parse_from_str("2026-02-01", "%Y-%m-%d").unwrap(), 60, 2).unwrap();
        assert!(result.is_empty());
    }
}
