# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""The cases for `gate_status`: the hook parser, the mode sweep, the verdict rule, the peaks sweep.

⚑ THE ORIGIN'S TWELVE CASES ARE PORTED (hook parse, continuation, conditional, the mode sweep seeing
a DOUBLED listing, the write-default narrowing and its sentinel, the two verdict rules), and the
parameterisation earns its keep with cases the origin could not write: the peaks sweep runs against
a FAKE RUNNER that prints a `retrying at 256MB` line and exits 137, or exits 0, so no lease is ever
started and the ladder's parse is proved on canned output.

⚑ A SWEEP THAT ONLY COMPARED EXIT CODES WOULD CALL A DOUBLED LISTING HEALTHY: the verdict and tail
line are identical in both modes, so the case asserts the LINE COUNT rises.
"""

from __future__ import annotations

import io
import os
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from substrate import build_settings
from substrate import gate_status_cli as cli
from substrate import gate_status_facts as facts
from substrate import gate_status_peaks as peaks
from substrate import gate_status_run as run
from substrate.gate_status_exec import TIMEOUT_RC, Outcome, run_process

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

_MIN_GATES = 15
_THREE = 3
_LEASE = "32"

_HOOK = (
    'run "tool selftests" python3 "$ROOT/scripts/run_selftests.py" --quiet\n'
    'run "wrapped gate" python3 "$ROOT/scripts/x.py" --quiet \\\n'
    "    --extra\n"
    '  run "conditional one" python3 "$ROOT/scripts/y.py"\n'
    "echo not a gate\n"
)

_DOUBLING = (
    "import sys\n"
    "keys = ['a', 'b']\n"
    "for k in keys: print('  claim:', k)\n"
    "if '--list' in sys.argv:\n"
    "    for k in keys: print('   ', k)\n"
    "print('dbl: 2 entries')\n"
)

_PEAK_HOOK = 'run "alpha gate" python3 "$ROOT/scripts/a.py" --quiet\n  run "beta gate" b.py\n'


class _Results:
    """Collect `(label, passed)` pairs."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, bool]] = []

    def check(self, label: str, got: object, want: object) -> None:
        """Record whether `got` equals `want`."""
        self.rows.append((label, got == want))

    def holds(self, label: str, got: object) -> None:
        """Record whether `got` is truthy."""
        self.rows.append((label, bool(got)))


class _Fake:
    """A runner that never starts anything: it answers every non-syntax command with `outcome`."""

    def __init__(self, outcome: Outcome) -> None:
        self.outcome = outcome
        self.seen: list[tuple[str | Sequence[str], Mapping[str, str]]] = []

    def __call__(
        self,
        cmd: str | Sequence[str],
        cwd: Path,
        env: Mapping[str, str],
        timeout: int,
    ) -> Outcome:
        """Answer a `bash -n` with success and anything else with the canned outcome."""
        del cwd, timeout
        if not isinstance(cmd, str) and cmd[:2] == ["bash", "-n"]:
            return Outcome(0, "", "", timed_out=False)
        self.seen.append((cmd, env))
        return self.outcome


def _hook_cases(out: _Results, scratch: Path) -> None:
    """Check the hook parser on a fixture: every `run` line, its continuation, its condition."""
    hook = scratch / "pre-commit"
    hook.write_text(_HOOK, encoding="utf-8")
    g = facts.gates(hook)
    out.check("every `run` line is a gate", len(g), _THREE)
    out.check("the gate's NAME is captured", g[0].name, "tool selftests")
    # ⚑ A BACKSLASH CONTINUATION IS ONE GATE, NOT A TRUNCATED ONE: reading only the first line
    # would run it without its arguments, a verdict about something the hook does not check.
    out.holds("a wrapped `run` line keeps its continuation", "--extra" in g[1].argv)
    # ⚑ AN INDENTED GATE IS CONDITIONAL; reporting it unconditional overstates the precondition.
    out.holds("an indented gate is marked conditional", g[2].conditional)
    out.holds("a top-level gate is not", not g[0].conditional)


