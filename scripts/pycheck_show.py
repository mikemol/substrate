#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Show the SOURCE LINES a strict-bar finding names, for a file or a candidate.

⚑⚑ THIS EXISTS BECAUSE I INFERRED A LINE'S IDENTITY FROM AN ERROR STRING FOUR TIMES
RUNNING AND WAS WRONG EVERY TIME. `hook_pycheck` lints an in-flight edit by writing
the post-edit content to a TEMPFILE and running ruff/mypy against that. It rewrites
the tempfile PATH to the real one in the deny message — but the LINE NUMBERS still
refer to the temp copy, which is deleted immediately and never existed on disk. So a
report saying `line 383` names a line the author cannot read, and the only way to act
on it is to guess which construct is there. That is judgement-in-the-turn, on the
output of the very gate built to stop judgement-in-the-turn.

⚑ AND THE COST WAS MEASURED, NOT ANTICIPATED. Chasing two `dict[Any, Any]` errors
through `hook_no_chaining`, I rewrote the payload reader three ways and the selftest
fixtures twice — five candidate versions, none of which touched the construct the
error actually named. The error line MOVED as the file grew, which I read as
confirmation I was getting closer. It was not: the line moved because the FILE moved,
and the construct never did.

WHAT THIS PRINTS: for each `path:line:` a report cites, the numbered neighbourhood of
that line in the source it was checked against.

⚑ THE HONEST LIMIT, STATED RATHER THAN IMPLIED: this reads what you GIVE it. If the
content differs from what the hook checked, the line numbers will not correspond, and
nothing here can detect that. The real fix for the in-flight case is for the hook to
print the numbered content itself; this is the reader that works today, against a file
a checker can be pointed at directly.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_VENV_PY = _ROOT / ".venv" / "bin" / "python3"
_PYPROJECT = _ROOT / "pyproject.toml"
_TIMEOUT_S = 180

# ruff renders `--> path:line:col`; mypy renders `path:line: error: …`. One pattern
# per renderer, because a single loose one matches prose containing a colon.
_RUFF_SITE = re.compile(r"-->\s+(?P<path>\S+?):(?P<line>\d+):\d+")
_MYPY_SITE = re.compile(r"^(?P<path>\S+?):(?P<line>\d+): (?:error|note):", re.MULTILINE)

# How many lines of context to show either side of a finding.
_CONTEXT = 3

# ⚑ THE COULD-NOT-RUN MARKER, NAMED ONCE. `run_checks` writes it and `_count_mode`
# reads it; spelling it at both ends is how a reader drifts off a writer and starts
# reporting UNKNOWN as CLEAN.
_UNRUN = "could not run"

# ruff renders `<CODE> <message>` at the head of a finding; mypy renders a bracketed
# `[error-code]` at the tail. One pattern each, for the same reason the site patterns
# are split: a single loose one reads prose as a code.
_RUFF_CODE = re.compile(r"^(?P<code>[A-Z]{1,4}\d{3,4})\s+\S", re.MULTILINE)
_MYPY_CODE = re.compile(r"^\S+?:\d+: error: .*\[(?P<code>[a-z-]+)\]\s*$", re.MULTILINE)


