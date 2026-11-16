# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.ambient` — write-once binding, and the one sanctioned way around it.

⚑⚑⚑ EVERY CASE RUNS IN ITS OWN CONTEXT, AND THAT IS LOAD-BEARING RATHER THAN HYGIENIC. The
variables under test are write-once for the life of a context, so two cases sharing one context
would make the SECOND fail for the first's reasons — and the failure would look like a defect in
the mechanism instead of in the suite. `contextvars.copy_context().run` gives each case a genuinely
fresh binding, which is the same primitive the override uses and is therefore also a demonstration
that the primitive does what the module claims.

⚑⚑ THE MECHANISM IS EXERCISED THROUGH A FIXTURE AMBIENT, not through `INTENT` or `TENANT`. A case
that bound the real `TENANT` would be stating a fact about this process's store, which is exactly
the kind of second independent resolution the module exists to refuse. The declared three get their
own cases, asserting only what they DECLARE.
"""

from __future__ import annotations

import contextvars
import sys
from typing import TYPE_CHECKING

from substrate import ambient as am

if TYPE_CHECKING:
    from collections.abc import Callable

#: A fixture ambient's vocabulary, so no case binds a variable the rest of the process reads.
FIXTURE_VOCAB = ("red", "blue")

#: The roster a case supplies when it means to exercise a REGISTERED override.
SANCTIONED = {("colour", "a-registered-site"): "the fixture's one sanctioned divergence"}

#: The smallest vocabulary that is still a CHOICE. A one-value ambient decides nothing.
A_CHOICE = 2


def _fresh[T](fn: Callable[[], T]) -> T:
    """Run `fn` in a context of its own, so write-once does not leak between cases.

    ⚑ GENERIC, NOT `object`-RETURNING. A first cut returned `object`, so every case unpacking a
    result lost its type and the checker refused the file — correctly: a suite whose assertions
    are untyped can compare a value against the wrong thing and still typecheck, which is exactly
    the class of defect these cases exist to catch in the code they test.
    """
    return contextvars.copy_context().run(fn)


def _amb() -> am.Ambient:
    """Return a fresh fixture ambient — a new one per case, never a shared module global."""
    return am.Ambient(
        "colour",
        FIXTURE_VOCAB,
        "'the colour asked for' and 'the colour this branch paints' differ.",
    )


def _binding_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for an ordinary first binding."""
    out: list[tuple[str, bool]] = []

    def case() -> tuple[str | None, str | None]:
        amb = _amb()
        amb.set("red", "the-entry-point")
        return amb.get(), amb.origin()

    value, origin = _fresh(case)
    out.append((f"a first write binds the value: {value}", value == "red"))
    # ⚑ THE ORIGIN IS WRITTEN IN THE SAME ACT, which is what keeps it from becoming a
    # hand-maintained field that drifts from the value it describes.
    out.append((f"and its origin, in the same act: {origin}", origin == "the-entry-point"))

    def unbound() -> tuple[str | None, str | None]:
        amb = _amb()
        return amb.get(), amb.origin()

    got, org = _fresh(unbound)
    out.append((f"an unbound ambient reads None: {got} / {org}", got is None and org is None))
    return out


def _write_once_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the refusal that is the module's whole reason for being.

    ⚑⚑⚑ THE SAME-VALUE CASE IS THE ONE THAT MATTERS. A second write of a DIFFERENT value is
    obviously wrong and any implementation catches it. A second write of the SAME value looks
    harmless and is the measured defect: two sites each believing they are the one that decides,
    agreeing today with nothing making them agree tomorrow.
    """
    out: list[tuple[str, bool]] = []

    def differing() -> str:
        amb = _amb()
        amb.set("red", "first-site")
        try:
            amb.set("blue", "second-site")
        except am.AmbientConflictError as exc:
            return str(exc)
        return ""

    said = _fresh(differing)
    out.append((f"a second write of a DIFFERENT value refuses: {bool(said)}", bool(said)))
    out.append(
        (
            f"and the refusal names the site that bound it: {'first-site' in said}",
            "first-site" in said,
        )
    )
    out.append(
        (f"and names the site that attempted it: {'second-site' in said}", "second-site" in said)
    )

    def matching() -> str:
        amb = _amb()
        amb.set("red", "first-site")
        try:
            amb.set("red", "second-site")
        except am.AmbientConflictError as exc:
            return str(exc)
        return ""

    same = _fresh(matching)
    out.append((f"a second write of the SAME value ALSO refuses: {bool(same)}", bool(same)))
    # ⚑ AND IT SAYS WHY AGREEMENT IS NOT A REPRIEVE, because a reader who sees the values match
    # will otherwise read the refusal as over-strict and reach for a way around it.
    out.append(
        (
            f"and says agreement is not a reprieve: {'not a reprieve' in same}",
            "not a reprieve" in same,
        )
    )
    return out


def _vocab_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the closed vocabulary."""
    out: list[tuple[str, bool]] = []

    def bad() -> str:
        amb = _amb()
        try:
            amb.set("green", "a-typo-site")
        except am.AmbientVocabError as exc:
            return str(exc)
        return ""

    said = _fresh(bad)
    out.append((f"an out-of-vocabulary value refuses: {bool(said)}", bool(said)))
    listed = "'red'" in said and "'blue'" in said
    out.append((f"and the refusal lists the vocabulary: {listed}", listed))
    return out


