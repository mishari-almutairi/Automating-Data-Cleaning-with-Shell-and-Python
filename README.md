# Automating Data Cleaning with Shell and Python

A learning project that turns inconsistent JSON product records into a single CSV dataset using Bash, Python, and pandas. The input data is fictional and intended for practice.

The pipeline organizes filenames, validates JSON records, normalizes their fields, archives processed inputs, and merges the cleaned records. Each stage writes UTC-timestamped messages to a daily log file.

## Requirements

- Python 3, available as `python`.
- pandas, listed in [requirements.txt](requirements.txt).
- Bash and standard Unix utilities, including `date`, `basename`, `tr`, `sed`, `cp`, and `rm`.

Use a Bash environment on Linux or macOS, or a suitable environment on Windows such as WSL or Git Bash. Run the shell scripts from Bash.

## Run the project

Open a terminal in the project directory. All paths are relative to that directory.

Install the Python dependency:

```bash
python -m pip install -r requirements.txt
```

Keep the fictional source files in `json_dump/`, then run:

```bash
bash run_pipeline.sh
```

The resulting dataset is written to `dataset/clean_products.csv`. Daily logs are written to `logs/YYYY-MM-DD.log`, using the UTC date.

The pipeline creates its output directories. Filename organization clears existing JSON files from `raw/`; validation clears JSON files from `invalid/` and resets `valid_files.txt`; processing clears JSON files from `clean/` and `archive/`. A successful merge overwrites the dataset CSV. Daily logs are appended to, and `json_dump/` is left unchanged.

## Pipeline stages

| Order | Script | What it does |
| --- | --- | --- |
| 1 | `organize_files.sh` | Lowercases filenames, replaces spaces and hyphens with underscores, and copies inputs to `raw/` with UTC timestamps and a `.json` extension. Skips `README.md`. |
| 2 | `validate_and_route.sh` | Calls `validate_json.py` for each raw JSON file, lists accepted paths in `valid_files.txt`, and copies rejected files to `invalid/`. |
| 3 | `process_jsons.py` | Normalizes accepted records into `clean/` and copies successfully processed originals into `archive/`. |
| 4 | `merge_to_dataset.py` | Loads cleaned records with pandas, converts numeric columns, and writes `dataset/clean_products.csv` without a row index. |

`run_pipeline.sh` runs these stages in order. It does not stop automatically when a stage fails, so check the logs and output files when verifying a run.

## Input and normalization

Validation expects a JSON object containing `category`, `price`, and `metadata`, plus either top-level `product_id` and `name` fields or a nested `product` object containing `id` and `name`. It checks required keys and product structure; it does not enforce every field's type or value.

For example:

```json
{
  "product_id": "DEMO-001",
  "name": "Desk Lamp",
  "category": "home",
  "price": "29.99",
  "metadata": {
    "color": "white",
    "stock": 12,
    "created_at": "2026-01-10T09:00:00Z"
  }
}
```

Normalization produces these fields:

| Field | Source or behavior |
| --- | --- |
| `product_id` | Top-level `product_id`, otherwise `product.id`. |
| `name` | Top-level `name`, otherwise `product.name`. |
| `category` | Top-level `category`; the normalizer defaults to `unknown` when absent. Validation currently requires this key. |
| `price` | Converted to a float; missing or unconvertible values become `0.0`. |
| `color` | `metadata.color`; absent values become JSON `null`. |
| `stock` | `metadata.stock`, defaulting to `0`; missing values become zero during merging, then the column is converted to integers. |
| `created_at` | `metadata.created_at`, falling back to `metadata.created`. |

Accepted records still need metadata and stock values compatible with processing and merging. Check the logs for records that fail at a later stage.

## Example output

[examples/clean_products_sample.csv](examples/clean_products_sample.csv) contains three illustrative, fictional records showing the output columns. It is a fixed example prepared for this repository, rather than an export from a pipeline run. Actual rows depend on the files in `json_dump/`.

## Repository contents

```text
.
|-- .gitignore
|-- README.md
|-- requirements.txt
|-- examples/
|   `-- clean_products_sample.csv
|-- json_dump/                 # Fictional source data
|-- organize_files.sh
|-- validate_and_route.sh
|-- validate_json.py
|-- process_jsons.py
|-- merge_to_dataset.py
`-- run_pipeline.sh
```

The generated directories `raw/`, `clean/`, `invalid/`, `archive/`, `dataset/`, and `logs/`, along with `valid_files.txt`, Python bytecode, and local virtual environments, are excluded by `.gitignore`. Source data and the fixed example CSV are included.

## Verify a run

This project does not include an automated test suite. After running the pipeline, check that:

- `json_dump/` still contains the original inputs.
- `raw/` contains copies with normalized, timestamped filenames.
- Rejected files appear in `invalid/`, and accepted paths appear in `valid_files.txt`.
- Successfully normalized records appear in `clean/`, with original copies in `archive/`.
- `dataset/clean_products.csv` contains the expected columns and records.
- The daily log records each stage and any processing errors.
