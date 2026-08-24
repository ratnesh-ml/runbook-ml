import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from .store import ExperimentStore

app = FastAPI(title='Runbook ML', version='0.1.0')
store = ExperimentStore(os.getenv('RUNBOOK_DB', 'artifacts/runbook.sqlite3'))

class PromotionRequest(BaseModel):
metric: str = Field(min_length=1)
minimum: float

@app.get('/health')
def health(): return {'status': 'ok', 'version': '0.1.0', 'runs': len(store.list_runs())}

@app.get('/runs')
def runs(): return store.list_runs()

@app.get('/compare')
def compare(metric: str = Query(..., min_length=1)): return store.compare(metric)

@app.post('/promote/{run_id}')
def promote(run_id: int, request: PromotionRequest):
try: return store.promote(run_id, request.metric, request.minimum)
except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc))
