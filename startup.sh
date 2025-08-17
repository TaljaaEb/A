#!/bin/bash
# startup.sh - Azure App Service entrypoint

echo "Starting A (SQL Monitor)..."
python3 a_sql_monitor.py &

echo "Starting B (Collector Monitor with TCP+HTTP trigger)..."
python3 b_collector_monitor.py &

# Keep the container alive (wait for any process to exit)
wait -n

