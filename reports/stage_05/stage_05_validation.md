# Stage 05 Validation

## Result

PASS.

Stage 05 figures, tables, draft text, and report are consistent with the regenerated local artifacts. Stage 05 can be committed and accepted.

## Preflight

- `pwd`: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- pre-validation `git status --short`: Stage 05 deliverables were untracked; no dangerous generated data files were tracked.

## Regenerated Commands

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
- component rows keep merge, conflict, and replay metrics as `NA`
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

## Acceptance Checklist

- PASS: `paper/figures/fig1_framework.png`, `paper/figures/fig2_update_state_transition.png`, and `paper/figures/fig3_case_study_replay_trace.png` exist and are valid PNG files.
- PASS: `paper/tables/table1_event_record_schema.md`, `paper/tables/table2_ablation_results.md`, and `paper/tables/table3_case_study_update_log.md` exist.
- PASS: Table 2 exactly matches a Markdown conversion of regenerated `tables/ablation_results.csv`.
- PASS: Table 3 exactly matches a Markdown conversion of regenerated `tables/case_study_updates.csv`.
- PASS: `paper/draft_sections/experiments_and_results.md` avoids the over-claiming and market-action language named in the acceptance checklist.
- PASS: figure/table terminology is aligned with Methodology terms and implemented operators: `ADD_EVENT`, `MERGE_EVENT`, `UPDATE_SLOT`, `MARK_CONFLICT`, `VERSION_LOG`, schema, evidence, replay, graph transition, and state transition.
- PASS: `reports/stage_05/stage_05_report.md` states `no_gpu_training_required` and reports no GPU use or training.
- PASS: generated data artifacts remain excluded from the commit set: `tables/*.csv`, `outputs/*`, `data/processed/*`, `data/raw/*`, `logs/*`, and `models/*`.

## Commit Safety

Allowed Stage 05 files:

- `scripts/plot_stage5_figures.py`
- `paper/draft_sections/experiments_and_results.md`
- `paper/figures/*.png`
- `paper/tables/*.md`
- `reports/stage_05/`

No README change was required for Stage 05 acceptance.
