#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""toolmodes.py — the CROSS-TOOL MODE CENSUS, DERIVED by running each tool bare.

⚑ WHY THIS EXISTS, MEASURED.  This repo has ~6 structural tools, each with its own
mode vocabulary and NO cross-tool index.  In one session a single operator burned
FIVE tool calls guessing mode names that do not exist on the tool invoked:

  * `pycodemod.py --grep`      — `--grep` is an **agda_defs** mode
  * `pycodemod.py --argstr`    — exists nowhere (a filed-but-unbuilt gap)
  * `agda_defs.py --module`    — the real mode is `--provides`
  * `pycodemod.py --source <fn> <wrong-module>`  — right mode, wrong file
  * `sppf_db.py --verify | head`                 — refused by a hook

Each miss printed a multi-KB usage block, so the failure costs context as well as
time.  The question — *which tool actually has this mode?* — had no reader.

⚑ AND THE ANSWER MUST NOT BE A HAND-WRITTEN TABLE.  `.claude/skills/struct-tools/
SKILL.md` used to refuse to tabulate modes at all, and said why: *"the tools
enumerate themselves, and a table here would be a derived view that rots the first
time a mode is added."*  That reasoning is correct **about a table someone
maintains**, and it is kept.  So this is a TOOL that re-derives the census on every
run from the authority the skill names — **each tool's own bare output** — and never
from a list anyone maintains here.  A frozen roster of modes would be the exact
artifact this exists to prevent.

⚑ BUT REFUSING TO PUBLISH IT WAS THE WORSE OUTCOME, AND THAT IS MEASURED TOO.  The
skill told every reader *"run the tool bare and read its mode list — THAT output is
the authority"*, and `--divergence` then found THIRTY modes that dispatch and appear
in no self-description (`mdstruct` alone accepts eleven such flags; `pycodemod`
eight).  The pointer was aimed at an incomplete authority, so a reader who obeyed it
still guessed.  `--sync` closes that WITHOUT restoring the rot: it rewrites a
delimited block inside SKILL.md from this census, and `--check` (a pre-commit gate)
refuses drift.  A generated block that nobody regenerates would be worse than no
block — it reads as authoritative — which is why the pair ships together, the same
shape as `query_defs.py --compile` / `--check`.

⚑ NO FROZEN ROSTER OF TOOLS EITHER.  The population comes from the skill's
`artifact | tool` table via `hook_structural_query.routes()` — the SAME parser the
PreToolUse gate reads live, imported rather than re-derived.  A second roster beside
that table is the duplication this repo keeps paying for.

