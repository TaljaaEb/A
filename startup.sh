#!/bin/bash
python3 a_sql_monitor.py &
python3 b_collector_monitor.py &
wait -n
