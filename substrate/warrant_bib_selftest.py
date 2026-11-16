#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.warrant_bib` — ENGINE-FREE, and that is the point of the file.

⚑⚑⚑ THIS SUITE MUST RUN WITHOUT PAPERKIT INSTALLED, because the module it tests must. A peer
measured that the whole `bibstruct` CLI was unreachable for a consumer without a paperkit venv:
the engine import sat at module scope in `warrant_bib`, three modules up a chain that runs at
load, so EVERY mode failed rather than one (gate-G209). The module split; this suite splits with
it, and the engine arms live in `warrant_records_selftest`.

⚑⚑ SO A CONSUMER WITHOUT THE ENGINE GETS A REAL VERDICT HERE RATHER THAN A COLLECTION ERROR.
That is the property this file exists to hold, and it is why nothing above imports paperkit — an
import here would reintroduce exactly the reachability defect the split repaired, in the suite
that is supposed to prove it repaired.

⚑⚑⚑ AND THE SPLIT DEADLOCKED BEFORE IT LANDED (gate-G210). The per-file gate runs mypy across the
whole package, so once the three functions moved, this suite's stale references became a
PACKAGE-WIDE error refusing every write in `substrate/` — including the rewrite of this file.
Deleting the suite did not clear it: `warrant_bib` then named a module that no longer existed, so
the block simply moved. What broke the cycle was making the delegation a RUNTIME lookup rather
than a type-checked import, after which both halves could land.

⚑⚑ `consumer_fields` AND `WarrantError` MOVED TO mtools (`mikemol.witness.warrant_bib`, W38), and
their cases went with them: the config-read, missing-config, malformed-config and
exception-not-exit arms are mtools' tests now. What stays here is what stays in this module — the
project's paths, and the engine-free property.
"""

from __future__ import annotations

import sys
from pathlib import Path

from substrate import warrant_bib


def the_module_needs_no_engine(out: list[str]) -> int:
    """Check this module reaches paperkit through nothing — the split's whole claim.

    ⚑⚑⚑ THE ARM THE SPLIT EXISTS FOR, and it asserts a NEGATIVE that a positive control makes
    meaningful: `warrant_bib`'s own source must not name the engine, while the engine half's
    source must. A case checking only the first would pass against a module that imports nothing
    at all, including the things it needs.
    """
    here = Path(warrant_bib.__file__)
    engine_half = here.parent / "warrant_records.py"
    if not engine_half.exists():
        out.append("selftest: warrant_records.py is absent — the engine half has no home")
        return 1

    # ⚑⚑⚑ THE STATEMENT, NOT THE STRING, AND A FALSE POSITIVE TAUGHT ME THE DIFFERENCE. A first
    # cut searched the source for `import paperkit` and FIRED — on this module's own docstring,
    # which mentions the phrase to explain why the import is not there. Use versus mention,
    # committed inside the probe written to catch a regression. An import is a top-level
    # STATEMENT, so the check reads statements: a mention in prose is not one.
    def imports_engine(path: Path) -> bool:
        """Report whether `path` has a module-scope import of the engine."""
        return any(
            line.startswith(("import paperkit", "from paperkit"))
            for line in path.read_text(encoding="utf-8").splitlines()
        )

    if imports_engine(here):
        out.append("selftest: warrant_bib imports the engine — the split has regressed")
        return 1
    # ⚑ THE POSITIVE CONTROL: the engine half DOES import it, so the check above is reading
    # statements rather than always answering no.
    if not imports_engine(engine_half):
        out.append("selftest: warrant_records does not import the engine — the probe is blind")
        return 1
    return 0


def the_paths_derive_from_the_corpus_root(out: list[str]) -> int:
    """Check BIB and CONFIG come from the corpus root, not this file's location.

    ⚑ THE MODULE MOVED TO `substrate/` WHILE THE BIB STAYED WITH THE WORKLIST, which is the drift
    the constants' own comment records. A path derived from `__file__` would have followed the
    module and pointed at nothing.
    """
    if warrant_bib.BIB.parent != warrant_bib.PROJECT:
        out.append(f"selftest: BIB is not under the project: {warrant_bib.BIB}")
        return 1
    if warrant_bib.CONFIG.parent != warrant_bib.PROJECT:
        out.append(f"selftest: CONFIG is not under the project: {warrant_bib.CONFIG}")
        return 1
    return 0


def speak_names_the_engine_half(out: list[str]) -> int:
    """Check the module's own description points at where the engine half went.

    ⚑ A READER ARRIVING AT THE SMALLER MODULE MUST NOT CONCLUDE THE CAPABILITY IS GONE. The split
    removed three functions from this file, and a description that did not name their new home
    would turn a move into an apparent deletion.
    """
    if "warrant_records" not in warrant_bib.speak():
        out.append("selftest: speak() does not name the engine half")
        return 1
    return 0


_ARMS = (
    the_module_needs_no_engine,
    the_paths_derive_from_the_corpus_root,
    speak_names_the_engine_half,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"warrant-bib selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"warrant-bib selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
