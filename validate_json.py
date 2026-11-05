#!/usr/bin/env python3

import json
import sys
import os
import datetime

# ---------- logging ----------
LOGS_DIR = "logs"
TODAY = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
LOG_FILE = os.path.join(LOGS_DIR, f"{TODAY}.log")
os.makedirs(LOGS_DIR, exist_ok=True)


def log(message):
    """Append a UTC-timestamped message to the daily log file."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(f"{timestamp} - validate_json.py: {message}\n")
# -----------------------------

if len(sys.argv) != 2:
    log("Error: Expected exactly one file path")
    sys.exit(1)

file_path = sys.argv[1]

if not os.path.isfile(file_path):
    log(f"File not found: {file_path}")
    sys.exit(1)
if os.path.getsize(file_path) == 0:
    log(f"Empty file: {file_path}")
    sys.exit(1)
try:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

except json.JSONDecodeError as error:
    log(f"Invalid JSON: {file_path} - {error}")
    sys.exit(1)

except (OSError, UnicodeError) as error:
    log(f"Cannot read file: {file_path} - {error}")
    sys.exit(1)

if not isinstance(data, dict):
    log(f"Invalid structure: {file_path}")
    sys.exit(1)


def validate_fields(data):
    """Check required keys for nested and top-level product records."""

    if "product" in data:
        product_data = data["product"]
        required_product = ["id", "name"]
    else:
        product_data = data
        required_product = ["product_id", "name"]

    if not isinstance(product_data, dict):
        return False

    for field in required_product:
        if field not in product_data:
            return False

    required_top = ["category", "price", "metadata"]

    for field in required_top:
        if field not in data:
            return False

    return True


if not validate_fields(data):
    log(f"Missing required fields or invalid structure: {file_path}")
    sys.exit(1)

log(f"Valid JSON: {file_path}")
sys.exit(0)
