# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Decide whether a worklist item's predicate still RESOLVES — distinct from whether it holds.

⚑⚑⚑ THE DISTINCTION THIS MODULE EXISTS FOR, AND `scripts/worklist.py` CANNOT EXPRESS IT.
That tool's `status()` collapses every failure onto `False` = OPEN. `_defines` returns False on
`OSError`, so *the file is gone* and *the file is present and lacks the name* are the same answer;
`_grep` does the same; `exists` on a deleted path is False. So a STALE predicate — one pointing at
an artifact that no longer exists — is indistinguishable from an item that is simply still open.

⚑⚑ AND THAT IS THE CLASS THE OPERATOR RULED SHOULD REFUSE. `gate-F93` measured that
`worklist.py --check` computes its offender list into a dead binding and exits 0 regardless. The
ruling was to refuse on a NARROWER class than "open": an item whose predicate no longer resolves.
Refusing on merely-open would be wrong, and the tool's own comment says so — an OPEN item with a
live artifact predicate is legitimately not-done, which is the ordinary state of a work list.

⚑⚑⚑ SO RESOLUTION IS A THIRD OUTCOME, NOT A SECOND VERDICT. This module answers RESOLVES /
STALE / UNDECIDABLE, and the third value is load-bearing rather than a hedge:

  * `commit` asks git whether any log message contains a string. A miss is an honest FALSE — the
    commit has not happened yet — so nothing about it can go stale. It always RESOLVES.
  * `cmd0` runs an arbitrary shell command. Whether its non-zero exit means *not yet* or *the
    thing it invokes is gone* is not decidable from the exit code, and guessing would manufacture
    exactly the false refusals this gate must not produce. UNDECIDABLE, and it blocks.
  * `manual` has no machine artifact by construction. UNDECIDABLE — and reporting it as stale
    would refuse a commit over a human judgement nobody encoded.

⚑ THE PATH PREDICATES ARE THE DECIDABLE ONES, and they are the whole point: `defines`, `grep` and
`exists` all name a file, so *does that file exist* is a question with an answer, asked separately
from *does the file say what the item claims*. That separation is the entire repair.

⚑ THE ROOTS ARE PASSED IN, NOT IMPORTED. `worklist.py` resolves `defines` against the Agda tree
and `grep`/`exists` against the repo root — two different bases for what looks like one kind of
operand. Taking both as arguments keeps this a pure function of its inputs, so a case can drive it
without a tree, and stops this module becoming a second authority on where the trees are.

⚑⚑ AND THE PER-FILE GATE NAMED THE SEAM RATHER THAN A SIZE. A first cut folded combinators inside
the dispatch and was refused at `C901` (11 > 10) and `PLR0911` (11 > 6). Those are one defect:
`verdict_for` was answering *which kind of predicate is this* AND *how do sub-verdicts combine*.
They are separate questions — the second does not look at a predicate at all, only at verdicts —
so the fold is its own function, and reading the refusal as a limit to satisfy rather than a
design signal would have produced a flatter function still carrying both.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import NamedTuple

#: Predicate heads whose operand at index 1 is a path resolved against the REPO root.
REPO_PATH_AT_1 = ("exists",)

#: `grep` puts its NEEDLE first — `("grep", pat, relpath)` — so its path is at index 2.
REPO_PATH_AT_2 = ("grep",)

#: ⚑⚑⚑ `defines` PUTS ITS PATH AT INDEX 1, NOT 2, AND I HAD IT AT 2. `worklist.py`'s docstring is
#: the authority and spells it `("defines", relpath, name)` — the path LEADS and the name trails,
#: the opposite of `grep`. A case caught it (the suite read 31/32) and nothing else could have:
#: `pycodemod --literal '"defines"'` finds the head in that docstring and in NO live item, so a
#: differential against the live roster would have agreed with a wrong reader indefinitely.
#: ⚑⚑ AND THE COMMENT WARNING ABOUT THIS EXACT TRAP was written one line above committing it —
#: two index conventions in one vocabulary, read as one. The warning was right; I applied it to
#: the wrong member, which is why the fixture had to exercise each head separately.
AGDA_PATH_AT_1 = ("defines",)

#: Heads that combine sub-predicates rather than naming an artifact.
COMBINATORS = ("all", "any")

#: Heads that name no inspectable artifact — see the module docstring for why each is UNDECIDABLE
#: rather than resolving vacuously.
OPAQUE = ("cmd0", "manual")

#: A head that cannot go stale: a commit either exists or has not happened yet.
ALWAYS_RESOLVES = ("commit",)

#: The tuple arity at which a path sits in the third slot — named so a case reads the rule rather
#: than a digit, and so the two path positions cannot be confused for one convention.
PATH_AT_2_ARITY = 2


class Verdict(Enum):
    """What can be said about a predicate's REFERENT, never about whether the predicate holds."""

    RESOLVES = "resolves"
    STALE = "stale"
    UNDECIDABLE = "undecidable"