def _catchability_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for WHO can catch these refusals.

    ⚑⚑⚑ THE KIND IS CHOSEN BY WHO MUST BE ABLE TO CATCH IT, NOT BY WHAT IT RESEMBLES. A vocabulary
    error reads like a `ValueError`, and making it one would put it back inside the reach of every
    broad advisory handler in the tree — where a refusal prints as a warning and the tool writes
    anyway. These arms assert the base is what the docstring claims.
    """
    out: list[tuple[str, bool]] = []
    shared = issubclass(am.AmbientVocabError, am.MutationContractError) and issubclass(
        am.AmbientConflictError, am.MutationContractError
    )
    out.append((f"the refusals share one base: {shared}", shared))

    # ⚑ THE LOAD-BEARING NEGATIVE: not a ValueError, so `except ValueError` does not swallow it.
    is_value = issubclass(am.AmbientVocabError, ValueError)
    out.append((f"and a vocab error is NOT a ValueError: {not is_value}", not is_value))

    # ⚑ AND NOT A SystemExit — a library that exits unwinds its CALLER's interpreter, and
    # SystemExit derives from BaseException so it slips past every `except Exception` on the way.
    is_exit = issubclass(am.MutationContractError, SystemExit)
    out.append((f"and no refusal is a SystemExit: {not is_exit}", not is_exit))
    return out


def _resolve_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for read-or-bind resolution."""
    out: list[tuple[str, bool]] = []

    def binds() -> str | None:
        return _amb().resolve("a-site", stated="blue")

    bound = _fresh(binds)
    out.append((f"resolve binds when nothing is bound: {bound}", bound == "blue"))

    def reads() -> str | None:
        amb = _amb()
        amb.set("red", "entry")
        return amb.resolve("a-later-site")

    read = _fresh(reads)
    out.append((f"resolve with no stated value READS: {read}", read == "red"))

    # ⚑⚑ AN AGREEING RESTATEMENT IS A NO-OP, which is what lets a site that hardcodes its own
    # value keep working while the guarantee still holds.
    def agrees() -> str | None:
        amb = _amb()
        amb.set("red", "entry")
        return amb.resolve("a-hardcoded-site", stated="red")

    agreed = _fresh(agrees)
    out.append((f"an agreeing restatement passes silently: {agreed}", agreed == "red"))

    # ⚑ AND A DISAGREEING ONE RAISES — the same site, opposite invocation. This is the pair that
    # makes the previous arm mean something: agreement passing is only safe if disagreement does
    # not, and an implementation that always passed would satisfy the arm above.
    def disagrees() -> bool:
        amb = _amb()
        amb.set("red", "entry")
        try:
            amb.resolve("a-hardcoded-site", stated="blue")
        except am.AmbientConflictError:
            return True
        return False

    refused = _fresh(disagrees)
    out.append((f"a disagreeing restatement RAISES: {refused}", refused))
    return out


