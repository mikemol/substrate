#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
r"""hook_cmdparse.py — ONE Bash-command tokenizer, shared by the PreToolUse hooks.

⚑ WHY THIS MODULE EXISTS, AND IT IS A MEASURED DEFECT NOT A TIDINESS URGE.
`hook_no_chaining` parsed commands with `shlex(punctuation_chars=True)` and tracked
COMMAND POSITION across operators. `hook_structural_query` did not: it used
`cmd.split("|")` then `seg.strip().split()` and tested ONLY `toks[0]`. So every
`timeout 180 grep -n foo x.py` sailed through — `toks[0]` was `timeout`, the textual
tool was never seen, and the gate was open for essentially every command this session
actually issued (a `timeout` prefix is the default invocation shape). The bypass was
demonstrated live, by the controller, while verifying an unrelated audit.

Two hooks needed the same capability and only one had it. That is the
`agda_files()`-was-four-bodies shape one layer up — and the tooling audit had just
found `py_files` living as a 3-body reimplementation feeding two pre-commit gates. So
the tokenizer is lifted HERE and imported, rather than copied a second time.

⚑ WRAPPERS DO NOT END THE SEARCH. `timeout`, `env`, `xargs`, `sudo`, `nice` and
friends are TRANSPARENT: the real command is behind them. A scan that stops at the
first word cannot see it, which is precisely the bug. `VAR=value` prefixes and a
leading `\` (quoting to defeat an alias) are stripped for the same reason.
"""

from __future__ import annotations

import importlib
import shlex
import sys
from pathlib import Path

# Shell operators that START a new command. THIS IS THE AUTHORITY: both hooks now
# derive membership from it (`hook_no_chaining` builds its explanation dict over
# these keys), so an operator added here is covered everywhere by construction.
#
# ⚑⚑ IT WAS NOT ALWAYS BOTH, AND THE GAP WAS `|&`. `hook_no_chaining` carried its own
# literal missing `|&`, justified by a comment claiming shlex "reduces" `|&` to
# `|` + `&`. It does not — `punctuation_chars=True` emits `|&` as ONE token, with
# and without `whitespace_split`. So `make |& grep foo x.py` was ALLOWED there while
# `make | grep foo` was denied. Measured end-to-end by a peer session (summit, ref
# linux-sources) with controls on both sides; reproduced here by `--tokens`.
#
# ⚑ AND I RULED THE DIVERGENCE DELIBERATE BEFORE CHECKING IT. Three things agreed
# with me and all three were downstream of that one stale sentence: the comment
# itself; `--explain`, which segments correctly HERE because this set has `|&`, so
# it could not speak to a hook whose set lacked it; and a green `--selftest`, which
# proved the arms the hook had and never the arm it lacked. The mode that would
# have caught it (`--tokens`) did not exist until the peer forced the question.
#
# So the lesson is sited on the DATA, not in a paragraph elsewhere: a second copy of
# this literal is how the gap happened, and deriving from one authority is the fix.
# Do not re-inline it in a consumer.
# ⚑ THE ANNOTATION IS FOR THE IMPORT CYCLE, NOT FOR THE READER. This module and
# `hook_no_chaining` import each other (that one derives its OPERATORS map from this
# set; this one's `--tokens` compares against that map). While both edges were
# `sys.path.insert` + bare import, mypy could follow neither and the cycle was
# invisible; once they became declarations it reported `Cannot determine type of
# "OPERATORS"` at the consumer — inference cannot complete a cycle it must traverse
# to type the binding it is traversing for. An explicit type terminates the recursion
# at the authority, which is where it costs nothing and says something true.
OPERATORS: set[str] = {"|", "||", "&&", ";", "&", "|&"}

