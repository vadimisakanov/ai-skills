# Skill format (Agent Skills spec)

Shared SKILL.md format used by Kilo Code, ZCode, and other agents implementing the Agent Skills spec (<https://agentskills.io/specification>).

A skill is a directory containing one required file, `SKILL.md`:

```text
<skill-name>/
├── SKILL.md           # required: metadata + instructions
├── scripts/           # optional: executable code
├── references/        # optional: loaded-on-demand docs
└── assets/            # optional: templates, resources
```

## Frontmatter fields

| Field           | Required | Rules |
|-----------------|----------|-------|
| `name`          | yes      | Max 64 chars; lowercase letters, numbers, hyphens; no leading/trailing hyphen; must match the parent directory name |
| `description`   | yes      | Max 1024 chars; states what the skill does AND when to use it |
| `license`       | no       | License name or reference to a bundled license file |
| `compatibility` | no       | Environment requirements (intended product, system packages, network access) |
| `metadata`      | no       | Arbitrary key-value mapping (`author`, `version`, ...) |

Minimal example:

```md
---
name: code-review-checklist
description: Review code changes with a focused checklist for correctness, regressions, tests, and maintainability. Use when asked to review a PR, merge request, or local diff.
---

# Code Review Checklist

...
```

## How agents use skills

1. **Discovery** — at session start, only metadata (name, description, path) is read.
2. **Prompt inclusion** — metadata for enabled skills is injected into the system prompt.
3. **On-demand load** — when a request "clearly and unambiguously" matches a description, the full body is read and followed.

There is no keyword matching or semantic search; the LLM decides from the description text alone. Consequences:

- Explicit invocation always works: "use the api-design skill", `$skill-name` (ZCode), `/skill-name` (Kilo).
- Vague descriptions cause unreliable auto-triggering. Spell out concrete trigger phrases and task types.
- Keep the body self-contained; reference bundled files by relative path so the agent can read them as needed.

## Description checklist

- Lead with the job, then the trigger: "Review the diff between... Use when asked to review a branch diff, check for typos, ..."
- Name the artifacts, commands, and request phrasings it applies to.
- One paragraph; long detail belongs in the body, not the description.
- Exceeding 1024 chars drops the whole skill in ZCode (not truncated), so stay well under it.

## What should become a skill

- A repeated workflow (code review, API debugging, release notes, test reports).
- A team-expected consistent output format.
- A workflow needing background knowledge, checklists, templates, or examples.
- Something reused across projects or conversations.

Use a command/prompt for a simple saved prompt; use a skill for a complete working method.
