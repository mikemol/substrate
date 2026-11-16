#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""PreToolUse(Edit|Write|NotebookEdit) — refuse a .py edit that ruff or mypy flags.

⚑ THE FOURTH SIBLING, AND IT GATES THE SAME PROPERTY `hook_shellcheck` GATES, ONE
LANGUAGE OVER. That hook's docstring names the class exactly: *"a defect that does
not crash, it returns a plausible transcript."* Everything it says about shell —
no suppression mechanism, relief on the enumerable side, fail open when the linter
is absent, advisory by default — is restated here by IMPORT rather than by copy
wherever the mechanism allows, because a second body of one capability is how `|&`
went uncovered in the sibling pair.

⚑⚑ THIS FILE IS THE HOOK'S I/O CONTRACT AND NOTHING ELSE, AS OF ⓝ.split-pycheck. It
reads the harness payload, dispatches the CLI modes, and owns the selftest; the
staging, the checker roster, the subprocess call, the COMPOSITE RULE and the message
rendering each live in a sibling with ONE reason to change. **The split was forced by a
lint exemption**: `S603` needs a per-file override, an override over a monolith grants
it to six responsibilities to cover one, and the operator's rule is *"we don't do
line-scoped overrides; we have ecosystem-wide standards, and, if necessary, SRP
per-file overrides."* Per-file overrides are per-RESPONSIBILITY overrides — which is
the import ban's argument in another language, since a `per-file-ignores` entry is a
`using` list, narrowing what is VISIBLE rather than what is covered.

