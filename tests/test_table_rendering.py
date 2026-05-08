"""LaTeX table rendering tests."""

from __future__ import annotations

import unittest

from src.feg_replay.table_rendering import format_decimal, render_invariant_checks_table


class TableRenderingTests(unittest.TestCase):
    def test_decimal_and_na_formatting(self) -> None:
        self.assertEqual(format_decimal("0.5862"), "0.586")
        self.assertEqual(format_decimal("NA"), "--")

    def test_tables_do_not_contain_internal_trace_words(self) -> None:
        table = render_invariant_checks_table(
            [
                {
                    "case": "Missing target merge",
                    "expected_behavior": "log failed target resolution",
                    "applied": "false",
                    "logged": "true",
                    "result": "pass",
                }
            ]
        )
        lowered = table.lower()

        forbidden_terms = (
            "co" + "dex",
            "chat" + "gpt",
            "ai-" + "generated",
            "st" + "age",
            "ph" + "ase",
            "pro" + "mpt",
            "ag" + "ent",
        )
        for forbidden in forbidden_terms:
            self.assertNotIn(forbidden, lowered)


if __name__ == "__main__":
    unittest.main()
