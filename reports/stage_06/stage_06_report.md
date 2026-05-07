# Stage 06 Report: Manuscript Integration and PDF v1

## Preflight

Required checks were run before Stage 06 edits:

- `pwd`: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- working tree before edits: clean
- `AGENTS.md`: checked; this remains a reproducible simulation-oriented prototype, not a financial event extraction benchmark system.

## Paper Integration

Created:

- `paper/manuscript.md`
- `paper/submission_info.md`
- `paper/build_pdf.sh`
- `paper/manuscript_v1.pdf`

Updated:

- `paper/tables/table2_ablation_results.md`

The manuscript integrates the prior draft sections, Stage 05 figures, Stage 05 tables, and fresh Stage 06 local ablation values. `paper/tables/table2_ablation_results.md` was refreshed from the current local `tables/ablation_results.csv` so Table 2 matches the Stage 06 reproduction run. The manuscript uses `paper/manuscript.md` as the primary source because the repository has Markdown draft sections and a downloaded template bundle, but no active TeX manuscript project.

The manuscript contains the required structure:

- Title, Abstract, Keywords
- Introduction
- Related Work with the three requested subsections
- Problem Definition
- Methodology with the five requested subsections
- Prototype Implementation
- Experiments and Results with the four requested subsections
- Discussion
- Conclusion
- References

## PDF Generation

PDF generated: yes.

Output:

- `paper/manuscript_v1.pdf`

Build command:

```bash
bash paper/build_pdf.sh
```

Observed PDF path:

- `paper/manuscript_v1.pdf`

Direct Pandoc PDF generation was attempted first and failed because `pdflatex` is not installed in the local environment. The build script then generated standalone HTML through Pandoc with embedded print CSS and printed it to PDF through headless Chrome. The generated PDF has 9 pages.

Visual verification was performed by rendering PDF pages with `pdftoppm`. The first page, figure page, and results-table page were inspected for duplicate titles, browser print headers, clipped figures, and table readability. The final PDF render removed duplicate titles and browser headers, scaled figures to the printable page, and kept Table 2 readable.

## Local Reproduction

Commands run locally:

```bash
python scripts/run_demo.py
```

Observed:

- processed records: 70
- active events: 40
- version logs: 70
- conflicts: 10
- output directory: `outputs`

```bash
python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out tables/ablation_results.csv
```

Observed:

- wrote `tables/ablation_results.csv`
- rows: `Direct`, `Schema`, `Evidence`, `Full`
- component rows kept merge, conflict, and replay metrics as `NA`
- `Full`: schema `1.000000`, evidence `1.000000`, merge `1.000000`, conflict `1.000000`, replay `1.000000`

Table 2 in `paper/manuscript.md` was populated from the fresh local `tables/ablation_results.csv`. Numeric values were not manually invented.

## Server Reproduction

Code and Stage 06 paper artifacts were synced to:

- `/home/TJK/i3m_financial_event_graph_2026`

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

Remote working directory:

- `/home/TJK/i3m_financial_event_graph_2026`

Remote large-output locations:

- `/data/TJK/i3m/outputs`
- `/data/TJK/i3m/tables`
- `/data/TJK/i3m/reports/stage_06`

The requested activation command path was checked. `/home/TJK/.conda/envs/tjk-feg/bin/activate` was not present, so the run used the env-specific interpreter:

- `/home/TJK/.conda/envs/tjk-feg/bin/python`

Remote commands run:

```bash
mkdir -p /data/TJK/i3m/reports/stage_06 /data/TJK/i3m/outputs /data/TJK/i3m/tables

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_demo.py \
  --outputs-dir /data/TJK/i3m/outputs

/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out /data/TJK/i3m/tables/ablation_results.csv
```

Observed server results:

- `run_demo.py`: processed 70 records, active events 40, version logs 70, conflicts 10.
- `run_ablation.py`: wrote `/data/TJK/i3m/tables/ablation_results.csv`.
- remote replay trace rows: 70.
- remote version log rows: 70.
- remote conflict rows: 10.
- remote `Full`: schema `1.000000`, evidence `1.000000`, merge `1.000000`, conflict `1.000000`, replay `1.000000`.

## Training

- training: no
- GPU training: no
- model inference: no
- external API calls: none
- no_gpu_training_required

## Claim Check

The manuscript uses conservative prototype wording. It explicitly states the required limitations, including that the paper is not designed as an extraction-performance advance, that the evaluation focuses on framework behavior, that the consistency modules are lightweight and rule-based, and that future work should extend the framework to document-level extraction and larger-scale simulation.

No broad benchmark, forecasting, or financial-utility claims were found in the manuscript.

## Blocked Wording Check

The configured blocked phrase scan was run against:

- `paper/manuscript.md`
- `paper/submission_info.md`
- `reports/stage_06/stage_06_report.md`

Result: no matches.

## Recommendation

Stage 06 is ready for user acceptance review.

No Git commit was created.
