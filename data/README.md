# Data Preparation

This project keeps data handling lightweight and reproducible for the Stage 1 prototype.

- `data/raw/` is the local raw-data directory. Real raw data is not committed to Git.
- `data/samples/` stores small synthetic examples that can be committed for reproducible smoke runs.
- `data/processed/` stores generated local data and is not committed to Git.
- `data/processed/controlled_stream.jsonl` is the generated controlled perturbation stream for later merge, conflict, update, and replay checks.

Regenerate Stage 1 data with:

```bash
python scripts/inspect_raw_data.py --raw-dir data/raw --out outputs/raw_data_manifest.json
python scripts/build_seed_financial_samples.py --out data/samples/seed_financial_events.jsonl --n 30 --seed 42
python scripts/generate_perturbation_stream.py --input data/samples/seed_financial_events.jsonl --out data/processed/controlled_stream.jsonl --seed 42 --duplicates 10 --conflicts 10 --updates 10 --shuffle
python scripts/validate_stage1_data.py --samples data/samples/seed_financial_events.jsonl --stream data/processed/controlled_stream.jsonl --summary tables/stage1_data_summary.csv
```
