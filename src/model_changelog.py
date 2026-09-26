
"""Model changelog generator.

Model releases need structured changelogs: entries carry a version
tuple, a date, a category (added/changed/deprecated/removed/fixed/
security), and a description. add() enforces monotonic version
increases; render_markdown() produces a keep-a-changelog-style
document newest-first; breaking_changes() surfaces removed and
deprecated entries for migration review.

Design:
- Versions are (major, minor, patch) tuples compared lexicographically.
- Entries are stored in insertion order; the last entry's version is
  the floor for the next add(): no going backwards.
- since(version) filters to newer entries for release-note diffs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

CATEGORIES = ("added", "changed", "deprecated", "removed", "fixed",
              "security")
BREAKING = ("removed", "deprecated")


@dataclass
class ChangeEntry:
    """One changelog entry."""
    version: tuple
    on: date
    category: str
    description: str

    def version_str(self):
        return ".".join(str(part) for part in self.version)


class ModelChangelog:
    """Append-only structured changelog for one model."""

    def __init__(self, model_name):
        self.model_name = model_name
        self._entries = []

    def add(self, entry):
        if entry.category not in CATEGORIES:
            raise ValueError("unknown category %r" % (entry.category,))
        if not isinstance(entry.on, date):
            raise TypeError("on must be a datetime.date")
        if len(entry.version) != 3 or any(not isinstance(p, int) or p < 0
                                          for p in entry.version):
            raise ValueError("version must be a (major, minor, patch) tuple")
        if self._entries and entry.version <= self._entries[-1].version:
            raise ValueError("version %s is not newer than %s"
                             % (entry.version_str(),
                                self._entries[-1].version_str()))
        self._entries.append(entry)
        return entry

    def entries(self):
        return list(self._entries)

    def latest_version(self):
        return self._entries[-1].version if self._entries else None

    def since(self, version):
        """Entries newer than the given version tuple."""
        return [e for e in self._entries if e.version > tuple(version)]

    def by_category(self, category):
        if category not in CATEGORIES:
            raise ValueError("unknown category %r" % (category,))
        return [e for e in self._entries if e.category == category]

    def breaking_changes(self):
        return [e for e in self._entries if e.category in BREAKING]

    def render_markdown(self):
        lines = ["# Changelog: %s" % self.model_name, ""]
        for entry in reversed(self._entries):
            lines.append("## %s - %s" % (entry.version_str(),
                                         entry.on.isoformat()))
            lines.append("- **%s**: %s" % (entry.category, entry.description))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"

    def entry_count(self):
        return len(self._entries)
