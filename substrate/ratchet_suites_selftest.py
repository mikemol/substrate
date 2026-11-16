#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ratchet_suites` — the composer that composes the composers.

⚑⚑ THE COMPOSER WAS THE LAST UNCOVERED THING IN ITS OWN CENSUS. Every module it composes owns
a suite; the file that decides WHICH modules those are owned none, and `suite_gap_report`
reported it INLINE — a `--selftest` dispatch with no sibling holding cases. A roster that is
green because it is empty and a roster that is green because it passed are indistinguishable
from the composer's own output, which is the whole failure ⟡derive-the-roster was dispatched
against, one level up.

⚑⚑ THE ARMS ARE POSSIBLE BECAUSE MEMBERSHIP IS DERIVED. `extracted`, `has_suite` and `members`
each take a `root`, so a FIXTURE TREE can be pointed at — a facade with known imports and
siblings that are present, absent, suite-shaped or not. Before ⟡derive-the-roster the roster was
a hand-typed tuple of bound callables and the only observable was "it ran"; a pure function of a
directory is a thing a case can actually interrogate.

⚑ WHAT THE ARMS PIN, in one line each: the manifest read yields exactly the facade's
`substrate.*` module-level imports (not dotted submodules, not deferred ones); a member with no
`_selftest` sibling is EXCLUDED rather than failing at import; a member with a sibling that
`suite_discovery` does not call a suite is likewise excluded; a discovered-but-unordered member
RAISES `UnorderedSuiteError`; `members` returns `ORDER`-relative order regardless of discovery
order; a sibling without an entry point RAISES `NoEntryPointError`; and the ORDER is LEAF-FIRST.

⚑⚑ THE TWO REFUSAL PATHS ARE THE POINT, AND THEY ARE PINNED AS REFUSALS. Appending an unordered
member would make "ordered deliberately" and "fell to the end because nobody said"
indistinguishable — and last is the load-bearing position, where the aggregate belongs. A
`getattr(..., None)` skip on a missing entry point would be a false green of exactly the shape
`census-green-is-a-fact-about-the-census` records. A case that only checked the happy path would
be satisfied by both defects.

⚑⚑⚑ AND THE MOTIVATING DEFECT GETS AN ARM AS A PROPERTY, NOT AS AN INSTANCE. The hand-typed
roster silently omitted `ratchet_render` — a module whose suite passes 29/29, re-exported by the
facade, missed by review AND by the coverage census. Naming `ratchet_render` in a case would be
green for the wrong reason now that the instance is fixed: it would pass against a roster that
had been re-hand-typed. So the arm pins the PROPERTY over the LIVE tree — every extracted
capability whose sibling is a suite is composed, no exceptions — which is false for any omission,
including the next one.

⚑⚑⚑ AND WRITING THIS FILE IMMEDIATELY FIRED THAT REFUSAL ON `ratchet_suites` ITSELF. The facade
re-exports `run_all` from the composer, so the moment the composer gained a suite sibling it
became a discovered member its own `ORDER` did not place — `UnorderedSuiteError`, on the first
run, before a single case executed. That is the derivation being right about a fact nobody had
typed: the composer is a composed capability like any other. It was placed last, after
`ratchet_core`, and the count went 8 → 9.

⚑⚑⚑ THE ORDER ITSELF WAS THE LAST UNVERIFIED CLAIM IN THIS FILE'S SUBJECT (⟡gate-the-order).
COMPLETENESS was gated from the first run — a discovered member `ORDER` does not place is
refused. SOUNDNESS was a COMMENT: *"ordered leaf-first, so a failure names the deepest broken
module"*, asserted and checked by nothing. `_order` pins it, and the discriminating half is a
fixture whose dependency is KNOWN-INVERTED — because an arm that computes no edges at all also
finds no violations, and the two are indistinguishable from a green line.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate.ratchet_suites import (
    ORDER,
    PACKAGE,
    SUITE_SUFFIX,
    NoEntryPointError,
    UnorderedSuiteError,
    extracted,
    has_suite,
    inversions,
    manifest_path,
    members,
    suite,
    suites,
)

# A suite-shaped sibling: an entry point plus the flag, which is what `suite_discovery` admits.
SUITE_SRC = (
    "import sys\n\n\ndef selftest() -> int:\n    return 0\n\n\n"
    'if __name__ == "__main__":\n    sys.exit(selftest() if "--selftest" in sys.argv'
    " else 0)\n"
)

