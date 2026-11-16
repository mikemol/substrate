#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Drive ONE hook the way the harness does, and report its decision.

⚑⚑ THIS MODULE EXISTS TO BE THE FIRE PROBE'S SOLE SUBPROCESS CALLER, AND THAT IS ITS
WHOLE RESPONSIBILITY. The operator's ruling is *"we don't do line-scoped overrides; we
have ecosystem-wide standards, and, if necessary, SRP per-file overrides."* A per-file
`S603` entry is only honest when the file has ONE reason to change, so the override and
this decomposition are the same act — exempting the probe as a whole would grant the
exemption to a case matrix and two report modes in order to cover one `subprocess.run`.
`pycheck_verdict.py` established the pattern; this is the same ruling at a second
boundary, and `pyproject.toml`'s `promote_frontier` entry asks exactly the question that
produced it: does this share a responsibility with the existing four? It does not —
those run CHECKERS over source; this runs a GATE over a payload.

⚑⚑⚑ THE SUBPROCESS IS THE DESIGN, NOT AN IMPLEMENTATION DETAIL, AND THE PROBE IS
WORTHLESS WITHOUT IT. Calling `hook_structural_query.verdict()` in process would re-check
the very predicate the probe exists to distrust, while skipping the root prelude, the
payload reader and the deny envelope — the three places an adopted hook actually breaks.
`check_hook_set`'s docstring records the measured instance: `hook_pycheck` crashed at
module load in a repo whose `scripts/` is not a package, and **the harness reads a hook's
empty stdout as ALLOW**, so it denied nothing while reading as armed in review. An
in-process call cannot distinguish an armed gate from a silently inert one; a real
process can, because it observes what the harness observes.

⚑ NOT `shell=True` — that is S602's subject and would trade a lint finding for a REAL
injection vector. The argv-list form is the safe one and stays.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# ⚑ `absolute()`, NEVER `resolve()`: `resolve()` follows symlinks, and these files are
# SYMLINKED into five checkouts, so a resolved `__file__` would derive SUBSTRATE's root in
# an adopting repo and probe the wrong tree's hooks. `PTH100` recommends the wrong spelling.
_HOOK_DIR = Path(__file__).absolute().parent

# A hook's three possible decisions, as the harness reads them.
DENY = "deny"
ADVISE = "advise"
ALLOW = "allow"

# ⚑⚑ THE ENV VARS THAT ARM A HOOK TO DENY RATHER THAN ADVISE, CLEARED BEFORE EVERY RUN.
# `.claude/settings.json` exports these into the SESSION, so they are already set in this
# process — and a caller passing `{}` to mean *unarmed* would silently get an ARMED run.
# The probe would then assert a distinction it had already erased. Clearing them first is
# what makes the `env` argument the whole truth about arming.
#
# ⚑ THIS LIST IS A FLOOR, NOT AN AUTHORITY: `hook_fire_probe.blocking_vars()` READS the
# settings file, so a var added there arms the probe with no edit here. What this set must
# cover is the inverse question — which vars to UNSET — and an unknown var left set makes
# an unarmed case read armed. That is a loud failure (an `advise` case returns `deny`),
# never a silent pass, which is the right direction for a floor to be wrong in.
ARMING_VARS = (
    "STRUCT_HOOK_BLOCK",
    "NOCHAIN_HOOK_BLOCK",
    "PYCHECK_HOOK_BLOCK",
    "SHELLCHECK_HOOK_BLOCK",
)

# How long one hook may take before the probe calls it hung rather than waiting forever.
TIMEOUT_S = 60

# A hook that could not START exits non-zero; one that ran and advised exits 0.
_RAN_OK = 0


def payload_for(command: str) -> str:
    """Render the PreToolUse payload carrying `command`, typed at every level.

    ⚑⚑ THE NESTED DICT IS BUILT THROUGH TYPED LOCALS, AND THAT IS THE WHOLE REASON THIS
    IS A FUNCTION. Written inline as `json.dumps({"tool_input": {"command": command}})`
    the INNER literal is inferred on its own as `dict[Any, Any]` — the call site gives it
    nothing to check against — and `disallow_any_expr` refuses it. `hook_structural_query`
    carries the identical construct in `_deny_payload`, with the same note; this is the
    same shape on the sending side of the same wire.

    ⚑⚑⚑ `tool_name` IS NOT OPTIONAL, AND OMITTING IT MADE A LIVE HOOK READ AS SILENT.
    The first cut sent only `tool_input`, which `hook_structural_query` and
    `hook_no_chaining` tolerate (they read the command directly) but `hook_shellcheck`
    does not: it dispatches on `tool_name`, finds no `"Bash"`, and returns 0 having
    analysed nothing. The probe then reported ALLOW for a command whose SC2086 the same
    hook's `--explain` prints — **a false silence produced by the probe's own payload**,
    which is precisely the defect class this suite exists to detect, aimed inward. ⚑ A
    fixture that under-specifies its input measures the fixture, not the subject.
    """
    tool_input: dict[str, str] = {"command": command}
    envelope: dict[str, object] = {"tool_name": "Bash", "tool_input": tool_input}
    return json.dumps(envelope)


