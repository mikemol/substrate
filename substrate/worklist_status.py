# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Evaluate a worklist item's done-predicate against the tree — DONE / OPEN / MANUAL.

⚑⚑⚑ THE STATUS IS NEVER STORED, WHICH IS THE WHOLE DESIGN OF THE TRACKER THIS SERVES. The
open-threads worklist kept going stale because status was a hand-edited value, and a regrounding
then re-dispatched completed work — five items turned up done-but-listed-open in one session. So
status is DERIVED from the tree on every run and cannot go stale by construction.

⚑⚑ AND THE THIRD OUTCOME IS LOAD-BEARING RATHER THAN A HEDGE. `None` means MANUAL: a
human-judged item with no machine artifact yet. Collapsing it into OPEN would put audits nobody
can mechanically discharge into the dispatch queue forever; collapsing it into DONE would retire
them silently. A manual item becomes mechanical the moment it is given an artifact predicate.

⚑ WHAT THIS DELIBERATELY DOES NOT ANSWER: whether the predicate's referent still EXISTS.
`defines` and `grep` return False when the file is gone, so *absent* and *present but lacking the
name* are one answer here — by design, because both mean the item is not discharged. The separate
question, whether the predicate can ever be satisfied as written, belongs to
`substrate.worklist_predicate`, and keeping them apart is what lets a gate refuse a STALE
predicate without refusing an ordinary open one (gate-F93, gate-F96).

⚑⚑ THE FOLD IS ITS OWN FUNCTION, AND THE PER-FILE GATE NAMED THAT SEAM TWICE THIS SESSION. A
first cut dispatched on the head AND folded combinators inline, refused at `PLR0911`. Those are
two questions — the second never looks at a predicate, only at verdicts — and the identical
refusal produced the identical split in `worklist_predicate`, which is evidence the seam is real
rather than a limit satisfied twice.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

#: How a combinator folds its members. `all` is DONE only if every member is; `any` is DONE if
#: one is. Both propagate MANUAL, because a fold over an unjudged member is itself unjudged.
COMBINATORS = ("all", "any")

#: Predicate heads carrying `(head, path, name)` — the arity a bounds check reads, named so the
#: rule is legible rather than a bare digit.
ARITY_3 = 2


def git_has_commit(root: Path, subject: str) -> bool:
    """Report whether any commit message contains `subject`, fixed-string.

    ⚑ `-F` IS NOT OPTIONAL: these subjects carry regex metacharacters — `⊢-△`, `Ⓖ★→jea` — and a
    pattern match would either error or silently match something else.

    ⚑ AND THE EXECUTABLE IS RESOLVED, NOT ASSUMED. A partial path takes whatever `PATH` offers,
    which is the undeclared-input class this tree has already paid for once at the agda shim.
    """
    git = shutil.which("git")
    if git is None:
        return False
    found = subprocess.run(  # noqa: S603 — a fixed argv, no shell, operands are roster data
        [git, "-C", str(root), "log", "--oneline", "-F", "--grep", subject],
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(found.stdout.strip())


def defines(agda: Path, relpath: str, name: str) -> bool:
    """Report whether the Agda module at `relpath` defines `name` at column 0.

    ⚑ A DEFINITION IS A LINE WHOSE FIRST TOKEN IS THE NAME, followed by a space or a colon — so
    a mention inside a comment or another declaration's body does not count. That is why the
    check is on the stripped line's prefix and the character after it, not a substring search.
    """
    path = Path(relpath) if Path(relpath).is_absolute() else agda / relpath
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return any(
        line.lstrip().startswith(name)
        and len(line.lstrip()) > len(name)
        and line.lstrip()[len(name)] in " :"
        for line in text.splitlines()
    )


def grep(root: Path, pattern: str, relpath: str) -> bool:
    """Report whether `relpath` contains `pattern` as a substring."""
    path = Path(relpath) if Path(relpath).is_absolute() else root / relpath
    try:
        return pattern in path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def cmd0(root: Path, command: str) -> bool:
    """Report whether `command` exits 0, run through a shell under `root`.

    ⚑ A SHELL IS USED BECAUSE THE PREDICATES ARE AUTHORED AS SHELL — one carries a command
    substitution and a numeric test. The commands are roster data, not caller input.
    """
    return (
        subprocess.run(
            command,
            shell=True,
            cwd=root,  # noqa: S602 — roster data, not input
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def _atom(pred: tuple[object, ...], *, root: Path, agda: Path) -> bool | None:
    """Return the verdict for a NON-combinator predicate, or None if its head is unrecognised.

    ⚑⚑ AN UNRECOGNISED HEAD RETURNS None RATHER THAN False, so a typo reads as *unjudged* rather
    than as *not done*. Reporting it OPEN would put a nonexistent check into the dispatch queue
    with no way to discharge it — and `manual` reaches this same branch by design, since it is
    exactly the head that names no artifact.
    """
    head = pred[0]
    if head == "commit" and len(pred) > 1:
        return git_has_commit(root, str(pred[1]))
    if head == "defines" and len(pred) > ARITY_3:
        return defines(agda, str(pred[1]), str(pred[2]))
    if head == "exists" and len(pred) > 1:
        target = Path(str(pred[1]))
        return (target if target.is_absolute() else root / target).exists()
    if head == "grep" and len(pred) > ARITY_3:
        return grep(root, str(pred[1]), str(pred[2]))
    if head == "cmd0" and len(pred) > 1:
        return cmd0(root, str(pred[1]))
    return None


def _fold(head: object, found: list[bool | None]) -> bool | None:
    """Fold member verdicts for `all`/`any`.

    ⚑ MANUAL PROPAGATES THROUGH BOTH, and that is the load-bearing rule: an `all` with an
    unjudged member is not DONE, and an `any` with no True and an unjudged member is not OPEN.
    Either collapse would report a judgement nobody made.
    """
    if head == "all":
        if any(r is False for r in found):
            return False
        return None if any(r is None for r in found) else True
    if any(r is True for r in found):
        return True
    return None if any(r is None for r in found) else False


def status(pred: tuple[object, ...], *, root: Path, agda: Path) -> bool | None:
    """Return True = DONE, False = OPEN, None = MANUAL for one predicate."""
    if not pred:
        return None
    head = pred[0]
    if head in COMBINATORS:
        members = pred[1] if len(pred) > 1 else ()
        if not isinstance(members, (list, tuple)):
            return None
        return _fold(head, [status(tuple(m), root=root, agda=agda) for m in members])
    return _atom(pred, root=root, agda=agda)


def label(verdict: bool | None) -> str:  # noqa: FBT001 — the tri-state IS the parameter
    """Return the display label for a verdict — the one place the three names are spelled."""
    return {True: "DONE", False: "OPEN", None: "MANUAL"}[verdict]
