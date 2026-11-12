#!/usr/bin/env bash
set -euo pipefail

echo "=== Running Python Unit and Benchmark Tests ==="
python3 -m pytest tests -v

echo "=== Running Go Gateway Tests and Contract Verification ==="
(cd go/ingest-gateway && go test -v ./...)

echo "=== Running Rust Signal Engine Tests and Contract Verification ==="
(cd rust/signal-engine && cargo test --verbose)

echo "=== Running TypeScript Tests and Production Build ==="
(cd web && npm test && npm run build)

echo "=== Running Filing Classification Evaluation Benchmark ==="
python3 benchmark/filing_eval.py

echo "=== All multi-language verification suites passed! ==="
