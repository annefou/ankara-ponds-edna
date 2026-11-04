#!/usr/bin/env bash
# Starts run_pema_all.sh fully detached from the terminal (setsid, no stdin), so it is not paused when it
# writes or reads the terminal. Downloads the missing Turkish runs, then runs PEMA (resuming finished steps).
# Progress: tail -f full_run.log
D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # this repository
setsid nohup bash "$D/run_pema_all.sh" < /dev/null > "$D/full_run.log" 2>&1 &
echo "Started (PID $!). Log: $D/full_run.log"
