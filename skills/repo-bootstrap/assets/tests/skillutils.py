"""Shared helpers for the ai-skills test suite. Python 3.8+ stdlib only."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"

SPEC_FRONTMATTER_KEYS = {"name", "description", "license", "compatibility", "metadata"}
SPEC_SUBDIRS = {"scripts", "references", "assets"}

LOADER_ROOTS = [
    ("kilo-code-vscode-extension (.kilo/skills, ~/.kilo/skills)", ".kilo/skills"),
    ("open-agent-standard (opencode, pi.dev, ...) (.agents/skills)", ".agents/skills"),
    ("claude-code-compat (.claude/skills)", ".claude/skills"),
    ("zcode (~/.zcode/skills)", ".zcode/skills"),
    ("opencode (.opencode/skill)", ".opencode/skill"),
    ("opencode alt layout (.opencode/skills)", ".opencode/skills"),
]


def iter_skills():
    return sorted((p.parent for p in REPO_ROOT.glob("skills/*/SKILL.md")), key=lambda d: d.name)


def read_skill(skill_dir):
    return (skill_dir / "SKILL.md").read_text(encoding="utf-8")


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, "missing opening '---' line"
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            fields = {}
            for line in lines[1:idx]:
                match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
                if match:
                    key, value = match.group(1), match.group(2).strip()
                    if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
                        value = value[1:-1]
                    fields[key] = value
            body = "\n".join(lines[idx + 1:])
            if "name" not in fields or "description" not in fields:
                return fields, body, "frontmatter is missing required 'name' or 'description'"
            return fields, body, None
    return {}, text, "missing closing '---' line"


def extract_code(text):
    """Return fenced blocks plus inline code spans as command-ish strings."""
    fenced = re.findall(r"```[^\n]*\n(.*?)```", text, re.DOTALL)
    without_fences = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    inline = re.findall(r"`([^`\n]+)`", without_fences)
    return fenced + inline
