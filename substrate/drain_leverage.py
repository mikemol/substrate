#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Rank a drain by the `sys.path` surgery it RETIRES, not by the findings it carries.

⚑⚑⚑ THE RANKING METRIC WAS THE DEFECT. A drain queue ordered by per-file finding count answers
*which file is cheapest to rewrite*, and the arc's actual goal is *stop mutating `sys.path`* — so
the cheap file may retire nothing while an expensive one retires a cluster. `adopter_import
--reach-back` ranks by CONSUMER COUNT, which is closer and still not the question: a name with
twenty consumers retires nothing if every one of those consumers holds the same insert for a
SECOND unpackaged name it also imports. Neither existing reader can see that, because neither
joins the insert to the names it enables.

⚑⚑ AN INSERT IS RETIRED ONLY WHEN EVERY BARE NAME IT SERVES IS GONE, AND THAT IS THE WHOLE JOIN.
MEASURED on the live tree at `scripts/check_ban_ratchet.py`: two inserts (`scripts/`, `scratch/`)
serving three bare names (`ratchet`, `_agdatext`, `agda_lex`). Draining `_agdatext` alone retires
NEITHER — `ratchet` still needs the first and `agda_lex` the second. A consumer-count ranking
scores that drain 21; this reader scores the insert it retires there at zero, and both numbers are
correct about different questions.

⚑⚑⚑ SO THE TWO READINGS ARE REPORTED SEPARATELY AND NEVER SUMMED. `retired` is the insert a drain
finishes off by itself; `contested` is one it reduces but leaves standing because a sibling name
holds it. Collapsing them into a single "inserts affected" score is the scalar collapse that made
the finding-count order look authoritative in the first place — it would let a name that merely
touches many inserts outrank one that actually finishes several.

⚑⚑ THE BLIND SPOT IS STATED BY THE INSTRUMENT, NOT LEFT TO THE READER. A `contested` insert names
the SIBLING names blocking it, so *"drain this and the insert survives"* arrives with the list of
what else must go — which is the co-drain, and the reason a transitive estimate that assumed a
single blocker would overcount. This is `--reach-back`'s recorded undercount (a module blocked on
`_agdatext` never reaches its `ratchet` line) seen from the other side: there, a blocked consumer
hides its later dependencies; here, a surviving insert names them.

⚑ THE INSERTS ARE READ STATICALLY, AND THAT IS A DIFFERENT POPULATION FROM `import_effects`.
That reader executes the import and reports the paths a module ACTUALLY added, so it sees an
insert built by a helper or a loop and cannot say which name the insert was for. `insert_read`
reads the `sys.path` call and the bare imports in one AST walk, so it can attribute — at the cost
of missing any insert not spelled statically. The two disagree legitimately; `unreadable` names
the shapes the static reader cannot resolve so a zero here is never read as an absence.

⚑ A NAME IS `bare` HERE IN `module_importers`' SENSE, and the vocabulary is deliberately shared
rather than respelled. A bare site resolves only under an insert and fails for an adopter; a
dotted site travels. Two spellings of that distinction in one toolkit is how a census ends up
answering about the method.

⚑⚑ AND THE READING NOW LIVES IN `insert_read`, WHICH IS WHY THE ATTRIBUTION IMPROVED. This module
held the mutation detector, the target resolver, the bare-import reader, the join, the ranking and
the CLI. Wiring a better resolver in needed an import AND a use — two hunks in one write — and the
refusal was the size signal: the reading was one job living inside another. Moved out, the
resolver gained the binding hop that `sys.path.insert(0, HERE)` needs, and this module kept the
question it actually owns.

⚑⚑⚑ AND `--kinds` ANSWERS THE QUESTION THE RANKING CANNOT. Three successive resolver improvements
recovered a large share of the previously unattributable inserts and moved the ordering NOT AT
ALL — the same names lead by the same margins. That stability is the finding: the ranking is
robust, and what it lacks is not precision but a SPLIT. Its top rows are third-party
distributions reached by path surgery, which no drain retires and installing does. `insert_kind`
partitions the population so an operator reads two queues with different fixes rather than one
list with a misleading head.
"""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast

from mikemol.corpus import tree_root

from substrate import corpus, insert_kind, insert_read
from substrate.insert_read import OPAQUE, Insert

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True, slots=True)
class Consumer:
    """One file's path surgery and the bare names it thereby reaches.

    ⚑ THE TWO LISTS ARE HELD TOGETHER BECAUSE THE JOIN IS BETWEEN THEM. A file's inserts alone
    say how much surgery it does; its bare names alone say what it depends on. Only the pair
    answers whether draining one name lets one insert go.
    """

    path: str
    inserts: tuple[Insert, ...]
    bare: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Leverage:
    """What draining one unpackaged name would retire, and what it would leave standing."""

    name: str
    consumers: tuple[str, ...]
    retired: tuple[Insert, ...]
    contested: tuple[tuple[Insert, tuple[str, ...]], ...]

    @property
    def blockers(self) -> tuple[str, ...]:
        """Return every sibling name holding a contested insert open — the co-drain."""
        return tuple(sorted({n for _i, names in self.contested for n in names}))


def consumer(path: Path, label: str, root: Path | None = None) -> Consumer | None:
    """Read one file's inserts and bare imports, or None when it does not parse.

    ⚑ `root` LETS THE TARGET RESOLVER TAKE ITS FOURTH RUNG (gate-F90). An insert whose target
    is an attribute on an imported module — `sys.path.insert(0, wg_engine.LIBRARY)` — is
    nameable only by parsing the module that binds the constant, which needs a tree to look
    in. Without it the answer is exactly what it was before, so a caller that has not opted
    in is not silently given a different verdict.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=label)
    except (OSError, SyntaxError, ValueError):
        return None
    return Consumer(label, insert_read.inserts(tree, label, root), insert_read.bare_names(tree))


