#!/usr/bin/env python3
"""Normalize frontmatter on every /hermes/ SKILL.md.

Runs after vendoring/syncing from Hermes upstream. Standardizes the
fields the Designer marketplace needs:

* ``author`` → ``hermes`` (uniform "by hermes" badge in the marketplace
  card; original attribution is preserved in the SKILL.md body where
  upstream put it).
* ``version`` → ``1.0.0`` if missing.
* ``license`` → ``MIT`` if missing (matches Hermes-agent's upstream
  license).

All other fields are preserved verbatim — description, tags,
prerequisites, metadata.hermes.tags, etc.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML required: pip install pyyaml")


DEFAULTS = {
    "author": "hermes",
    "version": "1.0.0",
    "license": "MIT",
}


def split_frontmatter(text: str):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    fm_text = text[3:end].strip()
    body = text[end + 4 :]  # skip "\n---"
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
    # author is always overwritten to canonicalize the marketplace badge.
    if fm.get("author") != DEFAULTS["author"]:
        fm["author"] = DEFAULTS["author"]
        changed = True
    # version and license are filled only when missing.
    for key in ("version", "license"):
        if not fm.get(key):
            fm[key] = DEFAULTS[key]
            changed = True

    if not changed:
        return False

    # Re-serialize with stable ordering: name, description first,
    # then version/author/license, then everything else.
    head_keys = ("name", "description", "version", "author", "license")
    head = {k: fm[k] for k in head_keys if k in fm}
    rest = {k: v for k, v in fm.items() if k not in head_keys}

    new_fm = yaml.safe_dump(
        {**head, **rest}, sort_keys=False, allow_unicode=True
    ).rstrip()
    new_text = f"---\n{new_fm}\n---\n{body.lstrip(chr(10))}"
    path.write_text(new_text, encoding="utf-8")
    return True


FORBIDDEN_LICENSE_MARKERS = (
    "Anthropic, PBC. All rights reserved",
    # Add more proprietary-license markers here as we discover them.
)


def find_forbidden_licenses(root: Path) -> list[Path]:
    """Return any LICENSE-like file inside the tree that we are not
    allowed to redistribute.

    Hermes upstream occasionally re-bundles vendor skills carrying
    proprietary licenses (e.g. an Anthropic skill copied verbatim).
    We can't ship those — and frontmatter normalization would silently
    paper over the conflict, so we scan for the marker text directly.
    """
    hits = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        name = p.name.upper()
        if not (name.startswith("LICENSE") or name.startswith("COPYING")
                or name.startswith("NOTICE")):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if any(marker in text for marker in FORBIDDEN_LICENSE_MARKERS):
            hits.append(p)
    return hits


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    hermes_root = repo_root / "hermes"
    if not hermes_root.is_dir():
        sys.exit(f"no /hermes/ at {hermes_root}")

    forbidden = find_forbidden_licenses(hermes_root)
    if forbidden:
        print("ERROR: forbidden-license content found under hermes/:",
              file=sys.stderr)
        for p in forbidden:
            rel = p.relative_to(repo_root)
            print(f"  {rel}", file=sys.stderr)
        print("Remove the containing skill directory before re-running.",
              file=sys.stderr)
        return 2

    changed = 0
    total = 0
    for p in sorted(hermes_root.rglob("SKILL.md")):
        total += 1
        if normalize_file(p):
            changed += 1

    print(f"Normalized {changed} / {total} SKILL.md files under hermes/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
