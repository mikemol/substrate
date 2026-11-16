#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Walk this process's PPID chain, and refuse a re-entrant invocation.

Extracted from `ratchet.py` as part of ⟡ratchet-seams. Process-tree introspection has
nothing to do with ratcheting a census; it lived there because that is where the fork
bomb was diagnosed, the same way the VictoriaLogs ingest did.

⚑⚑ ⟡worklist-gate-recursion, 2026-08-24. TWO TOOLS EACH DOING THE RIGHT THING COMPOSED
INTO AN UNBOUNDED FORK BOMB, and neither was wrong on its own:

    worklist_gate --selftest   wants to know the selftests pass, so it runs run_selftests
    run_selftests              runs every tool's --selftest, and worklist_gate HAS one

The roster contains its own caller. Measured off a live `ps` tree, four generations
deep: **load average 54.93 on a 10-core box, 68 concurrent selftest processes**, with
~28 postgres backends starved alongside — which was misdiagnosed as a database problem
because `--locks` reported ZERO lock-waiting. It was never contention. A machine-shaped
cause wearing a database-shaped symptom.

⚑ THE FIX IS SYMMETRIC AND MUST BE. If only the callee guards, the caller still forks a
generation before being refused; if only the caller guards, a hand-run callee re-enters.
Both ends check the same marker against the same ancestry — which is why this is one
shared function and not two local guards. A shared NAME is not a shared authority, but a
shared FUNCTION is.

⚑ ITS TWO EXTERNAL CONSUMERS ARE `run_selftests` AND `worklist_gate` — exactly the pair
the fork bomb ran between. Both import through `ratchet`, so that re-export stays and
the split is invisible to them.

⚑ THE CASES LIVE IN `proc_ancestry_selftest.py`, NOT IN THIS FILE'S TAIL
(⟡n-split-the-tails). They were inline until a coverage census counted that as a convention
rather than as debt; operator: *"n-split that crap. No more in-line/tail testing."* Inline cases
cannot run without importing the module under test, and a module too dirty to edit takes its own
suite hostage.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# A malformed `/proc` must not spin the walk; no real chain is anywhere near this deep.
_MAX_HOPS = 64

# ppid is the 4th field of `/proc/<pid>/stat`, counted after the parenthesised comm.
_PPID_OFFSET_AFTER_COMM = 1

# How much of an offending command line the refusal prints per row.
_CMDLINE_WIDTH = 120

#: The argv[0] basenames of processes that CARRY a command line rather than BEING one.
#: ⚑ A WRAPPER'S CMDLINE QUOTES THE COMMAND IT LAUNCHED, which is what makes a marker
#: naming that command match the launcher as well as any genuine ancestor invocation.
#: These are the layers the incident chain actually crosses — `membudget run` shells out,
#: which execs `/usr/bin/time -v`, which execs the interpreter — plus the `bash -c` the
#: harness and every `subprocess(shell=True)` wrap a command in.
_WRAPPER_ARGV0 = frozenset(
    (
        "sh",
        "bash",
        "dash",
        "zsh",
        "ksh",
        "env",
        "time",
        "nice",
        "ionice",
        "timeout",
        "stdbuf",
        "xargs",
        "sudo",
        "systemd-run",
        "strace",
        "uv",
    )
)


def _read_proc(path: str) -> str:
    """Read a `/proc` file as text, replacing undecodable bytes."""
    return Path(path).read_bytes().decode("utf-8", "replace")


def ancestry(pid: int | None = None) -> list[tuple[int, str]]:
    """Return [(pid, cmdline)] from `pid` (default: self) up to init — the CALL STACK.

    ⚑ WHY A PPID WALK AND NOT AN ENV VAR OR A DEPTH COUNTER. The cycle this exists to
    detect crosses `membudget run` -> `/usr/bin/time -v` -> `python3`, three exec layers
    with a shell in the middle. An env var survives that only if every layer forwards it,
    which is a precondition nobody checks and one `env -i` breaks silently. A depth
    counter bounds the damage without removing the edge — check-then-act against a
    process tree, which is the shape that produced the incident. **The ppid chain is the
    ground truth: it is what actually happened, not a token something agreed to pass
    along.**

    Reads `/proc/<pid>/stat` for the ppid and `/proc/<pid>/cmdline` for the command.
    Linux only, and deliberately so — this repo's hooks and build are Linux-only already,
    and a portable shim would add a second, weaker authority for the same question.

    ⚑ A DEAD OR UNREADABLE PID ENDS THE WALK RATHER THAN RAISING. A guard that crashes on
    a racing parent is worse than one that under-reports: under-reporting costs a
    duplicate run, crashing costs the caller its exit code.
    """
    out: list[tuple[int, str]] = []
    seen: set[int] = set()
    cur = pid if pid is not None else os.getpid()
    for _ in range(_MAX_HOPS):
        if cur in (0, 1) or cur in seen:
            break
        seen.add(cur)
        try:
            cmd = _read_proc(f"/proc/{cur}/cmdline").replace("\0", " ").strip()
            stat = _read_proc(f"/proc/{cur}/stat")
        except OSError:
            break
        out.append((cur, cmd))
        # ⚑ FIELD 4 IS PPID, AND THE COMM FIELD IS PARENTHESISED AND MAY CONTAIN SPACES —
        # so split after the LAST `)`, never `stat.split()[3]`. A process named
        # `(my prog)` shifts every positional field and the naive read returns a state
        # letter as a pid.
        try:
            cur = int(stat[stat.rindex(")") + 1 :].split()[_PPID_OFFSET_AFTER_COMM])
        except (ValueError, IndexError):
            break
    return out


