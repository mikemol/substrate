#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Census a file's licence header: SPDX line and copyright line, as TWO facts.

⚑⚑⚑ WHY THIS EXISTS, AND IT IS A RETRACTION OF TWO OF MY OWN CLAIMS (gate-F96). Substrate
told a peer it has NO licence-header population, citing `pycodemod --literal
'SPDX-License-Identifier'` returning zero across the promoted package. Then a header was
found by eye in `scripts/`, and the correction sent was *zero under substrate, not zero
repo-wide*. Both readings are void: `--literal` searches STRING CONSTANTS and a licence
header is a COMMENT, so that census could never have seen one anywhere. The zero was a fact
about the reader, twice, in opposite directions.

⚑⚑ AND THE TWO LINES ARE INDEPENDENT PROPOSITIONS, WHICH IS THE WHOLE POINT OF THE SPLIT.
A peer measured that two repos were MIRROR IMAGES here — one gated SPDX only, the other
gated Copyright only, and each had run the arm its own config would pass. A single
`has_header` boolean reproduces exactly that blind spot: it goes green on either line and
cannot say which is missing. So an `Entry` carries both, and a caller asking *is this file
ready for a gate that checks both* gets an answer that distinguishes the two failures.

⚑ IT READS COMMENTS, NOT STRINGS, AND ONLY THE HEAD OF THE FILE. A licence header is a
prologue: `#!`, then the lines before the first statement. Scanning the whole file would
count a header quoted inside a docstring — which is how a module that DOCUMENTS the
convention would read as CONFORMING to it, and this module is exactly that module.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from mikemol.corpus import tree_root

from substrate import corpus, scan_root, walk_scope

# How the two header lines are spelled. ⚑ MATCHED AS PREFIXES OF A COMMENT, never as a
# substring of the file: `# SPDX-License-Identifier: Apache-2.0` is a header and a docstring
# mentioning the same token is prose.
SPDX_PREFIX = "# SPDX-License-Identifier:"
COPYRIGHT_PREFIX = "# Copyright"

# How far into a file a header may begin. A prologue is a shebang, an encoding line and the
# licence lines — anything past that is body, and a comment there is not a header.
_PROLOGUE_LINES = 8


@dataclass(frozen=True, slots=True)
class Entry:
    """One file's two independent header facts."""

    label: str
    spdx: bool
    copyright: bool

    @property
    def complete(self) -> bool:
        """Whether BOTH lines are present — what a two-proposition gate requires."""
        return self.spdx and self.copyright

    @property
    def partial(self) -> bool:
        """Whether exactly one line is present.

        ⚑ THIS IS THE ROW A SINGLE BOOLEAN HIDES. A file with one of the two passes a gate
        armed on that one and fails the other, and the two repos that measured this were
        each blind to the arm their own config did not check.
        """
        return self.spdx != self.copyright


def _label(entry_: Entry) -> str:
    """Return an entry's sort key.

    ⚑ NAMED, NOT A LAMBDA — an untyped lambda is `Callable[[Any], Any]` under this repo's
    bar, and `file_mode` carries the identical helper for the identical reason.
    """
    return entry_.label


def prologue(text: str) -> list[str]:
    """Return the comment lines that could carry a header, before the first statement."""
    out: list[str] = []
    for line in text.splitlines()[:_PROLOGUE_LINES]:
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("#"):
            break
        out.append(stripped)
    return out


def read(text: str, label: str) -> Entry:
    """Return the header facts for one file's source."""
    head = prologue(text)
    return Entry(
        label=label,
        spdx=any(line.startswith(SPDX_PREFIX) for line in head),
        copyright=any(line.startswith(COPYRIGHT_PREFIX) for line in head),
    )


