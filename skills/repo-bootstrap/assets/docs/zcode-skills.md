# ZCode skills

Source: <https://zcode.z.ai/en/docs/skill>

## Location and invocation

- User-level skills: `~/.zcode/skills/<skill-name>/SKILL.md`
- The directory name is the skill name referenced in chat.
- Invoke with `$skill-name` in the input (e.g. `$branch-review review my changes`); skills also appear in the `/` menu under **Skills**.
- Manage in **Settings → Skills**: per-skill enable switches, search, refresh after edits, and per-skill diagnostics for ignored skills.

## Import from external agents

**Settings → Skills → Import** scans other tools' skill directories (Claude Code, Codex CLI, OpenClaw, Augment, Windsurf) and imports selected skills either as **symlink** (follows the source; needs the source path to stay available) or **copy** (independent), to **Global** or the current **Project**.

## Hard limits

- Frontmatter must include `name` and `description`; a skill missing either is ignored, with the reason shown in settings-page diagnostics.
- `description` over 1024 chars drops the **whole skill** (not truncated). Put long instructions in the body.
- Body over 100KB is truncated when loaded.

## Context budget

Each turn injects the metadata of every enabled skill (name + up to 250 chars of description); bodies load only on invocation. All skills share one fixed metadata budget — exceed it and injection degrades to names only, so the model cannot tell when to use which skill and auto-trigger rates drop sharply. Keep only the skills actually in use enabled; disabled skills are neither injected nor invocable.

## Skill visible in the panel but never used

1. Degraded metadata from too many installed skills — disable unused ones.
2. Vague `description` that does not spell out when to use the skill.
3. Subagent with a custom `tools` allowlist that omits the skill tool.
4. Parent plugin disabled (disabling removes its skills immediately).

## Distribution

No standalone skill marketplace. To distribute a set of skills, package them as a plugin with a **flat** `skills/<skill-name>/SKILL.md` layout and ship it via a plugin marketplace (GitHub repo, git URL, or local directory). Skills nested under grouping directories are not picked up.

## Remote hosts

User-level skills live on the local machine; use **Sync Skill** in the workspace header's Sync dropdown (over SSH/WSL) to copy them to the remote host.
