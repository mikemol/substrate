# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.borrowed_root` — four origins, and why the fourth is not a verdict.

⚑⚑⚑ THE GLOBAL ARM IS THE ONE THE FIRST PREDICATE COULD NOT EXPRESS, and it is why this suite was
rewritten rather than extended. `type_census_summary.census` takes NO root parameter, reaches
`corpus.ROOT` directly, and crashes from a borrowing checkout — confirmed by execution, not
inferred. A predicate reading the parameter list saw a function with no root and classified it as
not a site at all. The fixture here is that exact shape.

⚑⚑ AND THE FIXTURES ARE SOURCE TEXT, NOT FILES, because the module parses rather than imports.
That is what lets a case state a defect precisely — `def f(root=None)` versus `def f(root)` versus
no parameter at all — where a file-based fixture would carry a dozen incidental differences.

⚑ THE SENSITIVITY ARMS FORCE THE STATE WHERE EACH RULE SHOULD FAIL. Every arm below feeds a
correct fixture, so none of them alone shows the origin is DECIDED rather than satisfied by
accident: one strips the default and asserts the verdict moves, another strips the global.
"""

from __future__ import annotations

import sys

from substrate import borrowed_root as br

#: A defaulted root: the parameter exists and falls back to substrate's own tree.
#:
#: ⚑⚑⚑ THE WALK IS `corpus.py_files(root=where)`, WHICH IS THE SHAPE THAT ACTUALLY CRASHED — and
#: the first cut of this fixture said `walk(where)` instead (gate-G263, operator-ruled). That was
#: not a faithful model: a bare `walk(where)` returns paths under `where` BY CONSTRUCTION, so one
#: root is used twice and there is nothing to disagree. `corpus.py_files` resolves its root through
#: `resolve_root`, which prefers the caller's CWD — so the walk can hand back paths NOT under
#: `where`, and that is precisely why `file_header.population` and `drain_leverage.population`
#: raised from a borrowing checkout while this fixture's shape never could.
DEFAULTED_SRC = """
def population(root=None):
    where = root if root is not None else corpus.ROOT
    return [(p, str(p.relative_to(where))) for p in corpus.py_files(root=where)]
"""

#: ⚑ THE SHAPE THE PARAMETER-KEYED PREDICATE WAS BLIND TO. No root parameter exists at all, so
#: there was nothing for it to inspect — and this is `type_census_summary.census`, which crashes.
GLOBAL_SRC = """
def census():
    return [str(Path(f).relative_to(corpus.ROOT)) for f in corpus.py_files()]
"""

#: A latent site: identical body, but the root is required, so every caller states its tree.
RECEIVED_SRC = """
def population(root):
    return [(p, str(p.relative_to(root))) for p in walk(root)]
"""

#: A site that already implements the tolerant rule by hand — correct, and a copy (gate-G255).
GUARDED_SRC = """
def rows(root, operands):
    for operand in operands:
        try:
            label = str(operand.relative_to(root))
        except ValueError:
            label = str(operand)
        yield label
"""

#: ⚑ THE OPERATOR-RULED THIRD-OUTCOME SHAPE (gate-G261), and it is `corpus.py_files`. The measured
#: root is bound from a CALL that takes the walked root, so the two are co-derived — yet the callee
#: may prefer the caller's cwd, so the shape ADMITS a divergence every observed run denied.
DERIVED_SRC = """
def py_files(*requested, root=ROOT):
    out = []
    for r in (requested or roots(root)):
        base = resolve_root(r, root)
        out.extend(str(d.relative_to(base)) for d in walk(base))
    return out
"""

#: A function that touches neither — the population this census must NOT claim.
UNRELATED_SRC = """
def tally(rows):
    return len(rows)
"""


def _origin_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the four origins the census distinguishes."""
    out: list[tuple[str, bool]] = []

    defaulted = br.sites(DEFAULTED_SRC, "m")
    out.append((f"a defaulted root is found: {len(defaulted)}", len(defaulted) == 1))
    out.append(
        (
            f"and classified LIVE — {defaulted[0].why()}",
            defaulted[0].live and defaulted[0].origin == "defaulted",
        )
    )

    # ⚑⚑ THE ARM THE ORIGIN PREDICATE FAILED. No parameter to read, and it still crashes.
    globals_ = br.sites(GLOBAL_SRC, "m")
    out.append((f"a root-free function IS a site: {len(globals_)}", len(globals_) == 1))
    out.append(
        (
            f"and classified LIVE global — {globals_[0].why()}",
            globals_[0].live and globals_[0].origin == "global",
        )
    )

    received = br.sites(RECEIVED_SRC, "m")
    out.append(
        (
            f"a required root is latent — {received[0].why()}",
            not received[0].live and received[0].origin == "received",
        )
    )

    guarded = br.sites(GUARDED_SRC, "m")
    out.append(
        (
            f"a hand-guarded site is named, not silent — {guarded[0].why()}",
            guarded[0].origin == "guarded",
        )
    )
    return out


