#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The three readers over the inferred interface — generation, narrowing, under-annotation.

⚑⚑⚑ THE GENERATOR IS `stubgen`, AND THE REUSE-SEARCH THAT ESTABLISHED THAT SHRANK THIS FILE
RATHER THAN GROWING IT. `stubgen` ships with mypy (already a dependency), is byte-stable across
runs at fixed flags (verified by two runs and `cmp`), and emits exactly the derived view reader
1 asks for. So this module does NOT generate stubs; it decides WHICH modules are eligible and
reports what the derived view would and would not state. Building a second generator would be
the reinvention the standing rule exists to stop.

⚑⚑⚑ AND `stubgen` IS NOT SUFFICIENT ON ITS OWN, WHICH IS WHY THE ELIGIBILITY READER EXISTS.
Measured on `scripts/check_carrier_locality.py`: `stubgen` emits eight `Incomplete`s and
`def scan(paths=None): ...`, while the AUTHORED stub states `Iterable[str] | None` and a full
nested return type. Under this repo's `disallow_any_expr` bar `Incomplete` is `Any`, so the
generated view is not merely weaker — it is REFUSED by the gate that admits `substrate/`.
Regenerating that stub today would DELETE working type information.

⚑⚑ SO THE REPLACEMENT IS CONDITIONAL ON THE MODULE, NOT ON THE POLICY, and that condition is
computable: a module whose source states every slot derives a stub with no `Incomplete` in it,
and for that module the generated view is strictly better than an authored one (it cannot
contradict its subject). A module that states nothing derives a hollow stub. The eligibility
reader is therefore the honest form of reader 1 — it names which stubs can become generated
views TODAY, and what each remaining one owes first. That is the same answer the operator
asked for, with the precondition made visible rather than assumed.

⚑ WHICH MAKES READER 3 THE SCHEDULER FOR READER 1, not an independent report. The
under-annotation census ranks exactly the work that converts an authored stub into a
generatable one, so the two readers are one mechanism read at two points.

⚑⚑⚑ AND THE DENOMINATOR WAS SHORT BY A WHOLE SLOT KIND, WHICH IS WORSE THAN BEING SHORT BY A
COUNT. `--eligible` read `iface_infer.Interface.slots`, and that walk gives a module-level
assignment a Symbol with NO params and `is_function=False` — so `Symbol.slots` is 0 and the
symbol is `complete` by construction. An unannotated `DECL = re.compile(...)` therefore
contributed nothing to the denominator, nothing to the owed list, and read as fully stated.

⚑⚑⚑ THE MEASUREMENT THAT SETTLES IT: `stubgen --no-import` over
`scripts/check_carrier_locality.py` emits `ROOT: Incomplete`, `SRC: Incomplete`,
`BASELINE: Incomplete`, `ALLOW: Incomplete`, `DECL: Incomplete`, `SIG: Incomplete` — SIX
`Incomplete`s the eligibility reader could not see, in a module it reported as `0/13`. The
true denominator is 19. So the reader was not merely imprecise about how far a module was
from eligible; it was blind to a kind of debt that BLOCKS eligibility exactly as hard as an
unannotated parameter does, while reporting those assignments as though they were fine.

⚑⚑ THE TWO HALVES ARE COUNTED APART BECAUSE THEY COST DIFFERENT AMOUNTS TO RETIRE, AND THAT
ASYMMETRY IS MEASURED RATHER THAN ASSUMED. `iface_construct --module scratch/agda_lex.py`
resolves 16 of 17 assignments in 1.5s; `iface_dataflow --module` on the same file does not
finish in 600s (exit 124), because a parameter's type is a query over the whole corpus while
an assignment's type is a query over the defining module's own text. Merging them into one
number would put the cheap answer behind the expensive one, and a reader wanting only the
assignment half would have to pay four hundred times over for it.

⚑ SO THIS READER CALLS `iface_construct`, NOT `iface_dataflow`. The seam the operator named —
`iface_dataflow.module_interface` should enumerate assignments alongside functions — is real
and is REPORTED rather than taken: taking it there would make every assignment census pay the
corpus walk. `iface_construct.resolve_module` is the assignment-only reader, and it is the one
a gate can afford to run.