# ⚑⚑⚑ REDIRECTION IS DELIBERATELY *NOT* MODELLED, AND THE REFUSAL OF A WRITE IS CORRECT.
# I began building a `WRITE_REDIRECTS` exemption so `cat >> x.py` would pass — treating
# cassian-observability's report as a false positive. Operator ruling, 2026-08-19:
# *"don't support redirection, support editing"* / *"appendation causes files to grow out
# of control."* The hook is RIGHT to refuse `cat >> x.py`, and for a reason stronger than
# the one it prints: a shell append is an unbounded, unstructured, unreviewable write to
# an artifact that has a structural editor.
#
# ⚑⚑ AND THIS SESSION MEASURED THE DAMAGE IT CAUSES. `MEMORY.md`'s staging block is
# appended to and never drained (its self-clear regex has matched 0 of 44 lines across
# 167 recorded regens), so the file grew past the 200-line budget of the reader that
# loads it EVERY SESSION. Exempting `>>` would have blessed exactly that mechanism —
# a fix that removes an alarm because the alarm is inconvenient.
#
# ⚑ SO THE GAP IS IN THE REFUSAL TEXT, NOT THE VERDICT. `_refusal` tells a blocked
# READER to use the harness `Read` tool; a blocked WRITER is told the same thing, which
# is useless advice for an append and reads as a bug. Naming `Write`/`Edit` there is the
# real fix: same verdict, a route the author can actually take.

# ⚑ TRANSPARENT PREFIXES — a wrapper delegates to the command after it, so finding
# one means KEEP LOOKING, not stop. Every entry here was a live bypass shape.
WRAPPERS: set[str] = {
    "timeout",
    "env",
    "xargs",
    "command",
    "builtin",
    "exec",
    "nice",
    "ionice",
    "nohup",
    "stdbuf",
    "time",
    "watch",
    "sudo",
    "doas",
    "setsid",
    "script",
    "uv",
    "poetry",
    "pipenv",
    "hatch",
    "rye",
}

# A wrapper's own operand — never the program being wrapped.
_UV_SUBCOMMANDS: set[str] = {"run", "tool", "pip", "venv", "sync", "add", "exec", "shell"}

# ⚑ A duration suffix on a `timeout` operand: `timeout 30s`, `1.5h`.
_DURATION_SUFFIXES = "smhd"

# Wrappers whose first non-flag word is a SUBCOMMAND of the wrapper itself.
_SUBCOMMAND_WRAPPERS: set[str] = {"uv", "poetry", "pipenv", "hatch", "rye"}

# ⚑⚑⚑ WRAPPER FLAGS THAT TAKE A SEPARATE ARGUMENT — AND OMITTING THIS WAS A LIVE,
# MEASURED BYPASS OF EVERY HOOK THAT ROUTES THROUGH `programs()`.
#
# The skip loop below consumed a `-x` token (it cannot name a program) and then read
# the NEXT token as the program. For a flag that takes its argument SEPARATELY, that
# next token is the flag's OPERAND, so the operand was reported as the program and the
# real command behind it was never examined:
#
#     env -C /tmp grep -c def x.py   ->  program `tmp`,  `grep` INVISIBLE
#     timeout -s KILL 60 grep foo    ->  program `KILL`, `grep` INVISIBLE
#     sudo -u nobody grep foo x.py   ->  program `nobody`, `grep` INVISIBLE
#
# ⚑⚑ AND `programs()`' OWN DOCSTRING CLAIMED THIS ALREADY WORKED — *"A wrapper's own
# flags (`env -i`, `timeout -s KILL`) are skipped too"* — naming `timeout -s KILL` as a
# worked case when it was precisely the broken one. `env -i` passes because `-i` takes
# NO argument, so the single example that was checked was the one that could not fail.
# A docstring is not a witness; the arms below are.
#
# ⚑ THIS IS THE SAME CLASS AS THE `timeout 180` BYPASS THIS MODULE WAS CREATED TO FIX,
# one token to the right. That one skipped the wrapper and stopped before its numeric
# OPERAND; this one skips the flag and stops before the FLAG's operand. `_is_operand`
# was the answer there and is deliberately not the answer here: it is value-shaped
# (is this token a number, a duration, a known subcommand?) and a flag's argument can
# be ANY string — `/tmp`, `KILL`, `nobody`. Only the FLAG knows it takes one.
#
# ⚑ ATTACHED FORMS (`-Cdir`, `--chdir=dir`) NEED NO ENTRY: the operand is inside the
# same token, so the existing flag-skip already consumes it whole.
_FLAGS_WITH_ARG: dict[str, set[str]] = {
    "env": {"-C", "-u", "--chdir", "--unset", "-S", "--split-string"},
    "timeout": {"-s", "-k", "--signal", "--kill-after"},
    "sudo": {
        "-u",
        "-g",
        "-p",
        "-C",
        "-D",
        "-h",
        "-R",
        "-t",
        "-T",
        "--user",
        "--group",
        "--prompt",
        "--chdir",
        "--host",
    },
    "doas": {"-u", "-C"},
    "nice": {"-n", "--adjustment"},
    "ionice": {"-c", "-n", "-p", "-P", "--class", "--classdata", "--pid"},
    "stdbuf": {"-i", "-o", "-e", "--input", "--output", "--error"},
    "xargs": {
        "-a",
        "-E",
        "-I",
        "-i",
        "-L",
        "-l",
        "-n",
        "-P",
        "-s",
        "-d",
        "--arg-file",
        "--delimiter",
        "--max-args",
        "--max-procs",
        "--max-lines",
        "--replace",
        "--max-chars",
    },
    "setsid": set(),
    "nohup": set(),
    "script": {"-c", "--command", "-f", "-t"},
    "watch": {"-n", "-d", "--interval"},
    "command": set(),
    "builtin": set(),
    "exec": {"-a"},
    "time": {"-f", "-o", "--format", "--output"},
    "uv": {"--python", "-p", "--with", "--directory", "--project"},
    "poetry": {"-C", "--directory"},
    "pipenv": set(),
    "hatch": {"-p", "--project"},
    "rye": set(),
}


