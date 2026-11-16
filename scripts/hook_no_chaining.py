#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""PreToolUse(Bash) — refuse a COMPOSED command where ONE tool invocation belongs.

⚑ THE SIBLING OF `hook_structural_query`, AND THE SAME FINDING ONE LEVEL OVER.
That hook refuses a TEXTUAL question about a STRUCTURED artifact. This one
refuses the COMPOSITION — `&&`, `;`, `|`, `for` — because CLAUDE.md's standing
rule names both shapes and only one had a layer that could say no:

    "No complex command lines, no greps, no seds, no judgements not in code."
    "Needing more than ONE tooling command, or manipulating a tool's output
     (`| tail`, a `python3 -c` wrapper, a shell `case` over an error string),
     means the judgement is happening in the turn instead of in a program."

A pipeline IS the judgement-not-in-code shape: `tool | tail -5` decides in the
turn what the tool should have had a `--top` mode for; `A && B` sequences two
questions a single mode should answer; `for f in ...; do` is a loop the tool
should own. Each evaporates when the turn ends and the next reader re-derives
it differently. Refusing the composition is what turns "add the mode" from a
suggestion into the only available move.

⚑ PARSE, DO NOT SUBSTRING-MATCH — the false-positive surface IS the design.
`grep 'a|b'`, `awk '{print;n++}'`, `find -exec ... \;` and `format_for_each.py`
all CONTAIN the banned characters and none of them compose anything. A token ban
would fire on all four, and a guard whose first act is to break a working session
trains its owner to disable it (the lesson `hook_structural_query` recorded from
`prune_imports` shipping write-by-default). So the SHARED tokenizer
(`hook_cmdparse.tokenize`, POSIX shlex with `punctuation_chars=True`) does the
splitting: a quoted `|` stays inside its token — whether the quote opens at the
word's start or mid-word — a real operator becomes one, and `for` counts only as
a bare leading word.

⚑ ADVISORY BY DEFAULT, matching its sibling. `NOCHAIN_HOOK_BLOCK=1` (or the
shared `STRUCT_HOOK_BLOCK=1`) makes it refuse. The block rate earns its way in
after the false-positive rate is measured, not before.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

# ⚑ THE SHARED TOKENIZER, NOW ACTUALLY IMPORTED. `hook_cmdparse` was lifted so two
# hooks would agree on what "a new command begins" means, and its docstring said so
# — but only `hook_structural_query` ever imported it (measured: 1 binding in 88
# files). A module that exists to be shared, with one consumer, is one body plus one
# copy; the copy is how `|&` went uncovered here for as long as it did.
# ⚑⚑ THE REPO ROOT IS SELF-SUPPLIED, AND THIS TWO-LINE PRELUDE IS A BUG FIX WITH A
# FOUR-REPO BLAST RADIUS (cassian-observability, 2026-08-28). The import below became
# `from scripts import …` so mypy could follow it — a `sys.path.insert` is EXECUTED,
# not declared, and no checker can see it. That is right for the type checker and it
# introduced a PRECONDITION this file did not state: the absolute import resolves only
# when the repo ROOT is importable.
#
# ⚑ THE HARNESS SUPPLIES THAT AND A FIRE-PROBE DOES NOT. `python3 <abs-path-to-hook>`
# puts the SCRIPT's directory on `sys.path[0]`, never the repo root — so adopters who
# test their guards BY MAKING THEM FIRE got `ModuleNotFoundError: No module named
# 'scripts'` at import, no output, and a false ARMED-BUT-INERT red. cassian measured
# 13/13 → 11/13. Five repos symlink this file; the break reached all of them at once,
# and it reached them through the ONE testing discipline that is correct — a probe
# that runs the hook rather than reading its config.
#
# ⚑⚑⚑ SO THE PRECONDITION IS SATISFIED HERE RATHER THAN DOCUMENTED FOR ADOPTERS TO
# HONOUR. Asking each consumer to set `PYTHONPATH` is asking five repos to remember an
# invariant this file could enforce in two lines — and *a vendored hook transmits its
# mechanism, not its preconditions* (substrate → gcalculus, earlier today, now landing
# on its author). The insert is a no-op under the harness and load-bearing under a
# bare-path invocation; mypy still reads the declaration below and follows it.
# ⚑⚑⚑ `absolute()`, NEVER `resolve()`. `resolve()` FOLLOWS SYMLINKS, and this hook is
# symlinked into five other checkouts — a resolved `__file__` lands in SUBSTRATE, so
# the adopting repo's root never reaches `sys.path` and any repo-relative data the
# hook reads comes from the wrong tree. The original spelling was `os.path.abspath`,
# whose pathlib counterpart is `absolute()`, not `resolve()`; the translation looks
# mechanical and is not. Caught in the sibling by summit-1c's `--only routes` slice,
# which asserts that a symlinked hook still reads THIS repo's data — a property no
# selftest in substrate can check, because substrate is the tree with no symlink.
_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from scripts import hook_cmdparse  # noqa: E402  the SHARED tokenizer