Usage: iface_readers.py --eligible | --narrowing <upstream.pyi> <ours.pyi> | --census [paths]
       iface_readers.py --selftest
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus, iface_construct, iface_infer

# Where a repo-local stub's runtime module lives. `scratch/` and `scripts/` are the two
# unpackaged trees a `.pyi` exists to reach; a stub naming neither is a third-party narrowing.
_RUNTIME_DIRS = ("scratch", "scripts")

# `--narrowing` takes exactly two operands: the upstream surface and ours.
_NARROWING_OPERANDS = 2


@dataclass(frozen=True, slots=True)
class Assignments:
    """The module-level assignment half of one module's interface.

    ⚑ `stated` COUNTS WHAT THE SOURCE ANNOTATES, NOT WHAT A READER COULD DERIVE. Those are
    different questions and only the first bears on eligibility: `stubgen` writes
    `Incomplete` for `DECL = re.compile(...)` no matter how confidently `iface_construct`
    can type it. `derivable` is carried BESIDE `stated` rather than folded into it, because
    a slot a reader can retire and a slot the source already states are different work.
    """

    slots: int
    stated: int
    derivable: int
    owed: tuple[str, ...]


def assignment_slots(source: Path) -> Assignments:
    """Measure one module's module-level assignment slots — the kind `--eligible` missed.

    ⚑⚑ EVERY MODULE-LEVEL BINDING IS A SLOT, and `iface_construct.assignments` is the walk
    that enumerates them. It already excludes the two shapes that are not interface (a name
    bound inside a function; a tuple target it cannot split), so no second walk is written
    here — the same reuse rule that keeps `stated_slot` asking `iface_infer`.

    ⚑ THE ORACLE IS RUN ONCE FOR THE WHOLE MODULE, which is what makes this affordable.
    `resolve_module` batches every unresolved expression into ONE mypy probe; asking per
    slot would multiply a 1.5s read by the module's assignment count.
    """
    try:
        tree = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return Assignments(0, 0, 0, ())
    rows = iface_construct.resolve_module(tree, str(source))
    stated = sum(1 for r in rows if r.status == "STATED")
    derivable = sum(1 for r in rows if r.status == "COMPUTED")
    owed = tuple(r.name for r in rows if r.status != "STATED")
    return Assignments(len(rows), stated, derivable, owed)


@dataclass(frozen=True, slots=True)
class Eligibility:
    """Whether one repo-local stub can become a generated view, and what it owes."""

    module: str
    source: str
    slots: int
    stated: int
    owed: tuple[str, ...]
    assigns: Assignments = Assignments(0, 0, 0, ())

    @property
    def total_slots(self) -> int:
        """Return every slot a generated stub must state — functions AND assignments."""
        return self.slots + self.assigns.slots

    @property
    def total_stated(self) -> int:
        """Return how many of those slots the SOURCE states."""
        return self.stated + self.assigns.stated

    @property
    def eligible(self) -> bool:
        """Report whether a generated stub would state everything the authored one does.

        ⚑ THE PREDICATE IS "NO HOLLOW SLOTS", NOT "MOSTLY ANNOTATED". One `Incomplete`
        under `disallow_any_expr` poisons every downstream expression, so a 90%-annotated
        module derives a stub the gate still refuses. There is no partial credit here,
        which is why the census below ranks by slots OWED rather than by ratio.

        ⚑⚑ AND AN UNSTATED ASSIGNMENT IS A HOLLOW SLOT EXACTLY AS AN UNSTATED PARAMETER IS.
        Measured: `stubgen` writes `ROOT: Incomplete` for `ROOT = os.path.dirname(...)`.
        While this predicate read only the function half it could call a module eligible
        whose generated stub was full of `Incomplete` — the census-green shape, in the
        reader whose whole job is to refuse a generated view that loses information.
        """
        return self.total_slots == self.total_stated


