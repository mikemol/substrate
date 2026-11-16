#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""PreToolUse(Bash|Edit|Write|NotebookEdit) — refuse shell that shellcheck flags.

⚑ THE THIRD SIBLING, AND THE ONE THAT GATES CORRECTNESS RATHER THAN SHAPE.
`hook_no_chaining` refuses a COMPOSED command; `hook_structural_query` refuses a
TEXTUAL question about a STRUCTURED artifact. Both gate the SHAPE of a command —
neither reads what the shell MEANS. So `[ $x = y ]` with an empty `x`, an
unquoted `$f` carrying a space, and `cmd | tail; rc=$?` (which reports `tail`'s
status) all pass the existing pair untouched. That is the CLAUDE.md `A39` class
exactly: a defect that does not crash, it returns a plausible transcript.

⚑ NO SUPPRESSION MECHANISM EXISTS HERE, AND THAT IS THE DESIGN, NOT AN OMISSION.
The obvious affordance — some analogue of a per-line disable directive for a
one-line command — is deliberately absent. Operator ruling (2026-08-28):

    "I've seen far too many sloppy scripts doing/proving less than they're
     claimed to because of things shellcheck would block."

A disable directive is not a relief valve, it IS the defect being gated: it
does not make an unquoted expansion safe, it makes the script READ as reviewed.
That is this ecosystem's central failure mode (a claim outrunning the mechanism
that backs it) sited in shell. So relief lives on the ENUMERABLE side — the
`EXCLUDE` set below, finite and reviewable in one place — not on the
unenumerable side, where every call site may wave the rule away invisibly.

⚑ FAIL OPEN WHEN THE LINTER IS ABSENT — NEVER CLOSED. If `shellcheck` is not
installed, this hook must ALLOW and say so. A gate that denies every Bash call
because its own dependency is missing does not fail safe, it bricks the session
and cannot be repaired from inside the session it broke (installing shellcheck
needs root, which the agent does not have). An absent linter is an UNKNOWN, and
this hook does not convert an unknown into a verdict in either direction.

⚑ ADVISORY BY DEFAULT, matching both siblings. `SHELLCHECK_HOOK_BLOCK=1` (or the
shared `STRUCT_HOOK_BLOCK=1`) makes it refuse; an explicit `0` stands it down
even when the shared switch is on, so it can be staged behind the other two.

⚑⚑ WHAT THIS FILE NEEDS IN ORDER TO RUN, STATED HERE BECAUSE AN ADOPTER CANNOT
OTHERWISE KNOW. Copying this file alone is not enough and nothing said so until
now — the manifest is `scripts/HOOKS.tsv`, and it names every file a working
adoption requires. Measured: a peer vendored five hook files by name, and the set
was correct only because the person choosing it happened to know the import graph.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# ⚑ THE REPO ROOT IS SELF-SUPPLIED, BECAUSE THE ABSOLUTE IMPORT BELOW HAS A
# PRECONDITION THE HARNESS MEETS AND A FIRE-PROBE DOES NOT — see `hook_no_chaining`
# for the full record (cassian measured 13/13 → 11/13 across five adopting repos).
# `python3 <abs-path>` puts the script's own directory on `sys.path[0]`, never the
# repo root.
#
# ⚑⚑⚑ `absolute()`, NEVER `resolve()`, AND RUFF WILL TELL YOU OTHERWISE. `PTH100`
# offers `Path.resolve()` as the counterpart of `os.path.abspath`, and it is NOT one:
# `resolve()` FOLLOWS SYMLINKS. While this file was symlinked into other checkouts, a
# resolved `__file__` derived SUBSTRATE's root and the hook read substrate's data
# instead of the adopting repo's. That exact substitution shipped in the sibling on
# 2026-08-30, reached every adopter at write time, and was caught by a peer's routes
# slice — never by anything in this tree, because substrate is the one repo with no
# symlink to follow. `absolute()` is `abspath`'s real counterpart.
#
# ⚑⚑ AND UNDER THE VENDORING RULING THE HAZARD BECOMES UNOBSERVABLE RATHER THAN
# ABSENT. Adopters now vendor real copies instead of symlinking, so `absolute()` and
# `resolve()` return the SAME path in every tree that carries this file — measured.
# The defect does not go away, since `PTH100` still recommends the wrong spelling to
# the next maintainer; it stops being detectable by the tree that would suffer from
# it. That is why this note is load-bearing: the distinction has to be unmissable in
# the source precisely because no runtime check can see it any more.
_ROOT = Path(__file__).absolute().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# ⚑⚑ THE SIBLING'S HEREDOC STRIPPER WAS IMPORTED HERE AND IS NOW GONE, BECAUSE IT WAS
# SUPERSEDED AND THE BINDING OUTLIVED ITS USE. This hook first imported
# `hook_no_chaining`'s stripper on the one-body principle — a capability two hooks
# need must not have two copies, which is how `|&` went uncovered in that pair. Then
# DELETION turned out to be wrong for a PARSER: removing a heredoc body removes its
# terminator, and shellcheck reports SC1044/SC1072, a false positive INTRODUCED by
# the fix for the first one. `_neutralize_heredoc_bodies` below quotes the TAG
# instead, which is correct here and is genuinely this hook's own.
#
# ⚑ THE IMPORT AND ITS ALIAS SURVIVED THAT SUPERSESSION, UNUSED, UNTIL RUFF SAID SO
# (F401; `--calls _strip_heredoc_bodies` then reported 0 calls and 2 refs, both on the
# binding line). A DEAD BINDING OF A SHARED NAME IS WORSE THAN NO BINDING: it reads as
# a live one-body relationship that no longer exists, so a reader reasoning about
# drift between these two hooks would be reasoning about a link already cut.
#
# ⚑⚑⚑ AND IT CHANGES THIS FILE'S MANIFEST ENTRY. With that import gone, this hook is
# STANDALONE — no sibling required — where it previously needed `hook_no_chaining`
# and, through it, `hook_cmdparse`. An adopter can now vendor this one file and have
# a working hook. `scripts/HOOKS.tsv` records that, so the fact is readable without
# tracing imports by hand.

