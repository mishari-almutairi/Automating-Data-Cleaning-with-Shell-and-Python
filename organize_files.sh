#!/usr/bin/env bash
# Normalize filenames, append UTC timestamps, and copy inputs to raw/.

set -uo pipefail

RAW_DIR="raw"
DUMPS_DIR="json_dump"

# --- Daily logging setup ---
LOGS_DIR="logs"
TODAY="$(date -u +"%Y-%m-%d")"
log_file="$LOGS_DIR/$TODAY.log"
mkdir -p "$LOGS_DIR"

echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") organize_files.sh START" >> "$log_file"
# ----------------------------

# Create raw directory if it doesn't exist
mkdir -p "$RAW_DIR"

# Clear previous JSON copies before rebuilding raw/.
rm -f "$RAW_DIR"/*.json 2>/dev/null

# Skip the loop when the input directory is empty.
shopt -s nullglob

for src in "$DUMPS_DIR"/*; do

    base="$(basename "$src")"

    if [[ "$base" == "README.md" ]]; then
        continue
    fi
    # Lowercase the name and replace spaces and hyphens with underscores.
    newname="$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]')"

    newname="$(printf '%s' "$newname" | sed 's/[- ]/_/g')"

    # Replace the original extension with a UTC timestamp and .json.
    name_without_ext="${newname%.*}"

    ts="$(date -u +"%Y%m%dT%H%M%SZ")"

    final_name="${name_without_ext}_${ts}.json"

    cp -- "$src" "$RAW_DIR/$final_name"
    echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') organize_files.sh COPY $src -> $RAW_DIR/$final_name" >> "$log_file"
done

echo "$(date -u +'%Y-%m-%dT%H:%M:%SZ') organize_files.sh FINISH" >> "$log_file"
