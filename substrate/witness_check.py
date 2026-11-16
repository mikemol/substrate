# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Spell a roster witness as a bib `check` string — or refuse, when the spelling would lose it.

⚑⚑ THE SECOND STEP OF THE ROSTER CLEANROOM (W40). A witness read by `witness_source` becomes data
by being written as a `check` field on its paired bib entry, in the `kind:argument` grammar
`finding_kindspec.parse` already reads. This module is the WRITE half of that grammar.

⚑⚑ A SPELLING THAT DOES NOT PARSE BACK TO THE SAME WITNESS IS REFUSED, NEVER EMITTED. The grammar
splits a command on commas when it has any, else on spaces — so an argument that itself holds a
space or a comma cannot always be represented, and emitting it anyway would change what the
witness runs while reading as a faithful copy. `emit` round-trips every spelling through its
parser and returns a refusal when the parsed witness differs from the row.

⚑⚑ THREE KINDS ARE SPELLED HERE, LOCALLY (operator, 2026-09-25: *"Extend the grammar"*).
`excludes`, `agda_lacks_field` and `agda_grep_count` run SUBSTRATE-ONLY tools (`pycodemod`,
`agda_defs`); mtools' ledger builds five kinds and takes these through our kind order. So their
spelling is this repo's, parsed by `parse_local`; every other kind is delegated to `kindspec`.
The free-text field comes LAST in each, so it may itself contain a `:`:

    excludes:MOD_PATH:FUNC:NEEDLE      agda-field:MODULE:RECORD:FIELD      agda-grep:COUNT:PATTERN
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mikemol.ledger import finding_kindspec

if TYPE_CHECKING:
    from substrate.witness_source import Row

# The kinds whose spelling is the bare kind name.
BARE = ("standing", "unwitnessed")

# The kinds whose first argument is an argv to run.
COMMAND = ("selftest", "refuses")

# The substrate-local kinds: spelling prefix -> (kind, how many ':'-fields precede the last).
LOCAL: dict[str, tuple[str, int]] = {
    "excludes": ("excludes", 2),
    "agda-field": ("agda_lacks_field", 2),
    "agda-grep": ("agda_grep_count", 1),
}

# The spelling prefix for each local kind.
_PREFIX = {kind: prefix for prefix, (kind, _) in LOCAL.items()}

# How many arguments (before the note) a three-field local kind carries.
_THREE_FIELDS = 3

# Characters a POSIX shell interprets. paperkit substitutes a check's target UNQUOTED into a
# shell command, so a spelling holding one of these would run as something else.
SHELL_META = frozenset("\"'`$\\|;&<>(){}*?[]~#!\n\t ")


def shell_unsafe(check: str) -> str:
    """Return the shell metacharacters in `check`'s target, sorted, or '' when it is inert."""
    _, _, target = check.partition(":")
    return "".join(sorted(set(target) & SHELL_META))


def parse_local(check: str) -> tuple[str, tuple[object, ...]] | None:
    """Return `(kind, args-without-note)` for a local-kind spelling, or None when it is not one."""
    prefix, sep, rest = check.partition(":")
    if not sep or prefix not in LOCAL:
        return None
    kind, fixed = LOCAL[prefix]
    fields = rest.split(":", fixed)
    if len(fields) != fixed + 1 or not all(fields):
        return None
    if kind == "agda_grep_count":
        if not fields[0].isdigit():
            return None
        return kind, (fields[1], int(fields[0]))
    return kind, tuple(fields)


def _spelling(row: Row) -> str:
    """Return the check string for `row`'s kind, or the empty string when it has no spelling."""
    if row.kind in BARE:
        return row.kind
    first = row.args[0] if row.args else None
    if row.kind in COMMAND and isinstance(first, list):
        return f"{row.kind}:" + ",".join(str(word) for word in first)
    if row.kind == "mode_undocumented" and len(row.args) > 1:
        return f"mode:{row.args[0]}:{row.args[1]}"
    if row.kind == "agda_grep_count" and len(row.args) > 1:
        return f"agda-grep:{row.args[1]}:{row.args[0]}"
    if row.kind in _PREFIX and len(row.args) >= _THREE_FIELDS:
        return f"{_PREFIX[row.kind]}:{row.args[0]}:{row.args[1]}:{row.args[2]}"
    return ""


def _matches(row: Row, spec: finding_kindspec.Spec) -> bool:
    """Report whether a parsed kindspec spec is exactly the witness `row` describes."""
    if spec.builder != f"_{row.kind}":
        return False
    if row.kind in COMMAND:
        first = row.args[0] if row.args else None
        return isinstance(first, list) and spec.cmd == tuple(str(word) for word in first)
    if row.kind == "mode_undocumented":
        return (spec.tool, spec.flag) == (str(row.args[0]), str(row.args[1]))
    return True


def _unspellable(row: Row, check: str) -> str:
    """Return why `row` has no emittable spelling: none at all, or one the quoting cannot carry."""
    if not check:
        return f"{row.key}: kind {row.kind} has no check spelling"
    return f"{row.key}: {check!r} holds a single quote, which the verb's quoting cannot carry"


def emit(row: Row) -> tuple[str, str]:
    """Return `(check, "")` for a spelling that parses back to `row`, else `("", refusal)`."""
    check = _spelling(row)
    if not check or "'" in check.partition(":")[2]:
        return "", _unspellable(row, check)
    if row.kind in _PREFIX:
        parsed = parse_local(check)
        if parsed is None or parsed != (row.kind, row.args[:-1]):
            return "", f"{row.key}: {check!r} parses to a DIFFERENT witness"
        return check, ""
    spec, refusal = finding_kindspec.parse(check)
    if spec is None:
        return "", f"{row.key}: {check!r} does not parse: {refusal}"
    if not _matches(row, spec):
        return "", f"{row.key}: {check!r} parses to a DIFFERENT witness"
    return check, ""
