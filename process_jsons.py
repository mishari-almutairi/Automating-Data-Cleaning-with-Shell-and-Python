#!/usr/bin/env python3

import json
import os
import shutil
import datetime
import sys
# ---------- logging ----------
LOGS_DIR = "logs"
TODAY = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOGS_DIR, f"{TODAY}.log")
os.makedirs(LOGS_DIR, exist_ok=True)


def log(message):
    """Append a UTC-timestamped message to the daily log file."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} - process_jsons.py: {message}\n")
# -----------------------------

RAW_DIR = "raw"
CLEAN_DIR = "clean"
ARCHIVE_DIR = "archive"
VALID_FILES = "valid_files.txt"

os.makedirs(CLEAN_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Clear previous JSON outputs before rebuilding clean/ and archive/.
for _f in os.listdir(CLEAN_DIR):
    if _f.endswith(".json"):
        os.remove(os.path.join(CLEAN_DIR, _f))
for _f in os.listdir(ARCHIVE_DIR):
    if _f.endswith(".json"):
        os.remove(os.path.join(ARCHIVE_DIR, _f))

# ---------- load valid file list ----------

if not os.path.isfile(VALID_FILES):
    log(f"File not found: {VALID_FILES}")
    sys.exit(1)

files = []

with open(VALID_FILES, "r", encoding="utf-8") as f:
    for line in f:
        file_path = line.strip()

        if file_path:
            files.append(file_path)

log(f"Processing {len(files)} files")

# ---------- normalize one JSON ----------

def normalize_json(data):
    """Normalize a single JSON record into a consistent structure."""

    cleaned = {}

    # Accept product identifiers and names at the top level or under product.
    if "product_id" in data:
        cleaned["product_id"] = data["product_id"]
    else:
        cleaned["product_id"] = data["product"]["id"]

    if "name" in data:
        cleaned["name"] = data["name"]
    else:
        cleaned["name"] = data["product"]["name"]

    cleaned["category"] = data.get("category", "unknown")

    # Use zero when the price is missing or cannot be converted.
    try:
        cleaned["price"] = float(data.get("price", 0.0))
    except (ValueError, TypeError):
        cleaned["price"] = 0.0

    metadata = data.get("metadata", {})

    cleaned["color"] = metadata.get("color")
    cleaned["stock"] = metadata.get("stock", 0)

    # Support both timestamp keys used by the source records.
    cleaned["created_at"] = metadata.get("created_at", metadata.get("created"))
    return cleaned


# ---------- process each file ----------

for file_path in files:

    filename = os.path.basename(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        log(f"Failed to read {file_path}: {error}")
        continue

    try:
        cleaned_data = normalize_json(data)

        clean_path = os.path.join(CLEAN_DIR, filename)

        with open(clean_path, "w", encoding="utf-8") as file:
            json.dump(cleaned_data, file, indent=2)

    except (OSError, TypeError, ValueError, KeyError) as error:
        log(f"Failed to process {file_path}: {error}")
        continue

    log(f"Cleaned file written: {clean_path}")
    # Archive the original only after the cleaned JSON has been written.
    archive_path = os.path.join(ARCHIVE_DIR, filename)

    try:
        shutil.copy(file_path, archive_path)

    except OSError as error:
        log(f"Failed to archive {file_path}: {error}")
        continue

    log(f"Archived file: {archive_path}")

log("Processing complete")