# A sibling that is a CLI but not a suite — an entry point with no selftest evidence at all.
NOT_A_SUITE_SRC = 'import sys\n\n\nif __name__ == "__main__":\n    sys.exit(0)\n'

# The capability whose sibling the `NoEntryPointError` arm PLANTS for the length of one case.
# Spelled so no real module can claim the name and so no census mistakes the transient for a
# capability: it is never re-exported by the facade, so `extracted` cannot see it either.
ENTRYLESS = "_ratchet_suites_entryless_fixture"

# A sibling `suite_discovery` ADMITS and `suite()` must REFUSE — the flag is handled, so the
# predicate calls it a suite, but the entry point the composer calls is simply not there.
ENTRYLESS_SRC = (
    'import sys\n\n\nif __name__ == "__main__":\n'
    '    sys.exit(0 if "--selftest" in sys.argv else 2)\n'
)

# A capability body with no intra-package imports at all — a LEAF, in the `_order` fixtures.
LEAF_SRC = '"""A leaf capability."""\n'


def _fixture(tmp: Path, imports: tuple[str, ...], siblings: dict[str, str]) -> Path:
    """Build a fixture tree: a facade with `imports`, and `substrate/` holding `siblings`.

    ⚑ THE FACADE IS WRITTEN AT THE REAL `MANIFEST` PATH, read back through `manifest_path`, so
    the fixture cannot drift from the one spelling the module keys its derivation on.

    ⚑ `siblings` IS KEYED ON A BARE MODULE NAME, so the same helper writes a suite sibling
    (`alpha_selftest`) and a CAPABILITY (`ratchet_log`). The `_order` arms need the second: the
    edges that constrain the composition order are the capabilities' own imports, never their
    suites' — a suite imports the module under test by construction, which says nothing.
    """
    root = tmp / "tree"
    manifest = manifest_path(root)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text("".join(f"{line}\n" for line in imports), encoding="utf-8")
    package = root / PACKAGE
    package.mkdir(parents=True, exist_ok=True)
    for name, src in siblings.items():
        (package / f"{name}.py").write_text(src, encoding="utf-8")
    return root


def _derivation(cases: list[tuple[str, bool, str]]) -> None:
    """Pin what the manifest read admits and what suite-discovery accepts."""

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    def holds(label: str, *, got: bool) -> None:
        cases.append((label, got is True, f"{got!r} is not True"))

    def denies(label: str, *, got: bool) -> None:
        cases.append((label, got is False, f"{got!r} is not False"))

    # ⚑ THE MANIFEST READ IS MODULE-LEVEL `substrate.*` ONLY. A deferred import is not part of
    # the facade's surface, and a dotted submodule is not a capability — unioning either would
    # compose a suite for something the facade does not actually re-export.
    with tempfile.TemporaryDirectory() as d:
        root = _fixture(
            Path(d),
            (
                f"from {PACKAGE}.alpha import A",
                f"from {PACKAGE}.beta import B",
                f"from {PACKAGE}.gamma.deep import C",
                "import os",
                "",
                "def later():",
                f"    from {PACKAGE}.delta import D",
                "    return D",
            ),
            {},
        )
        equals(
            f"the manifest read yields exactly the facade's {PACKAGE}.* capabilities",
            extracted(root),
            frozenset({"alpha", "beta"}),
        )

    # ⚑ DISCOVERY IS `suite_discovery.is_suite`, NOT FILE EXISTENCE. Both directions matter: an
    # absent sibling excludes, and a PRESENT sibling that is merely a CLI also excludes — the
    # under-admitting direction has cost this repo more, so it is pinned rather than assumed.
    with tempfile.TemporaryDirectory() as d:
        root = _fixture(
            Path(d),
            (
                f"from {PACKAGE}.alpha import A",
                f"from {PACKAGE}.beta import B",
                f"from {PACKAGE}.gamma import C",
            ),
            {f"alpha{SUITE_SUFFIX}": SUITE_SRC, f"beta{SUITE_SUFFIX}": NOT_A_SUITE_SRC},
        )
        holds("a member with a suite sibling is admitted", got=has_suite("alpha", root))
        denies("...a sibling that is only a CLI is not a suite", got=has_suite("beta", root))
        denies("...and a member with no sibling at all is excluded", got=has_suite("gamma", root))