SHELLCHECK = "shellcheck"

# ⚑ PATH IS NOT THE AUTHORITY ON THIS MACHINE, AND TRUSTING IT FAILS SILENTLY OPEN.
# shellcheck here is a mise-managed tool (`mise use -g shellcheck@latest`), and mise
# tools are NOT on a non-interactive subprocess's bare PATH — measured 2026-08-28:
# `mise which shellcheck` resolves, `command -v shellcheck` exits 1. A hook that asks
# only PATH therefore concludes ABSENT, fails open (correctly, by its own rule), and
# announces itself inert — FOREVER, with the linter sitting installed three inches
# away. That is the armed-in-review/off-in-fact defect wearing this hook's own
# fail-open as a disguise: every part behaves as designed and the gate never runs.
#
# ⚑ THE SHIM, NOT THE INSTALL PATH. `mise which` returns a path carrying a VERSION
# that moves on the next upgrade. The shim is version-independent and verified to work
# without an activated shell, so it is the stable target. PATH is still tried FIRST: a
# repo that gets shellcheck from apt (or CI, or a container) must keep working with no
# mise present at all.
_MISE_SHIM = Path("~/.local/share/mise/shims/shellcheck").expanduser()

# ⚑ THE ENUMERABLE RELIEF SET. Every entry needs a reason and a date; this is the
# ONLY place a shellcheck rule may be waived, precisely so a waiver is visible to
# review instead of being scattered across call sites as disable directives.
# EMPTY IS THE CORRECT STARTING STATE — the false-positive population is
# MEASURED during advisory mode, not guessed at now. An entry added here without
# a measured false positive behind it is the suppression this hook exists to
# refuse, wearing the hook's own uniform.
EXCLUDE = {
    # ⚑ SC2329 — "This function is never invoked", raised on TRAP HANDLERS.
    # MEASURED 2026-08-28, and the first two hypotheses were WRONG, which is why
    # this entry exists at all rather than a rewrite:
    #   - shellcheck DOES understand `trap cleanup EXIT` (a minimal fixture with
    #     exactly that shape is clean), so "the linter can't see trap" is false;
    #   - `set -uo pipefail` vs `set -euo pipefail` makes no difference either.
    # Bisected by truncation with the EXIT CODE as the verdict: the flag appears
    # only when the script ends in an UNCONDITIONAL `exit 0`. shellcheck then
    # models every path as leaving via that explicit exit and does not treat the
    # EXIT trap as a call site — so a correct handler on a correct script reads
    # as dead code.
    # Affects three real handlers here, each of which DELETING WOULD BREAK:
    # build-telemetry (leaks 3 temp files), engine-trial (leaks a container +
    # a server process), collectors/ablate-zswap-compressor (leaves the zswap
    # compressor NOT restored — the ablation's whole safety property).
    # There is no idiom that makes the use visible to the linter, so the honest
    # move is the enumerable one: waive the rule HERE, in one reviewable place,
    # rather than scatter per-line directives across the call sites.
    "SC2329": "trap handlers read as uninvoked when a script ends in an "
    "unconditional `exit` (bisected 2026-08-28); deleting the handler "
    "breaks cleanup/restore",
    # ⚑ SC2016 — "Expressions don't expand in single quotes". True, and in a
    # CODE GENERATOR that is the entire point. Reviewed all 23 sites in this tree
    # on 2026-08-28; every one is a `$` or backtick that MUST stay literal:
    #   - scripts/prepare (16) generates co-sign PLAYBOOKS — the variables belong
    #     to the OUTPUT script. Double-quoting would expand them at generation time
    #     and emit a playbook with the values baked in or blanked. Following the
    #     rule here is not a style change, it is a BUG.
    #   - scripts/check-selftest (7) writes markdown fixtures containing backticks,
    #     and PLANTS fixture scripts whose substitution is the defect T14 must find —
    #     expanding those destroys the test.
    #   - scripts/replay, tests/* — same literal-text shape.
    # Unlike SC2086 (where quoting is the fix), SC2016 has no rewrite that keeps
    # the meaning: the text must stay unexpanded, so single quotes are correct and
    # the rule is simply mis-aimed at generator code. Waived in one reviewable
    # place rather than 23 scattered directives.
    "SC2016": "single quotes are correct in a code GENERATOR — the `$`/backtick "
    "belongs to the emitted script (23 sites reviewed 2026-08-28); "
    "expanding would corrupt the generated playbook or fixture",
    # ⚑⚑⚑ SC1091 — "Not following: <file> was not specified as input". This one is
    # an artifact of HOW THIS HOOK INVOKES SHELLCHECK, not a property of any script,
    # which makes it the clearest entry in this set: the script body is piped on
    # STDIN (`-`, see `_findings`), so shellcheck has NO DIRECTORY to resolve a
    # sourced path against and cannot follow the file however the script is written.
    # A `# shellcheck source=` directive does not help, and neither does `-x`.
    #
    # ⚑⚑ MEASURED 2026-09-01 on `scripts/membudget`, which sources `membudget-ledger`
    # after the ⟡ledger-parametric split: piped, SC1091; `shellcheck -x -P scripts
    # scripts/membudget`, CLEAN. Same bytes, two verdicts — so the finding tracks the
    # invocation, and reading it as a defect in the script would be a fact about the
    # METHOD reported as a fact about the SUBSTRATE.
    #
    # ⚑ AND THE ALTERNATIVE IS WORSE THAN THE WAIVER, WHICH IS WHY THIS IS NOT A FIX.
    # Making the hook write a temp file and run shellcheck ON A PATH would let it
    # follow sources — and would also make the hook lint whatever is ON DISK next to
    # that temp file, i.e. resolve a source against the wrong tree, and it would break
    # the pre-write check (the body being judged does not exist on disk yet, which is
    # the whole point of a PreToolUse gate). Piping is correct; not following is the
    # price, and it is a NOT-FOLLOWED, never a not-clean.
    #
    # ⚑ WHAT THIS DOES NOT WAIVE: findings INSIDE the sourced file. `membudget-ledger`
    # is a shell script with its own shebang, so this hook checks it in its own right
    # on any write to it. The split is what makes that true — one file, one verdict.
    "SC1091": "a sourced file cannot be followed when the body is piped on stdin, "
    "which is how this hook invokes shellcheck (measured 2026-09-01: "
    "`-x -P scripts` on the same bytes is clean); the sourced file is "
    "gated in its own right",
}

