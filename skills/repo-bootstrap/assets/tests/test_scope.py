"""Requirement 2: a skill never changes anything outside the target repo
unless the user explicitly grants permission.

Statically enforced on every skill's instructions:
- no command in a code span targets paths outside the repo (home, absolute
  system directories, parent-directory escapes)
- no command mutates remote or global state (git push, global config, system
  packages, OS-level settings, remote execution, containers/clusters)
- the instructions carry an explicit permission gate for committing/pushing
"""

import re
import unittest

from skillutils import extract_code, iter_skills, read_skill

OUTSIDE_TARGET_REPOSITORY = [
    ("home-relative path", r"(?<![\w.~-])~/"),
    ("$HOME reference", r"\$\{?HOME\}?"),
    ("absolute system path", r"(?<![\w.])/(?:Users|home|etc|var|opt|usr|tmp|Library|Applications|private|System)/"),
    ("parent-directory escape", r"\.\./"),
    ("git push (remote mutation)", r"\bgit\s+push\b"),
    ("global/system git config mutation", r"\bgit\s+config\s+--(?:global|system)\b"),
    ("branch/tag creation", r"\bgit\s+(?:branch|tag)\s+(?!-)"),
    ("output redirect to absolute path", r"(?:^|\s)>\s*/[A-Za-z]"),
    ("tee to absolute path", r"\btee\s+/[A-Za-z]"),
    ("global package install", r"\b(?:npm|pnpm|yarn)\s+(?:i|install|add)\s+(?:-g\b|--global\b)"),
    ("user site-packages install", r"\bpip\d?\s+install\s+--user\b"),
    ("system package mutation", r"\b(?:brew|apt|apt-get|dnf|yum|pacman)\s+(?:install|remove|uninstall|purge)\b"),
    ("OS-level mutation", r"\b(?:defaults\s+write|launchctl|crontab|systemctl)\b"),
    ("remote execution/copy", r"\b(?:ssh|scp)\s"),
    ("remote rsync target", r"\brsync\s[^;\n]*:"),
    ("container/cluster mutation", r"\b(?:docker\s+(?:run|exec|system)|kubectl\s+(?:apply|delete|edit|scale))\b"),
]

PERMISSION_GUARD = re.compile(
    r"unless\s+(?:explicitly\s+)?(?:asked|requested|instructed|told)"
    r"|(?:do\s+not|don't|never)\s+commit"
    r"|leave\s+(?:all\s+)?(?:changes\s+)?uncommitted"
    r"|without\s+(?:explicit\s+)?(?:permission|approval)",
    re.IGNORECASE,
)

GIT_STATE_MUTATION = re.compile(
    r"\bgit\s+(?:commit|push|merge|rebase|reset|checkout|switch|restore|stash)\b"
    r"|\bgit\s+(?:branch|tag)\s+(?!-)",
    re.IGNORECASE,
)


class TestScope(unittest.TestCase):
    def test_no_commands_target_outside_the_target_repo(self):
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                for chunk in extract_code(read_skill(skill)):
                    for label, pattern in OUTSIDE_TARGET_REPOSITORY:
                        match = re.search(pattern, chunk)
                        if match:
                            self.fail(
                                f"{skill.name}: command `{chunk}` contains {label} "
                                f"({match.group(0)!r}); skills must only touch the target repo"
                            )

    def test_instructions_carry_permission_gate(self):
        for skill in iter_skills():
            text = read_skill(skill)
            with self.subTest(skill=skill.name):
                self.assertRegex(
                    text,
                    PERMISSION_GUARD,
                    "instructions must state changes stay uncommitted / need explicit permission",
                )

    def test_git_state_mutations_are_gated(self):
        for skill in iter_skills():
            text = read_skill(skill)
            with self.subTest(skill=skill.name):
                if GIT_STATE_MUTATION.search(text):
                    self.assertRegex(
                        text,
                        PERMISSION_GUARD,
                        f"{skill.name} mutates git state but has no permission gate",
                    )


if __name__ == "__main__":
    unittest.main()
