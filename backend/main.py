"""
Behavioral Tracking System API
To run the server: uvicorn backend.main:app --reload
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .utils import load_json

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

@app.get("/logs")
def get_logs():
    """Return the full list of log entries from data/activity_log.json."""
    return load_json(ACTIVITY_LOG_FILE, [])

@app.get("/anomalies")
def get_anomalies():
    """Return the full list of anomalies from data/anomalies.json."""
    return load_json(ANOMALIES_FILE, [])

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