def _debare(tok: str) -> str | None:
    r"""Reduce a token to the program it names, or None if it names none.

    Strips a leading `\` (alias-defeating quote) and resolves a path to its
    basename, so `/usr/bin/grep` and `\grep` both read as `grep`.
    """
    if not tok:
        return None
    t = tok.lstrip("\\")
    if not t or t.startswith("-"):
        return None
    if "=" in t and not t.startswith("/") and t.split("=", 1)[0].isidentifier():
        return None  # VAR=value assignment, not a program
    return Path(t).name


def _is_operand(word: str, wrapper: str) -> bool:
    """Report whether `word` is an operand OF the wrapper, not the program it wraps.

    ⚑ CONSERVATIVE BY DESIGN: only forms that CANNOT name a program are consumed.
    Guessing wrong here silently reopens the bypass, so a doubtful token ends the
    skip and is treated as the program.
    """
    if word.replace(".", "", 1).isdigit():  # timeout 180 / 1.5
        return True
    if word[:-1].replace(".", "", 1).isdigit() and word[-1] in _DURATION_SUFFIXES:
        return True  # timeout 30s
    if wrapper in _SUBCOMMAND_WRAPPERS:
        return word in _UV_SUBCOMMANDS
    return False


def tokenize(cmd: str) -> list[str]:
    """Split a command into shell words with operators separated.

    Returns [] if the command will not parse.

    ⚑ AN UNBALANCED QUOTE IS BASH'S VERDICT, NOT OURS: return empty and let the
    command through rather than breaking the session on a parse failure.

    ⚑⚑⚑ POSIX MODE, BECAUSE BASH QUOTES MID-WORD AND NON-POSIX shlex DOES NOT. The default
    (non-POSIX) lexer recognises a quote only at a word's start, so `note="one; two"` split
    at the `;` and a byte inside an argument read as a sequence operator — six refused
    `bibstruct --add` calls in one session, each evaded by rewording (summit
    ask-structural-hook-distinguishes-a-pattern-from-a-path). POSIX mode also STRIPS the
    quotes, so every consumer sees the word bash would hand the program: `'foo|bar'` arrives
    as `foo|bar`, one token, still not an operator. `punctuation_chars=True` keeps `|&`,
    `&&`, `;` and friends as their own tokens in either mode.
    """
    try:
        lx = shlex.shlex(cmd, posix=True, punctuation_chars=True)
        lx.whitespace_split = True
        return list(lx)
    except ValueError:
        return []


def commands(cmd: str) -> list[list[str]]:
    """Split the command string into its individual commands.

    Each element is one command's words, operators removed. `a | b && c` yields
    three lists. This is what lets a caller ask "is a textual tool in command
    position ANYWHERE in this line", which is the question `toks[0]` could not answer.
    """
    out: list[list[str]] = []
    cur: list[str] = []
    for tok in tokenize(cmd):
        if tok in OPERATORS:
            if cur:
                out.append(cur)
            cur = []
            continue
        cur.append(tok)
    if cur:
        out.append(cur)
    return out


