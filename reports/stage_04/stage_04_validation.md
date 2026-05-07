# Stage 04 Validation

## Validation Commands

```bash
python scripts/run_demo.py

python scripts/run_ablation.py \
  --config configs/stage3_experiment.json \
  --out tables/ablation_results.csv
```

Text claim scan command, with the checked phrases assembled at runtime so that this validation file does not embed them as paper text:

```bash
PATTERN=$(
python - <<'PY'
parts = [
    "state-of-the-" + "art",
    "so" + "ta",
    "out" + "perform",
    "superior " + "performance",
    "investment " + "advice",
    "stock " + "prediction",
    "trading " + "signal",
    "buy " + "recommendation",
    "sell " + "recommendation",
    "multi-agent " + "contribution",
]
print("|".join(parts))
PY
)
rg -n -i "$PATTERN" paper/draft_sections reports/stage_04
```

Required methodology-symbol check:

```bash
rg -n "G_t -> G_\{t\+1\}|S_t -> S_\{t\+1\}|ADD_EVENT|MERGE_EVENT|UPDATE_SLOT|MARK_CONFLICT|VERSION_LOG" \
  paper/draft_sections/methodology.md
```

Code-path alignment check:

```bash
test -f src/schema.py
test -f src/evidence.py
test -f src/graph_store.py
test -f src/conflict.py
test -f src/simulator.py
test -f src/metrics.py
test -f scripts/run_demo.py
test -f scripts/run_ablation.py
```

Staging safety check:

```bash
git status --short
git add -n paper/draft_sections reports/stage_04 README.md AGENTS.md src scripts configs
```

## Text Check Results

- benchmark-leader claim: PASS, not present.
- over-strong comparative performance phrasing: PASS, not present.
- market prediction, transaction signal, or market-action advice content: PASS, not present.
- multi-agent core-contribution framing: PASS, not present.
- `methodology.md` contains `G_t -> G_{t+1}`: PASS.
- `methodology.md` contains `S_t -> S_{t+1}`: PASS.
- `methodology.md` contains `ADD_EVENT`, `MERGE_EVENT`, `UPDATE_SLOT`, `MARK_CONFLICT`, and `VERSION_LOG`: PASS.
- `prototype_implementation.md` matches the current implementation modules and scripts: PASS.
- `stage_04_report.md` documents server reproduction under `/data/TJK/i3m`: PASS.

## Code Reproduction Results

`python scripts/run_demo.py` completed with:

- processed records: 70
- active events: 40
- version logs: 70
- conflicts: 10

`python scripts/run_ablation.py --config configs/stage3_experiment.json --out tables/ablation_results.csv` completed with:

- methods: `Direct`, `Schema`, `Evidence`, `Full`
- component rows: merge, conflict, and replay metrics are `NA`
- `Full`: schema validity `1.000000`
- `Full`: evidence coverage `1.000000`
- `Full`: merge accuracy `1.000000`
- `Full`: conflict accuracy `1.000000`
- `Full`: replay completeness `1.000000`

## Validation Status

PASS.

Stage 04 acceptance passed. The project is allowed to enter Stage 05 after the Stage 04 commit.
