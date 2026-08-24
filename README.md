# Runbook ML

Runbook ML is a small experiment tracker and model registry for making ML
work reproducible. It logs parameters, metrics, tags, source commit text,
and artifacts into SQLite; compares runs; and applies a visible promotion
gate before a model can become the current candidate.

> **Question it answers:** can another student tell which run won, why it won,
> what data contract it used, and where its artifact came from?

## Lifecycle

```text
train -> log parameters/metrics -> compare runs -> validate gate -> promote candidate
```

| Capability | Implementation |
| --- | --- |
| Tracking | SQLite-backed run records |
| Metrics | JSON metrics with lower-is-better or higher-is-better goals |
| Artifacts | SHA-256 recorded for each copied model artifact |
| Governance | Promotion gate with minimum metric and required tags |
| Product surface | CLI, FastAPI read API, and HTML comparison dashboard |
| Reproducibility | Seeds, environment metadata, and a deterministic demo trainer |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python examples/train_demo.py --db artifacts/runbook.sqlite3
runbook list --db artifacts/runbook.sqlite3
runbook compare --db artifacts/runbook.sqlite3
runbook promote <RUN_ID> --db artifacts/runbook.sqlite3 --metric accuracy --minimum 0.75
pytest -q
```

The FastAPI surface can be started with
`RUNBOOK_DB=artifacts/runbook.sqlite3 uvicorn runbook_ml.api:app --reload`.
It exposes `/health`, `/runs`, `/compare`, and `/promote/{run_id}`.

## Why it is useful in a portfolio

It demonstrates the part of ML engineering that is easy to omit from a
notebook: lineage, comparison, artifacts, validation gates, and a reversible
promotion decision. The code is intentionally small enough to audit and
extend, but the workflow maps to larger platforms.

## Limitations and next experiments

This is a local SQLite tracker, not a multi-user production registry. The
promotion gate checks stored metrics but does not evaluate fairness, drift,
latency, or security. Next steps include dataset fingerprints, model cards,
role-based access, an immutable event log, and a real dashboard.

## License

MIT. See [LICENSE](LICENSE) and [INSPIRED_BY.md](INSPIRED_BY.md).
