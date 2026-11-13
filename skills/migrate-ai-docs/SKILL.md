---
name: migrate-ai-docs
description: Move a repo's LLM wiki and documentation from the legacy ai-docs/ directory to the ai/docs/ convention used by ai-skills repos - relocates every file including dotfiles, removes the old directory once empty, and rewrites ai-docs path references in AGENTS.md, README, scripts, and skills. Use when asked to migrate ai-docs to ai/docs, move repo docs into ai/docs, or consolidate documentation directories.
---

# Migrate ai-docs/ to ai/docs/

Moves documentation from the legacy `ai-docs/` directory to the `ai/docs/`
convention, then updates every reference to the old path.

## 1. Survey the target repo

- If `ai-docs/` does not exist, report that there is nothing to migrate and stop.
- Inventory every file under `ai-docs/` including dotfiles and subdirectories;
  list them with relative paths.
- Check what already exists: `ai/`, `ai/docs/`, and any file in `ai/docs/`
  whose name matches a file to be moved.
- List all references to the old path:

  `grep -rn "ai-docs" --exclude-dir=.git .`

## 2. Plan the move

- Map each `ai-docs/<path>` to `ai/docs/<path>`, preserving subdirectory
  structure.
- Never overwrite an existing `ai/docs/<path>`: on a name conflict, keep both
  files, flag the conflict, and ask the user which one wins.
- Dotfiles move too — do not rely on a shell glob that skips them; enumerate
  the inventory from step 1 and move file by file.

## 3. Move the files

- Create the destination: `mkdir -p ai/docs`
- Move each planned file with a plain `mv` so changes stay unstaged; git
  detects the renames at commit time.
- After all files are moved, remove the old directory only if it is empty:
  `rmdir ai-docs`. If it still contains anything, leave it and report the
  leftovers.

## 4. Update references

- In every file that references the old path (typically AGENTS.md, README,
  scripts, and other skills), rewrite `ai-docs/` to `ai/docs/`.
- Keep each edit minimal and local; do not reword surrounding prose.
- Do NOT rewrite historical mentions (changelogs, commit-quote blocks, notes
  that explicitly describe the old layout) — flag them instead.

## 5. Verify

- File count under `ai/docs/` equals the inventory from step 1 plus any
  pre-existing files.
- Re-run the reference search:

  `grep -rn "ai-docs" --exclude-dir=.git .`

  Only intentional historical mentions may remain; path references must be
  gone.
- Check that relative links between moved docs still resolve (paths inside
  the moved set are relative-unchanged; links from repo root docs need the
  new prefix).

## 6. Report

Structure the final answer as:

1. Inventory — files found under `ai-docs/` before the move
2. Files moved — old path → new path
3. References updated — file:line for each rewrite
4. Flagged, not changed — name conflicts, leftover files, historical mentions
5. Verification results
6. Confirmation that all changes are uncommitted

Leave all changes uncommitted unless explicitly asked to commit.
