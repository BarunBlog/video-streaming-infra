#!/bin/bash

# === Step 1: Define Node IPs and Ports ===
# Replace with your actual private IPs and ports
NODES=(
  "10.0.3.48:6379"
  "10.0.3.196:6379"
  "10.0.3.30:6379"
  "10.0.3.58:6379"
  "10.0.3.206:6379"
  "10.0.3.82:6379"
)

# === Step 2: Build cluster create command ===
CMD="redis-cli --cluster create"
for node in "${NODES[@]}"; do
  CMD+=" $node"
done

# === Step 3: Add replicas flag ===
#  Assign 1 replica per master
CMD+=" --cluster-replicas 1"

# === Step 4: Show and run the final command ===
echo "Running: $CMD"
yes yes | $CMD

