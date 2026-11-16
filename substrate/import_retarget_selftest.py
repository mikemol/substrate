# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Cases for `import_retarget` — the hoist, the removal, and what must be left alone.

⚑⚑ THE LOAD-BEARING CASE IS THE DEFERRED LINE AND ITS COMMENT. The tool exists because a
consumer imports the twin INSIDE a function, behind a trailing comment justifying the deferral;
the case asserts both the import and its comment leave together, and that exactly one top-level
import arrives however many sites there were.

⚑ THE CONTROLS: a sibling name on the same import line stays; an import of the name from a
DIFFERENT package is untouched; a file with no such import is returned byte-identical.
"""

from __future__ import annotations

import sys

from substrate import import_retarget

_OLD = "substrate"
_NEW = "mikemol.corpus"

_DEFERRED = '''"""Doc."""

from __future__ import annotations

import os


def f() -> str:
    """F."""
    from substrate import tree_root  # the deferral's reason

    return tree_root.of(os.getcwd()).label
'''

_SHARED = "from substrate import corpus, tree_root\n\nx = tree_root\ny = corpus\n"

_OTHER = "from elsewhere import tree_root\n\nx = tree_root\n"

_TWICE = (
    "from substrate import tree_root\n\n\n"
    "def g() -> None:\n"
    "    from substrate import tree_root\n\n"
    "    del tree_root\n"
)

_ALIASED = "from substrate import tree_root as tr\n\nx = tr\n"

# How many sites the twice-imported fixture carries: one top-level, one deferred.
_TWO_SITES = 2


def _cases() -> list[tuple[str, bool]]:
    """Return every case."""
    deferred, moved = import_retarget.retarget(_DEFERRED, _OLD, "tree_root", _NEW)
    shared, _ = import_retarget.retarget(_SHARED, _OLD, "tree_root", _NEW)
    other, other_moved = import_retarget.retarget(_OTHER, _OLD, "tree_root", _NEW)
    twice, twice_moved = import_retarget.retarget(_TWICE, _OLD, "tree_root", _NEW)
    aliased, _ = import_retarget.retarget(_ALIASED, _OLD, "tree_root", _NEW)
    return [
        ("a deferred import is moved", moved == 1),
        ("the deferred line is gone", "from substrate import tree_root" not in deferred),
        ("its trailing comment went with it", "the deferral's reason" not in deferred),
        ("the new import is top-level", "\nfrom mikemol.corpus import tree_root\n" in deferred),
        ("a sibling on the same line stays", "from substrate import corpus\n" in shared),
        ("an import from another package is untouched", other == _OTHER and other_moved == 0),
        ("two sites give one new import", twice.count("from mikemol.corpus") == 1),
        ("both sites are counted", twice_moved == _TWO_SITES),
        ("an alias survives the move", "from mikemol.corpus import tree_root as tr" in aliased),
        ("a wrong arity is refused", import_retarget.main(["ir"]) == import_retarget.USAGE_EXIT),
    ]


def main(argv: list[str]) -> int:
    """Run every case; exit 1 if any failed. Refuses any argument but `--selftest`."""
    if argv[1:] not in ([], ["--selftest"]):
        sys.stderr.write("import_retarget_selftest: takes no argument but --selftest\n")
        return import_retarget.USAGE_EXIT
    cases = _cases()
    failed = [name for name, ok in cases if not ok]
    for name in failed:
        sys.stdout.write(f"  FAIL  {name}\n")
    sys.stdout.write(f"import-retarget selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE: its predicate needs an entry point AND
# the `--selftest` literal, and a suite without it is written, green, and run by nothing.
if __name__ == "__main__":
    sys.exit(main(sys.argv))