def programs(cmd: str) -> list[tuple[str, list[str]]]:
    """Return every program INVOKED, seeing through wrappers, with its own arguments.

    ⚑ THE CAPABILITY THE BYPASS PROVED WAS MISSING. `timeout 180 grep -c x f.py`
    yields ('grep', ['-c', 'x', 'f.py']) — the wrapper and its numeric argument are
    consumed, and the real program is reported with the arguments IT receives.

    A wrapper's own flags are skipped too, AND SO ARE THEIR ARGUMENTS when the flag
    takes one separately (`_FLAGS_WITH_ARG`). ⚑ This sentence previously named
    `timeout -s KILL` as a worked example while that exact form was BROKEN — it
    reported `KILL` as the program. The arms in `_selftest` are the witness; this
    paragraph is not.
    """
    found: list[tuple[str, list[str]]] = []
    for words in commands(cmd):
        i = 0
        while i < len(words):
            name = _debare(words[i])
            if name is None:  # a flag or VAR= prefix: skip it
                i += 1
                continue
            if name in WRAPPERS:
                # ⚑ CONSUME THE WRAPPER *AND ITS OPERANDS*. `timeout 180 grep` puts
                # a DURATION between the wrapper and the real program; a first draft
                # skipped only the wrapper and then reported `180` as the program.
                # An operand that cannot name a program (a number, a duration like
                # `1.5s`, a bare subcommand word for uv/poetry) is skipped; the first
                # token that could be a program ends the skip.
                takes_arg = _FLAGS_WITH_ARG.get(name, set())
                i += 1
                while i < len(words):
                    raw = words[i]
                    nxt = _debare(raw)
                    if nxt is None:  # a flag: still the wrapper's
                        # ⚑⚑ AND SO IS ITS ARGUMENT, WHEN THE FLAG TAKES ONE SEPARATELY.
                        # Skipping only the flag left the loop pointing at the flag's
                        # OPERAND and reported THAT as the program — `env -C /tmp grep`
                        # read as `tmp`, hiding `grep` from every hook downstream.
                        # An attached form (`-C/tmp`, `--chdir=/tmp`) carries its operand
                        # in the same token, so only the SEPARATE spelling advances twice.
                        i += 1
                        if raw.lstrip("\\") in takes_arg and i < len(words):
                            i += 1
                        continue
                    if _is_operand(nxt, name):
                        i += 1
                        continue
                    break
                continue
            found.append((name, words[i + 1 :]))
            break  # the rest of THIS command is args
    return found


def consumer_operators() -> set[str] | None:
    """Return `hook_no_chaining`'s OPERATORS set, or None if it cannot be read.

    ⚑⚑ RESOLVED AT CALL TIME, AND THAT IS THE POINT — NOT A DEFERRED-COST TRICK.
    `hook_no_chaining` imports THIS module at its top level, so a top-level import
    back would be a genuine circular import: whichever module loaded second would
    see a half-initialised first. Resolving at call time breaks the cycle at the
    only edge that can afford it — this one is used by ONE diagnostic mode and one
    selftest case, never by the hook path.

    ⚑ AND THE None IS A REAL THIRD STATE, NOT A CONVENIENCE. "the consumer is not
    importable here" and "the consumer declares no operators" are different facts,
    and a caller that renders them identically reports a MISSING READER as an EMPTY
    SET — which is exactly the shape of the `|&` misreading this module exists to
    have caught.

    ⚑ THE `object` BINDING IS THE NARROWING, NOT A FORMALITY. A dynamic attribute
    read is untyped, and letting it flow straight into a typed return is how an
    unchecked shape crosses a module boundary unexamined. Binding it as `object`
    forces the checks below to be what establishes the type.

    ⚑⚑ THE CONSUMER'S `OPERATORS` IS A **dict**, NOT A SET, AND THE FIRST CUT OF
    THIS FUNCTION TESTED `isinstance(ops, set)` AND SILENTLY RETURNED None. The
    selftest then printed SKIP — a FALSE UNMEASURED that looked exactly like the
    honest one, on an arm built to catch a divergence between these two spellings.
    ⚑ A guard that cannot tell "absent" from "a shape I did not anticipate" reports
    the second as the first, which is how a comparison arm goes quiet without ever
    failing. Both containers are accepted; iterating a dict yields its KEYS, which
    is the operator set either way.
    """
    try:
        mod = importlib.import_module("scripts.hook_no_chaining")
    except ImportError:
        return None
    ops: object = getattr(mod, "OPERATORS", None)
    if not isinstance(ops, (set, frozenset, dict, list, tuple)):
        return None
    return {item for item in ops if isinstance(item, str)}


