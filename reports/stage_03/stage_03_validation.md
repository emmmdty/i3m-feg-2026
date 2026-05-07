# Stage 03 Validation

## Validation Commands

```bash
pwd
git branch --show-current
git status
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

- `configs/stage3_experiment.json`: PASS
- `tables/ablation_results.csv`: PASS, generated locally and left uncommitted
- `tables/case_study_updates.csv`: PASS, generated locally and left uncommitted
- `reports/stage_03/experiment_summary.md`: PASS
- ablation methods include Direct, Schema, Evidence, Full: PASS
- case study includes multiple operations: PASS, includes `ADD_EVENT`, `MERGE_EVENT`, `UPDATE_SLOT`, `MARK_CONFLICT`
- `outputs/replay_trace.jsonl` non-empty: PASS, 70 records
- report states training status: PASS, `no_gpu_training_required`
- no GPU training was run or fabricated: PASS
- no raw data, processed data, outputs, logs, table CSVs, models, archives, or model weights staged for commit: PASS

## Validation Status

PASS.

第 3 阶段验收通过，可以进入第 4 阶段。

## Commit Hash

Pending. This will be filled after the Stage 03 commit is created.
