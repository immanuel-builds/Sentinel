import subprocess
import time
import sys
import os

def main():
    """
    Continuous runner for the behavior tracking system pipeline.
    Automates data collection and analysis at regular intervals.
    Wrapped in try/except for production hardening.
    """
    interval = 12  # seconds between cycles

    # Path to scripts
    collector_script = os.path.join("collector", "collector.py")
    analyze_script = os.path.join("backend", "analyzer.py")

    while True:
        try:
            # 1. Collect data
            print("Collector running...")
            try:
                # collector.py is an infinite loop. We run it for a short duration
                # to allow it to capture and write at least one log entry.
                subprocess.run([sys.executable, collector_script], timeout=7, capture_output=True)
            except subprocess.TimeoutExpired:
                # Expected way to stop the infinite loop of collector.py
                pass
            except Exception as e:
                print(f"Error handled during collection: {e}. continuing...")

            # 2. Analyze data
            try:
                subprocess.run([sys.executable, analyze_script], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error handled during analysis: {e}. continuing...")
            except Exception as e:
                print(f"Error handled during analysis: {e}. continuing...")

            # 3. Cycle complete
            print("Cycle complete. Waiting...")
            time.sleep(interval)

        except KeyboardInterrupt:
            print("\nRunner stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error handled in runner loop: {e}. continuing...")
            time.sleep(interval)

if __name__ == "__main__":
    main()