def decide(hook: str, command: str, cwd: Path, env: dict[str, str]) -> str:
    """Return `deny` / `advise` / `allow` for `command`, with `hook` run from `cwd`.

    ⚑⚑ THE THREE-VALUED RETURN IS THE POINT AND IS NOT A CONVENIENCE. `advise` and
    `allow` must never merge: this repo's hooks are advisory unless an env var arms
    them, so a probe that folded the two would report an UNARMED gate as a silent one
    — and could never assert the difference between "correctly says nothing" and
    "should have denied but was not armed". `check_mypy_ratchet` exiting 0 on 116
    errors is the same collapse in a verdict channel too narrow to carry a third state.

    ⚑ A CRASH IS `allow`, DELIBERATELY AND WITH THE ARROW POINTING THE RIGHT WAY. That
    is not this function being lenient — it is this function reporting what the HARNESS
    would do with the same output, which is the only reading that makes the probe's
    verdict mean anything about production behaviour.

    ⚑⚑⚑ AND IT IS `allow` ONLY BECAUSE THE EXIT CODE IS CONSULTED. The first cut read
    stderr alone, so an ABSENT hook — a traceback on stderr — reported as `advise`: the
    same ABSENT-vs-FINDING collapse `pycheck_verdict` records from the other direction,
    caught here by its own positive control. A hook that cannot start writes to stderr
    AND exits non-zero; one that ran and chose to advise writes its notice and exits 0.
    Only the pair separates them, and conflating them would let a BROKEN hook satisfy
    every `advise` assertion in the probe — a green built from the failure it detects.
    """
    clean = {k: v for k, v in os.environ.items() if k not in ARMING_VARS}
    try:
        # ⚑ S603 CANNOT SEE WHETHER AN ARGV WAS VALIDATED — its own documentation says
        # so, citing astral-sh/ruff#4045 under *Known problems*. Here `sys.executable`
        # is the running interpreter and `hook` is a filename the caller takes from
        # `check_hook_set.HOOKS`, the declared roster. The command under test becomes
        # the payload's CONTENTS — data on stdin — never a word in this command line.
        proc = subprocess.run(
            [sys.executable, str(_HOOK_DIR / hook)],
            input=payload_for(command),
            capture_output=True,
            text=True,
            cwd=str(cwd),
            env={**clean, **env},
            timeout=TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ALLOW
    if DENY in proc.stdout:
        return DENY
    if proc.returncode != _RAN_OK:
        return ALLOW
    return ADVISE if proc.stderr.strip() else ALLOW


def _selftest() -> int:
    """Run the cases and return an exit code.

    ⚑ THE CASES PIN THE THREE-VALUED READING, which is the only judgement this file
    makes. Whether any particular hook SHOULD fire is `hook_fire_probe`'s question, and
    keeping it there is what stops this module growing a second responsibility.
    """
    failures = 0
    root = _HOOK_DIR.parent

    # ⚑ A POSITIVE CONTROL FOR EACH VALUE, because a reader that can only ever return
    # one of them would pass a suite built only from the case it happens to satisfy.
    # `hook_no_chaining` is the fixture: its verdict turns on command SHAPE alone, so
    # these cases depend on no routing table and on no cwd relation.
    armed = {"NOCHAIN_HOOK_BLOCK": "1"}
    if decide("hook_no_chaining.py", "echo a && echo b", root, armed) != DENY:
        sys.stderr.write("selftest: an armed hook's refusal did not read as deny\n")
        failures += 1

    # ⚑⚑ THE UNARMED ARM IS THE ONE WITH TEETH, AND IT FAILED ON FIRST RUN — the session
    # env already carried `NOCHAIN_HOOK_BLOCK=1`, so `{}` was not unarmed and this
    # returned `deny`. That is what `ARMING_VARS` now clears.
    if decide("hook_no_chaining.py", "echo a && echo b", root, {}) != ADVISE:
        sys.stderr.write("selftest: an UNARMED refusal did not read as advise\n")
        failures += 1

    if decide("hook_no_chaining.py", "echo hello", root, armed) != ALLOW:
        sys.stderr.write("selftest: a clean command did not read as allow\n")
        failures += 1

    # ⚑⚑ A HOOK THAT CANNOT RUN READS AS `allow` — the harness's own reading, and the
    # failure `check_hook_set` exists to prevent. This case also failed on first run
    # (an absent module's traceback read as `advise`), which is what forced the exit-code
    # test above. Asserting it is what makes the probe's green mean ARMED rather than
    # "nothing happened".
    if decide("hook_absent.py", "echo a && echo b", root, armed) != ALLOW:
        sys.stderr.write("selftest: an absent hook did not read as allow\n")
        failures += 1

    if failures:
        sys.stderr.write(f"hook_fire_run selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write("hook_fire_run selftest: 4/4\n")
    return 0


def main(argv: list[str]) -> int:
    """CLI: `--selftest` runs the cases."""
    if "--selftest" in argv:
        return _selftest()
    sys.stdout.write(f"{__doc__}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
