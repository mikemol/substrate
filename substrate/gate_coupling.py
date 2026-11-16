# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read which gates are coupled to git, and how — the question no mode answered.

⚑⚑⚑ FILED AS UNWITNESSED BECAUSE NOTHING COULD ANSWER IT. A gate partition for the
make-to-bazel evaluation had to be derived BY EYE from the hook, because one census
reports phase, another reports kind and baseline health, and neither reads coupling. That
partition is load-bearing — bazel has no git, so a git-coupled gate cannot become a build
target — and a hand reading is exactly the judgement-in-the-turn shape this toolkit
refuses.

⚑⚑ THREE COUPLINGS, NOT ONE, and conflating them gets the migration answer wrong in both
directions. A gate may be TRIGGERED by staged paths while its body is a pure function of
the tree — portable, behind a non-portable dispatch, and a build system selects by
dependency rather than by a staged-path regex, so that dispatch inverts cleanly. A gate
may WRITE state a later hook reads, which no sandboxed action can do. Or a gate may read
git IN ITS BODY, which is the only genuinely unportable shape.

⚑ THE TRIGGER EXTRACTION IS THE HOOK'S OWN SPELLING, re-derived here rather than imported
because the census that already owns it carries hundreds of its own findings and cannot
take an edit. That is a fork, and it is declared: the pattern below accepts EITHER
quoting, which the census records as a measured defect — a double-quote-only pattern found
zero and would have rendered an empty trigger section as though there were no conditional
gates at all.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / ".githooks" / "pre-commit"

# How a gate can be coupled to git.
TRIGGERED = "triggered"
READS_GIT = "reads-git"

# ⚑ EITHER QUOTING. The hook writes `grep -qE '^jea/...'` with single quotes, and a
# double-quote-only pattern matches nothing while rendering as "no conditional gates".
_TRIGGER = re.compile(r"""grep\s+-qE\s+(['"])(\^[^'"]+)\1""", re.MULTILINE)

# A git invocation anywhere in a line.
_GIT = re.compile(r"\bgit\s+(?:diff|rev-parse|checkout-index|add|log|status|stash)\b")

# The script a hook line invokes, as the hook spells it.
_SCRIPT = re.compile(r"\$ROOT/([\w/.\-]+\.(?:py|sh))")


@dataclass(frozen=True, slots=True)
class Coupling:
    """One hook line's git coupling, and the script it invokes."""

    line: int
    kind: str
    script: str | None
    text: str


def hook_lines(hook: Path | None = None) -> list[str]:
    """Return the hook's raw lines.

    ⚑ RAW, NOT CONTINUATION-JOINED. Joining rewrites the whitespace inside a `grep -qE`
    argument and the pattern stops matching — a defect the gate census records having hit
    when a join was introduced for a different reader.
    """
    path = HOOK if hook is None else hook
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def couplings(hook: Path | None = None) -> list[Coupling]:
    """Return every hook line that touches git, classified by how.

    ⚑ A LINE INVOKING A SCRIPT IS ATTRIBUTED TO IT; one that does not is still reported
    with a null script, because the hook's own git work — the staged-tree export, the
    report tee — is exactly the residue that cannot become a build target and would be
    invisible in a gate-keyed reading.
    """
    out: list[Coupling] = []
    for i, text in enumerate(hook_lines(hook), start=1):
        stripped = text.strip()
        if stripped.startswith("#") or not _GIT.search(stripped):
            continue
        found = _SCRIPT.search(stripped)
        kind = TRIGGERED if _TRIGGER.search(stripped) else READS_GIT
        out.append(Coupling(i, kind, found.group(1) if found else None, stripped))
    return out


def triggers(hook: Path | None = None) -> list[str]:
    """Return the staged-path regexes the hook's conditional gates key on."""
    text = "\n".join(hook_lines(hook))
    found: set[str] = set()
    for match in _TRIGGER.finditer(text):
        found.add(match.group(2))
    return sorted(found)


def render(hook: Path | None = None) -> str:
    """Render the coupling census, one line per git-touching hook line."""
    rows = couplings(hook)
    pats = triggers(hook)
    by_kind: dict[str, int] = {}
    for row in rows:
        by_kind[row.kind] = by_kind.get(row.kind, 0) + 1
    out = [f"{len(rows)} git-coupled hook line(s), {len(pats)} staged-path trigger(s)"]
    for kind, count in sorted(by_kind.items()):
        out.append(f"  {kind:<14} {count:>3}")
    for row in rows:
        where = row.script or "(the hook itself)"
        out.append(f"  {row.line:>4}  {row.kind:<14} {where}")
    out.append(
        "   ⚑ A TRIGGERED GATE IS PORTABLE BEHIND A NON-PORTABLE DISPATCH: its body "
        "may be a pure function of the tree, and a build system selects by "
        "dependency rather than by a staged-path regex."
    )
    out.append(
        "   ⚑ THIS READS THE HOOK, NOT THE GATES. A gate whose own body shells out "
        "to git is invisible here — a fact about this reader, not an absence."
    )
    return "\n".join(out)
