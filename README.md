# 📊 Resource-monitoring

This repository provides scripts for monitoring system resource usage — specifically **CPU Pressure Stall Information (PSI)** — at both the **host level** and **per-container (Docker/Kubernetes)** level.

It supports development and evaluation of **QoS-aware scheduling**, **resource-aware admission control**, and **performance debugging** for containerized applications.

---

## 📁 Files Overview

| File Name                        | Description                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| `PSI-PerPod-host-monitoring.py` | Monitors CPU PSI for each running container and the host at fixed intervals |
| `run_and_collect_logs.sh`       | Launches multiple load containers with CPU pinning and collects logs        |


---

## ⚙️ Requirements

- Python 3.x
- Docker with **cgroup v2** support
- Linux kernel **4.20+** (for PSI support)
- `sudo` privileges (to read `/proc` and `cgroup` files)

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/abmuslim/Resource-monitoring.git
cd Resource-monitoring
```

---

## ✅ Scripts & Usage

### 🔍 `PSI-PerPod-host-monitoring.py`

This script monitors CPU pressure for all running Docker containers **and** the host every 10 seconds.

#### ➤ Run

```bash
python3 PSI-PerPod-host-monitoring.py <duration_in_seconds>
```

📌 Example (monitor for 5 minutes):

```bash
python3 PSI-PerPod-host-monitoring.py 300
```

#### ➤ Output

A CSV file `psi_monitoring_log.csv` containing:

- Timestamp
- Container ID
- PSI metrics (`avg10`, `avg60`, `avg300`, `total`) for each container
- Host-level PSI metrics from `/proc/pressure/cpu`

---

### 🔧 `run_and_collect_logs.sh`

This script launches multiple load-generating containers, pins each to a specific CPU, waits, and then extracts logs.

#### ➤ Make it Executable

```bash
chmod +x run_and_collect_logs.sh
```

#### ➤ Run

```bash
./run_and_collect_logs.sh
```

#### ➤ What it Does

- Removes any existing containers with the prefix `mon_container_*`
- Starts **5 containers** using the `loadmonitor` image
- Pins each container to a **unique CPU core** using `--cpuset-cpus`
- Waits for the configured duration
- Copies logs (`core_logs.csv`) from each container into the host `./logs/` directory

#### ➤ Output

You will see:

```bash
logs/core_log_0.csv
logs/core_log_1.csv
...
```

Each log file contains application-specific metrics (e.g., CPU, latency), assuming your container generates this.

---

## 📘 Example Use Cases

- Compare **per-container CPU PSI** under different workloads
- Evaluate the impact of **CPU pinning**
- Feed PSI metrics into **QoS-aware admission control**
- Integrate with **control loops** for latency-sensitive services in Kubernetes

---

## 📩 Contributions

Issues and pull requests are welcome! Please help improve the tooling by sharing feedback or adding support for more resource metrics.
