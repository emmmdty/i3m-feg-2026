# Stage 06.5 Report: Experimental Strengthening and I3M/EMSS LaTeX Reconstruction

## 1. Why Stage 06.5 Was Inserted

Stage 06.5 was inserted because the Stage 06 manuscript and PDF were useful as a draft package, but not yet suitable as an I3M/EMSS LaTeX submission artifact.

Stage 06 had two main weaknesses:

- The main controlled replay experiment reported perfect controlled-stream metrics, so the paper needed explicit negative-control and scale-sensitivity checks to make the deterministic nature clear.
- `paper/manuscript_v1.pdf` was generated through a Pandoc HTML plus headless Chrome route after direct Pandoc PDF failed. It was not a PDF compiled from the official `elsarticle`/`ecrc` LaTeX template.

## 2. Preflight

Preflight checks before Stage 06.5 edits:

- `pwd`: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- `git status`: clean before edits
- `AGENTS.md`: checked

The project remains a reproducible simulation-oriented prototype for evidence-constrained financial event streams.

## 3. Official LaTeX Template Check

Template directory inspected:

- `paper/templates/EMSS2026_Paper_Template/PROCS_I3M 2025.tex`

The template source contains the required Procedia/Elsevier structure:

- `\documentclass[3p,times,procedia]{elsarticle}`
- `\usepackage{ecrc}`
- `\journalname{Procedia Computer Science}`
- `\dochead{38th European Modeling \& Simulation Symposium (EMSS 2026) ... I3M 2026}`
- `\begin{frontmatter}`
- `\begin{abstract}`
- `\begin{keyword}`

The original template file was not overwritten. The Stage 06.5 manuscript was built in `paper/i3m_submission/`.

Template support files copied into the submission workspace:

- `paper/i3m_submission/ecrc.sty`
- `paper/i3m_submission/elsevier-logo-3p.pdf`
- `paper/i3m_submission/SDlogo-3p.pdf`
- `paper/i3m_submission/Procs.pdf`

This was necessary because the first `latexmk` run stopped on a missing template logo file.

## 4. New Experimental Blocks

### E1. Main Controlled Replay

Commands run locally:

```bash
python scripts/build_seed_financial_samples.py \
  --out data/samples/seed_financial_events.jsonl \
  --n 30 \
  --seed 42

python scripts/generate_perturbation_stream.py \
  --input data/samples/seed_financial_events.jsonl \
  --out data/processed/controlled_stream.jsonl \
  --seed 42 \
  --duplicates 10 \
  --conflicts 10 \
  --updates 10 \
  --shuffle

python scripts/run_demo.py

python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out tables/ablation_results.csv

python scripts/build_case_study.py \
  --replay outputs/replay_trace.jsonl \
  --updates outputs/updates.jsonl \
  --conflicts outputs/conflicts.jsonl \
  --out tables/case_study_updates.csv
```

Observed local results:

- seed samples: 30
- controlled stream records: 70
- active events: 40
- version logs: 70
- conflicts: 10
- case-study rows: 70
- ablation rows: `Direct`, `Schema`, `Evidence`, `Full`
- `Full`: schema `1.000000`, evidence `1.000000`, merge `1.000000`, conflict `1.000000`, replay `1.000000`

### E2. Negative-Control Sanity Check

New scripts:

- `scripts/generate_negative_controls.py`
- `scripts/run_sanity_checks.py`

Commands run locally:

```bash
python scripts/generate_negative_controls.py \
  --input data/samples/seed_financial_events.jsonl \
  --out data/processed/negative_control_stream.jsonl \
  --seed 42

python scripts/run_sanity_checks.py \
  --input data/processed/negative_control_stream.jsonl \
  --out tables/sanity_check_results.csv \
  --tex-table paper/i3m_submission/tables/table_negative_controls.tex
```

Observed local results:

| metric | value |
| --- | ---: |
| total_cases | 20 |
| schema_rejected | 10 |
| evidence_rejected | 5 |
| invalid_date_rejected | 5 |
| unknown_operator_handled | 5 |
| crash_count | 0 |

Generated artifacts:

- `data/processed/negative_control_stream.jsonl` ignored by Git
- `tables/sanity_check_results.csv` ignored by Git
- `paper/i3m_submission/tables/table_negative_controls.tex`

### E3. Scale Sensitivity

New script:

- `scripts/run_scale_sensitivity.py`

Command run locally:

```bash
python scripts/run_scale_sensitivity.py \
  --out tables/scale_sensitivity_results.csv \
  --figure paper/i3m_submission/figures/fig_runtime_scaling.pdf \
  --tex-table paper/i3m_submission/tables/table_scale_sensitivity.tex \
  --seed 42 \
  --scales 30 60 120 240
```

