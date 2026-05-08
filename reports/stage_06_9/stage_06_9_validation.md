# Stage 6.9 Validation

## Validation Commands

Preflight and required-file checks:

```bash
pwd
git branch --show-current
git status --short
sed -n '1,220p' AGENTS.md
sed -n '1,240p' reports/stage_06_9/stage_06_9_report.md
sed -n '1,220p' REPRODUCE.md
sed -n '1,220p' README.md
sed -n '1,160p' requirements.txt
sed -n '1,220p' reports/reproducibility_checklist.md
```

Core validation:

```bash
python - <<'PY'
import json
from pathlib import Path

path = Path("data/samples/public_mini_events.jsonl")
assert path.exists(), "public_mini_events.jsonl missing"
lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
assert len(lines) >= 10, f"too few records: {len(lines)}"
required = {
    "record_id", "source_dataset", "source_license_note", "source_doc_id",
    "source_text", "event_id", "event_type", "subject", "object",
    "time", "trigger", "evidence_span", "status", "source_url"
}
for i, line in enumerate(lines, 1):
    obj = json.loads(line)
    missing = required - obj.keys()
    assert not missing, f"line {i} missing {missing}"
    assert obj["source_dataset"], f"line {i} empty source_dataset"
    assert obj["source_license_note"], f"line {i} empty source_license_note"
    assert obj["evidence_span"] in obj["source_text"], f"line {i} evidence mismatch"
print("public mini-case OK", len(lines))
PY

python scripts/run_public_mini_case.py \
  --input data/samples/public_mini_events.jsonl \
  --out tables/public_mini_case_results.csv \
  --tex-table paper/i3m_submission/tables/table_public_mini_case.tex \
  --trace-out outputs/public_mini_replay_trace.jsonl

bash scripts/reproduce_all.sh
bash paper/i3m_submission/build_latex.sh
pdfinfo paper/manuscript_i3m2026_v2.pdf || true
pdftotext paper/manuscript_i3m2026_v2.pdf reports/stage_06_9/manuscript_i3m2026_v2_validation.txt || true
```

Paper-source checks:

```bash
grep -R "Public-dataset mini-case" -n paper/i3m_submission/manuscript.tex
grep -R "table_public_mini_case" -n paper/i3m_submission/manuscript.tex
grep -R "metadata-hidden" -n paper/i3m_submission/manuscript.tex
grep -R "not extraction accuracy" -n paper/i3m_submission/manuscript.tex || true
grep -R "market prediction" -n paper/i3m_submission/manuscript.tex || true
```

## Public Mini-Case Check

- Status: PASS.
- Record count: 20.
- Required provenance/schema fields: present for all records.
- Evidence-span containment: passed for all records.
- Replay command result: `FewFC: records=20 schema=1.000000 evidence=1.000000 replay=1.000000`.

## Reproduce All Check

- Status: PASS locally.
- Command: `bash scripts/reproduce_all.sh`.
- Exit status: 0.
- Python: 3.10.20.
- Public mini-case in bundled script: `public_mini_case_status=ran`.
- Final script marker: `no_gpu_training_required`.
- Generated final PDF paths:
  - `paper/i3m_submission/manuscript.pdf`
  - `paper/manuscript_i3m2026_v2.pdf`

## PDF Check

- Status: PASS locally.
- Build command: `bash paper/i3m_submission/build_latex.sh`.
- Final PDF: `paper/manuscript_i3m2026_v2.pdf`.
- Page count: 8.
- Page-count requirement: PASS, within 3-10 pages.
- Forbidden-text scan: PASS, no matches for the Stage 6.9 forbidden phrase list.
- Required-text scan: PASS for `Public-dataset mini-case`, `FewFC`, `controlled replay`, `discrete-event simulation`, `auditability`, and `modeling and simulation`.
- Extracted validation text: `reports/stage_06_9/manuscript_i3m2026_v2_validation.txt`.

## Source-Of-Truth Check

- Status: PASS.
- `paper/i3m_submission/manuscript.tex` references `Public-dataset mini-case`.
- `paper/i3m_submission/manuscript.tex` inputs `tables/table_public_mini_case.tex`.
- `paper/i3m_submission/manuscript.tex` references `metadata-hidden`.
- The paper states it is not an extraction benchmark and not market prediction.
- Title remains: `A Controlled-Replay Prototype for Auditable Versioned Financial Event Graph Updates`.

## Server Reproduction Check

- Status: PASS for core Python replay and public mini-case; server-side PDF rebuild is blocked by missing LaTeX tools.
- Source report: `reports/stage_06_9/stage_06_9_report.md`.
- Server command recorded: `bash scripts/reproduce_all.sh` in `/home/TJK/i3m_financial_event_graph_2026`.
- Server Python: 3.10.20.
- Server public mini-case status: `public_mini_case_status=ran`.
- Server training: no.
- Server model inference: no.
- Server external API calls: none.
- Server GPU training label: `no_gpu_training_required`.
- Server `reproduce_all` exit status: 127, caused only by final LaTeX builder absence: missing `latexmk` and `pdflatex`/`bibtex`.
- Decision: not a core reproduction blocker because all Python reproduction steps, including the public mini-case, completed before the LaTeX environment failure.

## Decision

- Stage 6.9 validation: PASS.
- Stage 7 entry: ALLOWED.
- Commit hash: reported in the final acceptance response after Git commit creation.
