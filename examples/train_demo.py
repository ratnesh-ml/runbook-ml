import argparse
import json
from pathlib import Path

import joblib
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from runbook_ml.store import ExperimentStore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='artifacts/runbook.sqlite3')
    args = parser.parse_args()
    data = load_breast_cancer()
    x_train, x_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.25, random_state=17, stratify=data.target)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=17))
    model.fit(x_train, y_train)
    pred = model.predict(x_test)
    metrics = {'accuracy': round(float(accuracy_score(y_test, pred)), 4), 'f1': round(float(f1_score(y_test, pred)), 4)}
    artifact = Path(args.db).parent / 'model.joblib'
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, artifact)
    run_id = ExperimentStore(args.db).log_run(
        'breast-cancer-logistic',
        {'seed': 17, 'model': 'logistic_regression', 'test_size': 0.25},
        metrics,
        {'dataset': 'sklearn_breast_cancer', 'stage': 'candidate'},
        artifact,
    )
    print(json.dumps({'run_id': run_id, 'metrics': metrics, 'artifact': str(artifact)}, indent=2))


if __name__ == '__main__':
    main()