Observed local results:

| scale | num_records | active_events | version_logs | conflicts | replay_completeness | runtime_ms_per_record | total_runtime_ms |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 30 | 70 | 40 | 70 | 10 | 1.000000 | 0.013626 | 0.953807 |
| 60 | 140 | 80 | 140 | 20 | 1.000000 | 0.012763 | 1.786868 |
| 120 | 280 | 160 | 280 | 40 | 1.000000 | 0.021954 | 6.147123 |
| 240 | 560 | 320 | 560 | 80 | 1.000000 | 0.020474 | 11.465444 |

Runtime varies slightly across scales and should be interpreted only as lightweight scaling behavior under controlled streams.

Generated artifacts:

- `tables/scale_sensitivity_results.csv` ignored by Git
- `paper/i3m_submission/tables/table_scale_sensitivity.tex`
- `paper/i3m_submission/figures/fig_runtime_scaling.pdf`

### E4. Compact Submission Tables

New script:

- `scripts/make_submission_tables.py`

Command run locally:

```bash
python scripts/make_submission_tables.py \
  --ablation tables/ablation_results.csv \
  --case-study tables/case_study_updates.csv \
  --sanity tables/sanity_check_results.csv \
  --scale tables/scale_sensitivity_results.csv \
  --out-dir paper/i3m_submission/tables
```

Generated LaTeX tables:

- `paper/i3m_submission/tables/table_ablation.tex`
- `paper/i3m_submission/tables/table_case_study_excerpt.tex`
- `paper/i3m_submission/tables/table_negative_controls.tex`
- `paper/i3m_submission/tables/table_scale_sensitivity.tex`

Formatting policy:

- LaTeX `tabular` / `tabular*`
- decimal values rounded to 3 decimals in paper tables
- non-applicable values rendered as `--`
- case-study excerpt capped at 6 rows

## 5. LaTeX Manuscript Reconstruction

New submission files:

- `paper/i3m_submission/manuscript.tex`
- `paper/i3m_submission/references.bib`
- `paper/i3m_submission/build_latex.sh`
- `paper/i3m_submission/manuscript.pdf`
- `paper/manuscript_i3m2026_v2.pdf`

The manuscript uses the official `elsarticle`/`ecrc` Procedia structure and does not reuse Markdown-to-PDF fallback generation.

Build command:

```bash
bash paper/i3m_submission/build_latex.sh
```

Build result:

- `latexmk`: success
- PDF pages: 7
- `paper/i3m_submission/manuscript.pdf`: generated
- `paper/manuscript_i3m2026_v2.pdf`: generated

PDF metadata:

- title: `A Reproducible Versioned Event Graph Simulation Prototype for Evidence-Constrained Financial Event Streams`
- producer: `pdfTeX-1.40.22`
- pages: 7
- encrypted: no

LaTeX diagnostics from final build:

- fatal error: none
- unresolved citations: none
- unresolved references: none
- LaTeX warning: one template warning about `fleqn.clo` replacing obsolete `fleqn.sty`
- overfull hbox: no
- overfull vbox: yes, two first-page/template layout warnings
- underfull hbox/vbox: yes, table/frontmatter layout warnings

## 6. Text Risk Check

Command:

```bash
pdftotext paper/manuscript_i3m2026_v2.pdf reports/stage_06_5/manuscript_i3m2026_v2.txt
```

The generated text was scanned against the user-provided banned phrase list.

Result: PASS. No banned phrases were found in the PDF text.

## 7. Server Reproduction

Server connection and sync were completed after the SSH alias became reachable.

Sync command:

```bash
rsync -avz \
  --exclude '.git/' \
  --exclude 'data/raw/' \
  --exclude 'data/processed/' \
  --exclude 'outputs/' \
  --exclude 'logs/' \
  --exclude 'tables/*.csv' \
  --exclude 'models/' \
  ./ gpu-4090:/home/TJK/i3m_financial_event_graph_2026/
```

Server working directory:

- `/home/TJK/i3m_financial_event_graph_2026`

Server large-output directories:

- `/data/TJK/i3m/outputs`
- `/data/TJK/i3m/tables`
- `/data/TJK/i3m/reports/stage_06_5`

Server commands run:

