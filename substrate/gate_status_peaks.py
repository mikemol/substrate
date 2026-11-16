# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""`gate_status --peaks`: run each hook-wired gate under a membudget lease, RECORDING its maxRSS.

⚑ WHY THIS IS A MODE AND NOT A LOOP AT THE SHELL. Asked "what is the memory cap on the Python
stages", the measured answer was: there is none, and nothing had ever measured them. The agda shim
budgets compiles by PATH interposition and has no Python counterpart, so the population was
unmeasured, and measuring it by hand is one invocation per gate plus a tally — reasoning in the
turn.

⚑ IT MEASURES, IT DOES NOT SIZE. `membudget peaks` reads the history back and SUGGESTS a bucket;
nothing applies it. A lease chosen for an agda module and applied to a Python suite is what made
`worklist_gate` read `unfit`.

⚑ THE DEFAULT LEASE IS 32MB, AND THE FIRST DEFAULT (4096MB) DEADLOCKED THE SWEEP (user, 2026-08-05).
A lease is not an observation window, it is an EXCLUSION: reserving 4096MB does not observe 4096MB,
it forbids everyone else memory the gate never touches. MEASURED over 65 labels: 58 are <= 40MB, the
median ~20MB. So the default sits BELOW the fleet median deliberately, and the RETRY LADDER does the
discovering. Over-size only with `--lease=`, knowing it buys exclusion, not observation.

⚑ THE LADDER STAYS ON AND ITS FIRING IS THE FINDING. With it off a heavy stage is KILLED and nothing
is recorded, so the heaviest members would erase themselves from the ledger. With it on the stage
escalates, succeeds, and records its real peak; what was missing is that the escalation was
invisible. The client announces each retry on stderr as `retrying at NNNMB`, and this sweep reads
that line.