# The shells this hook understands. A `#!` naming something else (python, perl)
# is not shell and is not this hook's business.
_SHEBANG = re.compile(r"^#!\s*(?:/usr/bin/env\s+)?(?:\S*/)?(bash|sh|dash|ksh|zsh)\b")

# ⚑ SUFFIXES ARE A HINT, THE SHEBANG IS THE AUTHORITY. A file named `foo.sh` that
# opens with a python shebang is python; a file named `configure` that opens with a
# bash one is shell. Both tests run, and the shebang wins where they differ.
SHELL_SUFFIXES = (".sh", ".bash", ".ksh", ".zsh")

# zsh is a shell shellcheck does NOT support; linting it would produce a verdict
# about a language the linter cannot read. Excluded from the file path entirely.
_SC_DIALECTS = {"bash", "sh", "dash", "ksh"}

# How long to let the linter run before treating it as unable to answer.
_TIMEOUT_S = 15

# A finding: the rule code, the line in the operator's own coordinates, the message.
Finding = tuple[str, int, str]

# Directories a tree walk never descends into.
_SKIP_DIRS = {".git", "node_modules", "__pycache__", "worktrees", ".precommit-staged"}


def _shellcheck_bin() -> str | None:
    """Return the linter's executable path, or None when it cannot be found.

    ⚑ AN ABSENT LINTER IS AN UNKNOWN, not a clean bill. PATH first (a repo may
    install shellcheck by apt, or run in CI with no mise), then the mise shim, which
    is where this machine actually keeps it.
    """
    for d in os.environ.get("PATH", "").split(os.pathsep):
        if not d:
            continue
        candidate = Path(d) / SHELLCHECK
        if os.access(candidate, os.X_OK):
            return str(candidate)
    if os.access(_MISE_SHIM, os.X_OK):
        return str(_MISE_SHIM)
    return None


def _shellcheck_available() -> bool:
    """Report whether a linter can be found at all."""
    return _shellcheck_bin() is not None


def _findings_of(raw: object) -> list[Finding]:
    """Convert shellcheck's parsed JSON comments into findings, dropping EXCLUDEs.

    ⚑ `object` IS THE HONEST TYPE OF PARSED JSON; `Any` IS THE DISHONEST ONE. Every
    level is narrowed with a real runtime `isinstance` before it is read, so a
    shellcheck output shape this code does not expect yields NO findings rather than a
    wrong verdict — and a wrong verdict from a gate is worse than no verdict, because
    it is believed.
    """
    if not isinstance(raw, dict):
        return []
    comments = raw.get("comments")
    if not isinstance(comments, list):
        return []
    out: list[Finding] = []
    for entry in comments:
        if not isinstance(entry, dict):
            continue
        code = f"SC{entry.get('code')}"
        if code in EXCLUDE:
            continue
        line = entry.get("line")
        message = entry.get("message")
        out.append(
            (
                code,
                line if isinstance(line, int) else 0,
                message.strip() if isinstance(message, str) else "",
            )
        )
    return out