```bash
cd /home/TJK/i3m_financial_event_graph_2026

mkdir -p data/processed /data/TJK/i3m/outputs /data/TJK/i3m/tables /data/TJK/i3m/reports/stage_06_5

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/build_seed_financial_samples.py \
  --out data/samples/seed_financial_events.jsonl \
  --n 30 \
  --seed 42

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/generate_perturbation_stream.py \
  --input data/samples/seed_financial_events.jsonl \
  --out data/processed/controlled_stream.jsonl \
  --seed 42 \
  --duplicates 10 \
  --conflicts 10 \
  --updates 10 \
  --shuffle

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_demo.py \
  --outputs-dir /data/TJK/i3m/outputs

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out /data/TJK/i3m/tables/ablation_results.csv

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/build_case_study.py \
  --replay /data/TJK/i3m/outputs/replay_trace.jsonl \
  --updates /data/TJK/i3m/outputs/updates.jsonl \
  --conflicts /data/TJK/i3m/outputs/conflicts.jsonl \
  --out /data/TJK/i3m/tables/case_study_updates.csv

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/generate_negative_controls.py \
  --input data/samples/seed_financial_events.jsonl \
  --out data/processed/negative_control_stream.jsonl \
  --seed 42

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_sanity_checks.py \
  --input data/processed/negative_control_stream.jsonl \
  --out /data/TJK/i3m/tables/sanity_check_results.csv \
  --tex-table /data/TJK/i3m/reports/stage_06_5/table_negative_controls.tex

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_scale_sensitivity.py \
  --out /data/TJK/i3m/tables/scale_sensitivity_results.csv \
  --figure /data/TJK/i3m/reports/stage_06_5/fig_runtime_scaling.pdf \
  --tex-table /data/TJK/i3m/reports/stage_06_5/table_scale_sensitivity.tex \
  --seed 42 \
  --scales 30 60 120 240
```

Observed server results:

- `run_demo.py`: processed 70 records, active events 40, version logs 70, conflicts 10.
- `run_ablation.py`: wrote `/data/TJK/i3m/tables/ablation_results.csv`.
- `build_case_study.py`: wrote `/data/TJK/i3m/tables/case_study_updates.csv` with 70 rows.
- `generate_negative_controls.py`: wrote 20 negative-control records.
- `run_sanity_checks.py`: wrote `/data/TJK/i3m/tables/sanity_check_results.csv`; `crash_count` was 0.
- `run_scale_sensitivity.py`: wrote `/data/TJK/i3m/tables/scale_sensitivity_results.csv`, `/data/TJK/i3m/reports/stage_06_5/table_scale_sensitivity.tex`, and `/data/TJK/i3m/reports/stage_06_5/fig_runtime_scaling.pdf`.

Server ablation CSV:

| method | schema | evidence | merge | conflict | replay | ms/record | records |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Direct | 1.000000 | 1.000000 | NA | NA | NA | 0.001858 | 70 |
| Schema | 1.000000 | 1.000000 | NA | NA | NA | 0.003194 | 70 |
| Evidence | 1.000000 | 1.000000 | NA | NA | NA | 0.004742 | 70 |
| Full | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.028823 | 70 |

Server negative-control CSV:

| total_cases | schema_rejected | evidence_rejected | invalid_date_rejected | unknown_operator_handled | crash_count |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 20 | 10 | 5 | 5 | 5 | 0 |

Server scale-sensitivity CSV:

| scale | num_records | active_events | version_logs | conflicts | replay_completeness | runtime_ms_per_record | total_runtime_ms |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 30 | 70 | 40 | 70 | 10 | 1.000000 | 0.028819 | 2.017325 |
| 60 | 140 | 80 | 140 | 20 | 1.000000 | 0.027685 | 3.875918 |
| 120 | 280 | 160 | 280 | 40 | 1.000000 | 0.032911 | 9.215118 |
| 240 | 560 | 320 | 560 | 80 | 1.000000 | 0.037487 | 20.992499 |

Small server report artifacts synced back to:

- `reports/stage_06_5/server_data_reports/table_negative_controls.tex`
- `reports/stage_06_5/server_data_reports/table_scale_sensitivity.tex`
- `reports/stage_06_5/server_data_reports/fig_runtime_scaling.pdf`
- `reports/stage_06_5/server_data_reports/server_run_status.txt`

Runtime values differ from local values because they were measured in a different runtime environment. This report treats them as lightweight controlled-stream timing evidence, not as a high-scalability claim.

## 8. Training and GPU Status

- no_gpu_training_required
- training: no
- GPU training: no
- model inference: no
- external API calls: none
- server GPU use: not attempted

## 9. Git Status

No Git commit was created.

Generated files under these ignored paths are not intended for commit:

- `data/processed/*`
- `outputs/*`
- `tables/*.csv`
- LaTeX auxiliary files under `paper/i3m_submission/`

Current stage source and paper deliverables remain uncommitted for user acceptance.

## 10. Recommendation

Stage 06.5 is ready for user acceptance review:

- new experiments generated locally
- requested server reproduction completed
- `manuscript.tex` generated
- true LaTeX PDF compiled successfully
- PDF page count is within the 6--8 page target
- PDF text risk check passed

This stage has not been committed to Git.
