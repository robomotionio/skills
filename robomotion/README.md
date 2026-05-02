# Robomotion-curated skills

This namespace holds skills written and maintained by the Robomotion
team — primarily wrappers for SaaS APIs (Airtable, Notion, GitHub,
Stripe, …) dispatched through the `robomotion <skill>` CLI.

External vendor skills live under [`../hermes/`](../hermes/) (vendored
from Hermes upstream).

## Pattern

Every skill in this namespace follows the same shape:

```
robomotion/<skill-name>/
├── SKILL.md          ← prompt instructions + workflow guide
└── eval-set.json     ← evaluation harness (used by tools/run_eval.py
                       in the source repo)
```

The SKILL.md body explains when to use the skill, prerequisites
(`robomotion install <skill>`, vault credentials, etc.), and a worked
example of session-mode flow for multi-step operations. The agent
dispatches via `execute_bash` — Hermes via its built-in shell, LLM
Agent via ADK's `ExecuteBashTool`.

## Adding a Robomotion skill

1. `mkdir robomotion/<skill-name>` and create `SKILL.md` per
   [SCHEMA.md](../SCHEMA.md).
2. Add `eval-set.json` with at least one happy-path eval (see existing
   skills for the format).
3. `python ../tools/build-index.py` to refresh `skills-index.json`.
4. Open a PR.

Set `author: robomotion` in the frontmatter so the marketplace card
renders the right badge.