# The composition operators — each is a place a judgement left the program.
#
# ⚑⚑ THIS SET WAS WRONG, AND THE COMMENT THAT MADE IT LOOK RIGHT WAS THE DEFECT.
# It used to read: "`|&` and `||` reduce to these under shlex's punctuation
# splitting". That is HALF true and the wrong half is load-bearing. `||` needs no
# reduction (it is listed). `|&` DOES NOT REDUCE — shlex with
# `punctuation_chars=True` emits it as ONE token, under `whitespace_split` too.
# Run `hook_cmdparse.py --tokens "make |& grep foo x.py"` to see it.
#
# So `make |& grep foo x.py` read as a BARE COMMAND and was allowed, while `make |
# grep foo` was denied. Measured end-to-end by a peer session (summit, ref
# linux-sources) driving this hook with a synthetic event and NOCHAIN_HOOK_BLOCK=1;
# its `|`/`;` controls denied and its bare-command control passed, so the probe was
# sound. Reproduced here before the fix.
#
# ⚑ AND THE STALE COMMENT SURVIVED A RULING. Asked to adjudicate the divergence, I
# read this comment, believed it, and ruled the gap DELIBERATE — then checked it
# against `hook_cmdparse --explain`, which agreed with me FOR THE WRONG REASON
# (that module lists `|&`, so of course it segments). A green `--selftest` agreed
# too: it proved the arms the hook had, never the arm it lacked. Three
# confirmations, all downstream of the same unverified sentence.
#
# ⚑ SO THE COVERAGE IS NOW DERIVED FROM THE SHARED SET, NOT RESTATED BESIDE IT.
# `hook_cmdparse.OPERATORS` is the authority — that module exists BECAUSE two hooks
# needed one tokenizer and only one had it. Keeping a hand-written literal here is
# the same two-bodies shape one layer down; a token added there is now covered here
# by construction. The explanations stay local (they are this hook's voice); only
# membership is inherited, and an operator with no explanation gets a generic one
# rather than silently going uncovered.
_REASONS = {
    "|": "a pipe — the tool should have the mode that produces this directly",
    "&&": "a sequence — two questions that want one mode, or two calls",
    "||": "a fallback — a shell `case` over an error string is judgement-in-turn",
    ";": "a sequence — run the calls separately, or add the mode",
    "&": "a background spawn — use run_in_background, not shell control flow",
    "|&": "a pipe (stdout+stderr) — the tool should have the mode that produces this",
}
# ⚑⚑ THE ANNOTATION BREAKS AN INFERENCE CYCLE THE PATH MUTATION WAS HIDING, and the
# cycle is real rather than cosmetic: this module imports `hook_cmdparse`, and
# `hook_cmdparse`'s `--tokens` branch resolves back here. mypy could not follow
# either edge while both were `sys.path.insert` + bare import, so it never saw the
# cycle; once the imports became declarations it reported
# `Cannot determine type of "OPERATORS"` — a genuine finding that existed all along
# and was invisible because the import was executed rather than declared.
OPERATORS: dict[str, str] = {
    op: _REASONS.get(op, "a shell composition — one tool call, or add the mode")
    for op in hook_cmdparse.OPERATORS
}

# ⚑ THE INLINE INTERPRETER IS THE SAME DEFECT WITHOUT A SHELL OPERATOR.
# `python3 -c "..."` composes nothing bash can see, so the operator scan above
# is silent on it — but CLAUDE.md names "a `python3 -c` wrapper" in the SAME
# breath as `| tail`, and for the same reason: the program is written in the
# turn, run once, and discarded. The next reader re-derives it differently, or
# not at all. A throwaway script is a tool that was never added.
INTERPRETERS = (
    "python",
    "python3",
    "python3.14",
    "uv",
    "node",
    "ruby",
    "perl",
    "bash",
    "sh",
    "zsh",
)

# The flags that mean "the program is on this command line / on stdin" rather
# than "run this committed file".
INLINE_FLAGS = {
    "-c": "an inline script — this program dies with the turn; put it in a tool",
    "-e": "an inline script — this program dies with the turn; put it in a tool",
}

# Shell control flow. A loop belongs to the tool, not to the turn.
KEYWORDS = {
    "for": "a loop — the tool should take the whole set and iterate internally",
    "while": "a loop — same: the iteration belongs in a program",
    "until": "a loop — same: the iteration belongs in a program",
    "case": "a dispatch over strings — the classic judgement-not-in-code shape",
    "if": "a branch — the decision belongs in the tool that has the data",
}