def entry(path: Path, label: str) -> Entry | None:
    """Return the header facts for one file, or None when it cannot be read."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return read(text, label)


def entries(files: list[tuple[Path, str]]) -> tuple[Entry, ...]:
    """Return one Entry per readable file — the whole population, conforming or not."""
    got = [entry(p, label) for p, label in files]
    return tuple(e for e in got if e is not None)


def missing(found: tuple[Entry, ...]) -> tuple[Entry, ...]:
    """Return the entries that do NOT carry both lines.

    ⚑ THE DENOMINATOR IS THE CALLER'S TO PRINT. A bare count of offenders cannot separate
    *scanned and clean* from *never scanned* — the defect this session measured in the
    exe-bit sweep, whose frozen tree roster made a green a fact about the roster.
    """
    return tuple(e for e in found if not e.complete)


def by_tree(found: tuple[Entry, ...]) -> dict[str, tuple[int, int]]:
    """Return `{top-level dir: (complete, total)}`.

    ⚑ THE PER-TREE SPLIT IS THE ANSWER A MIGRATION NEEDS, and a repo-wide ratio hides it.
    A tree that is uniformly conforming and one that is uniformly bare average to a figure
    describing neither, and it is exactly the figure a peer would size intake against.
    """
    out: dict[str, tuple[int, int]] = {}
    for e in found:
        tree = e.label.split("/")[0]
        done, total = out.get(tree, (0, 0))
        out[tree] = (done + (1 if e.complete else 0), total + 1)
    return out


def population(root: Path | None = None, *scope: str) -> list[tuple[Path, str]]:
    """Return the corpus to scan, as `(path, repo-relative label)` pairs.

    ⚑⚑⚑ `scope` NAMES SUBTREES AND `root` NAMES THE REPO, AND WIRING THEM THE OTHER WAY
    ROUND READ AS AN EMPTY TREE. `corpus.py_files(*requested, root=)` walks `roots(root)`
    when nothing is requested, so passing a subtree as `root` made it look for directories
    INSIDE that subtree and report `0 of 0` for a tree holding hundreds of modules.

    ⚑⚑ AND `0 of 0` IS THE READING THIS REPO ALREADY REFUSES ELSEWHERE — a bare zero cannot
    separate *scanned and clean* from *never scanned*, which is why every count here ships
    its denominator. The denominator is what caught it: the label said zero files LACK the
    lines out of zero SCANNED, and only the second number was wrong.

    ⚑⚑⚑ AND THE LABEL RAISED FROM A BORROWING CHECKOUT (gate-G245 / gate-G249 / gate-G252).
    `Path.relative_to` demands the path lie under `where`, but `corpus.resolve_root` resolves
    the caller's CWD FIRST — deliberately — so a peer running this tool from their own tree
    walked THEIR files and measured them against SUBSTRATE's root, and the whole census died
    on the first row. `tree_root.of(where).label` carries one root and does both, so the tree
    that was walked is the tree that labels and they cannot disagree.
    """
    where = root if root is not None else corpus.ROOT
    found = corpus.py_files(*scope, root=where)
    tree = tree_root.of(where)
    return [(Path(p), tree.label(p)) for p in found]


def render(found: tuple[Entry, ...]) -> str:
    """Return the census: per-tree conformance, then the partial rows by name.

    ⚑ PARTIAL IS ITS OWN COLUMN, NOT FOLDED INTO A DEFICIT. A file carrying one of the two
    lines is a DIFFERENT repair from one carrying neither, and a gate armed on the line it
    already has reports it green — the mirror-image defect this split exists for.
    """
    if not found:
        return "file-header: no files scanned — a fact about the WALK, not the tree\n"

    rows = [f"  {'TREE':<12} {'BOTH':>6} {'PARTIAL':>8} {'NEITHER':>8} {'TOTAL':>6}"]
    for tree in sorted(by_tree(found)):
        here = [e for e in found if e.label.split("/")[0] == tree]
        both = sum(1 for e in here if e.complete)
        part = sum(1 for e in here if e.partial)
        rows.append(f"  {tree:<12} {both:>6} {part:>8} {len(here) - both - part:>8} {len(here):>6}")

    gaps = missing(found)
    partials = [e for e in gaps if e.partial]
    rows.append("")
    rows.append(
        f"file-header: {len(found) - len(gaps)} of {len(found)} file(s) carry BOTH "
        f"lines · {len(partials)} carry exactly one"
    )
    if partials:
        rows.append(
            "  ⚑ A PARTIAL FILE PASSES A GATE ARMED ON THE LINE IT HAS. Naming which "
            "is missing is the whole reason these are two facts:"
        )
        rows.extend(
            f"     {'no-spdx     ' if not e.spdx else 'no-copyright'}  {e.label}"
            for e in sorted(partials, key=_label)
        )
    return "\n".join(rows) + "\n"


def render_missing(found: tuple[Entry, ...]) -> str:
    """Return one row per non-conforming file, named, with the denominator scanned.

    ⚑⚑⚑ THE CENSUS COULD NOT BE AUDITED AGAINST A CASE UNTIL THIS EXISTED. `render` gives
    per-tree totals and no way to name WHICH files lack the lines, so a caller paying the
    population down could not enumerate it before acting on its count — and this repo's own
    rule is that a reader reporting only aggregates cannot be audited. `missing` was already
    built and bound to nothing.

    ⚑⚑ AND FINDING ONE CONFORMING FILE WAS NOT A QUESTION THIS TOOL COULD ANSWER EITHER. A
    search for the SPDX spelling by literal STRING returns zero across a tree this census
    reports as conforming, because the header is a COMMENT — so a caller reaching for an
    example by grep gets a false absence, and the only authority is the constant above.
    """
    absent = missing(found)
    rows = [
        f"  {'PARTIAL' if e.partial else 'NEITHER':<8} {e.label}"
        for e in sorted(absent, key=_label)
    ]
    rows.append(f"file-header: {len(absent)} of {len(found)} file(s) lack both lines")
    return "\n".join(rows) + "\n"


def main(argv: list[str]) -> int:
    """Print the licence-header census for the corpus, and the walk's own bound.

    ⚑ THE SCOPE STATEMENT IS APPENDED HERE, NOT INSIDE `render`, following `file_mode`. The
    walk's boundary is a fact about the DEFAULT corpus this `main` chose, so it is the
    caller's disclosure — folding it into `render` would make every fixture-driven case
    assert something about the real repo.

    ⚑⚑⚑ THE SCOPE OPERAND EXISTS BECAUSE ITS FIRST CUT REPRODUCED A DEFECT THIS REPO HAD
    JUST FILED AGAINST ANOTHER TOOL. `--missing` shipped with an exact-match guard, so
    `file_header.py --missing substrate` was REFUSED and a caller paying down one subtree
    could not ask about that subtree. `codepoints.py` had the same gap and silently WIDENED
    to the whole tree instead — refusing is the better direction, and it is the same class.

    ⚑⚑ RESOLUTION IS `scan_root`'s, NOT RE-DERIVED HERE. It refuses a path naming nothing
    rather than falling back to the tree, because a narrowing that does not narrow returns
    MORE rows and therefore reads as a rich answer rather than an error.
    """
    flags = [a for a in argv if a.startswith("-")]
    if any(f != "--missing" for f in flags):
        sys.stderr.write("usage: file_header.py [--missing] [<path>]\n")
        return 2

    scope = scan_root.resolve([a for a in argv if not a.startswith("-")])
    if isinstance(scope, scan_root.Refusal):
        sys.stderr.write(f"file-header: {scope.message}\n")
        return 2

    found = entries(population(None, *([] if scope.root == "." else [scope.root])))
    sys.stdout.write(render_missing(found) if "--missing" in flags else render(found))
    sys.stdout.write(walk_scope.render())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
