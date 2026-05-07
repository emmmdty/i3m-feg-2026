# Stage 02 Report: Minimal Reproducible Prototype Loop

## Stage Name

Stage 02 - Implement minimal reproducible experiment prototype loop.

## Local Modified Files

- `src/__init__.py`
- `src/io_utils.py`
- `src/schema.py`
- `src/evidence.py`
- `src/update_ops.py`
- `src/graph_store.py`
- `src/conflict.py`
- `src/simulator.py`
- `src/metrics.py`
- `scripts/run_demo.py`
- `scripts/run_ablation.py`
- `reports/stage_02/stage_02_report.md`
- `reports/stage_02/server/server_stage_02_report.md`
- `reports/stage_02/server_data_reports/server_stage_02_report.md`
- `reports/stage_02/server_data_reports/nvidia_smi.txt`

## Local Commands and Results

Preflight:

```bash
pwd
git branch --show-current
git status --short --branch
cat AGENTS.md
```

Result:

- `pwd`: `/home/tjk/myProjects/masterProjects/i3m_financial_event_graph_2026`
- branch: `main`
- status: `## main`
- `AGENTS.md` read successfully.

Implementation verification:

```bash
python -m compileall -q src scripts
mkdir -p outputs tables reports/stage_02
python scripts/run_demo.py
python scripts/run_ablation.py
python scripts/validate_stage1_data.py \
  --samples data/samples/seed_financial_events.jsonl \
  --stream data/processed/controlled_stream.jsonl \
  --summary tables/stage1_data_summary.csv
```

Results:

- `compileall`: exit 0.
- `run_demo.py`: exit 0; processed 70 records, active events 40, version logs 70, conflicts 10.
- `run_ablation.py`: exit 0; wrote `tables/ablation_results.csv`.
- `validate_stage1_data.py`: exit 0; Stage 1 data validation passed.

Local demo artifact line counts:

```text
40 outputs/events.jsonl
70 outputs/updates.jsonl
70 outputs/version_logs.jsonl
10 outputs/conflicts.jsonl
70 outputs/replay_trace.jsonl
```

## Server Sync Command

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

Result: exit 0. No `--delete` was used.

Note: the exact exclude list did not exclude ignored archives or Python bytecode caches; the rsync output showed ignored files such as `data/raw.zip`, `paper/templates/`, and `__pycache__/` entries being transferred. I did not delete remote files without explicit permission.

## Server Commands and Results

The first non-interactive activation attempt failed because `conda` was not on PATH and `/home/TJK/.conda/envs/tjk-feg/bin/activate` was absent. A read-only lookup confirmed the requested environment Python at `/home/TJK/.conda/envs/tjk-feg/bin/python`, and the server run used that interpreter directly.

Executed under:

- host: `gpu-4090`
- cwd: `/home/TJK/i3m_financial_event_graph_2026`
- Python: `/home/TJK/.conda/envs/tjk-feg/bin/python`

```bash
mkdir -p /data/TJK/i3m/outputs /data/TJK/i3m/tables /data/TJK/i3m/logs /data/TJK/i3m/reports/stage_02 reports/stage_02
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
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_demo.py --outputs-dir /data/TJK/i3m/outputs
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/run_ablation.py --tables-dir /data/TJK/i3m/tables
/home/TJK/.conda/envs/tjk-feg/bin/python scripts/validate_stage1_data.py \
  --samples data/samples/seed_financial_events.jsonl \
  --stream data/processed/controlled_stream.jsonl \
  --summary /data/TJK/i3m/tables/stage1_data_summary.csv
nvidia-smi
```

Results:

- seed samples regenerated: 30 records.
- controlled perturbation stream regenerated: 70 records.
- server `run_demo.py`: exit 0; processed 70 records, active events 40, version logs 70, conflicts 10.
- server `run_ablation.py`: exit 0; wrote `/data/TJK/i3m/tables/ablation_results.csv`.
- server Stage 1 validation: exit 0; wrote `/data/TJK/i3m/tables/stage1_data_summary.csv`.
- `nvidia-smi`: ran for visibility only and was saved to `/data/TJK/i3m/reports/stage_02/nvidia_smi.txt`.

Server demo artifact line counts:

```text
40 /data/TJK/i3m/outputs/events.jsonl
70 /data/TJK/i3m/outputs/updates.jsonl
70 /data/TJK/i3m/outputs/version_logs.jsonl
10 /data/TJK/i3m/outputs/conflicts.jsonl
70 /data/TJK/i3m/outputs/replay_trace.jsonl
```

## GPU and Training Status

- GPU visibility checked with `nvidia-smi`.
- GPU was not used by this stage.
- Training: `no_gpu_training_required`.

## Output Locations

Local:

- `outputs/events.jsonl`
- `outputs/updates.jsonl`
- `outputs/version_logs.jsonl`
- `outputs/conflicts.jsonl`
- `outputs/replay_trace.jsonl`
- `tables/ablation_results.csv`
- `tables/stage1_data_summary.csv`

Server:

- `/data/TJK/i3m/outputs/events.jsonl`
- `/data/TJK/i3m/outputs/updates.jsonl`
- `/data/TJK/i3m/outputs/version_logs.jsonl`
- `/data/TJK/i3m/outputs/conflicts.jsonl`
- `/data/TJK/i3m/outputs/replay_trace.jsonl`
- `/data/TJK/i3m/tables/ablation_results.csv`
- `/data/TJK/i3m/tables/stage1_data_summary.csv`
- `/data/TJK/i3m/reports/stage_02/server_stage_02_report.md`
- `/data/TJK/i3m/reports/stage_02/nvidia_smi.txt`

Synced-back server reports:

- `reports/stage_02/server/server_stage_02_report.md`
- `reports/stage_02/server_data_reports/server_stage_02_report.md`
- `reports/stage_02/server_data_reports/nvidia_smi.txt`

## Ablation Results Summary

Local:

```text
Direct: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Schema: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Evidence: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Full: schema=1.000000 evidence=1.000000 merge=1.000000 conflict=1.000000 replay=1.000000
```

Server:

```text
Direct: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Schema: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Evidence: schema=1.000000 evidence=1.000000 merge=NA conflict=NA replay=NA
Full: schema=1.000000 evidence=1.000000 merge=1.000000 conflict=1.000000 replay=1.000000
```

## Known Issues and Failed Items

- Initial local acceptance commands failed before implementation because `scripts/run_demo.py` and `scripts/run_ablation.py` did not exist; this was the expected pre-implementation failure.
- Initial SSH command construction failed locally due to shell quoting; no server workload ran in that attempt.
- Initial server activation command failed because the documented activation path was absent; rerun used `/home/TJK/.conda/envs/tjk-feg/bin/python` directly.
- The required rsync exclude list did not filter ignored archives or `__pycache__`; no remote cleanup was performed without permission.

No blocking code or runtime failures remain for Stage 02 acceptance.

## Acceptance Recommendation

Recommend entering user acceptance for Stage 02. Do not enter the next stage until the user accepts this stage.

本阶段尚未提交 Git，等待用户验收。
