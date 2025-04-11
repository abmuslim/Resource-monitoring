import os
import time
import csv
import subprocess
import sys

warned_pids = set()

def get_container_info():
    output = subprocess.check_output("docker ps --format '{{.ID}} {{.Names}}'", shell=True).decode().strip()
    info = {}
    for line in output.splitlines():
        cid, name = line.split()
        pid = subprocess.check_output(f"docker inspect --format '{{{{.State.Pid}}}}' {cid}", shell=True).decode().strip()
        info[name] = int(pid)
    return info

def find_psi_path(pid):
    root = f"/proc/{pid}/root/sys/fs/cgroup"
    for dirpath, _, filenames in os.walk(root):
        if "cpu.pressure" in filenames:
            return os.path.join(dirpath, "cpu.pressure")
    return None

def read_avg60_from_cgroup(pid):
    psi_path = find_psi_path(pid)
    if not psi_path:
        if pid not in warned_pids:
            print(f"[WARN] Could not locate cpu.pressure for PID {pid}")
            warned_pids.add(pid)
        return 0.0
    try:
        with open(psi_path, "r") as f:
            for line in f:
                if line.startswith("some"):
                    for part in line.split():
                        if part.startswith("avg60="):
                            return float(part.split("=")[1])
    except Exception as e:
        print(f"[ERROR] Reading PSI from {psi_path}: {e}")
        return 0.0
    return 0.0

def read_avg60_host():
    try:
        with open("/proc/pressure/cpu", "r") as f:
            for line in f:
                if line.startswith("some"):
                    for part in line.split():
                        if part.startswith("avg60="):
                            return float(part.split("=")[1])
    except Exception as e:
        print(f"[WARN] Failed to read host PSI: {e}")
        return 0.0
    return 0.0

def monitor_psi(duration_sec, interval_sec=10):
    fieldnames = ["seconds", "host"]
    container_names_set = set()
    rows = []

    start_time = time.time()
    while time.time() - start_time < duration_sec:
        current_sec = int(time.time() - start_time)
        container_info = get_container_info()

        row = {"seconds": current_sec}

        for name, pid in container_info.items():
            row[name] = read_avg60_from_cgroup(pid)

            if name not in container_names_set:
                container_names_set.add(name)
                fieldnames.insert(-1, name)  # insert before 'host'

        row["host"] = read_avg60_host()
        rows.append(row)

        time.sleep(interval_sec)

    # Ensure all rows contain all fields
    for row in rows:
        for field in fieldnames:
            if field not in row:
                row[field] = ""

    with open("avg60_psi_log.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("⚠️  This script must be run with sudo.")
        sys.exit(1)
    if len(sys.argv) < 2:
        print("Usage: sudo python3 PSI-PerPod-host-monitoring.py <duration_in_seconds>")
        sys.exit(1)

    duration = int(sys.argv[1])
    monitor_psi(duration)
