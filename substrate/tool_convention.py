#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""A flag whose MEANING is shared across tools — and the invoker that makes it so.

⚑⚑⚑ A CONVENTION IS NOT A NAME THAT RECURS; IT IS A NAME SOMETHING INVOKES. `--selftest` is a
convention because `run_selftests` dispatches `python <path> --selftest` against every discovered
suite — the flag is a property of the RUNNER. `--top` recurs across nine tools and is NOT one:
nothing invokes it, the nine just chose the same word. Counting cannot separate those — a
`--hidden` on 2 of 3 tools is a MAJORITY and emphatically not a convention — which is why every
record carries an invoker instead of a threshold.

⚑⚑ MODELLED ON gcalculus `farm.py`'s `Arm`, AND THE LOAD-BEARING FIELD IS THE SAME ONE. An F-arm
declares the MESSAGE its mutation must provoke, because *"it went red" is not evidence — "it went
red HERE, saying THIS" is*. A convention declares the INVOKER that makes the flag shared, because
*"many tools accept it"* is not evidence — *"this runner dispatches it against every tool"* is.
Both replace a popularity signal with a structural one, and both make the claim falsifiable: an
`Arm` that stops biting is VACUOUS, a `Convention` whose invoker stops invoking is STALE.

⚑ THE INVOKER MAY BE A DISCIPLINE RATHER THAN A DISPATCHER, and two records say so in as many
words — `--apply` and `--roundtrip` carry `(none — …)`. What is not permitted is leaving the
field unargued: a convention with no warrant of either kind is a popularity claim wearing a
record's clothes.

⚑ SINGLE-HOMED SO REUSE IS DECLARED RATHER THAN COINCIDENTAL. The census, the collision report
and any future gate read the same records, so *"is `--apply` a convention?"* has one answer. A
second list beside this one is the frozen-roster shape the whole census exists to retire.

⚑ EXTRACTED FROM `scratch/toolmodes.py` (⟡toolmodes-layers), 2,196 findings, refused whole by the
per-file gate. The cut continues until the dispatch moves out and the original is retired.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Convention:
    """One flag whose meaning is owned here rather than re-argued per tool.

    Fields deliberately mirror `Arm(key, file, find, replace, expect, why)`:

      flag      the spelling, e.g. `--selftest`
      invoker   the module that DISPATCHES it across tools — the structural warrant
      contract  what a tool accepting it PROMISES; the shared semantics, one line
      why       the argument: what recurrence-without-an-invoker would look like, and what a
                reader loses if this is read as N per-tool modes instead of one
    """

    flag: str
    invoker: str
    contract: str
    why: str


# Each entry is a flag whose meaning is OWNED here rather than re-argued per tool. Adding one is
# how a recurring flag earns the claim that it is a shared contract.
CONVENTIONS = (
    Convention(
        flag="--selftest",
        invoker="scripts/run_selftests.py",
        contract="run this tool's guarded cases; exit 0 iff all pass, and emit a typed "
        "`rungs.record` rather than prose.",
        why="the runner DISCOVERS suites (an entry point plus a selftest body) and dispatches "
        "`python <path> --selftest` at each — so the flag is the runner's, and a tool "
        "spelling it via argparse instead of an argv compare does not make it that tool's "
        "own invention. Reported per-tool it put 27 identical rows in a census whose whole "
        "value is that a row MEANS something.",
    ),
    Convention(
        flag="--apply",
        invoker="(none — the writers' shared discipline, not a dispatcher)",
        contract="PERFORM the change. ⚑ MUTUALLY EXCLUSIVE WITH `--dry-run` AND ONE IS "
        "REQUIRED: a mutating tool invoked with NEITHER must REFUSE, never guess.",
        why='⚑⚑ NO DEFAULT IN EITHER DIRECTION (operator, 2026-08-18: *"no default-dry, no '
        'default-apply, only explicit behavior"*). A default-dry tool silently does nothing '
        "when the caller meant to write; a default-apply tool silently writes when the "
        "caller meant to look. BOTH failures are silent, and which one you get is a property "
        "of whichever tool you happened to invoke — so the caller must carry the decision. "
        "⚑ 32 tools accept it with identical semantics, which is why declaring it stops a "
        "33rd inventing `--write` or `--fix`. But the CONTRACT is the pair, not the flag. "
        "→ ⟡explicit-mutation",
    ),
    Convention(
        flag="--quiet",
        invoker="the pre-commit hook (gates run under it)",
        contract="print only on FAILURE; a passing run says nothing.",
        why="gate-shaped tools only. ⚑ `ratchet.check_argv` records what a mis-spelling costs: a "
        "typo'd `--queit` degraded FIVE gates to verbose-but-passing, all exit 0 — so this "
        "flag's contract is load-bearing for whether a green build means anything.",
    ),
    Convention(
        flag="--dry-run",
        invoker="scripts/ratchet.py (UNIVERSAL_FLAGS, merged into every gate's known-set)",
        contract="report what WOULD change and change nothing. ⚑ MUTUALLY EXCLUSIVE WITH "
        "`--apply` AND ONE IS REQUIRED: neither stated is a REFUSAL, not a default.",
        why="⚑ IT IS `--apply`'s MIRROR AND THE PAIR IS THE CONVENTION — not either flag alone. "
        "The merge into every gate's known-set IS this contract, already single-homed. "
        "⚑⚑ AND `--dry` IS THE SAME CONTRACT MISSPELLED, MEASURED: three tools write by "
        "default and suppress on `--dry`; none accepts `--dry-run`, and none calls "
        "`check_argv`, so a typo'd `--dry` in any of them silently WRITES. That is a "
        "CONVERGE, not a second declaration — giving the misspelling its own record is "
        "exactly how a split becomes permanent. → ⟡dry-converge",
    ),
    Convention(
        flag="--sandbox",
        invoker="jea/metalanguage/store.py::sandbox_connect (1 def, 30 call sites)",
        contract="run against the THROWAWAY tenant. ⚑ THE TENANT MUST BE STATED: where live and "
        "sandbox could differ, a tool with neither `--sandbox` nor an explicit live "
        "selector must REFUSE. No default tenant, in either direction.",
        why="⚑⚑ NO DEFAULT TENANT (operator, 2026-08-18). THREE failure modes, and the third is "
        "the one a default guarantees: forgetting to care is indistinguishable from "
        "choosing. ⚑ MEASURED IN BOTH DIRECTIONS — `--fibre --sandbox` once reported the "
        "LIVE store's cores under the sandbox's question, because WRITE modes honoured the "
        "flag while READ modes ignored it; and a probe returned sandbox rows three orders of "
        "magnitude low *looking exactly like an answer*. → ⟡explicit-tenant",
    ),
    Convention(
        flag="--roundtrip",
        invoker="(none — the parsers' shared precondition)",
        contract="LOSSLESSNESS GATE: does parse→emit reproduce this artifact? Report what "
        "changed, not merely pass/fail.",
        why="`bibstruct`, `mdstruct` and `pycodemod` each own a parser, and each must answer the "
        "same question before any transform runs. ⚑ AND THE ANSWER DIFFERS BY ARTIFACT "
        "WITHOUT THE CONTRACT DIFFERING: libcst is lossless by construction so one arm is a "
        "formality, while pandoc NORMALIZES so another is expected to report changes — which "
        "is why the contract says *report what changed*. A pass/fail spelling would have "
        "made the markdown arm unusable and invited a fourth name for one precondition.",
    ),
)

