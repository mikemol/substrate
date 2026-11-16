# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Whether an `item:` check resolves to a witness that can actually close it.

⚑⚑⚑ THE GUARD IT REPLACES SCANS A FILE THE WITNESSES HAVE VACATED. `bibstruct --add` refuses an
`item:<key>` check unless it text-matches `def <KEY>(` or a lambda binding in the project's witness
module. That was right while `catalog/library/items.py` held the bodies; it no longer does — they
moved to the keyed library so a roster and its bodies stop sharing a home, after the origin grew to
2,736 lines carrying 1,804 findings and became uneditable. **So the guard looks where nothing is,
and a key that resolves perfectly at runtime is unwritable.** MEASURED: `items.py R14-v2` answers,
and no `def R14` exists in that file.

⚑⚑ AND THE GUARD'S OWN COMMENT ALREADY NAMED THE RIGHT PREDICATE: *"the predicate that matters is
can `--items <key>` resolve it, which is the dict membership tested below, and the definition check
is the weaker one."* It then tested the weaker one. **This module asks the resolver instead** —
which is not a loosening: it is the same question the GATE asks at check time, so a claim that
passes `--add` is exactly a claim the gate can run.

⚑ THE EXIT CODE IS THE FIRST DISCRIMINATOR, AND THE DISTINCTION IS THE POINT. `2` means the key
resolves to no witness — what this guard must refuse. `1` means the key resolves and its item is
OPEN — a healthy worklist entry, which must be ALLOWED. A guard keyed on "did it pass" would refuse
every honest open item, which is most of a live worklist.

⚑ EXTRACTED RATHER THAN EDITED IN PLACE. `scratch/bibstruct.py` carries 1,367 findings and the
per-file gate refuses every write to it, so the replacement is built whole and the monolith is left
alone until it can be swapped — decompose and replace, never patch behind a gate that cannot pass.
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from substrate import corpus, label_lease

# What the witness module exits when it does not know a key. ⚑ NOT "non-zero": a resolvable key
# whose item is OPEN exits 1, and refusing that would refuse the entire live worklist.
UNKNOWN_KEY = 2

# ⚑⚑⚑ AND EXIT 2 IS TWO DIFFERENT ANSWERS, WHICH COST A REAL FILING BEFORE IT WAS NOTICED. The
# `unwitnessed` kind — the ledger's own honest-gap kind, *"for a judgement or a lesson no command
# can distinguish true from false"* — is DEFINED to report 2. So a registered `unwitnessed` witness
# and an ABSENT one exit identically, and this guard refused the first while meaning the second.
#
# ⚑⚑ MEASURED, IN THE CENSUS BUILT TO CATCH IT: `gate-F58` sits in `findings.py --pairing`'s
# WITNESS-ONLY list — a registered witness whose paired bib entry this guard would not let be
# written. **A guard for roster/record agreement was producing roster/record drift.**
#
# ⚑⚑⚑ SO THE TEST IS A PROPERTY OF THE ANSWER, NOT ONE PHRASE — AND MY FIRST CUT MATCHED ONE
# MODULE'S WORDING, WHICH IS THE DEFECT THIS FIX IS ABOUT. It tested for `findings.py`'s *"no
# witness registered for"*, and `catalog/library/items.py` says *"unknown item key(s)"* instead, so
# four pinned cases went green against a probe that matched nothing. **A census keyed on one
# spelling, inside the repair for a census keyed on one spelling.**
#
# ⚑ A module that CANNOT resolve a key says so with the word UNKNOWN or a not-registered phrase; a
# module answering FOR the key emits its claim. Two witness modules, two wordings, one property.
#
# ⚑⚑⚑ AND EXIT 2 HAS A THIRD MEANING THAT IS NOT THE WITNESS MODULE'S AT ALL — the INTERPRETER'S.
# A module that does not exist exits 2 with *"can't open file"*, which is neither silence nor a
# refusal phrase, so a marker test alone read it as RESOLVED. **Three senders on one exit code**:
# the resolver saying it does not know the key, the resolver answering with an honest gap, and
# python saying it never reached the resolver. Only the middle one resolves.
UNKNOWN_MARKERS = ("no witness registered", "unknown item key", "can't open file")

