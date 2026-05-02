# Robomotion Skills

Curated and vendored skills for Robomotion agents.

A **skill** is a single SKILL.md file — YAML frontmatter plus markdown
instructions — that gets injected into an agent's system prompt at
runtime. Skills are how we teach a generic LLM/Hermes agent how to
operate a specific domain (email, GitHub, arXiv, …) without writing
imperative code.

This repository holds the catalog. Two consumer agents read from it:

- **Hermes Agent** (`packages-main/src/hermes-agent`)
- **LLM Agent** (`packages-main/src/agents`)

Both are configured from the **Robomotion Designer** marketplace; users
toggle skills on per agent node. Deskbot fetches the selected skills
to the host before each flow run; the agent reads them off disk.

See [SCHEMA.md](SCHEMA.md) for the on-disk layout, SKILL.md format, and
the Designer / deskbot / agent contract.

## Layout

```
skills/
├── robomotion/      ← Robomotion-curated skills
├── hermes/          ← Vendored from Hermes upstream (Nous Research), by category
└── community/       ← (future) Vetted community contributions
```

## Adding a skill

1. Pick a namespace.
2. `mkdir <namespace>/<skill-name>`, write `SKILL.md` (see SCHEMA.md
   for the frontmatter contract).
3. `python tools/build-index.py` to refresh `skills-index.json`.
4. Open a PR.

## Cross-references

- Designer marketplace UI:
  `robomotion-new-designer/src/components/skills/`
- Deskbot pre-flight installer:
  `robomotion-deskbot/skill/installer.go`
- Agent skill loaders:
  - `packages-main/src/hermes-agent/nodes/skills/skill_loader.py`
  - `packages-main/src/agents/nodes/agent/llm_agent.py` (`_load_skills`)
