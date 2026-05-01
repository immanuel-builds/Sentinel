"""
Behavioral Tracking System API
To run the server: uvicorn backend.main:app --reload
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from .utils import load_json, save_json

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"
ACTIVITY_LOG_FILE = os.path.join(DATA_DIR, "activity_log.json")
ANOMALIES_FILE = os.path.join(DATA_DIR, "anomalies.json")

class AnomalyUpdate(BaseModel):
    status: str

@app.get("/logs")
def get_logs():
    """Return the full list of log entries."""
    return load_json(ACTIVITY_LOG_FILE, [])

@app.get("/anomalies")
def get_anomalies():
    """Return the full list of anomalies."""
    return load_json(ANOMALIES_FILE, [])

@app.patch("/anomalies/{anomaly_id}")
def update_anomaly(anomaly_id: str, update: AnomalyUpdate):
    """Update an anomaly's status."""
    anomalies = load_json(ANOMALIES_FILE, [])
    found = False
    for anomaly in anomalies:
        if anomaly.get("id") == anomaly_id:
            anomaly["status"] = update.status
            found = True
            break

    if not found:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    save_json(ANOMALIES_FILE, anomalies)
    return {"message": "Status updated", "id": anomaly_id, "status": update.status}

@app.get("/summary")
def get_summary():
    """Return summary statistics across logs and anomalies."""
    logs = load_json(ACTIVITY_LOG_FILE, [])
    anomalies = load_json(ANOMALIES_FILE, [])

    unique_processes = set()
    for entry in logs:
        # Handle list of processes
        processes = entry.get("processes", [])
        if isinstance(processes, list):
            unique_processes.update(processes)
        # Handle single process field
        process = entry.get("process")
        if process:
            unique_processes.add(process)

    return {
        "total_events": len(logs),
        "total_anomalies": len(anomalies),
        "unique_processes": len(unique_processes)
    }
