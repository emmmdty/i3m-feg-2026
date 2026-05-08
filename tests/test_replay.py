"""Replay trace tests."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from src.feg_replay.operators import MERGE_EVENT
from src.feg_replay.simulator import simulate_replay


def base_record(event_id: str) -> dict[str, object]:
    return {
        "event_id": event_id,
        "event_type": "equity_pledge",
        "subject": "Company A",
        "object": "shares",
        "time": "2026-01-01",
        "trigger": "pledged",
        "evidence_span": "Company A pledged shares",
        "source_doc_id": "D1",
        "source_text": "Company A pledged shares.",
        "amount": "5 million shares",
        "status": "announced",
    }


class ReplayTests(unittest.TestCase):
    def test_missing_target_trace_marks_skip(self) -> None:
        record = {
            **base_record("E2"),
            "arrival_index": 1,
            "expected_operator": MERGE_EVENT,
            "perturbation_type": "duplicate",
            "base_event_id": "missing",
        }

        result = simulate_replay([record], policy_mode="oracle")
        trace = result.replay_trace[0]

        self.assertFalse(trace["target_exists"])
        self.assertFalse(trace["operation_applied"])
        self.assertEqual(trace["skipped_reason"], "target_missing")

    def test_unsupported_metadata_is_logged_without_apply(self) -> None:
        record = {
            **base_record("E3"),
            "arrival_index": 1,
            "perturbation_type": "unsupported_metadata",
            "expected_operator": "UNSUPPORTED_OPERATOR",
        }

        result = simulate_replay([record], policy_mode="oracle")
        trace = result.replay_trace[0]

        self.assertTrue(trace["unsupported_metadata_logged"])
        self.assertFalse(trace["operation_applied"])
        self.assertEqual(trace["skipped_reason"], "unsupported_or_unknown_metadata")

    def test_rule_based_unsupported_metadata_is_logged_without_apply(self) -> None:
        record = {
            **base_record("E4"),
            "arrival_index": 1,
            "perturbation_type": "unsupported_metadata",
        }

        result = simulate_replay([record], policy_mode="rule_based")
        trace = result.replay_trace[0]

        self.assertTrue(trace["unsupported_metadata_logged"])
        self.assertFalse(trace["operation_applied"])
        self.assertEqual(trace["skipped_reason"], "unsupported_or_unknown_metadata")

    def test_public_mini_case_jsonl_is_readable(self) -> None:
        path = Path("data/samples/public_mini_events.jsonl")
        self.assertTrue(path.exists())

        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(rows), 10)
        for row in rows:
            self.assertIsInstance(row, dict)
            self.assertIn("source_text", row)
            self.assertIn("evidence_span", row)
            self.assertIn(row["evidence_span"], row["source_text"])
            self.assertIn("source_dataset", row)
            self.assertIn("source_license_note", row)
            self.assertIn("source_url", row)
            self.assertTrue(row["source_dataset"])
            self.assertTrue(row["source_license_note"])
            self.assertTrue(row["source_url"])


if __name__ == "__main__":
    unittest.main()