def run_checks(target: Path, stands_for: Path | None = None) -> str:
    """Run ruff and mypy against `target` under the house config; return their output.

    ⚑ THE HOUSE CONFIG IS PASSED EXPLICITLY. ruff and mypy discover configuration by
    walking up from the file they are given, and a checker pointed at the wrong config
    is a checker that agrees with you — the same reason `hook_pycheck` puts its
    tempfile inside the project rather than outside it.

    ⚑⚑⚑ AND CONFIG DISCOVERY IS NOT THE WHOLE OF IDENTITY, WHICH COST A FALSE FINDING.
    `per-file-ignores` entries are EXACT relative paths, so a PROSPECTIVE edit staged
    under any other name is checked under different rules than the file it stands for.
    Measured: `substrate/type_scope.py` is CLEAN on disk because `pyproject` exempts
    `S603` for exactly that path, and its staged form reported `S603` — a finding the
    real file cannot carry (gate-G334). Relocating the staged file does not fix it:
    only the original path equals the entry (gate-G336).

    ⚑⚑ SO `stands_for` NAMES THE IDENTITY AND `target` HOLDS THE BYTES. Each checker
    has its own spelling for that split and BOTH are used — ruff takes the content on
    stdin with `--stdin-filename`, mypy keeps the real path as its argument and reads
    replacement content through `--shadow-file SOURCE SHADOW`. ⚑ This was filed
    claiming mypy has no equivalent: true of the SPELLING, false of the capability,
    and reading `--help` is what found it (gate-G337). Absent, this reads exactly as
    before — two of three call sites check a file that already IS itself.

    ⚑⚑ `--pretty` IS HERE BECAUSE ITS ABSENCE IS WHAT THIS FILE WAS BUILT AROUND, AND
    I COPIED THE OMISSION BEFORE I UNDERSTOOD IT. The whole premise of this tool was
    that mypy emits a bare line number into a deleted tempfile — but mypy renders the
    source line AND a caret under `--pretty`, which `hook_pycheck` simply never passed.
    I attributed a missing flag in OUR invocation to a limitation of the TOOL, then
    wrote this argv by copying that invocation, inheriting the very omission I was
    diagnosing.

    ⚑ summit-1c named the general form after making the mirror of it: *a probe that
    runs the tool the way the hook runs it inherits every one of the hook's omissions
    — and cannot, by construction, report them as omissions.* A control built from the
    subject's own configuration can only ever confirm the subject's own blind spots.
    """
    # ⚑ EXE001/EXE002 READ THE FILE MODE, SO A REPORT HERE CAN DIFFER FROM THE HOOK'S
    # ON A FILE THE HOOK CALLS CLEAN. `hook_pycheck` lints a TEMP COPY and sets its
    # mode from the CONTENT (`0o755` when it starts `#!`), so a shebanged source that
    # is not chmod +x on disk passes there and fails here. Neither is wrong: they
    # answer different questions — the hook asks about the EDIT, this asks about the
    # FILE AS IT SITS. Excluding the pair keeps this reader answering the hook's
    # question, which is the one a reader chasing a hook finding actually has.
    ruff = [
        str(_VENV_PY),
        "-m",
        "ruff",
        "check",
        "--config",
        str(_PYPROJECT),
        "--no-cache",
        "--extend-ignore",
        "EXE001,EXE002",
    ]
    mypy = [
        str(_VENV_PY),
        "-m",
        "mypy",
        "--config-file",
        str(_PYPROJECT),
        "--no-error-summary",
        "--no-color-output",
        "--pretty",
    ]
    # ⚑ ONLY RUFF IS FED ON STDIN, because only ruff's split puts the bytes there.
    # mypy's `--shadow-file` keeps the real path as its argument and reads the staged
    # file itself, so its stdin stays empty.
    pairs: list[tuple[str, list[str], str | None]]
    if stands_for is None:
        pairs = [("ruff", [*ruff, str(target)], None), ("mypy", [*mypy, str(target)], None)]
    else:
        pairs = [
            (
                "ruff",
                [*ruff, "--stdin-filename", str(stands_for), "-"],
                target.read_text(encoding="utf-8"),
            ),
            ("mypy", [*mypy, "--shadow-file", str(stands_for), str(target), str(stands_for)], None),
        ]
    out: list[str] = []
    for name, argv, feed in pairs:
        try:
            p = subprocess.run(
                argv,
                capture_output=True,
                text=True,  # noqa: S603
                input=feed,
                timeout=_TIMEOUT_S,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            out.append(f"--- {name} ---\n({_UNRUN}: {exc})")
            continue
        # ⚑ AN EXIT CODE OF 2 IS NOT A FINDING, IT IS A BROKEN INVOCATION. ruff and
        # mypy both use 1 for "flagged something" and 2 for "could not run" — a config
        # error, an unreadable path, a duplicate module name. summit-1c's probe read a
        # rejected config (`Invalid python version`, a TOML spelling in an INI) as
        # "no findings", producing a GREEN whose cause was a broken instrument, inside
        # the probe written to test an instrument. Naming the third state is the arm.
        if p.returncode not in (0, 1):
            detail = (p.stderr or p.stdout or "").strip()
            out.append(
                f"--- {name} ---\n⚑ {_UNRUN.upper()} (exit {p.returncode}), "
                f"this is UNKNOWN and not a clean bill:\n{detail}"
            )
            continue
        if p.returncode != 0:
            out.append(f"--- {name} ---\n{p.stdout}{p.stderr}")
    return "\n".join(out)


def cited_lines(report: str) -> list[int]:
    """Return every line number a report cites, in first-seen order, deduped."""
    seen: set[int] = set()
    order: list[int] = []
    for pattern in (_RUFF_SITE, _MYPY_SITE):
        for m in pattern.finditer(report):
            n = int(m.group("line"))
            if n not in seen:
                seen.add(n)
                order.append(n)
    return order


def census(report: str) -> list[tuple[str, int]]:
    """Return `(code, count)` for every rule a report cites, commonest first.

    ⚑⚑ THIS MODE EXISTS BECAUSE THE COUNT WAS BEING TAKEN IN THE TURN. A paydown asks
    "how many findings does this file carry, before and after" — and with only a
    full-text report to read, that number was arrived at by eye, or by piping the
    report into a shell counter. Both are the judgement-in-a-turn shape this repo's
    standing rule forbids, and neither survives the turn: the next reader re-derives it
    differently, on a report whose format has since moved.

    ⚑ AND THE CODE, NOT JUST THE TOTAL. A bare total says a file got better or worse; a
    per-code census says WHICH class moved, which is what tells a paydown whether it
    retired a class or merely shifted one. A total is recoverable from this; the split
    is not recoverable from a total.
    """
    counts: dict[str, int] = {}
    for pattern in (_RUFF_CODE, _MYPY_CODE):
        for m in pattern.finditer(report):
            code = m.group("code")
            counts[code] = counts.get(code, 0) + 1

    # ⚑ THE KEY IS A NAMED, TYPED FUNCTION RATHER THAN A LAMBDA. Under this repo's
    # `disallow_any_expr`, a bare `lambda kv:` is an untyped parameter, so every read
    # off it is an `Any` expression and the sort leaks three findings. The remedy is at
    # the DEFINITION — one annotation — not a cast at the call site.
    def _rank(kv: tuple[str, int]) -> tuple[int, str]:
        return (-kv[1], kv[0])

    return sorted(counts.items(), key=_rank)


def render(source: str, lines: list[int]) -> str:
    """Return the numbered neighbourhood of each cited line.

    ⚑ THE NEIGHBOURHOOD, NOT THE BARE LINE. A finding often names the first line of a
    multi-line construct — a decorator, a call whose arguments span lines, a
    comprehension — so a single line reads as innocent while its continuation carries
    the defect. Context either side is what makes the construct visible.
    """
    src = source.splitlines()
    if not lines:
        return "(the report cites no line numbers)"
    out: list[str] = []
    for target in lines:
        lo = max(1, target - _CONTEXT)
        hi = min(len(src), target + _CONTEXT)
        out.append(f"--- line {target} ---")
        out.extend(f"{n:>5} {'>' if n == target else ' '} {src[n - 1]}" for n in range(lo, hi + 1))
    return "\n".join(out)


def _usage() -> str:
    """Return the usage text."""
    return (
        "usage: pycheck_show.py <file.py>            check it and show every cited line\n"
        "       pycheck_show.py <file.py> <line>…    show those lines of it, no checking\n"
        "       pycheck_show.py --count <file.py>    per-rule finding census + the total\n"
        "\n"
        "  ⚑ Answers the question `--check-file` cannot: WHAT IS AT LINE N.\n"
        "    The hook lints a tempfile that is deleted before you can read it, so a\n"
        "    report naming `line 383` names a line with no readable referent — and\n"
        "    guessing which construct is there is judgement-in-the-turn.\n"
    )


def _census_cases() -> int:
    """Check `census` reads both renderers, ignores prose, and empties to nothing.

    ⚑ ITS OWN FUNCTION BECAUSE THE ARMS ARE THE UNIT. Folding three more branches into
    `_selftest` tripped the complexity gate — which is the gate saying the unit is
    wrong, not that the cases are unwelcome.
    """
    failures = 0
    # ⚑ BOTH RENDERERS, ORDERED BY COUNT. A ruff code sits at the HEAD of its finding;
    # a mypy code sits bracketed at the TAIL — so a reader that knows only one spelling
    # reports the other tool's findings as zero, which is the census-keyed-on-one-
    # spelling shape this repo has already been bitten by.
    mixed = (
        "ANN201 Missing return type\n  --> a.py:1:1\n"
        "ANN201 Missing return type\n  --> a.py:9:1\n"
        "T201 `print` found\n  --> a.py:4:1\n"
        'a.py:7: error: Expression has type "Any"  [misc]\n'
    )
    if census(mixed) != [("ANN201", 2), ("T201", 1), ("misc", 1)]:
        sys.stderr.write(f"selftest: census wrong: {census(mixed)}\n")
        failures += 1

    # ⚑ PROSE IS NOT A CODE, for the same reason prose is not a site. The deny message
    # this tool is read beside is full of capitalised words and colons.
    if census("  ⚑ ZERO TOLERANCE: there is no suppression path\n"):
        sys.stderr.write("selftest: prose read as a rule code\n")
        failures += 1

    # ⚑ AN EMPTY REPORT CENSUSES TO NOTHING, and that is a CLEAN file rather than an
    # unrun check — the two are distinguished upstream, by `run_checks` naming its own
    # third state, not here.
    if census(""):
        sys.stderr.write("selftest: an empty report censused to something\n")
        failures += 1

    # ⚑⚑ THE POSITIVE CONTROL FOR THE THIRD STATE, IN BOTH SPELLINGS. This is the arm
    # that would have caught the measured defect: an unrun checker's report censuses to
    # the empty list, indistinguishable from CLEAN, so the marker — not the count — is
    # what `_count_mode` must key on. `run_checks` writes it in two cases, and a
    # case-exact reader catches only one.
    for spelling in (
        f"--- ruff ---\n({_UNRUN}: [Errno 2] no such file)\n",
        f"--- mypy ---\n⚑ {_UNRUN.upper()} (exit 2), this is UNKNOWN\n",
    ):
        if census(spelling):
            sys.stderr.write(f"selftest: an unrun report censused rules: {spelling!r}\n")
            failures += 1
        if _UNRUN not in spelling.lower():
            sys.stderr.write(f"selftest: the unrun marker is unreadable: {spelling!r}\n")
            failures += 1
    return failures


def _count_mode(target: Path) -> int:
    """Print the per-rule census for one file, refusing when a checker did not run.

    ⚑⚑⚑ THE REFUSAL IS THE POINT, AND IT WAS FOUND BY RUNNING THIS MODE, NOT BY
    FORESEEING IT. The first draft printed `0 finding(s)` for a file carrying hundreds,
    because it was invoked as a COPY outside the tree: `_ROOT` is derived from
    `__file__`, so both checkers failed with `No such file or directory` on a venv that
    was not there, `run_checks` recorded its own COULD-NOT-RUN third state in the
    report text — and `census` counted no rule codes in it and returned an empty list.
    A count mode that cannot distinguish CLEAN from UNRUN is worse than no count mode:
    a paydown reads the zero as its own success.

    ⚑ SO THE THIRD STATE IS CHECKED WHERE IT IS CONSUMED, not left as prose in a report
    nobody re-reads. `run_checks` already names it correctly; the defect was a reader
    that collapsed it. Same shape as a ratchet whose absent baseline exits 0.
    """
    report = run_checks(target)
    # ⚑ CASE-INSENSITIVE BECAUSE THE TWO WRITERS DIFFER IN CASE — the OSError arm reads
    # `(could not run: …)` and the exit-2 arm shouts `⚑ COULD NOT RUN (exit 2)`. A
    # case-exact reader would catch the first and miss the second, which is a census
    # keyed on one spelling of a two-spelling relation.
    if _UNRUN in report.lower():
        sys.stderr.write(
            f"pycheck_show: a checker COULD NOT RUN against {target} — "
            f"this is UNKNOWN, not a count:\n{report}\n"
        )
        return 2
    rows = census(report)
    for code, n in rows:
        sys.stdout.write(f"  {n:>5}  {code}\n")
    # ⚑ THE TOTAL IS PRINTED BY THE PROGRAM, NEVER SUMMED BY THE READER. Summing the
    # column by eye is the same judgement-in-a-turn this mode replaces.
    sys.stdout.write(f"{target}: {sum(n for _c, n in rows)} finding(s) in {len(rows)} rule(s)\n")
    return 0


def _show_mode(target: Path, source: str, explicit: list[int]) -> int:
    """Show the given lines, or check the file and show every line it cites."""
    if explicit:
        sys.stdout.write(render(source, explicit) + "\n")
        return 0

    report = run_checks(target)
    if not report.strip():
        sys.stdout.write(f"{target}: CLEAN\n")
        return 0
    sys.stdout.write(report + "\n")
    sys.stdout.write(render(source, cited_lines(report)) + "\n")
    return 1


def _selftest() -> int:
    """Run the cases and return an exit code."""
    failures = 0

    ruff_report = "PLR0915 Too many statements\n  --> scripts/probe.py:475:5\n"
    if cited_lines(ruff_report) != [475]:
        sys.stderr.write("selftest: ruff site not parsed\n")
        failures += 1

    mypy_report = 'scripts/probe.py:428: error: Expression has type "Any"  [misc]\n'
    if cited_lines(mypy_report) != [428]:
        sys.stderr.write("selftest: mypy site not parsed\n")
        failures += 1

    # ⚑ BOTH RENDERERS IN ONE REPORT, DEDUPED AND IN ORDER — the real shape of a
    # `--check-file` failure, and the case that would notice one pattern eating the
    # other's output.
    both = ruff_report + mypy_report + mypy_report
    if cited_lines(both) != [475, 428]:
        sys.stderr.write(f"selftest: combined parse wrong: {cited_lines(both)}\n")
        failures += 1

    # ⚑ PROSE CONTAINING A COLON IS NOT A SITE. A loose pattern matches the deny
    # message's own explanatory text, which would print noise as findings.
    prose = "  ⚑ ZERO TOLERANCE: there is no suppression path\n"
    if cited_lines(prose) != []:
        sys.stderr.write("selftest: prose read as a site\n")
        failures += 1

    src = "\n".join(f"line{n}" for n in range(1, 11))
    shown = render(src, [5])
    if "    5 > line5" not in shown:
        sys.stderr.write("selftest: target line not marked\n")
        failures += 1
    # ⚑ THE BOUND IS COMPUTED FROM `_CONTEXT`, NOT TYPED. My first version of this
    # case asserted line 2 was absent — but 5 - _CONTEXT is 2, so 2 is IN range and
    # the case was wrong while the code was right. A literal in a test is a second
    # copy of a constant, and it fails on exactly the day someone tunes the original.
    if f"{5 - _CONTEXT - 1:>5} " in shown:
        sys.stderr.write("selftest: context wider than declared\n")
        failures += 1
    if "    8   line8" not in shown:
        sys.stderr.write("selftest: trailing context missing\n")
        failures += 1

    # A line near the start must not underflow.
    if "    1 > line1" not in render(src, [1]):
        sys.stderr.write("selftest: first line not renderable\n")
        failures += 1

    failures += _census_cases()

    if failures:
        sys.stderr.write(f"pycheck_show selftest: {failures} failure(s)\n")
        return 1
    sys.stdout.write("pycheck_show selftest: 15/15\n")
    return 0


def main(argv: list[str]) -> int:
    """Dispatch the CLI modes and return the exit code."""
    if "--selftest" in argv:
        return _selftest()
    counting = "--count" in argv
    rest = [a for a in argv if a != "--count"]
    if not rest:
        sys.stdout.write(_usage())
        return 2

    target = Path(rest[0])
    if not target.is_file():
        sys.stderr.write(f"pycheck_show: not a file: {target}\n")
        return 2
    source = target.read_text(encoding="utf-8")

    if counting:
        return _count_mode(target)

    return _show_mode(target, source, [int(a) for a in rest[1:] if a.isdigit()])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
