---
name: repo-bootstrap
description: Bootstrap a personal LLM agent skills repo with standard scaffolding - skills/ directory layout, AGENTS.md conventions, ai/docs reference docs (Agent Skills spec, Kilo Code, ZCode, install guide), and a stdlib-only ai/tests suite that validates every skill for cross-tool compatibility, repo-scoped writes, and safety. Use when initializing a new skills repo, adding this layout to an existing one, or restoring missing docs or tests.
---

# Skill repo bootstrap

Standardizes a skills repo so every `skills/<skill-name>/SKILL.md` is valid
for Kilo Code (VS Code extension), ZCode, and Agent-Skills-spec consumers such
as opencode or pi.dev. All templates are bundled in `assets/` and
self-contained.

## 1. Survey the target repo

- Skills live under `skills/`: list `skills/*/SKILL.md`; each parent directory
  is an existing skill. Create `skills/` if it does not exist.
- If skills sit at the repo root instead of under `skills/`, propose moving
  them into `skills/` and ask the user before moving anything.
- Check what already exists: `skills/`, `AGENTS.md`, `ai/docs/`, `ai/tests/`,
  `README.md`.
- Never delete or silently overwrite user-authored content: merge missing
  sections into an existing AGENTS.md, and only replace generated docs/tests
  after confirming with the user.

## 2. Create AGENTS.md

- Copy `assets/AGENTS.md` to the repo root as `AGENTS.md`.
- Replace `{{REPO_NAME}}` with the repo name and `{{REPO_DESCRIPTION}}` with a
  one-line description ending in a period.
- If `AGENTS.md` already exists: keep user sections, add only missing sections
  from the template, and resolve contradictions in favor of the user's rules.

## 3. Create ai/docs

- Copy every file from `assets/docs/` into `ai/docs/`.
- In `ai/docs/install.md`, replace `{{REPO_PATH}}` with the repo's absolute
  path and swap `<skill-name>` examples for the repo's real skill names.
- Leave the other docs unchanged; they are tool references, not repo-specific.

## 4. Create ai/tests

- Copy every file from `assets/tests/` into `ai/tests/`.
- Make the runner executable: `chmod +x ai/tests/run.sh`
- Run the suite from the repo root: `python3 -m unittest discover -s ai/tests -v`
  (equivalently `ai/tests/run.sh`). Python 3.8+ stdlib only; no dependencies.

## 5. Fix failures by fixing skills, not tests

The tests encode the guarantees this scaffolding exists to enforce:

- compatibility — skills/ flat layout, frontmatter rules, portability,
  simulated discovery from every documented skills root
- scope — no writes outside the target repo, permission gate for commits
- safety — no destructive commands in the instructions

Relaxing or skipping a test to make a skill pass requires explicit user
approval.

## 6. Report

Structure the final answer as:

1. Repo state before — skills found, existing files
2. Files created or merged — `AGENTS.md`, `ai/docs/*`, `ai/tests/*`
3. Skills detected and their per-suite test status
4. Test suite output summary
5. Confirmation that all changes are uncommitted

Leave all changes uncommitted unless explicitly asked to commit.