# ⚑⚑ `cd` IS FLAGGED IN ITS OWN RIGHT, AND THE REASON IS THE OBSERVED CASE MIX.
# Operator, 2026-08-30: *"the most common use of `&&` I see caught is `cd (dir) &&
# cmd`, and the correct tool to use instead is `env`."* The `&&` alone already fired,
# so the VERDICT was never wrong — but the message said only "a sequence: two
# questions that want one mode", which is true and useless here. A refused caller
# acts on the text, and the text did not name the one-call form that replaces it.
#
# ⚑ AND `cd` IS WORSE THAN AN ORDINARY SEQUENCE, WHICH IS WHY IT GETS ITS OWN ENTRY:
# it mutates the shell's working directory for everything after it in the line, so
# the second command's meaning depends on state established by the first. `env -C
# <dir> <cmd>` scopes that to the ONE invocation that needs it — the directory
# becomes an argument to the call rather than a mutation the rest of the line
# inherits. Same shape as every other rule here: make the state an INPUT, not an
# ambient effect.
DIRECTORY_CHANGE = {
    "cd": (
        "a directory change — it mutates the shell state every later command "
        "inherits.\n       Use `env -C <dir> <cmd>` (or the tool's own path "
        "argument) so the\n       directory is an INPUT to the one call that "
        "needs it, not an ambient effect."
    ),
}

_STDIN_SCRIPT = "a stdin script (heredoc) — same as `-c`: it dies with the turn; put it in a tool"
_HEREDOC_SCRIPT = "a heredoc script — same as `-c`: written in the turn, run once, discarded"

_HEREDOC_OPEN = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

# A finding: the token that composed, and why that is judgement-in-the-turn.
Finding = tuple[str, str]


def _strip_heredoc_bodies(cmd: str) -> str:
    """Remove heredoc BODIES, keeping the `<<TAG` redirection itself.

    A body is data being handed to a program — a commit message, a config, a
    SQL statement. Its `;` and `|` are characters in that data, not operators
    in this shell. The redirection stays so the heredoc-into-interpreter test
    (which is about the SHAPE of the call, not its content) still sees it.

    `<<-TAG` and quoted tags (`<<'EOF'`) are both handled; an unterminated
    heredoc drops the remainder, which is the conservative reading — an
    unterminated body cannot be shell either.
    """
    m = _HEREDOC_OPEN.search(cmd)
    if not m:
        return cmd
    head, tag = cmd[: m.end()], m.group(2)
    rest = cmd[m.end() :]
    # find the terminator on its own line (leading tabs allowed for <<-)
    for line_end in re.finditer(r"\n[\t ]*" + re.escape(tag) + r"[\t ]*(?=\n|$)", rest):
        return head + _strip_heredoc_bodies(rest[line_end.end() :])
    return head


def _mentions_interpreter(toks: list[str]) -> bool:
    """Report whether an interpreter is named anywhere in this command's tokens."""
    return any(Path(t).name in INTERPRETERS for t in toks)


def _tokenize(cmd: str) -> list[str]:
    """Split a command into shell words, or [] when it will not parse.

    ⚑ An unbalanced quote is bash's verdict, not ours: let it through and let bash
    report it. Never break the session on a parse failure.

    ⚑⚑⚑ A DELEGATOR TO `hook_cmdparse.tokenize`, WHICH THIS WAS A PRIVATE COPY OF. The copy
    ran shlex in non-POSIX mode, where a quote opening mid-word is not a quote, so
    `note="one; two"` split at the `;` and this hook refused six `bibstruct --add` calls in
    one session (summit ask-structural-hook-distinguishes-a-pattern-from-a-path). The shared
    tokenizer was repaired first and THIS hook kept refusing — the copy was the defect's
    second body, invisible to the fix. One authority, one delegator, as `_arg_after` already
    is for the argv reader.
    """
    return hook_cmdparse.tokenize(cmd)


def _classify(tok: str, *, found: list[Finding], pending_interp: bool) -> bool:
    """Record any inline-script tell on `tok`; return the new pending-interp state."""
    if Path(tok).name in INTERPRETERS:
        # ⚑ SEEN ANYWHERE, NOT ONLY IN COMMAND POSITION — `timeout 300 python3 -c`,
        # `uv run --with x python3 -c` and `PYTHONPATH=. python3 -c` all bury the
        # interpreter behind a wrapper or an env prefix. Requiring command position
        # would miss every one of them.
        return True
    if not pending_interp:
        return False
    if tok in INLINE_FLAGS:
        found.append((tok, INLINE_FLAGS[tok]))
        return False
    if tok == "-":
        # `python3 -` reads the program from stdin: a heredoc script.
        found.append(("-", _STDIN_SCRIPT))
        return False
    # ⚑ THE CASE THAT MUST PASS: a real path argument (anything that is not a flag)
    # means this is an invocation of a COMMITTED tool, which is exactly what the
    # rule wants — so it ends the flag scan for this command.
    return tok.startswith("-")


