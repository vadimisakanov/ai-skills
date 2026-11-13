# Kilo Code skills

Source: <https://kilo.ai/docs/customize/skills>

## Locations

- Global (user-level): `~/.kilo/skills/<name>/SKILL.md`
- Project (workspace-level): `.kilo/skills/<name>/SKILL.md`
- Compatibility directories, loaded alongside: `~/.agents/skills/` and `.agents/skills/` (open agent standard, by default); `~/.claude/skills/` and `.claude/skills/` (when Claude Code compatibility is enabled)

On a name clash, project-level skills take precedence over global skills.

Extra locations and remote sources go in `kilo.jsonc` (project or global):

```jsonc
{
  "skills": {
    "paths": ["/absolute/path", "~/home/relative", "relative/to/project"],
    "urls": ["https://example.com/.well-known/skills/"]
  }
}
```

## Trust rules for external paths

- Paths declared only in **project** config are untrusted: their `SKILL.md` files and `{file:...}` references must stay inside the project, even when the path is absolute or `~/`-relative. Violations fail with `blocked file reference outside project config scope`.
- To load skills from outside a project (e.g. this repo), declare the `skills.paths` entry in **user-level** config: `~/.config/kilo/kilo.jsonc`. Global-config absolute paths are treated as trusted.

## Loading and invocation

- Skills are scanned at session start; `/reload` re-scans without a new session.
- `name` in frontmatter must match the skill directory name (hard error otherwise).
- Every loaded skill is also a slash command; the `/` menu lists skills in a **Skills** group. A skill sharing a name with a command is listed as `/name:skill`.

## Remote URLs

The server must serve an `index.json` manifest:

```json
{
  "skills": [
    { "name": "skill-name", "version": "2", "files": ["SKILL.md", "references/file.md"] }
  ]
}
```

Files are fetched from `{url}/{skill-name}/{file}`. Bump `version` when content or the file list changes; the new version downloads fully and atomically replaces the cache, and a failed download keeps the previous version.

## Embedded shell commands

Trusted skills may embed `` !`command` `` placeholders; output replaces the placeholder before the body reaches the model.

- Trusted: global locations (`~/.kilo/skills/`, `~/.agents/skills/`, `~/.claude/skills/`), built-in skills, and absolute paths declared in global config. **Project and remote skills never execute commands** — their placeholders become a marker instead.
- Loading a trusted skill with commands shows one approval prompt listing every command; approving runs all, rejecting aborts the load. Any deny rule still blocks.
- Kill switch: `KILO_DISABLE_SKILL_SHELL` environment variable.
- Commands run in the project directory, with a per-command timeout; output is truncated before inlining. Placeholders inside fenced code blocks are documentation and never execute.

## Troubleshooting

- **Skill not loading**: verify `name` + `description` in frontmatter and that `name` matches the directory; run `/reload` or start a new session; check the path is `skills/<name>/SKILL.md` (not nested deeper); verify `skills.paths`/`skills.urls` values in `kilo.jsonc`.
- **Verify availability**: ask the agent "What skills do you have available?" — the most reliable check.
- **Confirm a skill was used**: look for a `skill` tool call in the conversation; its output includes the full skill content.
