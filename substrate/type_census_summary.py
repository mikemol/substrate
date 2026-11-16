#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The SHAPE of the mypy census: which codes dominate, which files carry them, which tree.

⚑⚑ `type_gate.py --list` IS 1,134 LINES AND 123 KB, AND THAT IS NOT A WORK LIST. Measured
2026-09-02. Every row renders honestly and the reader still cannot say which of the codes
matters, whether one root carries the debt or all four do, or whether a paydown of ten files
would move the number. A census that reports every row and no structure forces the judgement
into the reader's turn — which is the shape the standing rule exists to refuse, and it is
here in the tool the rule's own gate depends on.

⚑ IT SUMMARISES THE CENSUS, IT DOES NOT RE-TAKE IT. `mypy_census.type_errors` is the one
authority for what mypy said; a second invocation with its own flags would be a second census
disagreeing with the gate's at the moments it matters most. The unrunnable sentinel is
propagated, never folded into "no keys" — that fold is the defect `type_gate` was built after.

⚑⚑⚑ AND THE READING IT PRODUCES IS NOT THE READING THE KEY COUNT SUGGESTS. A census key is
`<code>::<relpath>`, so ONE key can stand for 213 messages; ranking keys ranks FILES and says
nothing about volume. Every listing here weights by MESSAGE, which is what turns "1,134 keys"
into "one error code is most of the tree". The two orderings disagree, and only the second
answers "is this one root cause or many".

    type_census_summary.py            # codes, roots and the top files — the whole shape
    type_census_summary.py --codes    # error codes by message volume
    type_census_summary.py --roots    # which promoted tree carries the debt
    type_census_summary.py --files 30 # the files carrying the most messages
    type_census_summary.py --texts 30 # the most-repeated MESSAGE TEXTS, across all files
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from mikemol.corpus import tree_root

from substrate import corpus, mypy_census, promoted
from substrate.type_gate import MypyUnavailable

if TYPE_CHECKING:
    from collections.abc import Callable

# How many rows a listing shows when the caller names no count.
#
# ⚑ PUBLIC BECAUSE THE SUITE NAMES IT. A default a case has to spell for itself is a second
# authority for the same number, and the two drift apart silently the first time one moves.
DEFAULT_TOP = 20

# How many rows each block of the combined (no-mode) view shows.
_OVERVIEW_TOP = 10

# How much of a message text to show in the `--texts` listing.
_EXCERPT = 72

# The separator `mypy_census` builds its keys from: `<code>::<relpath>`.
_SEP = "::"

# ⚑ RESTATED RATHER THAN IMPORTED FROM `type_gate`, because reaching for its `_NOT_INSTALLED`
# is a private read (`PLC2701`) and the refusal is right: a module-private constant is not an
# interface. The remedy — the part that would actually drift — is carried by `MypyUnavailable`
# itself, which IS imported, so the two refusals still name the same fix.
_NOT_INSTALLED = "mypy is not installed for this interpreter"

# The listing widths. A name column wide enough for `jea/evolution/...` paths.
_NAME_W = 52
_BAR_W = 28

# Exit code for a census that could not be taken — `gate_main`'s spelling, deliberately.
_CANNOT_MEASURE = 2

_MODES = ("--codes", "--roots", "--files", "--texts")


@dataclass(frozen=True, slots=True)
class Shape:
    """One census, counted three ways plus its raw message texts.

    ⚑ THE COUNTS ARE NOT DERIVABLE FROM EACH OTHER, which is why each is held. `key_count`
    answers "how many (code, file) pairs" — the ratchet's own unit. `messages` answers "how
    much work" — a file with one key and 213 messages outranks a hundred single-message keys.
    `by_file` answers "how concentrated" — the number that decides whether a paydown is a
    sprint or an arc. Reporting any one of them as "the size of the debt" is the
    collapse-to-a-scalar this repo keeps paying for.
    """

    by_code: Counter[str]
    by_file: Counter[str]
    by_root: Counter[str]
    texts: Counter[str]
    key_count: int

    @property
    def messages(self) -> int:
        """How many individual mypy findings the census stands for."""
        return sum(self.by_code.values())