def _scan_tokens(toks: list[str]) -> list[Finding]:
    """Walk the token stream once, collecting every composition point.

    ⚑ SPLIT OUT OF `analyze` BECAUSE THE COMPLEXITY GATE FIRED (C901, 12 > 10), and
    that gate is the per-file rule one level down: a function too tangled to check is
    the same finding as a file too large to leave clean. The walk is one job — token
    classification — while the heredoc pre-strip and the post-scan are two others.
    """
    found: list[Finding] = []
    at_command_start = True
    pending_interp = False  # an interpreter is open; its flags are in scope
    for tok in toks:
        if tok in OPERATORS:
            found.append((tok, OPERATORS[tok]))
            at_command_start = True
            pending_interp = False
            continue
        # ⚑ COMMAND POSITION IS THE DISCRIMINATOR: `for` leading a command is
        # shell control flow; `for` as an argument (`grep -w for notes.md`) or
        # inside a filename (`format_for_each.py`) is not. The same test guards
        # `cd`: a path containing `cd`, or `cd` as an argument, is not a chdir.
        if at_command_start and tok in KEYWORDS:
            found.append((tok, KEYWORDS[tok]))
        if at_command_start and tok in DIRECTORY_CHANGE:
            found.append((tok, DIRECTORY_CHANGE[tok]))
        pending_interp = _classify(tok, found=found, pending_interp=pending_interp)
        at_command_start = False
    return found


def analyze(cmd: str) -> list[Finding]:
    """Return the composition points in one Bash command string.

    Parses rather than scans: a `|` inside quotes is data, a `|` between two
    words is an operator, and `for` is a keyword only in command position.
    """
    # ⚑ A HEREDOC BODY IS DATA, NOT COMPOSITION.  `git commit -F - <<EOF` carries
    # PROSE, and prose contains `;` and `|` — a commit message describing a shell
    # pipeline, a claim mentioning `a || b`. Scanned as shell, every one reads as
    # an operator, and the hook refuses a single tool call for the content of its
    # own argument. MEASURED: the first false positive after arming was a commit
    # message that merely NAMED the operators the hook had just caught.
    #
    # ⚑⚑ THE BEHAVIOUR IS WITNESSED; THE HISTORY IS NOT, AND THEY READ IDENTICALLY.
    # `_selftest()` pins the case this note justifies ("prose in a heredoc body is not
    # composition"), so the RULE is checkable and re-run on every commit. The word
    # MEASURED is a claim of a different kind — about an incident, in the past — and
    # nothing re-runs it. Two sessions spent four rounds arguing over whether that
    # incident happened, from this comment and its twin at the selftest, because a
    # checked claim and an unchecked one sit in the same ⚑ vocabulary and look alike.
    # Where a ⚑ asserts HISTORY rather than a rule, it carries no witness by
    # construction — read it as testimony, and do not let it settle an argument the
    # selftest could settle instead.
    #
    # The body is stripped BEFORE tokenising, and only the body: the `<<TAG`
    # redirection itself stays in the token stream, so the heredoc-into-
    # interpreter test below still fires. This narrows what counts as shell; it
    # does not exempt anything that was shell.
    toks = _tokenize(_strip_heredoc_bodies(cmd))
    found = _scan_tokens(toks)

    # ⚑ A HEREDOC INTO AN INTERPRETER YIELDS NO `-c` AND NO `-` TOKEN — the
    # redirection itself is the only tell, and shlex hands `<<` back as
    # punctuation. Test for the redirection rather than for a still-open
    # interpreter: a bare `python3` with no args is a REPL, not a script.
    if (
        any(t.startswith("<<") for t in toks)
        and _mentions_interpreter(toks)
        and not any(t in ("-", "-c", "-e") for t, _ in found)
    ):
        found.append(("<<", _HEREDOC_SCRIPT))

    # dedupe, preserving first-seen order
    seen: set[str] = set()
    out: list[Finding] = []
    for tok, why in found:
        if tok not in seen:
            seen.add(tok)
            out.append((tok, why))
    return out


def _command_of(payload: object) -> str:
    """Extract the Bash command from a PreToolUse payload, or "" if absent.

    ⚑⚑ `object` IS THE HONEST TYPE OF AN UNTRUSTED VALUE; `Any` IS THE DISHONEST ONE
    (linux-sources, 2026-08-30). The payload arrives as untyped JSON, and every level
    is narrowed with a real runtime `isinstance` before anything is read from it — a
    check, not an assertion. A `cast` into a declared shape would ASSERT what this
    VALIDATES, and this hook's own docstring argues that a guard which mis-reads its
    input renders a verdict about something other than what ran.
    """
    if not isinstance(payload, dict):
        return ""
    raw_input = payload.get("tool_input")
    if not isinstance(raw_input, dict):
        return ""
    command = raw_input.get("command")
    return command if isinstance(command, str) else ""


