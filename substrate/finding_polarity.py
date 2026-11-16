#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Refuse a witness that would be BORN reporting the opposite of its own finding.

⚑⚑⚑ THE DISCRIMINATOR IS EXECUTION, NOT INSPECTION, AND IT IS FREE AT FILING TIME. Nothing in
a command's TEXT separates a CENSUS (reports a value, exits 0 on zero rows exactly as on many)
from a PREDICATE (reports an exit code) — `pycodemod --literal … ` and `schema.py --cancel
99999999` are the same shape. So a static check is impossible in principle. But the witness
will run this command on every `--list` anyway; running it ONCE MORE, now, answers the only
question that matters: does it exit the way this kind requires TODAY.

⚑⚑ THE MEASURED CASE IS `gate-F38`. A `refuses:` command returned 0 sites with exit 0, and the
freshly-filed witness immediately reported *the refusal is GONE* against a finding that was
perfectly true. That registration is now refused at the point of filing rather than banked and
rediscovered by whoever reads the ledger next.

⚑ WHAT THIS DOES NOT DETECT IS CENSUS-NESS, and saying so is the honest boundary. A census
whose zero result happens to exit non-zero would still register as `refuses:` and would still
be a category error this cannot see. What it DOES guarantee is that no witness is born
reporting the opposite of the finding it was filed to hold — the shape that actually cost a
false verdict.

⚑⚑⚑ AND THE `mode:` ARM IS NEW HERE (Ⓝ162⁗), BLOCKED IN THE ORIGIN FOR THE WHOLE ARC. The
origin probes `refuses` and `selftest` and returns three lines earlier for `mode`, so a `mode:`
witness registered unprobed — and `gate-F55` was filed with one reporting DOCUMENTED under a
claim that the flag IS documented-as-a-redirect and not dispatched: the opposite polarity of
its own finding, caught only by a manual run. The arm is unambiguous because
`_mode_undocumented` returns 0 on EXACTLY ONE path, the DOCUMENTED branch; both *still
dispatches undocumented* and *the mode is GONE* return 1, deliberately, since a finding is not
closed by the deletion of its subject.
"""

from __future__ import annotations

from substrate import finding_kinds

# The kinds whose polarity a probe can decide, and what exit code each REQUIRES at filing time.
# ⚑ `standing` AND `unwitnessed` ARE ABSENT BY CONSTRUCTION, not by omission: neither runs a
#   command, so neither has a polarity to be born wrong about.
PROBED: tuple[str, ...] = ("refuses", "selftest", "mode")


def _did_not_run(cmd: list[str], out: str) -> str:
    """Return the refusal for a command that could not start."""
    return ("the command for this witness DID NOT RUN, so it would report 2 forever while "
            f"looking mechanical — an absent instrument is not evidence:\n    {' '.join(cmd)}\n"
            f"    {out[:200]}")


def _refuses_is_gone(cmd: list[str], out: str) -> str:
    """Return the refusal for a `refuses:` command that currently exits 0.

    ⚑ TWO CAUSES, AND THEY NEED DIFFERENT ANSWERS — so the refusal names both rather than
    asserting one. Picking a cause here would be the same over-reach the kind system exists to
    prevent, one layer up.
    """
    return ("this `refuses:` command EXITS 0 RIGHT NOW, so the witness would be born reporting "
            "*the refusal is GONE* about a finding you are filing as true:\n"
            f"    {' '.join(cmd)}\n"
            "⚑ TWO CAUSES, AND THEY NEED DIFFERENT ANSWERS. (a) The refusal genuinely is not "
            "installed — then the finding is OPEN and `refuses:` is right but premature. (b) "
            "This is a CENSUS, not a predicate: it reports a VALUE and exits 0 whether it finds "
            "zero rows or many, so no exit code can carry the claim. That is the gate-F38 case "
            "and its honest kind is `unwitnessed`, naming the census value as the discriminating "
            "quantity no registered kind reads.\n"
            f"    last output: {finding_kinds.evidence(out)}")


def _selftest_is_open(cmd: list[str], code: int, out: str) -> str:
    """Return the refusal for a `selftest:` command that currently fails."""
    return (f"this `selftest:` command EXITS {code} RIGHT NOW, so the witness would be born "
            "OPEN — file the finding only once the mechanism it asserts actually holds, or use "
            f"`unwitnessed` if no command can carry the claim:\n    {' '.join(cmd)}\n"
            f"    {finding_kinds.evidence(out)}")


def _mode_is_documented(cmd: list[str], out: str) -> str:
    """Return the refusal for a `mode:` witness that currently reports DOCUMENTED.

    ⚑⚑ THIS ARM IS DECIDABLE BECAUSE THE UNDERLYING READER HAS EXACTLY ONE ZERO-PATH. Both
    *still dispatches undocumented* and *the mode is GONE* return 1 — the second deliberately,
    because a finding is not closed by the deletion of its subject. So exit 0 at filing time
    means DOCUMENTED and nothing else, and a `mode:` finding asserts the reverse.

    ⚑ AND THE NEAREST HONEST KIND IS NAMED, since the measured instance had one. `gate-F55`
    found a flag documented AS A REDIRECT and not dispatched — no predicate distinguishes that
    from documented-as-a-mode, which is `unwitnessed` by definition.
    """
    return ("this `mode:` witness reports DOCUMENTED RIGHT NOW, so it would be born asserting "
            "the opposite of a finding filed because the mode is UNDOCUMENTED:\n"
            f"    {' '.join(cmd)}\n"
            "⚑ THE READER HAS EXACTLY ONE ZERO-PATH, so this is unambiguous: both *dispatches "
            "undocumented* and *the mode is GONE* report 1. Exit 0 means the tool declares it.\n"
            "⚑ IF THE MODE IS DOCUMENTED IN A WAY THE CLAIM DISPUTES — a redirect, a prose "
            "mention, a usage line for a flag that no longer dispatches — no predicate separates "
            "that from an ordinary declaration, and `unwitnessed` is the honest kind.\n"
            f"    last output: {finding_kinds.evidence(out)}")


def probe(cmd: list[str], kind: str) -> str | None:
    """Return None if `cmd` already exits the way `kind` requires, else a REFUSAL string.

    ⚑ A COMMAND THAT CANNOT RUN IS REFUSED TOO, NEVER WAVED THROUGH. Registering then files a
    witness that reports UNRUNNABLE forever while looking mechanical — an absent instrument is
    not evidence, applied at the filing site rather than only at the reading site.
    """
    if kind not in PROBED:
        return None
    code, out = finding_kinds.run(*cmd)
    if code is None:
        return _did_not_run(cmd, out)
    if kind == "refuses" and code == 0:
        return _refuses_is_gone(cmd, out)
    if kind == "selftest" and code != 0:
        return _selftest_is_open(cmd, code, out)
    if kind == "mode" and code == 0:
        return _mode_is_documented(cmd, out)
    return None
