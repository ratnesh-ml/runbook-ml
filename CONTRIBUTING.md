# Contributing

Thanks for helping improve Runbook ML. Contributions should preserve reproducibility and make the lifecycle state easier to inspect. Include tests for changes to run storage, comparison, promotion rules, CLI output, or API responses.

Before opening a pull request, run:

```bash
pip install -e ".[dev]"
python -m compileall -q src examples
pytest -q
```

Use synthetic or permission-cleared datasets and artifacts only. Do not commit model files containing private data, credentials, access tokens, or large generated databases. If a registry rule changes, explain the governance trade-off in the README and add a test that demonstrates the new decision boundary.
