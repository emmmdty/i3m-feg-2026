# Public Mini-Case Conversion Notes

The conversion is implemented by `scripts/prepare_public_mini_case.py`.

- `source_text`: copied from the FewFC record content field.
- `evidence_span`: selected as the FewFC event trigger when that trigger is present in `source_text`.
- `event_type`: copied from the FewFC event type.
- `subject`: selected from argument mentions whose role names match subject-like hints such as `sub`, `subject`, `share-org`, or `share-per`.
- `object`: selected from object-like argument roles such as `obj`, `target`, `collateral`, or `title`; if no object-like role is available, the first unused non-trigger argument is used.
- `time`: normalized from date mentions or date text when available.
- `1970-01-01`: used only when the source record does not provide a stable ISO-normalizable date; the limitation is recorded in `extra_notes`.
- `source_license_note`: records the FewFC public research dataset and CC BY-SA 4.0 note.

This conversion supports only an external sanity case. It is not an extraction benchmark, not a complete public-dataset experiment, and not evidence of benchmark-level generalization.
