"""Schema validation tests."""

from __future__ import annotations

import unittest

from src.feg_replay.schema import normalize_event_record, validate_event_schema


class SchemaTests(unittest.TestCase):
    def test_nested_event_must_be_object(self) -> None:
        record = {"event": "not-an-object", "source_text": "text"}

        normalized = normalize_event_record(record)
        valid, errors = validate_event_schema(record)

        self.assertFalse(normalized.is_valid)
        self.assertIn("event must be an object", normalized.errors)
        self.assertFalse(valid)
        self.assertIn("event must be an object", errors)


if __name__ == "__main__":
    unittest.main()