def _selftest() -> bool:
    """Run the cases and report whether all of them hold."""
    cases: list[tuple[str, bool, object, object]] = []

    def check(label: str, got: object, want: object) -> None:
        cases.append((label, got == want, got, want))

    def progs(c: str) -> list[str]:
        return [p for p, _a in programs(c)]

    # --- the live bypass, and its family ----------------------------------
    check("a bare command is found", progs("grep -n foo x.py"), ["grep"])
    check("⚑ timeout does not hide the tool", progs("timeout 180 grep -c foo x.py"), ["grep"])
    check("env does not hide it", progs("env grep foo x.py"), ["grep"])
    check("xargs does not hide it", progs("xargs grep foo"), ["grep"])
    check("sudo does not hide it", progs("sudo grep foo x.py"), ["grep"])
    check("a VAR= prefix does not hide it", progs("PYTHONPATH=. grep foo x.py"), ["grep"])
    check("an absolute path resolves", progs("/usr/bin/grep foo x.py"), ["grep"])
    check("a backslash-quoted name resolves", progs("\\grep foo x.py"), ["grep"])
    check("stacked wrappers resolve", progs("timeout 60 env nice grep foo x.py"), ["grep"])

    # --- ⚑⚑⚑ A WRAPPER FLAG'S *ARGUMENT* IS THE WRAPPER'S TOO --------------
    # Each of these RAN successfully against every hook routing through this module:
    # the flag was skipped, its OPERAND was read as the program, and the real textual
    # tool behind it was never examined. Measured live — `env -C <dir> grep -c def
    # <abs path>.py` returned an answer while the bare `grep` was refused, which read
    # as "the hook is cwd-scoped" and is nothing of the kind.
    check("⚑⚑ env -C does not hide the tool", progs("env -C /somewhere grep -c def x.py"), ["grep"])
    check(
        "⚑⚑ timeout -s does not hide it (the docstring's own false example)",
        progs("timeout -s KILL 60 grep foo x.py"),
        ["grep"],
    )
    check("⚑ sudo -u does not hide it", progs("sudo -u nobody grep foo x.py"), ["grep"])
    check("⚑ nice -n does not hide it", progs("nice -n 10 grep foo x.py"), ["grep"])
    check("⚑ stdbuf -o does not hide it", progs("stdbuf -o0 grep foo x.py"), ["grep"])
    check(
        "⚑ long-form env --chdir does not hide it",
        progs("env --chdir /somewhere grep foo x.py"),
        ["grep"],
    )
    check(
        "⚑ stacked flag-taking wrappers resolve",
        progs("env -C /somewhere timeout -s KILL 60 grep foo x.py"),
        ["grep"],
    )
    # ⚑ THE ATTACHED SPELLINGS MUST NOT DOUBLE-SKIP — the operand is in the same
    # token, so consuming a second one would swallow the real program instead.
    check(
        "⚑ an attached -C<dir> does not swallow the program",
        progs("env -C/somewhere grep foo x.py"),
        ["grep"],
    )
    check(
        "⚑ an attached --chdir=<dir> does not swallow the program",
        progs("env --chdir=/somewhere grep foo x.py"),
        ["grep"],
    )
    # ⚑ A NO-ARGUMENT FLAG STILL MUST NOT CONSUME THE PROGRAM. `env -i` is the one
    # example the old docstring named that actually worked; it must keep working.
    check("env -i (no argument) still finds the tool", progs("env -i grep foo x.py"), ["grep"])
    check(
        "⚑ a flag-taking wrapper with the flag ABSENT is unaffected",
        progs("env grep foo x.py"),
        ["grep"],
    )
    # ⚑ THE ARGUMENTS REPORTED MUST STILL BE THE REAL PROGRAM'S, not the wrapper's.
    check(
        "the wrapped program's args survive the flag skip",
        programs("env -C /somewhere grep -c foo x.py")[0][1],
        ["-c", "foo", "x.py"],
    )

    # --- args must belong to the REAL program, not the wrapper ------------
    check(
        "args are the real program's",
        programs("timeout 180 grep -c foo x.py")[0][1],
        ["-c", "foo", "x.py"],
    )

    # --- every command in a chain, not just the first ---------------------
    check("both sides of a pipe are seen", progs("cat x.py | grep foo"), ["cat", "grep"])
    check("both sides of && are seen", progs("make && grep foo x.py"), ["make", "grep"])
    # ⚑ `|&` — THE OPERATOR A CONSUMER'S PRIVATE COPY OF THIS SET ONCE LACKED, on the
    # false premise that shlex reduces it to `|` + `&`. It does not: the tokenizer
    # emits it whole, which is exactly what the first case below pins. An earlier
    # version of this comment asserted the divergence was deliberate and cited the
    # empty-command argument for it — that was my error, corrected after a peer
    # measured the hook end-to-end. The cases were always right; the story was not.
    check("|& is ONE token, not two", tokenize("make |& grep foo"), ["make", "|&", "grep", "foo"])
    check("|& does not hide the tool", progs("make |& grep foo x.py"), ["make", "grep"])
    check(
        "|& is ONE delimiter (no spurious empty command)", len(commands("make |& grep foo x.py")), 2
    )

    # --- ⚑ THE FALSE POSITIVES: quoted data is not an operator ------------
    check("a quoted pipe is data, one command", len(commands("grep -nE 'foo|bar' notes.md")), 1)
    check("a quoted semicolon is data", len(commands("awk '{print; n++}' data.tsv")), 1)
    # ⚑⚑⚑ A QUOTE THAT OPENS MID-WORD IS STILL A QUOTE (summit
    # ask-structural-hook-distinguishes-a-pattern-from-a-path, 2026-09-20). The two cases
    # above quote at the word's START, which non-POSIX shlex honours; `note="one; two"`
    # opens its quote AFTER `note=`, which non-POSIX shlex does NOT — it read the `;` as an
    # operator and `hook_no_chaining` refused six `bibstruct --add` calls in one session,
    # each "fixed" by rewording the note. Bash quotes mid-word; so must the tokenizer.
    check(
        "⚑⚑ a quote opening mid-word still protects a semicolon",
        len(commands('python3 bibstruct.py --add k note="one; two" --apply')),
        1,
    )
    check(
        "⚑⚑ a quote opening mid-word still protects a pipe",
        len(commands("grep -E pat='a|b' notes.md")),
        1,
    )
    check(
        "⚑ and the operand survives as one word",
        programs('tool note="one; two"')[0][1],
        ["note=one; two"],
    )

    # --- an unparseable command is bash's problem, not ours ---------------
    check("unbalanced quote yields nothing, does not raise", programs("echo 'unterminated"), [])

    # --- ⚑ THE CONSUMER'S SET MUST AGREE WITH THIS AUTHORITY --------------
    # A divergence here IS the `|&` defect, and it was invisible for as long as the
    # two sets were separate literals with no arm comparing them.
    consumer = consumer_operators()
    if consumer is None:
        # ⚑ UNMEASURED, NOT PASSED — the distinction this whole toolkit turns on.
        sys.stdout.write("  SKIP consumer-set agreement: hook_no_chaining not importable\n")
    else:
        check("the consumer's OPERATORS match this authority", consumer, OPERATORS)

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            sys.stdout.write(f"  FAIL {n}: got {got!r} want {want!r}\n")
    sys.stdout.write(f"hook_cmdparse selftest: {ok}/{len(cases)}\n")
    return ok == len(cases)


