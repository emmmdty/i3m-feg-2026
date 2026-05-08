#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ -n "${PYTHON:-}" ]; then
  PYTHON_BIN="$PYTHON"
elif [ -x /home/tjk/miniconda3/envs/feg-dev-py310/bin/python ]; then
  PYTHON_BIN="/home/tjk/miniconda3/envs/feg-dev-py310/bin/python"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
else
  echo "No usable Python interpreter found. Set PYTHON=/path/to/python and rerun." >&2
  exit 1
fi

mkdir -p outputs tables data/processed paper/i3m_submission/tables paper/i3m_submission/figures

echo "[1/10] Prepare deterministic controlled data"
"$PYTHON_BIN" scripts/prepare_synthetic_data.py

echo "[2/10] Run oracle-controlled replay"
"$PYTHON_BIN" scripts/run_controlled_replay.py

echo "[3/10] Run controlled replay diagnostics"
"$PYTHON_BIN" scripts/run_ablation.py

echo "[4/10] Run metadata-hidden diagnostic"
"$PYTHON_BIN" scripts/run_metadata_hidden.py

echo "[5/10] Run negative controls"
"$PYTHON_BIN" scripts/run_negative_controls.py

echo "[6/10] Run invariant checks"
"$PYTHON_BIN" scripts/run_invariant_checks.py

echo "[7/10] Run scale sanity check"
"$PYTHON_BIN" scripts/run_scale_sensitivity.py

echo "[8/10] Run public mini-case"
"$PYTHON_BIN" scripts/run_public_mini_case.py

echo "[9/10] Refresh tables and figures"
"$PYTHON_BIN" scripts/make_tables.py
"$PYTHON_BIN" scripts/make_figures.py

echo "[10/10] Build LaTeX PDF"
bash paper/i3m_submission/build_latex.sh

cat > outputs/reproduce_summary.txt <<'EOF'
no_gpu_training_required
training=no
model_inference=no
external_api_calls=none
final_pdf=paper/manuscript_i3m2026_v2.pdf
EOF

echo "Final PDFs:"
echo "paper/i3m_submission/manuscript.pdf"
echo "paper/manuscript_i3m2026_v2.pdf"
echo "no_gpu_training_required"
