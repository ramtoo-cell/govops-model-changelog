
"""Tests for the model changelog generator."""
import unittest
from datetime import date

from src.model_changelog import ChangeEntry, ModelChangelog


def _entry(version, category="added", description="something new"):
    return ChangeEntry(version, date(2026, 5, 1), category, description)


class TestModelChangelog(unittest.TestCase):
    def setUp(self):
        self.c = ModelChangelog("fraud-scorer")
        self.c.add(_entry((1, 0, 0), "added", "initial release"))
        self.c.add(_entry((1, 1, 0), "changed", "recalibrated thresholds"))
        self.c.add(_entry((2, 0, 0), "removed", "dropped legacy features"))

    def test_monotonic_versions(self):
        with self.assertRaises(ValueError):
            self.c.add(_entry((1, 5, 0)))
        with self.assertRaises(ValueError):
            self.c.add(_entry((2, 0, 0)))

    def test_bad_category(self):
        with self.assertRaises(ValueError):
            self.c.add(_entry((3, 0, 0), "yolo"))

    def test_bad_version_shape(self):
        with self.assertRaises(ValueError):
            self.c.add(ChangeEntry((1, 2), date(2026, 5, 1), "added", "x"))

    def test_latest_version(self):
        self.assertEqual(self.c.latest_version(), (2, 0, 0))

    def test_since(self):
        entries = self.c.since((1, 0, 0))
        self.assertEqual([e.version for e in entries],
                         [(1, 1, 0), (2, 0, 0)])

    def test_breaking_changes(self):
        breaking = self.c.breaking_changes()
        self.assertEqual(len(breaking), 1)
        self.assertEqual(breaking[0].description, "dropped legacy features")

    def test_by_category(self):
        self.assertEqual(len(self.c.by_category("added")), 1)
        self.assertEqual(len(self.c.by_category("security")), 0)

    def test_render_markdown(self):
        md = self.c.render_markdown()
        self.assertIn("# Changelog: fraud-scorer", md)
        self.assertIn("## 2.0.0", md)
        self.assertLess(md.index("2.0.0"), md.index("1.0.0"))

    def test_entry_count(self):
        self.assertEqual(self.c.entry_count(), 3)


if __name__ == "__main__":
    unittest.main()
