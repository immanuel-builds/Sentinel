import subprocess
import time
import sys
import os

def main():
    """
    Continuous runner for the behavior tracking system pipeline.
    Automates data collection and analysis at regular intervals.
    """
    interval = 12  # seconds between cycles

    # Path to scripts
    # Scripts are in the collector/ directory
    collector_script = os.path.join("collector", "collector.py")
    analyze_script = os.path.join("collector", "analyze.py")

    while True:
        try:
            # 1. Collect data
            print("Collecting data...")
            try:
                # collector.py is an infinite loop. We run it for a short duration
                # to allow it to capture and write at least one log entry.
                # One iteration takes ~1s (CPU sampling) + IO, then sleeps 5s.
                # A timeout of 7 seconds should reliably capture one entry.
                subprocess.run([sys.executable, collector_script], timeout=7, capture_output=True)
            except subprocess.TimeoutExpired:
                # This is the expected way to stop the infinite loop of collector.py
                pass
            except Exception as e:
                print(f"Error during collection: {e}")

            # 2. Analyze data
            print("Analyzing data...")
            try:
                # analyze.py runs once and exits
                subprocess.run([sys.executable, analyze_script], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error during analysis: {e}")
            except Exception as e:
                print(f"Error during analysis: {e}")

            # 3. Cycle complete
            print("Cycle complete. Waiting...")
            time.sleep(interval)

        except KeyboardInterrupt:
            print("\nRunner stopped by user.")
            break
        except Exception as e:
            print(f"Unexpected error in runner loop: {e}")
            time.sleep(interval)

if __name__ == "__main__":
    main()
