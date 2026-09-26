# Model Changelog Generator

Structured model release changelogs with monotonic versioning, category sections, and markdown rendering.

**Stack:** Python 3.12 · stdlib only · unittest

## Problem

Model releases need structured changelogs: entries carry a version
tuple, a date, a category (added/changed/deprecated/removed/fixed/
security), and a description. add() enforces monotonic version
increases; render_markdown() produces a keep-a-changelog-style
document newest-first; breaking_changes() surfaces removed and
deprecated entries for migration review.

## Design decisions

- Versions are (major, minor, patch) tuples compared lexicographically.
- Entries are stored in insertion order; the last entry's version is
- since(version) filters to newer entries for release-note diffs.

## Layout

- `README.md`
- `src/model_changelog.py`
- `tests/test_model_changelog.py`
- `LICENSE`
- `.gitignore`

## Setup

No third-party dependencies — Python 3.11+ standard library only.

```bash
cd govops-model-changelog
python -m unittest discover -s tests -v
```

## Usage

```python
from datetime import date
from src.model_changelog import ChangeEntry, ModelChangelog

c = ModelChangelog("fraud-scorer")
c.add(ChangeEntry((1, 0, 0), date(2026, 5, 1), "added", "initial release"))
print(c.render_markdown())
```

## License

MIT — see [LICENSE](LICENSE).
