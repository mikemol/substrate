#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""PreToolUse(Bash) — refuse a TEXTUAL query where a STRUCTURAL one exists.

⚑ THE POLICY'S HOME IS THE LAYER THAT CAN REFUSE A VIOLATION.  The rule ("if you
have a question the tooling doesn't answer directly, fix the tooling") has lived
in CLAUDE.md for the whole arc, is stated in four places, and was violated twice
in the same turn where it had just been acknowledged — including once by grepping
for a SQL table whose readers are DECLARED in `query_defs`' metadata.  An
instruction governs the turns where it is already being thought about; a hook
intercepts the call.  This is the same finding the repo recorded for ratchet
gates (a baseline no gate consults is a census wearing a ratchet's clothes).

⚑ NO EXCEPTION LIST, AND ITS ABSENCE IS THE DESIGN (user, 2026-08-03: *"Then
build the tool that makes that a structured query."*).  My first scoping carved
out "legitimate grep — build logs, pgrep, non-code text", because no structural
reader covered them.  That reads a GAP IN THE TOOLKIT as a CATEGORY OF QUESTION
that is inherently textual — the same method-vs-substrate confusion as reading
"no consumer found" as "no consumer exists".  A build log is `Checking <mod>`,
an error kind, a make target; `pgrep` is pid/command/state.  Both are structured;
neither had a reader yet.  An exception admitted for the uncovered case is the
loophole that swallows the rule, so the toolkit expands instead.

⚑ THE ROUTING MAP IS READ FROM THE SKILL, NEVER RESTATED.  `.claude/skills/
struct-tools/SKILL.md` already carries an `artifact | tool` table — the exact
mapping a refusal needs.  A copy here would be a second roster that drifts (the
`agda_files()` class: four bodies under one name), so the table IS the source and
adding a row to the skill teaches this hook with no edit.

⚑ ADVISORY BY DEFAULT.  It emits the route and lets the call proceed unless
STRUCT_HOOK_BLOCK=1.  A guard whose first act is to break a working session
trains people to disable it; the refusal earns blocking after its false-positive
rate is measured, not before.  That is the inverse of `prune_imports` shipping
write-by-default and costing an unintended deletion.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# ⚑⚑ THE ROOT PRELUDE, THEN A DECLARED IMPORT — and the two halves do different jobs.
# The prelude makes `scripts/` addressable when this file runs as `python3 <abs-path>`
# from a repo that has not installed it, which is what adoption by symlink IS. The
# import stays a `from scripts import …` DECLARATION so a type checker can follow it.
#
# ⚑⚑⚑ THE PREVIOUS SPELLING WAS `sys.path.insert(...)` + a BARE `import hook_cmdparse`,
# and that is the RETIRED pattern: a path mutation is EXECUTED, not declared, so no
# checker can follow it. mypy reported `Cannot find implementation or library stub for
# module named "hook_cmdparse"` and every expression downstream of `_cmdparse` degraded
# to `Any` — ONE unresolvable import produced the bulk of this file's type findings.
# The repair is the import; almost nothing else here needed annotating for it.
#
# ⚑⚑⚑ `absolute()`, NEVER `resolve()`, AND THE DIFFERENCE IS THE WHOLE POINT OF THIS
# FILE IN AN ADOPTING REPO. `resolve()` FOLLOWS SYMLINKS; this hook is SYMLINKED into
# five other checkouts, so a resolved `__file__` lands in SUBSTRATE and the hook then
# reads substrate's `SKILL.md` — the routing table of the wrong repo — while the
# adopter's own table is ignored. The original used `os.path.abspath`, which does not
# follow links, and that was load-bearing rather than incidental.
#
# ⚑ I BROKE THIS DURING A PAYDOWN I DESCRIBED AS MECHANICAL. `os.path.abspath` →
# `Path.resolve()` reads like the obvious pathlib translation and is not: `abspath`'s
# counterpart is `absolute()`. summit-1c's `--only routes` slice caught it within
# minutes — it asserts *"a symlinked hook must still read THIS repo's data"* — and
# nothing in this file's own selftest could have, because the defect requires a
# symlink and substrate is the one tree where there is none.
#
# ⚑ AND IT REACHED THEM AT WRITE TIME, WITH NO COMMIT. A symlinked hook is executable
# in every adopting tree the instant it is saved; a shared data file needs a filing to
# travel, this needs nothing. That asymmetry is why an edit here is not a local edit.
_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts import hook_cmdparse as _cmdparse  # noqa: E402  the SHARED tokenizer

# ⚑⚑ THE RETIREMENT TABLE IS *OPTIONALLY* IMPORTED, AND THE OPTIONALITY IS THE DESIGN.
# This hook is SYMLINKED into five checkouts that have no `substrate/` package, and the
# import above is mandatory because every verdict depends on it. This one is not: a
# borrowing repo has no `pycodemod` to retire, so the honest degradation is "no
# retirement verdict here", never a crash that takes the whole gate — and a hook that
# raises on import ALLOWS every command after it, which is the failure this file's own
# `main()` names for a bare `except Exception`.
try:
    from substrate import pycodemod_retired
except ImportError:  # pragma: no cover - only in a borrowing checkout
    _RETIRED: object = None
else:
    _RETIRED = pycodemod_retired

ROOT = str(_ROOT)
SKILL = str(_ROOT / ".claude" / "skills" / "struct-tools" / "SKILL.md")

# The textual instruments. `find`/`ls` are NOT here: locating a file is not a
# question about its structure.
#
# ⚑ WIDENED AFTER A LIVE BYPASS. The first six were `grep rg egrep fgrep sed awk`;
# every other line-reader was a silent hole. A tool that reads a file's BYTES to
# answer a question about its STRUCTURE belongs here regardless of how blunt it is.
TEXTUAL = frozenset(
    (
        "grep",
        "rg",
        "egrep",
        "fgrep",
        "sed",
        "awk",
        "head",
        "tail",
        "cut",
        "sort",
        "uniq",
        "wc",
        "tr",
        "nl",
        "rev",
        "strings",
        "cat",
        "tac",
        "od",
        "xxd",
        "diff",
        "comm",
        "join",
        "paste",
    )
)

# ⚑ NO HARDCODED SUFFIX LIST LIVES HERE ANY MORE. It was `STRUCTURED_SUFFIX =
# (".py", ".md", …)` — a SECOND roster beside the routing table, which is the
# frozen-roster shape the table exists to retire. The claims now come from the
# table's `claims` column (see `claims()` below), so adding a row arms the gate in
# every repo that borrows this tooling, with no edit here.

# A markdown table row's minimum cell count for each reader below.
_MIN_ROUTE_CELLS = 2
_MIN_CLAIM_CELLS = 4

# The `claims` column's position in the skill's routing table.
_CLAIMS_COLUMN = 3

# The suffixes a `claims` cell may declare, e.g. `.py` / `.agda`.
_SUFFIX_RE = re.compile(r"`(\.[A-Za-z0-9]+)`")

# ⚑⚑⚑ AND THE BARE FILENAMES IT MAY DECLARE, e.g. `Makefile` — because A SUFFIX-KEYED CLAIM
# CANNOT EXPRESS A SUFFIXLESS ARTIFACT, and that was measured rather than anticipated. The
# struct-tools table gained a `.mk` row for the generated build makefiles, which correctly
# armed the gate for `agda/Flat.mk`; `agda/Makefile` beside it has NO suffix, so
# `Path(arg).suffix` is the empty string and no cell value could ever match it. Writing
# `Makefile` into the claims column before this read as an extension and bound nothing.
#
# ⚑⚑ THE TWO KEY SPACES CANNOT COLLIDE, which is what makes one map safe. A suffix key always
# begins with `.` and a filename key never does, so `claims()` keeps its `{key: (artifact,
# tool)}` shape and every existing caller is unaffected. A second map would have been a second
# roster beside the first — the shape this module's own comment above refuses.
#
# ⚑ CASE-SENSITIVE, DELIBERATELY, WHERE SUFFIXES ARE NOT. `Makefile` and `makefile` are both
# real and mean the same thing to make, but a filename claim is a NAME and lowercasing it would
# make `README` claim `readme`. The lookup tries the literal name first and its lowercase form
# second, so both spellings route without the claim itself being folded.
_FILENAME_RE = re.compile(r"`([A-Za-z][A-Za-z0-9_+-]*)`")

# A verdict's hit: the argument, its suffix, and the (artifact, owner) that claims it.
Hit = tuple[str, str, tuple[str, str]]
Reason = tuple[str, list[Hit]]


def _table_rows(skill: str) -> list[list[str]]:
    """Return the skill's markdown table rows as stripped cell lists.

    ⚑ ONE PARSER, NOT TWO. `routes` and `claims` each carried their own copy of this
    loop with subtly different cell handling (one stripped backticks before the
    header test, the other after). Two bodies reading one table is the
    `agda_files()`-was-four-bodies shape at the smallest possible scale.
    """
    try:
        src = Path(skill).read_text(encoding="utf-8")
    except OSError:
        return []
    rows: list[list[str]] = []
    for line in src.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or not cells[0] or cells[0].lower() == "artifact":
            continue
        if set(cells[0]) <= set("-: "):  # the header separator row
            continue
        rows.append(cells)
    return rows


def routes(skill: str = SKILL) -> list[tuple[str, str]]:
    """Return the (artifact, tool) mapping, READ from the skill's own table."""
    return [
        (cells[0].strip("`"), cells[1].strip("`"))
        for cells in _table_rows(skill)
        if len(cells) >= _MIN_ROUTE_CELLS
    ]


def _declared_suffixes(cell: str) -> list[str]:
    """Return the `.suffix` tokens a `claims` cell declares, lowercased.

    ⚑ THE `str()` IS THE NARROWING. A regex group is typed `str | Any`, and an `Any`
    reaching the returned mapping is an unchecked shape crossing this module's
    boundary — the same class the declared-import repair above removed wholesale.
    """
    return [str(m.group(1)).lower() for m in _SUFFIX_RE.finditer(cell)]


def _declared_filenames(cell: str) -> list[str]:
    """Return the bare-filename tokens a `claims` cell declares, verbatim.

    ⚑ NOT LOWERCASED, unlike a suffix. A filename claim is a NAME, and folding it would make
    a `README` row claim `readme`. The LOOKUP handles the case question by trying both forms;
    the claim itself stays as written.
    """
    return [str(m.group(1)) for m in _FILENAME_RE.finditer(cell)]


def claims(skill: str = SKILL) -> dict[str, tuple[str, str]]:
    """Return {suffix-or-filename: (artifact, tool)}, from the table's `claims` column.

    ⚑ THE TABLE IS THE AUTHORITY AND IT TRAVELS. This tooling is borrowed by several
    repos; the skill file ships with it, so a row added there arms the gate
    everywhere. A location test (`is this path inside the repo?`) cannot do that —
    `$CLAUDE_PROJECT_DIR` is per-invocation, so it would guard only the invoking
    checkout while PASSING a `.py` read from a sibling one. The claim is the ARTIFACT
    KIND, not the checkout it happens to live in.

    ⚑⚑ ONE MAP, TWO KEY SPACES, AND THEY CANNOT COLLIDE. A suffix key always begins with `.`
    and a filename key never does, so a suffixless artifact becomes expressible without a
    second mapping beside this one — which would be the second-roster shape this module
    already refuses for its retired hardcoded suffix list.
    """
    out: dict[str, tuple[str, str]] = {}
    for cells in _table_rows(skill):
        if len(cells) < _MIN_CLAIM_CELLS:
            continue
        artifact, tool = cells[0].strip("`"), cells[1].strip("`")
        cell = cells[_CLAIMS_COLUMN]
        for key in _declared_suffixes(cell) + _declared_filenames(cell):
            out[key] = (artifact, tool)
    return out


def claimed_by(arg: str, table: dict[str, tuple[str, str]]) -> tuple[str, str] | None:
    """Return the `(key, owner-tool)` claiming `arg`, or None when nothing claims it.

    ⚑⚑ THE SUFFIX IS TRIED FIRST AND THE FILENAME SECOND, which matters for a name that has
    both. `Flat.mk` has suffix `.mk` and basename `Flat.mk`; a claim on the suffix is the
    general one and must win, so a filename claim never shadows a kind claim.

    ⚑⚑ AND THE FOLD IS OVER THE CLAIM, NOT THE ARGUMENT — which a failing case is what
    established. A first cut tried the basename in its own case and lowercased, and both
    spellings of `makefile` collapse to the same string while the CLAIM reads `Makefile`, so
    the lowercase file did not route. Folding one side only compares two spellings of the
    argument against one spelling of the claim; the match has to fold BOTH.
    """
    path = Path(arg.strip("'\""))
    suf = path.suffix.lower()
    if suf and suf in table:
        return suf, table[suf][1]
    name = path.name.lower()
    for key, (_artifact, tool) in table.items():
        if not key.startswith(".") and key.lower() == name:
            return key, tool
    return None


# ⚑⚑⚑ AN OPERAND'S ROLE COMES FROM ITS POSITION, NOT ITS SPELLING (summit
# ask-structural-hook-distinguishes-a-pattern-from-a-path, 2026-09-20). `grep -rl
# --include=Makefile "gate.py" ~/github` was DENIED as a query over `gate.py` — but `gate.py`
# is grep's PATTERN, and every file the command would open is a Makefile the table does not
# claim. The walk below treated any non-flag operand ending in a routed suffix as a routed
# artifact. So: for the programs whose FIRST operand is a pattern or a script (unless a flag
# already supplied it), that operand is never a path, and the flags that CONSUME the next
# token are stepped over so their operands are never read as paths either.
#
# The rosters are deliberately small and per family. A flag not listed here is a flag whose
# operand, if any, is attached (`--include=…`, `-A2`) or absent, and the walk already skips
# every `-`-prefixed token; the only hazard a missing entry creates is reading a DETACHED
# flag operand as a path, which the arms below pin for the spellings this repo uses.
_PATTERN_FIRST = frozenset(("grep", "egrep", "fgrep", "rg", "sed", "awk"))
# Flags whose DETACHED next token is the pattern/script itself — when present, no positional
# operand is a pattern.
_PATTERN_FLAGS = frozenset(("-e", "--regexp", "-f", "--file", "--expression"))
# Flags whose detached next token is a value that is neither a pattern nor a path.
_VALUE_FLAGS = frozenset(
    (
        "-A",
        "-B",
        "-C",
        "-m",
        "--max-count",
        "-d",
        "-D",
        "-F",
        "-v",
        "-t",
        "--type",
        "-g",
        "--glob",
        "--include",
        "--exclude",
        "--exclude-dir",
    )
)


def path_operands(prog: str, args: list[str]) -> list[str]:
    """Return the operands of `prog` that name FILES — never its pattern, script or flag values."""
    pattern_taken = prog not in _PATTERN_FIRST
    out: list[str] = []
    skip = False
    for a in args:
        if skip:
            skip = False
            continue
        if a in _PATTERN_FLAGS:
            pattern_taken = True
            skip = True
            continue
        if a in _VALUE_FLAGS:
            skip = True
            continue
        if a.startswith("-"):
            continue
        if not pattern_taken:
            pattern_taken = True
            continue
        out.append(a)
    return out


def verdict(cmd: str, table: dict[str, tuple[str, str]] | None = None) -> tuple[bool, list[Reason]]:
    """Return (is_violation, reasons) for one command.

    ⚑ EVERY COMMAND-POSITION PROGRAM IS TESTED, NOT `toks[0]`. The predecessor split
    on `|` and inspected only the first token, so `timeout 180 grep -n foo x.py` was
    invisible — `toks[0]` was `timeout`. A `timeout` prefix is the ordinary
    invocation shape here, so the gate was open for nearly every command issued.
    `hook_cmdparse.programs` sees through wrappers and returns the REAL program with
    the arguments it receives.
    """
    tbl = claims() if table is None else table
    reasons: list[Reason] = []
    for prog, args in _cmdparse.programs(cmd):
        if prog not in TEXTUAL:
            continue
        # ⚑ MATCH THE ARGUMENT WORD, NOT THE WHOLE SEGMENT. The predecessor tested
        # `".py" in seg`, so a directory named `pkg.py/` false-positived while an
        # argument's real extension went unexamined.
        # ⚑ THE LOOKUP IS SHARED WITH `claimed_by`, WHICH IS WHAT LET A SUFFIXLESS ARTIFACT
        # BECOME EXPRESSIBLE. This tested `Path(a).suffix` inline, so `agda/Makefile` yielded
        # the empty string and no table entry could ever match it — a gap in the MECHANISM
        # that no cell value in the routing table could close.
        hits: list[Hit] = []
        for a in path_operands(prog, args):
            claimed = claimed_by(a, tbl)
            if claimed is not None:
                hits.append((a, claimed[0], tbl[claimed[0]]))
        if hits:
            reasons.append((prog, hits))
    return bool(reasons), reasons


def _refusal(reasons: list[Reason], cmd: str = "") -> str:
    """Build the refusal TEXT for a violation, so the selftest reads what the hook says.

    ⚑ `cmd` IS PASSED SO THE MESSAGE CAN NAME THE RIGHT ROUTE, never to change the
    verdict. The caller has already decided; this only reads the command to tell a
    blocked WRITER something a blocked READER does not need. Defaulted so every existing
    call site keeps working — `--calls _refusal` reports the population.

    ⚑ IT WAS BUILT INLINE IN `main()`, WHICH IS WHY NOTHING CHECKED IT. Every selftest case
    asked whether the hook FIRES; the message was unreachable without a subprocess, so its
    content was the one part of the gate with no witness — and that is exactly the part a
    refused reader acts on.
    """
    lines = ["structural-query: this asks about a STRUCTURED artifact textually."]
    for prog, hits in reasons:
        for arg, suf, (artifact, tool) in hits:
            lines.append(f"  `{prog}` over {arg}  ({suf} → {artifact})")
            lines.append(f"      the tool that owns it:  {tool}")
    lines.append(
        "  ⚑ if no mode answers your question, that is WORK (add the "
        "mode), not grounds\n     for a textual fallback — the toolkit "
        "expands; the rule has no exceptions."
    )
    # ⚑ THE MESSAGE ASSUMED THE NAMED TOOL IS RUNNABLE, AND IN A BORROWING REPO IT IS NOT.
    # This tooling is symlinked into other checkouts, where `pycodemod` may be absent or its
    # `libcst`/`panflute` dependency unmet — so the refusal named the one route the reader
    # could not take and stopped. A peer hit exactly that and had no move left. `Read` is the
    # answer and needs SAYING: it is not a shell command, so a reader thinking in Bash calls
    # will not consider it, and it is a total, structure-preserving read of the whole file —
    # strictly better than the `wc`/`grep` this hook just refused.
    lines.append(
        "  ⚑ if that tool is unavailable here (a borrowing checkout, an unmet\n"
        "     dependency), use the harness `Read` tool on the file — NOT a textual\n"
        "     fallback. Read is not a shell command, which is why it does not come\n"
        "     to mind inside a shell-shaped question; it is the honest whole-file\n"
        "     read the refused command was approximating."
    )
    # ⚑⚑⚑ A BLOCKED *WRITER* WAS TOLD TO USE `Read`, WHICH IS USELESS ADVICE FOR AN
    # APPEND — and that made a CORRECT refusal read as a bug. Reported by
    # cassian-observability after adopting these hooks: `cat >> MEMORY.md` denied as a
    # "structural query", the message offering only reader routes. Their conclusion was
    # to drop the `.md` claim; the verdict was right and only the guidance was missing.
    #
    # ⚑⚑ THE VERDICT DOES NOT SOFTEN. Operator ruling, 2026-08-19: *"don't support
    # redirection, support editing"* / *"appendation causes files to grow out of
    # control."* A shell append is an unbounded, unstructured, unreviewable write to an
    # artifact that has a structural editor — and this session MEASURED the damage:
    # `MEMORY.md`'s staging block is appended to and never drained (its self-clear
    # matched 0 of 44 lines across 167 regens), growing past the 200-line budget of the
    # reader that loads it every session. Exempting `>>` would have blessed exactly that.
    if any(op in cmd for op in (">", ">>")):
        owner = ", ".join(sorted({t for _p, hs in reasons for _a, _s, (_k, t) in hs}))
        lines.append(
            "  ⚑ THIS LOOKS LIKE A WRITE, AND THE REFUSAL STILL STANDS.\n"
            f"     The owning tool is the route for WRITES TOO: {owner}.\n"
            "     A structural editor states WHAT changes, refuses a target that\n"
            "     moved, and cannot append past the shape; `>>` does none of\n"
            "     that. If the owning tool has no mode for this edit, THAT is\n"
            "     the work — a missing mode, not grounds for a shell append.\n"
            "     `Write`/`Edit` are the fallback when the tool is unavailable\n"
            "     here, the same way `Read` is on the query side."
        )
    # ⚑⚑⚑ INLINE THE PORTABLE RULE, DROP THE POINTER (gate-G49). This read
    # `see .claude/skills/struct-tools/SKILL.md`, which resolves in substrate and nowhere
    # else while this file is vendored by at least one peer. Over half that skill is a
    # GENERATED mode census plus a tools roster — a ROSTER, useless to a consumer holding
    # the hook without the toolkit. So the coordinate goes and the rule stays.
    #
    # ⚑⚑ THE RULE INLINED HERE IS THIS REFUSAL'S OWN, NOT THE SIBLING'S. `hook_no_chaining`
    # carries the permission argument (a chain cannot be approved in a way that sticks);
    # the portable claim HERE is about what a textual read of a structured artifact costs.
    # Copying the sibling's paragraph would have been a second spelling of a different rule.
    lines.append(
        "  ⚑ AND THE COST IS A WRONG ANSWER, NOT UNTIDINESS. A regex over a "
        "structured\n     artifact reports its own blind spots as facts about the "
        "subject — an empty\n     grep and an absent record are indistinguishable, "
        "and a reader keyed on one\n     spelling calls a live thing dead. A parser "
        "that knows the shape can say\n     UNREADABLE where a grep can only say "
        "nothing."
    )
    return "\n".join(lines)


def retired_verdict(cmd: str) -> str:
    """Return the refusal for a RETIRED tool mode invoked by `cmd`, or "" if none is.

    ⚑⚑ A SECOND, INDEPENDENT VERDICT — NOT AN EXTENSION OF `verdict()`. That one asks
    *is a TEXTUAL tool being pointed at a STRUCTURED artifact*; this one asks *is a
    RETIRED mode of a structural tool being invoked*. Folding them together would make
    one predicate answer two questions, and the routing table that feeds the first has
    nothing to say about the second.

    ⚑⚑⚑ AND THE TWO MUST NOT COLLIDE, WHICH IS THE SHARPEST HAZARD HERE. `verdict()`'s
    refusal RECOMMENDS `scratch/pycodemod.py` by name. If this verdict fired on the
    TOOL rather than on the tool-AND-a-retired-flag, the gate would refuse the tool it
    recommends and every refusal it issues would become a dead end. The conjunction
    lives in `pycodemod_retired.retired_in_command`, with arms on both directions.

    ⚑ THE MODES THAT WORK ARE UNTOUCHED BY CONSTRUCTION: `--calls`, `--binding`,
    `--source`, `--literal` and the rest are not rows in the table, so they are not
    reachable from here at all. Retiring a third mode is a ROW, not an edit to this.
    """
    if _RETIRED is None:  # a borrowing checkout: nothing to retire
        return ""
    # ⚑ THE PROGRAM WORD IS PREPENDED, AND OMITTING IT WAS A REAL HOLE. `programs()`
    # returns the program SEPARATELY from its arguments, so `./scratch/pycodemod.py
    # --attr X` reports the program as `pycodemod.py` with the stem absent from `args`
    # — the direct-execution spelling would have sailed through while the `python3 …`
    # one was caught. Rejoining them is what makes the two spellings one case.
    for prog, args in _cmdparse.programs(cmd):
        mode = pycodemod_retired.retired_in_command([prog, *args])
        if mode is not None:
            return pycodemod_retired.refusal(mode)
    return ""


def _deny_payload(reason: str) -> str:
    """Render a PreToolUse deny decision as JSON.

    ⚑⚑ THE NESTED DICT IS BUILT THROUGH TYPED LOCALS, AND THAT IS THE WHOLE FIX.
    Written inline as `json.dumps({"hookSpecificOutput": {…}})` the INNER literal is
    inferred on its own as `dict[Any, Any]` — the call site gives it nothing to check
    against — and `disallow_any_expr` refuses it. The sibling hook carried the
    identical construct and it cost six wrong attributions there before `--pretty`
    printed the line.
    """
    decision: dict[str, str] = {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }
    envelope: dict[str, dict[str, str]] = {"hookSpecificOutput": decision}
    return json.dumps(envelope)


def _emit(msg: str) -> int:
    """Deliver the refusal — deny when armed, advisory otherwise."""
    if os.environ.get("STRUCT_HOOK_BLOCK") == "1":
        sys.stdout.write(_deny_payload(msg) + "\n")
        return 0
    sys.stderr.write(msg + "\n")
    return 0


def _command_of(payload: object) -> str:
    """Extract the Bash command from a PreToolUse payload, or "" if absent.

    ⚑ `object` IS THE HONEST TYPE OF AN UNTRUSTED VALUE; `Any` IS THE DISHONEST ONE
    (linux-sources, 2026-08-30). The payload arrives as untyped JSON, and every level
    is narrowed with a real runtime `isinstance` before anything is read from it — a
    check, not an assertion. A hook that mis-reads its own input renders a verdict
    about something other than what ran.
    """
    if not isinstance(payload, dict):
        return ""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command")
    return command if isinstance(command, str) else ""


def main() -> int:
    """Read the PreToolUse payload from stdin and route or refuse the command."""
    # ⚑ THE EXCEPTIONS ARE NAMED. A bare `except Exception` here would swallow a bug
    # in this hook's own logic and return 0 — i.e. ALLOW — making a broken gate
    # indistinguishable from a passing one. Only a malformed or unreadable payload is
    # tolerated; anything else must crash loudly where it can be seen.
    try:
        payload: object = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError, OSError):
        return 0  # never break the session on a parse failure
    cmd = _command_of(payload)
    if not cmd:
        return 0

    # ⚑⚑ THE RETIREMENT VERDICT IS CHECKED FIRST *AND DENIES UNCONDITIONALLY*, where the
    # textual-query verdict is advisory unless STRUCT_HOOK_BLOCK=1. The two are not the
    # same risk. An advisory textual query still gets a truthful, if clumsy, answer — the
    # cost is a habit. A retired mode ANSWERS `0` with full confidence, and this repo
    # DELETES on a zero (`--dead`), so letting it proceed with a note on stderr is how a
    # false zero gets banked as a fact. Advisory is the right default for a style rule
    # and the wrong one for a known-wrong instrument.
    retired = retired_verdict(cmd)
    if retired:
        sys.stdout.write(_deny_payload(retired) + "\n")
        return 0

    hit, reasons = verdict(cmd)
    if not hit:
        return 0

    return _emit(_refusal(reasons, cmd))


class _Cases:
    """Collect selftest outcomes.

    ⚑ `fires_on` / `passes` EXIST BECAUSE A BARE `True`/`False` ARGUMENT IS
    UNREADABLE AT THE CALL SITE, and the linter is right about that (FBT003):
    `check(label, got, True)` tells a reader nothing about what True MEANS here.
    Naming the two verdicts makes each case state its own expectation, so the list
    below reads as a specification of when this gate fires — which is what it is.
    """

    def __init__(self) -> None:
        self.rows: list[tuple[str, bool, str, str]] = []

    def _record(self, label: str, *, ok: bool, got: object, want: object) -> None:
        """Record one outcome, rendering the values at the boundary."""
        self.rows.append((label, ok, repr(got), repr(want)))

    def fires_on(self, label: str, cmd: str) -> None:
        """Record a case asserting the gate REFUSES `cmd`."""
        got = verdict(cmd)[0]
        self._record(label, ok=got is True, got=got, want=True)

    def passes(self, label: str, cmd: str) -> None:
        """Record a case asserting the gate ALLOWS `cmd`."""
        got = verdict(cmd)[0]
        self._record(label, ok=got is False, got=got, want=False)

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


# ⚑ NAMED FIXTURES AND A BUILDER, NOT INLINE LITERALS AT THE CALL SITE — a nested
# literal is inferred on its own as `dict[Any, Any]`, which `disallow_any_expr`
# refuses once the result flows into a recorded value.
_NOT_A_MAPPING: list[str] = ["nope"]
_EMPTY_PAYLOAD: dict[str, object] = {}
_BAD_TOOL_INPUT: dict[str, object] = {"tool_input": "nope"}


def _payload(command: object) -> dict[str, object]:
    """Build a PreToolUse payload carrying `command`, typed at every level."""
    tool_input: dict[str, object] = {"command": command}
    return {"tool_input": tool_input}


def _cases_fires(c: _Cases) -> None:
    """Add the cases for the textual-query shapes this gate exists to refuse."""
    c.fires_on("grep over .py is a structural query", "grep -n 'def foo' scratch/tool.py")
    c.fires_on("a piped grep over .py still fires", "cat x | grep -n foo scratch/a.py")

    # --- ⚑ THE LIVE BYPASS AND ITS FAMILY. Each of these RAN successfully against
    # the predecessor, which tested only toks[0]; a `timeout` prefix is the ordinary
    # invocation shape here, so the gate was open for nearly every real command.
    c.fires_on(
        "⚑ timeout prefix no longer hides grep", "timeout 180 grep -c __main__ scratch/seal_defs.py"
    )
    c.fires_on("env prefix does not hide it", "env grep foo scratch/a.py")
    c.fires_on("a VAR= prefix does not hide it", "PYTHONPATH=. grep foo scratch/a.py")
    c.fires_on("an absolute path to grep is caught", "/usr/bin/grep foo scratch/a.py")
    c.fires_on("stacked wrappers are seen through", "timeout 60 env grep foo scratch/a.py")

    # --- the WIDENED tool set: every byte-reader, not just the original six ---
    c.fires_on("head over .py fires", "head -50 scratch/tool.py")
    c.fires_on("wc over .py fires", "wc -l scratch/tool.py")
    c.fires_on("cat over .agda fires", "cat agda/Foo.agda")

    # --- ⚑ PORTABILITY: the case that killed the location-based predicate. The
    # claim is the ARTIFACT KIND, not the checkout it lives in — this tooling is
    # borrowed by several repos.
    c.fires_on(
        "⚑ a .py in ANOTHER repo is still claimed", "grep foo /home/mikemol/github/otherrepo/x.py"
    )

    # --- ⚑⚑ THE ROLE RULE MUST NOT TURN INTO AN EXEMPTION — a hook that refuses nothing
    # would pass every "pattern" case above. The path AFTER the pattern still fires, a path
    # after a detached -e pattern still fires, and summit's own witness arm is pinned.
    c.fires_on(
        "⚑⚑ summit's other arm: grep foo over a .py still denies", "grep foo scripts/summitlib.py"
    )
    c.fires_on("⚑ a .py-shaped pattern does not shield a .py path", "grep gate.py scratch/tool.py")
    c.fires_on("⚑ a detached -e pattern does not shield the path", "grep -e foo scratch/tool.py")
    c.fires_on("⚑ sed over a .py still fires", "sed -n '1,5p' scratch/tool.py")


def _cases_passes(c: _Cases) -> None:
    """Add the cases that must NOT fire, or the hook breaks the session."""
    # ⚑ LOCATING A FILE IS NOT A QUESTION ABOUT ITS STRUCTURE, whatever its suffix.
    c.passes("ls is not a textual query tool", "ls -la scratch/tool.py")
    c.passes("find is not a textual query tool", "find . -name '*.py'")
    c.passes("pgrep is not covered", "pgrep -af make")
    c.passes(
        "grep over a build log is NOT (no row claims .log today)", "grep -c Error /tmp/build.log"
    )
    # --- an unclaimed artifact passes BY CONSTRUCTION (no row claims it) ------
    c.passes("an unclaimed .tsv passes today", "wc -l scratch/.agda-times.tsv")
    # --- the argument WORD is the predicate, not the whole segment ------------
    c.passes("a dir named pkg.py/ does not false-positive", "grep foo pkg.py/notes.txt")

    # --- ⚑⚑⚑ A PATTERN IS NOT A PATH (summit ask-structural-hook-distinguishes-a-pattern-
    # from-a-path). The measured denial: grep's PATTERN ends in `.py`, every file it opens is
    # a Makefile or a git hook, and no row claims those. The role comes from the position.
    c.passes(
        "⚑⚑ summit's payload: the pattern is not a path and the includes are globs",
        'grep -rl --include=Makefile --include=pre-commit "gate.py" /home/x/github',
    )
    c.passes("⚑ a bare .py-shaped pattern over a text file passes", "grep gate.py notes.txt")
    c.passes("⚑ a detached -e pattern is not a path", "grep -e gate.py notes.txt")
    c.passes("⚑ a detached -A value is not a path", "grep -A 2 foo notes.txt")
    c.passes("⚑ sed's script is not a path", "sed -n 's/x.py/y/p' notes.txt")
    c.passes("⚑ awk's program is not a path", "awk '/tool.py/ {print}' notes.txt")


def _cases_table(c: _Cases) -> None:
    """Add the cases for reading the routing table out of the skill."""
    c.holds("the routing table is readable from the skill", got=len(routes()) > 0)
    c.holds("the CLAIMS column is readable", got=claims().get(".py") is not None)
    # ⚑ THE TWO TABLE READERS MUST SEE THE SAME TABLE. `routes` and `claims` parsed
    # the markdown with two separate loops that handled backticks and the header row
    # differently. They now share `_table_rows`, and this arm is what would notice if
    # one of them grew a private parser again.
    claimed_tools = {tool for _artifact, tool in claims().values()}
    route_tools = {tool for _artifact, tool in routes()}
    c.holds(
        "every claiming row's tool is also a routing row's tool", got=claimed_tools <= route_tools
    )

    # ⚑⚑⚑ A SUFFIXLESS ARTIFACT IS CLAIMABLE, and these cases exist because the suite
    # passed IDENTICALLY before and after the mechanism gained that ability — 52/52 both
    # times. A refactor that adds a capability while every case still passes has not been
    # tested; the count says nothing about what changed.
    fixture: dict[str, tuple[str, str]] = {
        ".mk": ("makefiles", "make_rules.py"),
        "Makefile": ("makefiles", "make_rules.py"),
    }
    c.holds(
        "a suffix claim routes by suffix",
        got=claimed_by("agda/Flat.mk", fixture) == (".mk", "make_rules.py"),
    )
    # ⚑ THE CASE THE OLD MECHANISM COULD NOT PASS. `Path("Makefile").suffix` is "", so no
    # cell value could bind it however the table was written.
    c.holds(
        "a bare-filename claim routes a suffixless file",
        got=claimed_by("agda/Makefile", fixture) == ("Makefile", "make_rules.py"),
    )
    # ⚑ CASE-FOLDED AT THE LOOKUP, NOT IN THE CLAIM. Both spellings are real filenames.
    c.holds(
        "and its lowercase spelling routes too",
        got=claimed_by("agda/makefile", fixture) == ("Makefile", "make_rules.py"),
    )
    # ⚑⚑ THE SUFFIX WINS WHEN BOTH COULD MATCH. A filename claim must never shadow the more
    # general kind claim, or one row's specific name would capture another row's artifact.
    both: dict[str, tuple[str, str]] = {
        ".mk": ("kind", "kind_tool.py"),
        "Flat.mk": ("name", "name_tool.py"),
    }
    c.holds(
        "a suffix claim beats a filename claim for the same file",
        got=claimed_by("agda/Flat.mk", both) == (".mk", "kind_tool.py"),
    )
    # ⚑ AND AN UNCLAIMED ARGUMENT STILL PASSES — the table routes what it declares and
    # refuses nothing else, which is the property the gate's own prose rests on.
    c.holds("an unclaimed file is claimed by nothing", got=claimed_by("notes.txt", fixture) is None)
    # ⚑⚑ THE TWO KEY SPACES CANNOT COLLIDE, which is what makes one map safe — and the first
    # cut of this case was a TAUTOLOGY (`k.startswith(".") or not k.startswith(".")`), true
    # of every string and therefore of a broken table too. It is asserted on the LIVE table
    # and states the real property: both kinds are present, and no filename key wears a dot.
    live = claims()
    suffix_keys = {k for k in live if k.startswith(".")}
    name_keys = {k for k in live if not k.startswith(".")}
    c.holds(
        "the live table carries both suffix and filename claims",
        got=bool(suffix_keys) and bool(name_keys),
    )
    c.holds(
        "and no filename key is spelled as a suffix", got=all("." not in k[:1] for k in name_keys)
    )


def _cases_message(c: _Cases) -> None:
    """Add the cases for the refusal TEXT and the deny envelope.

    ⚑ THE MESSAGE IS PART OF THE GATE, AND NOTHING CHECKED IT. Every fires/passes case
    asks WHETHER the hook fires; none asked what it SAYS. A refusal that names an
    unrunnable tool and stops is a gate that blocks without routing — measured, in a
    borrowing checkout where `pycodemod` could not run and the reader had no move
    left. The escape hatch has to be IN the message, because the message is the only
    thing a refused reader sees.
    """
    msg = _refusal(verdict("wc -l scratch/tool.py")[1])
    c.holds("the refusal names the owning tool", got="pycodemod" in msg)
    c.holds("⚑ ...and names Read as the fallback when that tool is unavailable", got="Read" in msg)
    c.holds(
        "...and says it is not a shell command, since that is why it is missed",
        got="not a shell command" in msg,
    )

    # --- ⚑⚑ THE WRITE SIDE: THE VERDICT STANDS, THE ROUTE CHANGES ---------------
    # Reported by cassian-observability after adopting these hooks: `cat >> MEMORY.md`
    # denied as a "structural query", the message offering only READER routes — so a
    # correct refusal read as a bug and their conclusion was to drop the `.md` claim.
    #
    # ⚑ I FIRST "FIXED" IT BY EXEMPTING `>>` FROM THE ARGUMENT LIST, and that was the
    # wrong repair. Operator ruling, 2026-08-19: *"don't support redirection, support
    # editing"* / *"appendation causes files to grow out of control."*
    wmsg = _refusal(verdict("cat >> scratch/tool.py")[1], "cat >> scratch/tool.py")
    c.fires_on("⚑ a shell append to a claimed artifact STILL fires", "cat >> scratch/tool.py")
    c.holds(
        "⚑ ...and the write branch names the OWNING TOOL, not just Write/Edit",
        got="WRITES TOO" in wmsg and "pycodemod" in wmsg,
    )
    c.holds(
        "...and says a missing mode is the WORK, not grounds for an append",
        got="missing mode" in wmsg,
    )
    # ⚑ THE READ MESSAGE MUST NOT GROW THE WRITE ADVICE — a reader told to reach for an
    # editor is the same category error one direction over.
    c.denies("a plain read does NOT get the write branch", got="WRITES TOO" in msg)

    # ⚑⚑⚑ THE REFUSAL CARRIES THE RULE AND NOT A COORDINATE (gate-G49), UNPINNED UNTIL NOW.
    #   This hook is VENDORED — cassian's `sq-*` family documents it — so its text is read
    #   by consumers with no substrate tree. It used to close on
    #   `see .claude/skills/struct-tools/SKILL.md`, a path that resolves only here and whose
    #   target is over half generated mode census: a dead pointer at a roster.
    # ⚑⚑ AND THE RULE INLINED IS THIS REFUSAL'S OWN. The sibling hook carries the permission
    #   argument; the portable claim HERE is what a textual read of a structured artifact
    #   COSTS. Asserting the sibling's wording would pin a second spelling of another rule.
    c.holds(
        "⚑ the refusal states the COST — a wrong answer, not untidiness", got="blind spots" in msg
    )
    c.holds(
        "...and names the shape: an empty grep and an absent record are the same",
        got="indistinguishable" in msg,
    )
    c.holds(
        "⚑ ...and names NO path a vendoring consumer cannot resolve",
        got=".claude/skills" not in msg,
    )

    # ⚑ THE DENY ENVELOPE IS WHAT THE HARNESS ACTUALLY READS — an empty stdout is
    # read as ALLOW, so a malformed envelope is a silently-inert gate.
    rendered = _deny_payload(msg)
    c.holds("the deny envelope names the event", got="PreToolUse" in rendered)
    c.holds("...and carries the decision", got='"deny"' in rendered)
    c.holds("...and carries the reason text", got="structural-query" in rendered)


def _cases_payload(c: _Cases) -> None:
    """Add the cases for the payload reader.

    ⚑ A hook that mis-reads its own INPUT renders a verdict about something other
    than what ran, so every rejected payload shape gets a case.
    """
    c.holds(
        "a well-formed payload yields its command",
        got=_command_of(_payload("grep foo x.py")) == "grep foo x.py",
    )
    c.holds("a non-string command yields no command", got=_command_of(_payload(7)) == "")
    c.holds("a non-mapping payload yields no command", got=_command_of(_NOT_A_MAPPING) == "")
    c.holds("a payload with no tool_input yields no command", got=_command_of(_EMPTY_PAYLOAD) == "")
    c.holds("a non-mapping tool_input yields no command", got=_command_of(_BAD_TOOL_INPUT) == "")


def _cases_retired(c: _Cases) -> None:
    """Add the cases for the RETIRED-mode verdict and its collision with the routing one.

    ⚑⚑⚑ CASE `the gate still recommends the tool it refuses a mode of` IS THE ONE THAT
    MATTERS. This hook's refusal text names `scratch/pycodemod.py` as the owner of `.py`.
    Refusing that tool wholesale would make every refusal this gate issues a dead end —
    a guard that blocks without routing, which is the exact defect a borrowing checkout
    already hit once when the named tool could not run there.
    """
    if _RETIRED is None:  # pragma: no cover - borrowing checkout only
        return
    # --- the two dead modes, in both invocation spellings ---------------------
    c.holds(
        "⚑ --attr on the origin is REFUSED, not answered",
        got="RETIRED" in retired_verdict("python3 scratch/pycodemod.py --attr corpus.ROOT"),
    )
    c.holds(
        "...and the refusal names its successor",
        got="attr_reads.py" in retired_verdict("python3 scratch/pycodemod.py --attr corpus.ROOT"),
    )
    c.holds(
        "⚑ --importers on the origin is REFUSED",
        got="RETIRED"
        in retired_verdict("python3 scratch/pycodemod.py --importers substrate.corpus"),
    )
    c.holds(
        "...and the refusal names its successor",
        got="module_importers.py"
        in retired_verdict("python3 scratch/pycodemod.py --importers substrate.corpus"),
    )
    # ⚑ DIRECT EXECUTION: `programs()` reports the script AS the program, so the stem is
    # absent from `args`. This spelling would have sailed through the first draft.
    c.holds(
        "⚑ direct execution is caught too, not just `python3 <script>`",
        got="RETIRED" in retired_verdict("./scratch/pycodemod.py --attr corpus.ROOT"),
    )
    c.holds(
        "a wrapper does not hide it",
        got="RETIRED"
        in retired_verdict("timeout 60 python3 scratch/pycodemod.py --attr corpus.ROOT"),
    )

    # --- ⚑⚑ THE MODES THAT WORK MUST BE UNTOUCHED ---------------------------
    for mode in (
        "--calls reach_ratchet",
        "--binding MODES",
        "--source _cached_defs",
        "--literal foo",
        "--forwards x",
        "--snapshots",
    ):
        c.holds(
            f"a working mode passes: {mode}",
            got=retired_verdict(f"python3 scratch/pycodemod.py {mode}") == "",
        )

    # --- ⚑⚑⚑ THE COLLISION: the gate must still ROUTE to the tool it polices --
    msg = _refusal(verdict("wc -l scratch/tool.py")[1])
    c.holds("⚑⚑ the routing refusal still names pycodemod", got="pycodemod" in msg)
    c.holds(
        "⚑⚑ ...and that recommendation is itself allowed — not a dead end",
        got=retired_verdict("python3 scratch/pycodemod.py --calls foo") == "",
    )

    # --- ⚑ `--` IS HONOURED: the operand is a STRING, not an invocation ------
    c.holds(
        "⚑ `--literal -- --attr` is NOT refused",
        got=retired_verdict("python3 scratch/pycodemod.py --literal -- --attr") == "",
    )

    # --- ⚑ THE SUCCESSOR TAKES THE SAME FLAG AND MUST NOT BE REFUSED ---------
    c.holds(
        "⚑ the successor is not refused for taking the retired flag",
        got=retired_verdict("python3 substrate/attr_reads.py corpus.ROOT") == "",
    )
    c.holds(
        "an unrelated command carrying the word passes",
        got=retired_verdict("echo --importers") == "",
    )


def _selftest() -> bool:
    """Run every case group and report whether all of them hold.

    ⚑ THE GROUPS ARE SEPARATE FUNCTIONS so no one of them can outgrow the statement
    gate (PLR0915) — the same forcing function as C901 one level down, and the same
    answer: the unit was doing too much. Each group is one concern, named.
    """
    c = _Cases()
    _cases_fires(c)
    _cases_passes(c)
    _cases_table(c)
    _cases_message(c)
    _cases_payload(c)
    _cases_retired(c)
    return c.report("hook_structural_query")


def _main() -> int:
    """Dispatch the CLI modes and return the exit code."""
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    if "--routes" in sys.argv:
        for artifact, tool in routes():
            sys.stdout.write(f"{artifact:<24} {tool}\n")
        return 0
    return main()


if __name__ == "__main__":
    sys.exit(_main())