# ⚑ THE REPO ROOT IS SELF-SUPPLIED, matching both siblings. `python3 <abs-path>` puts
# the SCRIPT's directory on `sys.path[0]`, never the repo root, so the absolute import
# below resolves under the harness and NOT under a fire-probe — the shape that took
# five adopting repos from 13/13 to 11/13. See `hook_no_chaining` for the full record.
# ⚑ `absolute()`, NEVER `resolve()`: `resolve()` FOLLOWS SYMLINKS, so a resolved
# `__file__` derives SUBSTRATE's root in an adopting checkout. `PTH100` recommends the
# wrong spelling here; `absolute()` is `abspath`'s real counterpart.
_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ⚑⚑⚑ THE SHARED READER IS IMPORTED LAZILY, INSIDE THE DELEGATOR — NEVER AT MODULE LOAD
# (summit ask-shared-hook-imports-a-package-only-its-owner-has, reopened 2026-09-20). This
# module is the tokenizer every vendored hook imports at load, so a module-level
# `from substrate.ratchet_flags import …` here killed BOTH siblings in any checkout without
# the `substrate` package: `ModuleNotFoundError` at load, empty stdout, read as ALLOW.
# Summit's witness named the two hooks; substrate's own adopter-shaped probe (a copy of
# the three files under a root with no `substrate/`) found the traceback lands HERE first.
# The reader serves the CLI modes alone; the hook path never touches it.
_NO_READER = (
    "cmdparse: this CLI mode needs `substrate.ratchet_flags`, which is not "
    "importable here ({err}). The hooks that import this module are unaffected.\n"
)


