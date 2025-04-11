import subprocess
import time
import sys
import csv
from datetime import datetime

def get_container_ids():
    result = subprocess.run(["docker", "ps", "-q"], stdout=subprocess.PIPE)
    return result.stdout.decode().splitlines()

def get_container_pid(cid):
    result = subprocess.run(["docker", "inspect", "--format", "{{.State.Pid}}", cid], stdout=subprocess.PIPE)
    return result.stdout.decode().strip()

def read_cpu_pressure(path):
    try:
        with open(path, "r") as f:
            data = f.read()
        for line in data.splitlines():
            if line.startswith("some"):
                return line.split()
    except Exception as e:
        return [f"Error: {e}"]
    return ["N/A"]

def monitor_psi(duration_sec=300, interval_sec=10):
    end_time = time.time() + duration_sec
    filename = "psi_monitoring_log.csv"

    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        # CSV header
        writer.writerow(["timestamp", "source", "avg10", "avg60", "avg300", "total"])

        while time.time() < end_time:
            timestamp = datetime.utcnow().isoformat()

            # Host-level PSI
            host_psi_path = "/proc/pressure/cpu"
            host_metrics = read_cpu_pressure(host_psi_path)
            if len(host_metrics) == 5:
                writer.writerow([timestamp, "host"] + host_metrics[1:])

            # Per-container PSI
            for cid in get_container_ids():
                pid = get_container_pid(cid)
                psi_path = f"/proc/{pid}/root/sys/fs/cgroup/cpu.pressure"
                metrics = read_cpu_pressure(psi_path)
                if len(metrics) == 5:
                    writer.writerow([timestamp, cid] + metrics[1:])

            file.flush()
            time.sleep(interval_sec)

    print(f"✅ Monitoring complete. Logs saved to: {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 PSI-PerPod&host-monitoring.py <duration_seconds>")
        sys.exit(1)

    duration = int(sys.argv[1])
    monitor_psi(duration_sec=duration)