def _run_shellcheck(script: str, shell: str = "bash") -> list[Finding] | None:
    """Return shellcheck's findings over one script body, or None for UNKNOWN.

    None means the linter could not render a verdict at all (absent, crashed,
    unparseable output) and the caller must allow; an empty list means
    MEASURED-CLEAN and is a different fact entirely.

    ⚑ THESE TWO STATES ARE NOT INTERCHANGEABLE, and collapsing them is the
    `success-state-can-be-byte-identical-to-failure-state` defect: "no findings"
    and "could not look" both render as an empty result if the caller is careless,
    and the second would then read as a clean bill of health.
    """
    binary = _shellcheck_bin()
    if binary is None:
        return None
    try:
        # ⚑ THE S603 EXEMPTION IS IN `pyproject.toml`, KEYED TO THIS FILE — not a
        # `noqa`. A line directive travels with the code into every adopting tree and
        # asserts substrate's rule set there; summit measured that this exact directive
        # made three shared hooks unwritable under their narrower config, reported as
        # `RUF100 Unused noqa directive (non-enabled: S603)`. A config entry stays home.
        proc = subprocess.run(
            [binary, f"--shell={shell}", "--format=json1", "-"],
            input=script,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    try:
        parsed: object = json.loads(proc.stdout)
    except ValueError:
        return None
    return _findings_of(parsed)


# --------------------------------------------------------------------------
# Bash tool command strings
# --------------------------------------------------------------------------

# ⚑ A BASH-TOOL COMMAND IS A FRAGMENT; SHELLCHECK LINTS A SCRIPT. Handing it a
# bare fragment earns SC2148 ("no shebang") on every single command — a finding
# about the WRAPPER's shape, not about the operator's shell. So a shebang is
# prepended, and its line MUST then be subtracted back out of every reported line
# number, or every finding points one line past where the operator can see it.
_PREAMBLE = "#!/usr/bin/env bash\n"
_PREAMBLE_LINES = _PREAMBLE.count("\n")

# ⚑ QUOTE THE TAG; DO NOT DELETE THE BODY. Deleting a heredoc body removes the
# terminator, and shellcheck then reports SC1044/SC1072 ("couldn't find end token",
# "here document was not correctly terminated") — a false positive INTRODUCED by the
# fix for the first one. Measured 2026-08-28.
#
# In bash, a QUOTED tag means the body is literal: no parameter expansion, no command
# substitution. shellcheck honours that and stops linting the contents — so quoting
# the tag says exactly what is true ("this body is data") while leaving the document
# structurally intact. The body is untouched, so LINE NUMBERS for any finding after
# the heredoc stay correct, which deletion would also have broken.
#
# ⚑ ONLY THE TAG IS REWRITTEN, AND ONLY WHEN UNQUOTED. An already-quoted tag is left
# alone. This narrows what counts as shell; it does not exempt anything that WAS
# shell — an operator after the heredoc still lints, and a heredoc into an
# interpreter is `hook_no_chaining`'s refusal, not this hook's.
_HEREDOC_TAG = re.compile(r"(<<-?)(\s*)([A-Za-z_][A-Za-z0-9_]*)")


def _quote_tag(m: re.Match[str]) -> str:
    """Return one heredoc redirection with its tag quoted.

    ⚑ A NAMED FUNCTION RATHER THAN A LAMBDA, BECAUSE THE LAMBDA WAS UNTYPED. `re.sub`
    takes a `Callable[[Match], str]`, and an inline lambda gets no annotation, so the
    strict bar reads the whole substitution expression as untyped. Naming it is the
    smallest change that makes the callable's contract checkable — and it gives the
    transformation somewhere to say what it does.
    """
    return f"{m.group(1)}{m.group(2)}'{m.group(3)}'"


def _neutralize_heredoc_bodies(cmd: str) -> str:
    """Quote every unquoted heredoc tag, so its body reads as data to the parser."""
    return _HEREDOC_TAG.sub(_quote_tag, cmd)


def analyze_command(cmd: str) -> list[Finding] | None:
    """Return findings over a Bash-tool command string, or None for UNKNOWN.

    ⚑ A HEREDOC BODY IS DATA, AND LINTING IT AS SHELL IS A MEASURED FALSE POSITIVE.
    Claude Code ships no commit tool, so every multi-line commit message goes
    through a heredoc — and a message containing a `$word` or a backtick earns
    SC2154 ("referenced but not assigned") and SC2006 ("use the modern substitution
    form") about ENGLISH PROSE. Measured 2026-08-28 while building this hook, on a
    commit message of exactly the shape this repo writes daily.

    ⚑ NOT an EXCLUDE entry: SC2154 and SC2006 are CORRECT about real shell, and
    waiving them globally would blind the hook to the genuine defect. The right
    cut is narrowing what counts as shell, not weakening the rule set.
    """
    if not cmd.strip():
        return []
    found = _run_shellcheck(_PREAMBLE + _neutralize_heredoc_bodies(cmd))
    if found is None:
        return None
    # ⚑ REPORT AGAINST THE OPERATOR'S OWN OFFSETS, not the wrapper's. The
    # preamble is this hook's private machinery and must be invisible in the
    # verdict; a line number that silently counts a line the operator never
    # wrote is a measurement reported in the wrong coordinate system.
    return [(code, max(1, line - _PREAMBLE_LINES), msg) for code, line, msg in found]


# --------------------------------------------------------------------------
# Written shell files
# --------------------------------------------------------------------------


def shell_dialect(path: str, content: str) -> str | None:
    """Return the shell dialect shellcheck can read for this file, else None.

    The shebang is authoritative; the suffix is the fallback for a file that has
    no shebang at all (a sourced fragment, a drop-in).
    """
    text = content.lstrip("﻿")
    m = _SHEBANG.match(text)
    if m:
        dialect = m.group(1)
        return dialect if dialect in _SC_DIALECTS else None
    # ⚑ A NON-SHELL SHEBANG IS AN ANSWER, NOT A MISS — and reading it as a miss is
    # how the suffix gets a second vote it must not have. `_SHEBANG` matches only
    # SHELL interpreters, so a python shebang fails it exactly as a file with no
    # shebang at all does; falling through to the suffix test then lints `x.sh`
    # (really python) as bash. The presence of ANY shebang settles the question —
    # the suffix is consulted only when the file declares nothing.
    if text.startswith("#!"):
        return None
    if path.endswith(SHELL_SUFFIXES):
        # a suffix-identified fragment with no shebang: bash is the house default
        return None if path.endswith(".zsh") else "bash"
    return None


def analyze_file(path: str, content: str) -> list[Finding] | None:
    """Return findings over post-edit file content, [] when not shell, or None."""
    dialect = shell_dialect(path or "", content or "")
    if dialect is None:
        return []  # not shell — not this hook's business
    return _run_shellcheck(content, shell=dialect)


def _text_of(value: object) -> str:
    """Return `value` when it is a string, else an empty string."""
    return value if isinstance(value, str) else ""


def post_edit_content(tool_name: str, tool_input: dict[str, object]) -> tuple[str, str | None]:
    """Return the (path, content) the tool is about to put on disk, or (path, None).

    ⚑ LINT WHAT WILL EXIST, NOT WHAT WAS ASKED FOR. Write carries the whole file
    and is exact. Edit carries only a replacement fragment, and linting the
    fragment alone would report on shell torn out of its context (an `esac` with
    no `case`, a `fi` with no `if`) — so the edit is APPLIED to the on-disk file
    in memory and the RESULT is linted. If the file cannot be read, the result
    is unknown and the caller allows rather than guessing.

    ⚑ PUBLIC, BECAUSE `hook_pycheck` IMPORTS IT. It was `_post_edit_content`, and the
    sibling reached across for the private name — which ruff flags (SLF001) and is
    right to: a private name carries no compatibility promise to a second module. The
    capability is genuinely shared, so the honest fix is to make it public here rather
    than to suppress the warning there.
    """
    path = _text_of(tool_input.get("file_path")) or _text_of(tool_input.get("notebook_path"))
    if tool_name == "Write":
        return path, _text_of(tool_input.get("content"))
    if tool_name == "Edit":
        old = _text_of(tool_input.get("old_string"))
        new = _text_of(tool_input.get("new_string"))
        try:
            current = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return path, None
        if tool_input.get("replace_all"):
            return path, current.replace(old, new)
        return path, current.replace(old, new, 1)
    return path, None


# ⚑ THE OLD PRIVATE SPELLING, KEPT AS AN ALIAS FOR ONE MIGRATION STEP. `hook_pycheck`
# binds the private name at import; renaming without the alias would break it, and
# under the vendoring ruling an adopter's copy may be at either revision.
_post_edit_content = post_edit_content


# --------------------------------------------------------------------------


def _render(findings: list[Finding], subject: str) -> str:
    """Build the refusal text for a set of findings."""
    lines = [f"shellcheck: this {subject} has findings the gate refuses."]
    lines.extend(f"  {code} (line {line})  {msg}" for code, line, msg in findings)
    lines.append(
        "  ⚑ there is NO suppression path here, by design — a per-line "
        "disable\n     directive does not make the shell correct, it makes "
        "it READ as reviewed."
    )
    lines.append(
        "  fix the shell. If the rule is genuinely wrong, that is an "
        "amendment to\n     EXCLUDE in hook_shellcheck.py, under review "
        "— the enumerable side."
    )
    lines.append(f"  see https://www.shellcheck.net/wiki/{findings[0][0]}")
    return "\n".join(lines)


def _deny_payload(reason: str) -> str:
    """Render a PreToolUse deny decision as JSON.

    ⚑ THE NESTED DICT IS BUILT THROUGH TYPED LOCALS. Written inline, the INNER
    literal is inferred on its own as an untyped mapping — the call site gives it
    nothing to check against — and the strict bar refuses it. The same construct in
    the sibling cost six wrong attributions before the checker was asked to print
    the offending line.
    """
    decision: dict[str, str] = {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }
    envelope: dict[str, dict[str, str]] = {"hookSpecificOutput": decision}
    return json.dumps(envelope)


def emit(msg: str, armed: bool) -> int:  # noqa: FBT001  positional: adopters call it so
    """Deliver the verdict — the single deny/advise site, shared with the selftest.

    ⚑ `armed` STAYS POSITIONAL DESPITE THE BOOLEAN-TRAP RULE. `hook_pycheck` calls
    this across the package boundary, and under the vendoring ruling an adopter's
    copy of either file may be at a different revision — so a signature change here
    breaks any adopter whose two copies are out of step. The rule is right in general
    and the blast radius decides this instance.
    """
    if armed:
        sys.stdout.write(_deny_payload(msg) + "\n")
        return 0
    sys.stderr.write(msg + "\n")
    return 0


# ⚑ THE OLD PRIVATE SPELLING, KEPT AS AN ALIAS — same reason as `post_edit_content`.
_emit = emit


def _armed() -> bool:
    """Report whether this hook should DENY rather than advise."""
    own = os.environ.get("SHELLCHECK_HOOK_BLOCK")
    if own is not None:
        return own == "1"
    return os.environ.get("STRUCT_HOOK_BLOCK") == "1"


def _as_record(value: object) -> dict[str, object]:
    """Return `value` as a string-keyed record, or an empty one if not a mapping."""
    if not isinstance(value, dict):
        return {}
    return {str(k): v for k, v in value.items()}


def _announce_inert() -> None:
    """Say once, on stderr, that this hook is armed but linting nothing.

    ⚑ UNKNOWN IS NOT CLEAN, AND UNKNOWN IS NOT GUILTY. A silently-toothless gate must
    not be able to masquerade as a passing one — the armed-in-review/off-in-fact
    defect this ecosystem has now measured five times.
    """
    if not _armed() or os.environ.get("_SHELLCHECK_HOOK_NOTIFIED"):
        return
    os.environ["_SHELLCHECK_HOOK_NOTIFIED"] = "1"
    sys.stderr.write(
        "shellcheck hook: ARMED BUT INERT — no shellcheck found on PATH or "
        "at the mise shim,\n  so nothing is being linted. This is failing "
        "OPEN deliberately (a gate cannot deny\n  every command because its "
        "own dependency is missing).\n"
        "  Install (no root needed): mise use -g shellcheck@latest\n"
    )


def _findings_for(tool: str, tool_input: dict[str, object]) -> tuple[str, list[Finding] | None]:
    """Return the (subject, findings) for one tool call, or ("", []) when out of scope."""
    if tool == "Bash":
        return "command", analyze_command(_text_of(tool_input.get("command")))
    if tool in ("Write", "Edit", "NotebookEdit"):
        path, content = post_edit_content(tool, tool_input)
        if content is None:
            return "", []
        return "shell file", analyze_file(path, content)
    return "", []


def main() -> int:
    """Read the PreToolUse payload from stdin and refuse or allow."""
    try:
        raw: object = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError, OSError):
        return 0  # never break the session on a parse failure
    payload = _as_record(raw)
    tool = _text_of(payload.get("tool_name"))
    subject, findings = _findings_for(tool, _as_record(payload.get("tool_input")))

    if findings is None:
        _announce_inert()
        return 0
    if not findings:
        return 0
    return emit(_render(findings, subject), _armed())


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

    def report(self, suite: str, note: str = "") -> bool:
        """Print any failures and the tally; return whether every case held."""
        ok = sum(1 for _n, g, _a, _b in self.rows if g)
        for name, good, got, want in self.rows:
            if not good:
                sys.stdout.write(f"  FAIL {name}: got {got} want {want}\n")
        sys.stdout.write(f"{suite} selftest: {ok}/{len(self.rows)}{note}\n")
        return ok == len(self.rows)


