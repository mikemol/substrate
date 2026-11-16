#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Read a bib entry's `check` field as a COMMAND, and refuse one born on the wrong polarity.

⚑⚑⚑ WHY THIS EXISTS (gate-F92). `findings.py --register` probes a witness's polarity at filing
time: a `refuses:` command that exits 0 today would be born reporting *the refusal is GONE*
about a finding filed as true, so registration is refused. `bibstruct --add` performs no such
probe — `bib_entry.validate` checks the duplicate key, the required fields, brace balance and
edge targets, and never inspects what a `check` says. So ONE hazard has TWO paths and only one
guard, and the unguarded path is the one that writes the durable record.

⚑⚑ THE MEASURED INSTANCE IS THIS SESSION'S OWN. A `refuses:` check reached a bib entry with its
`--name` flag dropped in transit. It still exits non-zero — but for ARGPARSE rejecting a stray
positional, not for the tool refusing an unknown candidate. Green on the wrong proposition, and
indistinguishable from a correct green by anything downstream.

⚑ THAT IS THE HARD CASE RATHER THAN THE EASY ONE. A gate that fires on nothing is eventually
noticed. A gate that fires for the wrong reason produces findings, passes review, and supplies
evidence for a proposition nobody stated. The remedy is not a stricter parse of the check's
TEXT — no text distinguishes a flagged command from a bare one as a CLAIM — it is RUNNING it
and reading the exit code, which is what the witness path already does.

⚑⚑⚑ AND THE PARSE ITSELF CARRIES THE SAME HAZARD, WHICH IS WHY IT IS NOT NON-WHITESPACE-ONLY.
`bib_entry`'s `ITEM_CHECK` takes one run of non-whitespace, correct for an item key (a slug,
no spaces) and WRONG for a command: it would truncate at the first space and probe a different
command than the one recorded — the very mangling that produced the finding. A command check
runs to the end of the field.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from substrate import witness_polarity

# How a `check` names a command to run, and what polarity that kind requires. ⚑ THE PATTERN
# TAKES THE REST OF THE FIELD, deliberately — see the header. A non-whitespace-only pattern
# here would silently probe a prefix of the recorded command.
COMMAND_CHECK = re.compile(r"(refuses|selftest):(.+)", re.DOTALL)


@dataclass(frozen=True)
class Command:
    """A check that names a command, and the polarity its kind requires."""

    kind: str
    argv: tuple[str, ...]


def command_of(check: str) -> Command | None:
    """Return the command a `check` names, or None when it names no runnable command.

    ⚑ A CHECK THIS DOES NOT RECOGNISE IS NOT A DEFECT. `item:`, `unwitnessed` and `standing`
    are all legitimate and none is a command, so the guard must fall through rather than
    refuse — the same contract `bib_entry.witness_key` keeps for a non-item check.
    """
    found = COMMAND_CHECK.match(check.strip())
    if found is None:
        return None
    # ⚑ THE ANNOTATIONS NARROW AT THE SEAM. `Match.group` is `str | Any`, and under
    #   `disallow_any_expr` that `Any` poisons every downstream expression, so each group is
    #   bound to a declared `str` before it is used rather than laundered through a cast.
    kind: str = found.group(1)
    rest: str = found.group(2)
    argv = tuple(w for w in rest.strip().split() if w)
    if not argv:
        return None
    return Command(kind, argv)


def refusal(check: str, cwd: str) -> str | None:
    """Return why this `check` must not be written, or None when it may be.

    ⚑ THE PROBE IS THE SAME ONE THE WITNESS PATH RUNS. Reusing `witness_polarity` rather than
    re-deriving the polarity rule here is the point: two spellings of one relation is the
    defect this ledger keeps paying for, and the whole finding is that the two paths had
    different coverage of one hazard.
    """
    got = command_of(check)
    if got is None:
        return None
    verdict = witness_polarity.probe(list(got.argv), got.kind, cwd)
    if verdict is None:
        return None
    return (
        f"bibstruct --add: this `check` would be written on the wrong polarity.\n{verdict}\n"
        "⚑ THE ENTRY IS THE DURABLE RECORD, so a check that is green for the wrong reason "
        "outlives the session that wrote it. Fix the command, or file the claim under a kind "
        "that does not assert an exit code."
    )
