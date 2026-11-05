#!/usr/bin/env python3

import json
import os
import sys
import pandas as pd
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
        file.write(f"{timestamp} - merge_to_dataset.py: {message}\n")
# -----------------------------

CLEAN_DIR = "clean"
DATASET_DIR = "dataset"
OUTPUT_FILE = os.path.join(DATASET_DIR, "clean_products.csv")

# Create dataset directory if it doesn't exist
os.makedirs(DATASET_DIR, exist_ok=True)

rows = []

log("Starting dataset merge")

for filename in os.listdir(CLEAN_DIR):
    if not filename.endswith(".json"):
        continue

    file_path = os.path.join(CLEAN_DIR, filename)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        rows.append(data)

        log(f"Successfully loaded: {file_path}")

    except Exception as e:
        log(f"Failed to load: {file_path}: {e}")

if not rows:
    log("No rows were loaded")
    sys.exit(1)
# ---------- pandas aggregation ----------

df = pd.DataFrame(rows)
# Standardize numeric columns; missing stock values become zero.
df["price"] = df["price"].astype(float)
df["stock"] = df["stock"].fillna(0).astype(int)
df.to_csv(OUTPUT_FILE, index=False)
log(f"Dataset written successfully: {OUTPUT_FILE}")
log("Dataset merge complete")
