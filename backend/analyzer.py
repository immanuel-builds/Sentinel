import os
import sys
from datetime import datetime

# Path adjustment for when running as a standalone script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.utils import load_json, save_json
else:
    from .utils import load_json, save_json

def analyze():
    """
    Reads activity_log.json, builds a behavioral baseline,
    and detects anomalies based on process novelty, active hours, and CPU usage.
    """
    data_dir = "data"
    input_file = os.path.join(data_dir, 'activity_log.json')
    output_file = os.path.join(data_dir, 'anomalies.json')

    # 1. Read the file "activity_log.json"
    data = load_json(input_file, [])

    if not isinstance(data, list) or not data:
        save_json(output_file, [])
        return

    # Sort entries by timestamp to ensure chronological analysis
    try:
        data.sort(key=lambda x: x.get('timestamp', ''))
    except Exception:
        pass

    # 2. Build a baseline
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

    # Calculate global average CPU usage
    all_cpu = [entry.get('cpu', 0) for entry in data if isinstance(entry.get('cpu'), (int, float))]
    avg_cpu = sum(all_cpu) / len(all_cpu) if all_cpu else 0

    # 3. Detect anomalies
    anomalies = []
    processes_seen_so_far = set()

    for entry in data:
        timestamp = entry.get('timestamp')
        processes = entry.get('processes', [])
        cpu = entry.get('cpu', 0)

        try:
            dt = datetime.fromisoformat(timestamp)
            current_hour = dt.hour
        except (ValueError, TypeError, AttributeError):
            continue

        # A. New Process Anomaly
        is_normal_hour = min_active_hour <= current_hour <= max_active_hour
        for proc in processes:
            if proc and proc not in processes_seen_so_far:
                risk = "low" if is_normal_hour else "medium"
                hour_context = "during normal hours" if is_normal_hour else f"outside normal hours ({min_active_hour}-{max_active_hour})"
                anomalies.append({
                    "timestamp": timestamp,
                    "type": "new_process",
                    "process": proc,
                    "reason": f"New process '{proc}' detected {hour_context}. This process was not observed in the baseline period.",
                    "risk": risk
                })
                processes_seen_so_far.add(proc)

        # B. Time Anomaly
        if not is_normal_hour:
            dist_min = abs(current_hour - min_active_hour)
            dist_max = abs(current_hour - max_active_hour)
            distance = min(dist_min, dist_max, 24 - dist_min, 24 - dist_max)

            if distance > 2:
                risk = "high"
                severity = "significant"
            else:
                risk = "medium"
                severity = "slight"

            anomalies.append({
                "timestamp": timestamp,
                "type": "time_anomaly",
                "process": None,
                "reason": f"{severity.capitalize()} time deviation: Activity at hour {current_hour} is outside the typical {min_active_hour}-{max_active_hour} range.",
                "risk": risk
            })

        # C. CPU Spike Detection
        if cpu > avg_cpu * 2 and cpu > 5:
            multiplier = cpu / avg_cpu if avg_cpu > 0 else 0
            if multiplier >= 3:
                risk = "high"
            else:
                risk = "medium"

            anomalies.append({
                "timestamp": timestamp,
                "type": "cpu_spike",
                "process": "System Wide",
                "reason": f"CPU usage spike: {cpu:.1f}% is {multiplier:.1f}x the session average of {avg_cpu:.1f}%.",
                "risk": risk
            })

    # 4. Output: Write all detected anomalies to a file named "anomalies.json"
    save_json(output_file, anomalies)

if __name__ == "__main__":
    analyze()
