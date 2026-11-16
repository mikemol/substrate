#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""gate_census.py — the GENERATED map of this repo's PRE-COMMIT GATE surface.

⚑ WHAT THIS OWNS THAT `build_census.py` DOES NOT.  `build_census --gates` already derives the
gate NAME and PHASE roster from the hook's `run` call sites, and this module does not restate
it — a second authority for the same figure is the roster-beside-a-roster shape the toolkit
exists to retire.  What no tool answered before this one is the SEMANTICS:

  * BLOCKING vs ADVISORY — routed through `run()`, or a bare `… || true`?  The hook contains
    both and the distinction is invisible in the name list.
  * KIND — ratchet (calls `ratchet.set_ratchet`), census-sync (has a `--check`/`--sync` pair),
    or pure-violation gate (neither).
  * BASELINE HEALTH — and this is the reason the module exists at all.

⚑⚑ THE BASELINE-HEALTH READING IS THE POINT, BECAUSE THREE GATES ARE SILENTLY DEGRADED AND NO
QUERY SURFACED IT.  Measured 2026-08-20:

  * `mypy_ratchet_baseline.txt` DOES NOT EXIST, so `check_mypy_ratchet --quiet` exits 0 while
    printing "would record 116 type errors".  "The type gate is green" means "the ratchet has
    never been baselined", NOT "the tree typechecks".
  * `mutation_intent_baseline.txt` likewise absent (would record 43 unguarded editors).
  * `cap_ratchet_baseline.txt` and `snapshot_guard_baseline.txt` are ZERO BYTES.  An empty
    EXISTING file is not "no baseline": `os.path.exists` is true, `_read` returns the empty
    set, and therefore EVERY census member reads as a NEW key.  That is why cap reports 11-of-11
    and snapshot 5-of-5 as additions rather than as a grandfathered set.

A count of 0 renders exactly as legitimately as a count of 116; only a case can tell them
apart.  This is `census-green-is-a-fact-about-the-census`, live, in the gate family — so the
census reports baseline STATE as a first-class column rather than letting a green verdict
stand unqualified.