def repo_local_stubs(root: Path = corpus.ROOT) -> list[tuple[str, Path]]:
    """Return each bare `.pyi` in `stubs/` paired with the in-repo module it describes.

    ⚑ A PACKAGE STUB IS A THIRD-PARTY NARROWING, NOT A REPO-LOCAL VIEW. `stubs/psycopg/`
    and friends are directories shadowing installed packages; the repo-local stubs are the
    bare `.pyi` files, each naming a module under `scratch/` or `scripts/`. Splitting on
    that structural fact is what keeps reader 1 and reader 2 from being handed each other's
    population — and it is DISCOVERED, so adding a stub needs no edit here.
    """
    out: list[tuple[str, Path]] = []
    for stub in sorted((root / "stubs").glob("*.pyi")):
        for d in _RUNTIME_DIRS:
            src = root / d / f"{stub.stem}.py"
            if src.is_file():
                out.append((stub.stem, src))
                break
    return out


def eligibility(module: str, source: Path) -> Eligibility | None:
    """Measure whether one module's source supports a fully-stated generated stub."""
    iface = iface_infer.interface_of(source)
    if iface is None:
        return None
    owed = tuple(f"{s.name}:{s.lineno}" for s in iface.hollow)
    return Eligibility(
        module, str(source), iface.slots, iface.stated, owed, assignment_slots(source)
    )


def owed_key(iface: iface_infer.Interface) -> tuple[int, str]:
    """Return the sort key ranking an interface by unstated slots, worst first.

    ⚑ A NAMED KEY RATHER THAN A LAMBDA, because an unannotated lambda parameter is `Any`
    under this repo's bar and would poison the whole sort expression. Naming it is what
    keeps the ranking concretely typed — the same narrow-at-the-seam move `stub_declines`
    records for `re.Match.group`.

    ⚑ THE MODULE NAME IS THE TIE-BREAK, so equal debt sorts stably rather than by
    whatever order the walk happened to produce.
    """
    return (-(iface.slots - iface.stated), iface.module)


def owed_order(interfaces: list[iface_infer.Interface]) -> list[iface_infer.Interface]:
    """Rank interfaces by the annotation slots they leave unstated, worst first.

    ⚑ RANKED BY SLOTS OWED, NOT BY RATIO. A 50%-annotated two-slot module and a
    50%-annotated eighty-slot module are the same ratio and vastly different work; ranking
    by ratio would put the trivial one at the same height as the one that matters. The
    ratio is reported beside each row, never used to order it.
    """
    return sorted(interfaces, key=owed_key)


def census(paths: list[str]) -> list[iface_infer.Interface]:
    """Infer every named module's interface and rank it by what it leaves unstated."""
    got = [iface_infer.interface_of(Path(p)) for p in paths]
    return owed_order([i for i in got if i is not None])


def _render_row(e: Eligibility) -> None:
    """Print one stub's two slot halves, kept apart because they cost differently."""
    mark = "OK " if e.eligible else "NO "
    sys.stdout.write(
        f"    {mark} {e.module}: {e.total_stated}/{e.total_slots} slots stated at source "
        f"({e.stated}/{e.slots} function, {e.assigns.stated}/{e.assigns.slots} assignment)\n"
    )
    if e.owed:
        sys.stdout.write(f"        owes annotation at: {', '.join(e.owed)}\n")
    if e.assigns.owed:
        sys.stdout.write(
            f"        owes assignment types: {', '.join(e.assigns.owed)}\n"
            f"        of which {e.assigns.derivable} are DERIVABLE today "
            f"(iface_construct resolves them from the module's own text)\n"
        )


def _render_eligible() -> int:
    """Print which repo-local stubs can become generated views today."""
    rows = [e for m, s in repo_local_stubs() if (e := eligibility(m, s)) is not None]
    ready = [e for e in rows if e.eligible]
    sys.stdout.write(
        f"iface-eligible: {len(ready)} of {len(rows)} repo-local stub(s) can be GENERATED "
        f"today (a generated view states every slot, so it cannot contradict its module).\n"
    )
    for e in rows:
        _render_row(e)
    if len(ready) != len(rows):
        sys.stdout.write(
            "  A stub is NOT eligible while its module leaves slots unstated: `stubgen`\n"
            "  writes `Incomplete` (= `Any`) there, which `disallow_any_expr` REFUSES —\n"
            "  so regenerating it would DELETE type information the authored stub states.\n"
            "  Annotate the module first; the owed sites above are that work, in order.\n"
            "  ⚑ THE TWO HALVES COST DIFFERENTLY. An assignment's type is a query over the\n"
            "  defining module's own text (1.5s on the largest of these); a parameter's is\n"
            "  a query over the whole corpus (600s+, unfinished). The DERIVABLE count names\n"
            "  the assignments a reader can retire now, without annotating anything.\n"
        )
    return 0


