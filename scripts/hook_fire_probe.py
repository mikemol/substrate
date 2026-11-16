#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""⟡the-ritual-in-the-blind-spot — fire every hook in BOTH cwd arms, verdicts asserted.

⚑⚑⚑ THIS EXISTS BECAUSE THE ACCEPTANCE RITUAL RAN IN THE BLIND SPOT OF THE THING IT
CERTIFIED. Every fire-probe in this arc invoked the hooks from a foreign cwd, spelled
`env -C /tmp <cmd>` because `hook_no_chaining` refuses `cd &&` and names `env -C` as its
successor. That spelling was itself a live BYPASS of every hook routing through
`hook_cmdparse.programs()`: the wrapper-skip consumed the flag `-C` but NOT its argument,
so `/tmp` was reported as the program and the `grep` behind it was never examined.
**The probe that certifies the hooks was written in the one shape they could not see**,
and a "refused" reading taken from it meant something other than it appeared to.

⚑⚑ AND THE CONCLUSION DRAWN FROM IT WAS WRONG IN KIND, NOT ONLY IN DEGREE. The observed
asymmetry — bare `grep <abs path>` refused, `env -C /tmp grep <same abs path>` allowed —
reads as *the hook is cwd-scoped and loses jurisdiction outside the repo*. It is not.
`hook_structural_query.verdict()` keys on the ARGUMENT'S SUFFIX against the routing table
and consults no cwd at all; `claims()`' own docstring rejects a location test as
unportable, and a case pins a `.py` in ANOTHER repo as still claimed. **A parser defect
wore the costume of a policy decision**, and a probe blind to the parser could not tell
them apart. The matrix below keeps both readings falsifiable: the `env -C` rows fail if
the parser regresses, and the outside-any-project row fails if someone "fixes" the
scoping by keying on the operand's project.

⚑ SO THE ARMS ARE NOT DECORATION. Each row is exercised under BOTH cwd relations with an
expected verdict stated for each, INCLUDING where the correct verdict is silence — an
unasserted silence is the vacuous case this arc records elsewhere, and it is how a gate
goes quiet without ever failing.

