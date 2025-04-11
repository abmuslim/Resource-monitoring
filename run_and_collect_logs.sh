#!/bin/bash

IMAGE_NAME="loadmonitor"
CONTAINER_PREFIX="mon_container"
DURATION_MINUTES=10
THREADS=2

# Step 1: Clean any old containers
echo "🧹 Cleaning up old containers..."
for i in {0..4}; do
  docker rm -f ${CONTAINER_PREFIX}_$i 2>/dev/null
done

# Step 2: Run containers pinned to individual CPUs with private cgroup namespaces
echo "🚀 Starting containers..."
for i in {0..4}; do
  echo " - Starting ${CONTAINER_PREFIX}_$i on CPU $i..."
  docker run -d \
    --cpuset-cpus="$i" \
    --cgroupns=private \
    --name "${CONTAINER_PREFIX}_$i" \
    "$IMAGE_NAME" "$DURATION_MINUTES" "$THREADS"
done

# Step 3: Wait for containers to finish
echo "⏳ Waiting for containers to finish..."
sleep $(($DURATION_MINUTES * 60 + 5))  # Add a small buffer

# Step 4: Copy logs to host
echo "📤 Copying logs from containers..."
mkdir -p logs
for i in {0..4}; do
  docker cp ${CONTAINER_PREFIX}_$i:/usr/app/src/core_logs.csv logs/core_log_$i.csv
done

echo "✅ Done. Logs saved in ./logs/core_log_*.csv"

