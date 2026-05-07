# I3M Financial Event Graph 2026 Prototype

This repository contains a lightweight, reproducible rule-based prototype for an evidence-constrained financial event graph simulation short paper. It is not a financial prediction, trading signal, or investment advice system.

## Reproducible Commands

```bash
python scripts/run_demo.py
python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv
python scripts/build_case_study.py \
  --replay outputs/replay_trace.jsonl \
  --updates outputs/updates.jsonl \
  --conflicts outputs/conflicts.jsonl \
  --out tables/case_study_updates.csv
python scripts/summarize_experiment.py \
  --ablation tables/ablation_results.csv \
  --case-study tables/case_study_updates.csv \
  --replay outputs/replay_trace.jsonl \
  --out reports/stage_03/experiment_summary.md
```

Generated outputs, table CSVs, raw data, processed data, logs, and model artifacts are intentionally excluded from Git.
