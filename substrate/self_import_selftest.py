#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.self_import` — the 2-cycle reader, and the false zeros it corrects.

⚑⚑⚑ THE POSITIVE CONTROL IS THE LOAD-BEARING CASE, BECAUSE THE NAIVE READER PASSES EVERY OTHER
ONE. `import_edges` truncates a name to its top-level package, so under it every file in
`substrate/` imports `substrate` and EVERY PAIR IS A CYCLE. A reader built on the truncated
reading would report a complete graph and satisfy any case that only asks *is the known pair
found*. The acyclic fixture is what tells a discriminating reader from one that waves the whole
population through.

⚑⚑ AND THE OTHER DIRECTION IS THE ONE THAT WAS MEASURED IN THE TREE. Three probes read 0 for a
trailer import because it sits inside `if __name__ == "__main__"` — a fact about where they look,
reported as a fact about the substrate. A case asserts the trailer shape specifically, so a
regression to module-scope-only reading fails loudly instead of shrinking a green number.

⚑⚑⚑ AND THE ANY-LENGTH WALK HAS ITS OWN POSITIVE CONTROL, THE DIAMOND, FOR THE SAME REASON.
A cycle finder that fires whenever it re-reaches a node it has already SEEN passes every arm
below except that one — and a DAG of any width is full of diamonds, so it would report the
whole corpus as tangled. Verified by mutation: relaxing the back-edge test to include finished
nodes makes `a_diamond_is_not_a_cycle` the failing arm.

⚑⚑ A THIRD FALSE ZERO WAS MEASURED DURING THE WIDENING AND IS NOW AN ARM. Matching only
repo-frame dotted names read `scratch/` as 507 modules and ZERO edges, printing a confident
`0 cycles` over a tree whose own source prose names its strongly-connected component. Script
trees import siblings by BARE NAME, resolved against the importing file's directory. What
caught it was the census printing its denominator — `0 over 0 edges` and `0 over 436 edges`
are different facts and a cycle count alone cannot separate them.

⚑ THE FIXTURES ARE WRITTEN SOURCE, NOT THE LIVE TREE. A case reading `substrate/` measures the
tree's current cycle population and would go green — or red — the moment an unrelated module
gained or lost a trailer. It would report the corpus rather than the reader.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import self_import

# `a` carries the convention's trailer: the import of its suite is inside `__main__`.
_TRAILER = '''"""A module with a selftest trailer."""
if __name__ == "__main__":
    from substrate import a_selftest
    raise SystemExit(a_selftest.selftest())
'''

_TRAILER_SUITE = '''"""The suite for `a`."""
from substrate import a


def selftest() -> int:
    """Exercise `a`."""
    return 0 if a else 0
'''

# Two modules that reach each other at module scope and are NOT a suite pair.
_PLAIN_ONE = '''"""One half of a non-trailer tangle."""
from substrate import two
'''

_PLAIN_TWO = '''"""The other half."""
from substrate import one
'''

# A strict DAG: `leaf` imports nothing, `stem` imports `leaf`.
_LEAF = '"""A leaf."""\n'

_STEM = '''"""Imports the leaf and nothing else."""
from substrate import leaf
'''

# `from substrate import NOT_A_MODULE` names an ATTRIBUTE, not a module.
_ATTR = '''"""Imports a name that is not a module."""
from substrate import NOT_A_MODULE
'''

_ATTR_BACK = '''"""Imports the attribute-importer back."""
from substrate import attr
'''

# A function-local import: deferred, but it still closes the loop for a static gate.
_DEFERRED = '''"""Reaches the other half only when called."""


def go() -> int:
    """Import late."""
    from substrate import two
    return len(dir(two))
'''


def _cycles(where: str, files: dict[str, str]) -> tuple[self_import.Cycle, ...]:
    """Write a fixture package and read its 2-cycles back."""
    pkg = Path(where) / self_import.PACKAGE
    pkg.mkdir(exist_ok=True)
    for stem, text in files.items():
        (pkg / f"{stem}.py").write_text(text, encoding="utf-8")
    return self_import.cycles(str(pkg))