def _deny_payload(reason: str) -> str:
    """Render a PreToolUse deny decision as JSON.

    ⚑⚑ THE NESTED DICT IS BUILT THROUGH TYPED LOCALS, AND THAT IS THE WHOLE FIX.
    Written inline as `json.dumps({"hookSpecificOutput": {…}})` the INNER literal is
    inferred on its own as `dict[Any, Any]` — the call site gives it nothing to check
    against — and `disallow_any_expr` refuses it.

    ⚑⚑⚑ THIS CONSTRUCT SAT UNCHANGED WHILE I ATTRIBUTED ITS ERROR SIX TIMES TO
    SOMETHING ELSE: the payload reader (rewritten three ways), the selftest fixtures
    (twice), and `_Cases.rows`. Each rewrite moved the reported LINE NUMBER, because
    the file grew — and I read the movement as evidence I was getting closer. The
    error was reported against a tempfile that is deleted microseconds after the
    check, so the citation had no readable referent and I inferred the construct from
    the error TEXT instead of looking at it. Adding `--pretty` to the hook's own mypy
    invocation printed the line and the caret, and the answer was immediate.
    """
    decision: dict[str, str] = {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }
    envelope: dict[str, dict[str, str]] = {"hookSpecificOutput": decision}
    return json.dumps(envelope)


def _armed() -> bool:
    """Report whether this hook should DENY rather than advise.

    ⚑ AN EXPLICIT OFF MUST WIN OVER THE SHARED ON. `STRUCT_HOOK_BLOCK` arms both
    hooks as a convenience, but reading it as a bare `or` made `NOCHAIN_HOOK_BLOCK=0`
    unable to stand this hook down while its sibling blocks — the per-hook switch has
    to be able to override the shared one, or staging one hook ahead of the other is
    impossible.
    """
    own = os.environ.get("NOCHAIN_HOOK_BLOCK")
    if own is not None:
        return own == "1"
    return os.environ.get("STRUCT_HOOK_BLOCK") == "1"


def _refusal(found: list[Finding]) -> str:
    """Build the refusal TEXT, so the selftest can read what the hook says."""
    lines = ["no-chaining: this command COMPOSES where one tool call belongs."]
    lines.extend(f"  `{tok}`  {why}" for tok, why in found)
    lines.append(
        "  ⚑ the judgement in this pipeline is happening in the TURN, "
        "not in a program —\n     it evaporates when the turn ends and "
        "the next reader re-derives it differently."
    )
    lines.append(
        "  run ONE tool call. If no mode answers your question, that is "
        "WORK (add the\n     mode), not grounds for a shell composition "
        "— the toolkit expands."
    )
    # ⚑⚑⚑ INLINE THE PORTABLE RULE, DROP THE POINTER (gate-G49). This line used to read
    # `see .claude/skills/struct-tools/SKILL.md` — a path that resolves in substrate and
    # NOWHERE ELSE, while this file is vendored by at least one peer. Measured against the
    # target: over half the skill's bytes are a GENERATED mode census, plus a tools roster
    # and an artifact→tool table. That is a ROSTER, and a consumer holding two hook files
    # has neither the tools nor the census — so the pointer cost them a dead path and
    # bought them nothing.
    #
    # ⚑⚑ AND THE SKILL'S ONE FULLY PORTABLE PARAGRAPH WAS THE PART THE REFUSAL OMITTED.
    # The permission argument is not substrate-specific and it is the strongest reason to
    # obey: it explains why this is not a style rule. So the refusal now carries the rule
    # and not the coordinate, which makes it strictly MORE useful to a consumer than the
    # pointer was — the third option, where the question had been posed as name-a-reachable-
    # successor versus name-none (SB-A10, mtools' constitution census).
    lines.append(
        "  ⚑ AND THIS IS NOT STYLISTIC: a chained command cannot be approved in a "
        "way that\n     STICKS. A one-off pipeline is a one-off approval, so every "
        "chain is a permission\n     prompt to be re-granted, while a named mode is "
        "approved once and reusable.\n     Composing converts durable tooling into "
        "disposable keystrokes."
    )
    return "\n".join(lines)