def is_interpreter_wrapper(cmdline: str) -> bool:
    """Report whether this ancestor CARRIES a command rather than BEING an invocation.

    ⚑⚑⚑ THE TEST IS PROCESS KIND, NOT STRING DISTANCE, AND THE FIRST CUT GOT THAT WRONG
    IN ITS OWN COMMENT. `check_cycle`'s docstring said *"the test is process-kind"* while
    the code compared `" ".join(sys.argv)` against each ancestor's command line — a
    SUBSTRING test wearing a kind test's description. The prose was right; the instrument
    was textual.

    ⚑ AND THE SUBSTRING FORM IS FRAGILE IN THE DIRECTION THAT COSTS MOST. It excludes a
    launcher only when the launcher's copy of the command is BYTE-IDENTICAL to this
    process's argv. MEASURED 2026-08-24 on a genuine two-generation chain: at generation
    1 the process's argv was `… cyc_inner.py 1` while the launching shell held
    `… cyc_inner.py 0`, so the shell was NOT excluded and appeared in the hit list beside
    the real ancestor. Any difference in spelling re-arms the 100%-false-positive the
    exclusion was patched for, and it re-arms SILENTLY.

    ⚑ A KIND TEST DOES NOT HAVE THAT FAILURE MODE, because it does not depend on the
    command at all. A shell reports its interpreter as argv[0]; a re-entry reports the
    tool. So a genuine `bash -> tool -> bash -> tool` chain stays visible — both shells
    are skipped as launchers, and the INNER TOOL is the hit, which is the process that
    actually re-entered.

    ⚑ THE ASYMMETRY IS DELIBERATE AND IS THE SAFE ONE. Over-skipping a wrapper can only
    MISS a cycle whose sole evidence was a shell's quoted command line. Under-skipping
    refuses a correct first invocation, which trains every reader to route around the
    guard — `run_selftests --list` refusing standalone is what that looked like.
    """
    if not cmdline:
        return False
    parts = cmdline.split()
    head = parts[0] if parts else ""
    base = head.rsplit("/", 1)[-1]
    # ⚑ A VERSIONED INTERPRETER IS NOT A WRAPPER. `python3` execs the tool as its OWN
    # argv[1]; the tool IS the invocation, so skipping it would blind the guard to every
    # `python3 <tool>` ancestor — i.e. to every re-entry there is.
    return base in _WRAPPER_ARGV0


def check_cycle(marker: str, label: str, pid: int | None = None) -> int | None:
    """Refuse when `marker` already appears in this process's OWN ancestry — a REENTRY.

    ⚑ THE MARKER IS MATCHED AGAINST THE FULL COMMAND LINE, not a process name, because
    the chain runs `bash membudget … -- /usr/bin/time -v … python3 <tool> --selftest`:
    the tool is an ARGUMENT at every layer but the last. Pass a marker distinctive enough
    not to collide — `"worklist_gate.py --selftest"`, not `"worklist_gate"`.

    ⚑ SELF IS EXCLUDED. The current process's own cmdline necessarily contains the
    marker; counting it would make every first invocation a refusal. Only ANCESTORS
    count.

    ⚑⚑ A LAUNCHING SHELL IS NOT AN ANCESTOR INVOCATION, AND MISSING THIS MADE THE FIRST
    CUT REFUSE ITS OWN FIRST RUN. `bash -c 'python3 run_selftests.py --list'` carries the
    whole command in its argv, so the shell that STARTED this process matches any marker
    naming it. MEASURED: the guard fired at 100% on a corpus with no cycle in it, which
    is a false-positive rate a guard cannot carry.

    Returns None when there is no cycle; otherwise prints the offending chain and returns
    0 — a SKIP, not a failure. ⚑ Zero is deliberate and is the whole ergonomic point: the
    roster asked a reasonable question and the answer is "already being answered
    upstream". Exiting non-zero would turn a correct de-duplication into a red gate, and
    someone would then route around the guard to get their build green.
    """
    chain = [
        (p, c)
        for p, c in ancestry(pid)[1:]  # [1:] — self is not an ancestor
        if not is_interpreter_wrapper(c)
    ]  # …nor a shell that launched self
    hit = [(p, c) for p, c in chain if marker in c]
    if not hit:
        return None
    rows = "".join(f"    pid {p}  {c[:_CMDLINE_WIDTH]}\n" for p, c in hit)
    sys.stderr.write(
        f"{label}: SKIPPING — {marker!r} is already in this process's ancestry "
        f"(⟡worklist-gate-recursion).\n"
        f"  This is a CYCLE in the selftest roster, not a failure: the work is already\n"
        f"  being done by the ancestor below. Running it again forks a generation that\n"
        f"  each fork repeats — measured at load 54.93 with 68 processes on 10 cores.\n"
        f"{rows}"
    )
    return 0