def a_trailer_import_inside_main_is_seen(out: list[str]) -> int:
    """Check the `if __name__` trailer closes the cycle.

    ⚑⚑ THIS IS THE MEASURED FALSE ZERO. `--importers`, `--binding` and a literal search each
    read 0 here because they key on module-scope spellings or on strings. A reader that lost
    the `ast.If` descent would report the deadlocking population as empty — and an empty census
    reads as a solved problem.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _cycles(where, {"a": _TRAILER, "a_selftest": _TRAILER_SUITE})
    if len(got) != 1 or not got[0].is_suite_pair:
        out.append(f"selftest: the trailer pair read {got!r}")
        return 1
    return 0


def an_acyclic_package_reports_no_cycle(out: list[str]) -> int:
    """Check a DAG yields nothing — the POSITIVE CONTROL.

    ⚑⚑⚑ WITHOUT THIS, A READER BUILT ON TRUNCATED NAMES PASSES EVERYTHING ELSE. Under
    `import_edges.module_level`, `from substrate import leaf` binds `substrate`, so `stem` and
    `leaf` would each "import" the package and read as a cycle. The whole reason
    `module_level_dotted` exists is the case this arm fails without it.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _cycles(where, {"leaf": _LEAF, "stem": _STEM})
    if got != ():
        out.append(f"selftest: an acyclic package reported cycles: {got!r}")
        return 1
    return 0


def a_non_trailer_cycle_is_reported_separately(out: list[str]) -> int:
    """Check a mutual pair that is not a module/suite pair is distinguished.

    ⚑ THE INTERESTING POPULATION. Folding it in with the trailer pairs would bury an
    unexplained tangle inside expected debt that has a scheduled retirement — the count would
    go down when the port lands and the tangle would still be there.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _cycles(where, {"one": _PLAIN_ONE, "two": _PLAIN_TWO})
    if len(got) != 1 or got[0].is_suite_pair or not got[0].eager:
        out.append(f"selftest: the non-trailer cycle read {got!r}")
        return 1
    return 0


def an_imported_attribute_is_not_an_edge(out: list[str]) -> int:
    """Check `from X import <attribute>` does not manufacture a module edge.

    ⚑ `from X import Y` IS AMBIGUOUS IN THE AST. Accepting every candidate would invent edges
    to names that are constants and functions — a census with more rows than the substrate has
    modules, every extra row looking exactly like a real one.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _cycles(where, {"attr": _ATTR, "attr_back": _ATTR_BACK})
    if got != ():
        out.append(f"selftest: an attribute import was read as a module edge: {got!r}")
        return 1
    return 0


def a_pair_is_emitted_once(out: list[str]) -> int:
    """Check a mutual edge yields one row, not one per direction.

    ⚑ A CENSUS THAT DOUBLES ITS OWN POPULATION overstates the work twofold, and the number is
    the thing a retirement plan is sized against.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _cycles(where, {"one": _PLAIN_ONE, "two": _PLAIN_TWO})
    if len(got) != 1 or got[0].low != f"{self_import.PACKAGE}.one":
        out.append(f"selftest: the pair was not emitted once, low-first: {got!r}")
        return 1
    return 0


def a_deferred_import_still_closes_the_loop(out: list[str]) -> int:
    """Check a function-local import counts, and is marked as not-eager.

    ⚑ THE GATE READS IMPORTS STATICALLY, so a deferred edge deadlocks exactly like a trailer —
    the opposite of the reading `import_edges` takes for store reachability. Reporting only
    eager edges would call a deadlocking pair acyclic.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _cycles(where, {"one": _DEFERRED, "two": _PLAIN_TWO})
    if len(got) != 1 or got[0].eager:
        out.append(f"selftest: the deferred edge read {got!r}")
        return 1
    return 0


def an_empty_census_says_so(out: list[str]) -> int:
    """Check the render names its own emptiness rather than printing nothing.

    ⚑ SILENCE AND SUCCESS ARE THE SAME BYTES — the false-zero shape every census in this tree
    prints its denominator to avoid.
    """
    if "no 2-cycle" not in self_import.render(()):
        out.append("selftest: an empty census does not name its emptiness")
        return 1
    return 0


def the_render_states_both_populations(out: list[str]) -> int:
    """Check trailer pairs and other cycles are both counted in the output.

    ⚑ ONE NUMBER OVER BOTH is how the second population disappears. The render must let a
    reader see that the interesting count is zero — or that it is not.
    """
    rows = (
        self_import.Cycle(low="substrate.a", high="substrate.a_selftest", eager=False),
        self_import.Cycle(low="substrate.one", high="substrate.two", eager=True),
    )
    text = self_import.render(rows)
    missing = [
        word
        for word in ("2-cycle(s)", "trailer pairs", "OTHER", "substrate.one <-> substrate.two")
        if word not in text
    ]
    if missing:
        out.append(f"selftest: the render omits {missing!r}:\n{text}")
        return 1
    return 0


# A diamond: `top` reaches `sink` two ways. ⚑ NOT A CYCLE, and the shape that separates a
# real cycle finder from one that fires on any re-visited node.
_DIAMOND_TOP = '''"""Reaches the sink two ways."""
from substrate import left
from substrate import right
'''