def main() -> int:
    """Read the PreToolUse payload from stdin and refuse or allow the command."""
    # ⚑ THE EXCEPTIONS ARE NAMED. A bare `except Exception` would swallow a bug in
    # this hook's own logic and return 0 — i.e. ALLOW — making a broken gate
    # indistinguishable from a passing one. Only a malformed payload is tolerated.
    try:
        payload: object = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError, OSError):
        return 0  # never break the session on a parse failure
    cmd = _command_of(payload)
    if not cmd.strip():
        return 0

    found = analyze(cmd)
    if not found:
        return 0

    msg = _refusal(found)
    if _armed():
        sys.stdout.write(_deny_payload(msg) + "\n")
        return 0
    sys.stderr.write(msg + "\n")
    return 0


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
        """Record one outcome, rendering the values at the boundary.

        ⚑ KEYWORD-ONLY, BECAUSE THE FIRST CUT OF THIS HELPER REINTRODUCED THE VERY
        SHAPE `fires_on`/`passes` EXIST TO AVOID. Extracting the shared body is right;
        passing a bare `True` into it is the boolean trap one layer down, and ruff
        caught it (FBT001/FBT003) in the same edit that removed sixty other findings.
        A refactor can carry in the defect it was cleaning.
        """
        self.rows.append((label, ok, repr(got), repr(want)))

    def fires_on(self, label: str, cmd: str) -> None:
        """Record a case asserting the gate REFUSES `cmd`."""
        got = bool(analyze(cmd))
        self._record(label, ok=got is True, got=got, want=True)

    def passes(self, label: str, cmd: str) -> None:
        """Record a case asserting the gate ALLOWS `cmd`."""
        got = bool(analyze(cmd))
        self._record(label, ok=got is False, got=got, want=False)

    def holds(self, label: str, *, got: bool) -> None:
        """Record a case asserting a plain property holds."""
        self._record(label, ok=got is True, got=got, want=True)

    def report(self, suite: str) -> bool:
        """Print any failures and the tally; return whether every case held."""
        ok = sum(1 for _n, g, _a, _b in self.rows if g)
        for name, good, got, want in self.rows:
            if not good:
                sys.stdout.write(f"  FAIL {name}: got {got} want {want}\n")
        sys.stdout.write(f"{suite} selftest: {ok}/{len(self.rows)}\n")
        return ok == len(self.rows)


# ⚑ NAMED FIXTURES AND A BUILDER, NOT INLINE LITERALS AT THE CALL SITE — the same
# reason `_deny_payload` exists: a nested literal is inferred on its own.
_NOT_A_MAPPING: list[str] = ["nope"]
_EMPTY_PAYLOAD: dict[str, object] = {}
_BAD_TOOL_INPUT: dict[str, object] = {"tool_input": "nope"}


def _payload(command: object) -> dict[str, object]:
    """Build a PreToolUse payload carrying `command`, typed at every level."""
    tool_input: dict[str, object] = {"command": command}
    return {"tool_input": tool_input}


def _cases_operators(c: _Cases) -> None:
    """Add the cases for shell composition operators and control flow."""
    c.fires_on("a pipe fires", "scripts/buildtime.py --top | tail -5")
    c.fires_on("&& fires", "make -C agda -j && echo done")
    c.fires_on("; fires", "cd agda; make")
    c.fires_on("a for-loop fires", "for f in *.py; do wc -l $f; done")
    c.fires_on("|| fires", "make || echo failed")
    c.fires_on("a case dispatch fires", "case $x in a) echo 1;; esac")
    # ⚑ THE ARM THIS SELFTEST DID NOT HAVE, AND ITS ABSENCE READ AS GREEN.
    # `|&` was uncovered: shlex emits it as ONE token and the local literal did not
    # list it, so this command was ALLOWED while `make | grep foo` was denied. The
    # suite passed throughout — it proved the operators the hook knew about. A
    # divergence measured by a peer, ruled deliberate by me on the strength of a
    # stale comment, and only settled by running the tokenizer.
    c.fires_on("⚑ |& fires (was the gap)", "make |& grep foo x.py")
    # and coverage is now DERIVED: every operator the shared authority knows is
    # covered here, so a token added there cannot silently go unhandled here.
    c.holds("every shared operator is covered", got=set(OPERATORS) >= hook_cmdparse.OPERATORS)


def _cases_directory_change(c: _Cases) -> None:
    """Add the cases for `cd`, the most common caught shape.

    ⚑ Operator, 2026-08-30: `cd <dir> && <cmd>` is what this hook catches most, and
    the `&&` explanation alone ("two questions that want one mode") is true and
    useless there. The message has to name `env -C`, or the refusal blocks without
    routing — the same defect `hook_structural_query` recorded when its text named an
    unrunnable tool and stopped.
    """
    c.fires_on("⚑ a bare cd fires on its own", "cd agda")
    c.fires_on("cd && cmd fires", "cd agda && make -j")
    cd_msg = _refusal(analyze("cd agda && make -j"))
    c.holds("⚑ ...and the message names `env -C` as the one-call form", got="env -C" in cd_msg)
    c.holds(
        "...and says why: the directory is an INPUT, not ambient state",
        got="ambient effect" in cd_msg,
    )
    # ⚑ COMMAND POSITION GUARDS `cd` THE SAME WAY IT GUARDS `for`.
    c.passes("`cd` as an argument is not a chdir", "grep -w cd notes.md")
    c.passes("a filename containing cd is not a chdir", "python3 scripts/abcd.py")
    # ⚑ AND THE REPLACEMENT THIS HOOK RECOMMENDS MUST ITSELF PASS, or the advice
    # routes into a second refusal.
    c.passes("⚑ the recommended `env -C` form passes", "env -C agda make -j")
    # ⚑⚑⚑ THE REFUSAL CARRIES THE RULE AND NOT A COORDINATE (gate-G49), AND NOTHING
    #   PINNED THIS UNTIL NOW. The text is this hook's entire product and it is VENDORED,
    #   so a consumer reads whatever it says with no access to substrate's tree. It used
    #   to end `see .claude/skills/struct-tools/SKILL.md` — a path that resolves here and
    #   nowhere else, pointing at a file over half of which is a generated mode census.
    # ⚑⚑ BOTH DIRECTIONS ARE ASSERTED, because either alone permits the defect: a case
    #   demanding the rule passes with the dead pointer still appended, and a case
    #   forbidding the pointer passes if the rule were dropped too.
    c.holds(
        "⚑ the refusal carries the PORTABLE rule, not a substrate path",
        got="approved in a way that" in cd_msg,
    )
    c.holds(
        "...and says WHY it is not stylistic — a chain is a one-off approval",
        got="one-off approval" in cd_msg,
    )
    c.holds(
        "⚑ ...and names NO path a vendoring consumer cannot resolve",
        got=".claude/skills" not in cd_msg,
    )