⚑⚑ THE FOREIGN DIRECTORY IS DERIVED, NEVER NAMED (operator: *"We shouldn't be hardcoding
/tmp ; TMPDIR doesn't even say /tmp."*). On this box `/tmp` is a small tmpfs shared with
the editor and the harness — `worklist_engine.scratch_root` records it filling twice, after
which every child failed at spawn with ENOSPC, a failure that reads as *the tool is broken*
rather than *the volume is full*. A probe that fails for a reason unrelated to what it
tests is worse than one that does not run, because its failure is attributed to the hook.
`tempfile` owns this question and honours `TMPDIR`; the arm CREATES and removes its own
directory, so a shared temp dir's existing contents cannot change what a hook sees.

⚑ AND "FOREIGN" IS A RELATION, NOT A LOCATION. What the arm needs is *a cwd outside this
project*, which `project_root.project_for` decides by marker walk. If the derived directory
turns out to be INSIDE a project this SAYS SO and fails, rather than silently testing the
wrong relation — the same distinction as reporting a missing reader as an empty set.

    hook_fire_probe.py --selftest    # assert both arms of every row
    hook_fire_probe.py --report      # print each arm's observed verdict
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

# ⚑ THE ROOT PRELUDE, THEN DECLARED IMPORTS — the shape `check_hook_set` arm 2 asserts for
# every hook importing a sibling, and whose ABSENCE from `hook_pycheck` once shipped a
# silently-inert gate into an adopting repo. ⚑⚑ `absolute()`, NEVER `resolve()`: these
# files are SYMLINKED into five checkouts, so a resolved `__file__` derives SUBSTRATE's
# root in an adopter and would probe the wrong tree. `PTH100` recommends the wrong spelling.
_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts import hook_fire_run, project_root  # noqa: E402  the runner and the root walk

# Where the hooks live, relative to the repo this probe ships in.
_HOOK_DIR = _ROOT / "scripts"

# ⚑ THE ARMING VARS ARE READ FROM THE FILE THE HARNESS READS, never restated. A second
# roster of var names beside the one that arms them is the frozen-copy shape these hooks
# were built to retire.
_SETTINGS = _ROOT / ".claude" / "settings.json"


def blocking_vars() -> dict[str, str]:
    """Return the hook-arming env vars declared in the harness settings.

    ⚑ DERIVED FROM `.claude/settings.json`, WHICH IS THE FILE THE HARNESS ACTUALLY READS.
    Hardcoding `STRUCT_HOOK_BLOCK=1` here would arm whatever this probe remembers rather
    than what the session runs, so a hook newly switched to advisory would keep reading as
    armed in this suite — a gate certified against a copy of its own configuration.

    ⚑ AN UNREADABLE SETTINGS FILE YIELDS `{}` AND THE CALLER SAYS SO. Returning some
    default set would report a MISSING READER as a known configuration.
    """
    try:
        raw: object = json.loads(_SETTINGS.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    env = raw.get("env")
    if not isinstance(env, dict):
        return {}
    return {k: v for k, v in env.items() if isinstance(k, str) and isinstance(v, str)}


def foreign_dir() -> tuple[Path, str]:
    """Return a freshly-created directory OUTSIDE any project, and a note if it is not.

    ⚑⚑ DERIVED VIA `tempfile`, WHICH HONOURS `TMPDIR` AND EVERY PLATFORM CONVENTION. A
    hardcoded `/tmp` freezes a fact whose authority lives elsewhere — the same class as a
    count quoted in prose — and on a box where `/tmp` is absent, unwritable, or a different
    mount, the arm fails for a reason having nothing to do with the hook.

    ⚑ AND THE RELATION IS CHECKED, NOT ASSUMED. `mkdtemp()` returns a location; the arm
    needs one that is not inside a project. `project_for` decides that by marker walk, and
    a temp dir that IS under a project is reported so the caller fails loudly rather than
    testing the wrong relation quietly.
    """
    path = Path(tempfile.mkdtemp(prefix="hook-fire-probe-"))
    owner = project_root.project_for(path)
    if owner is not None:
        return path, f"NOT FOREIGN: {path} lies under the project at {owner}"
    return path, ""


class _Cases:
    """Collect probe outcomes across both arms.

    ⚑ AN ARM IS NAMED IN EVERY LABEL. A failure reading only "grep over .py" cannot say
    WHICH cwd relation broke, which is the one fact this suite exists to expose.
    """

    def __init__(self) -> None:
        self.rows: list[tuple[str, bool, str, str]] = []

    def expect(self, label: str, got: str, want: str) -> None:
        """Record one arm's outcome against its stated expectation."""
        self.rows.append((label, got == want, got, want))

    def holds(self, label: str, *, got: bool) -> None:
        """Record a plain property that must hold."""
        # ⚑ `repr(True)` WOULD BE AN FBT003 BOOLEAN POSITIONAL — the linter is right that
        # a bare `True` at a call site says nothing about what it means. The expectation
        # is spelled as text because that is what the report prints.
        self.rows.append((label, got is True, repr(got), "True"))

    def report(self, suite: str) -> bool:
        """Print any failures and the tally; return whether every case held."""
        ok = sum(1 for _n, g, _a, _b in self.rows if g)
        for name, good, got, want in self.rows:
            if not good:
                sys.stdout.write(f"  FAIL {name}: got {got} want {want}\n")
        sys.stdout.write(f"{suite} selftest: {ok}/{len(self.rows)}\n")
        return ok == len(self.rows)


_DENY = hook_fire_run.DENY
_ALLOW = hook_fire_run.ALLOW

# ⚑⚑ THE MATRIX IS DATA, AND EVERY ROW STATES A VERDICT FOR *BOTH* ARMS — including the
# rows whose correct verdict is `allow`. A row naming only the refusing arm would let a
# hook go silent in the other without any case noticing, which is precisely how this arc's
# ritual stayed green while a bypass was live.
#
# ⚑ THE WRAPPER-FLAG ROWS ARE THE REGRESSION ARMS. Each RAN successfully against these
# hooks before `_FLAGS_WITH_ARG` was added to `hook_cmdparse`. `{foreign}` is substituted
# with the directory created at run time, so they cannot re-freeze the `/tmp` literal the
# operator ruled out.
#
# (hook, command template, verdict in-repo, verdict foreign, label)
_MATRIX: tuple[tuple[str, str, str, str, str], ...] = (
    # --- hook_structural_query: a textual read of a claimed artifact ---------------
    (
        "hook_structural_query.py",
        "grep -c def {abs_py}",
        _DENY,
        _DENY,
        "structural_query: bare grep over a repo .py",
    ),
    (
        "hook_structural_query.py",
        "env -C {foreign} grep -c def {abs_py}",
        _DENY,
        _DENY,
        "⚑⚑ structural_query: `env -C` no longer hides grep (THE live bypass)",
    ),
    (
        "hook_structural_query.py",
        "timeout -s KILL 60 grep -c def {abs_py}",
        _DENY,
        _DENY,
        "⚑ structural_query: `timeout -s` no longer hides grep",
    ),
    (
        "hook_structural_query.py",
        "sudo -u nobody grep -c def {abs_py}",
        _DENY,
        _DENY,
        "⚑ structural_query: `sudo -u` no longer hides grep",
    ),
    # ⚑ THE CLAIM IS THE ARTIFACT KIND, NOT THE CHECKOUT — so a .py under the foreign
    # directory is refused from BOTH arms. This row fails if anyone "fixes" the scoping
    # by keying on the operand's project, which was the tempting wrong repair.
    (
        "hook_structural_query.py",
        "grep -c def {foreign}/x.py",
        _DENY,
        _DENY,
        "⚑ structural_query: a .py OUTSIDE any project is still claimed",
    ),
    # --- ⚑ ASSERTED SILENCE: these must NOT fire, in either arm --------------------
    (
        "hook_structural_query.py",
        "ls -la {abs_py}",
        _ALLOW,
        _ALLOW,
        "⚑ structural_query is SILENT for `ls` (locating is not a structural question)",
    ),
    (
        "hook_structural_query.py",
        "pgrep -af make",
        _ALLOW,
        _ALLOW,
        "⚑ structural_query is SILENT for pgrep",
    ),
    # --- hook_no_chaining: guards command SHAPE, so both arms agree ----------------
    ("hook_no_chaining.py", "echo a && echo b", _DENY, _DENY, "no_chaining: `&&` refused"),
    (
        "hook_no_chaining.py",
        "env -C {foreign} bash -c 'echo hi'",
        _DENY,
        _DENY,
        "⚑ no_chaining: `bash -c` refused behind `env -C` too",
    ),
    (
        "hook_no_chaining.py",
        "echo hello",
        _ALLOW,
        _ALLOW,
        "⚑ no_chaining is SILENT for a single simple command",
    ),
    # --- hook_shellcheck: RETIRED FROM THIS MATRIX (2026-09-22) ---------------------
    # ⚑⚑ The shellcheck hook moved to mtools (`mikemol-hook-shellcheck`, the wired entry since
    # the operator's swap), and `scripts/hook_shellcheck.py` is deleted. These rows ran the OLD
    # script by path, so they would have tested a hook that is no longer wired — a green that
    # says nothing about the gate in force. The same two cases (SC2086 denied, a clean command
    # allowed) were run against the INSTALLED console script when it was adopted, plus the
    # per-tree waiver read proven both ways. ⚑ RESIDUE: this probe drives `scripts/<hook>` by
    # path only; teaching it to drive an installed console script is what would put the
    # wired mtools hooks back under its matrix.
)


def _probe_rows(c: _Cases, foreign: Path, env: dict[str, str]) -> None:
    """Drive every matrix row through both cwd arms."""
    abs_py = str(_HOOK_DIR / "hook_cmdparse.py")
    for hook, template, want_repo, want_foreign, label in _MATRIX:
        cmd = template.format(abs_py=abs_py, foreign=foreign)
        c.expect(f"[in-repo] {label}", hook_fire_run.decide(hook, cmd, _ROOT, env), want_repo)
        c.expect(f"[foreign] {label}", hook_fire_run.decide(hook, cmd, foreign, env), want_foreign)


def _cases_preconditions(c: _Cases, note: str, env: dict[str, str]) -> None:
    """Assert the arms test what they claim, before any verdict below is trusted.

    ⚑⚑ A PROBE WITH AN UNVERIFIED PRECONDITION REPORTS ITS OWN SETUP AS THE SUBJECT'S
    PROPERTY. If the "foreign" directory is not foreign, or the hooks are not armed, every
    row still produces a verdict — just not the one it is read as. Both get a case rather
    than a comment, which is the difference between this suite and the ritual it replaces.
    """
    c.holds(f"⚑ the foreign arm is genuinely outside any project {note}".rstrip(), got=note == "")
    c.holds(
        "⚑ the in-repo arm is genuinely inside this project",
        got=project_root.project_for(_ROOT) == _ROOT,
    )
    c.holds("⚑ the arming vars were READ from .claude/settings.json, not assumed", got=bool(env))


def selftest() -> int:
    """Run both arms of every hook and return an exit code."""
    c = _Cases()
    env = blocking_vars()
    foreign, note = foreign_dir()
    try:
        _cases_preconditions(c, note, env)
        _probe_rows(c, foreign, env)
    finally:
        shutil.rmtree(foreign, ignore_errors=True)
    return 0 if c.report("hook_fire_probe") else 1


def _report() -> int:
    """Print each arm's observed verdict without asserting, for inspection."""
    env = blocking_vars()
    foreign, note = foreign_dir()
    if note:
        sys.stdout.write(f"⚑ {note}\n")
    abs_py = str(_HOOK_DIR / "hook_cmdparse.py")
    try:
        for hook, template, want_repo, want_foreign, label in _MATRIX:
            cmd = template.format(abs_py=abs_py, foreign=foreign)
            got_repo = hook_fire_run.decide(hook, cmd, _ROOT, env)
            got_foreign = hook_fire_run.decide(hook, cmd, foreign, env)
            mark = "ok  " if (got_repo, got_foreign) == (want_repo, want_foreign) else "FAIL"
            sys.stdout.write(f"{mark} in-repo={got_repo:<7} foreign={got_foreign:<7} {label}\n")
    finally:
        shutil.rmtree(foreign, ignore_errors=True)
    return 0


def main(argv: list[str]) -> int:
    """CLI: `--selftest` asserts both arms; `--report` prints them."""
    if "--selftest" in argv:
        return selftest()
    if "--report" in argv:
        return _report()
    sys.stdout.write(f"{__doc__}\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