_DIAMOND_LEFT = '"""One route."""\nfrom substrate import sink\n'
_DIAMOND_RIGHT = '"""The other route."""\nfrom substrate import sink\n'
_DIAMOND_SINK = '"""A sink."""\n'

# A 3-cycle: cee → bee → ay → cee, written so alphabetical order is NOT cycle order.
_THREE_AY = '"""First."""\nfrom substrate import cee\n'
_THREE_BEE = '"""Second."""\nfrom substrate import ay\n'
_THREE_CEE = '"""Third."""\nfrom substrate import bee\n'

# A bare sibling import — the spelling `scratch/` uses, resolved by DIRECTORY not package.
_BARE_ONE = '"""Imports a sibling by bare name."""\nimport two\n'
_BARE_TWO = '"""Imports the first back by bare name."""\nimport one\n'


def _loops(where: str, files: dict[str, str]) -> tuple[tuple[str, ...], ...]:
    """Write a fixture package and read its any-length cycles back."""
    pkg = Path(where) / self_import.PACKAGE
    pkg.mkdir(exist_ok=True)
    for stem, text in files.items():
        (pkg / f"{stem}.py").write_text(text, encoding="utf-8")
    return self_import.loops(str(pkg))


def a_three_cycle_is_found(out: list[str]) -> int:
    """Check `A → B → C → A` is reported, which the pair reader called zero.

    ⚑⚑⚑ THE WHOLE SUBJECT OF THE EXTENSION. A 3-cycle deadlocks the per-file gate exactly as a
    trailer pair does — all three files become unwritable together and deleting a member leaves
    the survivors importing nothing — and the length-2 census printed `0` for it. A census
    narrower than the defect it sizes reads as a solved problem.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _loops(where, {"ay": _THREE_AY, "bee": _THREE_BEE, "cee": _THREE_CEE})
    want = (f"{self_import.PACKAGE}.ay", f"{self_import.PACKAGE}.cee", f"{self_import.PACKAGE}.bee")
    if got != (want,):
        out.append(f"selftest: the 3-cycle read {got!r}, wanted {want!r}")
        return 1
    return 0


def a_diamond_is_not_a_cycle(out: list[str]) -> int:
    """Check a DAG with two routes to one sink reports nothing — the POSITIVE CONTROL.

    ⚑⚑⚑ A LONGER-CYCLE FINDER THAT REPORTED EVERY PATH AS A CYCLE PASSES EVERY OTHER ARM. The
    naive walk fires whenever it re-reaches a node it has seen, and a diamond re-reaches `sink`
    on the second route — so it would call this acyclic fixture a cycle, and a DAG of any width
    is full of diamonds. The discriminator is membership of the CURRENT STACK, not of the
    visited set, and this fixture is the only case that can tell those apart.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _loops(
            where,
            {
                "top": _DIAMOND_TOP,
                "left": _DIAMOND_LEFT,
                "right": _DIAMOND_RIGHT,
                "sink": _DIAMOND_SINK,
            },
        )
    if got != ():
        out.append(f"selftest: a diamond was read as a cycle: {got!r}")
        return 1
    return 0


def one_loop_is_reported_once(out: list[str]) -> int:
    """Check a 3-cycle yields one row, not one per starting point.

    ⚑ A CYCLE IS A LOOP, NOT A LIST. A walk entered from each member finds `(A,B,C)`,
    `(B,C,A)` and `(C,A,B)` — three rows for one defect, sizing a retirement plan at N times
    the work. `rotate` canonicalises by starting at the lowest member.
    """
    got = {
        self_import.rotate(("c", "a", "b")),
        self_import.rotate(("a", "b", "c")),
        self_import.rotate(("b", "c", "a")),
    }
    if got != {("a", "b", "c")}:
        out.append(f"selftest: rotations were not identified: {got!r}")
        return 1
    return 0


def a_rotation_keeps_the_edge_direction(out: list[str]) -> int:
    """Check canonicalisation rotates rather than sorts.

    ⚑ SORTING THE MEMBERS WOULD ERASE THE DIRECTION, and the edge order is what tells a reader
    WHICH import to cut. `A → C → B → A` and `A → B → C → A` are different tangles that sort
    to the same row.
    """
    if self_import.rotate(("b", "a", "c")) != ("a", "c", "b"):
        out.append(f"selftest: rotate sorted instead: {self_import.rotate(('b', 'a', 'c'))!r}")
        return 1
    return 0


