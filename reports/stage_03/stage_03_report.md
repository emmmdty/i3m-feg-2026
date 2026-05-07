# Stage 03 Report: Reproducible Experiment and Case Study

## Stage Name

Stage 03 - Validate formal experiment results and reproducible case study.

## Preflight

```bash
pwd
git branch --show-current
git status
```

Observed before Stage 03 implementation:

- `pwd`: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- Stage 02 work was present as untracked files, so Stage 02 was verified and committed first.

Stage 02 prerequisite commit:

- `a7fc985` - `Implement stage2 minimal reproducible prototype`

## Local Commands

```bash
python scripts/run_demo.py
python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out tables/ablation_results.csv
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

## Results

- `run_demo.py`: processed 70 records, active events 40, version logs 70, conflicts 10.
- `run_ablation.py`: wrote `tables/ablation_results.csv`.
- `build_case_study.py`: wrote `tables/case_study_updates.csv` with 70 rows and operators `ADD_EVENT`, `MARK_CONFLICT`, `MERGE_EVENT`, `UPDATE_SLOT`.
- `summarize_experiment.py`: wrote `reports/stage_03/experiment_summary.md`.

## Training and GPU Use

- training: `no_gpu_training_required`
- gpu_training: `no_gpu_training_required`
- external_api_calls: none

No GPU training was started or claimed.

## Output Locations

- `outputs/replay_trace.jsonl`
- `outputs/updates.jsonl`
- `outputs/conflicts.jsonl`
- `tables/ablation_results.csv`
- `tables/case_study_updates.csv`
- `reports/stage_03/experiment_summary.md`
- `reports/stage_03/stage_03_validation.md`

Generated outputs and table CSVs are validation artifacts and are not committed.

## Known Issues

- No server or GPU run was required for Stage 03.
- `configs/runtime.local.env`, raw data, processed data, outputs, table CSVs, paper templates, and Python caches remain ignored and uncommitted.

## Recommendation

Stage 03 local acceptance passed. The project can enter Stage 04 after this validation is committed and `main` is clean.
