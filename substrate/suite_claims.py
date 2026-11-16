#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Which artefact a suite must hold exclusively while it runs — the exclusion policy.

⚑⚑ EXCLUSION IS DECLARED, NOT INFERRED, AND THE DIRECTION MATTERS. A census DISCOVERS which
suites reach a store; a declaration ENFORCES it. Inference alone is a false-safe — a suite
mutating through a path the census cannot trace would run concurrent with itself — while
over-declaring is only slower. So where the two disagree, the declaration wins.

⚑ THE LABEL IS THE MECHANISM. `membudget run <mb> claim:<artefact> -- …` treats that label as
an EXCLUSIVE lock: at most one live lease may carry it, every other label unaffected. No
scheduler, no registry, no lockfile — and the claim's lifetime IS the holder process's
lifetime, so the kernel releases it on any exit including SIGKILL.

⚑⚑ TWO ARTEFACTS, GUARDING TWO DIFFERENT FAILURES, and collapsing them would lose the
distinction:

    pg      several suites open the ONE postgres. The Agda build records what this costs when
            ungated: *"ENOUGH CONCURRENCY THROWN AT THE POSTGRES BACKEND CAUSED KERNEL HANGS"*.
    roster  a suite that RUNS the roster containing it forks at BREADTH when two of them run
            at once. The runner's own re-entrancy marker guards DEPTH — an inner run elides
            itself. Depth and breadth are different failures and each needs its own guard.

⚑ `pg` IS THE DEGENERATE CASE OF A POOL, AND SAYING SO NOW IS WHAT KEEPS IT HONEST LATER. If
the store safely carries N concurrent sessions this is a lease over a SET of N slots rather
than an exclusive lock — the same machinery at |members| = N. N is the store's real
concurrent-session ceiling minus headroom: a MEASURED number with one authority, never a
figure typed here. Until it is measured, one holder is the conservative answer.
"""

from __future__ import annotations

from substrate import tenant_pragma

# The one postgres. A suite declaring a tenant, or one the reach census finds, holds this.
PG = "pg"

# The suite roster itself. A suite that runs the roster containing it holds this.
ROSTER = "roster"


def claim_for(
    label: str, path: str, reaching: frozenset[str], fanout: frozenset[str]
) -> str | None:
    """Return the artefact this suite must claim exclusively, or None.

    ⚑ ROSTER OUTRANKS PG WHEN BOTH APPLY. A suite that runs the roster will itself invoke
    every pg-claiming suite, so holding `pg` for its whole duration would deadlock against its
    own children — the outer claim is the one that must be exclusive.
    """
    if label in fanout:
        return ROSTER
    if tenant_pragma.tenant(path) or path in reaching:
        return PG
    return None


def label_for(label: str, path: str, reaching: frozenset[str], fanout: frozenset[str]) -> str:
    """Return the membudget label for this suite: a claim, else a plain identifier.

    ⚑ A NON-CLAIMING SUITE STILL GETS A NAMED LABEL, because the label is what the lease
    ledger keys on — `auto` sizing reads that suite's own recorded peaks. An unnamed lease
    would size from nothing and silently take the default.
    """
    claim = claim_for(label, path, reaching, fanout)
    if claim:
        return f"claim:{claim}"
    return f"selftest:{path.rsplit('/', 1)[-1]}"


def reaching_store(suites: list[tuple[str, str]]) -> frozenset[str]:
    """Return the paths of suites that declare a tenant.

    ⚑ THE DECLARATION IS THE SOURCE HERE, not the import-reach census. `tenant_census` is the
    richer instrument and its two lenses disagree on the deferred rows by design; this policy
    wants the conservative half — what a suite SAYS about itself — with the census available
    as a cross-check rather than as the input.
    """
    return frozenset(path for _label, path in suites if tenant_pragma.tenant(path))