# ⚑ DERIVED, NOT A SECOND LIST. `universal` consumes this; nothing else may keep its own copy.
# The set-of-flags spelling is retained because every reader wants membership, but the RECORDS
# are the authority and the set is a projection of them.
HARNESS_CONTRACTS = frozenset(convention.flag for convention in CONVENTIONS)

# ⚑⚑⚑ `--top`/`--skip` ARE DELIBERATELY *NOT* DECLARED HERE, AND THIS MODULE'S OWN TEST IS WHY.
# `substrate/page.py` was built this session to give listings a deterministic bound, and `--top`
# was chosen over `--limit` precisely because the census reports it on NINE tools against one —
# so the temptation to declare it a convention is exactly the popularity signal the record shape
# exists to refuse. **Nothing INVOKES it.** `page` is a library a tool opts into at its own call
# site; no runner dispatches `--top` across the corpus the way `run_selftests` dispatches
# `--selftest`, and no shared known-set merges it the way `ratchet.UNIVERSAL_FLAGS` merges
# `--dry-run`.
#
# ⚑⚑ AND THE HONEST READING IS THAT IT IS NOT YET ONE, not that it never can be. Two of the six
# records carry `(none — …)` as their invoker, so a DISCIPLINE counts — but both name the
# discipline and argue it. `--top`/`--skip` would earn a record when either a runner dispatches
# them or the pair becomes a stated obligation on listing modes (as `--apply` XOR `--dry-run` is
# on mutating ones). Declaring it before that would make this list a tally of what recurs, which
# is the frozen-vocabulary shape every other entry here was written to avoid.
#
# ⚑ SO IT SITS IN THE UNDECLARED-RECURRENCE REPORT, WHICH IS THE CORRECT PLACE FOR IT: visible,
# counted, and named as a DECLARE-or-CONVERGE decision rather than silently blessed. → ⟡top-skip


def by_flag(flag: str) -> Convention | None:
    """Return the convention declaring `flag`, or None when it is not one."""
    return next((c for c in CONVENTIONS if c.flag == flag), None)


def universal(accepted: tuple[frozenset[str], ...]) -> frozenset[str]:
    """Return the flags MOST tools accept — a convention, not a per-tool mode.

    ⚑ MEASURED, NOT DECLARED IN A LIST. Reporting `--selftest` once per tool put dozens of
    identical rows in a census whose whole value is that a row means something. A hardcoded
    "ignore these" set would be the frozen vocabulary this toolkit keeps retiring; a measure over
    the roster moves on its own when a convention is added or dropped.

    ⚑⚑ THE INTERSECTION WAS PASSING ON BORROWED EVIDENCE, AND CLOSING A LEAK EXPOSED IT.
    `--selftest` is an argv compare in five tools and an argparse registration in another, so a
    strict intersection over `accepted` should never have held — it did only because the one-hop
    import walk leaked a CLI sibling's flags into every importer. Fixing that correctly dropped
    the flag from three tools, and the intersection then reported ZERO conventions.

    ⚑ SO THE UNION WITH THE DECLARED CONTRACTS IS WHAT KEEPS THIS HONEST: the measured arm stays
    alive for anything genuinely unanimous, and the declared arm covers what an invoker makes
    shared without every tool happening to accept it.
    """
    if not accepted:
        return frozenset()
    measured = frozenset.intersection(*accepted)
    declared = frozenset(flag for flag in HARNESS_CONTRACTS if any(flag in one for one in accepted))
    return measured | declared