⚑⚑⚑ ZERO TOLERANCE, ONE EXCEPTION — AND THE EXCEPTION IS NAMED IN ADVANCE
(operator, 2026-08-28: *"there is not a false positive rate. zero tolerance, with
one exception; ask the other two how they handled numpy and Any"*). This hook does
NOT carry an EXCLUDE set of discovered false positives. Its sibling's EXCLUDE
exists because shellcheck's false-positive population had to be MEASURED; here the
relief population is known before the first run and is a property of one
dependency:

    numpy ships type stubs, and those stubs thread `Any` through their DTYPE
    generics — an arithmetic or indexing expression on an `ndarray` is typed
    `ndarray[..., dtype[signedinteger[Any]]]`, so `disallow_any_expr` flags EVERY
    such expression. A cast does not rescue it: mypy flags the `Any` in the
    cast's argument before the cast concretises it.

⚑ AND THE RULE THAT FOLLOWS IS **STUB AN UNTYPED DEP, IGNORE A TYPED DEP WHOSE
TYPES CONTAIN `Any`** (linux-sources, measured on their live artifact 2026-08-28).
A stub ADDS types where a dependency ships none. numpy ships them; they merely
contain `Any` — so "fixing" it with a stub means SHADOWING numpy's own stubs with
better ones, i.e. maintaining a fork of numpy's typing surface that drifts with
every release. That is worse than one confined, gated suppression.

⚑⚑⚑ AND THAT SUPPRESSION WAS NEVER BUILT, NOR THE GATE THIS PARAGRAPH CITED FOR IT.
It read: *the suppression is gated by a token walk, not a grep — see
`scripts/check_ignore_holder.py`*, in the present tense, as the live enforcer.
VERIFIED ABSENT 2026-09-02: no such file under either spelling, no successor, and
`module_importers check_ignore_holder` finds no importer of the name.

⚑⚑ THE EXEMPTION DOES NOT EXIST AS POLICY EITHER, which is the finding rather than
the missing file — established from the config and the tree, not from a ledger:
`[tool.ruff.lint.per-file-ignores]` carries no `Any` entry (every row is
`S101`/`S603`/`FBT*`/`PLR*`, each scoped to one responsibility);
`disallow_any_explicit` means the word cannot be SPELLED; there is no numpy
boundary module and no `stubs/numpy`; and `files = ["substrate"]` admits NOT ONE of
numpy's importers, so this gate has never once seen numpy. The reasoning above
about numpy's DTYPE generics is sound and is what a numpy consumer WOULD face; it
describes a case this bar has not yet been asked.

⚑ WHERE THE SAME QUESTION WAS ACTUALLY ANSWERED, THE ANSWER WAS A STUB. `networkx`
ships stubs threading `Any` through its attribute-dict generics — the shape the rule
above says to IGNORE — and `pyproject.toml` records the opposite ruling: *"that is
not a walled boundary; it is the interface itself"*, resolved by `stubs/networkx/`
declaring the three methods this repo calls. So the rule's second clause has a
counter-instance in the tree, and no instance in its favour.

⚑⚑ SO RELIEF IS ENUMERABLE-SIDE ONLY, AND `warn_unused_ignores` IS NOT THE MISSING
GATE UNDER ANOTHER NAME — it bounds no COUNT and enumerates no HOLDER, it only makes
an ignore that stopped being load-bearing into an error. Recorded because it is the
nearest live mechanism and would otherwise be promoted into the enforcer nobody
wrote. `pycheck_message.render` carries the same correction for the DENY text, which
is where an author actually reads it.

⚑ FAIL OPEN WHEN A CHECKER CANNOT RUN — NEVER WHEN IT RAN AND FOUND SOMETHING.
This is the distinction substrate's own `check_mypy_ratchet` collapses, and the
collapse is the reason this hook exists: that ratchet's ABSENT baseline takes a
"no baseline → record and pass" branch and **exits 0 regardless of what it
measured** — once at 116 unrecorded type errors. The verdict is three-valued
(`True` clean / `False` findings / `None` tool absent) precisely so that UNKNOWN
never has to be spelled as PASS. It lives in `pycheck_verdict`.

⚑⚑⚑ AND UNPARSEABLE IS A FOURTH STATE THAT WAS LIVING IN THE FAIL-OPEN ONE
(⟡unparseable-is-not-clean, 2026-09-02). Content that does not parse now RESOLVES
ONTO THE REFUSING SIDE, decided by `pycheck_syntax` before any checker runs. The
`ok is None` arm fails open because a gate cannot deny every edit when its own
dependency is missing and could not be repaired from inside the session it broke; on
a syntax error that rationale INVERTS — the checkers ran fine, the FILE is broken,
and the author fixes it with their next write. **Under any condition that truncates a
write — ENOSPC is the measured one — a half-written file is the EXPECTED artifact**,
so this is not a curiosity: it is the shape the safety net was most likely to bless.

⚑⚑ THE MECHANISM WAS AN ORDERING ACCIDENT, NOT A BLIND SPOT IN BOTH CHECKERS, and
naming it wrong would have hidden a second defect. MEASURED: ruff reports a syntax
error as a FINDING and exits 1; mypy exits 2, which `run_checker` honestly reads as
UNKNOWN; and `analyze_python`'s loop returned on the first `None`, DISCARDING the
refusal ruff had already produced. The hole was a real finding overwritten by a later
checker's UNKNOWN — so it would have persisted even with one parse-aware checker.

⚑⚑⚑ AND THE ORDERING ACCIDENT ITSELF IS NOW GONE, WHICH IS A DIFFERENT REPAIR FROM
THE SYNTAX ONE (⟡the-first-none-wins). Answering unparseable early fixed ONE INSTANCE;
the mechanism — first `None` wins, discarding collected findings — survived for any
future checker that exits 2 after another exits 1 (a mypy plugin crash, a timeout, an
added third checker). `analyze_python` now COLLECTS every outcome and
`pycheck_compose.compose` folds them, so no outcome can pre-empt another by arriving
first. **A MIXED roster REFUSES on the finding AND states the blindness**, because
reporting only the findings would hide that coverage was partial —
`census-green-is-a-fact-about-the-census` on the other side of the same defect.

⚑ ARMED ON THE COMMAND LINE, NOT BY THE ENV BLOCK ALONE. A session already running
when `settings.json` changes never re-reads it, so a hook armed only in the env
block keeps exiting 0 — detecting every violation and reporting none, reading as
armed in review and off in fact. Set `PYCHECK_HOOK_BLOCK=1` inline in the command
string. Both peers volunteered this trap independently.

⚑ THIS FILE MUST PASS ITS OWN BAR. If it is written dirty it cannot be edited once
armed — the hook would refuse every fix to itself, which is the un-repairable-guard
state. It reached exactly that on 2026-08-30 and cost an operator disarm window to
escape; `--check-file` on this path is the dogfood that keeps it out of that state.

⚑⚑ AND THE SPLIT ITSELF NEEDED NO SUCH WINDOW, WHICH IS THE MORE USEFUL FINDING
(operator: *"I don't understand why you can't do a parallel build and then
move-into-place"*). The gate keys on the `.py` SUFFIX, so a module can be built
under another one, checked at its real path, and moved in — a bootstrap where three
files each blocked the next dissolves into three ordinary writes. Disarming was
never the only route; it was the only one being looked at.

⚑⚑ WHAT THIS FILE NEEDS IN ORDER TO RUN. It imports `hook_shellcheck` for two
shared halves, and five `pycheck_*` siblings for its own (which pull two more).
`check_hook_set.py --manifest` derives that set from the import graph, so an adopter
can ask rather than trace it by hand — and an incomplete adoption is a SILENT one,
because a hook that cannot import writes nothing and the harness reads empty stdout
as ALLOW.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# ⚑⚑ IMPORTED BY PACKAGE NAME, AND THAT TWO-LINE CHANGE WAS THE WHOLE MIGRATION IN
# MINIATURE. The first cut mutated `sys.path` and then imported the sibling by bare
# name, which WORKS at runtime and is INVISIBLE to mypy: a path mutation is executed,
# not declared, so no checker can follow it. The repair was not in the import line —
# it was making `scripts/` a package, after which the honest spelling resolves for the
# checker AND the interpreter.
#
# ⚑ THE `_ROOT` PRELUDE STAYS ANYWAY, AND IT IS NOT REDUNDANT WITH THAT. `scripts/` is
# a package HERE and a bare directory in an adopting repo; `check_hook_set.py` arm 2
# asserts every sibling-importing hook carries this. Measured by paperkit-c3: without
# it the honest spelling raises `ModuleNotFoundError` AT MODULE LOAD, the harness reads
# empty stdout as ALLOW, and the hook denies nothing while reading as armed in review.
#
# ⚑⚑⚑ `absolute()`, NEVER `resolve()`, AND RUFF WILL TELL YOU OTHERWISE. `PTH100`
# offers `Path.resolve()` as the counterpart of `os.path.abspath`, and it is NOT one:
# `resolve()` FOLLOWS SYMLINKS. While these hooks were symlinked into other checkouts,
# a resolved `__file__` derived SUBSTRATE's root and a hook read substrate's data
# instead of the adopting repo's. That substitution shipped in a sibling on
# 2026-08-30, reached every adopter at write time, and was caught by a peer's routes
# slice — never by anything in this tree, because substrate is the one repo with no
# symlink to follow.
_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    # ⚑⚑ NOT REPOINTED AT mtools' PACKAGE, AND THE REASON IS OUTSIDE THIS TREE (2026-09-22).
    # Importing `mikemol.hooks.shellcheck` here was tried and silently DISARMED paperkit's gate:
    # paperkit adopts this file by SYMLINK and runs it with bare `python3`, which has no
    # `mikemol` package, so the hook reported "ARMED BUT INERT — checking NOTHING". Symlinked
    # adopters get exactly the imports of this tree's `scripts/`; the repoint waits until each
    # adopter runs the hook from an environment that has mikemol-hooks.
    from scripts import hook_shellcheck
    from scripts.pycheck_analyze import analyze_python, tools_available
    from scripts.pycheck_compose import Outcome, compose
    from scripts.pycheck_message import CHECK_FILE_LINES, clip, render
    from scripts.pycheck_payload import armed, as_record, text_of
    from scripts.pycheck_syntax import syntax_error
except ImportError as _e:  # pragma: no cover - adoption-shaped, not reachable in-repo
    # ⚑ FAIL LOUD, NEVER SILENT-ALLOW. Emitting nothing here is what the harness reads
    # as permission granted; a hook that cannot load must SAY so on stderr and exit
    # non-blocking rather than vanish. This is the `None` arm of the tristate, raised
    # to module scope — the fourth state resolved INTO the design, not around it.
    sys.stderr.write(
        f"hook_pycheck: ARMED BUT INERT — cannot import a sibling ({_e}). This hook "
        f"is checking NOTHING. Fix: make the adopting repo's `scripts/` importable "
        f"(an `__init__.py`), or unarm this hook so it does not read as a guard it "
        f"is not. `check_hook_set.py --manifest` names the files a working adoption "
        f"requires.\n"
    )
    sys.exit(0)

# The tools this hook gates. Anything else is out of scope and must be allowed.
_EDIT_TOOLS = ("Write", "Edit", "NotebookEdit")


def _announce_inert(report: str) -> None:
    """Say once, on stderr, that this hook is armed but checking nothing.

    ⚑ UNKNOWN IS NOT CLEAN, AND UNKNOWN IS NOT GUILTY — the sibling's rule, repeated
    rather than assumed: a silently-toothless gate must not be able to masquerade as
    a passing one.

    ⚑⚑ AND UNPARSEABLE IS NEITHER, WHICH IS WHY IT NO LONGER ARRIVES HERE. This arm
    is for a gate whose own dependency is missing; a syntax error is the AUTHOR's
    content failing, is repairable in the next write, and refuses instead.

    ⚑⚑⚑ ONCE PER PROCESS IS RIGHT HERE AND WOULD BE WRONG ON A REFUSAL, which is why
    the MIXED case does not route through this function. This notice describes a
    STANDING condition — the venv is absent, nothing is being checked — and repeating
    it per write would be noise. Partial coverage beside a refusal is a PER-WRITE fact
    about one verdict, so it rides in that verdict's report (`compose.blindness_note`),
    where the second refused file in a session still carries it. Attaching it here
    would have made it silent exactly when a second refusal needed it.
    """
    if not armed() or os.environ.get("_PYCHECK_HOOK_NOTIFIED"):
        return
    os.environ["_PYCHECK_HOOK_NOTIFIED"] = "1"
    sys.stderr.write(
        f"pycheck hook: ARMED BUT INERT — {report}, so no Python is being "
        "checked.\n  This fails OPEN deliberately (a gate cannot deny every "
        "edit because its\n  own dependency is missing, and could not be "
        "repaired from inside the\n  session it broke).\n"
    )


def main() -> int:
    """Read the PreToolUse payload from stdin and refuse or allow the edit."""
    # ⚑ THE EXCEPTIONS ARE NAMED, AND BLE001 WAS RIGHT TO REFUSE THE BLIND CATCH.
    # A bare `except Exception` here would swallow a bug in this hook's own logic
    # and return 0 — i.e. ALLOW — making a broken gate indistinguishable from a
    # passing one. That is the fail-open this file exists to refuse, wearing the
    # uniform of defensive coding. Only a malformed or unreadable payload is
    # tolerated; anything else must crash loudly where it can be seen.
    try:
        raw: object = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError, OSError):
        return 0  # never break the session on a parse failure
    payload = as_record(raw)
    tool = text_of(payload.get("tool_name"))
    if tool not in _EDIT_TOOLS:
        return 0
    path, content = hook_shellcheck.post_edit_content(tool, as_record(payload.get("tool_input")))
    if content is None or not str(path).endswith(".py"):
        return 0

    ok, report = analyze_python(content, str(path))

    if ok is None:
        _announce_inert(report)
        return 0
    if ok:
        return 0
    return hook_shellcheck.emit(render(report, str(path)), armed())


def _check_file(target: str) -> int:
    """Run this hook's own analyzer over a file on disk and report the verdict.

    ⚑ THE DOGFOOD ENTRY POINT. This hook must read clean through its own analyzer or
    it cannot be edited once armed — the un-repairable-guard state, which this file
    reached on 2026-08-30 and escaped only through a disarm window the operator had
    to open. Keeping it clean is what makes that window unnecessary.
    """
    try:
        source = Path(target).read_text(encoding="utf-8")
    except OSError as e:
        sys.stdout.write(f"unreadable: {e}\n")
        return 2
    ok, report = analyze_python(source, target)
    label = {True: "CLEAN", False: "FINDINGS", None: "UNKNOWN"}[ok]
    sys.stdout.write(f"{target}: {label}\n")
    if report:
        # ⚑⚑ BOUNDED, BECAUSE THIS IS THE MODE THAT EMITTED 398 KB. `render` has
        # capped the DENY message since it was written; this path printed the whole
        # report, and it is the one a reader runs to understand a refusal — so the
        # unbounded output landed in exactly the context the bound exists to protect.
        sys.stdout.write(clip(report, CHECK_FILE_LINES) + "\n")
    return 0 if ok else 1


class _Cases:
    """Collect selftest outcomes, naming each expectation at the call site."""

    def __init__(self) -> None:
        self.rows: list[tuple[str, bool, str, str]] = []

    def _record(self, label: str, *, ok: bool, got: object, want: object) -> None:
        """Record one outcome, rendering the values at the boundary."""
        self.rows.append((label, ok, repr(got), repr(want)))

    def equal(self, label: str, got: object, want: object) -> None:
        """Record a case asserting `got == want`."""
        self._record(label, ok=got == want, got=got, want=want)

    def holds(self, label: str, *, got: bool) -> None:
        """Record a case asserting a plain property holds."""
        self._record(label, ok=got is True, got=got, want=True)

    def denies(self, label: str, *, got: bool) -> None:
        """Record a case asserting a plain property does NOT hold."""
        self._record(label, ok=got is False, got=got, want=False)

    def report(self, suite: str) -> bool:
        """Print any failures and the tally; return whether every case held."""
        ok = sum(1 for _n, g, _a, _b in self.rows if g)
        for name, good, got, want in self.rows:
            if not good:
                sys.stdout.write(f"  FAIL {name}: got {got} want {want}\n")
        sys.stdout.write(f"{suite} selftest: {ok}/{len(self.rows)}\n")
        return ok == len(self.rows)


# ⚑ NAMED FIXTURES, NOT INLINE LITERALS AT THE CALL SITE — a nested literal is
# inferred on its own as an untyped mapping, which the strict bar refuses once the
# result flows into a recorded value.
_NOT_A_MAPPING: list[str] = ["nope"]
_EMPTY_PAYLOAD: dict[str, object] = {}


def _payload(tool: str, path: str) -> dict[str, object]:
    """Build an edit payload naming `path`, typed at every level."""
    tool_input: dict[str, object] = {"file_path": path, "content": "x = 1\n"}
    return {"tool_name": tool, "tool_input": tool_input}


def _cases_verdict(c: _Cases) -> None:
    """Add the cases for the tristate — the property this hook exists to hold.

    ⚑ `False` (findings) AND `None` (checker absent) MUST NEVER MERGE. These arms
    exist because the ratchet this hook was built to replace merged them, and exited
    0 on 116 unrecorded errors.
    """
    # ⚑ THE CLEAN FIXTURE CARRIES A DOCSTRING, AND THE FIRST VERSION DID NOT — it was
    # `x: int = 1`, which is annotated and still fails D100 under this bar. The arm
    # reported FAIL and the HOOK WAS RIGHT: a fixture that does not meet the bar
    # cannot test whether the bar recognises clean. The case was wrong, not the gate.
    clean_ok, clean_report = analyze_python(
        '"""A clean probe module."""\n\nX: int = 1\n', "probe.py"
    )
    c.holds("a source meeting the bar reads CLEAN, not UNKNOWN", got=clean_ok is True)
    c.equal("...and carries no report", clean_report, "")

    dirty_ok, dirty_report = analyze_python(
        '"""A probe with one defect."""\n\nimport os\n', "scripts/probe.py"
    )
    c.holds("an unused import reads FINDINGS", got=dirty_ok is False)
    c.holds("...and the report names the rule", got="F401" in dirty_report)
    # ⚑ THE PATH IS PART OF THE VERDICT, not decoration: a message naming a deleted
    # tempfile tells the author nothing about their own file. ruff now renders it
    # directly via `--stdin-filename`; mypy's half still comes from the rewrite.
    c.holds("...and names the author's path", got="scripts/probe.py" in dirty_report)


def _cases_syntax(c: _Cases) -> None:
    """Add the cases for UNPARSEABLE — the fourth state, resolved onto the refusing side.

    ⚑⚑ THE HOLE THIS CLOSES: a file neither checker could report a normal finding on
    read as CLEAN and was banked as good. **Under any condition that truncates a write
    — ENOSPC is the measured one — a half-written file is the EXPECTED artifact**, so
    the disk condition converted the stated safety net into a rubber stamp.

    ⚑⚑ AND THE MECHANISM WAS AN ORDERING ACCIDENT, NOT A BLIND SPOT IN BOTH CHECKERS.
    ruff reports a syntax error as a FINDING (exit 1); mypy exits 2, honestly UNKNOWN;
    and `analyze_python`'s loop returned on the first `None`, DISCARDING the refusal
    ruff had already produced. The hole was a real finding overwritten by a later
    checker's UNKNOWN — it would have survived even one parse-aware checker.

    ⚑ THAT MECHANISM IS ADDRESSED SEPARATELY IN `_cases_compose`. Deciding syntax here
    is still right — one authoritative answer beats reconciling two disagreeing
    checkers — but it fixed the INSTANCE, and the general fold fixes the CLASS.

    ⚑⚑⚑ WHY IT REFUSES RATHER THAN JOINING THE INERT ARM. `None` fails open because a
    gate cannot deny every edit when its own dependency is missing and could not be
    repaired from inside the session it broke. On a syntax error that rationale
    INVERTS: the checkers ran, the FILE is broken, and the author repairs it with
    their next write without restoring anything.

    ⚑⚑ AND THERE IS NO AUTHOR-MID-REPAIR TRAP TO GUARD AGAINST. This hook gates
    POST-EDIT content, so the only writes refused are ones whose RESULT does not parse
    — a write that FIXES the syntax parses and is admitted however broken the file was
    before. An "improves parseability" allowance would be strictly WEAKER: it would
    admit a write that leaves the file unparseable, which is precisely the state this
    arm exists to catch.
    """
    broken_ok, broken_report = analyze_python("def broken(  # noqa: ANN201\n", "scripts/probe.py")
    c.holds("unparseable reads FINDINGS, not UNKNOWN", got=broken_ok is False)
    c.holds("...and not CLEAN", got=broken_ok is not True)
    c.holds(
        "...and the report names the syntax error, not 'no findings'",
        got="[syntax]" in broken_report,
    )
    c.holds("...and names the author's path", got="scripts/probe.py" in broken_report)

    # ⚑⚑ THE PAIRED ARM, AND IT IS WHAT MAKES THE REFUSAL MEAN ANYTHING. A gate that
    # refuses everything passes any "it refuses" test and is useless.
    admitted_ok, _r = analyze_python('"""A clean probe module."""\n\nX: int = 1\n', "probe.py")
    c.holds("valid clean source is still ADMITTED", got=admitted_ok is True)

    # ⚑ A NUL BYTE IS THE REACHABLE `ValueError` CASE, and a truncated write is exactly
    # how one arrives: the parser rejects it before it can locate a position, so
    # `compile` raises `ValueError` rather than `SyntaxError`.
    c.holds(
        "content the parser rejects without a position still refuses",
        got=bool(syntax_error("x = 1\x00\n", "probe.py")),
    )
    c.equal(
        "source that parses yields the empty reason", syntax_error('"""D."""\n', "probe.py"), ""
    )


def _mixed(*outcomes: tuple[str, Outcome]) -> tuple[bool | None, str]:
    """Compose a hand-built roster, so a could-not-run checker is testable at all.

    ⚑ THE UNRUNNABLE CHECKER IS THE SUBJECT, AND IT CANNOT BE STAGED THROUGH
    `analyze_python` WITHOUT BREAKING THE VENV FOR THE WHOLE PROCESS. `compose` is a
    pure fold over outcomes, so the mixed roster is built directly here; the live
    end-to-end confirmation is a separate probe pointing `VENV_PY` at a nonexistent
    interpreter, which is what actually proves the wiring.
    """
    return compose(list(outcomes))


def _cases_compose(c: _Cases) -> None:
    """Add the cases for MIXED — a checker FINDS while another CANNOT RUN.

    ⚑⚑ THE DEFECT: `analyze_python` returned on the first `None`, DISCARDING findings
    an earlier checker had already produced. MEASURED on `def broken(`: ruff exits 1
    with `invalid-syntax` (a real refusal) and mypy exits 2 (honestly UNKNOWN), and the
    composite reported UNKNOWN showing only mypy. **A refusal was overwritten by a later
    checker's inability to run** — an ordering accident, decided by roster position
    rather than by evidence.

    ⚑⚑⚑ THE THREE DISCRIMINATORS, AND WITHOUT THEM "it refuses" IS UNFALSIFIABLE. A
    fold that always returned `False` would pass a mixed-refuses test and destroy the
    hook; a fold that always returned `None` would pass an all-unknown test and gate
    nothing. So each arm is paired with a case that FAILS if the predicate is constant:
    mixed REFUSES, all-unknown stays UNKNOWN, and a fully-covered clean roster is
    ADMITTED.

    ⚑⚑ CLEAN-UNDER-PARTIAL-COVERAGE IS THE FOURTH ARM AND IT IS NOT A PASS. One checker
    clean and one unable to run is UNKNOWN, never `True`: the checker that did not run is
    exactly the one that might have objected, so banking it as clean is
    `census-green-is-a-fact-about-the-census` — a fact about the roster reported as a
    fact about the file.
    """
    found: Outcome = (False, "--- ruff ---\nF401 unused import")
    absent: Outcome = (None, "mypy is not installed in the project venv")
    clean: Outcome = (True, "")

    ok, report = _mixed(("ruff", found), ("mypy", absent))
    c.holds("a finding beside a could-not-run REFUSES", got=ok is False)
    c.holds("...and the finding survives", got="F401" in report)
    c.holds("...and the blindness is stated", got="--- coverage ---" in report)
    c.holds("...naming the checker that did not run", got="mypy is not installed" in report)

    # ⚑ ORDER-INDEPENDENCE IS THE REPAIR ITSELF, so it gets its own arm. The defect was
    # that the roster's ORDER decided the verdict; permuting it must now change nothing.
    flipped, _f = _mixed(("mypy", absent), ("ruff", found))
    c.holds("...and roster order does not change it", got=flipped is False)

    # ⚑⚑ DISCRIMINATOR: all-UNKNOWN must STILL be UNKNOWN, or the fail-open path — a
    # gate cannot deny every edit because its own dependency is missing — is gone.
    none_ok, none_report = _mixed(("ruff", absent), ("mypy", absent))
    c.holds("all-could-not-run stays UNKNOWN", got=none_ok is None)
    c.holds("...and reports why", got="not installed" in none_report)

    # ⚑⚑ DISCRIMINATOR: a fully-covered clean roster is ADMITTED, or the gate refuses
    # everything and "it refuses" means nothing.
    c.holds(
        "a clean fully-covered roster is ADMITTED",
        got=_mixed(("ruff", clean), ("mypy", clean))[0] is True,
    )

    # ⚑⚑ THE ARM THAT LOOKS LIKE A PASS AND MUST NOT BE ONE.
    partial_ok, _p = _mixed(("ruff", clean), ("mypy", absent))
    c.holds("clean under PARTIAL coverage is UNKNOWN, not clean", got=partial_ok is None)
    c.denies("...and is not banked as a pass", got=partial_ok is True)

    # ⚑ AN EMPTY ROSTER IS THE DEGENERATE PARTIAL CASE, never a green.
    c.holds("an empty roster is UNKNOWN", got=compose([])[0] is None)

    # ⚑ AND A CLEAN VERDICT CARRIES NO COVERAGE NOTE, so the note itself discriminates
    # rather than decorating every message.
    c.equal(
        "a fully-covered verdict states no blindness",
        compose([("ruff", clean), ("mypy", clean)])[1],
        "",
    )


def _cases_payload(c: _Cases) -> None:
    """Add the cases for reading the hook's own input.

    ⚑ A hook that mis-reads its own INPUT renders a verdict about something other
    than what ran, so every rejected shape gets a case.
    """
    c.equal("a non-mapping payload yields an empty record", as_record(_NOT_A_MAPPING), {})
    c.equal("an empty payload yields an empty record", as_record(_EMPTY_PAYLOAD), {})
    c.equal("a non-string tool name reads as empty", text_of(7), "")
    c.holds(
        "an edit payload's tool name is read",
        got=text_of(_payload("Write", "a.py").get("tool_name")) == "Write",
    )
    # ⚑ THE TOOL ROSTER IS THE SCOPE, and a tool outside it must be allowed rather
    # than analysed — this hook has no opinion about a Bash call.
    c.denies("Bash is not an edit tool this hook gates", got="Bash" in _EDIT_TOOLS)
    c.holds("every edit tool is gated", got=set(_EDIT_TOOLS) >= {"Write", "Edit"})


def _cases_config_reaches(c: _Cases) -> None:
    """Add the cases for configuration reaching an IN-FLIGHT edit.

    ⚑⚑ THIS IS THE ARM THE WHOLE SPLIT WAS FOR, AND NOTHING ASSERTED IT BEFORE. The
    hook stages content to a TEMPFILE, so without `--stdin-filename` a checker
    resolves path-keyed configuration against `tmpab12cd.py` and matches NO pattern —
    every `per-file-ignores` entry is inert for an in-flight edit while applying
    normally to the same file on disk. **The gate and a direct `ruff check` then
    disagree about the same file, always**, in the direction that manufactures
    findings the author cannot act on.

    ⚑ THE WITNESS IS THIS REPO'S OWN S603 ENTRY, which is keyed to
    `scripts/pycheck_verdict.py` and is the one exemption the split created. If
    configuration stops reaching, this arm fails — where previously the symptom was a
    file that could not be written and no test that said why.
    """
    source = Path(__file__).absolute().parent / "pycheck_verdict.py"
    if not source.exists():  # pragma: no cover - the sibling is in the manifest
        c.holds("the S603-exempt sibling exists to test against", got=False)
        return
    ok, _report = analyze_python(source.read_text(encoding="utf-8"), str(source))
    c.holds("a path-keyed exemption reaches an in-flight edit", got=ok is True)


def _selftest() -> bool:
    """Run every case group and report whether all of them hold.

    ⚑ THIS HOOK HAD NO SELFTEST AT ALL UNTIL 2026-08-30. `--selftest` fell through to
    normal hook operation, read empty stdin, and exited 0 SILENTLY — so the file
    ENFORCING the bar could not demonstrate that it worked. A gate whose own
    behaviour has never been observed is a gate nobody has read.

    ⚑ AND AN ABSENT CHECKER MAKES THIS UNMEASURED, NOT PASSED. The checkers are the
    SUBJECT here, not an environment detail: without them there is no verdict to
    test, and reporting green would be exactly the collapse the tristate exists to
    refuse.

    ⚑ THE MESSAGE ARMS MOVED OUT WITH ⓝ.split-pycheck. A module that owns a
    responsibility owns the cases for it; leaving them here would make this file the
    place every sibling's behaviour is asserted, which is the monolith re-forming
    through its test suite.
    """
    if not tools_available():
        sys.stdout.write(
            "hook_pycheck selftest: UNMEASURED — the project venv or pyproject.toml "
            "is absent, so no verdict arm can run.\n"
            "  ⚑ This is UNKNOWN, not a pass: the checkers are the subject.\n"
        )
        return False
    c = _Cases()
    _cases_verdict(c)
    _cases_syntax(c)
    _cases_compose(c)
    _cases_payload(c)
    _cases_config_reaches(c)
    return c.report("hook_pycheck")


def _main() -> int:
    """Dispatch the CLI modes and return the exit code."""
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    if "--check-file" in sys.argv:
        i = sys.argv.index("--check-file")
        if len(sys.argv) <= i + 1:
            sys.stderr.write("hook_pycheck: --check-file needs a path\n")
            return 2
        return _check_file(sys.argv[i + 1])
    return main()


if __name__ == "__main__":
    sys.exit(_main())
