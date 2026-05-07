# Stage 06.6 Report: I3M Pre-Submission Cleanup

## 1. Scope

Stage 06.6 was limited to pre-submission cleanup on top of the accepted Stage 06.5 artifacts.

No experiments, scripts, data, paper direction, or evaluation claims were changed.

## 2. Internal Trace Cleanup

Updated `paper/i3m_submission/manuscript.tex` to remove internal stage and engineering-package wording from the manuscript body:

- Replaced the abstract sentence that referred to the prior internal stage with a neutral evaluation-strengthening sentence.
- Replaced the conclusion sentence that referred to the package-building status with a neutral summary of the additional evaluation and LaTeX build artifacts.

Source check result:

- `paper/i3m_submission/manuscript.tex` no longer contains internal stage wording, package-oriented phrasing, or prohibited tool-origin wording from the cleanup list.

## 3. Author Placeholder Status

The manuscript still uses placeholder author metadata:

- `\author[a]{TBD Author}`
- `\address[a]{TBD Affiliation, TBD City, TBD Country}`
- `\runauth{TBD Author}`

final submission still requires replacing TBD author and affiliation.

## 4. README Reproducibility Update

Updated `README.md` with the Stage 6.5 / final LaTeX reproducibility commands for:

- negative-control generation
- sanity-check table generation
- scale-sensitivity table and figure generation
- compact LaTeX table generation
- final LaTeX PDF build

## 5. PDF Rebuild

Rebuild command:

```bash
bash paper/i3m_submission/build_latex.sh
```

Result:

- PDF recompiled: yes
- Final PDF path: `paper/manuscript_i3m2026_v2.pdf`
- Submission workspace PDF also updated: `paper/i3m_submission/manuscript.pdf`
- PDF pages: 7

## 6. Risk-Word Check

PDF text extraction command:

```bash
pdftotext paper/manuscript_i3m2026_v2.pdf reports/stage_06_6/manuscript_i3m2026_v2.txt || true
```

Risk-word scan result:

- PASS
- No matches were found in `reports/stage_06_6/manuscript_i3m2026_v2.txt`.

## 7. Recommendation

Stage 06.6 is suitable to enter Stage 7 after this cleanup commit.

Remaining final-submission blocker:

- Replace the TBD author and affiliation metadata before formal submission.
