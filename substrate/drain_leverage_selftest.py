#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases pinning the retired/contested join — the distinction the existing readers cannot make.

⚑⚑ EVERY CASE'S DISCRIMINATOR IS A READER THAT WOULD PASS A COUNT AND STILL BE WRONG. A reader
summing "inserts touched" passes the retired arm and fails the contested one; a reader treating
every bare name as a blocker passes the contested arm and reports the whole tree as zero. The pair
is what makes the join checkable rather than asserted.
"""

from __future__ import annotations

import sys

from substrate import drain_leverage

# The measured shape from `scripts/check_ban_ratchet.py`: two inserts, three bare candidate names,
# so NO single drain retires either insert. ⚑ THIS IS THE CASE THE RANKING EXISTS FOR.
_CONTESTED = (
    "import sys\n"
    "sys.path.insert(0, 'scripts')\n"
    "import ratchet\n"
    "import _agdatext\n"
    "sys.path.insert(0, 'scratch')\n"
    "import agda_lex\n"
)

# One insert serving exactly one bare name — the drain that actually finishes.
_SOLE = "import sys\nsys.path.insert(0, 'scratch')\nimport tsdbprobe\n"

# The dominant `scripts/` idiom, which carries NO string literal at all.
_SELF_DIR = (
    "import os, sys\n"
    "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
    "import ratchet\n"
)

# The same idiom climbing one level — a DIFFERENT directory, and the discriminator that stops a
# repo-root insert being attributed to the file's own package.
_PARENT_DIR = (
    "import os, sys\n"
    "sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\n"
    "import ratchet\n"
)


def _rank(source: str) -> tuple[drain_leverage.Leverage, ...]:
    """Rank the candidates in one probed source."""
    return drain_leverage.ranked((drain_leverage.probe(source),))


def _row(source: str, name: str) -> drain_leverage.Leverage:
    """Return one candidate's row from a probed source."""
    return next(r for r in _rank(source) if r.name == name)


def _cases() -> list[tuple[str, object, object]]:
    """Return the case roster."""
    sole = _row(_SOLE, "tsdbprobe")
    held = _row(_CONTESTED, "_agdatext")
    return [
        # ⚑ THE POSITIVE ARM: a lone bare name under an insert retires that insert outright.
        (
            "a name that is the insert's only candidate consumer RETIRES it",
            (len(sole.retired), len(sole.contested)),
            (1, 0),
        ),
        # ⚑⚑ THE ARM THAT OVERTURNS THE CONSUMER-COUNT ORDER. `_agdatext` has the most consumers
        # in the tree and retires NOTHING here, because `ratchet` and `agda_lex` hold both
        # inserts open. A reader summing touched inserts scores this 2 and is wrong.
        (
            "a name sharing its file with other candidates retires NOTHING",
            (len(held.retired), len(held.contested)),
            (0, 2),
        ),
        # ⚑ AND THE SURVIVING NAMES TRAVEL WITH THE ROW, so the answer carries its own co-drain
        # rather than leaving the reader to re-derive who is blocking. ⚑⚑ THE DRAINED NAME IS NOT
        # ITS OWN BLOCKER — this expectation was written wrong and the suite caught it. Listing
        # `_agdatext` among the names holding its own drain open would make every co-drain read
        # as one item longer than the work it names.
        (
            "a contested row names the SIBLINGS, never the drained name itself",
            held.blockers,
            ("agda_lex", "ratchet"),
        ),
        # ⚑⚑⚑ THE MEASURED FIRST-CUT DEFECT. `from scripts import ratchet` names the PACKAGE and
        # travels for an adopter, but its `node.module` is one dot-free word — so a reader
        # deciding on the word alone called it bare and put `scripts` into the drain population
        # as though a package were path debt. The discriminator is that `ratchet` (the module)
        # must NOT appear either: it is bound here through its package, needing no insert.
        (
            "a `from <package> import <mod>` is not bare in either name",
            [
                n
                for n in drain_leverage.probe(
                    "import sys\nsys.path.insert(0, 'x')\nfrom scripts import ratchet\n"
                ).bare
                if n != "sys"
            ],
            [],
        ),
        # ⚑ THE STDLIB FILTER LIVES IN `candidates`, NOT IN `_bare_names`, and this arm pins that
        # layering: the walk reports every dot-free import it sees, and the population narrows.
        # Asserting the filter at the walk would pass while the ranking still ranked `sys`.
        (
            "the walk reports dot-free stdlib names; the POPULATION is what excludes them",
            (
                "sys" in drain_leverage.probe(_SOLE).bare,
                "sys" in drain_leverage.candidates((drain_leverage.probe(_SOLE),)),
            ),
            (True, False),
        ),
        # ⚑ THE INSERT TARGET IS RESOLVED FROM THE LITERAL, so an unattributable one is admitted
        # rather than guessed — a well-formed wrong attribution reads as measurement.
        (
            "an insert built from a variable is UNRESOLVED, not attributed",
            [
                i.resolved
                for i in drain_leverage.probe(
                    "import sys\nsys.path.insert(0, HERE)\nimport ratchet\n"
                ).inserts
            ],
            [False],
        ),
        # ⚑ `append` IS THE SAME HAZARD AT THE OTHER END OF THE LIST and must be seen too.
        (
            "append is read as a mutation, not only insert",
            len(
                drain_leverage.probe(
                    "import sys\nsys.path.append('scratch')\nimport ratchet\n"
                ).inserts
            ),
            1,
        ),
        # ⚑⚑⚑ THE MEASURED BLIND SPOT. The dominant `scripts/` idiom carries NO string literal,
        # so a literal-only reader called it unattributable — 291 of 491 inserts, which made this
        # module's FIRST ranking a fact about the method rather than about the tree. It names the
        # file's OWN directory, and the label already carries that.
        (
            "a `__file__`-relative insert resolves to the file's own directory",
            [
                i.target
                for i in drain_leverage.probe(_SELF_DIR, "scripts/check_ban_ratchet.py").inserts
            ],
            ["scripts"],
        ),
        # ⚑ AND A DOUBLED `dirname` IS THE PARENT, NOT THE SAME DIRECTORY — the discriminator that
        # stops a repo-root insert being attributed to `scripts/`. A reader ignoring the nesting
        # depth passes the arm above and mislabels every root insert in the tree.
        (
            "a doubled dirname climbs to the parent, not the file's own directory",
            [
                i.target
                for i in drain_leverage.probe(_PARENT_DIR, "jea/metalanguage/store.py").inserts
            ],
            ["jea"],
        ),
    ]


def _selftest() -> int:
    """Run the roster."""
    cases = _cases()
    bad = [(n, g, w) for n, g, w in cases if g != w]
    for n, g, w in bad:
        sys.stdout.write(f"  FAIL {n}\n       got {g!r} want {w!r}\n")
    sys.stdout.write(f"drain_leverage selftest: {len(cases) - len(bad)}/{len(cases)}\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(_selftest())