def _cases_dialect(c: _Cases) -> None:
    """Add the pure-logic cases: which files are shell, and which dialect."""
    c.equal("a .sh path is shell", shell_dialect("x.sh", "echo hi"), "bash")
    c.equal("a bash shebang is shell", shell_dialect("configure", "#!/bin/bash\necho hi"), "bash")
    c.equal("a sh shebang is sh", shell_dialect("x", "#!/bin/sh\necho hi"), "sh")
    c.equal("env-style shebang is read", shell_dialect("x", "#!/usr/bin/env bash\necho hi"), "bash")
    # ⚑ THE SHEBANG OUTRANKS THE SUFFIX — a .sh file that is really python must
    # NOT be linted as shell, or the hook renders a verdict about a language it
    # cannot read.
    c.equal(
        "a python shebang in a .sh file is NOT shell",
        shell_dialect("x.sh", "#!/usr/bin/env python3\nprint(1)"),
        None,
    )
    c.equal("a plain .py file is not shell", shell_dialect("x.py", "print(1)"), None)
    c.equal(
        "zsh is not lintable by shellcheck", shell_dialect("x.zsh", "#!/bin/zsh\necho hi"), None
    )
    c.equal("a markdown file is not shell", shell_dialect("README.md", "# notes\n`echo hi`"), None)


