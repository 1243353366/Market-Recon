# AI Coding Reliability Benchmark (starter)

This repository includes a small, transparent benchmark harness, not a validated or statistically representative benchmark. The supplied 300-item taxonomy is a useful label space; it is not itself an evaluation dataset. The initial fixtures cover only a few categories and must not be presented as evidence that a coding agent is generally reliable.

## Evaluation dimensions

For each case, assess detection, precision/false-positive resistance, severity, fix correctness, regression resistance, and explanation quality. The scorer reports detection F1 and precision separately, then scores fix and regression outcomes only for cases with expected defects. Human-annotated expected findings are the ground truth; model confidence and number of comments earn no points.

Scoring weights (sum to 100):
- Detection F1: 20
- False-positive resistance (precision): 20
- Fix correctness: 25
- Regression resistance: 25
- Explanation quality, including severity rationale: 10

Severity accuracy is reported separately and is not added again to the score. Cases with no expected defects are critical false-positive checks. Missing predictions count as missed findings/fixes. `fix_passed` and `regression_free` must be assessed by independent tests or reviewers, not self-attested by the coding agent.

## Run

```bash
python -m benchmark.cli --predictions predictions.json
```

Prediction format:

```json
{
  "empty-price-history": {
    "finding_ids": ["empty-input-crash"],
    "severity_by_id": {"empty-input-crash": "medium"},
    "fix_passed": true,
    "regression_free": true,
    "explanation_score": 0.8
  }
}
```

Do not include the expected labels in the model prompt. Run the same tasks against clean known-good code and buggy variants, pin tool/model versions, preserve patches and test logs, and use multiple independent annotators for disputed findings. Track confidence intervals across a larger held-out set before comparing systems. Include compile/type/test results, security review, scope adherence, and human adjudication; a single aggregate score can hide dangerous weaknesses.

## Anti-reward-hacking controls

- Include known-good code and adversarial distractors; unnecessary findings count as false positives.
- Score final patched code, not comment volume.
- Have a separate evaluator run tests and compare the entire patch for unintended changes.
- Keep hidden test cases and hold out categories; avoid tuning against the public fixtures alone.
- Use mutation testing and regression suites to verify that tests can detect the target defect.
- Report metric definitions and failures; never claim coverage of all 300 taxonomy items from this starter.

## Repository audit notes

The initial repository scaffold had concrete implementation defects: core module contents were placed under mismatched filenames; the advertised CLI imported a missing module; report generation labeled technical indicators “Bullish/Cautious” as if they were thesis conclusions; the SEC client hard-coded the HTTP `Host` header to `www.sec.gov`, including for `data.sec.gov`; and RAG CLI storage flags were attached to the root parser instead of each subcommand. These are corrected in the current change. No tests were run in this tool environment; the added tests are not claimed as passing.