def _sweep_cases(out: _Results, scratch: Path, host: run.Host) -> None:
    """Check the mode sweep sees a doubled listing and a write-default tool is swept in --check."""
    dbl = scratch / "dbl.py"
    dbl.write_text(_DOUBLING, encoding="utf-8")
    got = run.modes(str(dbl), host, run.ModesRequest(), run_process)
    by = {r.mode: (r.rc, r.nlines) for r in got}
    # ⚑ DERIVED FROM `MODES`, NOT RESTATED: a case asserting a frozen copy of the thing it tests.
    out.check(
        "--modes runs every declared mode",
        sorted(by),
        sorted(m or "(default)" for m in facts.MODES),
    )
    out.check(
        "a DOUBLED listing shows as a line-count rise, not a bad exit code",
        (by["--list"][0], by["--list"][1] > by["(default)"][1]),
        (0, True),
    )
    # ⚑ THE FIXTURE WRITES A SENTINEL PER RUN, so the case counts ACTUAL writes: a count of runs
    # would pass even if the narrowing did nothing.
    sentinel = scratch / "written.txt"
    tool = scratch / "wtool.py"
    tool.write_text(
        "import sys\n"
        f"S = {str(sentinel)!r}\n"
        'if "--check" in sys.argv:\n'
        '    print("wtool: current")\n'
        "    sys.exit(0)\n"
        'open(S, "a").write("w\\n")\n'
        'print("wtool: wrote")\n',
        encoding="utf-8",
    )
    narrowed = run.modes(str(tool), host, run.ModesRequest(), run_process)
    wrote = len(sentinel.read_text(encoding="utf-8").splitlines()) if sentinel.exists() else 0
    out.check(
        "a write-default tool is swept in --check only", [r.mode for r in narrowed], ["--check"]
    )
    out.check("...and therefore writes NOTHING during the sweep", wrote, 0)
    free = run.modes(str(tool), host, run.ModesRequest(allow_writes=True), run_process)
    out.check("--allow-writes sweeps every mode", len(free), len(facts.MODES))


def _verdict_cases(out: _Results) -> None:
    """Check the labelled verdict beats a trailing hint, and an unlabelled gate keeps its tail."""
    out.check(
        "the labelled verdict beats a trailing refuse_hint",
        facts.verdict_line(
            ["banner", "sumtype-ratchet: 71 duplicate(s)", "Reuse the existing declaration…"]
        ),
        "sumtype-ratchet: 71 duplicate(s)",
    )
    out.check(
        "a gate with no labelled line still reports its tail",
        facts.verdict_line(["checking…", "all good"]),
        "all good",
    )
    out.check("no lines at all is an empty verdict", facts.verdict_line([]), "")


def _real_tree_cases(out: _Results, host: run.Host) -> None:
    """Check the real hook yields a real population, not a parse that narrowed to nothing."""
    gates = facts.gates(host.tree.hook)
    out.holds("the real hook declares more gates than the floor", len(gates) > _MIN_GATES)
    out.holds("the real hook has a conditional gate too", any(g.conditional for g in gates))
    out.holds(
        "the real fleet resolves to scripts that exist", len(cli.fleet(host, run_process)) > 0
    )
    out.check(
        "the membudget client is the build settings' one path",
        host.tree.membudget,
        build_settings.MEMBUDGET,
    )


def _peak_tree(scratch: Path) -> facts.Tree:
    """Return a fixture tree whose hook wires two gates."""
    hook = scratch / ".githooks" / "pre-commit"
    hook.parent.mkdir()
    hook.write_text(_PEAK_HOOK, encoding="utf-8")
    return facts.Tree(scratch, hook, scratch / "scripts" / "membudget")


def _measure(tree: facts.Tree, fake: _Fake, only: str | None = None) -> str:
    """Return what the peaks sweep prints against the fake runner."""
    buf = io.StringIO()
    request = peaks.Request(only=only)
    peaks.measure_peaks(tree, request, fake, {"PATH": "/bin"}, buf)
    return buf.getvalue()


def _peak_cases(out: _Results, scratch: Path) -> None:
    """Check the ladder parse, the exit codes and the advice strings on canned runner output."""
    tree = _peak_tree(scratch)
    climbed = _Fake(Outcome(137, "", "OOM-killed at 32MB … retrying at 256MB\n", timed_out=False))
    text = _measure(tree, climbed)
    out.holds("a `retrying at 256MB` line reads as OVER, landed at 256", "fit at 256MB" in text)
    out.holds(
        "the climb note names the lease and the landing",
        f"OVER {_LEASE}MB → fit at 256MB  ← heavy" in text,
    )
    out.holds("a conditional gate is tagged", "  (conditional)" in text)
    out.check("both gates were leased", len(climbed.seen), 2)
    cmd = climbed.seen[0][0]
    head = f"{tree.membudget} run {_LEASE} gate:alpha-gate -- "
    out.holds(
        "the lease command goes through the injected client path",
        isinstance(cmd, str) and cmd.startswith(head),
    )
    out.holds(
        "the gate's $ROOT is resolved before it is leased",
        isinstance(cmd, str) and f"{scratch}/scripts/a.py" in cmd,
    )
    out.check("the retry ladder is switched on", climbed.seen[0][1]["MEMBUDGET_RETRY_OOM"], "1")
    out.holds("the advice names the client's repo-relative path", "scripts/membudget peaks" in text)

    fit = _measure(tree, _Fake(Outcome(0, "ok\n", "", timed_out=False)))
    out.holds("a clean exit reads as rc=0", "rc=0" in fit)
    out.holds("a fleet that never climbs says it fits the sieve", "the whole fleet fits" in fit)

    killed = _measure(tree, _Fake(Outcome(137, "", "", timed_out=False)))
    out.holds(
        "exit 137 without a ladder line is never-fit", "never fit (no peak recorded)" in killed
    )
    terminated = _measure(tree, _Fake(Outcome(143, "", "", timed_out=False)))
    out.holds("exit 143 is read as over the lease too", f"OVER {_LEASE}MB, never fit" in terminated)

    timed = _measure(tree, _Fake(Outcome(TIMEOUT_RC, "", "", timed_out=True)))
    out.holds("a timeout is reported as OTHER, not as a heavy gate", "(timeout)" in timed)
    out.holds("...and never as an over-lease gate", "gate(s) exceeded" not in timed)

    only = _measure(tree, _Fake(Outcome(0, "", "", timed_out=False)), only="beta")
    out.holds("--gate= narrows the sweep by name", "alpha" not in only and "beta" in only)

    outside = peaks.advice(facts.Tree(scratch, tree.hook, Path("/opt/mb/membudget")))
    out.check(
        "a client outside the tree is named by its own path", outside, "/opt/mb/membudget peaks"
    )