def root_of(relpath: str) -> str:
    """Return the promoted tree a repo-relative path sits in."""
    head, _, tail = relpath.partition("/")
    return head if tail else "."


def shape_of(rows: dict[str, list[str]]) -> Shape:
    """Count a taken census by code, by file, by root and by message text.

    ⚑ WEIGHTED BY MESSAGE, NOT BY KEY. `len(msgs)` is the whole point: a key is a (code, file)
    pair, so counting keys counts files-carrying-that-code and hides that one file can hold
    two hundred findings. The gate ratchets on keys because keys are stable under unrelated
    edits; a HUMAN reading the debt needs the other axis.
    """
    by_code: Counter[str] = Counter()
    by_file: Counter[str] = Counter()
    by_root: Counter[str] = Counter()
    texts: Counter[str] = Counter()
    for key, msgs in rows.items():
        code, _, relpath = key.partition(_SEP)
        n = len(msgs)
        by_code[code] += n
        by_file[relpath] += n
        by_root[root_of(relpath)] += n
        for m in msgs:
            texts[m[:_EXCERPT]] += 1
    return Shape(
        by_code=by_code, by_file=by_file, by_root=by_root, texts=texts, key_count=len(rows)
    )


def census() -> dict[str, list[str]]:
    """Take the census over the promoted corpus, or refuse.

    ⚑ RAISES RATHER THAN RETURNING EMPTY, for the reason `type_gate.census` does: a caller
    that folds "mypy could not run" into "no findings" certifies its own blind spot, and this
    module's whole output would then read as a clean tree.

    ⚑⚑⚑ AND THIS IS THE SITE A PARAMETER-KEYED CENSUS COULD NOT SEE (gate-G256). It takes NO root
    argument, so there was no parameter to inspect — it reaches `corpus.ROOT` as a module global
    while `corpus.py_files` walks the caller's cwd, and the two are independent. Predicted from
    that shape and CONFIRMED BY EXECUTION before anything was changed: from a peer's tree it raised
    on `summit/scripts/__init__.py`. `tree_root` carries one root and does both.
    """
    tree = tree_root.of(corpus.ROOT)
    files = [tree.label(Path(f)) for f in corpus.py_files(*promoted.POPULATION)]
    rows = mypy_census.type_errors(files)
    if rows is None:
        raise MypyUnavailable(_NOT_INSTALLED)
    if mypy_census.UNRUNNABLE in rows:
        raise MypyUnavailable(rows[mypy_census.UNRUNNABLE][0])
    return rows


def bar(n: int, total: int) -> str:
    """Render a share as a fixed-width bar, so concentration is visible at a glance."""
    filled = 0 if total <= 0 else round(_BAR_W * n / total)
    return "#" * filled + "." * (_BAR_W - filled)


def listing(counts: Counter[str], total: int, top: int, label: str) -> str:
    """Render the `top` heaviest rows of one counter, with shares and a tail row.

    ⚑ THE TAIL ROW IS NOT DECORATION. A top-N with no remainder line reads as the whole
    population, and a reader who sums the shown shares to 40% cannot tell whether the rest is
    one more heavy row or six hundred light ones. Naming the residue is what makes the
    truncation honest rather than a second census with a different boundary.
    """
    lines = [f"{label:<{_NAME_W}}{'msgs':>8}  {'share':>6}"]
    # ⚑ TRUNCATED HERE, NOT AT THE CALL SITE, so no caller can overflow the column. The
    # `--texts` view feeds in whole mypy messages; a name longer than the field pushes every
    # later column right and the listing stops being scannable exactly where it is densest.
    lines.extend(
        f"{name[:_NAME_W]:<{_NAME_W}}{n:>8}  {100 * n / total:>5.1f}%  {bar(n, total)}"
        for name, n in counts.most_common(top)
    )
    shown = sum(n for _, n in counts.most_common(top))
    if len(counts) > top:
        rest = total - shown
        lines.append(
            f"{f'... {len(counts) - top} more':<{_NAME_W}}{rest:>8}  {100 * rest / total:>5.1f}%"
        )
    return "\n".join(lines)


