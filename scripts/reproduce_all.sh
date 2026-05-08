#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -n "${PYTHON:-}" ]; then
  PYTHON_BIN="$PYTHON"
elif [ -x /home/tjk/miniconda3/envs/feg-dev-py310/bin/python ]; then
  PYTHON_BIN="/home/tjk/miniconda3/envs/feg-dev-py310/bin/python"
elif [ -x /home/TJK/.conda/envs/tjk-feg/bin/python ]; then
  PYTHON_BIN="/home/TJK/.conda/envs/tjk-feg/bin/python"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "No usable Python interpreter found. Set PYTHON=/path/to/python and rerun." >&2
  exit 1
fi

mkdir -p outputs tables data/processed reports/reproduce_check paper/i3m_submission/tables paper/i3m_submission/figures

echo "[1/10] Python version"
"$PYTHON_BIN" --version | tee reports/reproduce_check/python_version.txt

echo "[2/10] Build deterministic seed samples"
"$PYTHON_BIN" scripts/build_seed_financial_samples.py --out data/samples/seed_financial_events.jsonl --n 30 --seed 42

echo "[3/10] Generate controlled perturbation stream"
"$PYTHON_BIN" scripts/generate_perturbation_stream.py --input data/samples/seed_financial_events.jsonl --out data/processed/controlled_stream.jsonl --seed 42 --duplicates 10 --conflicts 10 --updates 10 --shuffle

echo "[4/10] Run controlled replay demo"
"$PYTHON_BIN" scripts/run_demo.py

echo "[5/10] Run ablation and case-study tables"
"$PYTHON_BIN" scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv
"$PYTHON_BIN" scripts/build_case_study.py --replay outputs/replay_trace.jsonl --updates outputs/updates.jsonl --conflicts outputs/conflicts.jsonl --out tables/case_study_updates.csv

echo "[6/10] Run negative controls"
"$PYTHON_BIN" scripts/generate_negative_controls.py --input data/samples/seed_financial_events.jsonl --out data/processed/negative_control_stream.jsonl --seed 42
"$PYTHON_BIN" scripts/run_sanity_checks.py --input data/processed/negative_control_stream.jsonl --out tables/sanity_check_results.csv --tex-table paper/i3m_submission/tables/table_negative_controls.tex

echo "[7/10] Run metadata-hidden diagnostic"
"$PYTHON_BIN" scripts/run_metadata_hidden_replay.py --input data/processed/controlled_stream.jsonl --out tables/metadata_hidden_results.csv --tex-table paper/i3m_submission/tables/table_metadata_hidden.tex

echo "[8/10] Run scale sensitivity"
"$PYTHON_BIN" scripts/run_scale_sensitivity.py --out tables/scale_sensitivity_results.csv --figure paper/i3m_submission/figures/fig_runtime_scaling.pdf --tex-table paper/i3m_submission/tables/table_scale_sensitivity.tex --seed 42 --scales 30 60 120 240

echo "[9/10] Run public mini-case if available"
if [ -s data/samples/public_mini_events.jsonl ]; then
  "$PYTHON_BIN" scripts/run_public_mini_case.py --input data/samples/public_mini_events.jsonl --out tables/public_mini_case_results.csv --tex-table paper/i3m_submission/tables/table_public_mini_case.tex --trace-out outputs/public_mini_replay_trace.jsonl
  echo "public_mini_case_status=ran" | tee reports/reproduce_check/public_mini_case_status.txt
else
  echo "public_mini_case_status=skipped_missing_data_samples_public_mini_events_jsonl" | tee reports/reproduce_check/public_mini_case_status.txt
  echo "Read REPRODUCE.md for FewFC download and regeneration instructions."
fi

echo "[10/10] Refresh submission tables and build LaTeX PDF"
"$PYTHON_BIN" scripts/make_submission_tables.py --ablation tables/ablation_results.csv --case-study tables/case_study_updates.csv --sanity tables/sanity_check_results.csv --scale tables/scale_sensitivity_results.csv --metadata-hidden tables/metadata_hidden_results.csv --out-dir paper/i3m_submission/tables
bash paper/i3m_submission/build_latex.sh

echo "Final PDFs:"
echo "paper/i3m_submission/manuscript.pdf"
echo "paper/manuscript_i3m2026_v2.pdf"
echo "no_gpu_training_required"