def _order(cases: list[tuple[str, bool, str]]) -> None:
    """Pin LEAF-FIRST as a checked consequence, discriminated by a known-inverted fixture.

    ⚑⚑⚑ THE ORDER'S SOUNDNESS WAS PROSE (⟡gate-the-order). `ORDER` is hand-typed and stays that
    way — dependency order is a JUDGEMENT, not derivable from a flat import set — but a
    judgement that is UNDERIVABLE is not thereby UNVERIFIABLE, and those two words were being
    treated as one. The judgement has a mechanical consequence: if capability A imports
    capability B at module scope, B must precede A, because the entire reason the composition
    is ordered is that a failure should name the DEEPEST broken module rather than the
    composition that noticed it. An inverted row silently loses that and stays green.

    ⚑⚑ THE INVERTED FIXTURE IS THE DISCRIMINATOR, AND WITHOUT IT THE ARM WOULD BE VACUOUS. An
    implementation that computes NO edges — a wrong prefix, a suffix slip, a name that never
    matches — reports zero inversions over the live tree and is INDISTINGUISHABLE from a sound
    order. So the same two capabilities are written twice, once with the edge running the right
    way and once REVERSED, and the reversed tree must be reported. This is the shape
    `suite_gap_selftest`'s known-covered half already carries: a positive-only assertion cannot
    see a constant predicate.

    ⚑ AND EVERY ARM OBSERVES THE EFFECT. All three go through `inversions` — the verdict a
    reader would consult — rather than through `member_edges`, which would re-read the input one
    layer down and pass on an implementation that saw the edge and then judged it wrongly.
    """

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    # ⚑ THE FIXTURE USES REAL `ORDER` NAMES, because the property IS about this order. A pair of
    # invented names would exercise an ordering the module does not hold and could not detect a
    # ranking read from the wrong sequence.
    early, late = ORDER[0], ORDER[-1]

    # The edge runs the RIGHT way: the LATE capability imports the EARLY one, which is what a
    # leaf-first order looks like. Nothing is owed.
    with tempfile.TemporaryDirectory() as d:
        root = _fixture(Path(d), (), {late: f"from {PACKAGE} import {early}\n", early: LEAF_SRC})
        equals("a late capability importing an early one is NOT an inversion", inversions(root), ())

    # ⚑⚑ THE SAME TWO FILES WITH THE EDGE REVERSED — the EARLY capability imports the LATE one,
    # so the composition would run a module before the thing it depends on. THIS is the case
    # that fails if the arm computes no edges.
    with tempfile.TemporaryDirectory() as d:
        root = _fixture(Path(d), (), {early: f"from {PACKAGE} import {late}\n", late: LEAF_SRC})
        equals(
            "a KNOWN-INVERTED dependency is REPORTED — the discriminator",
            inversions(root),
            ((early, late),),
        )

    # ⚑ A DEFERRED IMPORT IS NOT A LOAD-ORDER CONSTRAINT. It fires when the function runs, not
    # when the module loads, so counting it would refuse orders that are correct — the
    # over-reporting direction, which is what teaches a reader to ignore a census.
    with tempfile.TemporaryDirectory() as d:
        root = _fixture(
            Path(d),
            (),
            {
                early: f'"""A leaf."""\n\n\ndef later():\n'
                f"    from {PACKAGE} import {late}\n    return {late}\n",
                late: LEAF_SRC,
            },
        )
        equals("a DEFERRED import is not an ordering edge", inversions(root), ())