⚑ WHAT IS DERIVED, AND FROM WHERE.  Three sources, each tagged in the output, so a
reader can tell a curated claim from a parser's inference:

  usage    a line of the tool's bare output naming the tool and a `--flag`
           (the tool's own curated mode list — what a reader is told to trust)
  optlist  an argparse `options:` block, when the tool builds one
  dispatch a `--flag` the tool's AST ANCHORS TO `sys.argv` — compared against the
           argument vector, registered with `add_argument`, declared to
           `check_argv`, or a key of an all-flag dispatch table (its own module
           plus the same-directory modules it imports, never a peer tool).  NOT a
           mode claim: it is what the code can actually branch on, and the only way
           to see a mode the self-description omits.  A flag the tool merely PASSES
           to mypy/git/agda is excluded and counted separately.
           `--divergence` reads this against the other two.

    toolmodes.py --all              # every tool, every mode, derived live
    toolmodes.py --find <name|description>
                                    # WHICH TOOL has this mode — by name, by gloss,
                                    # and by prose mention.  The mode that would
                                    # have prevented all five misses above.
                                    # ⚑ AND BY FUNCTION: a capability is often a
                                    # LIBRARY FUNCTION, never exposed as a mode, so
                                    # the fourth arm searches ~2800 documented defs
                                    # across the tool corpus — 22x the 128 declared
                                    # modes — matching a DESCRIPTION against each
                                    # docstring's first line under stemming.
                                    # Measured: `literal_flags` was reinvented as
                                    # `cli_flags` after four name-keyed searches
                                    # each returned a true answer and none found it.
                                    # `--find "flag constants in a tool"` finds it.
    toolmodes.py --find <name> --top <N>
                                    # how many FUNCTION-arm rows to print; `--top 0`
                                    # prints EVERY row.  The other three arms are
                                    # unbounded and always were — they are a roster
                                    # the census owns, while this arm searches ~2900
                                    # defs and can return hundreds.
                                    # ⚑ THE PAGE WAS A SILENT CAP UNTIL 2026-08-20.
                                    # `--find _sql` reported 54 hits and printed 20
                                    # with `… and 32 more`: an EXACT count beside an
                                    # INCOMPLETE list, and no flag to finish it. A
                                    # migration reading its roster here got a number
                                    # it could trust and names it could not — the
                                    # method's limit reported as the substrate's.
    toolmodes.py --collisions       # ONE NAME, SEVERAL TOOLS — with the semantic
                                    # divergence, not just the collision
    toolmodes.py --siblings         # DIFFERENT NAMES, SIMILAR CAPABILITY — what
                                    # makes someone guess a name that exists
                                    # elsewhere.  Three enumerations: identical
                                    # argument SIGNATURE, shared argument KIND, and
                                    # shared gloss VOCABULARY.
    toolmodes.py --gaps             # a capability one tool has and a comparable
                                    # tool lacks, plus modes NAMED in a tool's own
                                    # prose and declared by nothing
    toolmodes.py --divergence       # documented vs dispatchable: a mode the bare
                                    # output claims and no literal backs, and a
                                    # flag the code carries that NO reader can see
    toolmodes.py --sync             # REWRITE the generated census block in the
                                    # skill file — everything between the
                                    # `BEGIN mode-census` markers, and nothing
                                    # outside them.  Idempotent
    toolmodes.py --deps             # what this toolkit is TESTED AGAINST — the
                                    # third-party versions its answers depend on,
                                    # MEASURED per run rather than transcribed.
                                    # ⚑ Built because a borrower running its own pinned
                                    # venv (a deliberate, reasoned exception to
                                    # `friction-borrowed-tool-needs-its-owners-interpreter`)
                                    # named the live risk in that choice: the owner's
                                    # tested set was unpublished, so a drift between its
                                    # lock and this tree was INVISIBLE to both parties.
                                    # ⚑ DERIVED, NEVER PASTED: I read three versions by
                                    # hand and nearly wrote them into a registry record,
                                    # which is the hand-quoted figure that goes stale on
                                    # the next `uv sync` with nothing to say so.
                                    # ⚑ `pandoc` is in NO lockfile on either side and is
                                    # the one most likely to diverge; omitting it would
                                    # publish an incomplete surface that LOOKS complete.
                                    # UNKNOWN is reported, never guessed
    toolmodes.py --check            # DRIFT GATE: exit 1 when that block is not what
                                    # `--sync` would write, with the difference.  A
                                    # generated block nobody regenerates reads as
                                    # authoritative while being stale
    toolmodes.py --check --autosync # on drift, regenerate the block IMMEDIATELY — and
                                    # STILL EXIT 1.  ⚑ The `still` is the design: a gate
                                    # that silently repairs what it measures is an
                                    # unconditional pass with a side effect, and the
                                    # staleness was a FACT about the tree at check time
                                    # that repairing does not un-happen.  The rewritten
                                    # block must be STAGED, so this changes the amount of
                                    # typing, never the verdict.  Opt-in and never the
                                    # default because `--check` runs in pre-commit: a
                                    # read mode that writes by default is exactly what
                                    # the mutation-intent rule forbids (no default-dry,
                                    # no default-apply — STATE one).  A failed
                                    # regeneration is reported separately from the drift
                                    # it was handling; both exit 1, and the operator
                                    # needs to tell them apart
    toolmodes.py --conventions      # the DECLARED flag contracts (`CONVENTIONS`), each
                                    # measured against the live census — STALE if no tool
                                    # accepts it, SOLO if only one does.  Plus every flag
                                    # ≥3 tools accept that NO record explains: each of
                                    # those is a DECLARE-or-CONVERGE decision, which is
                                    # the judgement a count cannot make.
                                    # ⚑ A COLLISION IS NOT A DEFECT UNTIL SOMEONE SAYS
                                    # SO.  `--collisions` reports every recurring name;
                                    # most are conventions doing their job (`--selftest`
                                    # on 34 tools) or homonyms in different domains
                                    # (`--rows` = SQL rows / markdown cells).  This is
                                    # where the distinction is DECLARED and single-homed,
                                    # so `--apply` is not re-argued in 32 files.
    toolmodes.py --declines         # readings this toolkit CONSIDERED AND REFUSED, each
                                    # with its guarding check RUN.  ⚑ AN ABSENT ARGUMENT
                                    # READS AS AN ABSENT OBJECTION: a census reports what
                                    # it FOUND and what it COULD NOT READ, and neither says
                                    # "settled — here is why", so a rejected reading is
                                    # indistinguishable from one nobody thought of and the
                                    # next reader either re-derives it or ADOPTS it because
                                    # nothing contradicts it.  Measured: an over-broad
                                    # reading travelled two messages into a peer's tree
                                    # while the bound sat certified in a sibling file.
                                    # ⚑ THE CHECK ASSERTS THE NEGATION, never comments the
                                    # refusal — a comment governs only the reader already
                                    # looking at it, while a check that FAILS IF THE
                                    # REJECTED READING BECOMES TRUE governs the claim.
                                    # Four verdicts: GUARDED / LAPSED (the record stopped
                                    # being load-bearing — NOT "the claim is now correct")
                                    # / UNCHECKED (this run could not execute it — a fact
                                    # about the machine) / UNGUARDED (`check is None`, a
                                    # comment with a record around it), each reported
                                    # separately because they need different next actions
                                    # ⚑ `--quick` is a MODIFIER on this mode (like
                                    # `--autosync` on `--check`), not a mode: it lists the
                                    # records WITHOUT running their checks.  NOT the default
                                    # — a listing that never runs makes UNGUARDED and GUARDED
                                    # indistinguishable, which is the failure this record
                                    # type exists to prevent.
    toolmodes.py --nearmiss [--list]
                                    # PAYDOWN-ONLY RATCHET (Ⓐ47 ⟡dry-spelling-ratchet):
                                    # a mutating tool whose no-write flag is not
                                    # `--dry-run`.  ⚑⚑ THE GUARD THE INCIDENT DID NOT
                                    # GET.  Three tools spelled it `--dry`, none
                                    # validated argv, and all three WROTE to the Agda
                                    # tree by default — a typo'd `--dry-run` mutated it.
                                    # That was fixed and `edit_snapshot.
                                    # NEAR_MISS_SPELLINGS` was added so the REFUSAL names
                                    # its successor — but that table is FROZEN: it holds
                                    # seven spellings someone already met, so tool #4
                                    # spelling it `--dryrun` is caught by NOTHING.  A
                                    # frozen ALLOW-list wearing a DENY-list's clothes.
                                    # ⚑ SO THE PREDICATE IS DERIVED, not looked up: edit
                                    # distance ≤2 to a DECLARED pair flag (read from
                                    # `CONVENTIONS`, never retyped), plus a PREFIX arm —
                                    # `--dry` is distance 4 from `--dry-run`, past any
                                    # threshold tight enough to avoid false positives,
                                    # and it is the incident itself.
                                    # ⚑ FIXTURE FLAGS ARE EXCLUDED BY ENCLOSING DEF, and
                                    # the first live run banked two without it
                                    # (`ratchet::--aply`, a deliberate typo in a refusal
                                    # case; `climode::--a`, a toy branch fixture) — a
                                    # permanent unpayable row in a paydown-only baseline.
                                    # ⚑ IT CANNOT SEE THE SYNONYM CLASS.  A tool spelling
                                    # no-write `--preview` or `--report` is unreachable
                                    # from here — those are not near misses, they are
                                    # different words, and only `--conventions`'
                                    # undeclared-recurrence arm surfaces them.  This
                                    # closes the TYPO class, not the SYNONYM class.
                                    # ⚑ NOT WIRED INTO PRE-COMMIT: 18 gates are red and a
                                    # nineteenth buries a real failure.  `--list`
                                    # enumerates instead of comparing.

Every mode reports `n of m`: a bare list cannot distinguish *no matches* from *no
tool read*.

⚑ IT CLAIMS NO FILE ARTIFACT, so it adds NO row to the skill's table.  Its input is
other tools' OUTPUT (a process, not a path); the one file it touches is `SKILL.md`,
which `mdstruct` already claims.  A row here would arm the `grep` gate for an
artifact kind this tool does not own — the `claims` column is the gate's authority,
not a directory of tools.  `--sync` WRITES that file, and still claims nothing: it
owns one delimited region of one document, not the `.md` kind.

⚑ AND THE WRITE IS SELF-REFERENTIAL, WHICH IS A CORRECTNESS CONSTRAINT ON ITS SHAPE.
`routes()` builds this tool's own POPULATION by reading every `|`-leading line of
that same file as an `artifact | tool` row.  So a markdown TABLE inside the block
would feed `--sync`'s output back into its input — phantom tools in the roster, the
PreToolUse gate armed for artifacts nothing claims, and no fixed point.  The block is
therefore a fenced code block, and `render_block` is pinned by a selftest that no
rendered line may begin with `|`.
"""
import ast
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scratch"))
# ⚑ THE ROUTING TABLE'S PARSER IS IMPORTED, NEVER RE-DERIVED.  `routes()` and
# `claims()` already read the skill's table for the PreToolUse gate; a second copy
# here is the `agda_files()` class (four bodies under one name, two feeding gates).
import hook_structural_query as _hsq  # noqa: E402

# ⚑ THE UNKNOWN-FLAG GUARD IS THE SHARED ONE — `ratchet.check_argv`, 31 call sites
# across 24 files. Until 2026-08-24 THIS tool did not call it: the census that measures
# whether 82 tools declare what they dispatch was itself accepting any flag typed at it.
# Not an oversight worth a shrug — it is the `fix applied to the abstraction but not to
# the member that opted out of it` class `ratchet.may_write`'s own docstring records.
import ratchet as _ratchet  # noqa: E402

# ⚑ AND THE CONCURRENT RUNNER IS THE SHARED ONE.  `rungs.execute` is what
# `run_selftests` uses — one process per member, streamed, timed.  A private
# ThreadPoolExecutor here would be the same duplication one layer down.

# A long flag as it is WRITTEN.  Single-dash flags are deliberately out of scope:
# `-h`/`-j`/`-u` are argparse/make idioms, not this toolkit's mode vocabulary.
_FLAG = re.compile(r"--[A-Za-z][A-Za-z0-9-]*")
_FLAG_EXACT = re.compile(r"^--[A-Za-z][A-Za-z0-9-]*$")
_PLACE = re.compile(r"<[^>]*>")
_WORD = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
_PYFILE = re.compile(r"[\w./-]+\.py")
# argparse's own section header, both spellings python has shipped — PLUS the
# hand-rolled spelling this toolkit uses for the same structure.
#
# ⚑⚑ THIS READ `(options|optional arguments)` UNTIL 2026-08-26, AND IT MADE A WHOLE
# FILE'S MODES INVISIBLE.  `scripts/gate_census.py` publishes a textbook two-column
# roster — `modes:` then `  --baselines  per-ratchet baseline health (…)` — and all
# FIVE of its modes (`--baselines`, `--init-absent`, `--successors`, `--sync`,
# `--check`) read as UNDOCUMENTED.  The agent that added `--init-absent` checked, saw
# its four siblings read the same way, and correctly concluded the parser — not the
# file — was the narrower thing.
#
# ⚑ THE FILE IS NOT MALFORMED; THE EXPECTATION WAS.  `parse_usage`'s arm cannot see
# these rows either, because it requires every usage line to NAME the tool
# (`gate_census.py --baselines …`), and a `modes:`-headed roster deliberately factors
# the tool name out into the header — which is the more readable form, not a defect.
# So the roster arm is the right reader for it, and the ONLY thing standing between
# them was one word in this alternation.
#
# ⚑ AND THE MISS WAS SILENT IN BOTH DIRECTIONS AT ONCE, which is why it survived:
# `--find` reported the flags as `named … declared by NO tool` / `UNDOCUMENTED`, while
# `--divergence` did not list the file AT ALL — `_invisible` subtracts
# `rec["mentioned"]`, and the unparsed roster text lands in `mentioned` as prose.  Two
# modes of one census disagreeing about one file, each internally consistent.
_OPTHEAD = re.compile(r"^(options|optional arguments|modes):\s*$")
# ⚑ THE TAIL IS `\s.*`, NOT `[ =]\S.*`.  argparse pads a short flag out to the help
# column with a RUN of spaces (`  --ping                write a value…`), so requiring
# a non-space immediately after the separator matched only the flags that happen to
# carry a metavar — i.e. it silently dropped every store_true option, which is most
# of the mode-shaped ones.
_OPTROW = re.compile(r"^  (?:-\w,\s+)?(--[A-Za-z][A-Za-z0-9-]*)(?:\s.*)?$")
_METAVAR = re.compile(r"^(?:[A-Z][A-Z0-9_]*(?:\s+|$))+")

# ⚑ STOPWORDS ARE A MEASUREMENT PARAMETER, NOT A VOCABULARY.  They exist so gloss
# similarity reflects the CAPABILITY rather than English connective tissue.  They are
# domain-free on purpose: a repo-specific word list here would rot the way the
# hardcoded suffix list did.
_STOP = frozenset(["the", "and", "or", "of", "to", "in", "for", "is", "it", "its", "that", "this", "what", "which", "who", "whom", "whose", "does", "do", "not", "are", "was", "were", "will", "would", "can", "could", "should", "may", "might", "must", "shall", "be", "been", "being", "have", "has", "had", "a", "an", "as", "at", "by", "on", "from", "into", "over", "under", "with", "without", "than", "then", "when", "where", "why", "how", "each", "every", "any", "some", "all", "both", "few", "more", "most", "other", "such", "only", "own", "same", "so", "too", "very", "just", "also", "but", "if", "else", "while", "about", "against", "between", "through", "during", "before", "after", "above", "above", "below", "out", "off", "again", "further", "once", "here", "there", "you", "your", "they", "them", "their", "we", "our", "us", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "n", "m", "per", "its", "it's"])

TIMEOUT_S = "180"

#: Per-check budget for `--declines`, in SECONDS as a number — deliberately separate from
#: `TIMEOUT_S` above, which is a STRING argument to `timeout(1)` for a different purpose.
#: ⚑ A DECLINE'S CHECK IS A REAL GATE and several are corpus walks, so 180s is too tight:
#: measured 2026-08-19 on a host in POWERSAVE, `--conventions` exceeded it and reported
#: UNCHECKED. That verdict was CORRECT — but a budget tuned on a fast machine turns a slow one
#: into a tree of unverifiable refusals, i.e. a fact about the box read as a fact about the
#: claims. Override with `SUBSTRATE_DECLINE_TIMEOUT_S` where a host is slower still.
DECLINE_TIMEOUT_S = float(os.environ.get("SUBSTRATE_DECLINE_TIMEOUT_S", "900"))


# ─────────────────────────────────────────────────────────────────────────────
# the POPULATION — read from the skill's table, never listed here
# ─────────────────────────────────────────────────────────────────────────────
def roster():
    """[(artifact, relpath)] — every tool this census covers.

    ⚑ A TABLE CELL MAY NAME MORE THAN ONE TOOL.  The Agda row is
    ``scratch/agda_lex.py` + `scratch/agda_defs.py`` — two readers for one artifact
    kind.  Taking the cell as a path would silently drop the second, which is the
    under-reporting shape (`run_selftests`' `HAS_ENTRY`: a real suite vanishing into
    a green number).  Every `.py` token in the cell is a tool.

    ⚑⚑⚑ THE ROUTING TABLE ANSWERS A DIFFERENT QUESTION THAN THIS CENSUS DOES, AND
    DERIVING ONE FROM THE OTHER MADE `--find` STRUCTURALLY BLIND.  The table maps
    ARTIFACT KIND → OWNING READER, and its `claims` column arms the PreToolUse grep
    gate; that is a routing authority.  This census asks WHICH TOOLS PUBLISH MODES —
    a different population, and a strictly larger one.  Conflating them meant a tool
    with no artifact kind to own could not appear at all, however many modes it had.
    MEASURED: `toolmodes --find locks` returned **0 hits across 93 declared modes**
    and was read — in a dispatch brief — as *"the breakdown method was never built"*,
    when `schema.py` already had `--locks`, `--activity`, `--census` and seventeen
    more.  A fact about the census's POPULATION reported as a fact about the tree.

    ⚑⚑ THE RESIDUE THAT NOTE LEFT IS WHAT THIS CLOSES.  SKILL.md recorded the store
    row as *"still partial, which is residue and not a fix"* — `scripts/sppf_*.py` are
    store tools too and stayed outside.  One row was the reachable step, not the
    closure, and the closure cannot be more rows: an artifact kind is not what makes
    something a tool.

    ⚑ SO THE SECOND HALF IS DERIVED, NEVER LISTED.  SKILL.md:106 forbids a second
    roster beside the table in as many words — *"a hardcoded suffix list anywhere else
    is exactly the frozen-roster shape the table exists to retire"* — so the widening
    tests a STRUCTURAL property instead: a module in a tool directory that (a) has a
    CLI entry point and (b) PUBLISHES a usage line naming itself and a `--flag`.
    Both halves are load-bearing.  (a) alone admits every gate and codemod in
    `scripts/`; (b) is the census's own definition of a documented mode, so a module
    that publishes one IS asking to be censused.  A tool written tomorrow is covered
    the day it publishes its first mode, with nothing to update here.

    ⚑ ROUTED TOOLS KEEP THEIR ARTIFACT LABEL; derived ones carry `—`, because a tool
    that claims no artifact kind is exactly what the table could not express and the
    label would be an invention.
    """
    out, seen = [], set()
    for artifact, cell in _hsq.routes():
        for p in _PYFILE.findall(cell):
            if p in seen:
                continue
            seen.add(p)
            out.append((artifact, p))
    for p in sorted(_publishes_modes()):
        if p not in seen:
            seen.add(p)
            out.append(("—", p))
    return out


# ⚑ THE DIRECTORIES A TOOL MAY LIVE IN.  Not a roster of tools — a roster of PLACES,
# which is the thing that genuinely does not change per-tool.  `scratch/` and
# `scripts/` are this repo's tool dirs; `jea/metalanguage/` holds the store surface the
# table already routes to.
_TOOL_DIRS = ("scratch", "scripts", os.path.join("jea", "metalanguage"))


def _publishes_modes():
    """{relpath} — modules with a CLI entry point that PUBLISH at least one usage line.

    ⚑ THE SECOND CONDITION IS WHAT SEPARATES A TOOL FROM A SCRIPT, and it is the
    census's own definition rather than a new one: `parse_usage` finds a line naming
    the module and a `--flag`.  A gate that runs and exits, a codemod driven only by
    positionals, a fixture — none publish modes, none are censused.  Running every
    `scripts/*.py` bare to find out would be both slow and unsafe (several perform
    work), so the test is TEXTUAL over the source: the usage line has to be IN the
    file to be printed by it.

    ⚑⚑ ONE PUBLISHED MODE IS THE BAR, AND I FIRST SET IT AT TWO — WHICH WAS THE WRONG
    READING OF WHAT THIS CENSUS IS FOR.  At one the population goes 9 → 74 tools and the
    census 136/27 → 207/162, and I called the extra 40 entries (`⚑ NO SELF-DESCRIPTION`
    one-shot codemods, `(positional)`-only scripts) *noise burying the real ones* and
    tightened the bar to exclude them.
    ⚑ THAT INVERTED THE PURPOSE.  This census is not a curated index of blessed tools —
    it is the DISCOVERY AND CONVERGENCE surface.  The 162 undocumented modes ARE the
    paydown census (SKILL.md:143: *"a gap in that tool's self-description: WORK, not a
    capability this blesses"*), and a tool printing NO usage line is the sharpest instance
    of it, not an entry to filter out.  `(positional)` colliding seventeen ways is a real
    finding about naming convergence — exactly what a convergence instrument should
    surface — and hiding it to keep the collision list short is the tally-without-a-
    denominator move one level up: making the number pretty by shrinking the population.
    ⚑ A CENSUS THAT EXCLUDES WHAT IT CANNOT YET SEE WELL reports the boundary of its own
    coverage as the boundary of the toolkit — the frontier-as-edge error, in the
    instrument built to prevent it.  So: everything with an entry point and a published
    mode is IN, and what it fails to publish is the work.
    """
    found = set()
    for d in _TOOL_DIRS:
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for fn in os.listdir(base):
            if not fn.endswith(".py") or fn.startswith("_"):
                continue
            path = os.path.join(base, fn)
            if not _has_entry_point(path):
                continue
            try:
                src = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            # ⚑ ONE published mode admits it.  `(positional)` counts: a script whose
            # whole interface is "give me a path" still SHARES that interface with
            # sixteen others, and `--collisions` reporting so is the convergence
            # finding — the vocabulary drift this census exists to make visible.
            if parse_usage(src, fn):
                found.add(os.path.join(d, fn))
    return found


def _outside_brackets(s):
    """The part of a usage line NOT inside `[...]`, nesting-aware.

    ⚑ THIS IS THE WHOLE PARSE, AND THE NAIVE VERSION IS WRONG IN BOTH DIRECTIONS.
    `mdstruct.py --rows <file> [--table N] [--where <substr>]` has THREE `--flag`
    tokens and ONE mode: the bracketed two are options OF `--rows`.  Reading all
    three as modes invents two that no dispatch has; reading only the first token
    after the basename loses `--messages` in `transcriptstruct.py <file>
    --messages`, where a positional precedes the mode.
    """
    out, depth = [], 0
    for ch in s:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _split_gloss(seg):
    """(arguments, gloss) for the text following a tool's name on a usage line.

    ⚑ `#` IS NOT THE ONLY SEPARATOR, AND ASSUMING IT WAS EMPTIED A WHOLE TOOL.
    `pycodemod`/`mdstruct`/`agda_defs` comment their glosses; `bibstruct` does not —
    it column-aligns them (`--entries [bib]        every key, with the fields it
    carries`).  Partitioning on `#` alone gave bibstruct six modes with EMPTY
    glosses, and worse, swallowed the gloss into the argument region: `--field
    <name> [bib]   which entries set <name>` parsed as taking `<name> <name>`, so
    its signature — the thing `--siblings` and `--gaps` are computed from — was
    fabricated from prose.  The real separator is the COLUMN BREAK: `#`, or a run
    of three or more spaces after the arguments begin.

    ⚑ AND COLUMN ALIGNMENT IS NOT RELIABLE EITHER, because the tools do not hold to
    it: `bibstruct.py --mentions <key> [bib] whose PROSE names <key> — edge
    evidence` separates its gloss with ONE space.  So the third and last cut is
    GRAMMATICAL: an argument token is a `<placeholder>`, a `[bracketed]` group, a
    `--flag`, `/`, or an ellipsis, and the first token outside that grammar is where
    the prose starts.  Three cuts, earliest wins — each covers a shape the others
    miss, and the union is what stops a gloss's own `<key>` from being counted as a
    second argument.
    """
    body = seg.lstrip()
    lead = len(seg) - len(body)
    cut = len(seg)
    h = seg.find("#", lead)
    if h != -1:
        cut = h
    m = re.search(r"\s{3,}", seg[lead:])
    if m and lead + m.start() < cut:
        cut = lead + m.start()
    for tm in re.finditer(r"\S+", seg[:cut]):
        tok = tm.group(0)
        if any(c in tok for c in "<>[]") or tok.startswith("--") \
                or tok.strip("./,") == "":
            continue
        cut = tm.start()
        break
    return seg[:cut], seg[cut:].lstrip().lstrip("#").strip()


def _names(stem, line):
    """Does this line name the tool `stem` as a word (not as a substring)?

    `scratch/pycodemod.py` names it; `_pycodemod_query.py` does not.
    """
    m = re.search(r"(?<![A-Za-z0-9_])" + re.escape(stem), line)
    return m.end() if m else None


def parse_usage(text, stem):
    """{mode: {gloss, sig}} from the tool's OWN usage lines.

    A usage line is one that names the tool and is followed by its arguments; the
    gloss is the `#` comment on that line PLUS the continuation lines under it
    (every tool here wraps its rationale over several `#` lines, and the wrapped
    half is usually the part that says what the mode is *for*).

    A tool whose primary mode is POSITIONAL (`agda_defs.py <name> ...`) is recorded
    as `(positional)` rather than dropped — it is a real mode, and the one an
    operator reaches for first.
    """
    lines = text.splitlines()
    found = {}
    i = 0
    while i < len(lines):
        end = _names(stem, lines[i])
        if end is None:
            i += 1
            continue
        seg = lines[i][end:]
        code, gloss = _split_gloss(seg)
        outside = _outside_brackets(code)
        modes = _FLAG.findall(outside)
        sig = tuple(p.lower() for p in _PLACE.findall(outside))
        if not modes:
            if not sig:
                i += 1                      # a prose mention of the tool, not a usage line
                continue
            modes = ["(positional)"]
        # continuation: subsequent `#`-leading lines that do not start a new usage line
        j, parts = i + 1, [gloss.strip()]
        while j < len(lines):
            s = lines[j].strip()
            if not s.startswith("#") or _names(stem, lines[j]) is not None:
                break
            parts.append(s.lstrip("#").strip())
            j += 1
        text_gloss = " ".join(p for p in parts if p)
        for mo in modes:
            prev = found.get(mo)
            if prev is None:
                found[mo] = {"gloss": text_gloss, "sig": sig}
            else:
                # ⚑ A MODE MAY BE DOCUMENTED TWICE WITH DIFFERENT ARGUMENTS
                # (`pycodemod --attr <name>` and `--attr <Recv>.*`).  Both glosses
                # are kept: the second is where the INVERSE reading is explained,
                # and keeping only one loses half the mode.
                if text_gloss and text_gloss not in prev["gloss"]:
                    prev["gloss"] = (prev["gloss"] + " | " + text_gloss).strip(" |")
                if not prev["sig"]:
                    prev["sig"] = sig
        i = j
    return found


def bracketed_options(text, stem):
    """Flags a usage line declares INSIDE `[...]` — options of a mode, not modes.

    ⚑ DECLARED, JUST NOT AS MODES, AND CONFLATING THE TWO MANUFACTURES GAPS.
    `mdstruct --rows <file> [--table N] [--where <substr>]` declares `--table` and
    `--where`; they are correctly kept out of the mode list, but subtracting only
    the modes from a tool's prose mentions then reported both as "named by a tool
    and declared by nothing" — i.e. as filed gaps.  Eight of thirteen entries in
    that census were this artifact, which would have sent a reader building modes
    that already exist.
    """
    out = set()
    for line in text.splitlines():
        end = _names(stem, line)
        if end is None:
            continue
        code, _g = _split_gloss(line[end:])
        inside = code
        for tok in _outside_brackets(code).split():
            inside = inside.replace(tok, " ")
        out.update(_FLAG.findall(inside))
    return out


def parse_options(text):
    """{flag: gloss} from an argparse `options:` block, if the tool builds one.

    ⚑ THE TWO HALVES OF AN ARGPARSE TOOL'S BARE OUTPUT DISAGREE, MEASURED.
    `tsdbprobe` prints its docstring's curated list AND argparse's generated one;
    `--ping` is in the second and not the first.  Reading only the curated half
    reproduces the stale-index defect `pycodemod`'s own docstring records ("THIS
    LIST WAS SEVEN MODES SHORT").  Both are parsed and tagged by source.
    """
    lines = text.splitlines()
    out, i = {}, 0
    while i < len(lines) and not _OPTHEAD.match(lines[i]):
        i += 1
    i += 1
    while i < len(lines):
        line = lines[i]
        if line and not line.startswith(" "):
            break                                     # a new unindented section
        m = _OPTROW.match(line.rstrip())
        if m:
            flag = m.group(1)
            gloss = line.rstrip()[m.end(1):].strip()
            j, parts = i + 1, [gloss]
            while j < len(lines):
                s = lines[j]
                if not s.startswith("    ") or _OPTROW.match(s.rstrip()):
                    break
                parts.append(s.strip())
                j += 1
            # the METAVAR is argument syntax, not gloss: `--base BASE  store base
            # URL` describes a store URL, not a thing called BASE.
            out[flag] = _METAVAR.sub("", " ".join(p for p in parts if p))
            i = j
            continue
        i += 1
    return out


# A header that INTRODUCES a roster but is not one `parse_options` accepts.  Read as
# EVIDENCE, never as a roster: matching it says "there is a block here the parser
# declined", which is exactly the claim `unparsed` makes and no more.
_ROSTERISH = re.compile(r"^\s{0,4}([A-Za-z][A-Za-z ]{0,24}):\s*$")


def _unparsed_roster(text):
    """A WITNESS that this text carries mode rows this parser could not read, or "".

    ⚑⚑ THE WHOLE POINT IS THE DISTINCTION, NOT THE DETECTION.  `described == False`
    answers *"did this census find modes?"*, and a reader turns that into *"this tool
    documents no modes"* — a fact about the METHOD read as a fact about the SUBSTRATE.
    A false UNDOCUMENTED and a true one are indistinguishable to that reader, and the
    false one sends them to WRITE documentation that already exists.  So the census
    reports the third state explicitly: **could not parse this file's usage block**.

    ⚑ EVIDENCE, NOT INFERENCE.  It returns a witness only when the text contains BOTH
    a header-shaped line (`modes:`, `commands:`, …) AND, under it, at least two
    indented `--flag`-leading rows — i.e. a two-column roster in every respect except
    the one word this parser happened to recognise.  Absent that, it returns "" and
    the row keeps its honest NO SELF-DESCRIPTION: a tool whose bare run prints a
    selftest genuinely publishes nothing, and inventing an excuse for it would be the
    mirror defect.

    ⚑ AND IT IS DELIBERATELY NOT A SECOND PARSER.  It does not extract the modes — it
    reports that extraction FAILED and names the header it choked on, so the fix lands
    in `_OPTHEAD` (one alternation, one place) rather than accreting a parallel reader
    whose output could disagree with the real one.  A detector that quietly succeeded
    where the parser failed would give the census two answers for one file, which is
    the `agda_files()` shape this module already refuses one layer up.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = _ROSTERISH.match(line)
        if not m or _OPTHEAD.match(line.strip()):
            continue
        rows = 0
        for nxt in lines[i + 1:]:
            if not nxt.strip():
                break
            if _OPTROW.match(nxt.rstrip()) or re.match(r"^\s+--[A-Za-z]", nxt):
                rows += 1
            elif not nxt.startswith(" "):
                break
        if rows >= 2:
            return ("a `%s` block with %d `--flag` row(s) — a roster this parser "
                    "does not recognise (widen `_OPTHEAD`)" % (m.group(1), rows))
    return ""


def census_row_modes(rel):
    """{mode: rec} this census derives for ONE tool — the live read, for a case.

    ⚑ A FIXTURE PINS THE PARSER; ONLY THE LIVE FILE PINS THE CENSUS.  The `modes:`
    regression was invisible to every fixture in this suite because each fixture spelled
    a header the parser already knew.  A case that reads the real
    `scripts/gate_census.py` fails the day the roster stops being seen, which is the
    property that was missing — the same reason `bare()`'s selftest reads real tools.
    """
    text, _rc = bare([rel])[rel]
    stem = os.path.basename(rel)
    out = dict(parse_usage(text, stem))
    for fl, gloss in parse_options(text).items():
        out.setdefault(fl, {"gloss": gloss, "sig": (), "sources": {"optlist"}})
    return out


def _is_argv(node, alias=()):
    """Does this expression resolve to the process argument vector?"""
    if isinstance(node, ast.Attribute):
        return node.attr == "argv" or _is_argv(node.value, alias)
    if isinstance(node, ast.Name):
        return "argv" in node.id.lower() or node.id in alias
    if isinstance(node, ast.Subscript):
        return _is_argv(node.value, alias)
    return False


def _argv_aliases(tree):
    """Names bound, transitively, from the argument vector.

    ⚑ THE ANCHOR IS THE VECTOR, NOT THE SPELLING `sys.argv`, and pinning that took
    this file's own dogfood case to notice.  Every tool in the corpus dispatches as
    `if "--x" in sys.argv`, so a literal test for that expression looked total —
    until the census was run against THIS tool, which does `args = argv[1:]` then
    `flag = args[0]` then `flag == "--find"`, and `--find` came back UNBACKED.  A
    detector that only sees one idiom reports a different idiom as a missing
    capability: a fact about the METHOD in the shape of a fact about the tool.

    Fixpoint rather than one pass, because the chain has length: `argv → args →
    flag`, and a single sweep in source order catches only its first link.
    """
    alias = set()
    for _ in range(4):
        before = len(alias)
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            val = node.value
            if val is None or not any(_is_argv(s, alias) for s in ast.walk(val)):
                continue
            tgts = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in tgts:
                for sub in ast.walk(t):
                    if isinstance(sub, ast.Name):
                        alias.add(sub.id)
        if len(alias) == before:
            break
    return alias


def literal_flags(path, peers=()):
    """(accepted, all_literals) — the `--flag` string constants in a tool's AST.

    ⚑ NOT A MODE CLAIM — WHAT THE CODE CAN BRANCH ON.  A tool's bare output is the
    authority for what it SAYS it does; this is the authority for what a dispatch
    could possibly reach.  The gap between them is the only structural way to see a
    mode a self-description omits — and `agda_lex`'s bare output is its selftest, so
    for that tool it is the only signal at all.

    ⚑ AND A FLAG A TOOL *PASSES* IS NOT A FLAG IT *ACCEPTS* — a false positive here
    is a bug, not a caveat (the skill's own corollary).  Reading every flag-shaped
    literal as a mode credited `pycodemod` with mypy's `--ignore-missing-imports`,
    `mdstruct` with git's `--porcelain`, and `agda_defs` with the Agda pragma
    `--without-K` it SEARCHES FOR: 55 "undocumented modes", most of them another
    program's vocabulary quoted inside a subprocess argument list.

    The discriminator is ANCHORING TO `sys.argv`, which is what every tool here
    actually dispatches on (`if "--binding" in sys.argv`, measured across the
    corpus).  A flag is ACCEPTED when it is compared against the argument vector,
    registered with `add_argument`, declared to `ratchet.check_argv`, or used as a
    key in an all-flag dispatch table.  Everything else is returned in the second
    set — present, but not this tool's vocabulary.

    ⚑ ONE HOP THROUGH SAME-DIRECTORY IMPORTS, because the big tools are DECOMPOSED.
    `pycodemod.py` dispatches out of `_pycodemod_query.py`; reading only the entry
    module would report nearly every documented mode as unbacked — a defect of the
    METHOD reported as a defect of the tool.

    ⚑ BUT NEVER INTO A PEER TOOL, AND THE ROSTER IS THE DISCRIMINATOR.  `agda_lex`
    imports `agda_defs` at its entry point, so the hop credited agda_lex with all
    twelve of agda_defs' modes — reporting a NEIGHBOUR's vocabulary as this tool's
    undocumented one, which is the exact wrong-attribution the census exists to
    stop.  An implementation half is a module the routing table does NOT name; a
    module it DOES name is a tool in its own right and is censused separately.
    """
    d = os.path.dirname(path)
    stop = {os.path.basename(p) for p in peers} - {os.path.basename(path)}
    todo, seen, flags, accepts = [path], set(), set(), set()

    def _flag(n):
        return (isinstance(n, ast.Constant) and isinstance(n.value, str)
                and _FLAG_EXACT.match(n.value))

    while todo:
        p = todo.pop()
        if p in seen or not os.path.exists(p):
            continue
        seen.add(p)
        try:
            tree = ast.parse(open(p, encoding="utf-8", errors="replace").read())
        except (OSError, SyntaxError):
            continue
        alias = _argv_aliases(tree)
        for node in ast.walk(tree):
            if _flag(node):
                flags.add(node.value)
            # `"--x" in sys.argv`, `sys.argv[1] == "--x"` — the live dispatch shape
            if isinstance(node, ast.Compare):
                sides = [node.left] + list(node.comparators)
                if any(_is_argv(s, alias) for s in sides):
                    accepts.update(s.value for s in sides if _flag(s))
            if isinstance(node, ast.Call):
                fn = node.func
                nm = (fn.attr if isinstance(fn, ast.Attribute)
                      else fn.id if isinstance(fn, ast.Name) else "")
                if nm == "add_argument":                       # argparse
                    accepts.update(a.value for a in node.args if _flag(a))
                if nm == "check_argv":                         # this repo's gate guard
                    for a in node.args:
                        if isinstance(a, (ast.Set, ast.List, ast.Tuple)):
                            accepts.update(e.value for e in a.elts if _flag(e))
            # a dispatch TABLE: a dict every one of whose keys is a flag
            if isinstance(node, ast.Dict) and node.keys and all(
                    k is not None and _flag(k) for k in node.keys):
                accepts.update(k.value for k in node.keys)
            if p == path and isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = ([a.name for a in node.names]
                        if isinstance(node, ast.Import) else [node.module or ""])
                for mod in mods:
                    base = mod.split(".")[0] + ".py"
                    cand = os.path.join(d, base)
                    if base in stop or not os.path.exists(cand):
                        continue
                    # ⚑⚑ A MODULE WITH ITS OWN CLI IS A TOOL, NOT AN IMPLEMENTATION
                    # HALF — and the `peers` guard above cannot see it, because it
                    # excludes only modules the ROUTING TABLE names.  MEASURED
                    # 2026-08-18: `edit_snapshot.py` is a same-directory utility with
                    # its own `--holding`/`--list` dispatch, imported by `agda_defs`
                    # (:518), `bibstruct` (:630) and `mdstruct` (:1636) for snapshot
                    # arming — so the hop credited all three with ITS modes, and the
                    # census reported `--holding` and `--list` as three independent
                    # undocumented modes on three tools that accept neither.  Verified
                    # by running them: both fall through to the usage block, exit 2.
                    #
                    # ⚑ THE SAME DEFECT THIS FUNCTION ALREADY RECORDS FIXING for the
                    # `agda_lex` → `agda_defs` hop, arriving through the category that
                    # guard has no name for: not a peer tool, not an implementation
                    # half, but a SHARED UTILITY THAT IS ALSO A CLI.  A roster of such
                    # modules would be the frozen-roster shape; having an entry point
                    # is the structural property, so a new one is covered when written.
                    #
                    # ⚑ AND THE COST OF THE WRONG CALL IS ASYMMETRIC.  Refusing the hop
                    # into a real implementation half under-reports that tool's modes
                    # (a gap someone can see); taking it into a CLI module INVENTS modes
                    # on a tool that rejects them — and a reader who "documents" one is
                    # documenting a flag its tool does not own.
                    if _has_entry_point(cand):
                        continue
                    todo.append(cand)
    return accepts, flags


# ⚑ THE STRUCTURAL TEST, NOT A NAME LIST.  `run_selftests.HAS_ENTRY` reads the same
# two spellings for the same reason (a suite is discovered, never rostered); this asks
# the sibling question — does this module RUN, or is it only imported?
_ENTRY_RE = re.compile(r'^if\s+__name__\s*==\s*[\'"]__main__[\'"]\s*:'
                       r'|^if\s+[\'"]--\w[\w-]*[\'"]\s+in\s+sys\.argv\s*:',
                       re.MULTILINE)


def _has_entry_point(path):
    """Does this module dispatch on argv at module scope — i.e. is it a CLI?"""
    try:
        return bool(_ENTRY_RE.search(open(path, encoding="utf-8",
                                          errors="replace").read()))
    except OSError:
        return False


def _stem(w):
    """A crude English stem — enough to make `flags` and `flag` one token.

    ⚑ WITHOUT THIS THE GLOSS ARM MISSES ITS OWN MOTIVATING CASE BY ONE WORD.
    MEASURED 2026-08-17: `cli_flags` was written as a reinvention of
    `literal_flags`, and the gloss vocabularies share `tool` plus `flag`/`flags` —
    which is 2 shared tokens under stemming and **1 without**, failing the
    `>= 2` threshold the pairwise arm uses.  A capability search that cannot pair
    the reinvention it was built for is a search that reports method, not
    substrate.

    Deliberately NOT a real stemmer (no Porter, no dependency): plural `-s`/`-es`
    and `-ing`/`-ed` are the inflections a one-line capability gloss actually
    varies on.  Over-stemming would merge distinct capabilities, so the rules are
    the conservative ones and short words are left alone.
    """
    for suf, keep in (("ies", 3), ("es", 2), ("s", 1), ("ing", 3), ("ed", 2)):
        if len(w) > len(suf) + 2 and w.endswith(suf):
            if suf == "ies":
                return w[:-3] + "y"
            if suf == "s" and w.endswith("ss"):
                return w
            return w[:-keep]
    return w


def _tokens(gloss, stems=()):
    """Content words of a gloss — the capability, minus English and tool names."""
    drop = {s.replace(".py", "").lower() for s in stems}
    return {_stem(w) for w in (t.lower() for t in _WORD.findall(gloss))
            if w not in _STOP and w not in drop and not w.startswith("--")}


def _fn_glosses(paths=None):
    """[(relpath, qualname, gloss)] — the DOCSTRING FIRST LINE of every top-level def.

    ⚑ THE POPULATION `--find` WAS MISSING, MEASURED AT ~10×.  `cmd_find` searches
    128 DECLARED MODES over 9 tools; the corpus holds low-thousands of top-level
    defs (`pycodemod --dead` alone reports 352 with no caller at all).  So the
    description-keyed search covered roughly 5-10% of the functions, and a
    capability implemented as a library function rather than exposed as a mode was
    outside it by construction.

    ⚑ THE INCIDENT THIS CLOSES.  `scratch/toolmodes.py:408 literal_flags` answers
    "which CLI flags does this tool accept"; a second implementation was written as
    `cli_flags` after four well-formed searches (`--calls flags`, `--calls
    _dispatch`, `--calls cli_flags`, `--values sys.argv`) each returned a TRUE
    answer to the question typed and none surfaced it.  Every one was keyed on a
    NAME — and `literal_flags` is a name you only coin from the implementation's
    view.  `--find`'s gloss arm is the one existing description-keyed mechanism;
    it missed only because a function is not a mode.

    ⚑ FIRST LINE, NOT THE WHOLE DOCSTRING, and that is the same choice a mode's
    gloss already makes.  A full docstring in this corpus carries paragraphs of
    incident commentary — the ⚑ notes — whose vocabulary is about the DEFECT, not
    the capability, and matching on it would pair functions that share a failure
    story rather than a job.  Private helpers (leading `_`) are kept: `_argv_aliases`
    is exactly the kind of capability a reader needs to find before rebuilding it.
    """
    import ast as _ast
    out = []
    for p in (paths if paths is not None else _tool_py()):
        try:
            tree = _ast.parse(open(p, encoding="utf-8", errors="replace").read())
        except (OSError, SyntaxError):
            continue
        rel = os.path.relpath(p, ROOT)
        for node in tree.body:
            if not isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
                continue
            doc = _ast.get_docstring(node) or ""
            if not doc.strip():
                continue
            out.append((rel, node.name, doc.strip().split("\n")[0].strip()))
    return sorted(out)


def _tool_py():
    """Every Python file in the TOOL corpus — the population `_fn_glosses` reads.

    ⚑ NOT `roster()`, WHICH IS THE 9 ROSTERED TOOLS.  The reinvention this exists
    to catch lived in `_pycodemod_query.py` — an implementation module behind a
    rostered tool, not a rostered tool itself — so scoping to the roster would
    reproduce the miss one layer down.
    """
    out = []
    for d in ("scratch", "scripts", os.path.join("jea", "metalanguage")):
        base = os.path.join(ROOT, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirs, files in os.walk(base):
            if os.sep + "." in dirpath or "estate" in dirpath:
                continue
            for fn in sorted(files):
                if fn.endswith(".py"):
                    out.append(os.path.join(dirpath, fn))
    return sorted(out)


# ─────────────────────────────────────────────────────────────────────────────
# the CENSUS
# ─────────────────────────────────────────────────────────────────────────────
def _argparse_help(tree):
    """The `options:` block argparse WOULD render, reconstructed from `add_argument`.

    ⚑ THE SHAPE IS `parse_options`' INPUT, not argparse's exact output. That parser wants
    two-space-indented `  --flag  gloss` rows under an `options:` header, and that is all it
    reads — so this emits precisely those rows and nothing else. Reproducing argparse's
    wrapping, metavars and column alignment would be re-implementing a formatter in order to
    re-parse it, which is the round trip this whole change exists to delete.

    ⚑ MEASURED COVERAGE: 183 of 251 `add_argument` call sites in this corpus pass `help=`
    (`pycodemod --forwards add_argument help`). The other 68 render an EMPTY gloss under
    argparse too, so nothing is lost — an absent `help=` was never text this census could read.
    """
    rows = []
    # ⚑⚑ A THIRD DECLARATION SHAPE, FOUND BY THE REGRESSION THIS CHANGE CAUSED. `--widest`
    # went from documented to UNDOCUMENTED on the first static run, because `schema.py` builds
    # its usage block from a module-level `_MODES = (("--flag", "gloss"), …)` tuple rather than
    # from `__doc__` or from argparse. Launching the tool rendered that list; reading only the
    # docstring does not.
    #
    # ⚑ THAT IS STRUCTURED DATA AND IS THE BEST OF THE THREE SHAPES — a declared pair list
    # cannot drift from what dispatches the way a hand-written usage paragraph can. So it is
    # read HERE rather than treated as a gap: any module-level tuple/list whose elements are
    # 2-tuples of (flag-literal, string) is a mode roster, matched structurally so a second
    # tool adopting the shape is covered without being named.
    for node in ast.walk(tree):
        if isinstance(node, (ast.Tuple, ast.List)):
            pairs = [e for e in node.elts
                     if isinstance(e, (ast.Tuple, ast.List)) and len(e.elts) == 2
                     and isinstance(e.elts[0], ast.Constant)
                     and isinstance(e.elts[0].value, str)
                     and isinstance(e.elts[1], ast.Constant)
                     and isinstance(e.elts[1].value, str)]
            # every element a (flag, gloss) pair, and at least two — one pair is a coincidence
            if len(pairs) == len(node.elts) and len(pairs) >= 2 and all(
                    p.elts[0].value.split()[0].startswith("--") for p in pairs):
                for p in pairs:
                    rows.append("  %s  %s" % (p.elts[0].value,
                                              " ".join(p.elts[1].value.split())))
            continue
        # ⚑⚑ A FIFTH SHAPE — A DICT OF FLAG → CONSTRUCTOR, the `Arm`/`Convention` model this
        # repo took from gcalculus `farm.py` (operator, 2026-08-22). `pycodemod.MODES` is
        # `{"--calls": Mode(operand="name", paths=True, scans=True, why="…"), …}` — the keys are
        # flag literals, the VALUES are `ast.Call` nodes, so the (flag, gloss) pair reader above
        # skips it entirely: it requires both halves to be string constants.
        #
        # ⚑ AND THIS IS THE RICHEST DECLARATION OF THE FIVE, which is why missing it matters
        # most. `Mode`'s own ⚑ states the principle: *"the load-bearing field is the one a
        # discriminator can CHECK"* — it declares not just the argument shape but the BEHAVIOUR
        # a branch owes (`scans=True` ⟹ owes an incomplete-scan report), and
        # `--check-contracts` gates it. A census that reads glosses and skips contracts is
        # reading the least informative half of the best-declared tool.
        #
        # ⚑ THE GLOSS IS THE `why=` KEYWORD when present — the same field `Arm` and
        # `Convention` carry, and the same one `Decline` uses. Absent, the flag still counts as
        # DECLARED: being a key in the roster IS the declaration, independent of prose.
        if isinstance(node, ast.Dict) and node.keys and all(
                k is not None and isinstance(k, ast.Constant)
                and isinstance(k.value, str) and _FLAG_EXACT.match(k.value)
                for k in node.keys) and any(
                isinstance(v, ast.Call) for v in node.values):
            for k, v in zip(node.keys, node.values):
                why = ""
                if isinstance(v, ast.Call):
                    for kw in v.keywords:
                        if kw.arg == "why" and isinstance(kw.value, ast.Constant) \
                                and isinstance(kw.value.value, str):
                            why = " ".join(kw.value.value.split())
                rows.append("  %s  %s" % (k.value, why) if why else "  %s" % k.value)
            continue
        if not (isinstance(node, ast.Call)
                and getattr(node.func, "attr", None) == "add_argument"):
            continue
        flags = [a.value for a in node.args
                 if isinstance(a, ast.Constant) and isinstance(a.value, str)
                 and _FLAG_EXACT.match(a.value)]
        if not flags:
            continue
        gloss = ""
        for kw in node.keywords:
            if kw.arg == "help" and isinstance(kw.value, ast.Constant) \
                    and isinstance(kw.value.value, str):
                gloss = " ".join(kw.value.value.split())
        for f in flags:
            rows.append("  %s  %s" % (f, gloss) if gloss else "  %s" % f)
    return ("options:\n" + "\n".join(rows)) if rows else ""


def bare(paths, jobs=None):
    """{relpath: (text, rc)} — every tool's SELF-DESCRIPTION, read from SOURCE.

    ⚑⚑⚑ THIS USED TO RUN EVERY TOOL AS A SUBPROCESS, AND THAT WAS NOT MERELY SLOW — IT
    EXECUTED THE PRE-COMMIT GATES (⟡toolmodes-static, operator 2026-08-22: *"toolmodes needs
    to operate not by launching all of the other tools. That's incredibly expensive… especially
    since some of those tools actually do work when invoked, regardless of parameters passed"*).

    MEASURED, and it pegged a 10-core box: a single `--find` invoked `scripts/gate_status.py`
    bare, which ran the gate suite, which spawned `run_selftests.py` TWICE — each fanning the
    whole suite out in parallel under `membudget` — plus `set1_ratchet_cores.py`, `worklist.py`,
    `worklist_gate.py`, and `paperkit/gate.py` forking `items.py` per row. Dozens of processes,
    per call, on a tool whose whole purpose is answering *"which tool has this mode"*.

    ⚑⚑ AND THE FIX WAS ALREADY HALF-WRITTEN IN THIS FILE. `_publishes_modes` builds the roster
    by running `parse_usage` over SOURCE, and its own ⚑ says why: *"Running every scripts/*.py
    bare to find out would be both slow and unsafe (several perform work), so the test is
    TEXTUAL over the source: the usage line has to be IN the file to be printed by it."* That
    reasoning was correct and was applied to the roster only; the census kept launching.

    ⚑ THE TWO PARSERS NEVER NEEDED A SUBPROCESS. `parse_usage` and `parse_options` are pure
    functions of TEXT. Only the text was subprocess-derived, and both halves are in the source:
      * the usage block IS the module docstring (every tool here prints `__doc__` or a `USAGE`
        built from it — that is what `_publishes_modes` already relies on);
      * the argparse `options:` block is reconstructed by `_argparse_help` from the
        `add_argument` calls the AST already exposes — the same nodes `literal_flags` reads.

    ⚑⚑ FIVE DECLARATION SHAPES, AND FOUR OF THEM WERE FOUND BY BREAKING THE FIFTH. Launching
    rendered whatever a tool chose to print, so the census never had to know HOW a tool
    declares. Reading source does, and each shape surfaced as a regression:

      1. the module `__doc__` usage block                    — the assumed one
      2. argparse `add_argument(...)`                        — reconstructed by `_argparse_help`
      3. a module-level `_MODES = (("--flag","gloss"),…)`     — `schema.py`; found when
                                                                `--widest` went UNDOCUMENTED
      4. a usage string built INSIDE `__main__`              — `agda_defs.py` keeps a 9-line
                                                                docstring and prints its real
                                                                mode list from a 1,057-line
                                                                guard; the selftest caught it
      5. a dict of flag → CONSTRUCTOR                        — `pycodemod.MODES = {"--calls":
                                                                Mode(...)}`, the `Arm`/
                                                                `Convention` model from
                                                                gcalculus `farm.py` (operator)

    ⚑ SHAPE 5 IS THE RICHEST AND WOULD HAVE BEEN THE QUIETEST MISS. `Mode` declares not just
    the argument shape but the BEHAVIOUR a branch owes (`scans=True` ⟹ owes an incomplete-scan
    report), gated by `--check-contracts`. Its own ⚑ states the principle — *"the load-bearing
    field is the one a discriminator can CHECK"* — so a census that reads glosses and skips
    contracts reads the least informative half of the best-declared tool.

    ⚑⚑ AND A DECLARED ROSTER IS A SECOND SPELLING, WHICH WANTS A GATE (operator, 2026-08-22:
    *"There needs to be a gate to keep them in sync"*). `_MODES`/`MODES` say what a tool
    CLAIMS; the `sys.argv` branches say what it DOES — the `census-keyed-on-one-spelling` shape.
    **`--divergence` is already that reader**, reporting both directions (UNDOCUMENTED: 87
    dispatched-but-undeclared; UNBACKED: 7 declared-but-not-dispatched). What is missing is
    only the enforcement: `--calls cmd_divergence` → 0 calls, reachable solely from its own
    CLI, and `--check` gates the census BLOCK's freshness rather than this divergence.
    Filed ⟡divergence-ungated; wiring it is a ratchet decision (87 is a baseline, not a
    clean-zero gate) and not part of this change.

    ⚑ `rc` IS NOW ALWAYS 0 AND THAT IS A REAL LOSS, NAMED. A launched run distinguished
    "printed a usage block" from "crashed" from "timed out"; a source read cannot. That
    distinction had ONE consumer — the `⚑ NO SELF-DESCRIPTION` label — and it is preserved
    structurally: a tool whose docstring yields no usage line still reports as undescribed.
    What is genuinely gone is `--divergence`'s ability to say a tool TIMED OUT, and the
    ⟡tools-cannot-self-describe census (four tools crash when run bare) is now the reader that
    owns that question — it is a property of the TOOL, not of this census's method.
    """
    out = {}
    for rel in paths:
        p = os.path.join(ROOT, rel)
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            out[rel] = ("", None)      # unreadable: UNMEASURED, not mode-less
            continue
        doc = ""
        try:
            _t = ast.parse(src)
            doc = ast.get_docstring(_t) or ""
            # ⚑⚑ A FOURTH SHAPE, AND THE SELFTEST CAUGHT IT: the usage block need not be
            # `__doc__`. `agda_defs.py` keeps a 9-line module docstring and prints its real
            # mode list from inside a 1,057-line `__main__` guard — so a docstring-only read
            # lost `--grep` and `--provides`, both of which the tool genuinely accepts
            # (verified by running it). The live case pinned exactly that and failed.
            #
            # ⚑ SO EVERY MODULE-LEVEL STRING CONSTANT THAT LOOKS LIKE A USAGE BLOCK IS FED TO
            # `parse_usage`, not just the docstring. The parser already discriminates — it
            # requires a line naming the tool AND a `--flag` — so handing it extra text costs
            # nothing and a prose paragraph mentioning a flag was never going to match.
            for _n in ast.walk(_t):
                if isinstance(_n, ast.Constant) and isinstance(_n.value, str) \
                        and "\n" in _n.value and "--" in _n.value \
                        and _n.value is not doc:
                    doc += "\n" + _n.value
            # ⚑⚑⚑ A FIFTH SHAPE OF SHAPE FOUR, AND THE `"\n" in _n.value` TEST IS EXACTLY WHAT
            # HID IT. `agda_defs.py` prints its roster as ONE triple-quoted block, so a
            # multi-line-constant test finds it; `sppf_db.py` prints the SAME KIND of roster as
            # ~40 consecutive one-line `print("  --flag  gloss")` calls, and every one of those
            # constants is single-line — so the filter above excluded the whole block and the
            # census read ZERO usage-declared modes for that tool.
            #
            # ⚑⚑ MEASURED 2026-08-23, AND THE MISREADING IT PRODUCED IS THE POINT: `toolmodes
            # --find promote-core` answered *"named in scripts/sppf_db.py's own output, declared
            # by NO tool"* — BOTH CLAUSES TRUE AND JOINTLY ABSURD. `--promote-core` is run by
            # `make` on every module of a full build. The tool published its modes; this reader
            # could not see the FORM they were published in, and reported that as the tool
            # failing to declare them. A fact about the METHOD, rendered as a fact about the
            # SUBSTRATE — the same shape as the `--calls emit` census that missed `_emit_one`.
            #
            # ⚑ SO THE STRING'S OWN SHAPE IS THE WRONG DISCRIMINATOR; what matters is that the
            # ARGUMENT OF A `print` CAN BE A USAGE LINE. `parse_usage` still discriminates
            # (a line must NAME the tool AND carry a `--flag`), so feeding it every printed
            # literal costs nothing — the same argument the block above already makes for
            # feeding it every module-level constant.
            # ⚑⚑ A REFUSAL IS NOT A DECLARATION, AND THE FIRST CUT OF THIS LOOP CONFLATED
            # THEM. `schema.py` refuses a half-stated mutation with `print("schema.py
            # --coverage --reap: state --dry-run OR --apply …")`, and reading that as a usage
            # line promoted `--reap` to a TOP-LEVEL MODE of `schema.py` — precisely the defect
            # that file's `_MODES` block records having already fixed once (`--emit`/`--reap`
            # are `opts` OWNED by `--coverage`; as bare keys they "match no argv token"). A
            # census that re-derives a retired misreading from a new source is worse than one
            # that misses the modes, because the roster now ASSERTS a mode nothing dispatches.
            #
            # ⚑ THE DISCRIMINATOR IS THE `:` SEPARATOR, WHICH IS WHAT MAKES IT AN ERROR LINE —
            # `tool.py <modes>: <what went wrong>` is this toolkit's refusal shape, distinct
            # from `tool.py --mode <args>   <gloss>` (gloss separated by 3+ spaces or `#`,
            # which is what `_split_gloss` already parses). Lines printed to STDERR are
            # excluded for the same reason: a tool describes itself on stdout and complains
            # on stderr, so the stream is itself a declaration/refusal signal.
            for _n in ast.walk(_t):
                if not (isinstance(_n, ast.Call) and isinstance(_n.func, ast.Name)
                        and _n.func.id == "print"):
                    continue
                if any(isinstance(_k.value, ast.Attribute)
                       and _k.value.attr == "stderr" for _k in _n.keywords
                       if _k.arg == "file"):
                    continue
                for _a in _n.args:
                    if isinstance(_a, ast.Constant) and isinstance(_a.value, str) \
                            and "--" in _a.value and "\n" not in _a.value \
                            and not re.match(r"\s*\S+\.py\b[^:]*:", _a.value):
                        doc += "\n" + _a.value
        except SyntaxError:
            pass
        opts = ""
        try:
            opts = _argparse_help(ast.parse(src))
        except SyntaxError:
            pass
        out[rel] = (doc + ("\n\n" + opts if opts else ""), 0)
    return out


def census(jobs=None):
    """[(artifact, relpath, record)] in table order — the whole derived picture.

    record = {modes: {mode: {gloss, sig, sources}}, mentioned: set, literal: set,
              rc: int, described: bool}
    """
    pop = roster()
    outs = bare([rel for _a, rel in pop], jobs=jobs)
    rows = []
    for artifact, rel in pop:
        text, rc = outs.get(rel, ("", None))
        stem = os.path.basename(rel)
        modes = {}
        for mo, rec in parse_usage(text, stem).items():
            modes[mo] = dict(rec, sources={"usage"})
        for fl, gloss in parse_options(text).items():
            if fl in modes:
                modes[fl]["sources"].add("optlist")
                if gloss and gloss not in modes[fl]["gloss"]:
                    modes[fl]["gloss"] = (modes[fl]["gloss"] + " | " + gloss).strip(" |")
            else:
                modes[fl] = {"gloss": gloss, "sig": (), "sources": {"optlist"}}
        opts = bracketed_options(text, stem)
        mentioned = {f for f in _FLAG.findall(text)} - set(modes) - opts
        accepts, lits = literal_flags(os.path.join(ROOT, rel),
                                      peers=[r for _x, r in pop])
        rows.append((artifact, rel, {
            "modes": modes,
            "mentioned": mentioned,
            "options": opts,
            "accepts": accepts,
            "literal": lits,
            "rc": rc,
            # ⚑ THE HONEST PREDICATE.  A tool whose bare output yields no usage line
            # has NO SELF-DESCRIPTION — a fact about that tool, reported as such.
            # Falling back to a hand-written list here is the defect this file exists
            # to prevent, so there is no fallback.
            "described": bool(modes),
            # ⚑⚑ AND `described == False` IS TWO OPPOSITE FACTS UNDER ONE NAME, WHICH IS
            # THE COLLAPSE THIS TOOLKIT HAS NOW FIXED THREE TIMES (ABSENT-vs-EMPTY in
            # `gate_census`, "no consumer found"-vs-"no consumer exists" in the standing
            # rule, `--calls emit` missing `_emit_one`).  A tool that PUBLISHES NOTHING and
            # a tool whose publication THIS PARSER COULD NOT READ render identically —
            # and only the first is a fact about the substrate.  The second is a fact
            # about the METHOD, and it is the one that must name its own successor.
            #
            # ⚑ MEASURED, AND IT IS WHY THIS FIELD EXISTS: `scripts/gate_census.py`
            # published a five-row `modes:` roster and read as UNDOCUMENTED on every one,
            # because `_OPTHEAD` spelled only argparse's two headers.  The reader that
            # noticed was a HUMAN AGENT comparing a new mode against its four siblings —
            # nothing in this census could say "I failed to parse this".  Now it can.
            "unparsed": _unparsed_roster(text) if not modes else "",
            # ⚑ Ⓜ10 — THE TOOL'S OWN SOURCE, so a FIXTURE declaration can live in the
            # file that owns the fixture rather than in a roster here. Read from disk
            # rather than threaded out of `literal_flags` because that helper returns
            # flags, not text, and widening its contract to carry the source would make
            # every caller pay for one consumer. Best-effort: an unreadable tool yields
            # "" and simply declares no fixtures, which is the correct default — a
            # fixture is an EXEMPTION, and a read error must never grant one.
            "source": _read_source(os.path.join(ROOT, rel)),
        }))
    return rows


def _read_source(path):
    """The tool's source text, or "" — for reading in-file declarations.

    ⚑ FAILURE YIELDS "", AND THE DIRECTION MATTERS. Every consumer of this treats an
    empty source as "declares nothing", so an unreadable file loses its exemptions
    rather than gaining them. A reader that failed OPEN would let an I/O error silently
    clear a tool's debt.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def _index(rows):
    """{mode: [(relpath, record)]} — the inverted census."""
    idx = {}
    for _a, rel, rec in rows:
        for mo in rec["modes"]:
            idx.setdefault(mo, []).append((rel, rec))
    return idx


def _one_line(s, width=88):
    s = " ".join(s.split())
    return s if len(s) <= width else s[:width - 1] + "…"


def _universal(rows):
    """Flags MOST rostered tools accept — a convention, not a per-tool mode.

    ⚑ MEASURED, NOT DECLARED IN A LIST.  `--selftest` is the harness contract
    `run_selftests` invokes (`python <path> --selftest`); reporting it once per tool
    put seven identical rows in a census whose whole value is that a row means
    something.  A hardcoded "ignore these" set would be the frozen vocabulary this
    toolkit keeps retiring; a measure over the roster moves on its own when a
    convention is added or dropped.

    ⚑⚑ THE INTERSECTION WAS PASSING ON BORROWED EVIDENCE, AND CLOSING A LEAK EXPOSED
    IT.  `--selftest` is spelled as an argv compare in five tools and declared to
    argparse in `tsdbprobe`, so a strict intersection over `accepts` should never have
    held — it did only because the one-hop walk leaked a CLI sibling's flags into every
    importer.  Fixing that (`_has_entry_point`) correctly dropped `--selftest` from
    three tools' `accepts`, and the intersection then reported ZERO conventions and six
    duplicate rows.

    ⚑ A SHARE THRESHOLD IS THE WRONG SHAPE, and the fixture below says why: `--hidden`
    on 2 of 3 tools is a MAJORITY and is emphatically not a convention.  Coincident
    modes and a convention are not separable by counting — a tool convention exists
    because something INVOKES it, which is a structural fact, not a popularity one.

    ⚑ SO THE TEST IS THE HARNESS CONTRACT.  `--selftest` is universal because
    `run_selftests` runs `python <path> --selftest` against every discovered suite;
    that is the same authority `run_selftests.HAS_ENTRY` reads, so the two cannot
    drift.  A convention added tomorrow is covered by naming its invoker, never by
    editing a list here — and the UNION with the intersection keeps the measured arm
    alive for any convention that really is unanimous.
    """
    if not rows:
        return set()
    measured = set.intersection(*[rec["accepts"] for _a, _r, rec in rows])
    return measured | {f for f in HARNESS_CONTRACTS
                       if any(f in rec["accepts"] for _a, _r, rec in rows)}


class Convention:
    """One flag whose MEANING is shared across tools, and the invoker that makes it so.

    ⚑⚑⚑ A CONVENTION IS NOT A NAME THAT RECURS; IT IS A NAME SOMETHING INVOKES.
    `--selftest` is a convention because `run_selftests` dispatches
    `python <path> --selftest` against every discovered suite — the flag is a property
    of the RUNNER.  `--top` recurs across four tools and is NOT one: nothing invokes it,
    the four just chose the same word.  Counting cannot separate those (a `--hidden` on
    2 of 3 tools is a majority and emphatically not a convention), which is why this
    carries the invoker rather than a threshold.

    ⚑⚑ MODELLED ON gcalculus `farm.py`'s `Arm`, and the load-bearing field is the same
    one.  An F-arm declares the MESSAGE its mutation must provoke, because *"it went red"
    is not evidence — "it went red HERE, saying THIS" is*.  A convention declares the
    INVOKER that makes the flag shared, because "many tools accept it" is not evidence —
    "this runner dispatches it against every tool" is.  Both replace a popularity signal
    with a structural one, and both make the claim falsifiable: an `Arm` that stops
    biting is VACUOUS, a `Convention` whose invoker stops invoking is STALE.

    ⚑ SINGLE-HOMED SO REUSE IS DECLARED RATHER THAN COINCIDENTAL.  The census, the
    collision report and any future gate read the same records, so "is `--apply` a
    convention?" has one answer.  A second list beside this one is the frozen-roster
    shape the whole census exists to retire.

    Fields, deliberately mirroring `Arm(key, file, find, replace, expect, why)`:

      flag      the spelling, e.g. `--selftest`
      invoker   the module that DISPATCHES it across tools — the structural warrant
      contract  what a tool accepting it PROMISES; the shared semantics, one line
      why       the argument: what recurrence-without-an-invoker would look like, and
                what a reader loses if this is read as N per-tool modes instead of one
    """

    __slots__ = ("contract", "flag", "invoker", "why")

    def __init__(self, flag, invoker, contract, why):
        self.flag, self.invoker = flag, invoker
        self.contract, self.why = contract, why


# Each entry is a flag whose meaning is OWNED here rather than re-argued per tool.
# Adding one is how a recurring flag earns the claim that it is a shared contract.
CONVENTIONS = [
    Convention(
        flag="--selftest",
        invoker="scripts/run_selftests.py",
        contract="run this tool's guarded cases; exit 0 iff all pass, and emit a typed "
                 "`rungs.record` rather than prose.",
        why="the runner DISCOVERS suites (`HAS_ENTRY` + a `_selftest` body) and dispatches "
            "`python <path> --selftest` at each — so the flag is the runner's, and a tool "
            "spelling it via argparse instead of an argv compare does not make it that "
            "tool's own invention.  Reported per-tool it put 27 identical rows in a census "
            "whose whole value is that a row MEANS something.",
    ),
    Convention(
        flag="--apply",
        invoker="(none — the writers' shared discipline, not a dispatcher)",
        contract="PERFORM the change. ⚑ MUTUALLY EXCLUSIVE WITH `--dry-run` AND ONE IS "
                 "REQUIRED: a mutating tool invoked with NEITHER must REFUSE, never guess.",
        why='⚑⚑ NO DEFAULT IN EITHER DIRECTION (operator, 2026-08-18: *"no default-dry, no '
            'default-apply, only explicit behavior"*).  A default-dry tool silently does '
            "nothing when the caller meant to write; a default-apply tool silently writes "
            "when the caller meant to look.  BOTH failures are silent, and which one you get "
            "is a property of whichever tool you happened to invoke — so the caller must "
            "carry the decision, not the tool's history.\n"
            "⚑ 32 tools accept `--apply` with identical semantics, which is why declaring it "
            "here stops a 33rd inventing `--write` or `--fix`.  But the CONTRACT is the pair, "
            "not the flag: `--apply` XOR `--dry-run`, exactly one, always stated.  Today most "
            "members default to reporting — that is a DEFAULT, and this record says it is the "
            "wrong shape.  → ⟡explicit-mutation",
    ),
    Convention(
        flag="--quiet",
        invoker="the pre-commit hook (gates run under it)",
        contract="print only on FAILURE; a passing run says nothing.",
        why="gate-shaped tools only.  ⚑ `ratchet.check_argv` records what a mis-spelling "
            "costs here: a typo'd `--queit` degraded FIVE gates to verbose-but-passing, "
            "all exit 0 — so this flag's contract is load-bearing for whether a green "
            "build means anything.",
    ),
    Convention(
        flag="--dry-run",
        invoker="scripts/ratchet.py (UNIVERSAL_FLAGS, merged into every gate's known-set)",
        contract="report what WOULD change and change nothing. ⚑ MUTUALLY EXCLUSIVE WITH "
                 "`--apply` AND ONE IS REQUIRED: neither stated is a REFUSAL, not a default.",
        why="⚑ IT IS `--apply`'s MIRROR AND THE PAIR IS THE CONVENTION — not either flag "
            "alone.  `ratchet.UNIVERSAL_FLAGS = {\"--dry-run\"}` merges it into every gate's "
            "known-set so no caller re-declares it and none can be missing one — that merge "
            "IS this contract, already single-homed, and it is the mechanism ⟡explicit-"
            "mutation should extend rather than duplicate.\n"
            "⚑⚑ AND `--dry` IS THE SAME CONTRACT MISSPELLED, MEASURED: `paydown.py:251`, "
            "`scope_fix.py:771` and `telescope_migrate_gen.py:86` each write by default and "
            "suppress on `--dry`; none accepts `--dry-run`, and NONE calls "
            "`ratchet.check_argv`, so a typo'd `--dry` in any of them silently WRITES.  "
            "That is a CONVERGE, not a second declaration — recorded here rather than "
            "given its own record, because giving the misspelling a `Convention` of its own "
            "is exactly how a split becomes permanent.  → ⟡dry-converge",
    ),
    Convention(
        flag="--sandbox",
        invoker="jea/metalanguage/store.py::sandbox_connect (1 def, 30 call sites)",
        contract="run against the THROWAWAY tenant. ⚑ THE TENANT MUST BE STATED: where live "
                 "and sandbox could differ, a tool with neither `--sandbox` nor an explicit "
                 "live selector must REFUSE. No default tenant, in either direction.",
        why="⚑⚑ NO DEFAULT TENANT (operator, 2026-08-18: *\"I've seen many errors because "
            "something inspected sandbox when it meant to inspect the main thing. And when "
            "something modified the main thing when it meant to go to sandbox. Or when "
            'something simply forgot to care."*).  THREE failure modes, and the third is the '
            "one a default guarantees: forgetting to care is indistinguishable from choosing.\n"
            "⚑ MEASURED, BOTH DIRECTIONS.  `schema_rows._cli_connect` records `--fibre "
            "--sandbox` reporting the LIVE store's 152 cores under the sandbox's question — "
            "each mode had grown its own resolver, so WRITE modes honoured the flag while "
            "READ modes ignored it.  And this session: a plan taken through `--probe` "
            "returned `rows=124772` from the sandbox's ~4 cores against live's 93.4M, three "
            "orders of magnitude low and *looking exactly like an answer*.\n"
            "⚑ THE AUTHORITY IS `store.sandbox_connect`, a SEPARATE FUNCTION rather than a "
            "`connect(sandbox=True)` flag precisely so reaching the sandbox is deliberate at "
            "the call site — that reasoning is already in `store.py`; this record extends it "
            "from the API to the INVOCATION, where the same mistake is made by omission.  "
            "→ ⟡explicit-tenant",
    ),
    Convention(
        flag="--roundtrip",
        invoker="(none — the parsers' shared precondition)",
        contract="LOSSLESSNESS GATE: does parse→emit reproduce this artifact? Report what "
                 "changed, not merely pass/fail.",
        why="`bibstruct`, `mdstruct` and `pycodemod` each own a parser, and each must answer "
            "the same question before any transform runs.  ⚑ AND THE ANSWER DIFFERS BY "
            "ARTIFACT WITHOUT THE CONTRACT DIFFERING: libcst is lossless by construction so "
            "`pycodemod`'s is a formality that passes, while pandoc NORMALIZES so "
            "`mdstruct`'s is expected to report changes — which is exactly why the contract "
            "says *report what changed*.  A pass/fail spelling would have made the markdown "
            "arm unusable and invited a fourth name for the same precondition.",
    ),
]

# ⚑ DERIVED, NOT A SECOND LIST.  `_universal` consumes this; nothing else may keep its
# own copy.  The set-of-flags spelling is retained because every reader wants membership,
# but the RECORDS are the authority and the set is a projection of them.
HARNESS_CONTRACTS = {c.flag for c in CONVENTIONS}


class Decline:
    """One claim CONSIDERED AND REFUSED, with the check that fails if the refusal stops holding.

    ⚑⚑⚑ AN ABSENT ARGUMENT READS AS AN ABSENT OBJECTION.  A census reports what it FOUND and
    what it COULD NOT READ; neither can say *"this was considered and rejected, here is why"*.
    So a rejected reading leaves no trace, becomes indistinguishable from one nobody thought
    of, and the next reader either re-derives the question or ADOPTS the rejected reading
    because nothing contradicts it.  Measured 2026-08-19: I relayed *"`AND` IS the Kron/Schur
    elimination"* into a peer's tree; the bound existed, was certified, and sat in a sibling
    file — and the over-broad reading travelled two messages because nothing said it had
    already been refused.

    ⚑⚑ THE CHECK MUST ASSERT THE NEGATION, NOT COMMENT THE REFUSAL (linux-sources, 2026-08-19,
    from building the same thing in their tree).  A comment saying *"we considered and rejected
    the general reading"* governs only the reader already looking at it.  A check that FAILS IF
    THE REJECTED READING BECOMES TRUE governs the claim.  Their worked pair is the model:

        `and-is-schur` HOLDS at degree 2 ...
        ... and FAILS above it — a degree-2 specialisation, not an identity

    The second arm is doing the work.

    ⚑ SAME FAMILY AS `Convention` ABOVE AND gcalculus `farm.py`'s `Arm`, and the load-bearing
    field is the same one: a FALSIFIABLE DISCRIMINATOR.  An `Arm` declares the message its
    mutation must provoke; a `Convention` declares the invoker that makes a flag shared; a
    `Decline` declares the check that would go red if the refusal lapsed.  All three replace an
    assertion with something that can stop being true — and all three make their own VACUITY
    detectable: an `Arm` that stops biting is VACUOUS, a `Convention` whose invoker stops
    invoking is STALE, and a `Decline` whose check no longer runs is UNGUARDED.

    ⚑ A DECLINE IS NOT A TODO.  A missing mode is WORK; a declined reading is neither work nor
    finding — it is a SETTLED question, and the record exists so it stays settled.  Listing one
    is how a refusal becomes discoverable by a reader who does not already know to look.

    Fields, deliberately mirroring `Convention(flag, invoker, contract, why)`:

      claim     the REJECTED reading, stated as temptingly as someone would actually state it
      instead   what is true in its place, one line
      check     the command whose FAILURE would mean the refusal has lapsed — the
                discriminator.  `None` is legal and means UNGUARDED, which the census REPORTS
                rather than hides: a decline nothing checks is a comment with a record round it
      why       the argument, and what a reader loses by adopting the rejected reading
    """

    __slots__ = ("check", "claim", "instead", "why")

    def __init__(self, claim, instead, check, why):
        self.claim, self.instead = claim, instead
        self.check, self.why = check, why


#: Readings this toolkit CONSIDERED and REFUSED.  Adding one is how a settled question stops
#: being re-derived; each carries the check that would go red if the refusal lapsed.
DECLINES = [
    Decline(
        claim="a flag accepted by N tools is a CONVENTION once N is large enough",
        instead="a convention is a flag something INVOKES; recurrence is not evidence.",
        check="python3 scratch/toolmodes.py --conventions",
        why="⚑ COUNTING CANNOT SEPARATE THE TWO, AND A THRESHOLD MAKES IT WORSE.  `--top` "
            "recurs across 8 tools and is not a convention — nothing dispatches it, the eight "
            "chose the same word.  A `--hidden` on 2 of 3 tools is a MAJORITY and emphatically "
            "not one.  This was tried: a majority threshold was the first repair, and it "
            "reported zero conventions plus six duplicate rows.  Adopting the rejected reading "
            "turns a census whose rows MEAN something into a popularity table.",
    ),
    Decline(
        claim="a mutating tool given neither --apply nor --dry-run should default to dry",
        instead="it must REFUSE — no default in either direction, for mutation or for tenant.",
        # ⚑ THE CHECK MUST FAIL ONLY IF THE REFUSAL LAPSES, AND MY FIRST PICK DID NOT.
        # I chose `check_snapshot_guard --quiet`, which exits 1 because it is an UNMINTED
        # RATCHET on a blocked tree — its honest resting state, and nothing to do with whether
        # a default-dry has crept in.  A discriminator that is red for an unrelated reason is
        # VACUOUS in exactly `farm.py`'s sense: the red came from elsewhere.  `--conventions`
        # carries the mutation pair's verdict (`REQUIRED PAIRS`) and is green when the pairing
        # discipline holds, so it discriminates the thing this record is about.
        check="python3 scratch/toolmodes.py --conventions",
        why="⚑ A DEFAULT-DRY IS STILL A GUESS, AND IT IS THE ONE THAT READS AS SAFE.  Operator, "
            '2026-08-18: *"no default-dry, no default-apply"*.  The unstated case is the whole '
            "population the mutation-intent ratchet measures, so giving it a default makes that "
            "census read clean forever — a defaulted run is invisible to it.",
    ),
    Decline(
        claim="`--portable` reading GREEN on a file means that file's SQL ports",
        instead="it EXPLAINs raw LITERALS; Core-built SQL is outside its population entirely.",
        check="python3 scratch/pycodemod.py --funcnames --verbatim",
        why="⚑ MEASURED: `--portable jea/metalanguage/autocorr_synth.py` reported `0 blocking "
            "site(s)` while that file raised `UndefinedFunction: group_concat` on EVERY "
            "invocation — a whole capability dark and the gate green over it.  A Core statement "
            "is never a string, so EXPLAIN has nothing to parse.  Adopting the rejected reading "
            "is how a sqlite-ism survives a migration INSIDE a tool built to catch sqlite-isms.",
    ),
    Decline(
        claim="a `func.<name>` that compiles is a function the dialect HAS",
        instead="Core passes any name through VERBATIM; compiling proves nothing about it.",
        check="python3 scratch/pycodemod.py --funcnames --verbatim",
        why="⚑ MEASURED (compile-only probe, no connection): `func.totally_made_up_xyz(c)` "
            "compiles IDENTICALLY on postgres and sqlite, and `string_agg` — valid postgres — "
            "sits in the same bucket as the invented name.  SQLAlchemy has ONE generic registry "
            "(52 names) and NO per-dialect list to check against.  ⚑ So `--funcnames` reports "
            "UNVERIFIED-BY-CORE and never WRONG: a mode claiming a function does not exist "
            "would invent a verdict its instrument cannot support.  I planned exactly that mode.",
    ),
    Decline(
        claim="a zero from a span query means the population is clean",
        instead="it is a FLOOR — the join's basis may be thin, and a bare count cannot say so.",
        check="python3 scratch/pycodemod.py --resorts jea/metalanguage/sorted_stream.py",
        why="⚑ THE FAILURE MODE OF A BOUNDS-SHAPED READER IS SILENCE.  A reader that finds "
            'nothing reads as *"the claim is unbounded"* — the exact over-broad conclusion it '
            "exists to prevent — and NOTHING IN ITS OWN OUTPUT CONTRADICTS THAT.  `--resorts` "
            "shipped with this defect and printed a bare `0 re-sort(s)` for a day; it now "
            "states the producer census it matched against, and the check must keep printing "
            "that basis line.",
    ),
]


#: ⚑⚑⚑ Ⓜ10 / ⟡fixture-category — A FIXTURE IS NOT A MODE, AND DOCUMENTING ONE IS THE
#: WRONG FIX. `sppf_db --selftest-demo-failure` exists to FAIL: it is the positive
#: control that proves the selftest harness can report a failure at all. The divergence
#: census counted it as UNDOCUMENTED, which offers a reader exactly one way to clear it —
#: write a usage line — and a usage line advertising a deliberately-broken flag as a
#: capability is worse than the debt it retires. Round 1 and the tool's own owner reached
#: that verdict independently; the missing thing was never documentation, it was a KIND.
#:
#: ⚑⚑ THE MARKER IS IN THE TOOL'S SOURCE, NOT IN A LIST HERE. A roster of fixture names
#: maintained in this file would be the frozen-roster shape every other census in this
#: repo has been paid down out of — and worse, it would let ANY tool's debt be cleared by
#: an edit to MY file, with no witness in theirs. So the declaration lives where the
#: fixture lives: a tool marks the dispatch site with this token in a comment, and the
#: census reads it. The tool that owns the fixture is the tool that declares it.
#:
#: ⚑ AND IT IS DELIBERATELY UGLY TO SPELL. A fixture is a real exemption from a real
#: gate, so it should cost a visible line in the owning file — not be reachable by
#: forgetting to document something. The census reports fixtures in their own bucket
#: with a count, never silently: an exemption nobody can see is how a ratchet rots.
FIXTURE_MARK = "toolmodes:fixture"


def _fixtures(rec):
    """The flags this tool has DECLARED as deliberate failing fixtures, not capabilities.

    Read from the tool's own source: a dispatch site carrying a `toolmodes:fixture`
    comment. Returns a set, empty for the overwhelming majority of tools.

    ⚑ WHY A SET AND NOT A FILTER APPLIED INSIDE `_invisible`: the two consumers want
    different things. `--divergence` must SHOW the fixtures (an invisible exemption is
    the rot), while the ratchet must not COUNT them. Returning the class lets each
    decide, which is the same one-body-two-consumers discipline `_invisible` documents.

    ⚑⚑ A FIXTURE STILL HAS TO BE DISPATCHED. The mark is checked against `accepts`, so
    marking a flag the tool does not dispatch declares nothing — a comment cannot mint an
    exemption for a mode that is not there. That keeps the marker from becoming a way to
    pre-emptively silence future debt.
    """
    src = rec.get("source") or ""
    if FIXTURE_MARK not in src:
        return set()
    out = set()
    for line in src.splitlines():
        if FIXTURE_MARK not in line:
            continue
        for f in rec["accepts"]:
            if f in line:
                out.add(f)
    return out


def _citations(rows):
    """{(rel, flag): (kind, [owning rel])} — a flag a tool NAMES and ANOTHER tool DECLARES.

    ⚑⚑ A CITATION IS A THIRD THING, AND COLLAPSING IT INTO EITHER NEIGHBOUR IS THE
    DEFECT. `split_inner_module.py:544` prints *"contract is preserved — verified by
    `agda_defs --telescope`"*. `--telescope` is DECLARED, by `agda_defs`, `[optlist+usage]`
    — so booking it against `split_inner_module` as *"declared by NO tool"* is an
    ATTRIBUTION error, not a detection one: the mode exists, the reader was pointed at
    the wrong owner. `cited` is not `undeclared` and it is not `declared-here`, the same
    way `vfs.listdir`'s exit 3 is neither of the Presence codes.

    ⚑⚑⚑ AND THE STAKES ARE THE INVERSE OF A DEFECT. The operator's standing rule is that
    the tools must *"point to a document that points back at all of them, so they're
    cross-discoverable"* — so a sentence naming a sibling's mode is the REMEDY. Scoring
    it as debt would drive a paydown that DELETES cross-references and turns the corpus
    worse while turning a number greener.

    ⚑ THE RULE IS DERIVED FROM THE CORPUS, NOT INVENTED. `cmd_gaps` already resolves
    exactly this against the global index (`if f in declared: continue  # a
    cross-reference to another tool`) — the discriminator was ALREADY IN THE TREE and
    `cmd_find`'s prose arm simply did not consult it. This function is that predicate
    lifted to one body so the two arms cannot disagree again; `--gaps` was right and
    `--find` was wrong about the SAME flag in the SAME run.

    ⚑⚑ TWO KINDS, BECAUSE ONE OF THEM IS UNDECIDABLE AND SAYING SO IS THE POINT.
      CITATION   the citing LINE also names a declaring tool (`agda_defs --telescope`) —
                 tool and flag adjacent, so the owner is WITNESSED, not inferred.
      CITATION?  the flag is declared elsewhere but the citing line names no owner. A
                 bare `--binding` in a sentence whose SUBJECT is the tool is genuinely
                 undecidable from the flag's neighbourhood, and a "tool name near flag"
                 heuristic silently guesses. Reported with EVERY declarer rather than
                 one, so the reader resolves it and the census does not pretend to.

    ⚑ IT IS NOT PROMOTED TO A CENSUS KIND. `divergence_census` — the ratchet's data — is
    UNDOCUMENTED / UNBACKED / FIXTURE over `accepts` and `modes`, and a citation touches
    neither set: it lives in `mentioned`, which `_invisible` SUBTRACTS. So no ratchet row
    moves, by construction. That is the honest outcome, not a missed opportunity: the
    13 open rows were never citations, and a count that fell here would be a census
    getting weaker, not a tree getting better.
    """
    declared = _index(rows)
    out = {}
    for _a, rel, rec in rows:
        src = rec.get("source") or ""
        for f in sorted(rec["mentioned"]):
            hits = declared.get(f)
            if not hits:
                continue
            owners = sorted({r for r, _rec in hits if r != rel})
            if not owners:
                continue
            stems = {os.path.basename(o)[:-3] for o in owners}
            witnessed = any(f in line and any(s in line for s in stems)
                            for line in src.splitlines())
            out[(rel, f)] = ("CITATION" if witnessed else "CITATION?", owners)
    return out


def _invisible(rec, universal):
    """The flags a tool dispatches that NO READER CAN SEE — the sharp class.

    Argv-anchored, and absent from every usage line AND from the prose AND from the
    bracketed options: a capability that exists and is unreachable through the
    documented interface — exactly how `agda_lex`'s modes became invisible, since its
    bare run prints a selftest.

    ⚑ A BRACKETED OPTION IS DOCUMENTED.  `agda_defs.py --closure <Mod> [--prefix
    <Pfx>]` declares `--prefix` on the usage line; it is correctly not a MODE, and
    reporting it as an undocumented one would send a reader to document what the tool
    already documents.

    ⚑ ONE BODY, TWO CONSUMERS, AND THAT IS THE POINT.  `--divergence` reports this
    class and `--sync` publishes it into the skill.  Two copies of the predicate would
    let the gate's number and the document's number disagree while both were "right"
    — the `agda_files()` class (four bodies under one name) one layer up.
    """
    return sorted(f for f in rec["accepts"]
                  if f not in rec["modes"] and f not in rec["mentioned"]
                  and f not in rec["options"] and f not in universal)


# ─────────────────────────────────────────────────────────────────────────────
# modes
# ─────────────────────────────────────────────────────────────────────────────
def cmd_all(rows):
    n = 0
    for artifact, rel, rec in rows:
        # ⚑⚑ THREE VERDICTS, NOT TWO.  `⚑ UNREADABLE BY THIS CENSUS` is a fact about the
        # PARSER; `⚑ NO SELF-DESCRIPTION` is a fact about the TOOL.  Rendering both as
        # the latter is what made all five of `gate_census.py`'s modes read as
        # undocumented for as long as they existed.
        mark = ("" if rec["described"]
                else "   ⚑ UNREADABLE BY THIS CENSUS" if rec.get("unparsed")
                else "   ⚑ NO SELF-DESCRIPTION")
        print(f"\n── {rel}   [{artifact}]{mark}")
        if rec.get("unparsed"):
            print(f"   ⚑ COULD NOT PARSE this file's usage block: {rec['unparsed']}.\n"
                  f"   This is a fact about THIS READER, not about the tool — its modes\n"
                  f"   may be fully documented. Do NOT read the flags below as a\n"
                  f"   documentation gap, and do not 'fix' the tool.")
            for f in sorted(rec["accepts"]):
                print(f"     {f:<22} (argv-anchored; documentation status UNKNOWN)")
            n += 1
            continue
        if not rec["described"]:
            # ⚑ REPORTED, NOT PATCHED.  This is the tool whose bare run prints its
            # SELFTEST instead of a mode list; every flag below is one the AST
            # carries and no reader can see.
            print(f"   bare output yields NO usage line (exit {rec['rc']}); its "
                  f"modes cannot be derived from it.\n"
                  f"   {len(rec['accepts'])} flag(s) its code dispatches on "
                  f"(argv-anchored) — the only signal available,\n"
                  f"   and no reader is told about any of them:")
            for f in sorted(rec["accepts"]):
                print(f"     {f:<22} (argv-anchored, undocumented)")
            n += 1
            continue
        for mo in sorted(rec["modes"]):
            m = rec["modes"][mo]
            src = "+".join(sorted(m["sources"]))
            sig = " ".join(m["sig"])
            print(f"   {mo:<18} {sig:<22} [{src}]  {_one_line(m['gloss'], 60)}")
        n += 1
    total = sum(len(r["modes"]) for _a, _p, r in rows)
    print(f"\n{total} mode(s) across {n} of {len(rows)} tool(s) in the routing table.")
    return 0


#: The function arm's default page size.  A DEFAULT, not a cap — `--top` overrides it and
#: `--top 0` prints every row.  Named rather than spelled inline because the truncation
#: NOTICE has to quote the same number it truncated at; two literals is how a "… and N more"
#: comes to disagree with the list above it.
FIND_FN_PAGE = 20


def cmd_find(rows, needle, top=None):
    """WHICH TOOL has this mode — the mode that prevents a wrong-tool invocation.

    ⚑⚑ `top` PAGES THE FUNCTION ARM, AND THE OTHER THREE ARMS ARE DELIBERATELY UNBOUNDED.
    Mode names, glosses and undocumented dispatches are a roster the census OWNS — a few
    dozen at most — so truncating them would hide part of the answer to *which tool has
    this*. The function arm searches ~2,900 documented defs and can return hundreds, which
    is why it alone pages.

    ⚑⚑ AND THE PAGE WAS A SILENT CAP UNTIL NOW, WHICH IS THE DEFECT THIS PARAMETER CLOSES.
    Measured while migrating the decode family: `--find _sql` reports **54 hits** and printed
    **20**, with `… and 32 more` — so a migration planning its own roster from this mode got
    a count that was exact and a LIST that was not. The notice was honest and unactionable in
    the same breath: it said what was missing without offering any way to see it. A census
    that can name its own omission but not remove it is still reporting a fact about the
    METHOD as if it were the whole substrate.

    ⚑ `top=0` MEANS EVERY ROW, not "none" — the spelling `--fingerprint --top 0` already uses
    for the inverse ("suppress the ordering"). The divergence is deliberate and is why this
    reads `0 = all` at the SITE rather than only in the usage line: here there is no other way
    to ask for an unbounded list, and a mode whose maximum is spelled `999999` is a mode with
    a cap nobody wrote down.
    """
    key = needle.lstrip("-").lower()
    idx = _index(rows)
    all_tools = [rel for _a, rel, _r in rows]

    byname = sorted((mo, rel, rec) for mo, hits in idx.items()
                    for rel, rec in hits if key in mo.lstrip("-").lower())
    print(f"── by MODE NAME containing {key!r}")
    for mo, rel, rec in byname:
        m = rec["modes"][mo]
        print(f"   {mo:<18} on {rel:<28} [{'+'.join(sorted(m['sources']))}]  "
              f"{_one_line(m['gloss'], 50)}")
    if byname:
        # ⚑ THE OTHER HALF OF THE ANSWER, AND THE HALF THE FIVE MISSES NEEDED.
        # "`--grep` exists" was never the operator's problem; "it is not on the tool
        # I just typed" was.  Naming the tools that LACK it is what makes the census
        # actionable rather than merely correct.
        owners = {rel for _m, rel, _r in byname}
        lacks = [t for t in all_tools if t not in owners]
        print(f"   ⚑ NOT on: {', '.join(lacks) if lacks else '(every tool has it)'}")
    else:
        print("   (none)")

    byg = sorted((mo, rel, rec) for mo, hits in idx.items() for rel, rec in hits
                 if key in rec["modes"][mo]["gloss"].lower() and key not in mo.lower())
    print(f"\n── by GLOSS mentioning {key!r}  (the mode you MEANT may be named differently)")
    for mo, rel, rec in byg:
        print(f"   {mo:<18} on {rel:<28} {_one_line(rec['modes'][mo]['gloss'], 50)}")
    if not byg:
        print("   (none)")

    # ⚑⚑ THE ATTRIBUTION SPLIT. Until 2026-08-26 this arm read `rec["mentioned"]` alone
    # and printed *"declared by NO tool"* over it — while the BY-MODE-NAME arm above,
    # reading the same `idx`, printed the declarer. One run of `--find telescope`
    # therefore said `agda_defs` declares `--telescope [optlist+usage]` AND that no tool
    # declares it. The two arms disagreed because only one consulted the global index;
    # `cmd_gaps` had consulted it all along, so the fix is to share the predicate
    # (`_citations`), never to add a second copy of it here.
    cites = _citations(rows)
    prose, cited = [], []
    for _a, rel, rec in rows:
        for f in sorted(rec["mentioned"]):
            if key not in f.lstrip("-").lower():
                continue
            hit = cites.get((rel, f))
            (cited if hit else prose).append((rel, f, hit))
    prose.sort()
    cited.sort()
    lits = sorted((rel, f) for _a, rel, rec in rows for f in rec["accepts"]
                  if key in f.lstrip("-").lower() and f not in rec["modes"])
    if cited:
        # ⚑ A THIRD VERDICT, PRINTED IN ITS OWN SECTION. Folding these into the block
        # below — under either heading — is what made a correct cross-reference read as
        # debt, and the paydown that would follow deletes the cross-discoverability the
        # standing rule requires.
        print("\n── CITED  (this tool NAMES a mode another tool DECLARES — not a gap)")
        for rel, f, (kind, owners) in cited:
            mark = "" if kind == "CITATION" else "   ⚑ owner not named on the citing line"
            print(f"   {f:<18} named in {rel}, declared by {', '.join(owners)}{mark}")
    print("\n── NAMED but not declared  (prose mention / undocumented dispatch)")
    for rel, f, _k in prose:
        print(f"   {f:<18} named in {rel}'s own output, declared by NO tool")
    for rel, f in lits:
        print(f"   {f:<18} dispatched by {rel}, in no usage line — UNDOCUMENTED")
    if not prose and not lits:
        print("   (none)")

    # ⚑ THE FUNCTION ARM — the population that made this mode miss a reinvention.
    # A capability implemented as a library function and never exposed as a mode was
    # invisible to all three arms above; `literal_flags` is the measured instance.
    # Matched on the docstring's FIRST LINE (a function's gloss) by NAME SUBSTRING
    # and by STEMMED CONTENT-WORD OVERLAP, so a searcher who knows what the thing
    # DOES but not what it is CALLED gets an answer.
    stems = [os.path.basename(rel) for _a, rel, _r in rows]
    want = _tokens(needle, stems) or {_stem(key)}
    fns, seen_fn = [], set()
    for rel, name, gloss in _fn_glosses():
        if key in name.lstrip("_").lower():
            fns.append((rel, name, gloss, "name"))
            seen_fn.add((rel, name))
    for rel, name, gloss in _fn_glosses():
        if (rel, name) in seen_fn:
            continue
        sh = want & _tokens(gloss, stems)
        if len(sh) >= 2 or (len(want) == 1 and sh):
            fns.append((rel, name, gloss, "+".join(sorted(sh))))
    # ⚑ ONE `page` DRIVES BOTH THE SLICE AND THE NOTICE, so the number quoted in "… and N
    # more" is necessarily the number truncated at. Two independent literals is exactly how
    # a truncation notice comes to disagree with the list above it.
    page = FIND_FN_PAGE if top is None else top
    shown = fns if page <= 0 else fns[:page]
    print("\n── by FUNCTION  (a capability may be a library function, not a mode)")
    for rel, name, gloss, why in shown:
        print(f"   {name:<22} in {rel:<34} [{why}]  {_one_line(gloss, 46)}")
    if not fns:
        print("   (none)")
    elif len(shown) < len(fns):
        # ⚑ THE NOTICE NAMES ITS OWN REMEDY. A truncation that says only "N more" tells the
        # reader a list is incomplete and leaves them to guess how to complete it — which is
        # what sent a caller to `--top 60` (not a flag) and then to reading the file by hand.
        print(f"   … and {len(fns) - len(shown)} more — `--find {needle} --top 0` for all")

    # ⚑⚑⚑ THE TOOL ARM — AND ITS ABSENCE WAS THE FAMILY-SCALE INSTANCE OF THIS MODE'S
    # OWN DEFECT.  Every arm above searches INSIDE a tool (its modes, its glosses, its
    # prose, its functions).  None searched for a TOOL, so a file-level entry point with
    # no importers and no `--flag`-bearing usage line was unreachable from the census
    # built to make capabilities reachable.
    # ⚑ MEASURED 2026-08-26 on the telescope/split family: `--find telescope` returned
    # `_close_over_siblings`, `inner_modules`, `needed`, `arity` — LIBRARY FUNCTIONS —
    # while `split_telescoped.py`, the tool that performs the operation, appeared
    # nowhere.  `--find split_telescoped` returned **0 hits for the tool's own name**,
    # and `--find "split a telescoped module"` returned `collide` / `queue` /
    # `inner_modules`.  A reader asking "how do I split a telescoped module" was
    # answered with a function list.
    # ⚑ THAT IS A FACT ABOUT THE METHOD REPORTED AS A FACT ABOUT THE TOOLKIT — the same
    # shape as `--calls emit` missing `_emit_one`, one level up: the census could not see
    # the tools, so the tools read as absent.
    # ⚑ DERIVED, NEVER LISTED.  `rows` already carries every tool's relpath AND its
    # source (`rec["source"]`, added for fixture declarations), so this arm needs no new
    # population, no new I/O and no roster to maintain — a tool is matched on its own
    # basename and on the FIRST LINE of its self-description, which is the same
    # authority every other arm reads.
    # ⚑ THE MATCH READS THE WHOLE SELF-DESCRIPTION; THE DISPLAY SHOWS LINE ONE.  First
    # cut matched line 1 only, and that reproduced the defect one notch in: a tool whose
    # opening sentence is its MECHANISM rather than its OCCASION stayed unreachable.
    # Measured — `--find "repair a telescope after a split"` returned 0 tools while
    # `hoist_telescope_imports.py` is exactly that tool; its first line says "Hoist
    # imports that a module's TELESCOPE needs above its module header" and the words a
    # searcher would use ("repair", "split") sit further down. A one-line window is a
    # curated summary the tool never agreed to write.
    tools = []
    for _a, rel, rec in rows:
        stem = os.path.basename(rel)[:-3] if rel.endswith(".py") else os.path.basename(rel)
        _body = rec.get("source", "").lstrip("#!/usr/bin/env python3\n").lstrip().lstrip('"\'r')
        gloss = _one_line(_body, 60)
        why = None
        if key in stem.lower():
            why = "name"
        else:
            # ⚑ THE WINDOW IS THE MODULE DOCSTRING, NOT THE SOURCE.  A raw
            # `_body[:4000]` slice ran 29 hits on a 4-word query — it reaches past the
            # docstring into CODE, where identifiers match incidentally and a tool's
            # imports read as its subject.  The docstring is the tool's own curated
            # self-description, which is the authority every other arm already uses;
            # anything past its close is not a claim the tool made about itself.
            _end = _body.find('"""')
            sh = want & _tokens(_body[:_end if _end > 0 else 2000], stems)
            if len(sh) >= 2 or (len(want) == 1 and sh):
                why = "+".join(sorted(sh))
        if why:
            tools.append((rel, stem, gloss, why))
    tools.sort()
    print("\n── by TOOL  (the tool ITSELF, not a mode or function inside one)")
    for rel, _basename, gloss, why in tools:
        print(f"   {rel:<40} [{why}]  {gloss}")
    if not tools:
        print("   (none)")

    hits = len(byname) + len(byg) + len(cited) + len(prose) + len(lits) + len(fns) + len(tools)
    total = sum(len(r["modes"]) for _a, _p, r in rows)
    print(f"\n{hits} hit(s) for {needle!r}; {total} declared mode(s) + "
          f"{len(_fn_glosses())} documented function(s) over "
          f"{len(rows)} tool(s) / {len(_tool_py())} file(s) searched.")
    return 0


def cmd_collisions(rows):
    """ONE NAME, SEVERAL TOOLS — and whether it is the SAME question."""
    idx = _index(rows)
    coll = {mo: hits for mo, hits in idx.items() if len(hits) > 1}
    stems = [os.path.basename(rel) for _a, rel, _r in rows]
    for mo in sorted(coll):
        hits = coll[mo]
        toks = [_tokens(rec["modes"][mo]["gloss"], stems) for _rel, rec in hits]
        sigs = {rec["modes"][mo]["sig"] for _rel, rec in hits}
        shared = set.intersection(*toks) if toks and all(toks) else set()
        union = set.union(*toks) if toks else set()
        # ⚑ THE COLLISION IS NOT THE FINDING; THE DIVERGENCE IS.  Two tools spelling
        # a mode the same way is only dangerous when they answer DIFFERENT questions,
        # because that is when the wrong tool returns a plausible answer instead of
        # an error.  Reported as shared-vocabulary over union, with the signatures.
        verdict = ("DIVERGENT" if not shared else
                   "aligned" if len(shared) >= 2 else "weakly aligned")
        if len(sigs) > 1:
            verdict += ", DIFFERENT ARGUMENTS"
        print(f"\n{mo}   — {len(hits)} tools — {verdict}"
              f"  (shared gloss words: {', '.join(sorted(shared)) or 'none'}"
              f" of {len(union)})")
        for rel, rec in sorted(hits):
            m = rec["modes"][mo]
            print(f"   {rel:<30} {' '.join(m['sig']):<20} {_one_line(m['gloss'], 60)}")
    print(f"\n{len(coll)} colliding DECLARED name(s) of {len(idx)} distinct mode "
          f"name(s) across {len(rows)} tool(s).")

    # ⚑ THE DECLARED LAYER IS NOT WHERE THE COLLISIONS ARE.  Only one mode name is
    # documented twice — but the UNDOCUMENTED dispatch layer collides repeatedly,
    # and those are strictly worse: a flag that two tools both accept, that no
    # usage line mentions, cannot be checked against anything before it is typed.
    # Reported with no divergence verdict because an undocumented flag has no
    # gloss to compare — the absence is the finding.
    dis = {}
    for _a, rel, rec in rows:
        for f in rec["accepts"] - set(rec["modes"]):
            dis.setdefault(f, []).append(rel)
    dcoll = {f: v for f, v in dis.items() if len(v) > 1}
    print("\n── UNDOCUMENTED flags accepted by SEVERAL tools (no gloss on any side)")
    for f in sorted(dcoll):
        print(f"   {f:<16} {', '.join(sorted(dcoll[f]))}")
    print(f"   {len(dcoll)} colliding undocumented flag(s) of {len(dis)} "
          f"undocumented flag(s).")
    return 0


def _cross_pairs(rows):
    """Every (tool, mode) x (other tool, mode) pair — the full population."""
    flat = [(rel, mo, rec) for _a, rel, rec in rows for mo in rec["modes"]]
    for i, (r1, m1, c1) in enumerate(flat):
        for r2, m2, c2 in flat[i + 1:]:
            if r1 != r2:
                yield (r1, m1, c1), (r2, m2, c2)


def _sig_families(rows):
    """{exact signature: [(tool, mode)]} — same argument shape, any tool."""
    out = {}
    for _a, rel, rec in rows:
        for mo, m in rec["modes"].items():
            if m["sig"]:
                out.setdefault(m["sig"], []).append((rel, mo))
    return out


def kind_families(rows):
    """{placeholder kind: [(tool, mode)]} — every mode that takes a `<kind>`.

    ⚑ THE EXACT SIGNATURE IS TOO STRICT TO SEE THE FAMILY THAT MATTERS.
    `agda_defs --grep <regex>` and `transcriptstruct --grep-content <file>
    <regex>` are the same question over different corpora, and grouping by the
    ORDERED TUPLE puts them in different families because one takes its corpus
    positionally.  Grouping by the KIND of argument keeps them together — and it is
    the grouping that shows `<regex>` living on two tools and absent from three,
    which is what makes `pycodemod --grep` a guess someone will keep making.
    """
    out = {}
    for _a, rel, rec in rows:
        for mo, m in rec["modes"].items():
            for k in set(m["sig"]):
                out.setdefault(k, []).append((rel, mo))
    return out


def _label(rel, mo):
    return f"{os.path.basename(rel).replace('.py', '')}{mo}"


def cmd_siblings(rows):
    """DIFFERENT NAMES, SIMILAR CAPABILITY — why someone guesses the wrong tool."""
    stems = [os.path.basename(rel) for _a, rel, _r in rows]
    pairs = list(_cross_pairs(rows))

    # ── signal 1: identical ARGUMENT SIGNATURE ───────────────────────────────
    bysig = _sig_families(rows)
    fams = {s: v for s, v in bysig.items() if len({r for r, _m in v}) > 1}
    print("── SIGNATURE families (identical argument shape, different tools)")
    for sig in sorted(fams, key=lambda s: (-len(fams[s]), s)):
        print(f"   {' '.join(sig):<20} " +
              ", ".join(_label(r, m) for r, m in sorted(fams[sig])))
    print(f"   {len(fams)} cross-tool family(ies) of {len(bysig)} signature(s).")

    # ── signal 2: shared ARGUMENT KIND ───────────────────────────────────────
    kinds = kind_families(rows)
    xk = {k: v for k, v in kinds.items() if len({r for r, _m in v}) > 1}
    print("\n── ARGUMENT-KIND families (the same KIND of question, any tool)")
    for k in sorted(xk, key=lambda k: (-len({r for r, _m in xk[k]}), k)):
        print(f"   {k:<20} " + ", ".join(_label(r, m) for r, m in sorted(xk[k])))
    print(f"   {len(xk)} cross-tool kind(s) of {len(kinds)} argument kind(s).")

    # ── signal 3: shared GLOSS VOCABULARY, fully enumerated ──────────────────
    # ⚑ ENUMERATED BY WORD, NOT RANKED BY A SCORE.  A similarity cutoff is a
    # threshold someone tuned; "which content word do two different tools' glosses
    # both use" is a membership test over the whole population, and it is the query
    # that puts `--prose`, `--source` and `--grep-content` in one family — the exact
    # cluster that makes an operator reach for the wrong tool.
    vocab = {}
    for _a, rel, rec in rows:
        for mo, m in rec["modes"].items():
            for t in _tokens(m["gloss"], stems):
                vocab.setdefault(t, set()).add((rel, mo))
    xv = {t: v for t, v in vocab.items() if len({r for r, _m in v}) > 1}
    print("\n── VOCABULARY families (one gloss word, several tools)")
    for t in sorted(xv, key=lambda t: (-len({r for r, _m in xv[t]}), t)):
        print(f"   {t:<16} " + ", ".join(_label(r, m) for r, m in sorted(xv[t])))
    print(f"   {len(xv)} cross-tool word(s) of {len(vocab)} gloss word(s).")

    # ── signal 2: shared GLOSS VOCABULARY ────────────────────────────────────
    # ⚑ ENUMERATED, NOT THRESHOLDED.  The criterion is "shares at least two content
    # words", which is a membership test over the whole population — not a
    # similarity score cut at a number someone tuned.  Every pair is examined; the
    # denominator is printed so a reader sees what was considered.
    scored = []
    for (r1, m1, c1), (r2, m2, c2) in pairs:
        t1 = _tokens(c1["modes"][m1]["gloss"], stems)
        t2 = _tokens(c2["modes"][m2]["gloss"], stems)
        sh = t1 & t2
        if len(sh) >= 2:
            scored.append((len(sh), r1, m1, r2, m2, sh))
    print("\n── STRONGEST pairs (two or more gloss words in common)")
    for n, r1, m1, r2, m2, sh in sorted(scored, reverse=True):
        print(f"   {n}  {_label(r1, m1):<28} ≈ {_label(r2, m2):<28} "
              f"[{', '.join(sorted(sh))}]")
    print(f"   {len(scored)} sibling pair(s) of {len(pairs)} cross-tool pair(s) "
          f"examined.")
    return 0


def cmd_declines(argv=None):
    """The readings this toolkit CONSIDERED and REFUSED, each with its guarding check RUN.

    ⚑⚑ THE POINT IS THAT A REFUSAL BECOMES DISCOVERABLE.  Before this, a rejected reading
    left no trace: a census reports what it FOUND and what it COULD NOT READ, and neither
    says *"settled — here is why"*.  So the next reader re-derives the question, or adopts
    the rejected reading because nothing contradicts it.  That is not hypothetical; it
    happened to me, into a peer's tree, with a certified bound sitting one file away.

    ⚑ SO THE CHECK IS RUN, NOT QUOTED.  A `Decline` naming a command nobody executes is the
    inert-guard shape this repo has recorded five times — present, greppable, and doing
    nothing.  Three verdicts, and the middle one is the reason the mode exists:

        GUARDED    the check ran and passed — the refusal still holds
        LAPSED     the check RAN AND FAILED — ⚑ the rejected reading may now be true, or the
                   check has drifted off its subject.  Either way the record is no longer
                   load-bearing and someone must look
        UNGUARDED  `check is None` — a decline nothing verifies, which is a comment with a
                   record around it.  REPORTED, never hidden: an unguarded decline is exactly
                   the "absent argument reads as an absent objection" defect wearing this
                   mode's own clothes

    ⚑ `--quick` skips execution and lists the records only.  It is NOT the default, because a
    listing that never runs its checks would make UNGUARDED and GUARDED indistinguishable —
    which is the failure this whole record type exists to prevent.
    """
    quick = "--quick" in (argv or [])
    guarded = lapsed = unguarded = 0
    # ⚑ IDENTICAL CHECKS RUN ONCE.  Two declines share `--funcnames --verbatim` because they
    # are different REFUSALS guarded by the same discriminator — which is legitimate and is
    # not a duplicate record.  Running it twice is `_bare_calls`' repeated-work defect, third
    # recurrence in this toolkit today; the memo is keyed on the command string.
    ran: dict = {}
    unchecked = 0
    for d in DECLINES:
        if d.check is None:
            verdict, detail = "UNGUARDED", "no check declared"
            unguarded += 1
        elif quick:
            verdict, detail = "declared", d.check
        else:
            if d.check not in ran:
                # ⚑ ANNOUNCE BEFORE RUNNING.  These checks are real gates — three are corpus
                # walks — so a silent run is indistinguishable from a hung one, which is the
                # confusion `--discards` already records paying for twice.
                print(f"  … running {d.check}", flush=True)
                try:
                    # ⚑ A DECLINE'S CHECK IS A REAL GATE AND MAY BE A CORPUS WALK, so it gets
                    # its OWN budget rather than the module's 180s `timeout(1)` figure.
                    # MEASURED 2026-08-19: `--conventions` exceeded 180s and reported
                    # UNCHECKED — correct behaviour, and the cause was the host running in
                    # POWERSAVE for stability (operator). ⚑ A timeout tuned on a fast machine
                    # turns a slow one into a tree full of unverifiable refusals, which is a
                    # fact about the box read as a fact about the claims. `DECLINE_TIMEOUT_S`
                    # is separate so raising it cannot loosen the `timeout(1)` budget.
                    p = subprocess.run(d.check, shell=True, cwd=ROOT, capture_output=True,
                                       text=True, timeout=DECLINE_TIMEOUT_S)
                    ran[d.check] = (p.returncode == 0, f"exit {p.returncode}")
                except Exception as e:                                # noqa: BLE001
                    ran[d.check] = (None, f"{type(e).__name__}: {e}")
            ok, note = ran[d.check]
            if ok:
                verdict, detail = "GUARDED", d.check
                guarded += 1
            elif ok is None:
                # ⚑ COULD-NOT-RUN IS NOT THE SAME AS RAN-AND-FAILED, and collapsing them would
                # report a fact about THIS MACHINE as a fact about the refusal.
                verdict, detail = "UNCHECKED", f"{d.check}  ⚑ did not run: {note}"
                unchecked += 1
            else:
                verdict, detail = "LAPSED", f"{d.check}  → {note}"
                lapsed += 1
        print(f"  {verdict:<10} {d.claim}")
        print(f"             instead: {d.instead}")
        print(f"             check:   {detail}", flush=True)
    if quick:
        print(f"{len(DECLINES)} declared decline(s) — checks NOT run (--quick); "
              f"re-run bare to verify each refusal still holds")
        return 0
    print(f"{guarded}/{len(DECLINES)} decline(s) GUARDED; {lapsed} lapsed, "
          f"{unchecked} unchecked, {unguarded} unguarded")
    if unguarded:
        # ⚑ An unguarded decline is this mode's own defect class, in its own output.
        print("   ⚑ an UNGUARDED decline is a comment with a record around it — it states a "
              "refusal nothing would notice lapsing")
    if unchecked:
        # ⚑ A fact about THIS MACHINE, never about the refusal — the distinction `--portable`
        # already draws between an engine verdict and a degraded pattern guess.
        print("   ⚑ UNCHECKED means this run could not execute the check — a fact about this "
              "environment, not evidence either way about the refusal.")
    if lapsed:
        print("   ⚑ a LAPSED check does NOT mean the rejected reading is now correct — it "
              "means the record stopped being load-bearing. Read the check before the claim.")
    return 1 if (lapsed or unchecked) else 0


def cmd_conventions(rows):
    """The DECLARED flag conventions, each measured against the live census.

    ⚑ A DECLARATION THAT NOTHING CHECKS IS THE THING `farm.py` REFUSES.  An F-arm is
    only evidence because it declares the message its mutation must provoke and reports
    VACUOUS when the red comes from elsewhere.  The analogue here: a `Convention` claims
    a flag's meaning is shared, so this measures the claim against what tools actually
    accept and reports the two ways it can rot —

        STALE     declared, and NO tool accepts it → the convention outlived its flag
        SOLO      declared, and ONE tool accepts it → not shared; a per-tool mode
                  wearing a contract's clothes

    Neither is inferable from the record alone, which is exactly why the record is not
    enough on its own.
    """
    accepts = {}
    for _a, rel, rec in rows:
        for f in rec["accepts"] | set(rec["modes"]):
            accepts.setdefault(f, []).append(rel)
    bad = 0
    for c in CONVENTIONS:
        who = sorted(accepts.get(c.flag, []))
        if not who:
            verdict = "STALE"
        elif len(who) == 1:
            verdict = "SOLO"
        else:
            verdict = "SHARED"
        if verdict != "SHARED":
            bad += 1
        print(f"  {verdict:7} {c.flag:<14} {len(who)} tool(s)")
        print(f"          contract: {c.contract}")
        print(f"          invoker:  {c.invoker}")
        if verdict == "STALE":
            print("          ⚑ NO tool accepts this — the declaration outlived the flag.")
        elif verdict == "SOLO":
            print(f"          ⚑ only {who[0]} — a per-tool mode, not a shared contract.")
    # ⚑⚑ A REQUIRED PAIR IS A CONTRACT THE CENSUS CAN MEASURE, and measuring it is what
    # keeps `contract` from being prose.  `--apply`/`--dry-run` and the tenant selector
    # are declared MUTUALLY EXCLUSIVE AND REQUIRED — no default in either direction —
    # because a default is silent in both failure modes: a default-dry tool does nothing
    # when the caller meant to write, a default-apply tool writes when the caller meant to
    # look, and a default tenant makes "forgot to care" indistinguishable from "chose".
    # A tool accepting ONE side of a required pair still defaults on the other, so it is
    # HALF-PAIRED — which is exactly the state every member is in today.
    print("\n── REQUIRED PAIRS — a tool accepting one side still DEFAULTS on the other")
    _pairs = [("--apply", "--dry-run", "mutation"), ("--sandbox", None, "tenant")]
    _half = 0
    for _a, _b, _kind in _pairs:
        _has_a = set(accepts.get(_a, []))
        _has_b = set(accepts.get(_b, [])) if _b else set()
        _only_a = sorted(_has_a - _has_b)
        if _b:
            _only_b = sorted(_has_b - _has_a)
            _both = sorted(_has_a & _has_b)
            print(f"   {_kind}: {len(_both)} tool(s) take BOTH; "
                  f"{len(_only_a)} take only {_a}; {len(_only_b)} take only {_b}")
        else:
            # ⚑ THE TENANT PAIR HAS NO SECOND FLAG YET — there is no `--live`, which IS
            # the finding: the absent half is what makes "no flag" mean "live" silently.
            print(f"   {_kind}: {len(_only_a)} tool(s) take {_a}; there is NO explicit "
                  f"live selector, so its absence is a DEFAULT rather than a choice")
        _half += len(_only_a) + (len(_has_b - _has_a) if _b else 0)
    print(f"   ⚑ {_half} half-paired tool(s) — each still has a silent default. "
          f"→ ⟡explicit-mutation / ⟡explicit-tenant")

    # ⚑ THE OTHER DIRECTION IS THE ONE THAT FINDS WORK: a flag many tools accept and
    # NO record explains.  That is either an undeclared convention (declare it) or real
    # divergence (converge it) — and the census cannot tell which, which is the whole
    # reason a human writes the `why`.
    undeclared = sorted((f, w) for f, w in accepts.items()
                        if len(w) >= 3 and f not in HARNESS_CONTRACTS)
    print(f"\n── ACCEPTED BY ≥3 TOOLS, DECLARED BY NO CONVENTION ({len(undeclared)})")
    for f, w in undeclared:
        print(f"   {f:<16} {len(w):2d} tools: {', '.join(os.path.basename(x) for x in sorted(w)[:6])}"
              + (" …" if len(w) > 6 else ""))
    print(f"\n{len(CONVENTIONS) - bad}/{len(CONVENTIONS)} declared convention(s) hold; "
          f"{len(undeclared)} undeclared recurrence(s) — each is a DECLARE-or-CONVERGE decision.")
    return 1 if bad else 0


# ⚑ THE PAIR FLAGS A NEAR MISS IS MEASURED AGAINST — read from `CONVENTIONS`, never
# retyped.  A spelling is a near miss BECAUSE a declared required-pair flag is what the
# author meant; hardcoding the two words here would put the contract in two places, and
# the whole point of `Convention` is that it lives in one.
_PAIR_FLAGS = ("--apply", "--dry-run")


def _edit_distance(a, b):
    """Levenshtein, small strings.  ⚑ NOT a similarity score — a THRESHOLD input."""
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _selftest_only(rel, flags):
    """The subset of `flags` whose ONLY literal sites in `rel` sit in a selftest body.

    ⚑ THE DISCRIMINATOR IS THE ENCLOSING DEF, and `literal_sites` already carries it
    (`ctx`).  A flag with even ONE site outside a selftest is a real interface and is
    NOT excluded — the test is *only*, never *any*, because a tool that both dispatches
    a flag and exercises it in a fixture is dispatching it.

    ⚑ IT CANNOT SEE A FIXTURE FLAG BUILT BY CONCATENATION (`"--" + name`) or read from a
    table — that is a literal this mode never sees, so such a flag stays in the census
    and must be judged by opening the site.  Over-reporting is the conservative
    direction here ONLY because the ratchet refuses rather than records on a new key.
    """
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    try:
        import _pycodemod_query as _q
    except Exception:
        return set()                       # ⚑ a fact about this machine, not the tool
    path = os.path.join(ROOT, rel)
    # ⚑ A PATH THAT DOES NOT EXIST EXCLUDES NOTHING, and that is the honest direction:
    # this function's job is to REMOVE fixture flags from the census, so failing open
    # keeps a candidate IN (where the ratchet refuses on it) rather than silently
    # dropping it. Also what lets the selftest drive `near_misses` on synthetic rows.
    if not os.path.exists(path):
        return set()
    # ⚑ ONE PASS PER TOOL, NOT ONE PER FLAG.  `literal_sites` re-parses the file on every
    # call, so asking it once per candidate flag re-parsed a 2000-line tool ~40 times and
    # the census did not finish inside 120s.  Ask for the shared prefix `--` once and
    # bucket the answer — the same "the parse is the cost" measurement `scan`'s own
    # `_WRAPPER_CACHE` comment records, met again one layer up.
    by_flag = {}
    for s in _q.literal_sites("--", [path]):
        by_flag.setdefault(s[4], []).append(s)
    out = set()
    for f in flags:
        sites = by_flag.get(f, [])
        if not sites:
            continue
        if all("selftest" in (s[3] or "").lower() or s[2] == "doc" for s in sites):
            out.add(f)
    return out


def near_misses(rows):
    """{tool: [(spelling, the pair flag it misses)]} — DERIVED, never a table.

    ⚑⚑⚑ THE GUARD Ⓐ47 OWED, AND WHY A TABLE COULD NOT BE IT.  Three tools (`paydown`,
    `scope_fix`, `telescope_migrate_gen`) spelled no-write as `--dry`, none validated
    argv, and all three WROTE to the Agda tree by default — so a typo'd `--dry-run` fell
    through to the writing branch and mutated it.  That was fixed, and
    `edit_snapshot.NEAR_MISS_SPELLINGS` was added so the REFUSAL names its successor.

    ⚑⚑ BUT THAT TABLE IS FROZEN, AND A FROZEN TABLE IS THE SHAPE THIS FILE EXISTS TO
    RETIRE.  It holds seven spellings someone already met.  Tool #4 next week spelling
    it `--dryish`, `--nodry`, or `--applyy` is caught by NOTHING: the refusal fires only
    on a spelling already known, so the table teaches the lesson exactly once.  It is a
    frozen ALLOW-list wearing a DENY-list's clothes, and `policy_is_a_ratchet_over_census`
    is the recalled form of why that fails.

    ⚑ SO THE PREDICATE IS EDIT DISTANCE TO A DECLARED PAIR FLAG, over the LIVE census.
    A flag within distance 3 of `--apply` or `--dry-run` that is NOT one of them is a
    tool inventing a spelling for a contract that already has one — whether or not
    anybody has met it before.  `--dry` (distance 4 from `--dry-run`) is admitted by the
    substring arm below, which is the case the incident was actually about: a PREFIX of
    a declared flag reads to its author as the flag itself.

    ⚑ WHAT IT CANNOT DECIDE, and it is a real bound: a tool spelling no-write as
    `--report`, `--check`, or `--preview` is UNREACHABLE from here — those are not near
    misses of anything, they are different words for the same intent, and only the
    `--conventions` undeclared-recurrence arm (≥3 tools, a DECLARE-or-CONVERGE decision)
    can surface them.  This guard closes the TYPO class, not the SYNONYM class, and
    saying so is the difference between a guard and a claim of coverage.
    """
    out = {}
    for _a, rel, rec in rows:
        accepted = rec["accepts"] | set(rec["modes"])
        # ⚑⚑ A FIXTURE FLAG IS NOT AN INTERFACE, AND THE FIRST LIVE RUN BANKED TWO.
        # The census returned exactly two keys — `ratchet.py::--aply` and
        # `climode.py::--a` — and BOTH are literals inside `_selftest()`: `--aply` is a
        # DELIBERATE typo driving a refusal case, `--a`/`--b` are toy flags for a
        # branch-bounds fixture.  Neither is a spelling any caller can type at the tool.
        # Banking them would have put a permanent, unpayable row in a paydown-only
        # baseline — the hazard `set_ratchet`'s own docstring records, reproduced in the
        # guard written to prevent a different instance of it.
        #
        # ⚑ SO THE POPULATION IS FLAGS THE TOOL DISPATCHES ON, MINUS THOSE WHOSE ONLY
        # LITERAL SITES SIT IN A SELFTEST BODY.  `--divergence`'s `dispatch` source
        # already anchors a flag to `sys.argv`; what it cannot do is tell a fixture's
        # argv-compare from the real one, because both are argv compares.  The
        # enclosing-def context is the discriminator, and `literal_sites` carries it.
        _fixture = _selftest_only(rel, accepted)
        for f in sorted(accepted):
            if f in _PAIR_FLAGS or not f.startswith("--") or f in _fixture:
                continue
            for pair in _PAIR_FLAGS:
                # ⚑ A PROPER PREFIX IS THE `--dry` CASE AND EDIT DISTANCE ALONE MISSES IT.
                # `--dry` -> `--dry-run` is distance 4, past any threshold tight enough to
                # avoid false positives — yet it is the exact incident this guard is for.
                # A prefix of a declared flag is a near miss BY CONSTRUCTION: the author
                # typed the beginning of the right word and stopped.
                near = pair.startswith(f) or _edit_distance(f, pair) <= 2
                if near:
                    out.setdefault(rel, []).append((f, pair))
                    break
    return out


def cmd_nearmiss(rows):
    """PAYDOWN-ONLY RATCHET: a mutating tool whose no-write flag is not `--dry-run`.

    ⚑ IT ROUTES THROUGH `ratchet.set_ratchet` — the one authority — so it inherits the
    write-is-opt-in rule, the round-trip verification of a minted baseline, the
    `--dry-run` preview, and `list_keys`.  A hand-rolled compare here would be the
    eleventh copy of a dispatch block §60 deleted four of.

    ⚑ DELIBERATELY NOT WIRED INTO PRE-COMMIT.  18 gates are red; adding a nineteenth
    buries a real failure under a new one.  It is a mode you RUN, and the baseline it
    mints is what makes it gateable later without re-litigating the population.
    """
    import ratchet as _r
    found = near_misses(rows)
    cur = {f"{rel}::{f}" for rel, hits in found.items() for f, _p in hits}
    detail = {f"{rel}::{f}": p for rel, hits in found.items() for f, p in hits}
    return _r.set_ratchet(
        cur,
        os.path.join(ROOT, ".nearmiss-baseline"),
        "flag-nearmiss",
        noun="near-miss mutation flag(s)",
        list_keys="--list" in sys.argv,
        render=lambda k: f"{k}   → the convention declares {detail.get(k, '?')}",
        refuse_hint=(
            "  A mutating tool's no-write flag is `--dry-run` and its write flag is "
            "`--apply` —\n"
            "  `toolmodes.py --conventions` declares the pair MUTUALLY EXCLUSIVE and ONE "
            "REQUIRED.\n"
            "  Rename the flag at the tool; do NOT add it to edit_snapshot."
            "NEAR_MISS_SPELLINGS —\n"
            "  that table makes the REFUSAL name a successor, it does not bless the "
            "spelling."),
    )


def cmd_gaps(rows):
    """A capability one tool has and a comparable tool lacks."""
    # ⚑ A CELL MAY NAME TWO TOOLS, so membership is tested against the CELL, not
    # against its basename.  `os.path.basename` of the Agda row's cell returns only
    # the LAST path in it, which silently excluded `agda_lex` from the comparable
    # set — the right answer here for the wrong reason, and the wrong one the moment
    # a two-tool row's first entry declares modes.
    claimed = {tool for _suf, (_art, tool) in _hsq.claims().items()}
    filereaders = [rel for _a, rel, _r in rows if any(rel in c for c in claimed)]

    # ── A: a SIGNATURE family that some file-reading tool is absent from ──────
    # ⚑ "COMPARABLE" IS THE `claims` COLUMN, NOT MY JUDGEMENT.  A tool that claims a
    # FILE artifact is comparable to another that does; `tsdbprobe` claims `—` (a
    # live service), so its absence from a file-corpus family is not a gap.  The
    # authority is the same column the PreToolUse gate reads.
    kinds = kind_families(rows)
    nmodes = {rel: len(rec["modes"]) for _a, rel, rec in rows}
    n_gap = 0
    print("── CAPABILITY present on one file-reader, ABSENT on another")
    # ⚑ THE DENOMINATOR IS PART OF THE FINDING, NOT DECORATION.  A kind carried by
    # MOST of a tool's modes is that tool's CORPUS argument, not a capability:
    # `<file>` is on 6 of mdstruct's 7 modes because every mdstruct question names
    # its document, while `<regex>` is on 2 of agda_defs' 12 because it is a QUERY.
    # Collapsing both to "absent on X" would report `pycodemod` as unable to take a
    # file — it takes `[paths]`, optionally, on nearly every mode.  Printing the
    # coverage keeps the reader able to tell a gap from a calling convention.
    for k in sorted(kinds, key=lambda k: (-len(kinds[k]), k)):
        have = {r for r, _m in kinds[k] if r in filereaders}
        if len(have) < 2:
            continue                    # one tool doing it is not yet a family
        lack = [t for t in filereaders if t not in have]
        if not lack:
            continue
        n_gap += 1
        per = {}
        for r, _m in kinds[k]:
            per[r] = per.get(r, 0) + 1
        print(f"\n   a {k} question is answered by:")
        for r in sorted(have):
            print(f"       {r:<30} {per[r]} of {nmodes[r]} mode(s): " +
                  ", ".join(m for rr, m in sorted(kinds[k]) if rr == r))
        print(f"     ⚑ NO {k} mode on: {', '.join(lack)}")

    # ── B: a mode NAMED in a tool's own prose and declared by nothing ─────────
    # ⚑ A FILED-BUT-UNBUILT GAP IS WRITTEN DOWN IN THE TOOL'S OWN OUTPUT, which
    # makes it derivable rather than remembered.  `pycodemod`'s docstring files
    # `--import-cost` in prose precisely so "the next reader" finds it; until now
    # nothing read that.  A flag named in prose and declared by NO tool is either a
    # filed gap or a stale reference — both are work.
    declared = set(_index(rows))
    # ⚑ THE CROSS-REFERENCE WAS CORRECTLY EXCLUDED HERE AND SILENTLY. This arm has always
    # skipped a flag another tool declares, which is the RIGHT verdict — but a `continue`
    # makes the class invisible, and invisibility is why `cmd_find` could get the same
    # flag wrong for as long as it did with nothing to contradict it. Counted and named.
    cites = _citations(rows)
    print("\n── NAMED in a tool's own output, declared by NO tool (filed / stale)")
    n_named = 0
    for _a, rel, rec in rows:
        for f in sorted(rec["mentioned"]):
            if f in declared:
                continue                      # a cross-reference to another tool
            n_named += 1
            print(f"   {f:<20} named in {rel}")
    if not n_named:
        print("   (none)")
    n_sure = sum(1 for k, _o in cites.values() if k == "CITATION")
    print(f"\n{n_gap} capability gap(s) over {len(filereaders)} file-reading tool(s); "
          f"{n_named} named-but-undeclared flag(s) of {len(declared)} declared name(s).")
    print(f"{len(cites)} further mention(s) are CITATIONS of a mode another tool "
          f"declares — cross-references, NOT debt ({n_sure} name the owner on the "
          f"citing line; {len(cites) - n_sure} do not and are undecidable from the "
          f"flag alone). `--find <flag>` shows the declarer.")
    return 0


def divergence_census(rows):
    """`{"<rel> <flag>": kind}` — the divergence as DATA, for the ratchet gate.

    Three kinds: `UNDOCUMENTED` (dispatched on argv, in no usage line and no prose),
    `UNBACKED` (documented, no matching flag literal), and `FIXTURE` (dispatched, and
    DECLARED by the owning tool as a deliberate failing fixture — see `FIXTURE_MARK`).
    One key per (tool, flag).

    ⚑⚑ Ⓜ10 — A FIXTURE IS EMITTED, NOT DROPPED, and that is the whole design. Filtering
    fixtures out here would make an exemption invisible, which is how a ratchet rots: the
    gate would show a smaller number with nothing saying why. Instead the kind travels
    with the row, and the RATCHET decides not to count it while the REPORT still shows
    it. Same one-body-two-consumers split `_invisible` was extracted for.

    ⚑⚑ EXTRACTED SO THE GATE AND THE REPORT CANNOT DISAGREE. `cmd_divergence` computed
    these sets INLINE and returned only a printed count, so a gate wanting the numbers
    had two options: re-derive the predicates (a second spelling of `_invisible` /
    `_universal`, which is the `census-keyed-on-one-spelling` defect this repo has paid
    for repeatedly) or parse the printed text (the judgement-in-the-turn shape the
    standing rule forbids). Neither is acceptable, so the sets become the authority and
    the printer consumes them — the same lift `set_ratchet.render`/`summary` performed
    on four hand-rolled `--list` blocks.

    ⚑ THE KEY IS `<rel> <flag>`, NOT THE FLAG ALONE. `--check` is undocumented on two
    different tools and `--dry` on two more; a flag-keyed census would collide them into
    one entry, so paying down one tool would read as paying down both — a ratchet
    silently forgiving debt it never saw.
    """
    out = {}
    universal = _universal(rows)
    for _a, rel, rec in rows:
        lit, doc = rec["literal"], set(rec["modes"])
        fixtures = _fixtures(rec)
        for f in _invisible(rec, universal):
            out["%s %s" % (rel, f)] = "FIXTURE" if f in fixtures else "UNDOCUMENTED"
        for f in sorted(x for x in doc if x.startswith("--") and x not in lit):
            out["%s %s" % (rel, f)] = "UNBACKED"
    return out


def cmd_divergence(rows):
    """DOCUMENTED vs DISPATCHABLE — both directions, per tool."""
    n_undoc = n_unbacked = n_passed = 0
    # the two predicates live in `_universal` / `_invisible` — the SAME bodies
    # `--sync` publishes, so the gate's number and the skill's number cannot diverge.
    universal = _universal(rows)
    for _a, rel, rec in rows:
        acc, lit, doc = rec["accepts"], rec["literal"], set(rec["modes"])
        invisible = _invisible(rec, universal)
        unbacked = sorted(f for f in doc if f.startswith("--") and f not in lit)
        passed = len(lit - acc - doc)
        n_passed += passed
        if not invisible and not unbacked:
            continue
        print(f"\n── {rel}")
        for f in invisible:
            n_undoc += 1
            print(f"   UNDOCUMENTED  {f:<20} dispatched on argv, in no usage line "
                  f"and no prose")
        for f in unbacked:
            n_unbacked += 1
            print(f"   UNBACKED      {f:<20} documented, no matching flag literal "
                  f"(stale, or dispatched by prefix)")
    print(f"\n{n_undoc} undocumented mode(s) and {n_unbacked} unbacked mode(s) "
          f"across {len(rows)} tool(s).")
    # ⚑ THE EXCLUDED CLASS IS REPORTED, NOT SILENTLY DROPPED.  These are flags the
    # tools PASS to mypy / git / agda — another program's vocabulary quoted inside a
    # subprocess argument list.  Counting them keeps "not this tool's modes"
    # distinguishable from "not present".
    print(f"{n_passed} further flag literal(s) are not argv-anchored (flags PASSED "
          f"to other programs), excluded.")
    print(f"{len(universal)} flag(s) accepted by EVERY rostered tool — a convention, "
          f"not a per-tool mode: {', '.join(sorted(universal)) or '(none)'}")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# the GENERATED BLOCK in the skill — `--sync` writes it, `--check` gates it
# ─────────────────────────────────────────────────────────────────────────────
# ⚑ THE PATH IS THE GATE'S, IMPORTED.  `hook_structural_query.SKILL` already names
# the file for the PreToolUse hook and for `routes()`; restating it here would be the
# second-roster shape one level down from the one this module exists to avoid.
SKILL_MD = _hsq.SKILL
BLOCK = "mode-census"
BEGIN = "--- BEGIN %s ---" % BLOCK
END = "--- END %s ---" % BLOCK
WIDTH = 86


class BlockError(Exception):
    """The markers are missing or malformed — a PLACEMENT question, not a content one."""


def _wrap(items, indent, width=WIDTH):
    """`items` packed onto as few lines as fit, each prefixed with `indent`."""
    lines, cur = [], ""
    for it in items:
        if cur and len(indent) + len(cur) + 1 + len(it) > width:
            lines.append(indent + cur)
            cur = it
        else:
            cur = (cur + " " + it) if cur else it
    if cur:
        lines.append(indent + cur)
    return lines


def render_block(rows):
    """The census as the block's BODY (markers excluded) — deterministic.

    ⚑ NO RENDERED LINE MAY BEGIN WITH `|`, AND THAT IS CORRECTNESS, NOT STYLE.  This
    module builds its own population by calling `routes()`, which reads EVERY
    `|`-leading line of THIS SAME FILE as an `artifact | tool` row.  A markdown table
    in the block would therefore feed `--sync`'s output back into its input: phantom
    tools in the roster, the PreToolUse gate armed for artifacts nothing claims, and
    `--sync` never reaching a fixed point.  Hence a fenced code block, pinned by a
    selftest rather than by anyone remembering.

    ⚑ WHAT IS IN IT, AND WHY IT IS NOT THE WHOLE CENSUS.  The block is read at the
    moment someone would otherwise GUESS a mode name, so it carries the two facts a
    guess needs and stops: WHICH FLAGS EACH TOOL ACCEPTS (documented and
    undocumented, because the undocumented half is invisible everywhere else and is
    the finding that motivated the block), and WHICH NAMES ANSWER ON MORE THAN ONE
    TOOL (where the wrong tool answers instead of erroring — the only case a
    per-tool roster cannot warn about).  The full NAME→TOOL transpose is deliberately
    NOT rendered: it is ~100 rows carrying no information the roster lacks, and a
    wall nobody reads fails the block's purpose as surely as no block — `--find` is
    the by-name reader, and it also answers by GLOSS, which no static index can.

    ⚑ AND NO COUNT IS WRITTEN BY HAND ANYWHERE NEAR IT.  Every figure in the block is
    computed here.  A frozen number in prose beside a live census ages into a false
    claim about its own subject, and a reader trusts the sentence over the tool
    because the sentence is right there (the incident the pre-commit snapshot-guard
    comment records).
    """
    uni = _universal(rows)
    inv = {rel: _invisible(rec, uni) for _a, rel, rec in rows}
    ndoc = sum(len(rec["modes"]) for _a, _r, rec in rows)
    nund = sum(len(v) for v in inv.values())

    out = [
        "⚑ **GENERATED — DO NOT EDIT BY HAND.** `python3 scratch/toolmodes.py --sync`",
        "rewrites everything between the markers; a hand edit is overwritten on the next",
        "sync, and `--check` is a pre-commit gate that refuses drift. Both DERIVE it — the",
        "documented half from each tool's own bare output, the undocumented half from its",
        "AST (`--flag` literals anchored to `sys.argv`). No roster of modes is maintained",
        "here: a hand-written table is the thing that would rot, which is *why* this is",
        "generated rather than absent.",
        "",
        "**%d documented + %d undocumented mode(s) across %d tool(s).** A `--flag` that"
        % (ndoc, nund, len(rows)),
        "appears NOWHERE below is accepted by no tool — that is what makes `pycodemod",
        "--argstr` a guess rather than a lookup. For a mode's gloss, its owning tool, and",
        "the near-misses by name AND by meaning: `toolmodes.py --find <name>`.",
        "",
        "⚑ **The undocumented rows are the reason this block exists.** Those flags",
        'dispatch, and no usage line names them — so *"run the tool bare and read its mode',
        'list"* cannot see them, and until this block nothing else could either. Each one',
        "is a gap in that tool's self-description: WORK, not a capability this blesses.",
        "",
        "```",
    ]

    for artifact, rel, rec in rows:
        if rec["described"]:
            out.append("%s  [%s]  %d documented, %d undocumented"
                       % (rel, artifact, len(rec["modes"]), len(inv[rel])))
        else:
            # ⚑ REPORTED, NOT PATCHED.  This is the tool whose bare run prints its
            # SELFTEST instead of a mode list; there is no documented half to show,
            # and inventing one here is the defect the whole module exists to prevent.
            out.append("%s  [%s]  ⚑ NO SELF-DESCRIPTION — its bare run prints no usage line"
                       % (rel, artifact))
        if rec["modes"]:
            out += _wrap(sorted(rec["modes"]), "    ")
        if inv[rel]:
            out.append("  ⚑ dispatched, in NO usage line:")
            out += _wrap(inv[rel], "    ")
        out.append("")

    # ── one name, several tools — over the UNION of both layers ───────────────
    # ⚑ THE UNION, NOT THE DOCUMENTED LAYER ALONE.  `--collisions` splits the two
    # because their evidence differs (a documented pair has glosses to compare, an
    # undocumented pair has none).  A READER typing a flag does not make that split:
    # `--roundtrip` answers on pycodemod and mdstruct and ALSO on bibstruct, where no
    # usage line mentions it.  Reporting only the documented collision would hide the
    # tool most likely to surprise.
    owners = {}
    for _a, rel, rec in rows:
        stem = os.path.basename(rel).replace(".py", "")
        for mo in rec["modes"]:
            owners.setdefault(mo, []).append(stem)
        for f in inv[rel]:
            owners.setdefault(f, []).append(stem + "(undoc)")
    coll = {mo: v for mo, v in owners.items() if len(v) > 1}
    out.append("── ONE NAME, SEVERAL TOOLS — the wrong tool ANSWERS instead of erroring")
    for mo in sorted(coll):
        out.append("    %-18s %s" % (mo, "  ".join(sorted(coll[mo]))))
    if not coll:
        out.append("    (none)")
    out.append("")

    # ── documented, not dispatchable — the inverse finding ────────────────────
    unbacked = sorted((f, os.path.basename(rel).replace(".py", ""))
                      for _a, rel, rec in rows for f in rec["modes"]
                      if f.startswith("--") and f not in rec["literal"])
    out.append("── DOCUMENTED, NOT DISPATCHABLE — in a usage line, no matching flag literal")
    for f, stem in unbacked:
        out.append("    %-18s %s" % (f, stem))
    if not unbacked:
        out.append("    (none)")
    out.append("")

    out.append("── A CONVENTION, NOT A PER-TOOL MODE — accepted by every tool, "
               "or invoked by a harness")
    out.append("    " + ("  ".join(sorted(uni)) or "(none)"))
    out.append("```")
    return "\n".join(out)


def _span(src):
    """(body_start, body_end) for the marker block in `src`.

    ⚑ MISSING MARKERS ARE A REFUSAL, NOT AN INSERTION, AND THE CHOICE IS LOAD-BEARING.
    `--sync` owns the block's CONTENT; it does not own its PLACEMENT. A tool that
    inserted would append ~70 lines wherever it happened to reach — with none of the
    prose that introduces them — and, worse, would silently restore a block a human
    had deliberately removed, so "delete the block" would be an instruction nothing
    could carry out. Refusing names the remedy and leaves the editorial decision with
    the editor. It also keeps `--check` honest: absent markers are DRIFT (exit 1),
    reported as absent rather than repaired into a pass.
    """
    i, j = src.find(BEGIN), src.find(END)
    if i < 0 or j < 0:
        raise BlockError(
            "no `%s` … `%s` pair in %s — add the two marker lines where the block "
            "belongs; --sync fills between them but will not choose their place."
            % (BEGIN, END, SKILL_MD))
    if src.count(BEGIN) != 1 or src.count(END) != 1:
        raise BlockError(
            "%s carries %d `%s` and %d `%s` marker(s); exactly one of each is "
            "required — --sync cannot know which pair it owns."
            % (SKILL_MD, src.count(BEGIN), BEGIN, src.count(END), END))
    if j < i + len(BEGIN):
        raise BlockError(
            "`%s` precedes `%s` in %s — the markers are inverted."
            % (END, BEGIN, SKILL_MD))
    return i + len(BEGIN), j


def splice(src, body):
    """`src` with the block's body replaced — every byte OUTSIDE the markers preserved.

    The markers themselves are part of the preserved text: only the region strictly
    between them is rewritten, so `--sync` cannot move, duplicate or reformat them.
    """
    a, b = _span(src)
    return src[:a] + "\n" + body + "\n" + src[b:]


def current_body(src):
    """The block's body exactly as it sits on disk, including its framing newlines."""
    a, b = _span(src)
    return src[a:b]


def cmd_sync(rows):
    with open(SKILL_MD, encoding="utf-8") as f:
        src = f.read()
    new = splice(src, render_block(rows))
    rel = os.path.relpath(SKILL_MD, ROOT)
    if new == src:
        print("toolmodes --sync: %s in %s already current." % (BLOCK, rel))
        return 0
    with open(SKILL_MD, "w", encoding="utf-8") as f:
        f.write(new)
    print("toolmodes --sync: rewrote %s in %s (%d bytes -> %d; %d tool(s) re-run)."
          % (BLOCK, rel, len(src), len(new), len(rows)))
    return 0


def cmd_check(rows, autosync=False):
    """DRIFT GATE — exit 1 unless the committed block is what `--sync` would write.

    ⚑⚑⚑ `--autosync` REPAIRS THE DRIFT AND STILL EXITS 1, AND THE STILL IS THE WHOLE
    DESIGN.  A gate that silently fixes what it measures is not a gate — it is an
    unconditional pass with a side effect, and the next reader inherits a green census
    that never verified anything.  The staleness was a FACT about the working tree at
    the moment of the check; repairing it does not un-happen it, and the commit that
    triggered it still needs the regenerated block STAGED.  So this changes the amount
    of typing, never the verdict.

    ⚑⚑ WHICH IS ALSO WHY IT IS OPT-IN AND NOT THE DEFAULT.  `--check` runs in
    pre-commit.  If it repaired by default, a tree could not be checked without being
    MUTATED, and a read mode that writes is the thing this repo's mutation-intent rule
    exists to forbid (`edit_snapshot.require_explicit_mutation` — no default-dry, no
    default-apply, state one).  `--autosync` IS that statement, made per invocation.

    ⚑ THE REPAIR IS REPORTED, NEVER SILENT.  A caller reading only the exit code learns
    nothing new; a caller reading the output is told the block was rewritten and must be
    staged.  An autosync that fails to write is worse than no autosync, so its own
    failure is surfaced rather than swallowed into the drift verdict it was handling.
    """
    import difflib
    with open(SKILL_MD, encoding="utf-8") as f:
        src = f.read()
    fresh = render_block(rows)
    rel = os.path.relpath(SKILL_MD, ROOT)
    if splice(src, fresh) == src:
        uni = _universal(rows)
        print("toolmodes --check: %s in %s fresh (%d documented, %d undocumented, "
              "%d tool(s))."
              % (BLOCK, rel, sum(len(r["modes"]) for _a, _p, r in rows),
                 sum(len(_invisible(r, uni)) for _a, _p, r in rows), len(rows)))
        return 0
    # ⚑ PRINT THE DIFFERENCE, NOT JUST THE VERDICT.  "Stale" without the delta makes
    # the reader re-run --sync and read `git diff` to learn what changed — two steps
    # in the turn for a fact the gate already holds.
    for line in difflib.unified_diff(current_body(src).splitlines(),
                                     ("\n" + fresh + "\n").splitlines(),
                                     fromfile="%s (%s, committed)" % (rel, BLOCK),
                                     tofile="%s (derived just now)" % BLOCK,
                                     lineterm=""):
        print(line)
    if not autosync:
        print("\ntoolmodes --check: %s in %s is STALE — run "
              "`python3 scratch/toolmodes.py --sync`\n"
              "  (or re-run with --autosync to regenerate it now; the gate still "
              "FAILS — the block must be staged)"
              % (BLOCK, rel), file=sys.stderr)
        return 1
    rc = cmd_sync(rows)
    if rc != 0:
        # ⚑ A FAILED REPAIR MUST NOT HIDE INSIDE THE DRIFT VERDICT.  Both are exit 1,
        # so without this line the operator cannot tell "stale, and I fixed it" from
        # "stale, and I could not" — two states needing different next actions.
        print("\ntoolmodes --check --autosync: %s in %s is STALE and the regeneration "
              "FAILED — fix that first." % (BLOCK, rel), file=sys.stderr)
        return rc
    print("\ntoolmodes --check --autosync: %s in %s was STALE and has been "
          "REGENERATED.\n  ⚑ The gate still FAILS: staleness was a fact about the tree "
          "at check time, and\n     repairing it does not un-happen it. STAGE the "
          "rewritten block, then re-run." % (BLOCK, rel), file=sys.stderr)
    return 1


#: The third-party software this toolkit's answers depend on.  ⚑ A NAME PLUS HOW TO READ
#: ITS VERSION — never a version literal, because a literal is the thing that rots.
DEPS = (
    ("libcst", "pycodemod", "python", "the CST parser; `pycodemod` degrades to "
     "'FAIL libcst not importable' without it"),
    ("panflute", "mdstruct", "python", "the pandoc AST binding"),
    ("pandoc", "mdstruct", "binary", "⚑ OUTSIDE EVERY LOCKFILE — a system binary, so it "
     "is the version most likely to differ between an owner and a borrower"),
)


def deps():
    """[(name, tool, kind, version, why)] — what this toolkit is TESTED AGAINST, measured.

    ⚑⚑⚑ BUILT BECAUSE A BORROWER ASKED FOR A COMPARE-SURFACE AND I ALMOST HAND-TYPED ONE.
    cassian-observability adopted `mdstruct`/`pycodemod` by symlink but kept its OWN venv,
    pinned via its `uv.lock` — a deliberate, reasoned exception to
    `friction-borrowed-tool-needs-its-owners-interpreter`. It then named the one live risk
    in its own choice: *"your pins are now a claim about what mdstruct is tested against,
    and I don't publish that."* Without a published surface, a drift between its pins and
    my tested set is INVISIBLE to both of us until something breaks.

    ⚑⚑ SO THE ANSWER MUST BE DERIVED, NOT TRANSCRIBED. I read three versions by hand
    (`libcst 1.9.0`, `panflute 2.3.1`, `pandoc 3.8.3`) and was about to paste them into a
    registry record — which is exactly the hand-quoted figure this repo keeps paying for,
    and it would go stale on the next `uv sync` with nothing to say so. A version literal
    in a document is a claim that decays silently; a MODE re-derives it on every run.

    ⚑ `pandoc` IS THE ONE THAT MATTERS MOST AND IS IN NO LOCKFILE. `libcst`/`panflute` are
    pinned by `uv.lock` on both sides; `pandoc` is a system binary, so it is the version an
    owner and a borrower are most likely to differ on — and `mdstruct` shells to it for
    every AST read. Omitting it would publish an incomplete compare-surface that LOOKS
    complete, which is worse than publishing none.

    Reports UNKNOWN for anything it cannot read, never a guess — a borrower comparing
    against a guessed version is worse off than one told the owner cannot see it.
    """
    import subprocess as _sp
    out = []
    for name, tool, kind, why in DEPS:
        ver = "UNKNOWN"
        try:
            if kind == "python":
                r = _sp.run([sys.executable, "-c",
                             "import importlib.metadata as m;print(m.version(%r))" % name],
                            capture_output=True, text=True, timeout=60)
                if r.returncode == 0 and r.stdout.strip():
                    ver = r.stdout.strip()
            else:
                r = _sp.run([name, "--version"], capture_output=True, text=True,
                            timeout=60)
                if r.returncode == 0 and r.stdout.strip():
                    ver = r.stdout.split("\n", 1)[0].split()[-1]
        except Exception:
            pass                     # UNKNOWN stands — see the docstring
        out.append((name, tool, kind, ver, why))
    return out


USAGE = __doc__


def main(argv):
    args = argv[1:]
    if not args:
        print(USAGE, file=sys.stderr)
        return 2
    flag = args[0]
    if flag == "--deps":
        rows = deps()
        for name, tool, kind, ver, why in rows:
            print("  %-10s %-10s %-8s %s" % (name, ver, kind, tool))
            print("             %s" % why)
        unknown = [r for r in rows if r[3] == "UNKNOWN"]
        print("%d dependency/dependencies; %d UNKNOWN"
              % (len(rows), len(unknown)))
        # ⚑ THE COMPARE-SURFACE THIS EXISTS TO BE, SAID OUT LOUD.  A borrower running its
        # own pinned environment (cassian-observability, deliberately) has no way to tell
        # its lock apart from what these tools are TESTED against unless the owner
        # publishes it. This is that publication, re-derived per run so it cannot rot the
        # way a version pasted into a registry record would.
        print("   ⚑ TESTED-AGAINST, not required-minimum: a borrower whose pins differ is "
              "not\n     broken, but the difference is now VISIBLE rather than silent. "
              "`pandoc` is in\n     no lockfile on either side and is the most likely to "
              "diverge.")
        if unknown:
            # an UNKNOWN is a fact about THIS machine, never about the dependency
            print("   ⚑ UNKNOWN means this run could not read the version — a fact about "
                  "this\n     environment, not a claim the dependency is absent.")
        return 0
    if flag == "--declines":
        # ⚑ ITS OWN BRANCH BECAUSE IT TAKES NO CENSUS.  A decline is a claim about a READING,
        # not about the mode roster, so building the tool census for it would be paying a
        # corpus walk to answer a question that does not consult one.
        return cmd_declines(args[1:])
    if flag == "--find":
        # ⚑ `--top` IS A MODIFIER ON `--find`, and it is parsed HERE rather than in `cmd_find`
        # so the needle is never mistaken for it: `--find --top` would otherwise search for
        # the literal string "--top". Same shape as `--autosync` on `--check`.
        rest, top = [a for a in args[1:] if a != "--top"], None
        if "--top" in args:
            i = args.index("--top")
            if i + 1 >= len(args) or not args[i + 1].lstrip("-").isdigit():
                print("toolmodes: --top takes a COUNT (--top 0 = every row)", file=sys.stderr)
                return 2
            top = int(args[i + 1])
            if top < 0:
                # ⚑ A NEGATIVE WOULD SLICE FROM THE END — `fns[:-3]` silently drops the LAST
                # three rows and prints a truncation notice about the wrong end of the list.
                # Refused rather than clamped: the caller meant something this cannot do.
                print("toolmodes: --top must be >= 0 (0 = every row)", file=sys.stderr)
                return 2
            rest = [a for a in rest if a != args[i + 1]]
        if not rest:
            print("usage: toolmodes.py --find <name> [--top N]  (--top 0 = every row)",
                  file=sys.stderr)
            return 2
        return cmd_find(census(), rest[0], top=top)
    # ⚑ SAME TREATMENT AS `--autosync` / `--quick`: a modifier carries no verdict of its own,
    # so on any other mode it is a typo the caller should hear about rather than a flag
    # silently ignored. This branch sits AFTER `--find` has returned, so it only sees misuse.
    if "--top" in args:
        print("toolmodes: --top is a modifier on --find, not a mode (got %s)" % flag,
              file=sys.stderr)
        return 2
    disp = {"--all": cmd_all, "--collisions": cmd_collisions,
            "--siblings": cmd_siblings, "--gaps": cmd_gaps,
            "--divergence": cmd_divergence, "--conventions": cmd_conventions,
            "--nearmiss": cmd_nearmiss,
            "--sync": cmd_sync, "--check": cmd_check}
    # ⚑⚑ THE TOOL THAT MEASURES DISPATCH HYGIENE ACROSS 82 TOOLS WAS NOT SUBJECT TO IT.
    # `disp[flag](census())` below passes NOTHING from `args[1:]`, so every census mode
    # ACCEPTED AND SILENTLY DISCARDED any operand: `--divergence scratch/pipeflow.py`
    # printed the whole-corpus census, byte-identical to the bare call, while reading
    # exactly like a scoped one. MEASURED 2026-08-24 — the caller (me) believed the
    # census had been narrowed to one tool and reasoned from a corpus-wide answer.
    #
    # ⚑ AND THE SILENT-DROP IS THE WORSE HALF, not the missing scope. A refused operand
    # sends the caller to look for the mode that scopes; an accepted-and-ignored one
    # returns a plausible answer to a question nobody asked. So this REFUSES rather than
    # implementing scoping: `_invisible`/`_universal` are corpus-relative predicates (a
    # flag is "universal" only against the full population), so a per-tool census would
    # be a DIFFERENT statistic wearing the same mode name — the two-spelling defect this
    # file's own gate exists to prevent. Scoping is WORK, and it needs its own mode name.
    #
    # ⚑ `check_argv` COVERS THE FLAG HALF ONLY. It refuses an unrecognised `--flag` by
    # set membership and says so in its own docstring; a bare PATH does not start with
    # `-` and passes straight through. Both halves are needed, which is why the operand
    # check sits here rather than being delegated.
    # ⚑ `--list` IS A MODIFIER ON `--nearmiss` (the shape `--autosync`/`--quick`/`--top`
    # already have here): it enumerates the census instead of comparing it to the
    # baseline.  `set_ratchet` owns the behaviour; this only has to admit the spelling.
    _known = (set(disp) | {"--deps", "--declines", "--find", "--top", "--autosync",
                           "--quick", "--selftest", "--list"})
    if (rc := _ratchet.check_argv(args, _known, "toolmodes.py")) is not None:
        return rc
    if flag in disp and (operands := [a for a in args[1:] if not a.startswith("-")]):
        print("toolmodes: %s takes no operand (got %s) — this census is CORPUS-WIDE; "
              "it is not scoped by a path." % (flag, " ".join(operands)), file=sys.stderr)
        print("  Refusing rather than discarding it: a silently-ignored operand returns "
              "a whole-corpus answer that reads as a scoped one.", file=sys.stderr)
        return 2
    # ⚑ `--autosync` IS A MODIFIER ON `--check`, NOT A MODE.  It carries no verdict of
    # its own; on any other mode it is a typo the caller should hear about, not a flag
    # silently ignored — the unknown-flag class `ratchet.check_argv` exists to refuse.
    autosync = "--autosync" in args
    if autosync and flag != "--check":
        print("toolmodes: --autosync is a modifier on --check, not a mode "
              "(got %s)" % flag, file=sys.stderr)
        return 2
    # ⚑ SAME TREATMENT FOR `--quick`, AND THE SELFTEST IS WHY IT IS HERE. Documenting it on
    # its own usage line made the coherence gate read it as a MODE and report it undispatched
    # — correctly. A modifier carries no verdict of its own, so on any other mode it is a typo
    # the caller should hear about, not a flag silently ignored.
    if "--quick" in args and flag != "--declines":
        print("toolmodes: --quick is a modifier on --declines, not a mode "
              "(got %s)" % flag, file=sys.stderr)
        return 2
    if flag == "--check":
        try:
            return cmd_check(census(), autosync=autosync)
        except BlockError as e:
            print("toolmodes --check: %s" % e, file=sys.stderr)
            return 1
    if flag in disp:
        # ⚑ A MISSING/MALFORMED MARKER PAIR EXITS 1, NOT 2.  Exit 2 is this tool's
        # USAGE code (the caller typed something wrong); markers are a fact about the
        # TREE, and `--check` reporting it as a usage error would let a gate that
        # cannot verify anything be read as a gate that was invoked badly.
        try:
            return disp[flag](census())
        except BlockError as e:
            print("toolmodes %s: %s" % (flag, e), file=sys.stderr)
            return 1
    print(USAGE, file=sys.stderr)
    return 2


# ─────────────────────────────────────────────────────────────────────────────
def _selftest():
    cases, ok = [], 0

    def check(name, got, want):
        nonlocal ok
        cases.append(name)
        if got == want:
            ok += 1
        else:
            print(f"  FAIL {name}: got {got!r} want {want!r}")

    # ── the usage-line parse, against the EXACT shapes the live tools print ───
    # ⚑ EVERY CASE BELOW IS A SHAPE A PLAUSIBLE PARSER GETS WRONG, and each is
    # copied from a real tool's bare output rather than invented.

    # ⚑ FAILS against "every --flag on the line is a mode": that reads THREE.
    md = parse_usage(
        "    mdstruct.py --rows <file> [--table N] [--where <substr>]\n"
        "                                      # the table CELLS — the row-level\n"
        "                                      # read that makes it queryable\n",
        "mdstruct.py")
    check("bracketed options are NOT modes", sorted(md), ["--rows"])

    # ── the near-miss ratchet (Ⓐ47 ⟡dry-spelling-ratchet) ─────────────────────
    # ⚑⚑⚑ THE POSITIVE CONTROL IS THE POINT, AND WITHOUT IT THE ZERO IS UNREADABLE.
    # The live census returns 0 near-miss flags, and `census-green-is-a-fact-about-the-
    # census` says that reports the boundary of what the instrument can SEE. A false
    # positive gets investigated; a false ZERO gets banked. So the detector is starved
    # in both directions here: a synthetic tool spelling `--dryrun` MUST be caught, and
    # one spelling the declared words MUST NOT be.
    _fake = {"accepts": {"--dryrun", "--apply"}, "modes": {}}
    check("nearmiss: an UNSEEN spelling is caught (not a table lookup)",
          sorted(f for f, _p in near_misses([("a", "fake_tool.py", _fake)])
                 .get("fake_tool.py", [])),
          ["--dryrun"])
    _clean = {"accepts": {"--apply", "--dry-run"}, "modes": {}}
    check("nearmiss: the DECLARED pair is never a near miss of itself",
          near_misses([("a", "clean_tool.py", _clean)]), {})
    # ⚑ `--dry` IS THE INCIDENT ITSELF, and it is distance 4 from `--dry-run` — past any
    # threshold tight enough to avoid false positives. It is admitted by the PREFIX arm,
    # which is why that arm exists rather than a looser distance.
    _dry = {"accepts": {"--dry"}, "modes": {}}
    check("nearmiss: `--dry` is caught by the PREFIX arm, not by distance",
          sorted(f for f, _p in near_misses([("a", "dry_tool.py", _dry)])
                 .get("dry_tool.py", [])),
          ["--dry"])
    # ⚑ AND A FLAG THAT IS SIMPLY A DIFFERENT WORD IS *NOT* CAUGHT — the SYNONYM class
    # is outside this guard's reach, and pinning it stops a later reader reading the
    # zero as full coverage.
    _syn = {"accepts": {"--preview"}, "modes": {}}
    check("nearmiss: a SYNONYM is out of reach (the stated floor, pinned)",
          near_misses([("a", "syn_tool.py", _syn)]), {})
    check("the gloss continues across `#` lines",
          "row-level read" in md["--rows"]["gloss"], True)
    check("the signature is the UNBRACKETED placeholders",
          md["--rows"]["sig"], ("<file>",))

    # ⚑ FAILS against "the mode is the token right after the basename": a
    # positional precedes it here.
    ts = parse_usage(
        "    transcriptstruct.py <file> --grep-content <regex> [--role user]\n",
        "transcriptstruct.py")
    check("a mode after a positional is still found", sorted(ts), ["--grep-content"])

    # ⚑ FAILS against "one mode per usage line": pycodemod documents two.
    pc = parse_usage(
        "    pycodemod.py --shape / --shape-all   # the record shape a reader assumes\n",
        "pycodemod.py")
    check("two modes on one usage line are both kept",
          sorted(pc), ["--shape", "--shape-all"])

    # ⚑ FAILS against "a mode must start with --": agda_defs' primary mode is
    # POSITIONAL, and dropping it loses the mode an operator reaches for first.
    ad = parse_usage(
        "usage: agda_defs.py <name> ...        # where does this name live?\n"
        "       agda_defs.py --provides <Mod>  # what does this module define?\n",
        "agda_defs.py")
    check("a positional primary mode is recorded",
          sorted(ad), ["(positional)", "--provides"])
    check("and it keeps its gloss",
          "where does this name live" in ad["(positional)"]["gloss"], True)

    # ⚑ FAILS against "the basename matches as a substring": the decomposed
    # implementation modules would each look like a usage line.
    check("a decomposed sibling is not read as a usage line",
          parse_usage("import _pycodemod_query.py --nope <x>\n", "pycodemod.py"), {})
    # a bare prose mention with no arguments is not a usage line either
    check("a bare prose mention is not a usage line",
          parse_usage("see scratch/mdstruct.py for the normalizer\n",
                      "mdstruct.py"), {})

    # ⚑ FAILS against "`#` separates the gloss": `bibstruct` COLUMN-ALIGNS its
    # glosses instead.  Partitioning on `#` alone left all six of its modes with an
    # empty gloss AND fabricated their signatures out of the prose — `--field
    # <name> [bib]   which entries set <name>` parsed as taking TWO `<name>`s, and
    # the signature is what `--siblings` and `--gaps` are computed from.
    bs = parse_usage(
        "    bibstruct.py --field <name> [bib]   which entries set <name>, "
        "and to what\n", "bibstruct.py")
    check("a column-aligned gloss is read", sorted(bs), ["--field"])
    check("and it does NOT leak into the signature",
          bs["--field"]["sig"], ("<name>",))
    check("the column-aligned gloss text survives",
          bs["--field"]["gloss"], "which entries set <name>, and to what")
    # ⚑ FAILS against the column rule alone.  `bibstruct` separates THIS gloss with
    # a SINGLE space, so no column break exists to cut at — and the gloss's own
    # `<key>` then became a second argument, inventing a two-argument signature for
    # a one-argument mode.  The grammar cut is what catches it.
    bm = parse_usage(
        "    bibstruct.py --mentions <key> [bib] whose PROSE names <key> — "
        "edge evidence\n", "bibstruct.py")
    check("a single-space gloss is cut by the argument GRAMMAR",
          bm["--mentions"]["sig"], ("<key>",))
    check("and its prose is recovered as the gloss",
          bm["--mentions"]["gloss"].startswith("whose PROSE names"), True)
    # ⚑ AND THE GRAMMAR CUT MUST NOT EAT A REAL ARGUMENT LIST — `/` and a
    # bracketed ellipsis are argument syntax, not prose.
    check("`/` between two modes is argument syntax, not prose",
          sorted(parse_usage("    pycodemod.py --shape / --shape-all   # x\n",
                             "pycodemod.py")), ["--shape", "--shape-all"])
    check("a bracketed ellipsis is argument syntax",
          parse_usage("    transcriptstruct.py <file> --extract <n> [<n> ...]\n",
                      "transcriptstruct.py")["--extract"]["sig"],
          ("<file>", "<n>"))
    # and the `#` form is unharmed by the column rule
    check("a `#` gloss still wins when it comes first",
          parse_usage("    pycodemod.py --dead [paths]          # every def in the "
                      "corpus with no caller\n", "pycodemod.py")["--dead"]["gloss"],
          "every def in the corpus with no caller")

    # ── the argparse `options:` block — the second, fuller authority ──────────
    # ⚑ FAILS against "the docstring list is the mode list": tsdbprobe's curated
    # list omits `--ping`, which only the generated block carries.
    op = parse_options(
        "options:\n"
        "  -h, --help            show this help message and exit\n"
        "  --base BASE           store base URL (default http://127.0.0.1:8428)\n"
        "  --verify SELECTOR VALUE\n"
        "                        read-your-write: poll until SELECTOR returns VALUE\n"
        "  --ping                write a value we choose and read it back\n")
    check("argparse options are parsed", "--ping" in op, True)

    # ── a `modes:` roster is the SAME STRUCTURE under a different word ────────
    # ⚑ FAILS against `_OPTHEAD = (options|optional arguments)`: `scripts/gate_census.py`
    # publishes a textbook two-column roster under `modes:`, and ALL FIVE of its modes
    # read as UNDOCUMENTED for as long as they existed.  The file was never malformed —
    # the parser's expectation was the narrower thing, and a `modes:` header factors the
    # tool name out of every row, which is the MORE readable form.
    _gc = parse_options(
        "modes:\n"
        "  --baselines  per-ratchet baseline health (exists? empty? how many keys)\n"
        "  --init-absent  create every ABSENT baseline as a zero-byte file (ABSENT → EMPTY:\n"
        "               zero-tolerance, nothing grandfathered). MUTATES — state --apply or\n"
        "               --dry-run. Never touches an `ok` or EMPTY baseline.\n"
        "  --check      DRIFT GATE: exit 1 unless the STRUCTURAL block is current\n")
    check("a `modes:` roster is read like an `options:` one",
          sorted(_gc), ["--baselines", "--check", "--init-absent"])
    check("and its wrapped gloss is joined",
          "nothing grandfathered" in _gc["--init-absent"], True)
    # the live file, not only the fixture — the census must actually see it now
    _live = census_row_modes("scripts/gate_census.py")
    check("gate_census's five modes are DECLARED, not undocumented",
          sorted(_live) == ["--baselines", "--check", "--init-absent",
                            "--selftest", "--successors", "--sync"]
          or all(f in _live for f in ("--baselines", "--check", "--init-absent",
                                      "--successors", "--sync")), True)

    # ── COULD-NOT-PARSE is a THIRD verdict, distinct from NO-SELF-DESCRIPTION ──
    # ⚑⚑ THE DISTINCTION IS THE DELIVERABLE.  A false UNDOCUMENTED and a true one are
    # indistinguishable to a reader, and the false one sends them to write documentation
    # that already exists.  `described == False` must therefore never stand alone.
    check("a roster under an UNRECOGNISED header yields a could-not-parse witness",
          bool(_unparsed_roster(
              "commands:\n"
              "  --alpha   do the alpha thing\n"
              "  --beta    do the beta thing\n")), True)
    check("...and the witness NAMES the header it choked on",
          "commands" in _unparsed_roster(
              "commands:\n"
              "  --alpha   do the alpha thing\n"
              "  --beta    do the beta thing\n"), True)
    # ⚑ AND IT MUST NOT MANUFACTURE AN EXCUSE.  A tool that genuinely publishes nothing
    # (agda_lex prints its selftest) keeps the honest NO SELF-DESCRIPTION; inventing a
    # parser failure for it is the MIRROR defect — the method flattering itself.
    check("a tool that truly publishes nothing gets NO witness",
          _unparsed_roster("running 12 cases\nall passed\n"), "")
    check("one lone flag row is not a roster (a coincidence, not a block)",
          _unparsed_roster("stuff:\n  --alpha   the only one\n"), "")
    check("an `options:` block is not reported as unparsed — the parser reads it",
          _unparsed_roster("options:\n  --alpha  a\n  --beta   b\n"), "")
    check("a wrapped argparse gloss is joined",
          "poll until SELECTOR" in op["--verify"], True)
    check("`-h, --help` is read as --help", "--help" in op, True)

    # ── a bracketed flag is a declared OPTION, not an undeclared mention ──────
    # ⚑ FAILS against subtracting only the MODES from a tool's prose mentions:
    # `--table`/`--where` are declared right there in the usage line, and reporting
    # them as "named by a tool and declared by nothing" turned eight existing
    # options into phantom filed gaps.
    _line = ("    mdstruct.py --rows <file> [--table N] [--where <substr>]\n")
    check("bracketed flags are collected as options",
          bracketed_options(_line, "mdstruct.py"), {"--table", "--where"})
    check("and the unbracketed mode is NOT an option",
          "--rows" in bracketed_options(_line, "mdstruct.py"), False)
    # ⚑ AND AN OPTION DECLARED IN BRACKETS ON A *DIFFERENT* MODE'S LINE STILL
    # COUNTS AS DOCUMENTED — `agda_defs.py --closure <Mod> [--prefix <Pfx>]`.
    check("an option on another mode's line is collected too",
          bracketed_options("       agda_defs.py --closure <Mod> [--prefix <Pfx>]\n",
                            "agda_defs.py"), {"--prefix"})

    # ── brackets nest ────────────────────────────────────────────────────────
    check("nested brackets are stripped whole",
          _outside_brackets("x [--names [SUBSTR]] y").split(), ["x", "y"])

    # ── flag literals come from the AST, one hop through local imports ────────
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "helper.py"), "w").write(
            'import sys\ndef go(a):\n    return "--deep" in sys.argv\n')
        entry = os.path.join(td, "entry.py")
        open(entry, "w").write(
            'import helper\nimport os, subprocess\n'
            'if "--shallow" in os.sys.argv:\n    helper.go([])\n'
            'subprocess.run(["mypy", "--ignore-missing-imports", "x"])\n'
            'if "--without-K" in open("f").read():\n    pass\n')
        acc, lit = literal_flags(entry)
        check("a flag dispatched on argv is accepted", "--shallow" in acc, True)
        # ⚑ FAILS against a single-module AST walk — and that failure would report
        # nearly every documented mode of a DECOMPOSED tool as unbacked.
        check("a flag dispatched in a same-dir import is found too",
              "--deep" in acc, True)
        # ⚑ FAILS against "every flag-shaped literal is a mode", which credited
        # `pycodemod` with mypy's flags, `mdstruct` with git's, and `agda_defs`
        # with the Agda pragma it SEARCHES FOR — 55 phantom "undocumented modes".
        check("a flag PASSED to a subprocess is not accepted",
              "--ignore-missing-imports" in acc, False)
        check("a flag matched against FILE TEXT is not accepted (not argv)",
              "--without-K" in acc, False)
        # ⚑ FAILS against anchoring on the SPELLING `sys.argv`.  Found by running
        # the census against THIS tool: `args = argv[1:]; flag = args[0];
        # flag == "--find"` reported `--find` as an UNBACKED documented mode — a
        # limit of the detector reported as a defect in the tool.
        chain = os.path.join(td, "chain.py")
        open(chain, "w").write(
            'import sys\nargs = sys.argv[1:]\nflag = args[0]\n'
            'if flag == "--chained":\n    pass\n')
        check("an argv ALIAS CHAIN is followed (argv → args → flag)",
              "--chained" in literal_flags(chain)[0], True)
        # and it must still not admit an unrelated local
        other = os.path.join(td, "other.py")
        open(other, "w").write('cfg = open("f").read()\n'
                               'if cfg == "--nope":\n    pass\n')
        check("a non-argv local is still not an anchor",
              "--nope" in literal_flags(other)[0], False)
        # ...but both are still visible as literals, so `--divergence` can count
        # them rather than silently dropping them
        check("the excluded flags are still reported as literals",
              {"--ignore-missing-imports", "--without-K"} <= lit, True)
        check("a non-flag string is not a flag", "os" in lit, False)
        # ⚑ FAILS against an unconditional one-hop walk.  `agda_lex` imports
        # `agda_defs` — a PEER TOOL — so the hop credited agda_lex with all twelve
        # of agda_defs' modes and reported them as agda_lex's undocumented ones.
        # A module the routing table names is a tool, not an implementation half.
        check("a hop into a PEER TOOL is refused",
              "--deep" in literal_flags(entry, peers=["x/helper.py"])[0], False)
        check("and the entry module's own flags survive that refusal",
              "--shallow" in literal_flags(entry, peers=["x/helper.py"])[0], True)
        # a dispatch TABLE keyed by flags is the other live shape
        tbl = os.path.join(td, "tbl.py")
        open(tbl, "w").write('D = {"--alpha": 1, "--beta": 2}\nE = {"x": 1}\n')
        check("an all-flag dispatch table is accepted",
              literal_flags(tbl)[0], {"--alpha", "--beta"})

    # ⚑ THE FUNCTION POPULATION, AND THE REINVENTION IT EXISTS TO CATCH.
    # MEASURED 2026-08-17: `cli_flags` was written as a second implementation of
    # `literal_flags` after FOUR well-formed name-keyed searches each returned a
    # TRUE answer and none surfaced it.  `--find` was the one description-keyed
    # instrument and missed only because its population was DECLARED MODES (128)
    # rather than documented functions (~2800) — a ~22x gap.  These cases pin the
    # arm that closes it, against the exact query that failed.
    _fns = _fn_glosses()
    check("the function population is the corpus, not the 9-tool roster",
          len(_fns) > 1000, True)
    _homes = {(r, n) for r, n, _g in _fns}
    check("`literal_flags` is IN the searchable population",
          ("scratch/toolmodes.py", "literal_flags") in _homes, True)
    # ⚑ THE MOTIVATING QUERY, VERBATIM — a description, no knowledge of the name.
    _want = _tokens("flag constants in a tool")
    _hit = [(r, n) for r, n, g in _fns if len(_want & _tokens(g)) >= 2]
    check("a DESCRIPTION finds literal_flags without naming it",
          ("scratch/toolmodes.py", "literal_flags") in _hit, True)
    # ⚑ AND THE STEMMING RIDER IS LOAD-BEARING, NOT COSMETIC.  The query says
    # `flags`, the docstring says `flag`; unstemmed that pair shares ONE content
    # word and falls below the >= 2 threshold, so the search misses its own
    # motivating case by a single plural.
    check("`flags` and `flag` stem to one token", _stem("flags"), _stem("flag"))
    check("...and `ies` pluralisation folds too", _stem("rivalries"), "rivalry")
    # ⚑ CONSERVATIVE BY CONSTRUCTION — over-stemming merges distinct capabilities.
    check("a short word is left alone", _stem("as"), "as")
    check("a double-s word is not singularised", _stem("class"), "class")
    _plural = _tokens("which flags does a tool accept")
    check("the PLURAL query still pairs with the singular gloss",
          len(_plural & _tokens("the `--flag` string constants in a tool's AST")) >= 2,
          True)
    # ⚑ THE POPULATION MUST REACH IMPLEMENTATION MODULES, not just rostered tools.
    # The reinvention lived in `_pycodemod_query.py` — behind a rostered tool, not
    # one of the nine — so a roster-scoped population reproduces the miss.
    check("an implementation module behind a tool is searched",
          any(r.endswith("_pycodemod_query.py") for r, _n, _g in _fns), True)
    check("a private helper is searchable (it is still a capability)",
          any(n.startswith("_") for _r, n, _g in _fns), True)

    # ── the POPULATION is read from the skill's table, not listed here ────────
    pop = roster()
    check("the roster is non-empty", len(pop) > 0, True)
    # ⚑ FAILS against "one tool per table row": the Agda row names TWO, and taking
    # the cell as a path silently drops the second.
    rels = {r for _a, r in pop}
    check("a two-tool table cell yields both tools",
          {"scratch/agda_lex.py", "scratch/agda_defs.py"} <= rels, True)
    check("every rostered tool exists on disk",
          [r for r in rels if not os.path.exists(os.path.join(ROOT, r))], [])

    # ── the GENERATED BLOCK in SKILL.md: --sync / --check ─────────────────────
    # ⚑ AGAINST A SYNTHETIC CENSUS, NOT THE LIVE ONE.  The block's contract is about
    # its SHAPE and its splice algebra, both of which must hold for any corpus; running
    # the seven real tools here would make the suite pay 3s and — worse — make these
    # cases pass or fail on facts about OTHER tools, so a `pycodemod` edit could turn
    # this file's suite red.  Whether the COMMITTED block is current is the `--check`
    # gate's question, and it is asked at the commit, not here.
    def _fixture_rows():
        # ⚑ THREE TOOLS, NOT TWO, AND THAT IS THE POINT OF THE FIXTURE.  With two, the
        # intersection that defines a "convention" swallows `--hidden` as well as
        # `--selftest`, so the universal filter would pass for the wrong reason — the
        # denominator-of-one defect, in the test data instead of the report.
        specs = (("Python", "scratch/alpha.py", ["--calls", "--dead"],
                  ["--calls", "--dead", "--hidden", "--selftest"]),
                 ("markdown", "scratch/beta.py", ["--rows"],
                  ["--rows", "--hidden", "--selftest"]),
                 ("BibTeX", "scratch/gamma.py", ["--stats"],
                  ["--stats", "--selftest"]))
        return [(art, rel, {
            "modes": {m: {"gloss": "g", "sig": (), "sources": {"usage"}} for m in mo},
            "mentioned": set(), "options": set(), "accepts": set(ac),
            "literal": set(mo) | set(ac), "rc": 0, "described": bool(mo),
        }) for art, rel, mo, ac in specs]

    fix = _fixture_rows()
    uni = _universal(fix)
    # ⚑ FAILS against inlining the predicate in `--divergence` (as it was): the gate's
    # undocumented count and the published block's would then be free to disagree.
    check("a flag EVERY tool accepts is a convention, not an undocumented mode",
          "--selftest" in _invisible(fix[0][2], uni), False)
    check("a flag only SOME tools accept is undocumented",
          "--hidden" in _invisible(fix[0][2], uni), True)

    # ⚑⚑⚑ Ⓜ10 / ⟡fixture-category — THE EXEMPTION PATH, DRIVEN. An exemption nobody
    # exercises is the most dangerous kind of code in a ratchet: it is reached only when a
    # tool declares a fixture, so a regression here is silent until it silently forgives
    # real debt. `--selftest-demo-failure` is the live motivating case (`sppf_db`), but it
    # lives in another agent's file, so the MECHANISM is pinned against constructed rows
    # and the live row remains honest debt until its owner declares it.
    #
    # ⚑ ALL FOUR DIRECTIONS, because three of them are ways to grant an exemption by
    # accident: no mark at all, a mark naming an undispatched flag, and an unreadable
    # source must each declare NOTHING, while only a marked-and-dispatched flag is exempt.
    _fx_base = {"modes": {}, "mentioned": set(), "options": set(),
                "literal": set(), "rc": 0, "described": True}
    _fx_marked = dict(_fx_base, accepts={"--demo-failure", "--real"},
                      source='if "--demo-failure" in sys.argv:  # %s\n' % FIXTURE_MARK)
    check("a flag the owning tool MARKS is a declared fixture",
          _fixtures(_fx_marked), {"--demo-failure"})
    check("...and a sibling flag on the same tool is NOT swept in",
          "--real" in _fixtures(_fx_marked), False)
    # ⚑ THE MARK CANNOT MINT AN EXEMPTION FOR A FLAG THE TOOL DOES NOT DISPATCH — else a
    # comment becomes a way to pre-silence debt that has not been incurred yet.
    check("⚑ a mark naming an UNDISPATCHED flag declares nothing",
          _fixtures(dict(_fx_base, accepts={"--real"},
                         source="# --ghost %s\n" % FIXTURE_MARK)), set())
    # ⚑ AND AN UNREADABLE TOOL LOSES ITS EXEMPTIONS RATHER THAN GAINING THEM — the fail
    # direction that matters, pinned so a future `_read_source` change cannot invert it.
    check("⚑ no source means no fixtures — a read failure never grants an exemption",
          _fixtures(dict(_fx_base, accepts={"--real"}, source="")), set())
    # ⚑ AND THE KIND MUST REACH THE CENSUS, not just the predicate: the gate keys on the
    # string `"FIXTURE"`, so a rename here that missed the gate would exempt nothing.
    # ⚑⚑ THREE TOOLS, FOR THE REASON `_fixture_rows` ALREADY STATES — and my first cut had
    # ONE and returned `None`, because `_universal` makes every flag in a one-tool
    # population a "convention" and `_invisible` then yields nothing at all. The
    # denominator-of-one defect, reproduced in the test data of the very census that
    # documents it. Two peers must NOT carry the fixture flag, or it becomes universal.
    _fx_peer = lambda rel: (  # noqa: E731 — three near-identical rows, inline is clearer
        "Python", rel, dict(_fx_base, accepts={"--common"}, literal={"--common"}))
    _fx_rows = [("Python", "scratch/fx.py",
                 dict(_fx_base, accepts={"--demo-failure", "--common"},
                      source='if "--demo-failure" in sys.argv:  # %s\n' % FIXTURE_MARK)),
                _fx_peer("scratch/fy.py"), _fx_peer("scratch/fz.py")]
    _fx_cur = divergence_census(_fx_rows)
    check("the census emits FIXTURE as its own kind, never dropping the row",
          _fx_cur.get("scratch/fx.py --demo-failure"), "FIXTURE")
    # ⚑ AND AN UNMARKED UNDOCUMENTED FLAG ON THE SAME TOOL STAYS UNDOCUMENTED — the case
    # that proves the exemption is scoped to the mark rather than to the tool.
    check("...while an unmarked flag on that same tool stays UNDOCUMENTED",
          divergence_census(
              [("Python", "scratch/fx.py",
                dict(_fx_base, accepts={"--demo-failure", "--plain", "--common"},
                     source='if "--demo-failure" in sys.argv:  # %s\n' % FIXTURE_MARK)),
               _fx_peer("scratch/fy.py"), _fx_peer("scratch/fz.py")]
          ).get("scratch/fx.py --plain"), "UNDOCUMENTED")

    # ⚑⚑⚑ ⟡divergence-citations — A CROSS-REFERENCE IS NOT DEBT, AND THE CENSUS SAID IT
    # WAS. `--find telescope` printed, in ONE run, that `agda_defs` declares `--telescope`
    # `[optlist+usage]` AND that `--telescope` (named by `split_inner_module`) is "declared
    # by NO tool". The by-name arm read the global index; the prose arm read only the
    # citing tool's own record, so a flag another tool owned came back unowned. `cmd_gaps`
    # had resolved the same predicate against the same index all along — two arms of one
    # census disagreeing, each internally consistent, which is this file's recurring shape.
    #
    # ⚑ THE STAKES ARE INVERTED, WHICH IS WHY THIS IS PINNED RATHER THAN JUST FIXED. The
    # standing rule requires the tools to cross-reference each other so they are
    # discoverable; a paydown driven by the broken reading DELETES those sentences. A
    # remedy scored as a defect is worse than an unscored defect.
    _ct_base = {"accepts": set(), "options": set(), "literal": set(), "rc": 0,
                "described": True, "source": ""}
    _ct_owner = ("Agda", "scratch/owner.py",
                 dict(_ct_base, mentioned=set(),
                      modes={"--telescope": {"gloss": "the contract", "sig": (),
                                             "sources": {"usage"}}}))
    _ct_citer = ("Python", "scratch/citer.py",
                 dict(_ct_base, modes={}, mentioned={"--telescope"},
                      source="print('verified by `owner --telescope`')\n"))
    _ct = _citations([_ct_owner, _ct_citer])
    check("⚑ a flag ANOTHER tool declares is a CITATION, not 'declared by NO tool'",
          _ct.get(("scratch/citer.py", "--telescope")),
          ("CITATION", ["scratch/owner.py"]))
    # ⚑ THE SECOND VERDICT IS THE UNDECIDABLE ONE, AND COLLAPSING IT INTO THE FIRST WOULD
    # BE A GUESS. A bare `--binding` in a sentence whose SUBJECT is the tool names no
    # owner on its own line; the census reports that it cannot tell, rather than picking.
    _ct_bare = ("Python", "scratch/bare.py",
                dict(_ct_base, modes={}, mentioned={"--telescope"},
                     source="print('see --telescope for the contract')\n"))
    check("...and a citation naming NO owner on the citing line is CITATION?",
          _citations([_ct_owner, _ct_bare]).get(("scratch/bare.py", "--telescope")),
          ("CITATION?", ["scratch/owner.py"]))
    # ⚑ A FLAG NOBODY DECLARES IS STILL A REAL GAP — the direction that must NOT move, or
    # the fix becomes a way to launder undeclared modes into "cross-references".
    check("⚑ a flag NO tool declares is NOT a citation (the gap class is preserved)",
          _citations([_ct_owner,
                      ("Python", "scratch/g.py",
                       dict(_ct_base, modes={}, mentioned={"--nowhere"}))]), {})
    # ⚑ AND A TOOL CITING ITS OWN MODE IS NOT A CROSS-REFERENCE. `owners` excludes the
    # citing tool, so a self-mention can never manufacture an exemption for its own debt.
    check("⚑ a tool naming its OWN declared mode is not a citation",
          _citations([("Agda", "scratch/owner.py",
                       dict(_ct_owner[2], mentioned={"--telescope"}))]), {})

    # ⚑⚑ THE `CONVENTIONS` RECORDS MUST BE FALSIFIABLE, WHICH IS THE WHOLE POINT OF
    # MODELLING THEM ON `farm.py`'s `Arm`.  An F-arm declares the message its mutation
    # must provoke so a red "for another reason" reports VACUOUS instead of counting as
    # a pass; a `Convention` declares a shared meaning, so it must be measurable against
    # what tools actually accept — otherwise it is prose in a class named for refusing
    # prose.  `cmd_conventions` reports STALE (no tool accepts it) and SOLO (exactly
    # one does); these pin both verdicts against constructed rows rather than the live
    # census, so they cannot pass because today's tree happens to agree.
    _cf = [("x", "scratch/a.py", {"modes": {}, "accepts": {"--selftest", "--only-here"},
                                  "mentioned": set(), "options": set(), "literal": set(),
                                  "rc": 0, "described": True}),
           ("y", "scratch/b.py", {"modes": {}, "accepts": {"--selftest"},
                                  "mentioned": set(), "options": set(), "literal": set(),
                                  "rc": 0, "described": True})]
    _acc = {}
    for _a, _r, _rec in _cf:
        for _f in _rec["accepts"] | set(_rec["modes"]):
            _acc.setdefault(_f, []).append(_r)
    check("a declared convention NO tool accepts is STALE",
          _acc.get("--vanished", []), [])
    check("a declared convention exactly ONE tool accepts is SOLO",
          len(_acc["--only-here"]), 1)
    check("...and one SEVERAL accept is SHARED", len(_acc["--selftest"]), 2)
    # ⚑ AND THE PROJECTION MUST NOT DRIFT FROM THE RECORDS.  `HARNESS_CONTRACTS` is a
    # derived set; a second hand-maintained copy beside it is the frozen-roster shape
    # this whole census exists to retire.
    check("HARNESS_CONTRACTS is DERIVED from the records, never a second list",
          HARNESS_CONTRACTS, {c.flag for c in CONVENTIONS})
    # ⚑ EVERY RECORD CARRIES ITS ARGUMENT.  A convention with an empty `why` is the
    # thing `farm.py` refuses — a declaration whose rejected alternative is unstated,
    # so the next reader cannot tell a contract from a coincidence.
    check("every Convention states what it rejects",
          [c.flag for c in CONVENTIONS if not (c.why and c.contract)], [])

    # ── Decline: a claim CONSIDERED AND REFUSED, with the check that fails if it lapses ──
    # ⚑⚑ AN ABSENT ARGUMENT READS AS AN ABSENT OBJECTION. A census reports FOUND and
    # COULD-NOT-READ; neither says "settled, here is why", so a rejected reading is
    # indistinguishable from one nobody thought of. Measured 2026-08-19: an over-broad
    # reading travelled two messages into a peer's tree while the bound sat CERTIFIED in a
    # sibling file, because nothing recorded that it had already been refused.
    check("every Decline states the reading it refuses AND what is true instead",
          [d.claim for d in DECLINES if not (d.claim and d.instead and d.why)], [])
    # ⚑ THE FIELD THAT MAKES IT FALSIFIABLE, and the reason this is not a comment block.
    # `check is None` is LEGAL and reports UNGUARDED — the mode must not hide it, because an
    # unguarded decline is this record type's own defect wearing its clothes.
    check("a Decline may be UNGUARDED, and the type permits saying so",
          Decline("c", "i", None, "w").check, None)
    # ⚑ SAME FAMILY AS Convention/Arm: the load-bearing field is a FALSIFIABLE DISCRIMINATOR,
    # and all three make their own vacuity detectable (Arm VACUOUS / Convention STALE /
    # Decline UNGUARDED). Pinned so a future field addition keeps the parallel.
    check("Decline mirrors Convention's four-field shape",
          len(Decline.__slots__), len(Convention.__slots__))
    # ⚑⚑ A CHECK MUST FAIL ONLY IF THE REFUSAL LAPSES, AND MY FIRST PICK DID NOT. I chose
    # `check_snapshot_guard --quiet`, which exits 1 because it is an UNMINTED RATCHET on a
    # blocked tree — its honest resting state, unrelated to whether a default-dry crept in.
    # A discriminator red for an unrelated reason is VACUOUS in farm.py's exact sense: the
    # red came from elsewhere. This case pins that no declared check is a known always-red.
    check("no Decline is guarded by a command whose failure is its resting state",
          [d.claim for d in DECLINES
           if d.check and "check_snapshot_guard" in d.check], [])

    body = render_block(fix)
    # ⚑ FAILS against a markdown TABLE — the shape this block most obviously "wants".
    # `routes()` reads every `|`-leading line of THIS FILE as an `artifact | tool` row,
    # so a table here would feed --sync's output back into its own population: phantom
    # tools, the PreToolUse gate armed for artifacts nothing claims, and no fixed point.
    check("no rendered line may begin with `|` (routes() reads those as tool rows)",
          [ln for ln in body.splitlines() if ln.startswith("|")], [])
    check("the render is DETERMINISTIC for fixed rows", render_block(fix), body)
    check("the undocumented half is published, not just counted",
          "--hidden" in body, True)
    # ⚑ THE COLLISION LIST SPANS BOTH LAYERS.  `--collisions` splits them because their
    # evidence differs; a READER typing a flag does not make that split, so publishing
    # only documented collisions would hide the tool most likely to surprise — the one
    # that answers a flag none of its own usage lines mention.
    check("a collision across the documented/undocumented layers is published",
          "--hidden" in body.split("── ONE NAME, SEVERAL TOOLS")[1], True)

    doc = "before\n" + BEGIN + "\nstale junk\n" + END + "\nafter\n"
    once = splice(doc, body)
    # ⚑ FAILS against any splice that re-emits the markers or pads the region: running
    # --sync twice must produce byte-identical output, or the gate reports drift on a
    # tree nobody touched and trains people to ignore it.
    check("IDEMPOTENT: splicing the same body twice is byte-identical",
          splice(once, body), once)
    check("the body between the markers is exactly what was spliced",
          current_body(once), "\n" + body + "\n")
    # ⚑ FAILS against a line-based rewrite that normalizes whitespace outside the block.
    check("content BEFORE the markers is byte-preserved",
          once[:once.index(BEGIN)], "before\n")
    check("content AFTER the markers is byte-preserved",
          once[once.index(END):], END + "\nafter\n")
    check("the markers themselves are neither moved nor duplicated",
          (once.count(BEGIN), once.count(END)), (1, 1))

    # ── the DRIFT verdict is exactly `splice(src, fresh) == src` ──────────────
    check("a fresh block PASSES the drift predicate", splice(once, body) == once, True)
    # ⚑ FAILS against a check that only asserts the markers exist.
    check("DRIFT: a hand-edited block FAILS the drift predicate",
          splice(once.replace("--calls", "--kalls", 1), body)
          == once.replace("--calls", "--kalls", 1), False)
    # ⚑ and the gate must not police the prose it does not own
    check("a change OUTSIDE the markers is NOT drift",
          splice(once.replace("before", "BEFORE", 1), body)
          == once.replace("before", "BEFORE", 1), True)

    # ── missing markers: REFUSE, pinned ──────────────────────────────────────
    # ⚑ THE ALTERNATIVE (insert) IS THE ONE THAT LOOKS HELPFUL AND IS NOT.  It would
    # append ~70 lines wherever it reached, with none of the prose that introduces
    # them, and would silently restore a block a human had deliberately deleted — so
    # "remove the block" would be an instruction nothing could carry out.
    def _refuses(src):
        try:
            splice(src, body)
        except BlockError:
            return True
        return False

    check("MISSING markers are REFUSED, never inserted", _refuses("plain doc\n"), True)
    check("a lone BEGIN is refused", _refuses("x\n" + BEGIN + "\ny\n"), True)
    check("a lone END is refused", _refuses("x\n" + END + "\ny\n"), True)
    check("DUPLICATE marker pairs are refused",
          _refuses(once + BEGIN + "\n" + END + "\n"), True)
    check("INVERTED markers are refused", _refuses(END + "\n" + BEGIN + "\n"), True)
    try:
        splice("plain doc\n", body)
        _msg = ""
    except BlockError as _e:
        _msg = str(_e)
    check("the refusal NAMES THE REMEDY rather than just failing",
          "add the two marker" in _msg, True)

    # ── THE DOGFOOD CASE ─────────────────────────────────────────────────────
    # ⚑ A CENSUS TOOL WHOSE OWN SELF-DESCRIPTION ITS OWN PARSER CANNOT READ WOULD
    # BE THE DEFECT IT EXISTS TO FIND.  This also pins the docstring to the shape
    # the corpus uses: reformat the usage block and this fails before a reader ever
    # meets an unreadable tool.
    _self = parse_usage(USAGE, "toolmodes.py")
    check("this tool's own usage block parses",
          set(_self) >= {"--all", "--find", "--collisions", "--siblings",
                         "--gaps", "--divergence"}, True)
    check("and every mode it declares is one it dispatches",
          sorted(m for m in _self
                 if m not in literal_flags(os.path.abspath(__file__))[0]), [])

    # ── ONE live end-to-end case: the acceptance criterion itself ─────────────
    # ⚑ `--grep` IS AN `agda_defs` MODE, NOT A `pycodemod` ONE — miss #1, pinned
    # against the LIVE tool rather than a fixture, because the whole claim of this
    # file is that the census is derived and not written down.
    live = bare(["scratch/agda_defs.py"])
    got = parse_usage(live["scratch/agda_defs.py"][0], "agda_defs.py")
    check("LIVE: agda_defs really declares --grep", "--grep" in got, True)
    check("LIVE: agda_defs really declares --provides", "--provides" in got, True)
    # ⚑ AND THE MODE AN OPERATOR GUESSED IS REALLY ABSENT — a census that could not
    # say NO would answer every question affirmatively.
    check("LIVE: agda_defs has no --module (the guessed name)",
          "--module" in got, False)

    print(f"selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    sys.exit(main(sys.argv))
