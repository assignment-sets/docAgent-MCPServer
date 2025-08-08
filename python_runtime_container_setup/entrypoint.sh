#!/bin/bash
set -e

# Start the watcher in background
python3 /app/watcher.py &

# Small delay to ensure watcher is set up before code runs
sleep 1

# Run the user code
python3 /app/code.py

# Add small delay to ensure writes are flushed
sleep 1

# Signal to the watcher that code execution is done
touch /app/.done

# Wait for watcher to exit
wait