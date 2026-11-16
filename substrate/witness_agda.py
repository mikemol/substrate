# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The `agda-field:` and `agda-grep:` witnesses — Agda structural claims, read from the index (W40).

⚑⚑ CLEANROOMED FROM `.claude/agents/findings.py:_agda_lacks_field` and `_agda_grep_count`. Both
read `scratch/agda_defs.py` — the Agda corpus's authority — never a compile: the tree need not
build for a structural claim about its source to be checkable.

- `agda-field:MODULE:RECORD:FIELD` — CLOSED while `--provides MODULE` does not list FIELD. It
  flips the moment the field is added, which is exactly when the finding stops being true.
- `agda-grep:COUNT:PATTERN` — CLOSED while `--grep PATTERN` still answers COUNT. ⚑ This kind PINS
  A NUMBER ON PURPOSE: the count is the INSTRUMENT'S OWN (wrong) answer, so a moved count is the
  REPAIR ARRIVING, and the OPEN message says so.

⚑ A MISS IS UNWITNESSED, NEVER HOLDING. A tool that does not run, exits non-zero, prints nothing,
or changes its output shape is a fact about this reader.

⚑ ONE DELIBERATE DIVERGENCE: the RECORD is looked up as a whole TOKEN of `--provides` output, as
the field already was. The origin substring-tested it, so a record named `R` was "provided" by
any output containing an `R` anywhere — a missing record read as present, and the field claim
was then judged against a module that does not hold it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.ledger import finding_kinds

if TYPE_CHECKING:
    from mikemol.ledger.finding_kinds import Runner

# The Agda index, relative to the tree.
AGDA_DEFS = ("python3", "scratch/agda_defs.py")

# The footer `--grep` counts its matches in: `<label>: <n> name(s) matching …`.
_FOOTER = "name(s) matching"


def grep_count(out: str) -> int | None:
    """Return the count in `--grep` output's LAST footer line, or None when absent or unparsable."""
    footers = [line for line in out.splitlines() if _FOOTER in line]
    if not footers:
        return None
    head = footers[-1].split(":", 1)[-1].split()
    return int(head[0]) if head and head[0].isdigit() else None


def lacks_field(module: str, record: str, field: str, run: Runner) -> finding_kinds.Verdict:
    """Return the `agda-field:` verdict: CLOSED while `record` does not declare `field`."""
    rc, out = run([*AGDA_DEFS, "--provides", module])
    if rc != 0 or not out.strip():
        return finding_kinds.UNRUNNABLE, (
            f"UNWITNESSED — {module} provided no names (exit {rc}); the finding may still hold "
            "but this reader cannot say so"
        )
    names = out.split()
    if record not in names:
        return finding_kinds.UNRUNNABLE, (
            f"UNWITNESSED — {module} does not provide {record} (renamed or re-homed?); this "
            "reader cannot speak to the field claim"
        )
    if field in names:
        return finding_kinds.OPEN, f"{module}.{record} NOW DECLARES {field!r} — the absence is GONE"
    return finding_kinds.CLOSED, f"{module}.{record} does not declare {field!r}"


def grep_holds(pattern: str, expected: int, run: Runner) -> finding_kinds.Verdict:
    """Return the `agda-grep:` verdict: CLOSED while `--grep pattern` still answers `expected`."""
    rc, out = run([*AGDA_DEFS, "--grep", pattern])
    if rc != 0:
        return finding_kinds.UNRUNNABLE, (
            f"UNWITNESSED — `--grep {pattern!r}` exited {rc}; the finding may still hold but "
            "this reader cannot say so"
        )
    got = grep_count(out)
    if got is None:
        return finding_kinds.UNRUNNABLE, (
            f"UNWITNESSED — `--grep {pattern!r}` printed no countable `{_FOOTER}` footer; the "
            "output shape changed and this reader cannot count it"
        )
    if got != expected:
        return finding_kinds.OPEN, (
            f"`--grep {pattern!r}` now returns {got}, not {expected} — ⚑ THE CENSUS MOVED, "
            "which is the REPAIR ARRIVING rather than a broken witness"
        )
    return finding_kinds.CLOSED, f"`--grep {pattern!r}` still returns {got}"