def _cases_exclude(c: _Cases) -> None:
    """Add the cases pinning the enumerable relief set's discipline.

    ⚑ EVERY EXCLUDE ENTRY MUST CARRY A DATED WARRANT. The set began empty and an arm
    pinned that; an entry has since been EARNED (SC2329, bisected), so the arm now
    pins the DISCIPLINE rather than the emptiness — a waiver must say what was
    measured and when, or it is the suppression this hook exists to refuse.
    """
    # ⚑ THE `isinstance(v, str)` CONJUNCT IS GONE, AND ITS REMOVAL IS A REAL FINDING
    # RATHER THAN TIDYING. `EXCLUDE` is `dict[str, str]`, so the checker proved the
    # test always true (`redundant-expr`) — the arm was spending a conjunct on a
    # property the TYPE already guarantees, which reads as coverage while asserting
    # nothing. What is left is the part a type cannot state: a warrant must carry a
    # DATE and enough prose to say what was measured.
    min_warrant_length = 40
    c.holds(
        "every EXCLUDE entry carries a measured, dated warrant",
        got=all("20" in v and len(v) > min_warrant_length for v in EXCLUDE.values()),
    )
    # ⚑ THE ARM THAT THE WAIVER ACTUALLY TAKES EFFECT LIVES IN `_cases_linter`, NOT
    # HERE, AND THE MOVE IS A MEASURED FINDING RATHER THAN TIDYING. It called
    # `analyze_file` on a BASH script, so it reached `_run_shellcheck` and returned
    # None — the honest UNKNOWN — on any box without the linter, while sitting in a
    # bucket that runs unconditionally. It read as a pure-logic arm because its
    # SUBJECT is the exclude set; its WITNESS was always the linter's verdict.
    # ⚑ A case belongs to the bucket its WITNESS needs, not the one its subject
    # names — and `_DEFERRED_ARMS` was asserting a population this arm was not in.


def _cases_post_edit(c: _Cases) -> None:
    """Add the cases for reading what an edit will put on disk."""
    c.equal(
        "Write carries whole content",
        post_edit_content("Write", {"file_path": "a.sh", "content": "echo 1"}),
        ("a.sh", "echo 1"),
    )
    c.equal(
        "an unreadable Edit target yields unknown, not a guess",
        post_edit_content(
            "Edit", {"file_path": "/nonexistent/zz.sh", "old_string": "a", "new_string": "b"}
        )[1],
        None,
    )


