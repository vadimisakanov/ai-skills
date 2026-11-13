"""Requirement 1: skills work with the Kilo Code VS Code extension and any
Agent-Skills-spec consumer (opencode, pi.dev, ...).

Static conformance plus loader simulation against every documented skills root:
`.kilo/skills/` (project and `~/.kilo/skills/` global share the same shape),
`.agents/skills/` (open agent standard), `.claude/skills/` (Claude Code
compatibility), `.zcode/skills/`, `.opencode/skill/` and `.opencode/skills/`.
These tests cannot drive a live extension or agent; they prove the skill
package is valid, portable, and discoverable under each tool's documented
discovery and validation rules.
"""

import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from skillutils import (
    LOADER_ROOTS,
    REPO_ROOT,
    SPEC_FRONTMATTER_KEYS,
    SPEC_SUBDIRS,
    extract_code,
    iter_skills,
    read_skill,
    split_frontmatter,
)

NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")
DESCRIPTION_LIMIT = 1024
BODY_LIMIT = 100 * 1024


class TestRepoLayout(unittest.TestCase):
    def test_repo_has_at_least_one_skill(self):
        self.assertTrue(iter_skills(), "no skills/*/SKILL.md found in this repo")

    def test_repo_root_has_only_expected_directories(self):
        dirs = {p.name for p in REPO_ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")}
        unexpected = sorted(dirs - {"ai", "skills"})
        self.assertEqual(unexpected, [], "repo root holds only 'ai/' (docs/tests) and 'skills/' (skills)")

    def test_every_skills_dir_entry_is_a_skill(self):
        skills = REPO_ROOT / "skills"
        offenders = sorted(p.name for p in skills.iterdir() if not (p / "SKILL.md").is_file())
        self.assertEqual(offenders, [], "every entry in skills/ must be a skill directory with a SKILL.md")

    def test_no_skills_outside_skills_dir(self):
        stray = [str(p) for p in REPO_ROOT.glob("*/SKILL.md")]
        self.assertEqual(stray, [], "all skills must live under skills/<name>/SKILL.md, not at the repo root")

    def test_layout_is_flat_no_nested_skills(self):
        nested = [str(p) for p in REPO_ROOT.glob("skills/*/*/SKILL.md")]
        self.assertEqual(nested, [], "ZCode and other loaders ignore skills nested in grouping directories")

    def test_ai_dir_contains_no_skills(self):
        stray = [str(p) for p in REPO_ROOT.glob("ai/**/SKILL.md")]
        self.assertEqual(stray, [], "'ai/' holds docs and tests, never skills")


class TestFrontmatterSpec(unittest.TestCase):
    def test_frontmatter_rules(self):
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                text = read_skill(skill)
                fields, body, err = split_frontmatter(text)
                self.assertIsNone(err, f"{skill.name}: {err}")
                name = fields.get("name", "")
                self.assertTrue(NAME_RE.match(name), f"invalid name '{name}': lowercase letters/numbers/hyphens only, no leading/trailing hyphen")
                self.assertLessEqual(len(name), 64, "name exceeds 64 chars")
                self.assertEqual(name, skill.name, "frontmatter name must match the directory name (hard error in Kilo; ZCode references the directory name)")
                description = fields.get("description", "")
                self.assertGreaterEqual(len(description), 40, "description must state what the skill does")
                self.assertLessEqual(len(description), DESCRIPTION_LIMIT, "description over 1024 chars makes ZCode drop the whole skill")
                self.assertRegex(description, r"when", "description must say WHEN to use the skill; auto-triggering depends on it")
                unknown = set(fields) - SPEC_FRONTMATTER_KEYS
                self.assertFalse(unknown, f"non-spec frontmatter keys: {sorted(unknown)}")
                self.assertLessEqual(len(body.encode("utf-8")), BODY_LIMIT, "ZCode truncates bodies over 100KB")
                subdirs = {p.name for p in skill.iterdir() if p.is_dir()}
                extra = subdirs - SPEC_SUBDIRS
                self.assertFalse(extra, f"unexpected subdirectories {sorted(extra)}; spec allows scripts/, references/, assets/")


class TestPortability(unittest.TestCase):
    def test_no_embedded_shell_placeholders(self):
        pattern = re.compile(r"!`[^`\n]+`")
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                self.assertIsNone(pattern.search(read_skill(skill)), "embedded shell-command placeholders only execute in Kilo trusted locations; treat as nonportable")

    def test_no_machine_specific_paths_in_commands(self):
        pattern = re.compile(r"(?<![\w.])/(?:Users|home|etc|var|opt|usr|tmp|Library|Applications|private|System)/|(?<![\w.~-])~/|\$\{?HOME\}?")
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                for chunk in extract_code(read_skill(skill)):
                    match = pattern.search(chunk)
                    if match:
                        self.fail(f"{skill.name}: machine-specific path {match.group(0)!r} in command `{chunk}`")

    def test_markdown_fences_balanced(self):
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                self.assertEqual(read_skill(skill).count("```") % 2, 0, "unbalanced code fences")

    def test_no_trailing_whitespace(self):
        pattern = re.compile(r"[ \t]+$", re.MULTILINE)
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                self.assertIsNone(pattern.search(read_skill(skill)), "trailing whitespace; AGENTS.md requires clean markdown")


class TestLoaderSimulation(unittest.TestCase):
    def test_skill_discovers_from_each_tool_root(self):
        for skill in iter_skills():
            for tool, rel_root in LOADER_ROOTS:
                with self.subTest(skill=skill.name, tool=tool):
                    with tempfile.TemporaryDirectory() as tmp:
                        root = Path(tmp) / rel_root
                        root.mkdir(parents=True)
                        installed = root / skill.name
                        try:
                            os.symlink(skill.resolve(), installed)
                        except OSError:
                            shutil.copytree(skill, installed)
                        discovered = {p.parent.name for p in root.glob("*/SKILL.md")}
                        self.assertIn(skill.name, discovered, f"{skill.name} not discoverable under {rel_root}")
                        fields, _, err = split_frontmatter(read_skill(installed))
                        self.assertIsNone(err, err)
                        self.assertEqual(fields.get("name"), skill.name)
                        self.assertTrue(fields.get("description"))


if __name__ == "__main__":
    unittest.main()