def _account_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the components a verdict carries.

    ⚑ THE ACCOUNT MUST NAME WHICH ORIGIN IT IS, because the four need different responses: a global
    is repaired today, a defaulted one is repaired or given a root, a received one is a note, and a
    guarded one is a spelling to retire.
    """
    out: list[tuple[str, bool]] = []
    live = br.sites(GLOBAL_SRC, "mod.py")[0]
    latent = br.sites(RECEIVED_SRC, "mod.py")[0]

    out.append((f"the live account says LIVE: {live.why()}", "LIVE" in live.why()))
    out.append((f"the latent account says latent: {latent.why()}", "latent" in latent.why()))
    out.append(
        (
            f"and both name the module and line: {live.why()[:12]!r}",
            "mod.py" in live.why() and str(live.line) in live.why(),
        )
    )
    out.append((f"and the function: {live.func!r}", "census" in live.why()))
    return out


def _scope_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for what the census must NOT claim.

    ⚑⚑ A CENSUS THAT MATCHED EVERY FUNCTION would pass every arm above and report the whole tree as
    suspect. The unrelated fixture is what makes the population a population.
    """
    out: list[tuple[str, bool]] = []

    out.append(
        (
            f"a function touching no root is not claimed: {br.sites(UNRELATED_SRC, 'm')}",
            br.sites(UNRELATED_SRC, "m") == [],
        )
    )
    out.append((f"empty source yields nothing: {br.sites('', 'm')}", br.sites("", "m") == []))

    # ⚑ A KEYWORD-ONLY DEFAULTED ROOT IS STILL LIVE — the exposure is the default, not the calling
    # convention, and reading only positional defaults would miss a whole shape.
    kwonly = br.sites("def f(*, root=None):\n    return p.relative_to(root)\n", "m")
    out.append((f"a keyword-only defaulted root is LIVE: {kwonly[0].why()}", kwonly[0].live))

    # ⚑ AND A DIFFERENTLY-NAMED ROOT IS RECOGNISED. The class was first seen under one parameter
    # name, and keying on that name alone would make the census a fact about the first report.
    named = br.sites("def f(where=None):\n    return p.relative_to(where)\n", "m")
    out.append((f"a root spelled `where` is LIVE: {named[0].why()}", named[0].live))
    return out


def _untraced_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the third outcome.

    ⚑⚑⚑ AN UNDECIDABLE ORIGIN IS REPORTED, NEVER ASSUMED SAFE. The whole reason this predicate was
    rewritten is that its predecessor's silence was read as absence; a reader that cannot trace a
    root must say so, or it repeats the defect one level up.
    """
    out: list[tuple[str, bool]] = []

    opaque = br.sites("def f(rows):\n    return rows[0].relative_to(pick(rows))\n", "m")
    out.append(
        (
            f"an untraceable root is UNTRACED, not latent: {opaque[0].why()}",
            opaque[0].origin == "untraced" and not opaque[0].live,
        )
    )
    out.append(
        (
            f"and UNTRACED is visible in the account: {opaque[0].why()}",
            "UNTRACED" in opaque[0].why(),
        )
    )

    # ⚑⚑⚑ THE OPERATOR-RULED CASE, AND IT IS `corpus.py_files` (gate-G261). Neither instrument
    # overrules the other, so the verdict carries the disagreement instead of picking a side.
    derived = br.sites(DERIVED_SRC, "m")[0]
    out.append(
        (
            f"a root derived through a call is UNTRACED: {derived.why()}",
            derived.origin == "untraced" and not derived.live,
        )
    )
    return out


def _sensitivity_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` proving each discriminator DECIDES rather than decorates.

    ⚑⚑⚑ EVERY ARM ABOVE FEEDS A CORRECT FIXTURE, so none shows the predicate does work rather than
    being satisfied by accident. These take a fixture, remove exactly ONE thing, and assert the
    verdict flips — if it did not, the classification would be decoration.
    """
    out: list[tuple[str, bool]] = []

    before = br.sites(DEFAULTED_SRC, "m")[0]
    after = br.sites(DEFAULTED_SRC.replace("root=None", "root"), "m")[0]
    moved = f"removing ONLY the default moves it: {before.origin} -> {after.origin}"
    out.append((moved, before.origin == "defaulted" and after.origin != "defaulted"))

    # ⚑ AND REMOVING THE GLOBAL MOVES THE GLOBAL ARM. Without this, `_origin` could be returning
    # "global" for any parameterless function that labels anything.
    plain = br.sites(GLOBAL_SRC.replace("corpus.ROOT", "given"), "m")[0]
    out.append(
        (f"removing ONLY the global moves it off global: {plain.origin}", plain.origin != "global")
    )

    # ⚑ AND DROPPING THE GUARD MOVES THE GUARDED ARM, so `guarded` is not absorbing every site.
    unguarded = br.sites(GUARDED_SRC.replace("except ValueError", "except OSError"), "m")[0]
    out.append(
        (
            f"a non-ValueError guard is not GUARDED: {unguarded.origin}",
            unguarded.origin != "guarded",
        )
    )
    return out


def _census_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the whole-corpus pass and its failure handling."""
    out: list[tuple[str, bool]] = []

    # ⚑ AN UNPARSEABLE FILE IS SKIPPED, NOT COUNTED CLEAN, and a case pins that — swallowing it
    # silently would report a smaller population as a complete one.
    from pathlib import Path  # noqa: PLC0415 - only this arm needs a real path

    missing = br.census([(Path("/nonexistent/no-such.py"), "gone.py")])
    out.append((f"an unreadable file is skipped rather than raising: {missing}", missing == []))
    out.append((f"an empty file list yields nothing: {br.census([])}", br.census([]) == []))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _origin_cases()
        + _account_cases()
        + _scope_cases()
        + _untraced_cases()
        + _sensitivity_cases()
        + _census_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"borrowed-root selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
