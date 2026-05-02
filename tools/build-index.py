#!/usr/bin/env python3
"""Generate skills-index.json by walking every SKILL.md.

Run from the repo root: ``python tools/build-index.py``.

Reads YAML frontmatter from each SKILL.md, validates the required
fields, enforces name uniqueness across all namespaces, and writes a
flat ``skills-index.json`` at the repo root. The Designer marketplace
fetches this file once on workspace open.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REQUIRED_FIELDS = ("name", "description")
OPTIONAL_FIELDS = ("version", "author", "license")
NAMESPACES = ("robomotion", "hermes", "community")


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    raw = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    try:
        import yaml  # PyYAML
    except ImportError:
        sys.exit("PyYAML required: pip install pyyaml")
    try:
        fm = yaml.safe_load(raw) or {}
    except yaml.YAMLError as e:
        return None, body
    return fm if isinstance(fm, dict) else None, body


def normalize_compatibility(fm: Dict[str, Any]) -> List[str]:
    raw = fm.get("compatibility")
    if raw is None:
        # Default — most skills work with both runtimes. Skills that
        # need explicit dispatch (`prerequisites.commands`) tend to
        # only fit Hermes today, but the markdown-only ones are
        # framework-agnostic, so default both and let authors narrow.
        return ["hermes", "llm"]
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(x) for x in raw if x]
    return ["hermes", "llm"]


def normalize_tags(fm: Dict[str, Any]) -> List[str]:
    """Pull tags from either ``tags`` or ``metadata.hermes.tags``."""
    tags = fm.get("tags")
    if not tags:
        meta = fm.get("metadata") or {}
        if isinstance(meta, dict):
            hermes_meta = meta.get("hermes") or {}
            if isinstance(hermes_meta, dict):
                tags = hermes_meta.get("tags")
    if isinstance(tags, str):
        return [tags]
    if isinstance(tags, list):
        return [str(t) for t in tags if t]
    return []


def build_index(repo_root: Path) -> Dict[str, Any]:
    skills: List[Dict[str, Any]] = []
    seen_names: Dict[str, str] = {}  # name -> path (for collision diagnostics)
    errors: List[str] = []

    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        rel_path = skill_md.parent.relative_to(repo_root)
        ns = rel_path.parts[0] if rel_path.parts else ""
        if ns not in NAMESPACES:
            errors.append(f"{rel_path}: outside known namespaces ({NAMESPACES})")
            continue

        text = skill_md.read_text(encoding="utf-8")
        fm, _ = parse_frontmatter(text)
        if fm is None:
            errors.append(f"{rel_path}: missing or unparseable frontmatter")
            continue

        missing = [k for k in REQUIRED_FIELDS if not fm.get(k)]
        if missing:
            errors.append(f"{rel_path}: missing required fields {missing}")
            continue

        name = str(fm["name"]).strip()
        if name in seen_names:
            errors.append(
                f"{rel_path}: duplicate name {name!r} (also at {seen_names[name]})"
            )
            continue
        seen_names[name] = str(rel_path)

        entry: Dict[str, Any] = {
            "name": name,
            "path": str(rel_path).replace("\\", "/"),
            "description": str(fm["description"]).strip(),
            "tags": normalize_tags(fm),
            "compatibility": normalize_compatibility(fm),
        }
        for field in OPTIONAL_FIELDS:
            value = fm.get(field)
            if value:
                entry[field] = str(value).strip()
        prereq = fm.get("prerequisites")
        if isinstance(prereq, dict):
            entry["prerequisites"] = prereq

        skills.append(entry)

    return {
        "version": 1,
        "name": "Robomotion Skills",
        "description": "Curated and vendored skills for Robomotion agents.",
        "skills": skills,
        "_errors": errors,  # stripped before write if empty
    }


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    index = build_index(repo_root)

    errors = index.pop("_errors", [])
    if errors:
        print("Index build had errors:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)

    out = repo_root / "skills-index.json"
    out.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")

    print(f"Wrote {out} ({len(index['skills'])} skills, {len(errors)} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