def _refusals(cases: list[tuple[str, bool, str]]) -> None:
    """Pin both refusal paths as REFUSALS, and the ordering they protect."""

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    def raises(label: str, exc: type[Exception], call: object) -> None:
        try:
            call()  # type: ignore[operator]
        except exc as caught:
            cases.append((label, bool(str(caught)), "refused with an empty message"))
        except Exception as caught:  # noqa: BLE001 — the WRONG refusal is itself the finding
            cases.append((label, False, f"raised {type(caught).__name__}, not {exc.__name__}"))
        else:
            cases.append((label, False, f"returned instead of raising {exc.__name__}"))

    # ⚑⚑ DISCOVERED-BUT-UNORDERED RAISES. Appending would put an unjudged module in the position
    # that is load-bearing, and make "ordered" indistinguishable from "fell to the end".
    with tempfile.TemporaryDirectory() as d:
        root = _fixture(
            Path(d),
            (f"from {PACKAGE}.not_in_order import X",),
            {f"not_in_order{SUITE_SUFFIX}": SUITE_SRC},
        )
        raises(
            "a discovered member ORDER does not place is REFUSED, never appended",
            UnorderedSuiteError,
            lambda: members(root),
        )

    # ⚑ ORDER IS `ORDER`-RELATIVE, NOT DISCOVERY-RELATIVE. `extracted` returns a frozenset, so a
    # composition that trusted iteration order would be leaf-first only by luck, and the reason
    # ORDER is hand-typed at all is that leaf-first is a JUDGEMENT nothing else records.
    late, early = ORDER[-1], ORDER[0]
    with tempfile.TemporaryDirectory() as d:
        root = _fixture(
            Path(d),
            (f"from {PACKAGE}.{late} import Z", f"from {PACKAGE}.{early} import A"),
            {f"{late}{SUITE_SUFFIX}": SUITE_SRC, f"{early}{SUITE_SUFFIX}": SUITE_SRC},
        )
        equals(
            "members are returned in ORDER-relative order, not discovery order",
            members(root),
            (early, late),
        )

    # ⚑ A LISTED MEMBER WITH NO ENTRY POINT IS LOUD. `getattr(..., None)` would SKIP it — the
    # false green this composition exists to be incapable of.
    #
    # ⚑⚑ THE ENTRY-POINT-LESS SIBLING IS PLANTED, NOT BORROWED. No sibling in the tree has this
    # shape, and reaching for a module that merely fails to IMPORT would pin `ModuleNotFoundError`
    # while reading as a pass — the arm would be green for a reason unrelated to the property.
    # `suite` imports for real, so the branch under test is only reachable with a real module on
    # disk; it exists for the length of one case and is removed in a `finally`.
    planted = Path(__file__).with_name(f"{ENTRYLESS}{SUITE_SUFFIX}.py")
    planted.write_text(ENTRYLESS_SRC, encoding="utf-8")
    try:
        raises(
            "a sibling that answers --selftest but defines no selftest is REFUSED",
            NoEntryPointError,
            lambda: suite(ENTRYLESS),
        )
    finally:
        planted.unlink()
        sys.modules.pop(f"{PACKAGE}.{ENTRYLESS}{SUITE_SUFFIX}", None)
        # ⚑⚑ THE BYTECODE CACHE IS PART OF THE FIXTURE, AND IT WAS LEAKING. Removing the `.py`
        # and popping `sys.modules` left `__pycache__/<name>.cpython-*.pyc` on disk after every
        # run — the suite reported clean while a file named for a module that does not exist
        # accumulated beside the package. Found by sweeping the FILESYSTEM, not by enumerating
        # what this function believed it had written: the leak was in neither list.
        #
        # ⚑ GLOBBED, NOT SPELLED. The tag is the interpreter's (`cpython-313`), so naming one
        # would leak silently under any other interpreter — the same defect one version later.
        for stale in planted.parent.glob(f"__pycache__/{ENTRYLESS}{SUITE_SUFFIX}.*.pyc"):
            stale.unlink()


def selftest() -> int:
    """Pin the derivation, the ordering, both refusal paths, and no-silent-omission."""
    cases: list[tuple[str, bool, str]] = []
    _derivation(cases)
    _order(cases)
    _refusals(cases)

    def equals(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, f"{got!r} != {want!r}"))

    # ⚑⚑⚑ THE PROPERTY, NOT THE INSTANCE. `ratchet_render` was silently uncomposed by the
    # hand-typed roster; naming it here would pass against a roster that had merely been
    # re-typed. This is false for ANY omission, including the next one — which is exactly what
    # the instance-shaped case could not be. It runs against the LIVE tree for the same reason:
    # a fixture cannot be omitted from a roster it does not participate in.
    live = members()
    omitted = tuple(sorted(mod for mod in extracted() if has_suite(mod) and mod not in live))
    equals("every extracted capability with a suite is composed — no silent omission", omitted, ())
    equals("...and every composed member resolves to a real entry point", len(suites()), len(live))

    # ⚑⚑ AND THE LIVE ORDER IS LEAF-FIRST — the claim the comment made alone until
    # ⟡gate-the-order. It is the same predicate the fixture arms above discriminate, so a zero
    # here is a READ rather than a constant; without those arms it would be neither.
    equals(
        "the live ORDER is leaf-first — nothing precedes a capability it imports", inversions(), ()
    )

    failed = [(n, d) for n, good, d in cases if not good]
    for n, d in failed:
        sys.stderr.write(f"  FAIL {n}: {d}\n")
    sys.stdout.write(f"ratchet_suites selftest: {len(cases) - len(failed)}/{len(cases)}\n")
    return 1 if failed else 0


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
