# ai-skills test suite

Static test suite enforcing three guarantees for every skill in this repo
(all `skills/*/SKILL.md` files are picked up automatically):

1. **Cross-tool compatibility** (`test_compat.py`) — the skill works with the
   Kilo Code VS Code extension and any Agent-Skills-spec consumer (opencode,
   pi.dev, ...): flat layout, Agent Skills frontmatter rules (name/description,
   64/1024-char limits, name == directory name), 100KB body cap, portability
   (no Kilo-only shell placeholders, no machine-specific paths), plus a loader
   simulation that installs each skill into every documented skills root
   (`.kilo/skills/`, `.agents/skills/`, `.claude/skills/`, `.zcode/skills/`,
   `.opencode/skill/`, `.opencode/skills/`) and re-runs discovery + validation.
2. **Repo-scoped writes** (`test_scope.py`) — no command targets paths outside
   the target repo, none mutates remote/global/OS state (push, global config,
   system packages, ssh/docker/kubectl), and the instructions must carry an
   explicit permission gate for commits/pushes.
3. **No harmful commands** (`test_safety.py`) — fails on any `rm` combining
   recursive and forced flags, system-path deletion, `sudo`, fork bombs,
   `dd of=/dev/*`, `mkfs`, `curl | sh`, shutdown/reboot, `--no-preserve-root`,
   force push, hard resets.

## Run

```bash
ai/tests/run.sh
# or
python3 -m unittest discover -s ai/tests -v
```

Python 3.8+ stdlib only; no dependencies.

## What these tests are (and are not)

They are static conformance, instruction-analysis, and loader-simulation
tests. They cannot run a live LLM, the VS Code extension, opencode, or pi.dev,
so they cannot prove runtime behavior — they prove each skill package is
valid and portable and that its instructions contain no out-of-scope or
destructive commands for an agent to follow.
