#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `substrate.scratch_cli` — every mode driven through `run`, exit codes included.

⚑⚑ THE CASES DRIVE `run`, NOT THE MODULES. Each module's suite already proves its reader; what
this suite owes is the WIRING — that the hook's spelling (`--quiet`) reaches the gate, that
`--promotable` refuses with 2 on no operand and 1 on BLOCK, that `--scope` is 0 even when it
finds couplings, and that the modifier order does not matter. A refusal is a returned code, so
every one of those is an assertion rather than an abort.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from substrate import scratch_cli as cli

# A promoted tree with one coupling, and an unpromoted candidate that is clean.
_LIVE = 'import sys\nsys.path.insert(0, "scratch")\n'
_CLEAN = "X = 1\n"


def _plant(files: dict[str, str]) -> Path:
    """Write a fixture tree under a fresh root and return that root."""
    root = Path(tempfile.mkdtemp(prefix="scratch-cli-"))
    for rel, text in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return root


def the_gate_fails_on_a_hit_and_the_hook_spelling_is_quiet(out: list[str]) -> int:
    """Check the bare gate and `--quiet`/`--check` all reach the gate, and exit 1 on a hit."""
    root = _plant({"jea/m.py": _LIVE})
    bad = 0
    for argv in ([], ["--quiet"], ["--check"]):
        o, e, code = cli.run(argv, root)
        if code != cli.FAILED or o or not e or "FAILED" not in e[0]:
            out.append(f"selftest: gate {argv!r} read code={code} out={o!r} err={e[:1]!r}")
            bad += 1
    return bad


def the_gate_passes_quietly_or_loudly(out: list[str]) -> int:
    """Check a clean tree exits 0, with the OK line only when not quiet."""
    root = _plant({"jea/m.py": _CLEAN})
    loud = cli.run([], root)
    quiet = cli.run(["--quiet"], root)
    if loud[2] != cli.OK or not loud[0] or loud[1]:
        out.append(f"selftest: a clean loud gate read {loud!r}")
        return 1
    if quiet != ([], [], cli.OK):
        out.append(f"selftest: a clean quiet gate read {quiet!r}")
        return 1
    return 0


def promotable_refuses_without_an_operand_and_blocks_with_one(out: list[str]) -> int:
    """Check `--promotable` exits 2 bare, 1 on a blocked candidate, 0 on a clean one."""
    root = _plant({"cand/m.py": _LIVE, "ok/m.py": _CLEAN})
    bad = 0
    o, _e, code = cli.run(["--promotable"], root)
    if code != cli.USAGE or not o or not o[0].startswith("usage:"):
        out.append(f"selftest: bare --promotable read code={code} out={o!r}")
        bad += 1
    o, _e, code = cli.run(["--promotable", "cand"], root)
    if code != cli.FAILED or not any(line.startswith("  BLOCK") for line in o):
        out.append(f"selftest: a blocked candidate read code={code} out={o!r}")
        bad += 1
    return bad


def scope_is_a_read_and_never_a_gate(out: list[str]) -> int:
    """Check `--scope` exits 0 with couplings found, 2 bare, and modifiers in either order."""
    root = _plant({"tools/m.py": _LIVE})
    bad = 0
    _o, e, code = cli.run(["--scope"], root)
    if code != cli.USAGE or not e or not e[0].startswith("usage:"):
        out.append(f"selftest: bare --scope read code={code} err={e!r}")
        bad += 1
    o, _e, code = cli.run(["--scope", "tools"], root)
    if code != cli.OK or not o or "1 DEPENDENC" not in o[0]:
        out.append(f"selftest: --scope tools read code={code} out={o[:1]!r}")
        bad += 1
    first = cli.run(["--quiet", "--scope", "tools"], root)
    second = cli.run(["--scope", "tools", "--quiet"], root)
    if first != second or len(first[0]) >= len(o):
        out.append("selftest: --quiet did not modify --scope the same way in both positions")
        bad += 1
    o, _e, code = cli.run(["--scope", "tools", "--mentions"], root)
    if code != cli.OK or not o or "--mentions" not in o[0]:
        out.append(f"selftest: --scope --mentions read code={code} out={o[:1]!r}")
        bad += 1
    return bad


def promotable_takes_precedence_over_scope(out: list[str]) -> int:
    """Check the origin's dispatch order: `--promotable` wins when both flags are present."""
    root = _plant({"ok/m.py": _CLEAN})
    o, _e, code = cli.run(["--scope", "ok", "--promotable", "ok"], root)
    if not any("PROMOTABLE" in line for line in o) or code not in (cli.OK, cli.FAILED):
        out.append(f"selftest: precedence read code={code} out={o!r}")
        return 1
    return 0


_ARMS = (
    the_gate_fails_on_a_hit_and_the_hook_spelling_is_quiet,
    the_gate_passes_quietly_or_loudly,
    promotable_refuses_without_an_operand_and_blocks_with_one,
    scope_is_a_read_and_never_a_gate,
    promotable_takes_precedence_over_scope,
)

_CASE_COUNT = 3 + 2 + 2 + 4 + 1


def selftest() -> int:
    """Run every arm and return an exit code."""
    out: list[str] = []
    failures = sum(arm(out) for arm in _ARMS)
    if failures:
        sys.stderr.write("\n".join(out) + "\n")
        sys.stderr.write(f"scratch-cli selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write(f"scratch-cli selftest: {_CASE_COUNT}/{_CASE_COUNT}\n")
    return 0


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv or len(sys.argv) == 1 else 0)
