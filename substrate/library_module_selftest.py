#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.library_module` — the loader for the unpackaged worklist library.

⚑⚑⚑ THE ARM THAT MATTERS IS THE FAILED-IMPORT CLEANUP, because its damage is invisible and
DEFERRED. `library_module` registers the module in `sys.modules` BEFORE executing it, so a module
importing its own siblings by bare name can find itself mid-import. If a module then raises, the
half-executed object must be REMOVED — otherwise the next caller finds it, gets `(module, None)`,
and reads partial state as a successful load. Nothing fails at that moment; something fails later,
somewhere else, with no trace back to here.

⚑⚑ AND `BaseException` IS CAUGHT, WHICH IS NORMALLY WRONG AND IS RIGHT HERE. A library module may
`sys.exit` at import — an unstated tenant, an unknown flag — and `SystemExit` does not derive from
`Exception`, so catching only `Exception` would let a module's own refusal propagate out of a
loader whose job is to REPORT it. That is a case rather than a comment, and the fixture exits at
module scope to exercise the same path a live refusal takes.

⚑⚑ THE FIXTURES ARE PLANTED IN THE REAL `catalog/library/`, because the resolver builds its path
from `corpus.ROOT` and `LIBRARY_DIR` by construction — there is no root to inject. Each is removed
in `__exit__`, along with the `sys.modules` entry it may have left, so no case can leak state into
the next. The planter REFUSES to write over an existing file rather than clobbering a real module.

⚑⚑ THE FIXTURE'S VALUE IS READ THROUGH AN `object` BINDING, NOT STRAIGHT OUT OF `getattr`, which
is typed `Any` and propagates into whatever holds it — 2 findings on the first draft. This is the
same discipline `sort_key` records for its field access, applied to a suite: bind the dynamic read
before it travels.