class Finding(NamedTuple):
    """One predicate's verdict, carrying the path so a refusal can name what went missing."""

    verdict: Verdict
    detail: str


def _path_verdict(base: Path, operand: str) -> Finding:
    """Return whether `operand`, resolved against `base`, still names something on disk.

    ⚑ AN ABSOLUTE OPERAND IS HONOURED AS WRITTEN, matching `worklist.py`'s own resolution — it
    tests `os.path.isabs` before joining. A module that always joined would report every absolute
    path as missing, which is a refusal manufactured by the reader.
    """
    path = Path(operand) if Path(operand).is_absolute() else base / operand
    if path.exists():
        return Finding(Verdict.RESOLVES, str(operand))
    return Finding(Verdict.STALE, f"{operand} — no such path under {base}")


def combine(head: object, found: list[Finding]) -> Finding:
    """Fold sub-verdicts into one, for an `all`/`any` predicate.

    ⚑⚑ A COMBINATOR IS AS STALE AS ITS WORST MEMBER, AND UNDECIDABLE BEATS RESOLVES. An `all`
    whose members are one live path and one missing one is STALE — the item cannot be discharged
    as written. And a combinator carrying an opaque member cannot be called clean, because the
    opaque member is precisely the part nothing checked.

    ⚑ THIS LOOKS AT VERDICTS, NEVER AT PREDICATES, which is why it is a separate function: the
    ordering rule here is about the lattice, and it holds whatever the predicates were.
    """
    if not found:
        return Finding(Verdict.UNDECIDABLE, f"{head!r} carries no sub-predicate")
    stale = [f for f in found if f.verdict is Verdict.STALE]
    if stale:
        return Finding(Verdict.STALE, "; ".join(f.detail for f in stale))
    unknown = [f for f in found if f.verdict is Verdict.UNDECIDABLE]
    if unknown:
        return Finding(Verdict.UNDECIDABLE, "; ".join(f.detail for f in unknown))
    return Finding(Verdict.RESOLVES, f"{head} over {len(found)} member(s)")


def _artifact_verdict(pred: tuple[object, ...], *, repo: Path, agda: Path) -> Finding:
    """Return the verdict for a NON-combinator predicate — one that names an artifact, or none.

    ⚑ AN UNRECOGNISED HEAD IS UNDECIDABLE, NEVER RESOLVES. `worklist.py`'s `status` returns None
    for an unknown head, so a typo'd predicate reads as MANUAL and is silently excused. Answering
    RESOLVES here would extend that excuse into the gate that exists to catch it.
    """
    head = pred[0]
    if head in ALWAYS_RESOLVES:
        return Finding(Verdict.RESOLVES, "a commit either exists or has not happened yet")
    if head in OPAQUE:
        return Finding(Verdict.UNDECIDABLE, f"{head!r} names no inspectable artifact")
    if head in REPO_PATH_AT_1 and len(pred) > 1:
        return _path_verdict(repo, str(pred[1]))
    if head in AGDA_PATH_AT_1 and len(pred) > 1:
        return _path_verdict(agda, str(pred[1]))
    if head in REPO_PATH_AT_2 and len(pred) > PATH_AT_2_ARITY:
        return _path_verdict(repo, str(pred[2]))
    return Finding(Verdict.UNDECIDABLE, f"unrecognised predicate head {head!r}")


def verdict_for(pred: tuple[object, ...], *, repo: Path, agda: Path) -> Finding:
    """Return the resolution verdict for one predicate tuple, recursing through combinators."""
    if not pred:
        return Finding(Verdict.UNDECIDABLE, "an empty predicate names nothing")
    head = pred[0]
    if head in COMBINATORS:
        members = pred[1] if len(pred) > 1 else ()
        if not isinstance(members, (list, tuple)):
            return Finding(Verdict.UNDECIDABLE, f"{head!r} carries no sub-predicate")
        return combine(head, [verdict_for(tuple(m), repo=repo, agda=agda) for m in members])
    return _artifact_verdict(pred, repo=repo, agda=agda)


def stale_items(
    items: list[dict[str, object]],
    *,
    repo: Path,
    agda: Path,
) -> list[tuple[str, str]]:
    """Return `(symbol, detail)` for every item whose predicate no longer resolves.

    ⚑ ONLY STALE ROWS ARE RETURNED, AND THAT IS THE OPERATOR'S RULING RENDERED AS A TYPE. An
    UNDECIDABLE row is not an offender — it is a row this reader declines to judge, and a gate
    that refused on it would block every commit over the `manual` items the list is designed to
    carry. Ask `verdict_for` directly when the third outcome is what you want to see.
    """
    out: list[tuple[str, str]] = []
    for item in items:
        pred = item.get("done")
        if not isinstance(pred, (list, tuple)):
            continue
        found = verdict_for(tuple(pred), repo=repo, agda=agda)
        if found.verdict is Verdict.STALE:
            out.append((str(item.get("sym", "?")), found.detail))
    return out
