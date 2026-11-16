# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Where the repo mutates `sys.path`, grouped by the directory each mutation makes reachable.

⚑⚑⚑ THE DRAIN IS PER-DIRECTORY, NOT PER-FILE, WHICH IS WHY THIS GROUPS RATHER THAN LISTS.
A `sys.path` insert exists to make ONE directory importable; the repair is a package boundary
for that directory, after which every insert naming it becomes deletable at once. A per-file
listing invites hundreds of separate edits for what is a much smaller number of decisions.

⚑⚑ AND THE SHAPE OF THE PROBLEM IS NOT WHAT ITS NAME SUGGESTS. The work was queued as a
`scripts/` package question; measured, `scripts` is the THIRD-largest target behind `scratch`
and `metalanguage`, and one target (`eliza`) is a directory that ALREADY has `__init__.py`,
so its inserts are a test-bootstrap problem rather than a packaging one. Ordering the drain by
the queue's framing would have started with neither the largest nor the easiest.

⚑ `<unresolved>` IS A REPORTED BUCKET, NOT A DROPPED ONE. An insert whose argument is computed
— a variable, a call, a join this reader cannot fold — has no statically knowable target, and
counting it under some plausible directory would be an invented fact. It is named so its size
is visible: those sites need reading, and the census says how many.

⚑ THE POPULATION EXCLUDES VENDORED AND GENERATED TREES (`build/`, `.venv/`, `stubs/`) because
a mutation in a copy is not a site anyone can fix, and counting copies would inflate the drain
with work that does not exist.
"""

from __future__ import annotations

import ast
import sys
from collections import Counter
from dataclasses import dataclass

from substrate import corpus, insert_read

# Trees whose contents are copies, dependencies, or type-only declarations.
SKIP_PREFIXES = ("build/", ".venv/", "stubs/", "agda/")


@dataclass(frozen=True, slots=True)
class Target:
    """One directory made importable, and who makes it so."""

    directory: str
    sites: int
    files: tuple[str, ...]

    @property
    def is_resolved(self) -> bool:
        """Whether a static read could name this target at all."""
        return self.directory != insert_read.UNKNOWN


def python_files(skip: tuple[str, ...] = SKIP_PREFIXES) -> list[str]:
    """Return every repo-relative `.py` path outside the skipped trees.

    ⚑ HIDDEN DIRECTORIES ARE SKIPPED TOO — `.git`, `.venv` and the snapshot trees hold
    copies, and a census counting a snapshot reports the same defect twice.
    """
    root = corpus.ROOT
    out: list[str] = []
    for path in sorted(root.rglob("*.py")):
        rel = str(path.relative_to(root))
        if any(rel.startswith(s) for s in skip) or "/." in f"/{rel}":
            continue
        out.append(rel)
    return out


def census(paths: list[str] | None = None) -> tuple[list[Target], int]:
    """Return `(targets, unparsed)` — the mutation sites grouped by directory.

    ⚑ AN UNPARSEABLE FILE IS COUNTED, NOT SKIPPED SILENTLY. A syntax error means this reader
    saw nothing in that file, which is a fact about the reader; folding it into a zero would
    report the file as clean.
    """
    root = corpus.ROOT
    counts: Counter[str] = Counter()
    owners: dict[str, set[str]] = {}
    unparsed = 0

    for rel in paths if paths is not None else python_files():
        try:
            tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            unparsed += 1
            continue
        for ins in insert_read.inserts(tree, rel):
            counts[ins.target] += 1
            owners.setdefault(ins.target, set()).add(rel)

    targets = [Target(d, n, tuple(sorted(owners[d]))) for d, n in counts.most_common()]
    return targets, unparsed


def total_sites(targets: list[Target]) -> int:
    """Return how many mutation sites the census found."""
    return sum(t.sites for t in targets)


def owning_files(targets: list[Target]) -> set[str]:
    """Return every file holding at least one mutation.

    ⚑ A SET, BECAUSE ONE FILE MAY INSERT SEVERAL DIRECTORIES. Summing per-target file counts
    would double-count exactly the files that are hardest to drain.
    """
    return {f for t in targets for f in t.files}


def render(targets: list[Target], unparsed: int, show: int = 0) -> str:
    """Render the census, largest target first."""
    head = (
        f"{total_sites(targets)} sys.path mutation(s) across {len(owning_files(targets))} file(s)"
    )
    out = [head]
    if unparsed:
        out.append(f"  ⚑ {unparsed} file(s) did not parse — a fact about this reader")
    out.append("")
    out.append("by directory made importable:")
    out.extend(
        f"  {t.directory:<18} {t.sites:>4} site(s) in {len(t.files):>3} file(s)"
        + ("" if t.is_resolved else "   ⚑ no static target — these need reading")
        for t in targets
    )
    for target in targets[:show]:
        out.append(f"\n  {target.directory}:")
        out.extend(f"      {f}" for f in target.files)
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    """Print the `sys.path` census, optionally naming the files under the largest targets.

    ⚑⚑⚑ THE READER WAS BUILT AND BOUND TO NOTHING, THE SECOND INSTANCE IN THREE TICKS.
    `census`, `render` and a `show` parameter that names files all existed with no dispatch,
    so the only way to ask this question was an inline script — which the no-chaining hook
    refuses, correctly, because a judgement made in a turn evaporates with it. A clean
    function nothing calls is indistinguishable from an absent one to every reader except
    someone opening the file.

    ⚑⚑ AND THE QUESTION IT ANSWERS IS NOW A PEER'S. A `sys.path` insert is exactly what breaks
    a tool invoked through a symlink: the insert is computed from `__file__`, which `abspath`
    does not resolve, so the directory made importable is the CALLER's rather than the tool's.
    A peer hit that on `mdstruct` and asked whether a routing table can check that its named
    successors run. This census is the static half of that answer — a tool with no insert
    cannot fail that way.

    ⚑ IT IS A FLOOR ON THE HAZARD, NOT A VERDICT, AND `<unresolved>` IS WHY. An insert whose
    argument is computed has no statically knowable target, so a tool can carry a hazard this
    reader reports as unresolved rather than as absent.
    """
    show = 0
    if argv and argv[0] == "--files":
        show = int(argv[1]) if len(argv) > 1 else 3
    elif argv:
        sys.stderr.write("usage: syspath_census.py [--files [N]]\n")
        return 2

    targets, unparsed = census()
    sys.stdout.write(render(targets, unparsed, show=show))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
