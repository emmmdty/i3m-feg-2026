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

python scripts/generate_negative_controls.py --input data/samples/seed_financial_events.jsonl --out data/processed/negative_control_stream.jsonl --seed 42

python scripts/run_sanity_checks.py --input data/processed/negative_control_stream.jsonl --out tables/sanity_check_results.csv --tex-table paper/i3m_submission/tables/table_negative_controls.tex

python scripts/run_scale_sensitivity.py --out tables/scale_sensitivity_results.csv --figure paper/i3m_submission/figures/fig_runtime_scaling.pdf --tex-table paper/i3m_submission/tables/table_scale_sensitivity.tex --seed 42 --scales 30 60 120 240

python scripts/make_submission_tables.py --ablation tables/ablation_results.csv --case-study tables/case_study_updates.csv --sanity tables/sanity_check_results.csv --scale tables/scale_sensitivity_results.csv --out-dir paper/i3m_submission/tables

bash paper/i3m_submission/build_latex.sh
```

Generated outputs, table CSVs, raw data, processed data, logs, and model artifacts are intentionally excluded from Git.