def _cases_false_positives(c: _Cases) -> None:
    """Add the cases that would get the hook disabled if they fired.

    Each CONTAINS a banned character and composes nothing. A substring ban fires on
    every one of these; parsing is why they pass.
    """
    c.passes("a quoted pipe in a regex is data", "grep -nE 'foo|bar' notes.md")
    c.passes("a semicolon inside an awk body is data", "awk '{print; n++}' data.tsv")
    c.passes("a quoted semicolon is data", 'echo "a;b"')
    # ⚑⚑⚑ A QUOTE THAT OPENS MID-WORD IS STILL A QUOTE (summit
    # ask-structural-hook-distinguishes-a-pattern-from-a-path, 2026-09-20). The three cases
    # above quote at the word's START; this hook's private tokenizer ran shlex in non-POSIX
    # mode, which does not recognise a quote after `note=`, so the `;` below read as an
    # operator and the hook refused six `bibstruct --add` calls in one session. Each was
    # "fixed" by rewording the note — the evasion the ask names. The hook now delegates to
    # the shared POSIX tokenizer; this case is what reddens if the copy ever comes back.
    c.passes(
        "⚑⚑ a semicolon inside a mid-word-quoted argument is data",
        'python3 scratch/bibstruct.py --add k note="one; two" --apply',
    )
    c.passes("⚑ a pipe inside a mid-word-quoted argument is data", "tool pat='a|b' notes.md")
    c.passes("`for` inside a filename is not a keyword", "python3 scripts/format_for_each.py")
    c.passes("`for` as an argument is not a keyword", "grep -w for notes.md")
    c.passes("a plain single call passes", "scripts/worklist_gate.py --order")
    c.passes("a flag containing a pipe char stays quoted", "rg --glob '*.{py|md}' xyz")
    # ⚑ THE CASES THAT MUST PASS: invoking a COMMITTED tool is the behaviour the rule
    # WANTS. If these fire, the hook has inverted its own purpose.
    c.passes("running a real script passes", "python3 scripts/worklist_gate.py --order")
    c.passes("a wrapped real script passes", "timeout 400 python3 scripts/worklist_gate.py --order")
    c.passes("python3 -m on a real module passes", "python3 -m json.tool data.json")
    c.passes("a bare REPL is not a script", "python3")
    c.passes("an interpreter named as an argument passes", "grep -rn python3 notes.md")
    # ⚑ AN UNBALANCED QUOTE IS BASH'S VERDICT, NOT OURS.
    c.passes("an unparseable command is allowed through, not crashed on", "echo 'unterminated")


def _cases_inline_interpreter(c: _Cases) -> None:
    """Add the cases for a program written in the turn, and for heredoc bodies."""
    c.fires_on("python3 -c fires", 'python3 -c "import ast; print(1)"')
    c.fires_on("python -c fires", 'python -c "print(1)"')
    c.fires_on("a wrapper does not hide it", 'timeout 300 python3 -c "print(1)"')
    c.fires_on("uv run does not hide it", 'uv run --with networkx python3 -c "print(1)"')
    c.fires_on("an env-var prefix does not hide it", 'PYTHONPATH=scratch python3 -c "print(1)"')
    c.fires_on("a stdin script fires", "python3 - < prog.py")
    c.fires_on("a heredoc script fires", "python3 <<EOF\nprint(1)\nEOF")
    c.fires_on("perl -e fires", 'perl -e "print 1"')

    # ⚑ A HEREDOC BODY IS DATA, AND THIS WAS THE FIRST MEASURED FALSE POSITIVE
    # AFTER ARMING.  Claude Code ships no commit tool, so every multi-line commit
    # message goes through `git commit -F - <<EOF` — and a message that DESCRIBES
    # shell (or merely contains prose punctuation) was being read as shell. The
    # hook refused a single tool call because of the content of its own argument.
    c.passes(
        "prose in a heredoc body is not composition",
        "git commit -F - <<EOF\nfixed a ; b and c | d and e || f\nEOF",
    )
    c.passes("a quoted heredoc tag is handled", "cat > f <<'EOF'\na | b\nEOF")
    # …and the two things that must STILL fire, or the strip has overreached:
    c.fires_on(
        "an operator AFTER the heredoc still fires",
        "git commit -F - <<EOF\nmsg\nEOF\necho done | wc -l",
    )
    c.fires_on("a heredoc INTO an interpreter still fires", "python3 <<PY\nprint(1)\nPY")