def _cases_linter(c: _Cases) -> None:
    """Add the arms that need a real linter present."""
    expected_heredoc_lines = [4, 4]
    # T-arm: real defects are caught.
    c.holds(
        "an unquoted expansion is caught", got=bool(analyze_command("f=$1; [ $f = x ] && echo hi"))
    )
    # …and the EXCLUDE waiver actually takes effect: a trap handler on a script
    # ending in an unconditional `exit` must pass. ⚑ PAIRED DELIBERATELY WITH THE
    # T-ARM ABOVE: a suppression arm alone cannot distinguish "the waiver worked"
    # from "the linter reported nothing at all", so the case that must STILL fire
    # sits immediately beside the case that must NOT.
    c.equal(
        "a trap handler before an unconditional exit passes",
        analyze_file(
            "x.sh",
            "#!/usr/bin/env bash\nset -uo pipefail\n"
            'T="$(mktemp)"\ncleanup() { rm -f "$T"; }\n'
            "trap cleanup EXIT\necho hi\nexit 0\n",
        ),
        [],
    )
    # ⚑ THE PREAMBLE MUST BE INVISIBLE. A finding on the operator's FIRST line must
    # report as line 1, not line 2 — the arm that catches a verdict rendered in the
    # wrong coordinate system.
    f1 = analyze_command("[ $x = y ]")
    c.holds(
        "line numbers exclude the synthetic preamble",
        got=bool(f1) and all(ln >= 1 for _c, ln, _m in (f1 or [])),
    )
    c.denies(
        "SC2148 (no shebang) is not reported for a fragment",
        got=any(c2 == "SC2148" for c2, _l, _m in (analyze_command("echo hi") or [])),
    )
    # ⚑ THE HEREDOC FALSE POSITIVES, BOTH MEASURED 2026-08-28 WHILE BUILDING THIS
    # HOOK. Claude Code ships no commit tool, so EVERY multi-line commit message goes
    # through a heredoc, and `hook_no_chaining` deliberately ALLOWS that shape (it
    # fires only on a heredoc into an INTERPRETER) — so these reach this hook and
    # nothing upstream stops them.
    c.equal(
        "a commit-message heredoc body is data, not shell",
        analyze_command("git commit -F - <<EOF\nfix $thing and `x`\nEOF"),
        [],
    )
    c.denies(
        "neutralizing does not unterminate the document",
        got=any(
            c2 in ("SC1044", "SC1072")
            for c2, _l, _m in (analyze_command("cat <<EOF\nhi\nEOF") or [])
        ),
    )
    # …and the two things that must STILL fire, or the neutralizer overreached:
    after = analyze_command("cat <<EOF\nprose $v\nEOF\n[ $x = y ]")
    c.holds("real shell AFTER a heredoc still lints", got=bool(after))
    # ⚑ LINE NUMBERS SURVIVE, which is why the body is QUOTED rather than DELETED —
    # deletion would shift every subsequent finding's offset.
    c.equal(
        "a finding after a heredoc keeps its true line number",
        [ln for _c, ln, _m in (after or [])],
        expected_heredoc_lines,
    )
    c.equal(
        "an already-quoted heredoc tag is left alone",
        analyze_command("cat <<'EOF'\nprose $v\nEOF"),
        [],
    )

    # F-arm: clean shell passes. Without this the hook could deny everything.
    c.equal("clean shell passes", analyze_command('echo "hello"'), [])
    c.equal(
        "a clean file passes",
        analyze_file("x.sh", '#!/usr/bin/env bash\nset -euo pipefail\necho "hi"\n'),
        [],
    )
    c.equal(
        "a non-shell file is not linted", analyze_file("x.py", "import os\nprint(os.getcwd())"), []
    )


# The linter-dependent arms, named so an absent linter DEFERS them visibly.
_DEFERRED_ARMS = (
    "an unquoted expansion is caught",
    "a trap handler before an unconditional exit passes",
    "line numbers exclude the synthetic preamble",
    "SC2148 is not reported for a fragment",
    "clean shell passes",
    "a clean file passes",
    "a non-shell file is not linted",
)


def _selftest() -> bool:
    """Run the cases and report whether all of them hold.

    ⚑ THE ARMS THAT NEED NO LINTER RUN ALWAYS; the rest are DECLARED-SKIPPED. A
    selftest that silently shrinks when shellcheck is absent would report green over
    a population it chose after seeing the environment. So the linter-dependent arms
    are counted and NAMED as deferred, never dropped.
    """
    c = _Cases()
    _cases_dialect(c)
    _cases_exclude(c)
    _cases_post_edit(c)

    if _shellcheck_available():
        _cases_linter(c)
        note = ""
    else:
        sys.stdout.write("  DEFERRED (shellcheck absent — Phase 0 co-sign not discharged):\n")
        for name in _DEFERRED_ARMS:
            sys.stdout.write(f"    - {name}\n")
        # ⚑ AND THE FAIL-OPEN ITSELF IS AN ARM, testable precisely BECAUSE the
        # linter is missing. This is the only environment in which it can be
        # observed rather than reasoned about.
        c.equal(
            "absent linter yields UNKNOWN (None), never a false clean",
            analyze_command("[ $x = y ]"),
            None,
        )
        note = f"  ({len(_DEFERRED_ARMS)} arms deferred: shellcheck absent)"

    return c.report("hook_shellcheck", note)


