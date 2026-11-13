---
name: branch-review
description: Review the diff between the current git branch and main. Walks the full merge-base diff in logical chunks, fixes high-confidence typos (spelling, broken markdown, wrong path separators, trailing whitespace) and small safe bugs, updates the ai-docs wiki when the branch adds roles/playbooks/inventories, verifies with syntax checks, and reports fixes vs flagged items without committing. Use when asked to review a branch diff, check for typos, or update ai-docs/repo docs after changes.
---

# Branch Review (diff vs main, typo check, docs update)

Workflow for requests like "review the difference between current branch and main", "check for typos", "add updates to ai-docs if needed".

## 1. Establish scope

- `rtk git status` and `rtk git branch --show-current` — confirm a clean tree and the branch name
- `rtk git log --oneline main..HEAD` — commits ahead of main
- `rtk git diff main...HEAD --stat` — full changed-file list

Use the three-dot (merge-base) diff so new commits on main itself do not pollute the
review. Files present in the working tree but absent from the diff are out of scope.
Renames show as 0-line entries — note them, do not review unchanged content.

## 2. Read the entire diff in logical chunks

Never review from the stat alone. Order:

1. Playbooks and inventories (structure: hosts, groups, group_vars)
2. Role logic: tasks, handlers, defaults, vars
3. Content: templates, READMEs, lint configs, meta

If the diff output truncates a long file, read the file directly.

## 3. Review checklist — bugs first, then typos

Functional issues (report; fix only with clear one-line justification):

- Modified expressions that change semantics. Example: `failed_when: some_var | bool`
  where the variable's default is a lazily-evaluated expression string such as
  `'gitlab_restart.rc != 0'` — the `| bool` cast silently turns it into `False`,
  so failures are never detected. Restore lazy evaluation by dropping the filter.
- References to nonexistent roles, files, groups, or hosts (commented-out blocks
  referencing an existing role are fine).
- Indentation inconsistent between sibling blocks in new files.

Typos — fix only high-confidence cases:

- Spelling/grammar in prose and task names: "of" → "if", "os" → "OS",
  "hwe kernel" → "HWE kernel", product/OS name capitalization in newly written lines.
- Broken markdown: unbalanced `**` bold markers, stray closing markup.
- Wrong path separators: `templates\file.j2` → `templates/file.j2`.
- Jinja2 whitespace consistency: `{{ var}}` → `{{ var }}`.
- Trailing whitespace, broken list indentation under a mapping key.
- Task-name capitalization (start with a capital letter) in new roles.

Do NOT:

- Mass-edit capitalization or spelling inside vendored/upstream-derived files
  (e.g. a README forked from geerlingguy) — flag it in the report instead.
- Translate or reword non-English notes — fix markup only, keep the language.
- Refactor or reformat whole files; keep each edit minimal and local.

## 4. Apply fixes

- Batch small edits per file; rewrite only tiny task files where cleanup is safe.
- Normalize indentation only in files added by this branch.
- Leave all changes uncommitted unless explicitly asked to commit.

## 5. Update ai-docs if needed

If the repo has an LLM wiki (e.g. `ai-docs/repo-docs.md`), update it when the branch:

- adds a role → Directory Structure section (one-line purpose; for vendored roles
  note the upstream origin)
- adds a playbook → Key Playbooks table
- adds/renames inventories or host groups → Inventory Structure section
  (per-inventory breakdown, which playbook targets which group)
- correct statements that contradict AGENTS.md (e.g. secrets policy must say
  HashiCorp Vault `community.hashi_vault`, not ansible-vault, if AGENTS.md says so)

Keep descriptions scoped to what the diff actually shows — do not guess the behavior
of roles you have not read. Flag (but do not edit) other stale docs such as an
AGENTS.md inventory list that no longer matches reality.

## 6. Verify

- `ansible-playbook --syntax-check <playbook> -i <inventory>` for every touched
  playbook (per AGENTS.md). Host-pattern warnings for groups outside the chosen
  inventory are expected and harmless.
- YAML lint if a linter is configured; a missing local yaml lib is not a failure
  if syntax-check already passed.

## 7. Report

Structure the final answer as:

1. Branch overview — commits, files, insertions; what the branch adds/changes/renames
2. Typos/issues fixed — file:line, what and why
3. Functional bug fixes — called out separately with justification
4. Flagged, not changed — style inconsistencies, stale docs, open TODOs
5. ai-docs changes
6. Verification results and confirmation that changes are uncommitted
