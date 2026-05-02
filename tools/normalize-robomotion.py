#!/usr/bin/env python3
"""Normalize frontmatter on every /robomotion/ SKILL.md.

Mirrors tools/normalize-hermes.py for the /robomotion/ namespace.
Standardizes the fields the Designer marketplace renders:

* ``author`` → ``robomotion`` (always; "by robomotion" badge).
* ``version`` → ``1.0.0`` if missing.
* ``license`` → ``Apache-2.0`` if missing.

Tags are *not* touched — they're per-skill content and live wherever
the skill author put them.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")


DEFAULTS = {
    "author": "robomotion",
    "version": "1.0.0",
    "license": "Apache-2.0",
}


def split_frontmatter(text: str):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    fm_text = text[3:end].strip()
    body = text[end + 4 :]
    return fm_text, body


def normalize_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    if fm_text is None:
        print(f"  skip (no frontmatter): {path}", file=sys.stderr)
        return False

    fm = yaml.safe_load(fm_text) or {}
    if not isinstance(fm, dict):
        print(f"  skip (frontmatter not a dict): {path}", file=sys.stderr)
        return False

    changed = False
    if fm.get("author") != DEFAULTS["author"]:
        fm["author"] = DEFAULTS["author"]
        changed = True
    for key in ("version", "license"):
        if not fm.get(key):
            fm[key] = DEFAULTS[key]
            changed = True

    if not changed:
        return False

    head_keys = ("name", "description", "version", "author", "license", "tags")
    head = {k: fm[k] for k in head_keys if k in fm}
    rest = {k: v for k, v in fm.items() if k not in head_keys}

    new_fm = yaml.safe_dump(
        {**head, **rest}, sort_keys=False, allow_unicode=True
    ).rstrip()
    new_text = f"---\n{new_fm}\n---\n{body.lstrip(chr(10))}"
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    ns_root = repo_root / "robomotion"
    if not ns_root.is_dir():
        sys.exit(f"no /robomotion/ at {ns_root}")

    changed = 0
    total = 0
    for p in sorted(ns_root.rglob("SKILL.md")):
        total += 1
        if normalize_file(p):
            changed += 1

    print(f"Normalized {changed} / {total} SKILL.md files under robomotion/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
