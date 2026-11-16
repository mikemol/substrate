# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The command line of `gate_status`: dispatch the flags, print the report, return the exit code.

⚑ DRAINED FROM `scripts/gate_status.py` (W330). The tree, the runner and the output stream are
PARAMETERS, so the whole CLI is exercised against a fake runner and a `StringIO`; the shim in
`scripts/` resolves the root from its own location, at call time, and hands them in.

    gate_status.py             # run them all, report verdicts
    gate_status.py --list      # just enumerate what the hook wires
    gate_status.py --modes <script>   # one gate ACROSS ITS FLAG MODES
    gate_status.py --peaks [--lease=<MB>] [--gate=<name>] [--allow-writes]
                               # MEASURE each gate's peak memory, one cgroup-leased run per gate

⚑ `--only=<flag>` IMPLIES `--modes`, AND ITS ABSENCE MADE THE FLAG INERT. Reachable only inside the
`--modes` branch with explicit paths, it fell through to the ordinary hook sweep, which ignored it
and printed every gate's DEFAULT verdict — 13 FAIL rows that were the gates' normal red state, a
result that looked like a measurement and answered nothing. Asking the question implies the mode.

⚑ NO PATHS MEANS THE DISCOVERED FLEET, not an error: "does this flag reach every gate?" is a
question about the POPULATION, and the population is parsed from the hook — the same source
`gates` uses, so it cannot drift from what actually runs. A gate's `argv` is a SHELL FRAGMENT, so
the script is the first `.py` token with `$ROOT` resolved, not the fragment itself.

⚑ `--peaks` MEASURES the fleet's memory footprint; it does not size a cap.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from substrate import gate_status_facts as facts
from substrate import gate_status_peaks as peaks
from substrate import gate_status_run as run

if TYPE_CHECKING:
    from typing import TextIO

    from substrate.gate_status_exec import Runner

#: Exit status for a fleet sweep that found no script to sweep.
USAGE_RC = 2

_USAGE = "usage: gate_status.py --modes <script> [more scripts]\n"
_ONLY = "--only="
_SAMPLE = "--sample="
_LEASE = "--lease="
_GATE = "--gate="
_ALLOW = "--allow-writes"
_MODES_FLAG = "--modes"
_PEAKS_FLAG = "--peaks"
_LIST_FLAG = "--list"
_NAME_WIDTH = 32
_MODE_WIDTH = 11
_COUNT_WIDTH = 3
_ROW_CHARS = 110
_STATUS_WIDTH = 8


def _option(argv: list[str], prefix: str) -> str | None:
    """Return the operand of the first `prefix…` argument, or `None` when absent."""
    return next((a.split("=", 1)[1] for a in argv if a.startswith(prefix)), None)


def fleet(host: run.Host, runner: Runner) -> list[str]:
    """Return the script each hook-wired gate runs: the first `.py` token that exists on disk."""
    scripts: list[str] = []
    for gate in facts.gates(host.tree.hook, runner):
        for tok in gate.argv.split():
            rel = tok.strip('"').replace("$ROOT/", "")
            if rel.endswith(".py"):
                path = host.tree.root / rel
                if path.is_file():
                    scripts.append(str(path))
                break
    return scripts


def _sweep_one(script: str, argv: list[str], host: run.Host, runner: Runner, out: TextIO) -> int:
    """Print one script's modes and return how many answered non-zero."""
    sample = 0
    for a in argv:
        if a.startswith(_SAMPLE):
            sample = int(a.split("=", 1)[1])
    only = _option(argv, _ONLY)
    allow = _ALLOW in argv
    out.write(f"{script}\n")
    wd, why = (False, "") if allow else facts.write_default(script, host.tree.root)
    if wd:
        out.write(f"{facts.WRITE_DEFAULT_HINT}\n")
        out.write(f"     ({why})\n")
    bad = 0
    request = run.ModesRequest(sample=sample, allow_writes=allow)
    for row in run.modes(script, host, request, runner):
        if only and row.mode.strip() != only:
            continue
        flag = "" if row.rc == 0 else "  ← NONZERO"
        out.write(
            f"  {row.mode:<{_MODE_WIDTH}} rc={row.rc}  {row.nlines:>{_COUNT_WIDTH}} line(s)  "
            f"{row.verdict}{flag}\n"
        )
        out.writelines(f"                 │ {r[:_ROW_CHARS]}\n" for r in row.rows)
        if row.rc:
            bad += 1
    return bad


def sweep_modes(argv: list[str], host: run.Host, runner: Runner, out: TextIO) -> int:
    """Run `--modes` / `--only=`: one script (or the whole fleet) under each flag mode."""
    scripts = [a for a in argv[1:] if not a.startswith("-")]
    if not scripts:
        scripts = fleet(host, runner)
        if not scripts:
            out.write(_USAGE)
            return USAGE_RC
    bad = sum(_sweep_one(s, argv, host, runner, out) for s in scripts)
    return 1 if bad else 0


def list_gates(host: run.Host, runner: Runner, out: TextIO) -> int:
    """Print what the hook wires, one line per gate, and the count."""
    gs = facts.gates(host.tree.hook, runner)
    out.writelines(
        f"{'COND' if g.conditional else '    '}  {g.name:<{_NAME_WIDTH}} {g.argv}\n" for g in gs
    )
    unconditional = sum(1 for g in gs if not g.conditional)
    out.write(f"{len(gs)} gate(s) wired ({unconditional} unconditional)\n")
    return 0


def sweep_gates(host: run.Host, runner: Runner, out: TextIO) -> int:
    """Run every wired gate, print its verdict, and return 1 when any is red."""
    gs = facts.gates(host.tree.hook, runner)
    red: list[str] = []
    for gate in gs:
        rc, tail = run.run_gate(gate.argv, host, runner)
        mark = "PASS" if rc == 0 else f"FAIL({rc})"
        cond = "COND " if gate.conditional else ""
        out.write(f"{mark:<{_STATUS_WIDTH}} {cond}{gate.name:<{_NAME_WIDTH}} {tail}\n")
        if rc:
            red.append(gate.name)
    out.write(f"\n{len(gs)} gate(s); {len(gs) - len(red)} pass, {len(red)} FAIL\n")
    out.writelines(f"   red: {n}\n" for n in red)
    return 1 if red else 0


def main(argv: list[str], host: run.Host, runner: Runner, out: TextIO) -> int:
    """Dispatch the flags in `argv` (program name first) and return the exit code."""
    if _MODES_FLAG in argv or any(a.startswith(_ONLY) for a in argv):
        return sweep_modes(argv, host, runner, out)
    if _PEAKS_FLAG in argv:
        lease = _option(argv, _LEASE)
        request = peaks.Request(
            mb=peaks.Request().mb if lease is None else lease,
            only=_option(argv, _GATE),
            writes_ok=_ALLOW in argv,
        )
        return peaks.measure_peaks(host.tree, request, runner, host.environ, out)
    if _LIST_FLAG in argv:
        return list_gates(host, runner, out)
    return sweep_gates(host, runner, out)
