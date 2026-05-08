"""Evidence gate tests."""

from __future__ import annotations

import unittest

from src.feg_replay.evidence import has_evidence_match


class EvidenceTests(unittest.TestCase):
    def test_evidence_gate_requires_exact_containment(self) -> None:
        record = {
            "evidence_span": "Company A pledged five million shares",
            "source_text": "Company A pledged 5 million shares in the disclosure.",
        }

        self.assertFalse(has_evidence_match(record))


if __name__ == "__main__":
    unittest.main()