def headline(shape: Shape) -> str:
    """Name every count, so no single number can stand in for the debt."""
    return (
        f"mypy census: {shape.key_count} keys, {shape.messages} messages, "
        f"{len(shape.by_file)} files, {len(shape.by_code)} codes"
    )


def report(shape: Shape, mode: str, top: int) -> str:
    """Render the requested view of a counted census."""
    total = shape.messages
    views: dict[str, tuple[Counter[str], str]] = {
        "--codes": (shape.by_code, "error code"),
        "--roots": (shape.by_root, "promoted root"),
        "--files": (shape.by_file, "file"),
        "--texts": (shape.texts, "message text"),
    }
    view = views.get(mode)
    if view is not None:
        counts, label = view
        return f"{headline(shape)}\n\n{listing(counts, total, top, label)}"
    blocks = [
        listing(shape.by_code, total, _OVERVIEW_TOP, "error code"),
        listing(shape.by_root, total, _OVERVIEW_TOP, "promoted root"),
        listing(shape.by_file, total, _OVERVIEW_TOP, "file"),
    ]
    return headline(shape) + "\n\n" + "\n\n".join(blocks)


def render_or_refuse(take: Callable[[], dict[str, list[str]]], mode: str, top: int) -> int:
    """Take a census through `take` and render it, or refuse with the reason it gave.

    ⚑⚑ THE CENSUS ARRIVES AS AN ARGUMENT SO THE REFUSAL ARM IS REACHABLE WITHOUT A PRIVATE
    POKE. `type_gate`'s suite learned this the hard way: setting up its render case tripped
    `SLF001`, and that refusal named a real design fault rather than a test inconvenience —
    state only a private poke can establish is state the interface does not admit exists. The
    alternative here was monkeypatching the module attribute, which needs a `type: ignore`
    this tree does not grant.

    ⚑ AND THE REFUSAL IS NOT SILENCEABLE. There is no `--quiet` on this tool at all, because
    a summary that renders nothing and exits 0 is exactly the clean-looking blind spot the
    gate it summarises exists to prevent.
    """
    try:
        rows = take()
    except MypyUnavailable as e:
        sys.stderr.write(
            "type-census-summary: CANNOT MEASURE -- refusing rather than "
            f"reporting an empty shape.\n  reason: {e.reason}\n"
        )
        if e.remedy:
            sys.stderr.write(f"  try:  {e.remedy}\n")
        return _CANNOT_MEASURE
    sys.stdout.write(report(shape_of(rows), mode, top) + "\n")
    return 0


def main(argv: list[str]) -> int:
    """Render the census shape. 0 = rendered, 2 = the census could not be taken."""
    tail = argv[1:]
    unknown = [a for a in tail if a.startswith("-") and a not in _MODES]
    if unknown:
        sys.stderr.write(
            f"type-census-summary: unknown flag(s) {' '.join(unknown)}"
            f" -- known: {' '.join(_MODES)} [N]\n"
        )
        return _CANNOT_MEASURE
    mode = next((a for a in tail if a in _MODES), "")
    # ⚑ SPELLED AS A LOOP RATHER THAN `next(..., DEFAULT_TOP)`, and the reason is the very
    # flag this tool exists to explain: under `disallow_any_expr` a `next()` with a default
    # types as `int | Any`, so the idiomatic one-liner is itself a census key. The tool that
    # reports the Any surface may not add to it.
    top = DEFAULT_TOP
    for a in tail:
        if a.isdigit():
            top = int(a)
    return render_or_refuse(census, mode, top)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