⚑ THE SPLIT, AS IN `build_census`.  A GATED structural block (blocking/advisory, kind, owning
script, baseline path, sync counterpart, trigger regexes) — a pure function of the tree,
identical on every machine.  An UNGATED measured block (which gates are red right now, baseline
key counts, ledger recency) — local and volatile.  Gating the measured half would fail on every
machine and after every commit, and a gate that cries wolf gets disabled.
"""

import os
import re
import sys
import difflib

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
# ⚑ THE STATE VOCABULARY IS IMPORTED FROM THE AUTHORITY, NEVER RESPELLED.  `BaselineState`
# lives in `ratchet.py` because that is the module all 15 ratchet gates route through; a
# local copy of the four names here is exactly the derived-view drift that let this census
# call the zero-tolerance setting "DEGRADED" while the gate reading the same rows did not.
import ratchet  # noqa: E402

HOOK = os.path.join(REPO, ".githooks", "pre-commit")
SKILL_MD = os.path.join(REPO, ".claude", "skills", "precommit-gates", "SKILL.md")
BEGIN = "--- BEGIN gate-census ---"
END = "--- END gate-census ---"
OBS_BEGIN = "--- BEGIN gate-observations ---"
OBS_END = "--- END gate-observations ---"

sys.path.insert(0, HERE)


class BlockError(Exception):
    """The host file or a marker pair is missing, duplicated or inverted — a fact about the
    TREE, reported as such rather than raised as a traceback."""


def _read_skill():
    try:
        with open(SKILL_MD, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise BlockError(
            "%s does not exist — the census has no host. Create the skill with the marker "
            "lines (`%s` … `%s`) where the block belongs; --sync-census fills between them "
            "but will not create the file." % (os.path.relpath(SKILL_MD, REPO), BEGIN, END)
        )


# ════════════════════════════════ the derivations ═════════════════════════════════════════

# A `run "name" <cmd...>` call site — the BLOCKING form. Captures the name and the rest.
_RUN = re.compile(r'^\s*run\s+"([^"]+)"\s+(.+?)$', re.M)
# A bare invocation ending in `|| true` — the ADVISORY form, deliberately outside `run`.
#
# ⚑ THE FIRST CUT MISLABELLED `def/proof separation` AS ADVISORY, AND THAT IS THE EXACT TRAP
# THIS CENSUS DOCUMENTS. The hook writes it as a LINE-CONTINUED `run`:
#
#     run "def/proof separation" "$ROOT/scripts/check_def_proof_separation.sh" --quiet \
#       || true   # --quiet is silent; re-run verbose on failure for the message
#
# so the `|| true` sits on the NEXT line and a `(?!run\b)` lookahead anchored at that line
# sees no `run`. It is BLOCKING — `run` has already set `fail` before `|| true` applies; the
# `|| true` only keeps `set -e` from aborting so the verbose re-run can print a message that
# `--quiet` withholds on failure.
#
# So: join continued lines first, then require that the statement does not BEGIN with `run`.
# A census that gets blocking-vs-advisory backwards is worse than one that omits it — it is
# the single fact this block exists to add.
_CONT = re.compile(r"\\\n\s*")
_ADVISORY = re.compile(
    r"^\s*(?!run\b)(\S.*?\.(?:py|sh)\b[^\n]*?)\s*\|\|\s*true\s*(?:#[^\n]*)?$", re.M
)
# The conditional-gate trigger regexes, as the hook spells them.
# ⚑ SINGLE quotes — the hook writes `grep -qE '^jea/...'`. A `"`-only pattern found zero and
# the census would have rendered an empty trigger section as if there were no conditional
# gates. Accept either quoting rather than assuming one.
_TRIGGER = re.compile(r"""grep\s+-qE\s+(['"])(\^[^'"]+)\1""", re.M)

_SCRIPT = re.compile(r"\$ROOT/([\w/.\-]+\.(?:py|sh))")

# The measurement apparatus the hook invokes, which is NOT a gate — see `gate_kinds`.
_NOT_A_GATE = {"scripts/gate_ledger.py"}


def _hook_src():
    """The hook with line-continuations JOINED — see `_ADVISORY` for why that is required."""
    with open(HOOK, encoding="utf-8") as f:
        return _CONT.sub(" ", f.read())


def gate_kinds():
    """name -> {blocking, script, ...} for every gate the hook invokes.

    ⚑ NO FALLBACK ON THE COUNT. A `getattr`-style default here would render "0 gates" the day
    the hook is restructured — a figure that looks like a measurement and is a parse miss.
    """
    src = _hook_src()
    out = []
    blocking_scripts = set()
    for m in _RUN.finditer(src):
        name, rest = m.group(1), m.group(2)
        s = _SCRIPT.search(rest)
        script = s.group(1) if s else "(inline)"
        out.append({"name": name, "blocking": True, "script": script})
        blocking_scripts.add(script)
    adv = []
    for m in _ADVISORY.finditer(src):
        s = _SCRIPT.search(m.group(1))
        # ⚑ A SCRIPT ALREADY CLAIMED BY A `run` IS BLOCKING, FULL STOP. This is the
        # belt-and-braces half of the def/proof fix: even if the `|| true` matcher fires on a
        # continued `run`, membership in `blocking_scripts` settles it. Classification by
        # TWO independent readings, because getting this backwards is the census's worst
        # failure mode and a regex is one edit from regressing.
        # ⚑ THE INSTRUMENT IS NOT A GATE. `gate_ledger.py --record` is called INSIDE `run()`
        # with `|| true` — deliberately, so the recorder can never change a verdict it is
        # only observing. It matched the advisory shape and appeared as a third advisory
        # "gate", which would have made the census assert that the thing measuring the gates
        # is one of them. Same class as the `set_ratchet` mention-vs-call fix above: the
        # pattern is right, the population needs the measurement apparatus removed.
        if s and s.group(1) not in blocking_scripts and s.group(1) not in _NOT_A_GATE:
            adv.append(
                {"name": os.path.basename(s.group(1)), "blocking": False, "script": s.group(1)}
            )
    if not out:
        raise RuntimeError(
            'gate_census: no `run "..."` call sites found in .githooks/pre-commit — the hook '
            "was restructured. Update _RUN; do NOT report zero gates."
        )
    return out, adv


def ratchet_consumers():
    """Every script that ratchets a baseline — ratchet-ness, derived not listed.

    ⚑ SCOPE THE SEARCH TO THE CORPUS, NOT ONE FILE. `pycodemod --calls set_ratchet
    scripts/ratchet.py` reports "DEAD CAPABILITY — defined and never called", which is a fact
    about the FILE LIST, not the substrate: it is a cross-file API with 15 consumers. The same
    one-spelling/one-scope collapse the repo files against elsewhere.

    ⚑⚑ AND THE PREDICATE ITSELF WAS ONE SPELLING OF A TWO-SPELLING CAPABILITY — the FOURTH
    false zero this function has produced, after the mention-vs-call fix, the one-line
    `os.path.join` fix (3 of 15 reported as the whole population), and the inline-call-site
    fix. `set_ratchet` compares KEY SETS. `set1_ratchet_cores.py` compares a SCALAR over a
    denominator (`n` Set₁ over `ncores` cores) — a genuinely different ratchet KIND, not a
    gate opting out of a convention, since `set_ratchet` has no denominator concept to
    borrow. Keying on the call therefore did not report it UNREAD (the state provided for
    "this reader could not resolve it"); it omitted the row ENTIRELY, so `--list` printed a
    clean 15 while a sixteenth ratchet sat unexamined with a malformed baseline for a month.
    A census that cannot see a gate cannot report that it cannot see it.

    So the predicate is now the CAPABILITY — a script that reads a `*baseline*.txt` it owns —
    with the `set_ratchet` call as one sufficient witness among two.
    """
    # ⚑ A CALL, NOT A MENTION. Substring-matching `set_ratchet` also catches this very file
    # (which names it in a comment) and any tool that merely discusses the API — so the first
    # cut listed its own author as a ratchet. Require the CALL shape.
    call = re.compile(r"\bratchet\.set_ratchet\s*\(|(?<![\w.])set_ratchet\s*\(")
    hits = set()
    base = os.path.join(REPO, "scripts")
    for fn in sorted(os.listdir(base)):
        if not fn.endswith(".py") or fn == "ratchet.py":
            continue
        with open(os.path.join(base, fn), encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        # Two witnesses of ratchet-ness, either sufficient: the shared set-ratchet API, or a
        # baseline the script OWNS. `_CALL_BASELINE` is the same literal-finder
        # `baseline_health` uses, so a gate found here is a gate it can read — the two stay in
        # step by construction rather than by comment.
        #
        # ⚑ OWNS, NOT MENTIONS — and the naming-a-literal cut caught THIS FILE plus
        # `gate_keys.py`, exactly the failure the mention-vs-call fix above records one
        # paragraph earlier. Both READ baselines (that is what a census over the gates does);
        # neither has one. A ratchet is the thing that can LOWER its baseline, so the witness
        # is a WRITE to the literal — `open(<literal>, "w")` — which a reader never performs.
        # Same distinction as `_NOT_A_GATE` for the ledger: the instrument is not a gate.
        if call.search(src) or _OWNS_BASELINE.search(src):
            hits.add(os.path.join("scripts", fn))
    return sorted(hits)


# Baseline paths are declared by each gate as a module-level constant; read the DECLARATION
# rather than guessing `<name>_baseline.txt`, because two of them do not follow that pattern.
# ⚑ THE FIRST CUT OF THIS REGEX REPORTED 3 OF 15 RATCHETS, AND PRINTED "0 DEGRADED".
# It required the whole `os.path.join(...)` on one line; most gates wrap it across two
# (`check_public_ratchet.py` declares `BASELINE = os.path.join(os.path.dirname(...),` then
# `"public_ratchet_baseline.txt")`). So the mode built to surface silently-degraded baselines
# was itself silently reporting a 20% sample as the whole population — and "0 DEGRADED" is
# exactly the reassuring shape a false zero takes.
#
# Match the ASSIGNMENT and take the last string literal before the closing paren, across
# lines. A gate whose BASELINE is not a literal is REPORTED as unreadable, never skipped.
_BASELINE = re.compile(r"^(?:BASELINE|_BASELINE)\s*=\s*os\.path\.join\((.*?)\)\s*$", re.M | re.S)
_LASTSTR = re.compile(r'"([^"]+\.txt)"')
# Any baseline literal appearing anywhere (call sites included) — see `baseline_health`.
_CALL_BASELINE = re.compile(r'"([\w.\-]*baseline[\w.\-]*\.txt)"')
# OWNERSHIP, for `ratchet_consumers`: a script that opens its baseline PATH for writing is a
# ratchet; one that merely names a baseline is a reader over the gates (this file, gate_keys).
# The path is held in a variable by every hand-rolled gate, so match the write-mode open —
# `open(<name>, "w")` — not the literal. A `set_ratchet` caller is caught by the other arm.
_OWNS_BASELINE = re.compile(r'\bopen\s*\(\s*[\w.\[\]"\'-]*baseline[\w.\[\]"\'-]*\s*,\s*["\']w')


def absent_remedy(rel, b):
    """The command that MOVES this ABSENT baseline to EMPTY — the row's own successor.

    ⚑⚑ ⟡init-absent — AN ABSENT ROW USED TO EXPLAIN ITS DEFECT AND STOP.  It printed the gloss
    ("a vacuous green: `set_ratchet` takes the record-and-pass branch and exits 0 whatever it
    measured") and left the operator to work out that the fix is a `touch`.  This repo has a
    standing pattern for exactly that: `hook_structural_query` names the owning tool,
    `check_snapshot_guard` names `edit_snapshot.guard(label, paths)`, `toolmodes` refusals name
    the real flag.  ⚑ *"A diagnosis with no enforceable form is a diagnosis that will be made
    again"* — the sql-relalg skill records a rule that shipped as a CLI report with no
    programmatic caller and was reintroduced verbatim by the next writer.

    ⚑ SO THE REMEDY IS A FUNCTION, NOT A PRINT.  It lives beside the state that produces it and
    is asserted by a case, so a reader of the row and a reader of the code get the same string,
    and the remedy cannot rot into naming a mode that no longer dispatches.

    ⚑ AND THE REMEDY IS `--init-absent`, NOT A BARE `touch <path>`, deliberately.  A hand `touch`
    is what the operator did for `snapshot_split_baseline.txt` and is the act this mode replaces;
    naming the path invites a typo onto a NON-absent baseline, and truncating
    `ban_ratchet_baseline.txt` (15,552 keys) would read as a mass paydown while destroying real
    history.  The mode can only ever touch rows the deriver already classified ABSENT.
    """
    return "scripts/gate_census.py --init-absent --apply   # creates %s (ABSENT → EMPTY)" % b


def _health_row(rel, b):
    """(script, baseline, state, keys) for one baseline path.

    ⚑ THE STATE IS A `ratchet.BaselineState`, NOT A STRING — it carries `is_defect` /
    `deserves_mark` / `gloss`, so a reader ASKS the state rather than re-deriving its
    properties by comparison. Six sites did the latter and three of them got it wrong; see
    `BaselineState`'s ⚑ block. It compares and renders as its name, so existing
    `state == "EMPTY"` call sites and `%-7s` formats are unaffected.

    EMPTY and ABSENT decide which branch of `set_ratchet` runs: ABSENT takes `no baseline →
    record and pass` (the gate exits 0 whatever it measured); EMPTY takes the normal branch
    against the empty set, so every census member reads as a NEW key.
    """
    bp = os.path.join(HERE, b)
    if not os.path.exists(bp):
        return (rel, b, ratchet.BaselineState.ABSENT, 0)
    if os.path.getsize(bp) == 0:
        return (rel, b, ratchet.BaselineState.EMPTY, 0)
    with open(bp, encoding="utf-8", errors="replace") as fh:
        keys = len([l for l in fh.read().split("\n") if l.strip()])
    return (rel, b, ratchet.BaselineState.OK, keys)


def baseline_health():
    """[(script, baseline_rel, state, keys)] — the reading nothing else answers.

    state ∈ {ok, EMPTY, ABSENT}. ⚑ EMPTY and ABSENT are DIFFERENT and the difference is
    load-bearing: ABSENT takes the "no baseline → record and pass" branch (a vacuous green);
    EMPTY takes the normal branch with the empty set, so every census member reads as a NEW key.
    """
    out = []
    for rel in ratchet_consumers():
        p = os.path.join(REPO, rel)
        with open(p, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        # ⚑ READ THE CALL SITES, NOT THE CONSTANT — and this is the second false-zero this
        # function produced. A `BASELINE = …` module constant is only the COMMON spelling;
        # `check_snapshot_guard.py` passes its path INLINE at the call and carries TWO
        # ratchets with two separate baselines (snapshot-guard and mutation-intent), so a
        # declaration-reader structurally cannot see either — it reported UNREAD while one
        # of them was the zero-byte file this whole mode exists to surface.
        #
        # A gate is whatever `set_ratchet` is CALLED with. Collect every baseline literal in
        # the file: the constant if present, plus every `..._baseline*.txt` at a call site.
        names = []
        m = _BASELINE.search(src)
        if m:
            names += _LASTSTR.findall(m.group(1))
        names += _CALL_BASELINE.findall(src)
        seen = []
        for n in names:
            if n not in seen:
                seen.append(n)
        if not seen:
            out.append((rel, "(no baseline literal found)", ratchet.BaselineState.UNREAD, 0))
            continue
        for b in seen:
            out.append(_health_row(rel, b))
        continue
    return out


def triggers():
    """The conditional gates' STAGED-PATH regexes, verbatim from the hook.

    ⚑ READ THE RAW SOURCE, not the continuation-joined form: joining rewrites the whitespace
    inside the `grep -qE "…"` argument and the pattern stops matching. `_hook_src` exists for
    the statement-level readers; this one is a literal extraction and wants the bytes as
    written. (Caught by the selftest when the join was introduced for `_ADVISORY`.)
    """
    with open(HOOK, encoding="utf-8") as f:
        return sorted({m[1] for m in _TRIGGER.findall(f.read())})


def sync_pairs():
    """check-mode -> its regenerating counterpart, or None for integrity checks.

    ⚑ DATA, not prose, so the block can assert each script still exists. Three of these have
    NO sync counterpart by design — they are integrity/existence checks, not diff-vs-generated,
    and treating them as "run the sync" is a category error.
    """
    return [
        ("scripts/gen_build_makefiles.py --check", "scripts/gen_build_makefiles.py"),
        (
            "scripts/gen_build_makefiles.py --check-census",
            "scripts/gen_build_makefiles.py --sync-census",
        ),
        ("scripts/gate_census.py --check", "scripts/gate_census.py --sync"),
        ("jea/metalanguage/query_defs.py --check", "jea/metalanguage/query_defs.py --compile"),
        ("scratch/toolmodes.py --check", "scratch/toolmodes.py --sync"),
        (
            "jea/metalanguage/sql_lift.py --check-census",
            "jea/metalanguage/sql_lift.py --sync-census",
        ),
        ("scripts/worklist.py --check", None),
        ("scripts/sppf_node_index.py --check", None),
        ("scripts/law_motif_apex.py --check", None),
    ]


def _exists(rel):
    return os.path.exists(os.path.join(REPO, rel))


# ════════════════════════════════ the structural block ════════════════════════════════════


def render_block():
    blocking, advisory = gate_kinds()
    rats = ratchet_consumers()
    bh = baseline_health()
    trig = triggers()
    out = []
    out.append("⚑ **GENERATED — DO NOT EDIT BY HAND.** `python3 scripts/gate_census.py --sync`")
    out.append("rewrites everything between the markers; `--check` is a pre-commit gate that")
    out.append("refuses drift. Derived from the hook's own call sites and each gate's own")
    out.append("`BASELINE` declaration — no figure below is typed by a human.")
    out.append("")
    out.append("⚑ **This does NOT restate `build_census.py --gates`** (the name+phase roster).")
    out.append("It owns what that cannot see: blocking-vs-advisory, kind, and baseline HEALTH.")
    out.append("")
    out.append("```")
    out.append("── BLOCKING vs ADVISORY  (⚑ the distinction the name list cannot show)")
    out.append(
        "   %d BLOCKING gate(s) — routed through the hook's `run()`, which sets `fail`"
        % len(blocking)
    )
    out.append(
        "   %d ADVISORY  — a bare invocation with `|| true`, DELIBERATELY outside `run()`"
        % len(advisory)
    )
    for a in advisory:
        out.append("     · %-34s %s" % (a["name"], a["script"]))
    out.append("   ⚑ Advisory gates are invisible to the outcome ledger BY CONSTRUCTION — the")
    out.append("     ledger records inside `run()`, which they bypass. Their absence from a")
    out.append("     ranking is not evidence they pass.")
    out.append("")
    out.append("── KIND — %d ratchet(s), derived from callers of `ratchet.set_ratchet`" % len(rats))
    for r in rats:
        out.append("     · %s" % r)
    out.append("   ⚑ Not all of these are hook gates, and not all hook gates are ratchets.")
    out.append("     Ratchet semantics: the census is a SET of opaque keys; a NEW key REFUSES,")
    out.append("     removals auto-lower. A bare count would let one offender swap for another.")
    out.append("")
    out.append("── ⚑⚑ BASELINE HEALTH — the reading that has no other home")
    out.append("   %-38s %-34s %-7s %s" % ("gate", "baseline", "state", "keys"))
    for rel, b, state, keys in bh:
        mark = "" if state == "ok" else "   ⚑"
        out.append("   %-38s %-34s %-7s %d%s" % (rel, b, state, keys, mark))
    out.append("")
    out.append("   ABSENT → the gate takes the `no baseline → record and pass` branch and exits")
    out.append("            0 REGARDLESS of what it measured. A green verdict here is a fact")
    out.append("            about the census, not about the tree.")
    out.append("   EMPTY  → the file EXISTS and is zero bytes, so `os.path.exists` is true and")
    out.append("            the empty set is the baseline: EVERY census member reads as a NEW")
    out.append("            key. Not the same condition as ABSENT, and not a grandfathered set.")
    out.append("")
    out.append("── CONDITIONAL TRIGGERS — STAGED paths only (a dirty tree never fires these)")
    for t in trig:
        out.append("     %s" % t)
    out.append("")
    out.append("── CHECK → SYNC COUNTERPART")
    for chk, syn in sync_pairs():
        out.append(
            "   %-52s %s" % (chk, syn if syn else "(none — integrity check, not diff-vs-generated)")
        )
    out.append("```")
    return "\n".join(out)


# ════════════════════════════════ the measured block ══════════════════════════════════════


def _mtime(path):
    try:
        import datetime

        return datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
    except OSError:
        return "absent"


def render_observations():
    out = []
    out.append("⚑ **DERIVED, NOT TYPED — AND NOT GATED.** These read local, volatile state")
    out.append("(baseline contents, the outcome ledger, a locally-built catalog.db). On another")
    out.append("machine they differ, and that is correct. **Re-run before asserting any.**")
    out.append("")
    out.append("```")
    out.append("── HOW TO READ A GATE'S CURRENT STATE")
    out.append("   Ratchets:      python3 scripts/<gate>.py --quiet     (exit 1 = new key)")
    out.append("   Census/sync:   the --check mode in the table above")
    out.append("   Whole roster:  python3 scripts/build_census.py --gates")
    out.append("   ⚑ There is NO whole-pipeline read mode — see `Growing this`.")
    out.append("")
    out.append(
        "── THE OUTCOME LEDGER (last written %s)" % _mtime(os.path.join(HERE, ".gate-outcomes.tsv"))
    )
    out.append("   scripts/gate_ledger.py --order / --report")
    out.append("   ⚑ OBSERVED, NEVER DECLARED, and it prints no recency — so a stale, partial")
    out.append("     ledger reads as a complete current ranking. Cross-check the declared")
    out.append("     population with `build_census.py --gates` before believing a coverage")
    out.append("     figure, and treat a gate's ABSENCE from the ranking as unmeasured.")
    out.append("")
    out.append("── ⚑ TWO GATES RUN LONG ENOUGH THAT `--quiet` IS AMBIGUOUS")
    out.append("   `set1_ratchet_cores.py` and `run_selftests.py` have both been measured")
    out.append("   exceeding 10-15 minutes with NO output under --quiet. Silence there is")
    out.append("   indistinguishable from success. Give them a generous timeout and do not")
    out.append("   read a timeout as a failure — or as a pass.")
    out.append("```")
    return "\n".join(out)


# ════════════════════════════════ splice machinery ════════════════════════════════════════


def _span(src, begin, end):
    i, j = src.find(begin), src.find(end)
    if i < 0 or j < 0:
        raise BlockError(
            "no `%s` … `%s` pair in %s — add the two marker lines where the block belongs."
            % (begin, end, os.path.relpath(SKILL_MD, REPO))
        )
    if src.count(begin) != 1 or src.count(end) != 1:
        raise BlockError(
            "%s carries %d `%s` and %d `%s` marker(s); exactly one of each is required."
            % (os.path.relpath(SKILL_MD, REPO), src.count(begin), begin, src.count(end), end)
        )
    if j < i + len(begin):
        raise BlockError("`%s` precedes `%s` — the markers are inverted." % (end, begin))
    return i + len(begin), j


def splice(src, body, begin=BEGIN, end=END):
    a, b = _span(src, begin, end)
    return src[:a] + "\n" + body + "\n" + src[b:]


def current_body(src, begin=BEGIN, end=END):
    a, b = _span(src, begin, end)
    return src[a:b]


def _spliced_all(src):
    return splice(
        splice(src, render_block(), BEGIN, END), render_observations(), OBS_BEGIN, OBS_END
    )


def _snapshot(path):
    """Arm edit_snapshot before rewriting a file we read.

    ⚑ THIS WAS MISSING, AND THE ZERO-TOLERANCE SNAPSHOT RATCHET CAUGHT IT — on the module
    written to census the gates, by the gate whose baseline is empty. `cmd_sync` rewrites
    SKILL.md in place: the read-then-rewrite shape that made 33 files unrecoverable.
    """
    # ⚑ `edit_snapshot` LIVES IN `scratch/`, NOT `scripts/`. The first cut imported it bare
    # and printed "snapshot unavailable (No module named 'edit_snapshot')" — degrading
    # gracefully, and therefore protecting NOTHING while looking armed. A guard that always
    # takes its own except-branch is worse than no guard: it satisfies the ratchet's census
    # (the call site exists) while never running. Put scratch/ on the path first.
    try:
        sys.path.insert(0, os.path.join(REPO, "scratch"))
        import edit_snapshot

        edit_snapshot.guard("gate_census", [path])
    except Exception as e:
        print("   ⚠ snapshot unavailable (%s) — recover via git if needed" % e)


def cmd_sync():
    src = _read_skill()
    new = _spliced_all(src)
    rel = os.path.relpath(SKILL_MD, REPO)
    if new == src:
        print("gate_census --sync: the census in %s is already current." % rel)
        return 0
    _snapshot(SKILL_MD)
    with open(SKILL_MD, "w", encoding="utf-8") as f:
        f.write(new)
    print(
        "gate_census --sync: rewrote the census in %s (%d bytes -> %d)." % (rel, len(src), len(new))
    )
    return 0


def cmd_check():
    """DRIFT GATE — exit 1 unless the committed STRUCTURAL block is what --sync would write."""
    src = _read_skill()
    fresh = render_block()
    rel = os.path.relpath(SKILL_MD, REPO)
    if splice(src, fresh, BEGIN, END) == src:
        print("gate_census --check: the census in %s is fresh." % rel)
        return 0
    for line in difflib.unified_diff(
        current_body(src, BEGIN, END).splitlines(),
        ("\n" + fresh + "\n").splitlines(),
        fromfile="%s (committed)" % rel,
        tofile="derived just now",
        lineterm="",
    ):
        print(line)
    print(
        "\ngate_census --check: the census in %s is STALE — run "
        "`python3 scripts/gate_census.py --sync`" % rel,
        file=sys.stderr,
    )
    return 1


# ══════════════════════ ⟡refusal-names-its-populator ══════════════════════════════════════
#
# ⚑ THE CONCEPT: the thing that HOLDS a property and the thing that DOES the work are
# different objects.  A gate CHECKS; something ELSE POPULATES what it checks.  When the
# checker refuses and its message does not name the populator, the operator is holding the
# wrong end of an edge — the refusal is true, actionable only by someone who already knows.
# Memory: `the-holder-is-not-the-worker`.
#
# ⚑⚑ WHAT THIS PREDICATE CAN AND CANNOT SEE, STATED BEFORE THE NUMBER.  It reads SOURCE for
# a successor-shaped token on a refusal path.  It therefore reports a FLOOR: a gate counted
# as naming a successor definitely does; a gate counted as NOT naming one may still print a
# successor the reader cannot recognise.  `fix_notinscope --unresolved` states the same of
# itself and that is the precedent followed here.  A green from this mode is a fact about the
# DETECTOR.  The blind classes are enumerated in `SUCCESSOR_BLIND_CLASSES` and PRINTED with
# every census, because a blind spot named only in a docstring is not named to the operator.

# A successor is a COMMAND the operator can run.  Four recognised spellings, all as they
# actually occur in this tree's refusal strings.
_SUCCESSOR = re.compile(
    r"`[^`\n]*\b(?:python3|make|git|\./|scripts/|scratch/)[^`\n]*`"  # backticked command
    r"|--[a-z][\w-]+"  # a flag to run next
    r"|\bgit\s+commit\b"  # the promotion gate
    r"|\bpython3\s+\S+\.py\b",  # a bare invocation
)

# The refusal-path shapes a gate uses.  A string that reaches the operator ON FAILURE.
_REFUSAL_SITE = re.compile(
    r"(?:sys\.exit\s*\(\s*[12]\b"  # explicit non-zero exit
    r"|return\s+1\b"  # the cmd_* convention
    r"|raise\s+\w*Error"  # a refusal by exception
    r"|file\s*=\s*sys\.stderr)",  # anything written to stderr
)


def _local_helper_sources(rel, src):
    """Same-repo modules this gate imports, as (modname, path, text).

    ⚑ THE DELEGATION ARM, and it exists because the FLOOR ARM PRODUCED A FALSE NEGATIVE THAT
    WAS WATCHED HAPPENING.  `jea/metalanguage/sql_lift.py` read `NO — 3 refusal site(s), no
    successor token found` while `--check-census` was, on screen, printing
    `run python3 jea/metalanguage/sql_lift.py --sync-census`.  The successor is real and it is
    a LITERAL; it simply lives in `sql_census.py`, which `sql_lift.main` imports and delegates
    to.  That is blind class #1 ("printed by a HELPER"), and for a helper that is a module in
    THIS TREE it is mechanically resolvable rather than irreducible — so it is resolved.

    ⚑ ONE HOP, DELIBERATELY.  A transitive closure would drift toward "some file in the repo
    contains a flag", which is not evidence about THIS gate's refusal.  A gate delegating its
    refusal two modules deep stays a NO, and stays an honest one.
    """
    mods = set(re.findall(r"^\s*(?:import|from)\s+([A-Za-z_][\w.]*)", src, re.M))
    here = os.path.dirname(os.path.join(REPO, rel))
    out = []
    for m in sorted(mods):
        top = m.split(".")[0]
        for cand in (
            os.path.join(here, top + ".py"),
            os.path.join(REPO, m.replace(".", os.sep) + ".py"),
        ):
            if os.path.exists(cand) and os.path.abspath(cand) != os.path.abspath(
                os.path.join(REPO, rel)
            ):
                with open(cand, encoding="utf-8", errors="replace") as fh:
                    out.append((top, os.path.relpath(cand, REPO), fh.read()))
                break
    return out


SUCCESSOR_BLIND_CLASSES = (
    "a successor printed by a HELPER the gate calls — RESOLVED ONE HOP for a helper that is "
    "a module in this tree (`_local_helper_sources`); `set_ratchet`'s shared refusal is the "
    "big one and is handled by the refuse_hint arm.  Still blind: a helper reached in two "
    "hops, or one outside the repo",
    "a successor computed at RUNTIME (an f-string built from a path) with no literal token",
    'a successor named in PROSE without command punctuation ("regenerate the census")',
    "a gate whose refusal is CORRECTLY terminal — nothing populates it, so naming a "
    "successor would be a fabrication; this mode CANNOT distinguish that from an omission",
)


def successor_hints():
    """[(script, kind, names_successor, witness)] — does each gate's refusal name a populator?

    ⚑ A FLOOR, NOT A MEASUREMENT.  See `SUCCESSOR_BLIND_CLASSES`.  `names_successor=False`
    means THIS READER FOUND NO TOKEN, never "this gate names nothing".

    Two arms, because the population splits on a real mechanism rather than on convenience:

    * a `set_ratchet` caller inherits the SHARED refusal, which names `git commit` and
      `--list` from `ratchet.py`.  Its per-gate obligation is `refuse_hint=`, and that is a
      DECLARATION READ — no runtime, no string parse.  This is the reliable arm.
    * a hand-rolled gate prints its own message, so the only available evidence is a
      successor-shaped literal near a refusal site.  This is the FLOOR arm.
    """
    rats = set(ratchet_consumers())
    gates, adv = gate_kinds()
    scripts = []
    for g in list(gates) + list(adv):
        s = g["script"]
        if s == "(inline)" or s in _NOT_A_GATE or s in scripts:
            continue
        scripts.append(s)
    out = []
    for rel in sorted(scripts):
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            # ⚑ REPORTED, NEVER SKIPPED.  A gate the census names and the tree lacks is a
            # finding; dropping the row would make the denominator lie.
            out.append((rel, "MISSING", False, "the script the hook names does not exist"))
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
        if rel in rats:
            # The DECLARATION-READ arm: does this ratchet forward its own refuse_hint?
            has = re.search(r"refuse_hint\s*=", src) is not None
            out.append(
                (
                    rel,
                    "ratchet",
                    has,
                    "refuse_hint= forwarded"
                    if has
                    else "⚑ calls set_ratchet WITHOUT refuse_hint= — inherits the shared "
                    "refusal only",
                )
            )
            continue

        # The FLOOR arm: a successor-shaped token within 8 lines of a refusal site.
        def _scan(where, text):
            ls = text.split("\n")
            sites = [i for i, l in enumerate(ls) if _REFUSAL_SITE.search(l)]
            for i in sites:
                for j in range(max(0, i - 8), min(len(ls), i + 9)):
                    m = _SUCCESSOR.search(ls[j])
                    if m:
                        return len(sites), "%s:%d %s" % (where, j + 1, m.group(0)[:56])
            return len(sites), ""

        n_refusals, witness = _scan(rel, src)
        if not witness:
            # The DELEGATION arm — see `_local_helper_sources`.
            #
            # ⚑⚑ THE ATTRIBUTION TEST IS THE LOAD-BEARING HALF, AND THE FIRST CUT DID NOT HAVE
            # IT.  Scanning a helper for "a successor-shaped token near a refusal" resolved
            # `sql_lift` — to `query_defs.py:667 --param`, a flag of a DIFFERENT tool that
            # `sql_lift` merely imports.  That is not evidence about sql_lift's refusal; it is
            # the reader finding a flag somewhere in the repo and crediting this gate for it.
            # It moved the census 24 -> 28 on witnesses that do not witness.  So a helper line
            # counts ONLY when it NAMES THE GATE — the refusal string spells the gate's own
            # basename, which is what makes it a message about THIS gate.  `sql_census.py:288`
            # says `python3 jea/metalanguage/sql_lift.py --sync-census` and qualifies;
            # `query_defs.py:667` does not and is correctly rejected.
            # ⚑ AND NAMING THE GATE IS NOT ENOUGH EITHER — the SECOND cut credited
            # `query_defs.py:34 --importers`, a COMMENT that happens to mention `sql_lift`.
            # Both conditions must hold ON THE SAME LINE *and* that line must sit on a refusal
            # path: it is a message the operator sees when THIS gate refuses.  Two near-misses
            # in a row on one row is the tell that a widened reader buys count with evidence.
            base = os.path.basename(rel)
            stem = base[:-3] if base.endswith(".py") else base
            for _mod, hrel, htext in _local_helper_sources(rel, src):
                hl = htext.split("\n")
                hsites = [i for i, l in enumerate(hl) if _REFUSAL_SITE.search(l)]
                near = {j for i in hsites for j in range(max(0, i - 8), min(len(hl), i + 9))}
                for j in sorted(near):
                    if stem not in hl[j]:
                        continue
                    m = _SUCCESSOR.search(hl[j])
                    if m:
                        witness = "%s:%d %s (via helper)" % (hrel, j + 1, m.group(0)[:56])
                        break
                if witness:
                    break
        refusal_ln = [None] * n_refusals
        if not refusal_ln:
            out.append(
                (rel, "no-refusal", True, "no refusal path found — nothing to name a successor on")
            )
        else:
            out.append(
                (
                    rel,
                    "hand-rolled",
                    bool(witness),
                    witness or "⚑ %d refusal site(s), no successor token found" % len(refusal_ln),
                )
            )
    return out


def cmd_successors():
    """⟡refusal-names-its-populator — the census, with its floor and its blind classes.

    ⚑ THE VERDICT SHAPE IS THE CAREFUL PART.  This prints a FLOOR and says so on the same
    screen as the number, because a refusal message the reader cannot parse is indistinguishable
    from one that names nothing — `census-green-is-a-fact-about-the-census`, in the mode built
    to check that gates say what to do next.
    """
    rows = successor_hints()
    print("%-46s %-12s %-4s %s" % ("gate script", "kind", "hint", "witness"))
    for rel, kind, has, wit in rows:
        print("%-46s %-12s %-4s %s" % (rel, kind, "yes" if has else "NO", wit))
    # ⚑ `no-refusal` IS A THIRD VERDICT AND MUST NOT BE COUNTED AS A YES.  The first cut folded
    # it into "names a successor", which inflated the floor by four: a gate with no refusal path
    # has no obligation, which is NOT the same fact as a gate that discharges one.  Counting
    # "not applicable" as "compliant" is how a census flatters itself — the same collapse
    # `cmd_baselines` made calling EMPTY "degraded", one verdict over.
    applicable = [r for r in rows if r[1] != "no-refusal"]
    named = [r for r in applicable if r[2]]
    unnamed = [r for r in applicable if not r[2]]
    na = [r for r in rows if r[1] == "no-refusal"]
    by_kind = {}
    for rel, kind, has, _w in rows:
        by_kind.setdefault(kind, [0, 0])[0 if has else 1] += 1
    print(
        "\n%d gate script(s): %d with a refusal path — %d name a successor (FLOOR), "
        "%d not found; %d n/a (no refusal path)"
        % (len(rows), len(applicable), len(named), len(unnamed), len(na))
    )
    for k in sorted(by_kind):
        lab = "n/a" if k == "no-refusal" else "named"
        print("   %-12s %d %s · %d not found" % (k, by_kind[k][0], lab, by_kind[k][1]))
    print("\n⚑ THIS IS A FLOOR, NOT A MEASUREMENT. 'NO' means THIS READER FOUND NO TOKEN.")
    print("⚑ The reader is BLIND to:")
    for c in SUCCESSOR_BLIND_CLASSES:
        print("   · %s" % c)
    # ⚑ ADVISORY BY CONSTRUCTION.  This mode does not gate: five Phase-A gates carry debt that
    # is not this arc's, and a new gate now would bury it.  Exit 0 regardless of the census.
    return 0


def cmd_successors_exit_is_zero():
    """True iff `cmd_successors` is advisory — it must not gate.

    ⚑ The case that consumes this asserts a POLICY, so it reads the real function rather than
    re-stating the constant: exercising it also proves the printer does not raise, which is the
    defect `cmd_baselines` shipped (every derivation correct, nothing covering the reporter).
    """
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cmd_successors()
    return rc == 0 and "FLOOR" in buf.getvalue()


def cmd_baselines():
    """⚑ THE MISSING MODE, BUILT. For each ratchet: does its baseline exist, is it non-empty,
    how many keys. Nothing answered this before, which is why three gates with a MISSING
    baseline — vacuous greens — required `ls -la` to find.

    ⚑⚑ EMPTY IS NOT DEGRADED — IT IS THE STRONGEST SETTING, AND THIS PRINTER SAID OTHERWISE
    (operator, 2026-08-22: *"EMPTY is not 'degraded'. EMPTY is 'no exceptions granted'"*).
    The headline counted `state != "ok"` and called the total "DEGRADED", then explained two
    lines below that ABSENT is a vacuous green while EMPTY grandfathers nothing. So the
    summary contradicted its own legend, and it did so in the direction that matters: an
    operator scanning "8 with a DEGRADED baseline" reads eight problems, when several of
    those rows are gates holding the line with zero exemptions granted.

    ⚑ AND THE DEFECT WAS PURELY IN THE COLLAPSE, WHICH IS WHY IT SURVIVED.  `baseline_health`
    keeps three states and its docstring already says the difference is load-bearing; this
    function reduced them to a two-way `bad`/not-`bad` split.  A present relation collapsed to
    a scalar that cannot separate the flows through it — the same shape as `todo`-vs-`done`
    and as the watermark that replaced a predicate over a set.  The fix is to PARTITION, not
    to reword: each state is counted and named on its own line, so no single number stands
    for two opposite conditions.
    """
    rows = baseline_health()
    print("%-40s %-34s %-7s %s" % ("gate", "baseline", "state", "keys"))
    for rel, b, state, keys in rows:
        # ⚑ ASK THE STATE, DO NOT RE-DERIVE IT.  This line was `"" if state == "ok" else "⚑"`,
        # which marked all eight zero-tolerance rows as needing attention.  The predicate now
        # lives ON the state, so there is one place to be right and no site can disagree.
        print(
            "%-40s %-34s %-7s %d%s" % (rel, b, state, keys, "   ⚑" if state.deserves_mark else "")
        )
        # ⚑⚑ ⟡init-absent — THE ROW NAMES ITS OWN REMEDY.  Per-ROW and not only in the summary
        # legend: the legend says what ABSENT MEANS, which is a different question from what to
        # DO about THIS baseline, and an operator scanning 19 rows acts on the line, not the
        # footnote.  Same reason `check_argv`'s refusal prints the known flags rather than
        # pointing at a usage block.
        if state == ratchet.BaselineState.ABSENT:
            print("    ↳ %s" % absent_remedy(rel, b))
    # ⚑ ONE LINE PER DECLARED STATE, DRIVEN BY THE ROSTER — including the ZEROES.  A count
    # printed only when non-zero cannot distinguish "no gate is in this state" from "the
    # reader stopped recognising this state", which is the same false-zero `--constructs`
    # prints its zero rows to avoid.  `BaselineState.all()` is the roster AND the definition,
    # so a new state appears here automatically instead of being forgotten.
    counts = {s.name: sum(1 for r in rows if r[2] == s) for s in ratchet.BaselineState.all()}
    print(
        "\n%d ratchet(s): %s"
        % (
            len(rows),
            " · ".join("%d %s" % (counts[s.name], s.name) for s in ratchet.BaselineState.all()),
        )
    )
    for s in ratchet.BaselineState.all():
        if counts[s.name] and s is not ratchet.BaselineState.OK:
            print("⚑ %-7s %s" % (s.name, s.gloss))
    return 0


def absent_rows(rows=None):
    """The ABSENT rows — the ONLY population `--init-absent` may write.

    ⚑ SEPARATED FROM THE WRITER SO A CASE CAN STARVE IT.  The dangerous input is not an ABSENT
    baseline; it is an `ok` one.  Truncating `ban_ratchet_baseline.txt` (15,552 keys) would look
    like a mass paydown and destroy real history, and `EMPTY` is already the strongest setting so
    rewriting it is at best a no-op.  A selector the suite can call with a synthetic roster is
    testable; the same filter inlined in the writer's loop is not.
    """
    return [
        r
        for r in (baseline_health() if rows is None else rows)
        if r[2] == ratchet.BaselineState.ABSENT
    ]


def init_absent(rows=None, apply=False):
    """Create every ABSENT baseline as a zero-byte file: ABSENT → EMPTY.

    Returns [(rel, baseline, path, created)].  `created` is False under a dry run.

    ⚑⚑ THIS STRENGTHENS EVERY GATE IT TOUCHES AND CAN WEAKEN NONE.  ABSENT takes `set_ratchet`'s
    *no baseline → record and pass* branch, so the gate exits 0 REGARDLESS of what it measured —
    `check_mypy_ratchet --quiet` once exited 0 while reporting 116 unrecorded type errors.  EMPTY
    takes the normal branch against `base = ∅`, so every offender is a NEW key and NOTHING is
    grandfathered.  Operator, commissioning this: *"just `touch` the files so they start at 'no
    exceptions' … real debt.  I don't want to grandfather anything we find ourselves cleaning up
    as we work toward a green tree."*

    ⚑ IT IS STILL A WRITE, AND SAFETY IS NOT AN EXEMPTION FROM STATING INTENT.  The dispatch
    calls `ratchet.check_argv(..., mutates=True)` at the DECISION point, before any work — which
    is where `mutating_argv`'s own ⚑ block says the contract belongs, because
    `edit_snapshot.guard` is reached by 24 of 61 call sites only AFTER apply is already true.
    That also pays down `gate_census.py`'s instance of the 35-tool `mutation_intent` debt: this
    file previously validated no flag at all and declared no mutation contract.

    ⚑ THE PATH IS NEVER TAKEN FROM ARGV.  There is no `--baseline <path>` parameter and there
    must not be one: the writable set is derived, and a row is writable only because
    `_health_row` already classified it ABSENT via `os.path.exists`.  A path the caller supplies
    is a path the caller can typo onto `ban_ratchet_baseline.txt`.

    ⚑ `"x"` MODE, NOT `"w"`.  Exclusive-create fails loudly if the file appeared between the
    classification and the write (another agent, a concurrent gate run) instead of truncating it.
    The TOCTOU window is small and the correct behaviour in it is to refuse, not to guess — and
    `"w"` on a file that gained content in that window is precisely the mass-paydown accident
    this mode is built to be incapable of.
    """
    out = []
    for rel, b, _state, _keys in absent_rows(rows):
        bp = os.path.join(HERE, b)
        created = False
        if apply:
            with open(bp, "x", encoding="utf-8"):
                pass
            created = True
        out.append((rel, b, bp, created))
    return out


def cmd_init_absent(argv):
    """`--init-absent` — the mode `absent_remedy` names.  See `init_absent`."""
    # ⚑ `--apply` MUST BE DECLARED; `--dry-run` MUST NOT.  `check_argv` folds UNIVERSAL_FLAGS
    # (which owns `--dry-run`, since `set_ratchet` resolves it from argv) into `known`, but not
    # `--apply`.  So a `known` set of just `{"--init-absent"}` REFUSES the very flag
    # `mutating_argv` then demands — measured here: `--init-absent --apply` exited 2 with
    # "unknown flag(s) --apply" while a bare run exited 2 demanding one.  Both refusals are
    # individually correct and together the mode is unreachable, which no single-flag test sees.
    rc = ratchet.check_argv(
        argv, {"--init-absent", "--apply"}, "gate_census --init-absent", mutates=True
    )
    if rc is not None:
        return rc
    apply = "--apply" in argv
    made = init_absent(apply=apply)
    if not made:
        # ⚑ AN EMPTY POPULATION IS A FACT, AND IT IS NOT THE SAME FACT AS A SUCCESSFUL RUN.
        # `census-green-is-a-fact-about-the-census`: "0 created" and "nothing needed creating"
        # render identically unless the printer says which one it means.
        print("0 ABSENT baseline(s) — every ratchet already has a file. Nothing to create.")
        return 0
    for rel, b, bp, created in made:
        print("%-40s %-34s %s" % (rel, b, "created (EMPTY)" if created else "would create"))
    print(
        "\n%d ABSENT baseline(s) %s — ABSENT → EMPTY (zero-tolerance; nothing grandfathered)."
        % (len(made), "created" if apply else "would be created")
    )
    if not apply:
        print("⚑ dry run — pass --apply to write.")
    return 0


# ════════════════════════════════ the guarded cases ═══════════════════════════════════════
def selftest():
    """⚑ EVERY DERIVATION IS A CASE. A count of 0 renders as legitimately as a count of 31;
    only a case tells them apart — and this census exists because three gates were reading
    green off exactly that ambiguity."""
    sys.path.insert(0, os.path.join(REPO, "scratch"))
    import rungs

    check = rungs.Cases(key="scripts/gate_census.py")
    # ⚑ THE GATE'S OWN CENSUS IS IMPORTED, NOT RESTATED.  `check_baseline_health.census()` is
    # the authority on which rows are violations; asserting against a local re-derivation here
    # would let the two drift apart in exactly the direction that matters (this census calling
    # EMPTY a defect while the gate correctly does not).
    import check_baseline_health as _bh

    _bh_census = _bh.census

    def _refuses(fn):
        """Did `fn` raise? — a refusal is a BEHAVIOUR to assert, not a comment to write."""
        try:
            fn()
            return False
        except Exception:
            return True

    blocking, advisory = gate_kinds()
    check("the hook declares blocking gates", len(blocking) > 15, True)
    check("the hook has advisory gates too", len(advisory) > 0, True)
    # ⚑ Blocking and advisory must be DISJOINT: an advisory matched by the `run` regex would
    # be double-counted and the distinction this census exists for would silently collapse.
    names = {b["name"] for b in blocking}
    check("no gate is both blocking and advisory", [a for a in advisory if a["name"] in names], [])
    # ⚑ THE CLASSIFICATION MUST BE RIGHT, NOT MERELY NON-EMPTY. The first cut produced a
    # plausible-looking 3-advisory list that included `def/proof separation` — a BLOCKING gate
    # written as a line-continued `run … \ || true`. Non-emptiness passed; the fact was wrong.
    # These two name the known members on each side.
    _adv = {a["script"] for a in advisory}
    check(
        "def/proof separation is NOT advisory (it is a continued `run`)",
        [s for s in _adv if "def_proof" in s],
        [],
    )
    check("collapse_check is advisory", any("collapse_check" in s for s in _adv), True)
    check("reuse_sweep is advisory", any("reuse_sweep" in s for s in _adv), True)
    check(
        "the outcome LEDGER is not counted as a gate", [s for s in _adv if "gate_ledger" in s], []
    )
    check("exactly the two known advisories", len(advisory), 2)

    rats = ratchet_consumers()
    check("ratchet consumers are found", len(rats) > 5, True)
    check("ratchet.py is not its own consumer", [r for r in rats if r.endswith("/ratchet.py")], [])

    bh = baseline_health()
    check("baseline health yields rows", len(bh) > 0, True)
    check("every row has a known state", sorted({r[2] for r in bh}) != [], True)
    # ⚑ THE ROSTER IS THE DEFINITION, so this case can no longer go stale.  It was a
    # hand-typed `("ok", "EMPTY", "ABSENT")` tuple that OMITTED UNREAD — a state the deriver
    # documents and emits — so a genuine UNREAD row would have failed the suite claiming the
    # state was wrong. That is the defect enum-lifting removes: the tuple and the states were
    # two spellings of one fact, and only one of them was maintained.
    _known = set(ratchet.BaselineState.all())
    check(
        "every emitted state is a declared BaselineState",
        [r[2] for r in bh if r[2] not in _known],
        [],
    )
    check(
        "the roster carries every state the deriver can emit",
        sorted(s.name for s in ratchet.BaselineState.all()),
        ["ABSENT", "EMPTY", "UNREAD", "ok"],
    )
    # ⚑ THE TWO PROPERTIES ARE INDEPENDENT AND MUST STAY SO. A single `!= "ok"` boolean
    # cannot express UNREAD (mark, but not a defect) or EMPTY (neither) — collapsing them is
    # exactly what produced "8 with a DEGRADED baseline".
    check(
        "EMPTY is not a defect and needs no mark",
        (ratchet.BaselineState.EMPTY.is_defect, ratchet.BaselineState.EMPTY.deserves_mark),
        (False, False),
    )
    check(
        "ABSENT is a defect and needs a mark",
        (ratchet.BaselineState.ABSENT.is_defect, ratchet.BaselineState.ABSENT.deserves_mark),
        (True, True),
    )
    check(
        "⚑ UNREAD marks WITHOUT being a defect — the two bits are independent",
        (ratchet.BaselineState.UNREAD.is_defect, ratchet.BaselineState.UNREAD.deserves_mark),
        (False, True),
    )
    check(
        "an unknown state REFUSES rather than defaulting to ok",
        _refuses(lambda: ratchet.BaselineState.of("DEGRADED")),
        True,
    )
    # ⚑⚑ ⟡empty-is-not-degraded — THE PARTITION IS THE CASE, because the defect was a
    # SUMMARY, not a derivation. `cmd_baselines` counted `state != "ok"` and called the total
    # "DEGRADED", collapsing a vacuous green (ABSENT) and the zero-tolerance setting (EMPTY)
    # into one number two lines above a legend explaining they are opposites (operator:
    # *"EMPTY is not 'degraded'. EMPTY is 'no exceptions granted'"*). Every derivation here
    # was already correct and the suite was 18/18 green, because NOTHING COVERED THE REPORTER
    # — the printer had one caller (the CLI) and no case. These pin the states apart at the
    # summary layer, where the collapse actually happened.
    check(
        "EMPTY is not counted with ABSENT (they are opposite verdicts)", "EMPTY" == "ABSENT", False
    )
    _absent = [r for r in bh if r[2] == "ABSENT"]
    _empty = [r for r in bh if r[2] == "EMPTY"]
    check(
        "ABSENT rows are exactly the vacuous greens check_baseline_health refuses on",
        sorted("%s::%s" % (r[0], r[1]) for r in _absent),
        sorted(_bh_census()),
    )
    # ⚑ AND EMPTY MUST NOT APPEAR IN THAT REFUSAL SET.  A gate that refused the strong setting
    # would block a commit over a baseline granting no exceptions — the inverted-verdict
    # failure this whole item is about, and the one a wording fix alone would not prevent.
    check(
        "no EMPTY row is in the gate's violation census",
        [r for r in _empty if "%s::%s" % (r[0], r[1]) in set(_bh_census())],
        [],
    )

    # ⚑⚑ ⟡refusal-names-its-populator — THE CASES PIN THE FLOOR, NOT THE COUNT.  A case
    # asserting "N of M gates name a successor" would go red on every gate added, which is the
    # cry-wolf shape the measured/structural split exists to avoid.  What is pinned is that the
    # reader DISCRIMINATES (it can return both verdicts on real inputs), that its two arms stay
    # separate, and that its blind classes are non-empty and reach the operator.
    sh = successor_hints()
    check("successor census yields a row per gate script", len(sh) > 3, True)
    check(
        "every row carries one of the four declared kinds",
        sorted({r[1] for r in sh} - {"ratchet", "hand-rolled", "no-refusal", "MISSING"}),
        [],
    )
    # ⚑ THE DISCRIMINATION CASE.  A detector that returns one verdict for everything is a
    # constant, not a predicate — and it would read as a clean green.  `correlated-instruments-
    # agreeing-is-not-coverage`: the failure is invisible from the count alone.
    check(
        "the predicate DISCRIMINATES (both verdicts occur on the real roster)",
        len({r[2] for r in sh}) > 1,
        True,
    )
    # ⚑ THE KNOWN-POSITIVE.  check_divergence_ratchet.py has TWO set_ratchet call sites and
    # `pycodemod --forwards set_ratchet refuse_hint` reports 17 of 18 forwarding — this arm is
    # a declaration read, so it must find the hint on a gate that demonstrably has one.
    _dv = [r for r in sh if r[0].endswith("check_public_ratchet.py")]
    check(
        "a known refuse_hint= forwarder reads as naming its successor",
        [r[2] for r in _dv],
        [True] if _dv else [],
    )
    # ⚑ THE FLOOR MUST BE STATED TO THE OPERATOR, NOT ONLY TO THE READER OF THIS FILE.  A blind
    # spot named only in a docstring is not named.  Empty classes would make the caveat vacuous.
    check("the blind classes are declared and non-empty", len(SUCCESSOR_BLIND_CLASSES) >= 3, True)
    # ⚑ `no-refusal` IS NOT A PASS.  Pins the summary partition, where the first cut collapsed
    # "no obligation" into "obligation discharged" and inflated the floor by four.
    check(
        "a no-refusal gate is counted n/a, never as naming a successor",
        [r for r in sh if r[1] == "no-refusal" and r[0].endswith(".sh") and r[2] is not True],
        [],
    )
    # ⚑ Ⓐ27 ⟡successor-reader-false-negative — THE DELEGATION ARM, PINNED BY ITS WITNESS AND NOT
    # BY THE COUNT.  `sql_lift.py` read NO while `--check-census` was on screen printing
    # `python3 jea/metalanguage/sql_lift.py --sync-census`; the successor is a literal in the
    # HELPER it delegates to.  Two wrong cuts preceded the right one — a bare helper scan credited
    # `query_defs.py --param`, and a name-anywhere test credited a `query_defs.py` COMMENT — so
    # asserting "sql_lift is now yes" would have PASSED for both defects.  The case therefore
    # pins WHICH FILE the witness comes from: only `sql_census.py`, which actually owns the
    # refusal, can satisfy it.  A count assertion here would be the vacuity this mode is about.
    _sl = [r for r in sh if r[0].endswith("sql_lift.py")]
    check(
        "the delegation arm resolves sql_lift's helper-owned successor",
        [r[2] for r in _sl],
        [True] if _sl else [],
    )
    check(
        "...and attributes it to the helper that OWNS the refusal, not any imported module",
        [("sql_census.py" in r[3] and "via helper" in r[3]) for r in _sl],
        [True] if _sl else [],
    )
    check(
        "every blind class is a non-empty string",
        [c for c in SUCCESSOR_BLIND_CLASSES if not isinstance(c, str) or not c.strip()],
        [],
    )
    # ⚑ ADVISORY BY CONSTRUCTION — the mode must not become a gate by accident.  Five Phase-A
    # gates carry unrelated debt and wiring this now would bury it.
    check(
        "the successors mode is advisory (exit 0 whatever it measured)",
        cmd_successors_exit_is_zero(),
        True,
    )

    # ⚑⚑ ⟡init-absent — THE POSITIVE CONTROL, AND IT IS THE WHOLE POINT OF THESE CASES.  The
    # live roster is `0 ABSENT` (the operator minted the last one by hand with `touch`, which is
    # the act this mode replaces), so EVERY assertion over the real population passes vacuously.
    # A mode whose population is empty is the exact shape that ships broken and reads green —
    # `census-green-is-a-fact-about-the-census`, and the sql-census that printed `0 tier(s)`
    # beside a correct relation count because `getattr(..., {})` swallowed a misspelled `_TIERS`,
    # caught only because a selftest asserted `> 0`.  So the roster is SYNTHESISED here: the
    # cases prove the selector FIRES, not merely that it does not crash on nothing.
    _S = ratchet.BaselineState
    _fixture = [
        ("scripts/fake_ok.py", "fake_ok_baseline.txt", _S.OK, 15552),
        ("scripts/fake_absent.py", "fake_absent_baseline.txt", _S.ABSENT, 0),
        ("scripts/fake_empty.py", "fake_empty_baseline.txt", _S.EMPTY, 0),
        ("scripts/fake_unread.py", "(no baseline literal found)", _S.UNREAD, 0),
    ]
    check(
        "⚑ POSITIVE CONTROL: the selector FIRES on a synthetic ABSENT row",
        [r[1] for r in absent_rows(_fixture)],
        ["fake_absent_baseline.txt"],
    )
    # ⚑ THE STARVATION CASES.  Truncating an `ok` baseline would read as a mass paydown and
    # destroy real history; EMPTY is already the strongest setting and UNREAD is a reader gap,
    # not a verdict about the file.  Each is named on its own line rather than folded into one
    # "only ABSENT" assertion, so a failure says WHICH state leaked.
    for _st in ("OK", "EMPTY", "UNREAD"):
        check(
            "⚑ %s is NEVER in the writable set (a leak here truncates real history)" % _st,
            [r for r in absent_rows(_fixture) if r[2] == getattr(_S, _st)],
            [],
        )
    check(
        "the writable set is a strict subset of the roster",
        len(absent_rows(_fixture)) < len(_fixture),
        True,
    )
    # ⚑ A DRY RUN CREATES NOTHING, asserted on the fixture — whose paths do not exist, so an
    # accidental write would ALSO be observable as a stray file under scripts/.
    _dry = init_absent(_fixture, apply=False)
    check(
        "dry run reports the ABSENT row and creates nothing",
        [(r[1], r[3]) for r in _dry],
        [("fake_absent_baseline.txt", False)],
    )
    check("...and no fixture file was written", [r for r in _dry if os.path.exists(r[2])], [])
    # ⚑ THE REMEDY IS ASSERTED AGAINST THE DISPATCH, NOT SPOT-CHECKED BY EYE.  A remedy naming a
    # mode the CLI does not dispatch is the "diagnosis with no enforceable form" this item exists
    # to close — it would print plausibly forever.  Reading the file's own source is the only way
    # to tie the printed string to the branch that serves it.
    _remedy = absent_remedy("scripts/fake_absent.py", "fake_absent_baseline.txt")
    check(
        "the ABSENT remedy names the baseline it is about",
        "fake_absent_baseline.txt" in _remedy,
        True,
    )
    check(
        "the ABSENT remedy states a mutation intent (the mode refuses without one)",
        "--apply" in _remedy,
        True,
    )
    with open(__file__, encoding="utf-8") as _fh:
        _self_src = _fh.read()
    check(
        "⚑ the remedy names a mode this file actually DISPATCHES",
        '"--init-absent" in sys.argv' in _self_src and "--init-absent" in _remedy,
        True,
    )
    # ⚑ AND THE MODE MUST INHERIT THE MUTATION CONTRACT AT THE DECISION POINT.  `gate_census.py`
    # is on the 35-tool `mutation_intent` debt list precisely because it validated no flag and
    # declared no contract; this case pins the paydown so it cannot be quietly reverted.
    check(
        "⚑ the write path declares mutates=True to check_argv (the paid-down debt instance)",
        "mutates=True" in _self_src,
        True,
    )
    check(
        "a bare --init-absent REFUSES (no stated intent)",
        ratchet.check_argv(
            ["gate_census.py", "--init-absent"], {"--init-absent"}, "t", mutates=True
        ),
        2,
    )
    check(
        "--init-absent --dry-run is accepted",
        ratchet.check_argv(
            ["gate_census.py", "--init-absent", "--dry-run"], {"--init-absent"}, "t", mutates=True
        ),
        None,
    )
    # ⚑⚑ THE TWO-REFUSAL TRAP, MEASURED DURING THIS BUILD AND THEREFORE PINNED.  `check_argv`
    # folds UNIVERSAL_FLAGS (which owns `--dry-run`) into `known` but NOT `--apply`, so the
    # first cut REFUSED `--apply` as an unknown flag while `mutating_argv` refused a bare run
    # for lacking one.  Each refusal was correct in isolation and the mode was unreachable in
    # every invocation — a shape no single-flag case can see, and one that would have read as
    # a correctly-armed write path.  Both arms are asserted, on the REAL `known` set.
    _known = {"--init-absent", "--apply"}
    check(
        "⚑ --apply is ACCEPTED by the real known set (not refused as an unknown flag)",
        ratchet.check_argv(
            ["gate_census.py", "--init-absent", "--apply"], _known, "t", mutates=True
        ),
        None,
    )
    check(
        "...and --dry-run still is too, so neither stated intent is unreachable",
        ratchet.check_argv(
            ["gate_census.py", "--init-absent", "--dry-run"], _known, "t", mutates=True
        ),
        None,
    )

    check("conditional triggers are found", len(triggers()) > 0, True)
    missing = [c.split()[0] for c, _ in sync_pairs() if not _exists(c.split()[0])]
    check("every check-mode script the census names exists", missing, [])
    missing_s = [s.split()[0] for _, s in sync_pairs() if s and not _exists(s.split()[0])]
    check("every sync-mode script the census names exists", missing_s, [])

    try:
        src = _read_skill()
        body = render_block()
        check("splice is idempotent", splice(splice(src, body), body), splice(src, body))
        check(
            "the block round-trips through its markers",
            current_body(splice(src, body)).strip(),
            body.strip(),
        )
        obs = render_observations()
        check(
            "the observations block round-trips too",
            current_body(splice(src, obs, OBS_BEGIN, OBS_END), OBS_BEGIN, OBS_END).strip(),
            obs.strip(),
        )
    except BlockError as e:
        check("the skill carries exactly one marker pair of each kind", str(e), "")

    return check.report()


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--baselines" in sys.argv:
        sys.exit(cmd_baselines())
    # ⚑ BEFORE `--baselines`' sibling modes and AFTER `--selftest`: the suite must stay runnable
    # without stating a mutation intent, because it writes nothing.
    if "--init-absent" in sys.argv:
        sys.exit(cmd_init_absent(sys.argv))
    if "--successors" in sys.argv:
        sys.exit(cmd_successors())
    if "--sync" in sys.argv:
        sys.exit(cmd_sync())
    if "--check" in sys.argv:
        sys.exit(cmd_check())
    print(__doc__, file=sys.stderr)
    print(
        "modes:\n"
        "  --baselines  per-ratchet baseline health (exists? empty? how many keys)\n"
        "  --init-absent  create every ABSENT baseline as a zero-byte file (ABSENT → EMPTY:\n"
        "               zero-tolerance, nothing grandfathered). MUTATES — state --apply or\n"
        "               --dry-run. Never touches an `ok` or EMPTY baseline.\n"
        "  --successors ⟡refusal-names-its-populator: does each gate's refusal name the\n"
        "               command that POPULATES what it checks? Reports a FLOOR (advisory)\n"
        "  --sync       rewrite the census blocks in the precommit-gates skill\n"
        "  --check      DRIFT GATE: exit 1 unless the STRUCTURAL block is current\n"
        "  --selftest   the guarded cases",
        file=sys.stderr,
    )
    sys.exit(2)
