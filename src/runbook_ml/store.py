from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  started_at REAL NOT NULL,
  status TEXT NOT NULL,
  parameters TEXT NOT NULL,
  metrics TEXT NOT NULL,
  tags TEXT NOT NULL,
  artifact_path TEXT,
  artifact_sha256 TEXT,
  promoted INTEGER NOT NULL DEFAULT 0
);
"""


class ExperimentStore:
    def __init__(self, db_path='artifacts/runbook.sqlite3'):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def log_run(self, name, parameters, metrics, tags=None, artifact_path=None):
        tags = tags or {}
        digest = None
        if artifact_path:
            digest = hashlib.sha256(Path(artifact_path).read_bytes()).hexdigest()
        with self._connect() as conn:
            cur = conn.execute(
                'INSERT INTO runs (name, started_at, status, parameters, metrics, tags, artifact_path, artifact_sha256) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (name, time.time(), 'finished', json.dumps(parameters, sort_keys=True), json.dumps(metrics, sort_keys=True), json.dumps(tags, sort_keys=True), str(artifact_path) if artifact_path else None, digest),
            )
            return cur.lastrowid

    def list_runs(self):
        with self._connect() as conn:
            rows = conn.execute(
                'SELECT run_id, name, started_at, status, parameters, metrics, tags, artifact_path, artifact_sha256, promoted FROM runs ORDER BY run_id DESC'
            ).fetchall()
        return [self._row(row) for row in rows]

    def get_run(self, run_id):
        with self._connect() as conn:
            row = conn.execute(
                'SELECT run_id, name, started_at, status, parameters, metrics, tags, artifact_path, artifact_sha256, promoted FROM runs WHERE run_id=?',
                (run_id,),
            ).fetchone()
        return self._row(row) if row else None

    @staticmethod
    def _row(row):
        if row is None:
            return None
        keys = ('run_id', 'name', 'started_at', 'status', 'parameters', 'metrics', 'tags', 'artifact_path', 'artifact_sha256', 'promoted')
        out = dict(zip(keys, row))
        out['parameters'] = json.loads(out['parameters'])
        out['metrics'] = json.loads(out['metrics'])
        out['tags'] = json.loads(out['tags'])
        out['promoted'] = bool(out['promoted'])
        return out

    def compare(self, metric):
        rows = self.list_runs()
        return sorted(rows, key=lambda row: row['metrics'].get(metric, float('-inf')), reverse=True)

    def promote(self, run_id, metric, minimum, required_tags=None):
        row = self.get_run(run_id)
        if not row:
            raise ValueError(f'unknown run: {run_id}')
        if row['metrics'].get(metric, float('-inf')) < minimum:
            raise ValueError(f'promotion gate failed: {metric} below {minimum}')
        required_tags = required_tags or {}
        if any(row['tags'].get(k) != v for k, v in required_tags.items()):
            raise ValueError('promotion gate failed: required tags missing')
        with self._connect() as conn:
            conn.execute('UPDATE runs SET promoted=0')
            conn.execute('UPDATE runs SET promoted=1 WHERE run_id=?', (run_id,))
        return self.get_run(run_id)