def a_bare_sibling_import_is_an_edge(out: list[str]) -> int:
    """Check `import two` beside `two.py` resolves — the spelling `scratch/` uses.

    ⚑⚑⚑ THIS WAS A MEASURED FALSE ZERO OF THE WIDENED READER, CAUGHT BY ITS OWN DENOMINATOR.
    Matching only repo-frame dotted names read `scratch/` as 507 modules with ZERO edges and
    printed a confident `0 cycles` — over the tree whose own source prose says *"the cycle is
    what places these in the core"*. Script-style trees import siblings by bare name, and
    resolution against the importing file's directory is what makes them visible.
    """
    with tempfile.TemporaryDirectory() as where:
        got = _cycles(where, {"one": _BARE_ONE, "two": _BARE_TWO})
    if len(got) != 1 or not got[0].eager:
        out.append(f"selftest: the bare sibling pair read {got!r}")
        return 1
    return 0


def a_bare_name_does_not_reach_another_directory(out: list[str]) -> int:
    """Check bare-name resolution is scoped per directory.

    ⚑ A FLAT BARE-NAME MAP WOULD INVENT EDGES BETWEEN FILES THAT CANNOT SEE EACH OTHER —
    `scratch/x.py`'s `import util` resolving to `jea/util.py`. That is the same invented-cycle
    failure the dotted naming exists to stop, reintroduced one layer down.
    """
    with tempfile.TemporaryDirectory() as where:
        pkg = Path(where) / self_import.PACKAGE
        pkg.mkdir(exist_ok=True)
        (pkg / "one.py").write_text(_BARE_ONE, encoding="utf-8")
        far = pkg / "far"
        far.mkdir(exist_ok=True)
        (far / "two.py").write_text(_BARE_TWO, encoding="utf-8")
        got = self_import.loops(str(pkg))
    if got != ():
        out.append(f"selftest: a bare name crossed a directory: {got!r}")
        return 1
    return 0


def a_dotted_name_keeps_its_subpackage(out: list[str]) -> int:
    """Check a nested file's name carries its directories.

    ⚑ THE ORIGINAL NAMING WAS A BARE STEM, WHICH IS ONLY CORRECT FOR A FLAT PACKAGE. Collapsing
    `jea/metalanguage/schema.py` to `schema` would merge it with every other `schema.py` in the
    corpus into one node — inventing cycles between files that never name each other.
    """
    got = self_import.dotted("/repo/jea/metalanguage/schema.py", Path("/repo"))
    if got != "jea.metalanguage.schema":
        out.append(f"selftest: the nested name read {got!r}")
        return 1
    return 0


def the_denominator_separates_absence_from_blindness(out: list[str]) -> int:
    """Check the census prints modules read AND edges resolved.

    ⚑⚑ `0 cycles` HAS TWO CAUSES AND NO PREDICATE SEPARATES THEM: the tree is acyclic, or the
    reader resolved no edges at all. Printing both counts is what made the bare-sibling blind
    spot visible instead of banking it as a green number.
    """
    with tempfile.TemporaryDirectory() as where:
        pkg = Path(where) / self_import.PACKAGE
        pkg.mkdir(exist_ok=True)
        (pkg / "stem.py").write_text(_STEM, encoding="utf-8")
        (pkg / "leaf.py").write_text(_LEAF, encoding="utf-8")
        text = self_import.denominator(str(pkg))
    if "2 module(s)" not in text or "1 intra-population edge(s)" not in text:
        out.append(f"selftest: the denominator read {text!r}")
        return 1
    return 0


def the_loop_render_states_both_lengths(out: list[str]) -> int:
    """Check the any-length render splits length-2 from longer.

    ⚑ ONE TOTAL BURIES THE INTERESTING ROW. Ten known trailer pairs plus one unexplained
    3-cycle printed as `11 cycle(s)` reads as the known debt growing by one.
    """
    text = self_import.render_loops((("a", "b"), ("c", "d", "e")))
    missing = [
        w for w in ("cycle(s) of any length", "LONGER THAN 2", "c → d → e → c") if w not in text
    ]
    if missing:
        out.append(f"selftest: the loop render omits {missing!r}:\n{text}")
        return 1
    return 0


_ARMS = (
    a_trailer_import_inside_main_is_seen,
    a_three_cycle_is_found,
    a_diamond_is_not_a_cycle,
    one_loop_is_reported_once,
    a_rotation_keeps_the_edge_direction,
    a_bare_sibling_import_is_an_edge,
    a_bare_name_does_not_reach_another_directory,
    a_dotted_name_keeps_its_subpackage,
    the_denominator_separates_absence_from_blindness,
    the_loop_render_states_both_lengths,
    an_acyclic_package_reports_no_cycle,
    a_non_trailer_cycle_is_reported_separately,
    an_imported_attribute_is_not_an_edge,
    a_pair_is_emitted_once,
    a_deferred_import_still_closes_the_loop,
    an_empty_census_says_so,
    the_render_states_both_populations,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"self-import selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"self-import selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
