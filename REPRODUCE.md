# Reproducing the I3M/EMSS Controlled-Replay Artifact

Run all commands from the repository root unless noted otherwise.

## 1. Minimal Python Environment

Use Python 3.10 or newer. The core replay scripts use the Python standard library. `matplotlib` is listed in `requirements.txt` for optional figure rendering compatibility, but the current scale-sensitivity figure writer has a standard-library fallback.

```bash
python --version
python -m pip install -r requirements.txt
```

LaTeX dependencies are not Python packages. The final PDF build requires `latexmk` and `pdflatex`.

## 2. Synthetic Controlled Replay

Regenerate the deterministic seed records and controlled perturbation stream:

```bash
python scripts/build_seed_financial_samples.py --out data/samples/seed_financial_events.jsonl --n 30 --seed 42

python scripts/generate_perturbation_stream.py --input data/samples/seed_financial_events.jsonl --out data/processed/controlled_stream.jsonl --seed 42 --duplicates 10 --conflicts 10 --updates 10 --shuffle

python scripts/run_demo.py
```

## 3. Negative Controls

```bash
python scripts/generate_negative_controls.py --input data/samples/seed_financial_events.jsonl --out data/processed/negative_control_stream.jsonl --seed 42

python scripts/run_sanity_checks.py --input data/processed/negative_control_stream.jsonl --out tables/sanity_check_results.csv --tex-table paper/i3m_submission/tables/table_negative_controls.tex
```

## 4. Metadata-Hidden Diagnostic

```bash
python scripts/run_metadata_hidden_replay.py --input data/processed/controlled_stream.jsonl --out tables/metadata_hidden_results.csv --tex-table paper/i3m_submission/tables/table_metadata_hidden.tex
```

## 5. Scale Sensitivity

```bash
python scripts/run_scale_sensitivity.py --out tables/scale_sensitivity_results.csv --figure paper/i3m_submission/figures/fig_runtime_scaling.pdf --tex-table paper/i3m_submission/tables/table_scale_sensitivity.tex --seed 42 --scales 30 60 120 240
```

## 6. Public Mini-Case

The repository includes `data/samples/public_mini_events.jsonl`, a FewFC-derived 20-record external sanity case. It is not an extraction benchmark.

Run the public mini-case if the sample file is present:

```bash
python scripts/run_public_mini_case.py --input data/samples/public_mini_events.jsonl --out tables/public_mini_case_results.csv --tex-table paper/i3m_submission/tables/table_public_mini_case.tex --trace-out outputs/public_mini_replay_trace.jsonl
```

If the sample file must be regenerated after downloading FewFC, use:

```bash
python scripts/prepare_public_mini_case.py --source fewfc --input-dir data/raw/FewFC --out data/samples/public_mini_events.jsonl --max-records 20 --seed 42
```

Do not fabricate public mini-case records if the FewFC source is unavailable or unparsable.

## 7. LaTeX PDF Build

Refresh the submission tables and rebuild the PDF:

```bash
python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv

python scripts/make_submission_tables.py --ablation tables/ablation_results.csv --case-study tables/case_study_updates.csv --sanity tables/sanity_check_results.csv --scale tables/scale_sensitivity_results.csv --metadata-hidden tables/metadata_hidden_results.csv --out-dir paper/i3m_submission/tables

bash paper/i3m_submission/build_latex.sh
```

The final PDF paths are:

- `paper/i3m_submission/manuscript.pdf`
- `paper/manuscript_i3m2026_v2.pdf`

## 8. Expected Key Outputs

- `outputs/replay_trace.jsonl`
- `outputs/updates.jsonl`
- `outputs/conflicts.jsonl`
- `tables/ablation_results.csv`
- `tables/sanity_check_results.csv`
- `tables/metadata_hidden_results.csv`
- `tables/scale_sensitivity_results.csv`
- `tables/public_mini_case_results.csv`
- `paper/i3m_submission/tables/table_ablation.tex`
- `paper/i3m_submission/tables/table_case_study_excerpt.tex`
- `paper/i3m_submission/tables/table_negative_controls.tex`
- `paper/i3m_submission/tables/table_metadata_hidden.tex`
- `paper/i3m_submission/tables/table_scale_sensitivity.tex`
- `paper/i3m_submission/tables/table_public_mini_case.tex`
- `paper/manuscript_i3m2026_v2.pdf`

## 9. Notes on Raw/Public Data

The synthetic controlled replay data is generated locally and is reproducible from the scripts above.

The full raw FewFC dataset is not committed because it is an upstream public dataset and should remain under its original repository and license terms. The committed mini-case is a small converted sanity sample with provenance fields and license notes. It is used only to check the replay path on public event text, not to report extraction accuracy.

No GPU training, model inference, market prediction, investment advice, trading signal generation, or external API call is required. Reproduction status: `no_gpu_training_required`.
