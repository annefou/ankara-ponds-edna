#!/usr/bin/env bash
# 1. Stops the paused full run (script, pixi and Nextflow processes of ankara-ponds-edna; state T after it
#    touched the terminal). Matches only processes whose command line contains run_pema_all.sh or pema_all.yaml.
# 2. Restarts it detached (start_full_run.sh): missing runs are downloaded with pauses (ENA 403s), finished
#    downloads are kept, PEMA resumes.
D=/opt/vth/OpenAIRE_Alien_AI_Hackathon/ankara-ponds-edna
PIDS=$(pgrep -f "$D/run_pema_all.sh|pema_all.yaml" | grep -v "^$$\$" || true)
if [ -n "$PIDS" ]; then
  echo "Stopping: $PIDS"
  kill -CONT $PIDS 2>/dev/null; kill -TERM $PIDS 2>/dev/null
  sleep 5
  kill -KILL $PIDS 2>/dev/null || true
fi
rm -f "$D/pema/.nextflow/cache/"*/db/LOCK 2>/dev/null || true
bash "$D/start_full_run.sh"