def _cases_message_and_payload(c: _Cases) -> None:
    """Add the cases for the refusal TEXT, the deny envelope, and the payload reader.

    ⚑ A refused caller acts on the MESSAGE, so its content needs a witness the same
    way the verdict does. And a hook that mis-reads its own INPUT renders a verdict
    about something other than what ran, so every rejected payload shape gets a case.
    """
    msg = _refusal(analyze("make | tail -5"))
    c.holds("the refusal names the offending token", got="`|`" in msg)
    c.holds("...and says a missing mode is the WORK", got="add the" in msg)

    # ⚑ THE DENY ENVELOPE IS WHAT THE HARNESS ACTUALLY READS — an empty stdout is
    # read as ALLOW, so a malformed envelope is a silently-inert gate.
    rendered = _deny_payload(msg)
    c.holds("the deny envelope names the event", got="PreToolUse" in rendered)
    c.holds("...and carries the decision", got='"deny"' in rendered)
    c.holds("...and carries the reason text", got="no-chaining" in rendered)

    c.holds(
        "a well-formed payload yields its command", got=_command_of(_payload("a | b")) == "a | b"
    )
    c.holds("a non-string command yields no command", got=_command_of(_payload(7)) == "")
    c.holds("a non-mapping payload yields no command", got=_command_of(_NOT_A_MAPPING) == "")
    c.holds("a payload with no tool_input yields no command", got=_command_of(_EMPTY_PAYLOAD) == "")
    c.holds("a non-mapping tool_input yields no command", got=_command_of(_BAD_TOOL_INPUT) == "")


def _selftest() -> bool:
    """Run every case group and report whether all of them hold.

    ⚑ THE GROUPS ARE SEPARATE FUNCTIONS BECAUSE THE STATEMENT GATE FIRED (PLR0915,
    54 > 50) when the `cd` cases were added — the same forcing function as C901 one
    level down, and the same answer: the unit was doing too much. Each group is now
    one concern, and the concern is its name.
    """
    c = _Cases()
    _cases_operators(c)
    _cases_directory_change(c)
    _cases_false_positives(c)
    _cases_inline_interpreter(c)
    _cases_message_and_payload(c)
    return c.report("hook_no_chaining")


# ⚑ THE READER IS SHARED, NOT COPIED. `_arg_after` lived here as one of FOUR
# byte-identical private copies (this hook, `hook_cmdparse`, `hook_shellcheck`, and
# `hook_structural_query` — whose copy had ZERO CALLERS). That is the
# `agda_files()`-had-four-bodies shape, which this repo has already paid for once, so
# the paydown is a DELETION of the copies rather than four separate conversions.
# ⚑ THE COPIES WERE CAPTIVE: each read `sys.argv` directly, so no case could vary the
# input and none ever exercised an ABSENT flag — where every copy raised `ValueError`
# instead of returning the empty string its own docstring promised. The shared reader
# takes argv as a PARAMETER, which is both the fix and the testability.
#
# ⚑⚑⚑ IMPORTED LAZILY, ON THE CLI PATH ONLY — NEVER AT MODULE LOAD (summit
# ask-shared-hook-imports-a-package-only-its-owner-has, reopened 2026-09-20 by
# measurement). This hook is VENDORED into checkouts without the `substrate` package; a
# module-level import raised `ModuleNotFoundError` AT LOAD there, the harness read empty
# stdout as ALLOW, and the hook guarded nothing while reading as armed. The reader serves
# `--explain` alone; the hook path never touches it, so an adopter keeps a fully ARMED
# hook and loses only the maintainer CLI, which says so. `hook_shellcheck` carries the
# same shape for the same reason.
_NO_READER = (
    "no-chaining hook: --explain needs `substrate.ratchet_flags`, which is not "
    "importable here ({err}). The HOOK itself is unaffected.\n"
)


def _explain_operand() -> str:
    """Return `--explain`'s operand through the shared reader, refusing loudly without it."""
    try:
        from substrate.ratchet_flags import arg_after  # noqa: PLC0415 - the vendoring seam
    except ImportError as err:
        sys.stderr.write(_NO_READER.format(err=err))
        sys.exit(2)
    return arg_after(sys.argv, "--explain")


def _main() -> int:
    """Dispatch the CLI modes and return the exit code."""
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    if "--explain" in sys.argv:
        # `--explain '<cmd>'` — what would this hook say about one command?
        for tok, why in analyze(_explain_operand()):
            sys.stdout.write(f"{tok:<4} {why}\n")
        return 0
    return main()


if __name__ == "__main__":
    sys.exit(_main())
