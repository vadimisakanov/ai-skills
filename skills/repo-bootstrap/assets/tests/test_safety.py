"""Requirement 3: a skill never instructs anything real harmful such as
recursive forced deletion of system paths, privilege escalation, device wipes,
fork bombs, or piping remote content into a shell.

Catastrophic patterns are scanned against the FULL SKILL.md text (prose and
code): an agent may follow prose instructions just like commands, so there is
no legitimate place for these patterns in a skill body.
"""

import re
import unittest

from skillutils import extract_code, iter_skills, read_skill

CATASTROPHIC_PATTERNS = [
    ("recursive+forced rm flag combo (-rf/-fr)", r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\b|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*\b"),
    ("rm --recursive --force", r"\brm\s+(?:--recursive\s+--force|--force\s+--recursive)\b"),
    ("fork bomb", r":\(\)\s*\{[^}]*\}\s*;\s*:"),
    ("filesystem format (mkfs)", r"\bmkfs(?:\.\w+)?\b"),
    ("raw device write (dd of=/dev/...)", r"\bdd\b[^;\n|]*\bof=/dev/"),
    ("redirect to device node", r">\s*/dev/(?:sd|nvme|disk|hd)"),
    ("pipe remote content into shell", r"\b(?:curl|wget)\b[^|\n]*\|\s*(?:ba|z|fi)?sh\b"),
    ("eval of fetched content", r"eval\s[^;\n]*\$\("),
    ("world-writable chmod on system paths", r"chmod\s+[^;\n]*-R[^;\n]*777\s+/"),
    ("recursive chown on system paths", r"chown\s+[^;\n]*-R[^;\n]*\s+/(?:etc|usr|var|home|Users|Library|Applications)\b"),
    ("no-preserve-root", r"--no-preserve-root"),
    ("system power control", r"\b(?:shutdown|reboot|halt|poweroff)\b"),
    ("privileged deletion (sudo rm)", r"\bsudo\s+rm\b"),
    ("force push", r"\bgit\s+push\b[^;\n]*(?:--force\b|-f\b|--force-push\b)"),
    ("hard reset of working tree", r"\bgit\s+reset\s+--hard\b"),
    ("forced clean of untracked files", r"\bgit\s+clean\s+[^;\n]*-[a-zA-Z]*f"),
]

PRIVILEGE_ESCALATION = re.compile(r"\b(?:sudo|pkexec)\b|\bsu\s+-\b")

SYSTEM_RM_TARGETS = {"/", "/*", "~", "~/", "~/*", "*", "$HOME", ".", "..", "./", "../"}
SYSTEM_RM_PREFIXES = (
    "/etc", "/usr", "/var", "/bin", "/sbin", "/lib", "/lib64", "/boot", "/dev",
    "/proc", "/sys", "/home", "/Users", "/Library", "/Applications", "/System",
    "/private", "/Volumes",
)


def rm_invocations(text):
    """Token-level scan for rm commands; catches separated flags (-r -f)."""
    found = []
    for raw_line in text.splitlines():
        tokens = raw_line.split()
        if "rm" not in tokens:
            continue
        start = tokens.index("rm")
        flag_chars = ""
        recursive = force = bypass = False
        target = None
        for token in tokens[start + 1:]:
            if token.startswith("--"):
                if token == "--recursive":
                    recursive = True
                elif token == "--force":
                    force = True
                elif token == "--no-preserve-root":
                    bypass = True
                continue
            if token.startswith("-") and len(token) > 1:
                flag_chars += token[1:]
                continue
            if target is None:
                target = token.strip("\"'`")
        recursive = recursive or "r" in flag_chars
        force = force or "f" in flag_chars
        if recursive or force or bypass or target:
            found.append({
                "line": raw_line.strip(),
                "target": target,
                "recursive": recursive,
                "force": force,
                "bypass": bypass,
            })
    return found


class TestSafety(unittest.TestCase):
    def test_no_recursive_forced_rm(self):
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                for invocation in rm_invocations(read_skill(skill)):
                    self.assertFalse(
                        invocation["recursive"] and invocation["force"],
                        f"{skill.name}: destructive rm in `{invocation['line']}`; skill instructions must never combine recursive and forced deletion",
                    )

    def test_rm_never_targets_system_paths(self):
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                for invocation in rm_invocations(read_skill(skill)):
                    target = invocation["target"] or ""
                    self.assertFalse(
                        invocation["bypass"]
                        or target in SYSTEM_RM_TARGETS
                        or target.startswith(SYSTEM_RM_PREFIXES),
                        f"{skill.name}: rm targets a system path in `{invocation['line']}`",
                    )

    def test_no_privilege_escalation_in_commands(self):
        for skill in iter_skills():
            with self.subTest(skill=skill.name):
                for chunk in extract_code(read_skill(skill)):
                    match = PRIVILEGE_ESCALATION.search(chunk)
                    if match:
                        self.fail(f"{skill.name}: privilege escalation {match.group(0)!r} in `{chunk}`")

    def test_no_catastrophic_patterns_anywhere(self):
        for skill in iter_skills():
            text = read_skill(skill)
            with self.subTest(skill=skill.name):
                for label, pattern in CATASTROPHIC_PATTERNS:
                    match = re.search(pattern, text)
                    if match:
                        self.fail(f"{skill.name}: {label} matched {match.group(0)!r}")


if __name__ == "__main__":
    unittest.main()
