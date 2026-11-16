# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which repos' LIVE harness hooks still call files under a target directory BY PATH.

⚑⚑ THE SECOND ADOPTION CHANNEL, AND THE ONE A SYMLINK CENSUS CANNOT SEE. A repo can run
substrate's `scripts/hook_*.py` by naming its path in a `.claude/settings*.json` hook command,
with no symlink anywhere; `symlink_adopters` would report it clean.

⚑⚑ AND A TEXT SEARCH OVER-COUNTS. `gcalculus`'s settings name `substrate/scripts/` only in a
`_comment` recording that it MOVED OFF them — a grep reads that history as a live dependency.
So this parses the JSON and reads only `hooks.<event>[].hooks[].command`: the strings the harness
actually executes.

    python -m substrate.settings_adopters <search-root> <path-fragment>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# The exit a refused invocation returns.
USAGE_EXIT = 2

USAGE = "usage: python -m substrate.settings_adopters <search-root> <path-fragment>"


def commands(doc: object) -> list[str]:
    """Return every hook command string a parsed settings document executes."""
    if not isinstance(doc, dict):
        return []
    hooks: object = doc.get("hooks")
    if not isinstance(hooks, dict):
        return []
    out: list[str] = []
    for groups in hooks.values():
        if not isinstance(groups, list):
            continue
        for group in groups:
            inner: object = group.get("hooks") if isinstance(group, dict) else None
            if not isinstance(inner, list):
                continue
            out.extend(
                cmd
                for h in inner
                if isinstance(h, dict) and isinstance(cmd := h.get("command"), str)
            )
    return out


def census(root: Path, fragment: str) -> tuple[list[tuple[Path, str]], list[str]]:
    """Return `(settings, command)` per live command naming `fragment`, and unparsable files."""
    found: list[tuple[Path, str]] = []
    unparsable: list[str] = []
    for path in sorted(root.glob("*/.claude/settings*.json")):
        try:
            doc: object = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            unparsable.append(f"{path}: {exc}")
            continue
        found.extend((path, cmd) for cmd in commands(doc) if fragment in cmd)
    return found, unparsable


def main(argv: list[str]) -> int:
    """Print every live hook command naming the fragment, with the denominator."""
    arity = 3
    if len(argv) != arity:
        sys.stderr.write(USAGE + "\n")
        return USAGE_EXIT
    root = Path(argv[1])
    found, unparsable = census(root, argv[2])
    for path, cmd in found:
        sys.stdout.write(f"{path.relative_to(root).parts[0]}: {cmd}\n")
    files = len(list(root.glob("*/.claude/settings*.json")))
    sys.stdout.write(f"{len(found)} live command(s) over {files} settings file(s)\n")
    for line in unparsable:
        sys.stdout.write(f"  UNPARSABLE {line}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