def _render_narrowing(upstream: Path, ours: Path) -> int:
    """Print the names an upstream states that our stub does not."""
    up_src = upstream.read_text(encoding="utf-8", errors="replace")
    our_src = ours.read_text(encoding="utf-8", errors="replace")
    missing = iface_infer.narrowing(up_src, our_src)
    have = len(iface_infer.declared_names(up_src))
    sys.stdout.write(
        f"iface-narrowing: our stub declares {have - len(missing)} of {have} upstream "
        f"name(s); {len(missing)} unreachable while the narrowing stands.\n"
    )
    for n in missing:
        sys.stdout.write(f"    - {n}\n")
    return 0


def _render_census(paths: list[str]) -> int:
    """Print the under-annotation ranking — the paydown queue reader 1 waits on."""
    rows = census(paths)
    owed = [i for i in rows if i.slots != i.stated]
    sys.stdout.write(
        f"iface-census: {len(owed)} of {len(rows)} module(s) leave annotation slots "
        f"unstated — the half `stubtest` can never verify.\n"
    )
    for i in owed:
        sys.stdout.write(
            f"    {i.slots - i.stated:5d} owed  {i.stated}/{i.slots} ({i.ratio:.0%})  {i.module}\n"
        )
    return 0


def main(argv: list[str]) -> int:
    """Dispatch one reader; 2 on an unusable command line."""
    rest = [a for a in argv[1:] if not a.startswith("-")]
    if "--eligible" in argv:
        return _render_eligible()
    if "--narrowing" in argv:
        if len(rest) != _NARROWING_OPERANDS:
            sys.stdout.write("--narrowing needs <upstream.pyi> <ours.pyi>\n")
            return 2
        return _render_narrowing(Path(rest[0]), Path(rest[1]))
    if "--census" in argv:
        return _render_census(corpus.py_files(*rest))
    sys.stdout.write(__doc__ or "")
    return 2


def _cases_assign() -> list[tuple[str, object, object]]:
    """Pin the ASSIGNMENT half of eligibility — the slot kind the reader could not see.

    ⚑ WRITTEN AGAINST A FILE ON DISK because `assignment_slots` reads a path, which is the
    shape `eligibility` actually calls. A source-text variant would be a second code path
    existing only for the suite, and a path the shipped mode does not take can drift from it.
    """
    tmp = Path(__file__).absolute().parent / "_iface_readers_fixture"
    tmp.mkdir(exist_ok=True)
    # ⚑ THREE ARMS IN ONE FIXTURE: an ANNOTATED assignment (stated), an unannotated literal
    # (unstated but derivable), and an unannotated machine-dependent one (unstated and NOT
    # derivable). A reader collapsing any pair of these fails here.
    probe = tmp / "afix.py"
    probe.write_text("import os\nA: int = 1\nB = 'x'\nC = os.environ['HOME']\n", encoding="utf-8")
    try:
        got = assignment_slots(probe)
    finally:
        probe.unlink(missing_ok=True)
        tmp.rmdir()
    return [
        # ⚑⚑ THE DISCRIMINATOR IS THAT ALL THREE NUMBERS DIFFER. `slots` counts every
        # binding, `stated` only the annotated one, `derivable` only the one a reader can
        # retire. A walk that returned the same number for all three — the shape the old
        # reader effectively had, at zero — passes no arm of this.
        (
            "assignment slots separate stated, derivable and neither",
            (got.slots, got.stated, got.derivable),
            (3, 1, 1),
        ),
        # ⚑ AND THE OWED LIST NAMES THE UNSTATED ONES, including the derivable one: a slot a
        # reader can type is still a slot `stubgen` writes `Incomplete` for, so it still
        # blocks eligibility. Conflating "derivable" with "stated" is the whole trap.
        (
            "the owed list names every UNSTATED assignment, derivable or not",
            sorted(got.owed),
            ["B", "C"],
        ),
    ]


if __name__ == "__main__":
    sys.exit(main(sys.argv))
