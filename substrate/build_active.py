# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Push `substrate_build_active` to luthen's vmagent while a build runs (W49, 2026-09-23).

luthen's stall rule reads `substrate_build_active{tenant,peer="substrate"} == 1` beside its own
`luthen_tenant_backends`: a build claiming to be active while the tenant has had no active
backend for 15m is STALLED. Samples are stamped at ingest, so a running build re-pushes every
`--every` seconds and pushes 0 when it ends. Three modes:

    python -m substrate.build_active --tenant sandbox -- make -C agda -f Flat.mk promote
    python -m substrate.build_active --tenant sandbox --pid 12345   # a build already running
    python -m substrate.build_active --tenant sandbox --once 1      # one sample, then exit

⚑ A FAILED PUSH IS REPORTED AND NEVER FAILS THE BUILD — an observer that can kill what it
observes has inverted the dependency. It is not silent either: each failure goes to stderr.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from substrate import prom_push, vmagent_address

DEFAULT_EVERY_S = 60
#: Only a DEFAULT for the CLI's own `--luthen` flag (W35, operator 2026-09-24) -- an entry-point
#: default is where a constant belongs; everything downstream (vmagent_address, prom_push) now
#: takes the checkout as a required parameter instead of guessing it. The constant itself lives
#: in `vmagent_address` (the one sanctioned default, shared with `vlogs_destination`) rather than
#: a second copy here.
DEFAULT_LUTHEN = vmagent_address.DEFAULT_LUTHEN
USAGE = (
    "usage: python -m substrate.build_active --tenant T [--every S] [--luthen PATH]"
    " (-- CMD... | --pid PID | --once 0|1)\n"
)


def line(tenant: str, value: int) -> str:
    """Render the one sample as Prometheus text exposition."""
    return f'substrate_build_active{{tenant="{tenant}",peer="substrate"}} {value}\n'


def push(tenant: str, value: int, luthen: Path) -> bool:
    """Push one sample; report and return False on failure, never raise."""
    try:
        prom_push.push(line(tenant, value), luthen)
    except (OSError, vmagent_address.UnresolvedError, subprocess.SubprocessError) as exc:
        sys.stderr.write(f"build-active: push {value} failed: {exc}\n")
        return False
    return True


def watch_pid(tenant: str, pid: int, every_s: int, luthen: Path) -> int:
    """Push 1 every `every_s` while `pid` lives, then 0."""
    while Path(f"/proc/{pid}").exists():
        push(tenant, 1, luthen)
        time.sleep(every_s)
    push(tenant, 0, luthen)
    return 0


def run(tenant: str, cmd: list[str], every_s: int, luthen: Path) -> int:
    """Run `cmd`, pushing 1 while it runs and 0 after; return its exit code."""
    child = subprocess.Popen(cmd)
    while child.poll() is None:
        push(tenant, 1, luthen)
        try:
            child.wait(timeout=every_s)
        except subprocess.TimeoutExpired:
            continue
    push(tenant, 0, luthen)
    return child.returncode


def _opt(argv: list[str], name: str) -> str | None:
    """Return the operand of `name`, "" when it has none, or None when absent."""
    if name not in argv:
        return None
    at = argv.index(name)
    return argv[at + 1] if at + 1 < len(argv) else ""


def main(argv: list[str]) -> int:
    """Parse the flags and dispatch to exactly one mode."""
    cmd: list[str] = []
    if "--" in argv:
        cut = argv.index("--")
        argv, cmd = argv[:cut], argv[cut + 1 :]
    tenant, every = _opt(argv, "--tenant"), _opt(argv, "--every") or str(DEFAULT_EVERY_S)
    pid, once = _opt(argv, "--pid"), _opt(argv, "--once")
    luthen_opt = _opt(argv, "--luthen")
    luthen = Path(luthen_opt) if luthen_opt else DEFAULT_LUTHEN
    chosen = [m for m in (cmd, pid, once) if m]
    if not tenant or not every.isdigit() or len(chosen) != 1:
        sys.stderr.write(USAGE)
        return 2
    if once is not None:
        return 0 if once in {"0", "1"} and push(tenant, int(once), luthen) else 1
    if pid is not None:
        return watch_pid(tenant, int(pid), int(every), luthen) if pid.isdigit() else 2
    return run(tenant, cmd, int(every), luthen)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