def _arg_after(flag: str) -> str:
    """Return the argument following `flag` on the command line, or an empty string.

    ⚑ A ONE-LINE DELEGATOR to `substrate.ratchet_flags.arg_after`. This body was one of
    FOUR byte-identical private copies (this hook, `hook_no_chaining`, `hook_shellcheck`
    and `hook_structural_query` — whose copy had ZERO CALLERS): the
    `agda_files()`-had-four-bodies shape, which this repo has already paid for once, and
    which is paid down by DELETING the copies rather than converting each separately.
    ⚑⚑ THE COPIES WERE CAPTIVE: each read `sys.argv` directly, so no case could vary the
    input and none ever exercised an ABSENT flag — where every copy raised `ValueError`
    instead of returning the empty string this docstring promises. The shared reader
    takes argv as a PARAMETER, which is both the fix and the testability.
    ⚑ `check_argv` DOES NOT SUBSUME IT: that VALIDATES a flag set and returns an exit
    code; this EXTRACTS a flag's VALUE. Neither is spellable in terms of the other.
    ⚑ The import lives here, not at module scope, so a vendored copy without the package
    fails on a maintainer command and never at hook load (see the note above).
    """
    try:
        from substrate.ratchet_flags import arg_after  # noqa: PLC0415 - the vendoring seam
    except ImportError as err:
        sys.stderr.write(_NO_READER.format(err=err))
        sys.exit(2)
    return arg_after(sys.argv, flag)


def _main() -> int:
    """Dispatch the CLI modes and return the exit code."""
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1

    if "--explain" in sys.argv:
        for p, a in programs(_arg_after("--explain")):
            sys.stdout.write(f"{p:<12} {a}\n")
        return 0

    if "--tokens" in sys.argv:
        # ⚑ THE RAW TOKENS, AND WHICH OF THEM ANY GIVEN HOOK WOULD SEE AS AN
        # OPERATOR.  `--explain` reports the PROGRAMS this module finds, which is
        # a fact about THIS module's OPERATORS set — so it cannot answer "would a
        # hook with a DIFFERENT set split here".  A peer measured `|&` surviving
        # as one token and I checked it against `--explain`, which agreed with me
        # for the wrong reason: this module lists `|&`, so of course it segments.
        # The mode that would have caught my error is this one.
        toks = tokenize(_arg_after("--tokens"))
        sys.stdout.write(f"tokens: {toks}\n")
        sys.stdout.write(f"of these, operators HERE: {[t for t in toks if t in OPERATORS]}\n")
        consumer = consumer_operators()
        if consumer is None:
            sys.stdout.write("operators in hook_no_chaining: (not importable)\n")
        else:
            sys.stdout.write(
                f"operators in hook_no_chaining: {[t for t in toks if t in consumer]}\n"
            )
        return 0

    sys.stdout.write(f"{__doc__}\n")
    return 2


if __name__ == "__main__":
    sys.exit(_main())
