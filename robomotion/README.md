# Robomotion-curated skills

This namespace holds skills written or vetted by the Robomotion team —
typically wrappers for Robomotion-specific automations (Designer
shortcuts, deskbot tooling, internal services) that wouldn't make sense
upstream.

External vendor skills live under [`../hermes/`](../hermes/) (vendored
from Hermes upstream).

## Adding a Robomotion skill

1. `mkdir robomotion/<skill-name>` and create `SKILL.md` per
   [SCHEMA.md](../SCHEMA.md).
2. `python ../tools/build-index.py` to refresh `skills-index.json`.
3. Open a PR.

Set `author: robomotion` in the frontmatter so the marketplace card
renders the right badge.
