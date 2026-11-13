# ai-skills

Personal repo of LLM agent skills. Each top-level directory is one skill, consumable by Kilo Code, ZCode, and any agent implementing the Agent Skills spec (<https://agentskills.io>).

Reference docs live in `ai/docs/`:

- `ai/docs/skill-format.md` — shared SKILL.md format and authoring rules
- `ai/docs/kilo-skills.md` — Kilo Code locations, config, trust rules
- `ai/docs/zcode-skills.md` — ZCode locations, limits, context budget
- `ai/docs/install.md` — how to consume skills from this repo in each tool

Tests live in `ai/tests/` (see `ai/tests/README.md`): they validate every skill for cross-tool compatibility, repo-scoped writes, and absence of harmful commands.

## Layout

- Skills live under `skills/`: one directory per skill, `skills/<skill-name>/SKILL.md` (same shape as the ZCode plugin layout).
- Flat inside `skills/` only. No grouping/category directories — ZCode does not pick up nested skills.
- Repo root holds only `skills/` and `ai/`; `ai/` holds repo docs and tests, never skills.
- Optional per-skill subdirectories: `scripts/` (executable code), `references/` (loaded-on-demand docs), `assets/` (templates, resources).

## SKILL.md rules (all tools)

- YAML frontmatter with required `name` and `description`; optional `license`, `compatibility`, `metadata`.
- `name`: max 64 chars, lowercase letters/numbers/hyphens only, no leading/trailing hyphen, and MUST match the directory name.
- `description`: max 1024 chars. Must state what the skill does AND when to use it — agents decide to invoke purely from this text; over 1024 chars drops the whole skill in ZCode.
- Body: markdown instructions, loaded on demand. Keep under 100KB (ZCode truncates).
- Keep descriptions tight: every enabled skill's metadata is injected each turn (ZCode shows ~250 chars per skill); bloat degrades triggering across the board.

## Authoring checklist

Before finishing any skill edit:

1. Frontmatter parses; `name` matches the directory name; `description` ≤ 1024 chars and names concrete trigger phrases/task types.
2. Body is self-contained: an agent reading only `SKILL.md` can execute the workflow end to end.
3. No secrets or machine-specific absolute paths.
4. Avoid embedded shell commands (`` !`cmd` ``) — they only execute for trusted skill locations in Kilo; treat as nonportable.
5. Markdown is clean: balanced fences/markers, no trailing whitespace.
6. Run `ai/tests/run.sh` (Python 3 stdlib) — all tests pass. Fix the skill, not the tests, when they fail.

## Conventions

- Write the body for an agent audience: imperative voice, numbered workflow steps, explicit verification commands, explicit structure for the final report.
- Keep skills general and reusable across repos; repo-specific detail belongs in that repo's AGENTS.md, not here.
- Do not commit unless explicitly asked.
