from pathlib import Path
import pytest
from runbook_ml.store import ExperimentStore


def test_log_compare_and_promote(tmp_path: Path):
    store = ExperimentStore(tmp_path / 'runs.sqlite3')
    one = store.log_run('baseline', {'seed': 1}, {'accuracy': 0.72}, {'stage': 'candidate'})
    two = store.log_run('better', {'seed': 2}, {'accuracy': 0.84}, {'stage': 'candidate'})
    assert store.compare('accuracy')[0]['run_id'] == two
    promoted = store.promote(two, 'accuracy', 0.8)
    assert promoted['promoted'] is True
    assert store.get_run(one)['promoted'] is False


def test_promotion_gate_explains_failure(tmp_path: Path):
    store = ExperimentStore(tmp_path / 'runs.sqlite3')
    run_id = store.log_run('weak', {}, {'accuracy': 0.5})
    with pytest.raises(ValueError, match='promotion gate failed'):
        store.promote(run_id, 'accuracy', 0.8)