def _override_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the sanctioned divergence."""
    out: list[tuple[str, bool]] = []
    good = am.Divergence("blue", "the fixture's stated reason", "a-registered-site")

    def runs() -> str | None:
        amb = _amb()
        amb.set("red", "entry")
        amb.override(good, SANCTIONED, announce_to=lambda _m: None).run(amb.get)
        return amb.get()

    def inner_value() -> object:
        amb = _amb()
        amb.set("red", "entry")
        return amb.override(good, SANCTIONED, announce_to=lambda _m: None).run(amb.get)

    inner = _fresh(inner_value)
    out.append((f"an override runs the body under its own value: {inner}", inner == "blue"))

    # ⚑⚑⚑ AND THE OUTER BINDING IS UNTOUCHED, which is the property that separates a scoped
    # override from a re-assignment. Without this arm the override would be indistinguishable
    # from the leak it exists to avoid.
    after = _fresh(runs)
    out.append((f"and the OUTER binding is unchanged: {after}", after == "red"))
    return out


def _override_refusal_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three ways an override is refused."""
    out: list[tuple[str, bool]] = []

    def refused(div: am.Divergence) -> str:
        try:
            _amb().override(div, SANCTIONED, announce_to=lambda _m: None)
        except ValueError as exc:
            return str(exc)
        return ""

    unregistered = refused(am.Divergence("blue", "a reason", "an-unregistered-site"))
    out.append((f"an UNREGISTERED override refuses: {bool(unregistered)}", bool(unregistered)))
    # ⚑ AND IT NAMES ITS SUCCESSORS, because a refusal with none invites a local invention —
    # which is the route-around the whole mechanism exists not to provoke.
    out.append(
        (f"and names its successors: {'Successors' in unregistered}", "Successors" in unregistered)
    )

    no_reason = refused(am.Divergence("blue", "   ", "a-registered-site"))
    out.append((f"an override with no REASON refuses: {bool(no_reason)}", bool(no_reason)))
    out.append(
        (f"and says why a reason is required: {'no-verify' in no_reason}", "no-verify" in no_reason)
    )

    off_vocab = refused(am.Divergence("green", "a reason", "a-registered-site"))
    out.append((f"an off-vocabulary override refuses: {bool(off_vocab)}", bool(off_vocab)))
    return out


def _not_a_context_manager_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for `with` being refused with a named successor.

    ⚑⚑ THE REFUSAL MUST BE THE MODULE'S, NOT PYTHON'S. With only `__enter__` defined, Python
    raises its own "does not support the context manager protocol" before calling anything here —
    a correct refusal carrying no successor, which is the shape this module argues against
    everywhere else. So both halves are defined and this arm asserts whose message arrives.
    """
    out: list[tuple[str, bool]] = []
    amb = _amb()
    over = amb.override(
        am.Divergence("blue", "a reason", "a-registered-site"),
        SANCTIONED,
        announce_to=lambda _m: None,
    )

    try:
        with over:
            pass
    except TypeError as exc:
        out.append(
            (f"`with` is refused: {str(exc).splitlines()[0]}", "not a context manager" in str(exc))
        )
        out.append((f"and the successor is named: {'.run(' in str(exc)}", ".run(" in str(exc)))
    else:
        out.append(("`with` is refused", False))
        out.append(("and the successor is named", False))

    # ⚑ AND `__exit__` EXISTS SO THE MESSAGE ABOVE IS REACHED AT ALL — asserted directly, because
    # deleting it would not fail any arm above in an obvious way, it would change WHOSE error the
    # reader sees.
    halves = hasattr(over, "__exit__") and hasattr(over, "__enter__")
    out.append((f"both protocol halves are defined: {halves}", halves))
    return out


def _declared_cases() -> list[tuple[str, bool]]:
    """Return `(label, passed)` for the three declared ambients.

    ⚑ THE ROSTER IS ASSERTED AGAINST THE DECLARATIONS, never against a typed count. A case pinning
    a number is a second roster, and it drifts the first time a fourth ambient is declared.
    """
    out: list[tuple[str, bool]] = []
    names = [a.kw for a in am.DECLARED]

    out.append((f"the declared ambients are enumerable: {names}", len(names) == len(set(names))))
    out.append(
        (
            f"and DECLARED holds exactly the module's own: {names}",
            set(names) == {"intent", "tenant", "snapshot"},
        )
    )

    # ⚑ EACH DECLARES A CLOSED VOCABULARY AND NAMES THE TWO READINGS IT WOULD CONFLATE — the
    # field that makes a refusal legible rather than merely correct.
    sizes = [len(a.vocab) for a in am.DECLARED]
    out.append((f"each has a closed vocabulary: {sizes}", all(n >= A_CHOICE for n in sizes)))
    readings = [bool(a.two_readings.strip()) for a in am.DECLARED]
    out.append((f"and each names the readings it conflates: {readings}", all(readings)))
    return out


def selftest() -> bool:
    """Run every case, reporting failures by name."""
    cases = (
        _binding_cases()
        + _write_once_cases()
        + _vocab_cases()
        + _catchability_cases()
        + _resolve_cases()
        + _override_cases()
        + _override_refusal_cases()
        + _not_a_context_manager_cases()
        + _declared_cases()
    )
    ok = sum(1 for _, passed in cases if passed)
    for label, passed in cases:
        if not passed:
            print(f"  FAIL {label}")  # noqa: T201
    print(f"ambient selftest: {ok}/{len(cases)}")  # noqa: T201
    return ok == len(cases)


# ⚑ THE FLAG IS NAMED SO `run_selftests.discover()` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    if "--selftest" in sys.argv or len(sys.argv) == 1:
        raise SystemExit(0 if selftest() else 1)
    raise SystemExit(0)