def _cli_cases(out: _Results, scratch: Path, host: run.Host) -> None:
    """Check the dispatch prints the census, the verdict table and the fleet-less usage refusal."""
    tree = _peak_tree(scratch)
    fake = _Fake(Outcome(0, "banner\nratchet-x: 3 left\nadvice\n", "", timed_out=False))
    fixture = run.Host(tree, host.python, host.environ)
    listing = io.StringIO()
    out.check("--list returns 0", cli.main(["g", "--list"], fixture, fake, listing), 0)
    out.holds(
        "--list counts the gates and the unconditional ones",
        listing.getvalue().endswith("2 gate(s) wired (1 unconditional)\n"),
    )
    table = io.StringIO()
    out.check("an all-green sweep returns 0", cli.main(["g"], fixture, fake, table), 0)
    out.holds("the verdict, not the advice, fills the row", "ratchet-x: 3 left" in table.getvalue())
    red = io.StringIO()
    bad = _Fake(Outcome(1, "x: 9 over\n", "", timed_out=False))
    out.check("a red gate returns 1", cli.main(["g"], fixture, bad, red), 1)
    out.holds("...and is listed as red", "   red: alpha gate\n" in red.getvalue())
    refusal = io.StringIO()
    out.check(
        "a fleet sweep with no scripts refuses with 2",
        cli.main(["g", "--modes"], fixture, fake, refusal),
        cli.USAGE_RC,
    )
    out.holds("...and says how to ask", refusal.getvalue().startswith("usage: gate_status.py"))
    gone = run.run_gate("sleep 9", host, _Fake(Outcome(TIMEOUT_RC, "", "", timed_out=True)))
    out.check("a timed-out gate reports its own wording", gone, (TIMEOUT_RC, "TIMEOUT after 600s"))


def _syntax_cases(out: _Results, scratch: Path) -> None:
    """Check a hook that does not parse as shell REFUSES instead of yielding a short census."""
    hook = scratch / "broken"
    hook.write_text('run "x" y\nif then\n', encoding="utf-8")
    label = "an unparseable hook refuses, naming the shell error"
    try:
        facts.gates(hook)
    except SyntaxError as exc:
        out.holds(label, "not valid shell" in str(exc))
    else:
        out.holds(label, "")


def cases(root: Path) -> list[tuple[str, bool]]:
    """Return `(label, passed)` for every case, against the tree at `root`."""
    out = _Results()
    tree = facts.Tree(root, root / ".githooks" / "pre-commit", build_settings.MEMBUDGET)
    host = run.Host(tree, sys.executable, os.environ)
    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp)
        _hook_cases(out, scratch)
        _sweep_cases(out, scratch, host)
        _verdict_cases(out)
        _real_tree_cases(out, host)
        _syntax_cases(out, scratch)
        (scratch / "peaks").mkdir()
        _peak_cases(out, scratch / "peaks")
        (scratch / "clitree").mkdir()
        _cli_cases(out, scratch / "clitree", host)
    return out.rows


def selftest(root: Path) -> bool:
    """Run every case, reporting failures by name."""
    rows = cases(root)
    ok = sum(1 for _, passed in rows if passed)
    for label, passed in rows:
        if not passed:
            sys.stdout.write(f"  FAIL {label}\n")
    sys.stdout.write(f"gate_status selftest: {ok}/{len(rows)}\n")
    return ok == len(rows)


def main() -> int:
    """Run the suite against the tree this file sits in; the tree is resolved here, at the entry."""
    root = Path(__file__).resolve().parent.parent
    return 0 if selftest(root) else 1


# ⚑ THE FLAG IS NAMED SO `suite_discovery` SEES THIS SUITE (⟡selftest-discovery).
if __name__ == "__main__":
    sys.exit(main() if ("--selftest" in sys.argv or len(sys.argv) == 1) else 1)
