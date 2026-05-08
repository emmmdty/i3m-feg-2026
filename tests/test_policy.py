"""Replay policy tests."""

from __future__ import annotations

import unittest

from src.feg_replay.graph import GraphStore
from src.feg_replay.operators import MERGE_EVENT
from src.feg_replay.policy import (
    predict_operator_oracle,
    predict_operator_rule_based,
    select_target_oracle,
    select_target_rule_based,
)


def base_record() -> dict[str, object]:
    return {
        "event_id": "E1",
        "event_type": "equity_pledge",
        "subject": "Company A",
        "object": "shares",
        "time": "2026-01-01",
        "trigger": "pledged",
        "evidence_span": "Company A pledged shares",
        "source_doc_id": "D1",
        "source_text": "Company A pledged shares in a filing.",
        "amount": "5 million shares",
        "status": "announced",
    }


class PolicyTests(unittest.TestCase):
    def test_oracle_reads_expected_operator_but_rule_based_does_not(self) -> None:
        graph = GraphStore()
        graph.add_event(base_record(), 1)
        record = {
            **base_record(),
            "event_id": "E2",
            "expected_operator": MERGE_EVENT,
            "perturbation_type": "duplicate",
            "base_event_id": "E1",
            "gold_group_id": "G1",
            "amount": "changed amount",
            "status": "changed status",
            "source_text": "Unrelated text without duplicate signals.",
        }

        self.assertEqual(predict_operator_oracle(record, graph), MERGE_EVENT)
        self.assertNotEqual(predict_operator_rule_based(record, graph), MERGE_EVENT)

    def test_rule_based_target_does_not_use_direct_base_event_id(self) -> None:
        graph = GraphStore()
        graph.add_event(base_record(), 1)
        record = {
            **base_record(),
            "event_id": "E2",
            "subject": "Company Z",
            "base_event_id": "E1",
            "expected_operator": MERGE_EVENT,
        }

        self.assertEqual(select_target_oracle(record, graph), "E1")
        self.assertIsNone(select_target_rule_based(record, graph))

    def test_unknown_metadata_is_not_mapped_to_add_event(self) -> None:
        graph = GraphStore()
        record = {**base_record(), "perturbation_type": "unsupported_metadata"}

        self.assertIsNone(predict_operator_oracle(record, graph))
        self.assertIsNone(predict_operator_rule_based(record, graph))


if __name__ == "__main__":
    unittest.main()