# ⚑ THE ARGV READER IS SHARED, NOT COPIED. `_arg_after` lived here as one of FOUR
# byte-identical private copies (this hook, `hook_cmdparse`, `hook_no_chaining`, and
# `hook_structural_query` — whose copy had ZERO CALLERS): the
# `agda_files()`-had-four-bodies shape, which this repo has already paid for once. The
# paydown is a DELETION of the copies, not four separate conversions.
# ⚑⚑ THE COPIES WERE CAPTIVE: each read `sys.argv` directly, so no case could vary the
# input and none ever exercised an ABSENT flag — where every copy raised `ValueError`
# instead of returning the empty string its own docstring promised. The shared reader
# takes argv as a PARAMETER, which is both the fix and the testability.
# ⚑ `check_argv` DOES NOT SUBSUME IT: that VALIDATES a flag set and returns an exit
# code; this EXTRACTS a flag's VALUE. Neither is spellable in terms of the other.
#
# ⚑⚑⚑ IMPORTED LAZILY, AND ONLY ON THE CLI PATH — NEVER AT MODULE LOAD (summit
# ask-shared-hook-imports-a-package-only-its-owner-has, reopened 2026-09-20 by
# measurement). This hook is VENDORED into checkouts that do not carry the `substrate`
# package, and a module-level `from substrate.ratchet_flags import …` raised
# `ModuleNotFoundError` there AT LOAD — so the harness read empty stdout as ALLOW and the
# hook guarded nothing while reading as armed. Measured by summit's witness with
# site-packages masked (`python -S`, PYTHONPATH=<adopter root>): 2 of 14 vendored bodies,
# this one and `hook_no_chaining`. The shared reader is needed by `--check-file`,
# `--check-tree` and `--explain` ALONE; the hook path (`main`) never touches it, so the
# import belongs where its only consumers are, and an adopter without the package keeps a
# fully ARMED hook and loses only the maintainer CLI — which says so, rather than the
# hook's guard silently vanishing.
_NO_READER = (
    "shellcheck hook: this CLI mode needs `substrate.ratchet_flags`, which is not "
    "importable here ({err}). The HOOK itself is unaffected — only "
    "--check-file/--check-tree/--explain need the substrate package.\n"
)


def _arg_after(flag: str) -> str:
    """Return the argument following `flag` on the command line, or an empty string.

    ⚑ A ONE-LINE DELEGATOR to `substrate.ratchet_flags.arg_after`, kept so this hook's
    three call sites read unchanged while the BODY resolves to the shared authority —
    the same shape the `agda_files()` paydown used (one authority, N delegators). The
    import is inside the delegator so that a vendored copy without the package fails
    HERE, on a maintainer command, and never at hook load (see the note above).
    """
    try:
        from substrate.ratchet_flags import arg_after  # noqa: PLC0415 - the vendoring seam
    except ImportError as err:
        sys.stderr.write(_NO_READER.format(err=err))
        sys.exit(2)
    return arg_after(sys.argv, flag)


def _check_file(target: str) -> int:
    """Report the dialect decision and findings for one file on disk.

    ⚑ Reports the DIALECT decision and the findings SEPARATELY, because "not shell"
    and "clean shell" are different facts and one of them must never read as the
    other.
    """
    try:
        body = Path(target).read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        sys.stdout.write(f"unreadable: {e}\n")
        return 2
    dialect = shell_dialect(target, body)
    if dialect is None:
        sys.stdout.write(f"NOT SHELL — this hook would not lint {target}\n")
        return 0
    res = analyze_file(target, body)
    if res is None:
        sys.stdout.write("UNKNOWN — shellcheck unavailable; the hook fails OPEN.\n")
        return 0
    sys.stdout.write(f"dialect={dialect}  findings={len(res)}\n")
    for code, line, msg in res:
        sys.stdout.write(f"  {code}  line {line}  {msg}\n")
    return 0


def _check_tree(root: str) -> int:
    """Walk `root` and report the shell population together with its findings.

    ⚑ THE POPULATION MODE. Auditing a tree one file at a time discovers files one at
    a time, which is how a sweep reports clean over a set it never enumerated. This
    applies the SAME dialect rule the hook applies and reports the count alongside the
    findings — so "0 findings" is always accompanied by "over N files".
    """
    n_shell = n_bad = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            if p.is_symlink():
                continue
            try:
                body = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if shell_dialect(str(p), body) is None:
                continue
            n_shell += 1
            res = analyze_file(str(p), body)
            if res:
                n_bad += 1
                sys.stdout.write(f"{p}  ({len(res)})\n")
                for code, line, msg in res:
                    sys.stdout.write(f"    {code}  line {line}  {msg}\n")
    sys.stdout.write(f"shell files: {n_shell}   with findings: {n_bad}\n")
    return 1 if n_bad else 0


def _explain(probe: str) -> int:
    """Report what this hook would say about one command string."""
    res = analyze_command(probe)
    if res is None:
        sys.stdout.write("UNKNOWN — shellcheck is not installed; the hook fails OPEN here.\n")
        return 0
    for code, line, msg in res:
        sys.stdout.write(f"{code}  line {line}  {msg}\n")
    return 0


def _main() -> int:
    """Dispatch the CLI modes and return the exit code."""
    if "--selftest" in sys.argv:
        return 0 if _selftest() else 1
    if "--check-file" in sys.argv:
        return _check_file(_arg_after("--check-file"))
    if "--check-tree" in sys.argv:
        return _check_tree(_arg_after("--check-tree") or ".")
    if "--explain" in sys.argv:
        return _explain(_arg_after("--explain"))
    return main()


if __name__ == "__main__":
    sys.exit(_main())
