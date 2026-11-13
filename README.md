# ai-skills

Personal repo of LLM agent skills for Kilo Code, ZCode, and any agent implementing the Agent Skills spec (<https://agentskills.io>).

## Layout

- `skills/<skill-name>/SKILL.md` — one skill per directory (same shape as the ZCode plugin layout)
- `ai/docs/` — skill format and per-tool reference docs
- `ai/tests/` — compatibility, scope, and safety test suite; run `ai/tests/run.sh`

## Skills

- `branch-review` — review the diff between the current git branch and main; typo fixes, bug flags, docs updates
- `repo-bootstrap` — scaffold a skills repo with AGENTS.md, ai/docs, and the ai/tests suite
- `migrate-ai-docs` — move a repo's docs from legacy `ai-docs/` to `ai/docs/` and rewrite references
