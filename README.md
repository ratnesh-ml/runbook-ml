# Runbook ML

[![CI](https://github.com/ratnesh-ml/runbook-ml/actions/workflows/test.yml/badge.svg)](https://github.com/ratnesh-ml/runbook-ml/actions/workflows/test.yml)

I built Runbook ML to practise the questions that appear after an experiment produces a promising number: which run produced it, what parameters and dataset assumptions did it use, where is the artifact, and what evidence should be required before I promote it?

This is a compact experiment tracker and local model registry. It logs parameters, metrics, tags, source-commit text, and artifact records in SQLite; compares runs; and exposes a visible promotion gate before a candidate is selected.

## The workflow I wanted to make explicit

```text
train → log parameters and metrics → compare runs → validate gate → promote candidate
```

| Capability | Implementation | Why it is there |
| --- | --- | --- |
| Run tracking | SQLite-backed records | A simple, inspectable source of experiment history. |
| Metrics | JSON metrics with lower- or higher-is-better goals | To make comparison rules explicit. |
| Artifacts | SHA-256 recorded for copied artifacts | To preserve a basic lineage trail. |
| Promotion | Minimum metric and required-tag gate | To avoid treating the latest run as the winner by default. |
| Product surface | CLI, FastAPI read API, and HTML comparison dashboard | To practise useful interfaces around a workflow. |
| Reproducibility | Fixed seeds, environment metadata, and deterministic demo training | To make reruns meaningful. |

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

python examples/train_demo.py --db artifacts/runbook.sqlite3
runbook --db artifacts/runbook.sqlite3 list
runbook --db artifacts/runbook.sqlite3 compare --metric accuracy
runbook --db artifacts/runbook.sqlite3 promote <RUN_ID> --metric accuracy --minimum 0.75
pytest -q
```

For the API surface:

```bash
RUNBOOK_DB=artifacts/runbook.sqlite3 uvicorn runbook_ml.api:app --reload
```

The API exposes `/health`, `/runs`, `/compare`, and `/promote/{run_id}`.

## What I learned while building it

The model is only one artifact in an ML workflow. I intentionally kept this project small enough to audit, but it made lineage, comparison, artifact hashes, validation gates, and reversible promotion decisions tangible. Those are the habits I want to carry into larger tooling rather than imitate a large platform without understanding its boundaries.

## What this does not claim

This is a local SQLite tracker, not a multi-user production registry. The promotion gate checks stored metrics; it does not evaluate fairness, drift, latency, security, or organisational approvals. My next steps would be dataset fingerprints, model cards, role-based access, an immutable event log, and a richer dashboard.

## Verification, contribution, and license

Run `pytest -q` locally. GitHub Actions compiles the source and examples and runs the test suite on pushes and pull requests. Contributor guidance is in [CONTRIBUTING.md](CONTRIBUTING.md); use synthetic or permission-cleared datasets and artifacts only.

MIT licensed. See [LICENSE](LICENSE) and [INSPIRED_BY.md](INSPIRED_BY.md).
