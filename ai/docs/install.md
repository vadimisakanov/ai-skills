# Installing skills from this repo

Every directory under `skills/` in this repo is a standalone skill. Paths
below assume the repo is at `~/git/vadimisakanov/ai-skills`.

The `skills/` directory already matches the flat layout ZCode uses for
plugins, so the whole directory can also be packaged as a plugin as-is.

## Kilo Code

Option A — user-level config (recommended: trusted, available in all workspaces):

```jsonc
// ~/.config/kilo/kilo.jsonc
{
  "skills": {
    "paths": ["~/git/vadimisakanov/ai-skills/skills"]
  }
}
```

Option B — symlink into a default location:

```bash
ln -s ~/git/vadimisakanov/ai-skills/skills/branch-review ~/.agents/skills/branch-review
# or ~/.kilo/skills/branch-review
```

Then `/reload` or start a new session. Project-config paths pointing outside the project stay untrusted, so prefer Option A or B for this repo.

## ZCode

Symlink or copy each skill into `~/.zcode/skills/`:

```bash
mkdir -p ~/.zcode/skills
ln -s ~/git/vadimisakanov/ai-skills/skills/branch-review ~/.zcode/skills/branch-review
```

Then **Settings → Skills → Refresh** and enable the switch. Alternatively use **Settings → Skills → Import** and pick symlink or copy mode.

## Any spec-compliant agent

Copy or symlink the `skills/<skill-name>/` directory into the agent's skills
directory (e.g. `~/.agents/skills/` per the open agent standard).

## Invocation

- ZCode: `$branch-review ...`
- Kilo: `/branch-review` or just describe the task and let the agent match the description.

Symlinks keep edits in this repo live; copies decouple and need re-copying after changes.
