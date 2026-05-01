import os
import sys
import hashlib
from datetime import datetime
import pandas as pd
import numpy as np

# Path adjustment for when running as a standalone script
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.utils import load_json, save_json
else:
    from .utils import load_json, save_json

def generate_id(timestamp, anomaly_type, process):
    """Generate a stable hash ID for an anomaly."""
    unique_str = f"{timestamp}-{anomaly_type}-{process}"
    return hashlib.md5(unique_str.encode()).hexdigest()

def analyze():
    """
    Hybrid Anomaly Detection: Combines Rule-Based logic with Statistical Analysis.
    """
    data_dir = "data"
    input_file = os.path.join(data_dir, 'activity_log.json')
    output_file = os.path.join(data_dir, 'anomalies.json')

    # Load existing anomalies to preserve statuses and IDs
    existing_anomalies_data = load_json(output_file, [])
    existing_anomalies_map = {a['id']: a for a in existing_anomalies_data if 'id' in a}

    # 1. Read the raw activity logs
    raw_data = load_json(input_file, [])
    if not isinstance(raw_data, list) or not raw_data:
        save_json(output_file, [])
        return

    # --- PART 1: RULE-BASED DETECTION (Preserved Exactly) ---
    rule_anomalies = []

    # Sort entries by timestamp for baseline consistency
    try:
        raw_data.sort(key=lambda x: x.get('timestamp', ''))
    except Exception:
        pass

    baseline_size = min(10, max(1, len(raw_data) // 2))
    baseline_sample = raw_data[:baseline_size]

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

    all_cpu_raw = [entry.get('cpu', 0) for entry in raw_data if isinstance(entry.get('cpu'), (int, float))]
    avg_cpu_raw = sum(all_cpu_raw) / len(all_cpu_raw) if all_cpu_raw else 0

    processes_seen_so_far = set()

    for entry in raw_data:
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

                aid = generate_id(timestamp, "new_process", proc)
                rule_anomalies.append({
                    "id": aid,
                    "timestamp": timestamp,
                    "type": "new_process",
                    "process": proc,
                    "reason": f"New process '{proc}' detected {hour_context}. This process was not observed in the baseline period.",
                    "risk": risk,
                    "status": existing_anomalies_map.get(aid, {}).get('status', 'pending')
                })
                processes_seen_so_far.add(proc)

        # B. Time Anomaly
        if not is_normal_hour:
            dist_min = abs(current_hour - min_active_hour)
            dist_max = abs(current_hour - max_active_hour)
            distance = min(dist_min, dist_max, 24 - dist_min, 24 - dist_max)

            risk = "high" if distance > 2 else "medium"
            severity = "significant" if distance > 2 else "slight"

            aid = generate_id(timestamp, "time_anomaly", "None")
            rule_anomalies.append({
                "id": aid,
                "timestamp": timestamp,
                "type": "time_anomaly",
                "process": None,
                "reason": f"{severity.capitalize()} time deviation: Activity at hour {current_hour} is outside the typical {min_active_hour}-{max_active_hour} range.",
                "risk": risk,
                "status": existing_anomalies_map.get(aid, {}).get('status', 'pending')
            })

        # C. CPU Spike Detection (Rule-Based)
        if cpu > avg_cpu_raw * 2 and cpu > 5:
            multiplier = cpu / avg_cpu_raw if avg_cpu_raw > 0 else 0
            risk = "high" if multiplier >= 3 else "medium"

            aid = generate_id(timestamp, "cpu_spike", "System Wide")
            rule_anomalies.append({
                "id": aid,
                "timestamp": timestamp,
                "type": "cpu_spike",
                "process": "System Wide",
                "reason": f"CPU usage spike: {cpu:.1f}% is {multiplier:.1f}x the session average of {avg_cpu_raw:.1f}%.",
                "risk": risk,
                "status": existing_anomalies_map.get(aid, {}).get('status', 'pending')
            })

    # --- PART 2: STATISTICAL DETECTION (New) ---
    stat_anomalies = []
    df = pd.DataFrame(raw_data)

    if not df.empty and 'cpu' in df.columns:
        # 1. CPU Statistical Baseline
        cpu_mean = df['cpu'].mean()
        cpu_std = df['cpu'].std()

        if not pd.isna(cpu_std) and cpu_std > 0:
            moderate_threshold = cpu_mean + (2 * cpu_std)
            severe_threshold = cpu_mean + (3 * cpu_std)

            for _, row in df.iterrows():
                cpu_val = row['cpu']
                if cpu_val > moderate_threshold:
                    risk = "high" if cpu_val > severe_threshold else "medium"
                    aid = generate_id(row['timestamp'], "statistical_anomaly", "CPU_Statistical")
                    stat_anomalies.append({
                        "id": aid,
                        "timestamp": row['timestamp'],
                        "type": "statistical_anomaly",
                        "process": "System Wide",
                        "reason": f"CPU usage {cpu_val:.1f}% exceeds threshold (mean {cpu_mean:.1f}%, std {cpu_std:.1f}%)",
                        "risk": risk,
                        "status": existing_anomalies_map.get(aid, {}).get('status', 'pending')
                    })

        # 2. Process Frequency Analysis
        # Flatten processes list
        if 'processes' in df.columns:
            process_series = df.explode('processes')['processes']
            total_logs = len(df)

            if total_logs > 0:
                process_counts = process_series.value_counts()

                for proc, count in process_counts.items():
                    freq_ratio = count / total_logs
                    if freq_ratio < 0.05:
                        # Find the first occurrence for the anomaly timestamp
                        first_occurrence = df[df['processes'].apply(lambda x: proc in x if isinstance(x, list) else False)].iloc[0]

                        aid = generate_id(first_occurrence['timestamp'], "statistical_anomaly", proc)
                        stat_anomalies.append({
                            "id": aid,
                            "timestamp": first_occurrence['timestamp'],
                            "type": "statistical_anomaly",
                            "process": proc,
                            "reason": f"Process '{proc}' appears in only {freq_ratio*100:.1f}% of logs (rare behavior)",
                            "risk": "medium",
                            "status": existing_anomalies_map.get(aid, {}).get('status', 'pending')
                        })

    # --- PART 3: MERGING & DEDUPLICATION ---
    all_new_anomalies = rule_anomalies + stat_anomalies

    final_anomalies = []
    seen_ids = set()

    for anomaly in all_new_anomalies:
        aid = anomaly['id']
        if aid not in seen_ids:
            final_anomalies.append(anomaly)
            seen_ids.add(aid)

    save_json(output_file, final_anomalies)

if __name__ == "__main__":
    analyze()
