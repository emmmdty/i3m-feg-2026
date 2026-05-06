# AGENTS.md

## Project

EMSS/I3M 2026 short-paper prototype:
A Reproducible Versioned Event Graph Prototype for Evidence-Constrained Financial Event Stream Simulation.

This is a reproducible simulation-oriented prototype, not a financial event extraction SOTA system.

## Local paths

- Local project: `~/myProjects/masterProjects/i3m_financial_event_graph_2026`
- Local raw data: `~/myProjects/masterProjects/i3m_financial_event_graph_2026/data/raw`
- Local conda env: `feg-dev-py310`
- Local conda path: `/home/tjk/miniconda3/envs/feg-dev-py310`

## Server paths

- SSH alias: `gpu-4090`
- Server project: `/home/TJK/i3m_financial_event_graph_2026`
- Server conda env: `tjk-feg`
- Server conda path: `/home/TJK/.conda/envs/tjk-feg`
- Server data symlink target: `/data/TJK/i3m/data`
- Server raw data: `/data/TJK/i3m/data/raw`
- Large server outputs must go under `/data/TJK/i3m`, such as:
  - `/data/TJK/i3m/outputs`
  - `/data/TJK/i3m/tables`
  - `/data/TJK/i3m/logs`
  - `/data/TJK/i3m/models`

## Optional local model on server

- Qwen model path: `/data/TJK/DEE/models/Qwen/Qwen3-4B-Instruct-2507`
- If needed, symlink it into the project. Do not copy model files.

## Workflow

1. Develop and commit code locally.
2. Keep `main` clean after each completed stage.
3. Upload code to server with `rsync`.
4. Run training or heavy experiments only on server.
5. Keep large generated artifacts under `/data/TJK/i3m`.

Example rsync command:

```bash
rsync -avz --delete \
  --exclude '.git/' \
  --exclude 'data/raw/' \
  --exclude 'data/processed/' \
  --exclude 'outputs/' \
  --exclude 'logs/' \
  --exclude 'tables/*.csv' \
  --exclude 'models/' \
  ./ gpu-4090:/home/TJK/i3m_financial_event_graph_2026/
```

## Safety rules

- Do not use `sudo`.
- Do not delete shared server files.
- Do not run destructive commands on `/data`, `/home`, or model directories.
- Do not copy large model files into the repo.
- Do not commit raw data, generated outputs, logs, checkpoints, or model weights.
- Do not implement investment advice, stock prediction, trading signals, or buy/sell recommendations.

## Minimum future commands

Later implementation stages should make these commands stable:

```bash
python scripts/run_demo.py
python scripts/run_ablation.py
```
