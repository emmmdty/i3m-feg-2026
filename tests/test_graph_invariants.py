"""Graph invariant tests."""

from __future__ import annotations

import unittest

from src.feg_replay.graph import GraphStore


def incoming_record() -> dict[str, object]:
    return {
        "event_id": "E-missing",
        "event_type": "equity_pledge",
        "subject": "Company A",
        "object": "shares",
        "time": "2026-01-01",
        "trigger": "pledged",
        "evidence_span": "Company A pledged shares",
        "source_doc_id": "D1",
        "source_text": "Company A pledged shares.",
        "base_event_id": "E-does-not-exist",
    }


class GraphInvariantTests(unittest.TestCase):
    def test_missing_target_merge_is_logged_but_not_counted(self) -> None:
        graph = GraphStore()

        update = graph.merge_event(incoming_record(), 1, "E-does-not-exist")

        self.assertFalse(update["operation_applied"])
        self.assertEqual(update["skipped_reason"], "target_missing")
        self.assertEqual(graph.snapshot_state(1)["merged_event_count"], 0)
        self.assertEqual(graph.version_logs[-1]["operation_applied"], False)

    def test_missing_target_update_is_logged_but_not_counted(self) -> None:
        graph = GraphStore()

        update = graph.update_slot(incoming_record(), 1, "E-does-not-exist")

        self.assertFalse(update["operation_applied"])
        self.assertEqual(update["skipped_reason"], "target_missing")
        self.assertEqual(graph.snapshot_state(1)["updated_slot_count"], 0)

    def test_missing_target_conflict_is_failed_attempt_only(self) -> None:
        graph = GraphStore()

        update = graph.mark_conflict(incoming_record(), 1, "E-does-not-exist")
        snapshot = graph.snapshot_state(1)

        self.assertFalse(update["operation_applied"])
        self.assertEqual(update["skipped_reason"], "target_missing")
        self.assertEqual(snapshot["unresolved_conflict_count"], 0)
        self.assertEqual(snapshot["failed_conflict_attempt_count"], 1)


if __name__ == "__main__":
    unittest.main()
