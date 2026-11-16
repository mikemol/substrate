#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The flag vocabulary every gate speaks — now an ADAPTER over mtools' `flag_contract` (W38d).

⚑⚑ THE REFUSALS MOVED; THE SPELLINGS STAYED. mtools row 5b (`mikemol.hooks.flag_contract`) owns
the unknown-flag refusal (`check_flags`) and the state-exactly-one refusal (`exactly_one`), with
every event sent through `refusal_log` to a destination the CALLER names. What stays here is this
repo's policy, which did not travel by design:

- `UNIVERSAL_FLAGS` — `--dry-run` is `set_ratchet`'s vocabulary, so every gate here admits it;
- `TENANT_FLAGS` and the tenant `Choice` — the store policy and its `tenant(require=…)` remedy;
- `arg_after` — it EXTRACTS a value rather than validating one, and mtools' hooks parse their own.

⚑ THE THREE SIGNATURES ARE UNCHANGED, which is why this module keeps its name. Fourteen files
import it directly and ~38 more reach `check_argv` through the `scripts/ratchet.py` facade
(el-openglo among them, by symlink); an adapter here changes none of them.

⚑ WHAT CHANGED, STATED RATHER THAN HIDDEN:
- `SUBSTRATE_EXPLICIT_MUTATION=0` no longer downgrades the mutation refusal to a warning. mtools
  dropped it (a caller wanting advice does not call the refusal), and it has no counterpart here.
- `check_flags` records its "accepted" event BEFORE the mutation/tenant checks run, so a run
  that is then refused for an unstated choice also counts as accepted. The old module recorded
  an accept only on the final return; matching that would mean re-implementing `check_flags`.
- the refusal destination is resolved BY NAME per call (`vlogs_destination.destination()`), not
  read from `SUBSTRATE_VLOGS_URL`.

⚑ THE CASES LIVE IN `ratchet_flags_selftest.py`, NOT IN THIS FILE'S TAIL (⟡n-split-the-tails).
"""

from __future__ import annotations

from mikemol.hooks import flag_contract

from substrate import vlogs_destination

# Flags THIS repo's ratchet implements on every caller's behalf, so no gate needs to declare
# them and none can be missing one. Keep in step with what `set_ratchet` reads.
UNIVERSAL_FLAGS = {"--dry-run"}

# ⚑⚑ THE TENANT VOCABULARY. `store.tenant` resolves these two flags and is the authority on what
# they MEAN; this is the authority on what every tool may SAY. Written out twice — here and at
# `store.TENANT_FLAGS` — and kept in step BY HAND (Ⓗ1ᵈ), blocked on packaging `jea` (Ⓟ25).
TENANT_FLAGS = ("--sandbox", "--live")

# The tenant choice, in `flag_contract`'s terms; mtools left it to this repo because it is store
# policy, and the remedy names the in-code escape at the point of refusal.
TENANT = flag_contract.Choice(
    flags=TENANT_FLAGS,
    subject="This tool reaches a STORE.",
    consequence=(
        "A read that hits the wrong tenant returns PLAUSIBLE ROWS nobody can distinguish; "
        "a write that does is worse."
    ),
    reason="unstated-tenant",
    remedy=(
        "Pass --live or --sandbox.  A caller whose tenant is not the operator's to choose "
        "states it in code: tenant(require='live'|'sandbox')."
    ),
)


def arg_after(argv: object, flag: str) -> str:
    """Return the argument following `flag` in `argv`, or an empty string.

    ⚑ ONE CAPABILITY THAT EXISTED AS FOUR BYTE-IDENTICAL PRIVATE COPIES in the `hook_*` scripts,
    one with zero callers, every one raising `ValueError` on an absent flag. Taking `argv` as a
    parameter is the fix and the testability at once.
    """
    items = flag_contract.rest(argv)
    if flag not in items:
        return ""
    i = items.index(flag)
    return items[i + 1] if len(items) > i + 1 else ""


def mutating_argv(argv: object, label: str) -> int | None:
    """Refuse an UNSTATED mutation intent (`--apply` / `--dry-run`) at the decision point."""
    return flag_contract.exactly_one(
        argv, label, flag_contract.MUTATION, destination=vlogs_destination.destination()
    )


def store_argv(argv: object, label: str) -> int | None:
    """Refuse an UNSTATED tenant (`--sandbox` / `--live`) where a tool says it reaches a store."""
    return flag_contract.exactly_one(
        argv, label, TENANT, destination=vlogs_destination.destination()
    )


def check_argv(
    argv: object, known: object, label: str, *, mutates: bool = False, needs_store: bool = False
) -> int | None:
    """Refuse an unrecognised flag, then any unstated choice. Call this FIRST in every `main()`.

    ⚑ IN SEVERITY ORDER, as `flag_contract` requires: an unknown flag first (a typo'd `--aply`
    must not read as an unstated intent), then MUTATION, then TENANT — a wrong-tenant write is
    worse than a wrong-tenant read, so the mutation contract is satisfied first.

    ⚑ THE TENANT VOCABULARY IS ADMITTED ONLY WHEN DECLARED: a tool that opens no store accepting
    `--live` is a flag that reads as meaningful and does nothing.

    Returns None if fine; otherwise the refusal's exit code, so a caller can
    `if (rc := check_argv(...)) is not None: return rc`.
    """
    names = {str(k) for k in known} if isinstance(known, (list, tuple, set, frozenset)) else set()
    names |= UNIVERSAL_FLAGS
    if needs_store:
        names |= set(TENANT_FLAGS)
    destination = vlogs_destination.destination()
    refused = flag_contract.check_flags(argv, names, label, destination=destination)
    if refused is None and mutates:
        refused = flag_contract.exactly_one(
            argv, label, flag_contract.MUTATION, destination=destination
        )
    if refused is None and needs_store:
        refused = flag_contract.exactly_one(argv, label, TENANT, destination=destination)
    return refused