⚑ THE PARSE SURVIVES A CLIENT SWAP. The python membudget client prints `retrying at NNNMB` (pinned
by mtools' `test_membudget_cli.py`) and exits 137 on a cap kill (143 when terminated), which are the
only two facts read here: the client's path is `substrate.build_settings.MEMBUDGET`, passed in by
the caller, and the process runner is INJECTED so the suite never starts a real lease.

⚑ THE ADVICE STRINGS ARE FORMATTED FROM THE CLIENT'S REPO-RELATIVE PATH, so they name the program
that was actually run rather than a spelling frozen here.
"""

from __future__ import annotations

import re
import shlex
from typing import TYPE_CHECKING, NamedTuple, cast

from substrate import gate_status_facts as facts
from substrate.gate_status_exec import TIMEOUT_RC

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import TextIO

    from substrate.gate_status_exec import Runner

#: Exit statuses that mean the cap (or a terminate) ended the run: SIGKILL and SIGTERM, shell-style.
OOM_RCS = (137, 143)

#: The ladder's own announcement; the last one is where the stage finally fit.
CLIMB = re.compile(r"retrying at (\d+)MB")

#: A peak measurement may take this long per gate before it is recorded as a timeout.
PEAK_TIMEOUT_S = 900

#: Exit statuses that are a gate's verdict (pass / red) rather than a failure to complete.
VERDICT_RCS = (0, 1)

_NAME_WIDTH = 34
_LABEL_CHARS = 40
_RETRY_ENV = "MEMBUDGET_RETRY_OOM"


class Request(NamedTuple):
    """What to measure: the lease, an optional gate-name filter, and the write opt-in."""

    mb: str = "32"
    only: str | None = None
    writes_ok: bool = False


class Row(NamedTuple):
    """One gate's measurement."""

    name: str
    label: str
    rc: int
    conditional: bool
    over: bool
    landed: str | None


def label_for(name: str) -> str:
    """Return the ledger label a gate is leased under."""
    return "gate:" + re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")[:_LABEL_CHARS]


def advice(tree: facts.Tree) -> str:
    """Return the command that reads the recorded peaks, spelled from the client's repo path."""
    try:
        shown = tree.membudget.relative_to(tree.root)
    except ValueError:
        shown = tree.membudget
    return f"{shown} peaks"


def measure_one(
    gate: facts.Gate,
    tree: facts.Tree,
    mb: str,
    runner: Runner,
    environ: Mapping[str, str],
) -> Row:
    """Run one gate under a lease and return how far up the ladder it climbed."""
    cmd = facts.expand(gate.argv, tree.root)
    label = label_for(gate.name)
    client = shlex.quote(str(tree.membudget))
    full = f"{client} run {shlex.quote(mb)} {shlex.quote(label)} -- {cmd}"
    env = dict(environ)
    env[_RETRY_ENV] = "1"
    outcome = runner(full, tree.root, env, PEAK_TIMEOUT_S)
    blob = outcome.stderr + outcome.stdout
    climbs = [cast("str", m.group(1)) for m in CLIMB.finditer(blob)]
    over = bool(climbs) or outcome.rc in OOM_RCS
    landed = climbs[-1] if climbs else None
    return Row(gate.name, label, outcome.rc, gate.conditional, over, landed)


def note_for(row: Row, mb: str) -> str:
    """Return the one-line reading of a row."""
    if row.landed:
        return f"OVER {mb}MB → fit at {row.landed}MB  ← heavy"
    if row.rc in OOM_RCS:
        return f"OVER {mb}MB, never fit  ← heavy"
    return f"rc={row.rc}"


def report_row(row: Row, mb: str) -> str:
    """Render a row as the sweep prints it."""
    tag = "  (conditional)" if row.conditional else ""
    name = f"{row.name[:_NAME_WIDTH]:<{_NAME_WIDTH}}"
    return f"  {name} {row.label:<{_LABEL_CHARS}} {note_for(row, mb)}{tag}\n"


def _where(landed: str | None) -> str:
    """Return where a heavy gate landed on the ladder."""
    return f"fit at {landed}MB" if landed else "never fit (no peak recorded)"


def summarise(rows: list[Row], mb: str, tree: facts.Tree) -> list[str]:
    """Render the heavy gates, the gates that did not complete, and the pointer to the peaks."""
    lines = ["\n"]
    heavy = [r for r in rows if r.over]
    if heavy:
        lines.append(
            f"⚑ {len(heavy)} gate(s) exceeded {mb}MB — the heavy ones, with where they landed:\n"
        )
        lines.extend(f"    {r.name:<40} {_where(r.landed)}\n" for r in heavy)
        lines.append(f"  their measured peaks:  {advice(tree)}\n")
    else:
        lines.append(f"no gate exceeded {mb}MB — the whole fleet fits the sieve.\n")
    bad = [r for r in rows if r.rc not in VERDICT_RCS and not r.over]
    if bad:
        lines.append(
            f"⚑ {len(bad)} gate(s) did not complete for OTHER reasons (no peak recorded):\n"
        )
        lines.extend(
            f"    {r.name:<40} rc={r.rc}{' (timeout)' if r.rc == TIMEOUT_RC else ''}\n" for r in bad
        )
    lines.append("\n")
    lines.append(f"peaks for what DID fit:  {advice(tree)}\n")
    return lines


def measure_peaks(
    tree: facts.Tree,
    request: Request,
    runner: Runner,
    environ: Mapping[str, str],
    out: TextIO,
) -> int:
    """Run each wired gate under a membudget lease, print the table, and return 0.

    ⚑ `request.writes_ok` IS CARRIED FOR THE CLI AND READ BY NOTHING, as in the origin: each gate
    runs with the argv THE HOOK USES, which is the safe form by construction, and "the hook's argv"
    is not a guarantee anyone re-derives — so the opt-in stays on the request until it has a reader.
    """
    rows: list[Row] = []
    for gate in facts.gates(tree.hook, runner):
        if request.only and request.only not in gate.name:
            continue
        row = measure_one(gate, tree, request.mb, runner, environ)
        rows.append(row)
        out.write(report_row(row, request.mb))
    out.writelines(summarise(rows, request.mb, tree))
    return 0