# Where a project keeps its witnesses, in the order `--add` looks. ⚑ THE PROJECT OWNS THE VERB:
# `paper.toml`'s `[checks.item] cmd` is what resolves a witness at gate time, so the search starts
# beside the bib. The repo-wide fallback keeps every pre-existing caller working, since that is
# where the original project's witnesses live.
WITNESS_NAMES = ("findings.py", "items.py")
FALLBACK = ("catalog", "library", "items.py")

# ⚑⚑⚑ THE PROBE'S TIMEOUT IS A WALL HANG GUARD, NOT A VERDICT — AND IT WAS RENDERED AS ONE. This
# sat at a bare `60` and a `TimeoutExpired` fell into the same `return False` as an unknown key, so
# `refusal()` then printed *"exits 2"* about a probe that never exited at all. MEASURED (t71): the
# witness for gate-G453 PASSES in 86 s and its bib entry was refused twice as *"resolves to no
# witness"* — a reading of the box reported as a fact about the roster, the class W8 had repaired
# in `sync_verdict` an hour earlier. Ruled 2026-09-20: *"Use cputime for your timing gate, not
# wall time."* So the guard is HANG_MULTIPLE x a CPU ceiling (one authority, `label_lease`), a
# crossing REFUSES WITH ITS CAUSE and the CPU the probe burned, and nothing says "exit 2" unless
# the resolver said it.
CPU_CEILING_S = 120
TIMEOUT_S = CPU_CEILING_S * label_lease.HANG_MULTIPLE


@dataclass(frozen=True, slots=True)
class Probe:
    """What asking the resolver established: whether it answers, and if not, why not."""

    resolved: bool
    # Empty when resolved, or when the resolver itself said the key is unknown; otherwise the
    # cause that is NOT "no witness" — a hang-guard crossing, a launch failure.
    cause: str = ""


def witness_module(bib_path: str) -> Path | None:
    """Return the witness module for the project owning `bib_path`, or None.

    ⚑ THE WITNESS FILE IS THE TARGET PROJECT'S, NOT A HARDCODED PATH — and it WAS hardcoded until
    the first other paperkit project in the tree could not file a single entry: a correct refusal,
    aimed at the wrong file, naming a project the filer was not using.
    """
    beside = Path(bib_path).resolve().parent
    for name in WITNESS_NAMES:
        found = beside / name
        if found.exists():
            return found
    fallback = corpus.ROOT.joinpath(*FALLBACK)
    return fallback if fallback.exists() else None


def resolves(module: Path, key: str) -> bool:
    """Report whether `module` can answer for `key` — `probe(...).resolved`, kept for callers."""
    return probe(module, key).resolved


