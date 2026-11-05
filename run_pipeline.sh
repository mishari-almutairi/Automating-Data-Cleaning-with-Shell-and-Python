#!/bin/bash
#
# run_pipeline.sh
#
# Purpose:
# Run the full data processing pipeline from start to finish.
#

# ---------- logging ----------
LOGS_DIR="logs"
TODAY=$(date -u +"%Y-%m-%d")
LOG_FILE="$LOGS_DIR/$TODAY.log"

mkdir -p "$LOGS_DIR"

log() {
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "$timestamp - run_pipeline.sh: $1" >> "$LOG_FILE"
}
# -----------------------------

echo "Pipeline started"
log "Pipeline started"

echo "Starting filename organization"

bash organize_files.sh

echo "Starting validation"

bash validate_and_route.sh

echo "Starting JSON processing"

python process_jsons.py

echo "Starting dataset merging"

python merge_to_dataset.py

echo "Pipeline completed successfully"
log "Pipeline completed successfully"
