import json
import os
from datetime import datetime

def analyze():
    """
    Reads activity_log.json, builds a behavioral baseline,
    and detects anomalies based on process novelty and active hours.
    """
    input_file = 'activity_log.json'
    output_file = 'anomalies.json'

    # 1. Read the file "activity_log.json"
    if not os.path.exists(input_file):
        with open(output_file, 'w') as f:
            json.dump([], f, indent=4)
        return

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        with open(output_file, 'w') as f:
            json.dump([], f, indent=4)
        return

    if not isinstance(data, list) or not data:
        with open(output_file, 'w') as f:
            json.dump([], f, indent=4)
        return

    # Sort entries by timestamp to ensure chronological analysis
    try:
        data.sort(key=lambda x: x.get('timestamp', ''))
    except Exception:
        pass

    # 2. Build a baseline
    # To detect anomalies in the same file, we use the first portion of the log
    # to establish the "typical" active hours. Otherwise, if we used all data,
    # no hour would ever be "outside" the range.

    # We'll use up to the first 10 entries or 50% of the data (whichever is smaller)
    # as the "typical" baseline for hours, ensuring at least one entry if possible.
    baseline_size = min(10, max(1, len(data) // 2))
    baseline_sample = data[:baseline_size]

    baseline_hours = []
    for entry in baseline_sample:
        ts = entry.get('timestamp')
        if ts:
            try:
                dt = datetime.fromisoformat(ts)
                baseline_hours.append(dt.hour)
            except (ValueError, TypeError):
                continue

    if baseline_hours:
        min_active_hour = min(baseline_hours)
        max_active_hour = max(baseline_hours)
    else:
        min_active_hour, max_active_hour = 0, 23

    # 3. Detect anomalies
    anomalies = []
    processes_seen_so_far = set()

    for entry in data:
        timestamp = entry.get('timestamp')
        processes = entry.get('processes', [])

        try:
            dt = datetime.fromisoformat(timestamp)
            current_hour = dt.hour
        except (ValueError, TypeError, AttributeError):
            continue

        # A. New Process Anomaly
        # Flag if a process appears that was not seen in EARLIER entries.
        for proc in processes:
            if proc not in processes_seen_so_far:
                anomalies.append({
                    "timestamp": timestamp,
                    "type": "new_process",
                    "process": proc,
                    "reason": f"Process '{proc}' was not observed in any earlier log entries.",
                    "risk": "medium"
                })
                # Update seen set sequentially
                processes_seen_so_far.add(proc)

        # B. Time Anomaly
        # Flag if an event occurs outside the typical active hour range.
        if current_hour < min_active_hour or current_hour > max_active_hour:
            anomalies.append({
                "timestamp": timestamp,
                "type": "time_anomaly",
                "process": None,
                "reason": f"Event occurred at hour {current_hour}, which is outside the typical range ({min_active_hour}-{max_active_hour}).",
                "risk": "high"
            })

    # 4. Output: Write all detected anomalies to a file named "anomalies.json"
    with open(output_file, 'w') as f:
        json.dump(anomalies, f, indent=4)

if __name__ == "__main__":
    analyze()