def probe(module: Path, key: str, timeout_s: int = TIMEOUT_S) -> Probe:
    """Ask `module` whether it answers for `key`, carrying the cause when it does not.

    ⚑ `timeout_s` IS A PARAMETER SO THE CROSSING CAN BE DRIVEN in a second rather than eight
    minutes — the arm that pins the cause is otherwise the slowest case in the tree (gate-G362's
    lesson, one module over).

    ⚑⚑ ASKS THE RESOLVER, DOES NOT SCAN THE TEXT. A witness may be a `def` in this file, a lambda
    in a registry dict, or — as the keyed library now does — a binding in another module entirely.
    Only the resolver knows all three, and it is the same one the gate runs.

    ⚑ A PROBE THAT CANNOT RUN REPORTS UNRESOLVED, which refuses the write. That is the safe
    direction here: an entry filed against a witness nobody could reach is
    ordered-but-never-closable, and the ordering surfaces it as work forever.

    ⚑⚑⚑ AND EXIT 2 IS READ WITH ITS MESSAGE, NOT ALONE. The `unwitnessed` kind reports 2 BY DESIGN,
    so an exit-code-only test refused the ledger's own honest-gap kind — measured on `gate-F58`,
    which sits in `--pairing`'s WITNESS-ONLY list because this guard would not let its bib entry be
    written. **A registered witness answering *"I cannot distinguish this"* is a witness that
    RESOLVES; only an UNREGISTERED key does not.**
    """
    before = label_lease.child_cpu()
    try:
        asked = subprocess.run(  # noqa: S603 — argv list, no shell
            [sys.executable, str(module), key],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        # ⚑⚑ A CROSSING IS NOT "NO WITNESS". The probe is killed at the wall guard and the CPU it
        # burned is reported beside it — a hang (no CPU) and an honest slow witness (all CPU) are
        # different next steps, and neither is the roster's fault.
        spent = label_lease.child_cpu() - before
        cause = (
            f"the probe crossed the {timeout_s}s wall hang guard "
            f"({label_lease.HANG_MULTIPLE}x the {CPU_CEILING_S}s CPU ceiling) having spent "
            f"{spent:.1f}s CPU — NOT an unknown key; a witness this slow needs a label so "
            "the ledger can size it"
        )
        return Probe(resolved=False, cause=cause)
    except (OSError, subprocess.SubprocessError) as exc:
        return Probe(resolved=False, cause=f"the probe could not run: {exc}")
    if asked.returncode != UNKNOWN_KEY:
        return Probe(resolved=True)
    # ⚑ BOTH STREAMS, because a refusal may print to either — and reading one is how a
    # message-based discriminator silently becomes an exit-code one again.
    said = (asked.stdout + asked.stderr).lower()

    # ⚑⚑⚑ SILENCE IS NOT AN ANSWER, AND READING IT AS ONE WAS THIS FIX'S OWN FIRST DEFECT. A
    # MISSING module exits 2 saying nothing, so a marker test alone found no marker and reported
    # RESOLVED — the exact inversion the safe-direction rule above forbids. **An absent instrument
    # is not evidence**, so an empty answer refuses.
    if not said.strip():
        return Probe(resolved=False, cause=f"`{module}` exited {UNKNOWN_KEY} saying nothing")

    return Probe(resolved=not any(marker in said for marker in UNKNOWN_MARKERS))


def refusal(module: Path, key: str, cause: str = "") -> str:
    """Return the message for a key that resolves to no witness, or for a probe that could not say.

    ⚑ A CAUSE REPLACES THE "EXITS 2" CLAUSE. That clause is a report of what the resolver said,
    and a probe that was killed or never launched heard nothing; printing it anyway was the
    false "no witness" gate-G453's filing hit twice.
    """
    rel = os.path.relpath(module, corpus.ROOT)
    if cause:
        return (
            f"bibstruct --add: check=item:{key} could not be resolved — {cause}. Refused, "
            "because a witness nobody could reach files as ordered-but-never-closable."
        )
    return (
        f"bibstruct --add: check=item:{key} resolves to no witness — {rel} does not answer "
        f"for it (`{rel} {key}` exits {UNKNOWN_KEY}). The witness must exist FIRST, or the "
        f"item files as ordered-but-never-closable."
    )


def missing_module(bib_path: str, key: str) -> str:
    """Return the message for a project with no witness module at all.

    ⚑ THE FALLBACK IS NAMED AS A DISPLAY PATH, joined with the posix separator rather than built
    as a `Path`. It is text in a refusal, not a location anything opens — and rendering it through
    the filesystem API would invite a reader to treat a message as a handle.
    """
    beside = Path(bib_path).resolve().parent
    return (
        f"bibstruct --add: no witness module to resolve check=item:{key} against — looked "
        f"for {' or '.join(WITNESS_NAMES)} beside {beside}, then "
        f"{'/'.join(FALLBACK)}"
    )