def population(root: Path | None = None) -> tuple[tuple[Path, str], ...]:
    """Return the corpus to scan, as `(path, repo-relative label)` pairs.

    ⚑⚑ THE LABEL RAISED FROM A BORROWING CHECKOUT (gate-G245 / gate-G249 / gate-G252).
    `Path.relative_to` demands the path lie under `where`, and `corpus.resolve_root` resolves
    the caller's CWD FIRST — so a peer running this from their own tree walked THEIR files and
    measured them against SUBSTRATE's root. `tree_root.of(where).label` carries one root and
    does both, so the tree that was walked is the tree that labels.
    """
    where = root if root is not None else corpus.ROOT
    tree = tree_root.of(where)
    return tuple((Path(p), tree.label(p)) for p in corpus.py_files(root=where))


def consumers(files: Iterable[tuple[Path, str]], root: Path | None = None) -> tuple[Consumer, ...]:
    """Return every file that both mutates `sys.path` and imports something bare."""
    out = [consumer(p, label, root) for p, label in files]
    return tuple(c for c in out if c is not None and c.inserts and c.bare)


def leverage(name: str, found: tuple[Consumer, ...], known: frozenset[str]) -> Leverage:
    """Return what draining `name` retires across `found`.

    ⚑⚑ AN INSERT IS RETIRED ONLY IF NO OTHER CANDIDATE NAME IN THE SAME FILE SURVIVES IT. This is
    the join the two existing readers cannot perform, and it is the difference between a drain
    that finishes a file's surgery and one that shortens it. The surviving names travel with the
    contested insert so the answer carries its own next step.

    ⚑ THE SIBLING TEST IS OVER CANDIDATE NAMES, NOT ALL BARE NAMES. A bare `import json` needs no
    insert, so counting it as a blocker would report every insert as permanently contested and
    make the whole ranking read zero — the false-negative twin of the finding-count order.
    """
    retired: list[Insert] = []
    contested: list[tuple[Insert, tuple[str, ...]]] = []
    who: list[str] = []
    for item in found:
        if name not in item.bare:
            continue
        who.append(item.path)
        others = tuple(sorted(n for n in item.bare if n != name and n in known))
        for ins in item.inserts:
            if others:
                contested.append((ins, others))
            else:
                retired.append(ins)
    return Leverage(name, tuple(sorted(who)), tuple(retired), tuple(contested))


def candidates(found: tuple[Consumer, ...]) -> frozenset[str]:
    """Return every bare name reached under an insert — the drain population.

    ⚑ DERIVED FROM THE CORPUS, NOT DECLARED. A hand-listed roster would go stale the first time a
    drain landed, and a ranking over a stale population reports its own list rather than the tree.
    """
    return frozenset(n for item in found for n in item.bare if n not in sys.stdlib_module_names)


def ranked(found: tuple[Consumer, ...]) -> tuple[Leverage, ...]:
    """Rank every candidate name by inserts RETIRED, then by contested, then by name."""
    known = candidates(found)
    rows = [leverage(name, found, known) for name in sorted(known)]
    live = [r for r in rows if r.consumers]
    live.sort(key=lambda r: (-len(r.retired), -len(r.contested), r.name))
    return tuple(live)


def unreadable(found: tuple[Consumer, ...]) -> tuple[str, ...]:
    """Return the insert sites whose target this reader could not name.

    ⚑ THE ZERO MUST CARRY ITS BOUNDARY. An insert built from an expression the resolver cannot
    follow is invisible to the attribution above, so a name scoring zero retired inserts may
    simply hold one this reader could not read. Reported rather than dropped.
    """
    return tuple(
        sorted(
            f"{OPAQUE}: {i.path}:{i.line} adds a path this reader cannot name"
            for item in found
            for i in item.inserts
            if not i.resolved
        )
    )


