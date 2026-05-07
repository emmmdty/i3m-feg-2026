# Stage 05 Report: Paper Figures, Tables, and Results Draft

## Preflight

Required checks were run before Stage 05 edits:

- `pwd`: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- working tree before edits: clean
- `AGENTS.md`: checked; this remains a reproducible simulation-oriented prototype, not a financial event extraction benchmark system.

## Generated Figures

- `paper/figures/fig1_framework.png`: generated.
- `paper/figures/fig2_update_state_transition.png`: generated.
- `paper/figures/fig3_case_study_replay_trace.png`: generated.

Figure data sources:

- Figure 1: implemented pipeline structure and Stage 05 requested labels.
- Figure 2: implemented operators in `src/update_ops.py` and methodology state transitions.
- Figure 3: `outputs/replay_trace.jsonl` and `tables/case_study_updates.csv`.

Both local and server project Python environments lacked `matplotlib`, so `scripts/plot_stage5_figures.py` used its standard-library PNG renderer. No seaborn or new dependency was used.

## Generated Tables

- `paper/tables/table1_event_record_schema.md`: generated from `src.schema.REQUIRED_EVENT_FIELDS` and controlled-stream metadata fields.
- `paper/tables/table2_ablation_results.md`: generated from `tables/ablation_results.csv`.
- `paper/tables/table3_case_study_update_log.md`: generated from `tables/case_study_updates.csv`.

Table data sources:

- Table 1: `src/schema.py`.
- Table 2: fresh local `scripts/run_ablation.py` output.
- Table 3: fresh local `scripts/build_case_study.py` output.

## Draft Section

- `paper/draft_sections/experiments_and_results.md`: generated.

The draft contains:

- `## Experimental Setup`
- `## Metrics`
- `## Results`
- `## Case Study`

The draft uses conservative wording and describes deterministic prototype behavior on the controlled stream.

## Local Command Results

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

```bash
python scripts/build_case_study.py \
  --replay outputs/replay_trace.jsonl \
  --updates outputs/updates.jsonl \
  --conflicts outputs/conflicts.jsonl \
  --out tables/case_study_updates.csv
```

Observed:

- wrote `tables/case_study_updates.csv`
- rows: 70
- operators: `ADD_EVENT`, `MARK_CONFLICT`, `MERGE_EVENT`, `UPDATE_SLOT`

```bash
python scripts/plot_stage5_figures.py \
  --ablation tables/ablation_results.csv \
  --case-study tables/case_study_updates.csv \
  --replay outputs/replay_trace.jsonl \
  --figures-dir paper/figures \
  --tables-dir paper/tables
```

Observed:

- renderer: `stdlib_png`
- ablation rows read: 4
- case-study rows read: 70
- replay rows read: 70
- figures written to `paper/figures`
- tables written to `paper/tables`

## Server Command Results

Code and Stage 05 artifacts were synced to:

- `/home/TJK/i3m_financial_event_graph_2026`

Server commands were run with:

- `/home/TJK/.conda/envs/tjk-feg/bin/python`

Large server outputs were written under:

- `/data/TJK/i3m/outputs`
- `/data/TJK/i3m/tables`
- `/data/TJK/i3m/reports/stage_05`

Observed server results:

- `run_demo.py`: processed 70 records, active events 40, version logs 70, conflicts 10.
- `run_ablation.py`: wrote `/data/TJK/i3m/tables/ablation_results.csv`; rows were `Direct`, `Schema`, `Evidence`, `Full`.
- `build_case_study.py`: wrote `/data/TJK/i3m/tables/case_study_updates.csv` with 70 rows and operators `ADD_EVENT`, `MARK_CONFLICT`, `MERGE_EVENT`, `UPDATE_SLOT`.
- `plot_stage5_figures.py`: renderer `stdlib_png`; read 4 ablation rows, 70 case-study rows, and 70 replay rows.
- server report synced back to `reports/stage_05/server_data_reports/stage_05_server_run.md`.

## Training and GPU Use

- GPU used: no
- training: no
- model inference: no
- external API calls: none
- no_gpu_training_required

## Claim Audit

The draft and Stage 05 report were checked for the high-risk claim phrases named in the stage request.

Observed result: no matches.

The draft frames the outputs as deterministic controlled-stream prototype evidence and does not expand claims beyond the implemented scripts.

## Recommendation

Stage 05 is ready for user acceptance review.

No Git commit was created.
