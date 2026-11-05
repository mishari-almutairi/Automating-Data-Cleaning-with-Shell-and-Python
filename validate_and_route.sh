#!/usr/bin/env bash
# List valid JSON files and copy rejected files to invalid/.

set -uo pipefail

RAW_DIR="raw"
INVALID_DIR="invalid"
VALID_FILE_LIST="valid_files.txt"

# Create required directories
mkdir -p "$INVALID_DIR" "logs"

# Clear rejected JSON copies from the previous run.
rm -f "$INVALID_DIR"/*.json 2>/dev/null

LOGS_DIR="logs"
TODAY="$(date -u +"%Y-%m-%d")"
log_file="$LOGS_DIR/$TODAY.log"

# Rebuild the valid-file list for this run.
> "$VALID_FILE_LIST"

for file in "$RAW_DIR"/*.json; do
    if [[ ! -f "$file" ]]; then
    continue
    fi
    echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') validate_and_route.sh VALIDATING $file" >> "$log_file"
    python validate_json.py "$file"
    status=$?
    if [[ "$status" -eq 0 ]]; then
        echo "$file" >> "$VALID_FILE_LIST"
        echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') validate_and_route.sh VALID $file" >> "$log_file"
    else
        cp -- "$file" "$INVALID_DIR/"
        echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') validate_and_route.sh COPIED TO INVALID $file" >> "$log_file"
    fi
done