⚑ THE THREE LOADERS ARE A FAMILY AND THE REFUSAL IS DIAGNOSTIC. `gate_module` serves `scripts/`,
`scratch_module` serves `scratch/`, this serves `catalog/library/` — one per unpackaged directory.
Reaching for the wrong one reports a present module as absent, which is a diagnosis the refusal
makes for itself by NAMING THE PATH IT TRIED. So the absence arm asserts the path is in the
message, not merely that a message exists.
"""

from __future__ import annotations

import sys

from substrate import corpus, library_module

# A module that loads cleanly and carries a value a case can read back.
_MARK = "loaded-by-the-selftest"
_GOOD = f'"""A fixture."""\nMARK = "{_MARK}"\n'

# A module that raises during execution — the cleanup case.
_RAISES = '"""A fixture."""\nraise RuntimeError("fixture refuses")\n'

# A module that EXITS at import scope — the `BaseException` case. `SystemExit` does not derive
# from `Exception`, so this is the path a narrower catch would let escape.
_EXITS = '"""A fixture."""\nimport sys\nsys.exit(2)\n'

# Fixture stems, distinct per case so a leak in one is visible in another rather than masked.
_OK = "library_module_selftest_ok"
_BAD = "library_module_selftest_bad"
_GONE = "library_module_selftest_exits"


class _Planted:
    """Write a library fixture, and remove it AND its module registration afterwards.

    ⚑ THE `sys.modules` CLEANUP IS PART OF THE FIXTURE, not part of what is being tested. A
    case leaving an entry behind would make the NEXT case's already-loaded branch fire, and the
    suite would pass while measuring the wrong thing.
    """

    def __init__(self, stem: str, body: str) -> None:
        """Record the fixture to plant."""
        self.stem = stem
        self.path = corpus.ROOT / library_module.LIBRARY_DIR / f"{stem}.py"
        self._body = body

    def __enter__(self) -> str:
        """Write the fixture and return its stem."""
        if self.path.exists():
            msg = f"fixture would clobber a real file at {self.path}"
            raise RuntimeError(msg)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self._body, encoding="utf-8")
        return self.stem

    def __exit__(self, *_exc: object) -> None:
        """Remove the fixture, its bytecode cache, and any registration it left.

        ⚑⚑ THE `.pyc` IS PART OF THE FIXTURE AND A FIRST DRAFT MISSED IT. Executing a module
        writes `__pycache__/<stem>.cpython-*.pyc` beside it, so removing only the source left
        three bytecode files in `catalog/library/` — found by a filesystem sweep AFTER the
        suite reported clean, which is the point: a cleanup arm that checks only what it knows
        it wrote cannot see what the code under test created on its behalf.
        """
        self.path.unlink(missing_ok=True)
        for cached in self.path.parent.glob(f"__pycache__/{self.stem}.*.pyc"):
            cached.unlink(missing_ok=True)
        sys.modules.pop(self.stem, None)


def a_library_module_loads(out: list[str]) -> int:
    """Check the happy path returns a module and no reason."""
    with _Planted(_OK, _GOOD) as stem:
        module, why = library_module.library_module(stem)
        if module is None:
            out.append(f"selftest: a valid library module did not load: {why}")
            return 1
        if why is not None:
            out.append(f"selftest: a successful load carried a reason: {why!r}")
            return 1
        # ⚑ BOUND AS `object` BEFORE IT TRAVELS — `getattr` is typed `Any`, and comparing its
        # result directly propagates that into the expression.
        mark: object = getattr(module, "MARK", None)
        if mark != _MARK:
            out.append("selftest: the loaded module is not the fixture that was planted")
            return 1
    return 0


def the_py_suffix_is_optional(out: list[str]) -> int:
    """Check a caller may name the module either way — the suffix is stripped once."""
    with _Planted(_OK, _GOOD) as stem:
        module, why = library_module.library_module(f"{stem}.py")
        if module is None:
            out.append(f"selftest: naming the module with its suffix failed: {why}")
            return 1
    return 0


def an_absent_module_names_the_path_it_tried(out: list[str]) -> int:
    """Check the refusal is DIAGNOSTIC — THE FAMILY ARM.

    ⚑⚑ THREE LOADERS SERVE THREE UNPACKAGED DIRECTORIES, and reaching for the wrong one reports
    a present module as absent. The refusal naming the path it tried is what lets a reader see
    which loader they used, so a bare "not found" would leave the commonest mistake undiagnosed.
    """
    module, why = library_module.library_module("no_such_library_module_here")
    if module is not None:
        out.append("selftest: a nonexistent module loaded")
        return 1
    if why is None:
        out.append("selftest: an absent module refused without a reason")
        return 1
    if library_module.LIBRARY_DIR not in why:
        out.append(f"selftest: the refusal does not name the directory it tried: {why!r}")
        return 1
    return 0


def the_resolved_path_is_under_the_library_directory(out: list[str]) -> int:
    """Check `module_path` composes the documented location, suffix-insensitively."""
    bare = library_module.module_path("thing")
    if bare != f"{library_module.LIBRARY_DIR}/thing.py":
        out.append(f"selftest: module_path returned {bare!r}")
        return 1
    if library_module.module_path("thing.py") != bare:
        out.append("selftest: the two spellings resolve to different paths")
        return 1
    return 0


def a_module_that_raises_is_reported_not_propagated(out: list[str]) -> int:
    """Check an exception during execution becomes a reason, not a traceback through a caller."""
    with _Planted(_BAD, _RAISES) as stem:
        module, why = library_module.library_module(stem)
        if module is not None:
            out.append("selftest: a module that raised was returned as loaded")
            return 1
        if why is None or "RuntimeError" not in why:
            out.append(f"selftest: the reason does not name the exception: {why!r}")
            return 1
    return 0


def a_module_that_exits_at_import_is_reported(out: list[str]) -> int:
    """Check `SystemExit` is caught — THE `BaseException` ARM.

    ⚑⚑ `SystemExit` DOES NOT DERIVE FROM `Exception`. A loader catching only `Exception` would
    let a library module's own refusal kill the caller trying to report it, which is exactly the
    justification `gate_module` records for the same catch one directory over.
    """
    with _Planted(_GONE, _EXITS) as stem:
        module, why = library_module.library_module(stem)
        if module is not None:
            out.append("selftest: a module that exited at import was returned as loaded")
            return 1
        if why is None or "SystemExit" not in why:
            out.append(f"selftest: the reason does not name the exit: {why!r}")
            return 1
    return 0


def a_failed_load_leaves_nothing_registered(out: list[str]) -> int:
    """Check the half-executed module is UNREGISTERED — THE DEFERRED-DAMAGE ARM.

    ⚑⚑⚑ THE REGISTRATION HAPPENS BEFORE EXECUTION so a module importing its own siblings can
    find itself mid-import. If a failure left that entry behind, the NEXT caller would take the
    already-loaded branch and receive a partially-executed module as a SUCCESS. Both failure
    kinds are checked, because the two exit through different arms of the same handler.
    """
    for stem, body in ((_BAD, _RAISES), (_GONE, _EXITS)):
        with _Planted(stem, body):
            library_module.library_module(stem)
            if stem in sys.modules:
                out.append(f"selftest: a failed load left {stem!r} registered")
                return 1
    return 0


def a_second_failed_load_still_refuses(out: list[str]) -> int:
    """Check the failure is not cached as a success — the consequence of the cleanup working.

    ⚑ THIS IS THE OBSERVABLE EFFECT OF THE ARM ABOVE, asked the way a caller would. Checking
    `sys.modules` inspects the mechanism; asking twice observes what the mechanism is FOR.
    """
    with _Planted(_BAD, _RAISES) as stem:
        library_module.library_module(stem)
        module, why = library_module.library_module(stem)
        if module is not None:
            out.append("selftest: a second load of a failing module succeeded")
            return 1
        if why is None:
            out.append("selftest: the second refusal carried no reason")
            return 1
    return 0


def an_already_loaded_module_is_returned_as_is(out: list[str]) -> int:
    """Check a second caller gets the SAME object, not a second execution.

    ⚑⚑ TWO MODULE OBJECTS FOR ONE LIBRARY differ only in which one holds the state a later
    reader looks at — a divergence with no error at the point it is created. Identity is the
    assertion; equality would not distinguish two fresh executions of the same source.
    """
    with _Planted(_OK, _GOOD) as stem:
        first, _why = library_module.library_module(stem)
        second, _why2 = library_module.library_module(stem)
        if first is None or second is None:
            out.append("selftest: the fixture did not load, so the identity arm asserts nothing")
            return 1
        if first is not second:
            out.append("selftest: a second load produced a DIFFERENT module object")
            return 1
    return 0


def a_successful_load_registers_the_module(out: list[str]) -> int:
    """Check the registration survives a success — the other half of the cleanup arm.

    ⚑ WITHOUT THIS, A LOADER THAT UNREGISTERED UNCONDITIONALLY passes the failure arms. The two
    together distinguish cleaning up after a failure from never registering at all.
    """
    with _Planted(_OK, _GOOD) as stem:
        if stem in sys.modules:
            out.append(f"selftest: {stem!r} was registered before the load")
            return 1
        library_module.library_module(stem)
        if stem not in sys.modules:
            out.append("selftest: a successful load registered nothing")
            return 1
    return 0


def the_fixtures_leave_nothing_in_the_library(out: list[str]) -> int:
    """Check a load-and-unwind leaves NO file behind — asserted from the DISK, not the plan.

    ⚑⚑⚑ THIS ARM EXISTS BECAUSE THE CLEANUP WAS INCOMPLETE AND THE SUITE STILL REPORTED CLEAN.
    Executing a module writes a `.pyc` beside it; the first `__exit__` removed only the source,
    and three bytecode files survived in `catalog/library/` — found by sweeping the directory
    afterwards, never by any case. A cleanup that checks only what it knows it WROTE cannot see
    what the code under test created on its behalf, so this reads the directory instead.
    """
    library = corpus.ROOT / library_module.LIBRARY_DIR
    before = {p.name for p in library.rglob("*") if p.is_file()}
    with _Planted(_OK, _GOOD) as stem:
        library_module.library_module(stem)
    after = {p.name for p in library.rglob("*") if p.is_file()}
    leaked = sorted(after - before)
    if leaked:
        out.append(f"selftest: a load-and-unwind left files behind: {leaked!r}")
        return 1
    return 0


_ARMS = (
    a_library_module_loads,
    the_py_suffix_is_optional,
    an_absent_module_names_the_path_it_tried,
    the_resolved_path_is_under_the_library_directory,
    a_module_that_raises_is_reported_not_propagated,
    a_module_that_exits_at_import_is_reported,
    a_failed_load_leaves_nothing_registered,
    a_second_failed_load_still_refuses,
    an_already_loaded_module_is_returned_as_is,
    a_successful_load_registers_the_module,
    the_fixtures_leave_nothing_in_the_library,
)

_CASE_COUNT = 3 + 1 + 3 + 2 + 2 + 2 + 2 + 2 + 2 + 2 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)

    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"library-module selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"library-module selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
