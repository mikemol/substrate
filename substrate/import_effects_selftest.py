#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.import_effects` — a probe that reports nothing is not a probe.

⚑⚑⚑ THE POSITIVE CONTROL IS THE WHOLE POINT, because this reader's headline result is a NEGATIVE
one: it swept an installed distribution and found no import-time side effects. A reader that
cannot detect an effect would report exactly the same thing, and the two are indistinguishable
from the output alone. That is the census-green defect this repo has banked twice — a zero that
describes the instrument being read as a fact about the substrate.

⚑⚑ SO EVERY ARM IS PAIRED AGAINST A SPECIMEN BUILT TO HAVE THE EFFECT. Each of the four axes gets
a module written for the occasion that provably exercises it, plus an inert control, plus an
explicit check that the two answers DIFFER. A suite asserting only "the inert module is inert"
would pass with a probe hard-wired to return nothing at all.

⚑ THE SPECIMENS ARE WRITTEN INTO A TEMPORARY DIRECTORY AND IMPORTED FROM THERE, never committed
into the tree. A committed fixture that writes at import is a hazard to every reader that sweeps
the package — including `adopter_import`, whose population is exactly this directory.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import import_effects

# The path the `sys.path` specimen prepends. ⚑ DELIBERATELY NOT UNDER A TEMP ROOT: a real
# temp-directory path would make this arm indistinguishable from the specimen's own home, and a
# `/tmp` literal is refused here as an insecure fixed temp path. A name that exists nowhere is
# both unambiguous and inert.
_SENTINEL_PATH = "/nonexistent-substrate-import-effects-sentinel"

# A module whose import writes a file — the effect originally alleged, and the one the report that
# commissioned this reader attributed to a module that does not do it.
_WRITER = "with open('sentinel.txt', 'w') as fh:\n    fh.write('x')\n"

# A module whose import prepends to `sys.path` — the SHADOWING mechanism. ⚑ This is the axis the
# original report described and no instrument measured; a module doing this corrupts every LATER
# import in the process, which is why an exception-typed probe cannot see it.
_PATHER = f"import sys\nsys.path.insert(0, {_SENTINEL_PATH!r})\n"

# A module whose import leaves a foreign name in `sys.modules`.
_MODDER = "import sys, types\nsys.modules['a_foreign_name'] = types.ModuleType('a_foreign_name')\n"

# A module whose import spawns a subprocess — an unbounded effect no static reader can follow.
_SPAWNER = "import subprocess, sys\nsubprocess.run([sys.executable, '-c', 'pass'], check=False)\n"

# A module whose import does nothing at all — the control without which every arm above is
# satisfied by a probe that reports every effect for every module.
_INERT = "VALUE = 1\n"


def _measured(body: str) -> import_effects.Effects:
    """Write a one-off specimen into a private directory and measure importing it.

    ⚑ THE SPECIMEN'S DIRECTORY IS ALSO THE PROBE'S CWD, so it is importable by bare name and any
    write it performs lands where the measurement can attribute it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        where = Path(tmp)
        (where / "specimen_under_test.py").write_text(body, encoding="utf-8")
        return import_effects.effects("specimen_under_test", where)


def an_import_time_write_is_named(out: list[str]) -> int:
    """Check a module that writes at import is reported, with the filename as the witness."""
    got = _measured(_WRITER)
    if not any("sentinel.txt" in name for name in got.wrote):
        out.append(f"selftest: the import-time write was not detected ({got.wrote})")
        return 1
    return 0


def a_syspath_mutation_is_named(out: list[str]) -> int:
    """Check a `sys.path` mutation is reported — the shadowing axis, alleged and never measured."""
    got = _measured(_PATHER)
    if _SENTINEL_PATH not in got.path_added:
        out.append(f"selftest: the sys.path mutation was not detected ({got.path_added})")
        return 1
    return 0


def a_stray_module_entry_is_named(out: list[str]) -> int:
    """Check a foreign `sys.modules` entry is reported."""
    got = _measured(_MODDER)
    if "a_foreign_name" not in got.modules_added:
        out.append(f"selftest: the sys.modules entry was not detected ({got.modules_added})")
        return 1
    return 0


def a_subprocess_spawn_is_named(out: list[str]) -> int:
    """Check a subprocess spawned at import is reported."""
    got = _measured(_SPAWNER)
    if not got.spawned:
        out.append("selftest: the import-time subprocess spawn was not detected")
        return 1
    return 0


def an_inert_module_is_inert(out: list[str]) -> int:
    """Check the POSITIVE CONTROL: a module doing nothing is reported as doing nothing.

    ⚑ WITHOUT THIS ARM THE PROBE COULD REPORT EVERY EFFECT FOR EVERY MODULE and still satisfy
    every arm above. A reader that flags the whole population is as useless as one that flags
    none, and only a member it must NOT flag tells them apart.
    """
    got = _measured(_INERT)
    if not got.inert:
        out.append(f"selftest: an inert module was reported with effects ({got.render()})")
        return 1
    return 0


def the_specimens_disagree(out: list[str]) -> int:
    """Check the probe DISCRIMINATES rather than answering uniformly.

    ⚑ THE ARMS ABOVE PIN INDIVIDUAL VALUES; this pins that inert and non-inert are DIFFERENT
    answers from the same call, stated directly rather than left as an inference across arms.
    """
    if _measured(_WRITER).inert == _measured(_INERT).inert:
        out.append("selftest: the writer and the inert module got the same verdict")
        return 1
    return 0


def an_unmeasured_probe_is_not_inert(out: list[str]) -> int:
    """Check a probe that returned no ledger is NOT reported as clean.

    ⚑ THE FALSE ZERO THIS WHOLE SURFACE EXISTS TO PREVENT. `measured` and `inert` must not
    collapse: a module that could not be measured is unknown, and reporting it as having no
    effects is the census-green defect committed inside the reader built to catch it.
    """
    blank = import_effects.Effects("m", import_effects.UNMEASURED, (), (), (), ())
    if blank.inert or blank.measured:
        out.append("selftest: an unmeasured probe was reported as inert or as measured")
        return 1
    return 0


def a_read_is_not_reported_as_a_write(out: list[str]) -> int:
    """Check a module that only READS a file is not flagged.

    ⚑ THE FALSE-POSITIVE TWIN. Every import reads files; a reader that reported those would bury
    the writes it exists to surface, which fails as badly as missing them and is harder to notice.
    """
    with tempfile.TemporaryDirectory() as tmp:
        where = Path(tmp)
        (where / "data.txt").write_text("x", encoding="utf-8")
        (where / "specimen_under_test.py").write_text(
            "with open('data.txt') as fh:\n    fh.read()\n", encoding="utf-8"
        )
        got = import_effects.effects("specimen_under_test", where)
    if any("data.txt" in name for name in got.wrote):
        out.append("selftest: a plain file READ was reported as a write")
        return 1
    return 0


_ARMS = (
    an_import_time_write_is_named,
    a_syspath_mutation_is_named,
    a_stray_module_entry_is_named,
    a_subprocess_spawn_is_named,
    an_inert_module_is_inert,
    the_specimens_disagree,
    an_unmeasured_probe_is_not_inert,
    a_read_is_not_reported_as_a_write,
)

_CASE_COUNT = len(_ARMS)


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"import-effects selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"import-effects selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
