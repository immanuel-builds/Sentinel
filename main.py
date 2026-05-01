"""
Behavioral Tracking System API
To run the server: uvicorn main:app --reload
"""

import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Any

app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ACTIVITY_LOG_FILE = "activity_log.json"
ANOMALIES_FILE = "anomalies.json"

def load_json_file(filepath: str, default_value: Any) -> Any:
    """Safely load a JSON file, returning a default value if file is missing, empty, or malformed."""
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r") as f:
            content = f.read().strip()
            if not content:
                return default_value
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return default_value

@app.get("/logs")
def get_logs():
    """Return the full list of log entries from activity_log.json."""
    return load_json_file(ACTIVITY_LOG_FILE, [])

@app.get("/anomalies")
def get_anomalies():
    """Return the full list of anomalies from anomalies.json."""
    return load_json_file(ANOMALIES_FILE, [])

@app.get("/summary")
def get_summary():
    """Return summary statistics across logs and anomalies."""
    logs = load_json_file(ACTIVITY_LOG_FILE, [])
    anomalies = load_json_file(ANOMALIES_FILE, [])

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
