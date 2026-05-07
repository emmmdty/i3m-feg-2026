# Stage 06.5 Validation

## Validation Time

- Local time: `2026-05-07T16:37:36+08:00`
- Working directory: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- Branch: `main`

## Validation Commands

Preflight:

```bash
pwd
git branch --show-current
git status
sed -n '1,220p' AGENTS.md
sed -n '1,360p' reports/stage_06_5/stage_06_5_report.md
```

Local experiment and paper rebuild:

```bash
python scripts/build_seed_financial_samples.py --out data/samples/seed_financial_events.jsonl --n 30 --seed 42
python scripts/generate_perturbation_stream.py --input data/samples/seed_financial_events.jsonl --out data/processed/controlled_stream.jsonl --seed 42 --duplicates 10 --conflicts 10 --updates 10 --shuffle
python scripts/run_demo.py
python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv
python scripts/build_case_study.py --replay outputs/replay_trace.jsonl --updates outputs/updates.jsonl --conflicts outputs/conflicts.jsonl --out tables/case_study_updates.csv
python scripts/generate_negative_controls.py --input data/samples/seed_financial_events.jsonl --out data/processed/negative_control_stream.jsonl --seed 42
python scripts/run_sanity_checks.py --input data/processed/negative_control_stream.jsonl --out tables/sanity_check_results.csv --tex-table paper/i3m_submission/tables/table_negative_controls.tex
python scripts/run_scale_sensitivity.py --out tables/scale_sensitivity_results.csv --figure paper/i3m_submission/figures/fig_runtime_scaling.pdf --tex-table paper/i3m_submission/tables/table_scale_sensitivity.tex --seed 42 --scales 30 60 120 240
python scripts/make_submission_tables.py --ablation tables/ablation_results.csv --case-study tables/case_study_updates.csv --sanity tables/sanity_check_results.csv --scale tables/scale_sensitivity_results.csv --out-dir paper/i3m_submission/tables
bash paper/i3m_submission/build_latex.sh
```

PDF and risk checks:

```bash
pdfinfo paper/manuscript_i3m2026_v2.pdf
pdftotext paper/manuscript_i3m2026_v2.pdf reports/stage_06_5/manuscript_i3m2026_v2_validation.txt
rg -n -i 'GPT-generated|Codex-generated|AI-generated|state-of-the-art method|outperform|superior performance|stock prediction|trading signal|buy recommendation|sell recommendation|investment advice|Instructions to Authors|energy demand|Insert here your abstract text' reports/stage_06_5/manuscript_i3m2026_v2_validation.txt
pdftoppm -png -r 120 paper/manuscript_i3m2026_v2.pdf /tmp/i3m_stage065_final_page
```

## Local Experiment Results

- `build_seed_financial_samples.py`: PASS, wrote 30 seed records.
- `generate_perturbation_stream.py`: PASS, wrote 70 controlled stream records.
- `run_demo.py`: PASS, processed 70 records, 40 active events, 70 version logs, 10 conflicts.
- `run_ablation.py`: PASS, wrote four rows: `Direct`, `Schema`, `Evidence`, `Full`.
- `Full` ablation row: schema `1.000000`, evidence `1.000000`, merge `1.000000`, conflict `1.000000`, replay `1.000000`.
- `build_case_study.py`: PASS, wrote 70 CSV rows including header; submission excerpt is capped at 6 table rows.
- `generate_negative_controls.py`: PASS, wrote 20 negative-control records.
- `run_sanity_checks.py`: PASS, total cases `20`, schema rejected `10`, evidence rejected `5`, invalid dates rejected `5`, unknown operator handled `5`, crashes `0`.
- `run_scale_sensitivity.py`: PASS, scales `30 60 120 240`, replay completeness `1.000` at every scale.
- `make_submission_tables.py`: PASS, regenerated all four submission tables with 3-decimal numeric formatting.

## Server Reproduction

Server reproduction evidence was checked in `reports/stage_06_5/stage_06_5_report.md`.

- Server path: `/home/TJK/i3m_financial_event_graph_2026`
- Large outputs: `/data/TJK/i3m/outputs`, `/data/TJK/i3m/tables`, `/data/TJK/i3m/reports/stage_06_5`
- `run_demo.py`: PASS on server.
- `run_ablation.py`: PASS on server.
- `run_sanity_checks.py`: PASS on server.
- `run_scale_sensitivity.py`: PASS on server.
- `no_gpu_training_required`: recorded.
- `training: no`: recorded.
- `model inference: no`: recorded.
- `external API calls: none`: recorded.

## LaTeX and PDF Validation

- Required submission files: PASS.
- Build command: `bash paper/i3m_submission/build_latex.sh`
- Build route: PASS, `latexmk -pdf` using `pdfTeX-1.40.22`.
- Chrome HTML fallback: PASS, not used.
- ReportLab fallback: PASS, not used.
- Hard-coded `/home/tjk/.codex` path in `build_latex.sh`: PASS, not present.
- Template: PASS, `\documentclass[3p,times,procedia]{elsarticle}` with `\usepackage{ecrc}`.
- Template placeholders: PASS, no `Instructions to Authors`, `Insert here your abstract text`, or example energy-demand references found.
- PDF output: `paper/manuscript_i3m2026_v2.pdf`
- PDF pages: `7`, within the 6--8 page target.
- Visual render check: PASS. First-page footer overlap was corrected by starting the main text after `\clearpage`; tables and figures render without obvious overflow.
- LaTeX log: no fatal errors, no overfull hbox. Remaining overfull vbox warnings are template/frontmatter layout warnings and were visually checked after rendering.

## Manuscript Content and Risk Check

- Title uses the simulation prototype framing: PASS.
- Abstract uses conservative claims and does not overstate extraction or market utility: PASS.
- Clear simulation model: PASS.
- `G_t = (V_t, E_t, L_t)`: PASS.
- `S_t \rightarrow S_{t+1}`: PASS.
- Five operators are described: add event nodes, merge duplicate records, update slots, mark unresolved conflicts, append version logs.
- Controlled perturbation stream: PASS.
- Negative-control sanity check: PASS.
- Scale sensitivity: PASS.
- Limitations discussion: PASS.
- Not extraction SOTA: PASS.
- Not financial prediction: PASS.
- No model training, GPU inference, external API calls, or model copying: PASS.
- PDF text risk scan: PASS. No banned phrases were found in `reports/stage_06_5/manuscript_i3m2026_v2_validation.txt`.

## Final Decision

Stage 06.5 validation: PASS.

Stage 06.5 is accepted and may proceed to Stage 7 after the validation commit is created.

Commit hash after submission commit: see final validation report.