def render(
    rows: tuple[Leverage, ...], found: tuple[Consumer, ...], blind: tuple[str, ...], limit: int
) -> str:
    """Render the ranking, with retired and contested kept apart.

    ⚑⚑ THE CONTESTED COLUMN PRINTS BY DEFAULT. A ranking showing only what a drain retires reads
    as a promise; the same row showing what it leaves standing is the one an operator can plan
    with, and putting that behind a flag means the optimistic half is the half that gets banked.
    """
    total = sum(len(c.inserts) for c in found)
    head = (
        f"{len(rows)} drain candidate(s) over {total} `sys.path` insert(s) in {len(found)} file(s)"
    )
    out = [head]
    for row in rows[:limit]:
        out.append(
            f"  {row.name:<28} retires {len(row.retired):>2}  "
            f"contested {len(row.contested):>2}  "
            f"consumers {len(row.consumers):>2}"
        )
        if row.blockers:
            out.append(f"      co-drain: {', '.join(row.blockers)}")
    if blind:
        out.append(
            f"   ⚑ {len(blind)} insert(s) this reader CANNOT attribute — a zero above "
            f"is not yet an absence:"
        )
        out.extend(f"     {b}" for b in blind)
    return "\n".join(out)


def render_kinds(found: tuple[Consumer, ...]) -> str:
    """Render the candidate population split by the KIND of problem each name is.

    ⚑⚑ THE RANKING'S TOP ROWS ARE INSTALL PROBLEMS, AND THAT IS WHY THIS MODE EXISTS. The
    third-party distributions lead the retire-count order, and no drain retires any of them —
    installing them does, after which the insert is redundant. One queue holding both kinds
    means the first thing an operator reads is the chore that belongs to dependency declaration
    rather than to module ownership.

    ⚑ THE TWO ARE PRINTED AS SEPARATE QUEUES, NEVER SUMMED. A total over both is the scalar
    collapse this module's header already refuses for retired-versus-contested: it would let a
    long install list make the drain queue look like progress.
    """
    names = sorted({n for item in found for n in item.bare})
    grouped = insert_kind.partition(names, corpus.ROOT)
    out = [f"{len(names)} bare name(s) reached under an insert, split by KIND"]
    for kind in (insert_kind.DRAIN, insert_kind.INSTALL, insert_kind.STDLIB):
        rows = grouped[kind]
        out.append(f"  {kind:<9} {len(rows):>4}")
        if rows:
            out.append(f"      {', '.join(rows)}")
    out.append(
        "   ⚑ an INSTALL name is a dependency-declaration chore, not a drain: the insert "
        "goes away when the import resolves normally."
    )
    out.append(
        "   ⚑ a name DECLARED but not installed here reads as DRAIN — this reader cannot "
        "tell it from an own-tree module, and over-reports rather than under-reports."
    )
    return "\n".join(out)


def probe(source: str, label: str = "probe.py") -> Consumer:
    """Resolve one source string into a consumer — the fixture the cases share.

    ⚑ THE LABEL IS A PARAMETER BECAUSE IT IS AN INPUT TO THE ANSWER, not decoration. A
    `__file__`-relative insert resolves against the importing file's own path, so a fixture that
    could not vary the label could not exercise that arm at all — and the arm it could not
    exercise is the one whose absence made the first ranking unusable.
    """
    tree = ast.parse(source, filename=label)
    return Consumer(label, insert_read.inserts(tree, label), insert_read.bare_names(tree))


def main(argv: list[str]) -> int:
    """Print the drain ranking by `sys.path` inserts retired."""
    parser = argparse.ArgumentParser(
        description="rank drain candidates by the path surgery each one retires"
    )
    parser.add_argument("--top", type=int, default=20, help="how many rows to print")
    parser.add_argument("--name", help="report one candidate in full")
    parser.add_argument(
        "--kinds",
        action="store_true",
        help="split the population into install-reach and drain-reach",
    )
    namespace = parser.parse_args(argv)
    top = cast("int", namespace.top)
    one = cast("str | None", namespace.name)
    kinds = cast("bool", namespace.kinds)
    # ⚑ THE ROOT IS PASSED SO THE FOURTH RUNG CAN FIRE (gate-F90). `population` already
    # resolves it and then discarded it, so the resolver had no tree to find a binding
    # module in and every imported-constant target reported opaque.
    found = consumers(population(), corpus.ROOT)
    if kinds:
        sys.stdout.write(render_kinds(found) + "\n")
        return 0
    rows = ranked(found)
    if one is not None:
        rows = tuple(r for r in rows if r.name == one)
        if not rows:
            sys.stderr.write(f"{one}: not a bare name reached under an insert in this corpus\n")
            return 2
    sys.stdout.write(render(rows, found, unreadable(found), top) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
