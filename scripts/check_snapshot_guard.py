#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""check_snapshot_guard.py — an in-place source editor must be RECOVERABLE.

⟡ `scratch/edit_snapshot.py` exists because a tool rewrote 33 files and the work
was unrecoverable (`Coxeter/Core.agda` 76 lines → 3).  It records a `git stash
create` SHA and prints `git checkout <sha> -- <path>` so any single file can be
restored.  It never restores automatically — an automatic rollback would be a
revert in disguise, and reverting is what costs a day's work.

WHY A GATE AND NOT A CONVENTION.  MEASURED 2026-08-01: **59 tools have a write
path; 10 import `edit_snapshot`; 49 do not** — and the un-adopting set includes
tools that edit Agda sources in place, i.e. exactly the ones that can repeat the
incident.  One-by-one adoption is what produced that ratio, so the population has
to be DISCOVERED and gated, not declared and hoped for.

THE PREDICATE IS THE READ-THEN-WRITE SHAPE, not "has a write".  A generator that
writes a NEW file (`gen_kat.py`, `gen_fcr_slices.py`) is not destructive and must
not be censused — a false positive banked into a paydown-only baseline is debt
that can never legitimately be paid (`ratchet.py`'s own warning).  So a tool is
censused iff it writes to a variable it also READ from: `open(p,"w")` where `p`
is also opened for reading, which is the in-place edit.

Paydown-only over a materialized census, per the standing shape.

Usage: check_snapshot_guard.py [--quiet] [--list]
"""

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "scratch"))
import ratchet

ROOT = os.path.dirname(HERE)
# ⚑ DISCOVERED, not declared: every .py under the tool dirs, so a NEW tool is
# covered the day it lands.  A frozen list is the defect this gate exists to
# catch, one level up (§9g).
DIRS = ("scratch", "scripts")
SKIP = {"edit_snapshot.py", "check_snapshot_guard.py"}

WRITE_VAR = re.compile(r'open\(\s*(\w+)[^)]*["\']w["\']')
BACKUP_DIRS = ("__pycache__", ".edit-snapshots", ".venv")


def in_place_editors():
    """{relpath} for tools that write back to a path they also read."""
    out = set()
    for d in DIRS:
        for p in sorted(glob.glob(os.path.join(ROOT, d, "*.py"))):
            if os.path.basename(p) in SKIP:
                continue
            if any(b in p for b in BACKUP_DIRS):
                continue
            src = open(p, encoding="utf-8", errors="replace").read()
            # ⚑ A SELFTEST FIXTURE IS NOT A WRITE PATH.  A `_selftest` routinely
            # writes a tempfile and reads it back to drive the predicate under test —
            # read-then-write on the same var, in a function that never touches a
            # source file.  MEASURED: that shape alone censused `mdstruct.py`, whose
            # only real write goes to a freshly-created tempfile.  Arming a fixture
            # would snapshot the repo on every selftest run and pay down nothing, so
            # the census stops at the suite boundary.
            _st = re.search(r"^def _selftest\(", src, re.M)
            if _st:
                src = src[: _st.start()]
            for m in WRITE_VAR.finditer(src):
                v = m.group(1)
                # ⚑ THE VARIABLE MUST ALSO BE READ.  My first cut also accepted
                # "bound to something ending .agda", which matched a GENERATOR's
                # output-path constant (`gen_kat.py:31 RELPATH = "…FullKATGen.agda"`)
                # and censused two generators that never read their target — a false
                # positive headed for a paydown-only baseline, which is debt that can
                # never legitimately be paid.  Destructive means READ-then-WRITE.
                # ⚑ AND THE SAME-VARIABLE TEST WAS NOT A SAME-VARIABLE TEST.
                # `{v}\b[^\n]*\)\.readlines\(\)` and `read_text\(\)[^\n]*{v}\b` match
                # ANY line mentioning `v` near ANY read, so a tool that reads `path`
                # and writes a fresh `tf` satisfied both halves.  MEASURED: it
                # censused `scratch/mdstruct.py`, which writes ONLY to a tempfile it
                # just created (`:390`) — a FALSE POSITIVE headed for a paydown-only
                # baseline, i.e. debt that can never legitimately be paid, which is
                # the exact hazard the comment above records for the previous cut.
                # The predicate must bind the write variable to a read OF THAT
                # VARIABLE: `open(v).read()`, `open(v).readlines()`, `Path(v)
                # .read_text()`.  File-level-vs-positional, one more time.
                # ⚑ AND MY FIRST TIGHTENING WENT TOO WIDE IN THE OTHER DIRECTION.
                # An `as\s+\w+` alternative was meant to catch `with open(v) as fh:
                # fh.read()`, but it also matches `with open(v,"w") as fh` — a
                # WRITE — so the census jumped 48→55 and re-admitted `gen_kat.py`,
                # the generator the comment above records as the ORIGINAL false
                # positive.  Undoing a fix by widening past it is the same defect
                # wearing the opposite sign; the read must be an actual read CALL,
                # and a `with` form is admitted only when the mode is not "w"/"a".
                _v = re.escape(v)
                # ⚑ AND THE `with` FORM MATCHED THE WRITE STATEMENT ITSELF.  With
                # `with open(out,"w") as fh`, WRITE_VAR binds v=out and a bare
                # `with open(v …) as \w+` alternative then re-matched that same line
                # as a "read" — a predicate satisfied by its own counterexample.
                # So a `with` counts only when the bound handle is later `.read()`,
                # which is a fact about the BODY, not about the open call.
                _mode = rf'(?:,\s*(?!["\'][wa])[^)]*)?'
                _rd = rf"open\(\s*{_v}\s*{_mode}\)"
                hit = re.search(
                    rf"{_rd}\s*\.read(?:lines)?\(\)"
                    rf"|Path\(\s*{_v}\s*\)\s*\.read_text",
                    src,
                )
                if not hit:
                    m2 = re.search(rf"with\s+{_rd}\s*as\s+(\w+)", src)
                    hit = m2 and re.search(rf"\b{m2.group(1)}\s*\.read(?:lines)?\(\)", src)
                if hit:
                    out.add(os.path.relpath(p, ROOT))
                    break
    return out


def sites(rel):
    """[(lineno, var, text)] — the read-then-write sites that CENSUSED `rel`.

    ⚑⚑ THE CENSUS NAMED A FILE AND NOTHING NAMED THE LINE, so every reader paid
    down a row by RE-DERIVING the predicate by hand — grepping for `open(`, or
    reading the whole file hunting the shape.  That is the judgement happening in
    the turn rather than in the program: two readers re-derive it differently, and
    one of them arms the wrong write.  `--list` answers *which tools*; this answers
    *which line in this tool*, which is the question a paydown actually asks.

    ⚑ IT DRIVES `in_place_editors`' OWN PREDICATE, never a second copy of it.  A
    reimplementation here could disagree with the gate — reporting a site the
    census does not hold, or missing the one it does — and this file's comments
    record that hazard six times over.  The loop below is the same WRITE_VAR /
    read-of-that-variable pair, kept in one place by construction: if `rel` is not
    in `in_place_editors()`, this returns empty rather than inventing a site.
    """
    if rel not in in_place_editors():
        return []
    src = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
    _st = re.search(r"^def _selftest\(", src, re.M)
    if _st:
        src = src[: _st.start()]
    out = []
    for m in WRITE_VAR.finditer(src):
        v = m.group(1)
        _v = re.escape(v)
        _mode = rf'(?:,\s*(?!["\'][wa])[^)]*)?'
        _rd = rf"open\(\s*{_v}\s*{_mode}\)"
        hit = re.search(
            rf"{_rd}\s*\.read(?:lines)?\(\)"
            rf"|Path\(\s*{_v}\s*\)\s*\.read_text",
            src,
        )
        if not hit:
            m2 = re.search(rf"with\s+{_rd}\s*as\s+(\w+)", src)
            hit = m2 and re.search(rf"\b{m2.group(1)}\s*\.read(?:lines)?\(\)", src)
        if hit:
            ln = src[: m.start()].count("\n") + 1
            out.append((ln, v, src.split("\n")[ln - 1].strip()))
    return out


# ⚑⚑ THE DELEGATED-WRITE FORMS.  A tool's FIRST destructive act is not always an
# `open(...,"w")` it performs itself: it can be a CALL to a helper that writes.
# `split_upstream.py` is the measured case — `SL.split(path, apply=True)` at :96
# destroys the monolith while the tool's own first `open(...,"w")` is at :130, so a
# "guard above the first open-write" rule would have placed the snapshot 34 lines
# AFTER the act it exists to recover.  That is not a hypothetical: it is the recorded
# incident ("the one file this tool destroys first was the one file the snapshot could
# not recover") reproduced by the rule that looks only at opens.
#
# ⚑ SO THIS LIST IS NOT USED TO PLACE THE GUARD — it is used to REFUSE to place it.
# A name here appearing before the first open-write makes the mitigation point
# UNDETERMINED, because the honest answer is that a delegated writer's destructive
# moment is inside a callee this census does not follow.  Naming a line anyway would
# be worse than naming none: a guessed line number gets FOLLOWED.
#
# ⚑⚑⚑ EVERY ENTRY IS RECEIVER-QUALIFIED, AND MY FIRST CUT WAS NOT — which reproduced
# the `--calls emit` defect CLAUDE.md records, in the file whose own comments name it.
# A bare roster of `("split", "replace", "rename", "unlink", …)` reads `str.split` and
# `str.replace` as destructive filesystem acts, so EVERY offender came back
# UNDETERMINED citing `split at :114` — a string method inside a parser.  Seven of
# seven rows refused for a reason that was false at all seven, which is strictly worse
# than the naive first-write rule it was meant to correct: it converts a wrong answer
# into a confident refusal, and a refusal nobody can act on is the route-around
# invitation this whole item exists to close.
#
# ⚑ SO THE DISCRIMINATOR IS THE RECEIVER, which `scan` resolves natively via its
# dotted-target form.  `os.replace` is a filesystem rename; `s.replace` is a string
# substitution, and they share only a spelling.  `shutil` and `Path` are named because
# they are the two other write surfaces in this corpus.  The receiver is SYNTACTIC
# (scan's own stated scope): an aliased `import os as _os` is a different key, and this
# reports "spelled this way", never "resolves to the os module".
DELEGATED_WRITE_FORMS = (
    "os.replace",
    "os.rename",
    "os.remove",
    "os.unlink",
    "os.truncate",
    "shutil.move",
    "shutil.copy",
    "shutil.copy2",
    "shutil.rmtree",
    "Path.write_text",
    "Path.write_bytes",
    "Path.unlink",
    "Path.rename",
)

# ⚑ THE DESTRUCTIVE SUBSET — the verbs that REMOVE or REPLACE a path rather than
# merely writing one.  Used only to ask whether a SIBLING module can destroy content
# the caller did not author; a sibling that writes caches and tempfiles (the
# `_pycodemod_core` shape) must not make every call into it UNDETERMINED.
DESTRUCTIVE_FORMS = (
    "os.replace",
    "os.rename",
    "os.remove",
    "os.unlink",
    "shutil.move",
    "shutil.rmtree",
    "Path.unlink",
    "Path.rename",
)

# ⚑ A SELF-OWNED TEMP PATH.  Matched against the destructive call's ARGUMENT SOURCE
# TEXT (`possrc[0]`) — an AST fact about that one argument, never a scan of the file's
# prose.  A sibling tearing down its own tempdir is not destroying the caller's
# content, which is `check_known` case (3)'s principle applied to a callee.
#
# ⚑⚑ IT IS A NAME HEURISTIC AND IS LABELLED AS ONE, because it cannot be anything
# else without dataflow: deciding that `self._tmp` HOLDS a tempfile path means
# following its binding, which is the call graph this gate does not build.  My first
# cut hid that behind a permissive pattern (`tmp\w*|td\b|d\b`) that would have matched
# a bare `d` — i.e. almost any single-letter path variable — and silently suppressed
# real delegated writes.  A heuristic that swallows the class it screens is worse than
# no screen, so the spellings are the MEASURED ones only, anchored whole-word.
#
# ⚑ THE BIAS IS DELIBERATE AND IS THE OPPOSITE OF THE ARM AROUND IT: a MISS here
# yields an UNDETERMINED row with a named witness a reader dismisses in one look,
# while an over-match yields a confident insertion line placed after a real deletion.
# So it errs toward reporting the delegation.
_TEMP_PATH = re.compile(r"^(?:self\._tmp|_tmp|tmpdir|tempdir)$")


def _open_sites(rel):
    """[(line, target_src, mode, ctx)] for every REAL `open()` CALL in `rel`.

    ⚑⚑⚑ AST, NOT SUBSTRING — and the four rows that forced it were COMMENTS WARNING
    ABOUT THIS EXACT DEFECT.  `WRITE_VAR` is a regex over source TEXT, so it matched
    `open(p, "w")` inside prose: `scope_source.py:422/:437/:442`, `vfs.py:408`,
    `seal_ops.py:13`, `unseal_defs.py:36`, and — the one that should have been
    decisive — `rename_at_source.py:215`, whose comment reads *"READ FIRST.
    `open(f,"w").write(sub(open(f).read()))` truncates the…"*.  A locator that points
    a reader at a comment explaining the hazard, instead of at the line that commits
    it, is reporting the METHOD as the SUBSTRATE.
    #
    ⚑ AND THE FIX IS NOT TO STRIP COMMENT LINES, which is a second textual patch
    wearing a fix's clothes: it would still mis-locate a write inside a string
    literal, a docstring code block, or a line where prose and code share the row.
    A `.py` write site is an AST FACT.  libcst cannot parse prose into a `Call` node,
    so the entire class is excluded BY CONSTRUCTION rather than by a filter that must
    be kept in step with new ways of writing prose.
    #
    ⚑ IT DELEGATES TO `_pycodemod_query.scan`, THE CORPUS AUTHORITY, and does not
    re-walk.  A second CST visitor here could disagree with the one every other
    structural query in this repo reads — reporting a site the corpus does not hold —
    which is the drift hazard this file's own comments record seven times over.
    `possrc` (the argument's source text) and `positions` (its constant value) are two
    readings of ONE stamped scan: the mode is recovered from `positions[1]`, the target
    from `possrc[0]`, and neither reading alone can say which variable a site writes.
    """
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    from _pycodemod_query import KwIndex, scan

    p = os.path.join(ROOT, rel)
    seen = KwIndex()
    rows = [r for r in scan([p], "open", kwseen=seen) if r[1] == "call"]
    out = []
    for _p, _k, _n, line in rows:
        pos = seen.positions.get((_p, line), {})
        src = seen.possrc.get((_p, line), {})
        kws = seen.constants.get((_p, line), {})
        # mode is `args[1]` positionally or `mode=` by keyword; anything else is a read
        mode = pos.get(1)
        if mode is None:
            mode = kws.get("mode")
        out.append((line, src.get(0), mode, seen.contexts.get((_p, line), "<module>")))
    return sorted(out)


def _delegated_writes(rel):
    """[(line, form, ctx)] — calls to a form that WRITES INSIDE A CALLEE.

    ⚑ THE HOLDER IS NOT THE WORKER, in the mutation family.  A census that reads only
    the writes a tool performs ITSELF cannot see the write it DELEGATES, and the
    delegated one is routinely FIRST — which is the whole reason the mitigation point
    is a different object from the offending line.

    ⚑ THE TARGETS ARE DOTTED, so `scan` filters by RECEIVER and a `str.replace` never
    reaches this list.  Its own scope applies unchanged: the receiver is syntactic, so
    a delegated write reached through an alias is a MISS here — which is the
    conservative direction (a missed delegation yields a NAMED mitigation line that a
    reader still verifies, where a false one yields an unactionable refusal).
    """
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    from _pycodemod_query import KwIndex, scan

    p = os.path.join(ROOT, rel)
    out = []
    for form in DELEGATED_WRITE_FORMS:
        seen = KwIndex()
        for _p, _k, _n, line in scan([p], form, kwseen=seen):
            if _k != "call":
                continue
            out.append((line, form, seen.contexts.get((_p, line), "<module>")))
    # ⚑⚑⚑ THE SECOND ARM, AND `split_upstream` IS THE CASE THAT DEMANDS IT.  The
    # receiver roster above is a list of STDLIB write surfaces, and the incident's own
    # first write is none of them: `SL.split(path, apply=True)` at :96, where `SL` is a
    # SIBLING TOOL in this same tree.  A roster arm can never reach that — the set of
    # sibling tools that write is the corpus itself — so keying on the stdlib alone
    # would have returned `:130` for the one file whose documented defect is that :130
    # is 34 lines too late.  The list would have been a fact about the roster, reported
    # as a fact about the tool.
    #
    # ⚑ SO THIS ARM IS DERIVED, NOT ENUMERATED: any call whose RECEIVER is a name the
    # file IMPORTS FROM THIS TREE is a delegation whose write behaviour lives in a
    # callee, and this census follows no callees.  That is not a claim the sibling
    # writes — it is a statement that this instrument CANNOT SEE whether it does, which
    # is precisely when UNDETERMINED is the honest verdict rather than a line number.
    #
    # ⚑ IT OVER-REPORTS, DELIBERATELY AND IN THE SAFE DIRECTION.  A read-only sibling
    # call (`AD.exports(path)`) also lands here and pushes the row to UNDETERMINED with
    # a named witness the reader can dismiss in one look.  The inverse error — a
    # confident insertion line placed after a delegated destruction — is the recorded
    # incident, and the two are not symmetric.
    # ⚑ THE METHOD NAME IS NOT ENUMERATED.  A roster of verbs (`split`, `apply`,
    # `run`, …) would be the frozen ALLOW-list this repo's own policy shape forbids —
    # sibling tool #4 spelling its entry point `emit_all` is caught by nothing.  What
    # is derivable is the RECEIVER, so every call on a local-module receiver counts,
    # whatever it is called.
    #
    # ⚑⚑ AND THE RECEIVER MODULE MUST ITSELF BE A WRITER, WHICH MY FIRST CUT DID NOT
    # CHECK — I predicted the over-report, called it "safe because it errs toward
    # UNDETERMINED", and shipped it. It then refused 2 of the 3 live offenders citing
    # `_pycodemod_core.py_files` and `_ctl._as_list`, both PURE READERS. An
    # over-report that fires on most of the population is not a conservative bias; it
    # is the census answering UNDETERMINED as its default, which is the same
    # unactionable refusal the bare-name roster produced one commit earlier. I
    # reproduced my own corrected defect because "errs safe" felt like an argument.
    #
    # ⚑ THE DISCRIMINATOR IS ALREADY IN THIS FILE: `in_place_editors()` is the set of
    # tools that write back what they read. A sibling in that set can destroy; a
    # sibling that writes nothing cannot, so a call to it is not a delegated write.
    #
    # ⚑⚑⚑ BUT `in_place_editors()` ALONE IS TOO NARROW, AND `split_lemmas` IS THE
    # PROOF — the exact module the incident names. It writes NEW leaf files and
    # DELETES the monolith, so it is destructive without ever rewriting a file it
    # read, and this gate's own predicate (read-then-write) cannot see it. Scoping
    # the arm to in-place editors therefore sent `split_upstream` back to `:130`:
    # the census silently stopped detecting the one case that motivated the whole
    # mitigation column, and the row read GREEN with a confident wrong line.
    #
    # ⚑ SO THE SIBLING TEST IS "DOES IT WRITE AT ALL", which is the union of the two
    # write shapes this file can already see: read-then-write (`in_place_editors`)
    # and a stdlib destructive call (`DELEGATED_WRITE_FORMS` in the sibling's own
    # source). That is still DERIVED per sibling and still excludes the pure readers
    # (`_pycodemod_core`, `_ctl`) whose false refusals the previous cut produced.
    _writers = in_place_editors()
    local = {b for b, mod in _local_module_names(rel).items() if _sibling_writes(mod, _writers)}
    if local:
        seen = KwIndex()
        for _p, _k, name, line in scan([p], None, kwseen=seen):
            if _k != "call":
                continue
            recv = seen.receivers.get((_p, line))
            if recv in local:
                out.append((line, f"{recv}.{name}", seen.contexts.get((_p, line), "<module>")))
    return sorted(out)


def _sibling_writes(mod, writers):
    """Can a call into sibling module `mod` destroy content this census cannot see?

    ⚑ THE UNION OF THE TWO WRITE SHAPES THIS FILE CAN SEE, and it is a union because
    each alone misses a measured case.  `in_place_editors()` misses `split_lemmas`
    (writes new leaves, DELETES the monolith — destructive without read-then-write),
    which is the module the `split_upstream` incident names.  A stdlib-destructive
    scan alone would miss a sibling that only rewrites what it read.

    ⚑ IT ANSWERS "CAN IT WRITE", NEVER "DOES THIS CALL WRITE".  Following the callee
    to decide whether THIS entry point is the destructive one needs a call graph this
    gate does not build — which is exactly why a positive answer yields UNDETERMINED
    rather than a line, and why the reason names the sibling so a reader can dismiss
    it in one look.
    """
    for d in DIRS:
        rel = os.path.join(d, mod + ".py")
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        if rel in writers:
            return True
        # ⚑ STRUCTURAL, NOT A SUBSTRING TEST.  My first cut here asked whether the
        # sibling's SOURCE TEXT contains `os.replace` — which is the very defect this
        # whole change exists to remove, reintroduced one call deeper, inside the
        # helper that decides when to trust the AST result.  `scan` with a dotted
        # target is already the receiver-qualified authority; there is no reason to
        # approximate it here except that the text was in hand.
        #
        # ⚑⚑⚑ AND THE FORM SET IS NARROWED TO THE *DESTRUCTIVE* VERBS, not every
        # write.  Widening this to "opens any file for writing" re-admitted
        # `_pycodemod_core` — which writes its own caches and tempfiles and destroys
        # nothing of the CALLER's — and two of the three live offenders then refused
        # citing `_pycodemod_core.py_files`, a pure reader. That is the third time in
        # this one change that a broadened predicate turned actionable rows into
        # unactionable refusals, and the pattern is the same each time: I widened to
        # avoid a miss, without asking whether the added shape can destroy anything.
        #
        # ⚑ THE QUESTION IS "CAN IT DESTROY CONTENT THE CALLER DID NOT AUTHOR", so a
        # sibling qualifies by REMOVING or REPLACING a path — the shapes that made the
        # 33-file incident — not by having a write path at all.  `split_lemmas`
        # qualifies (it deletes the monolith); `_pycodemod_core` does not.
        #
        # ⚑⚑ AND A DESTRUCTIVE CALL ON A PATH THE SIBLING ITSELF CREATED IS NOT ONE.
        # `_pycodemod_core:583` is `shutil.rmtree(self._tmp)` in a context manager's
        # `__exit__` — it removes the tempdir that same object extracted, and destroys
        # nothing the caller authored. Counting it made BOTH `_pycodemod_census` and
        # `_pycodemod_fingerprint` refuse, citing `_pycodemod_core.py_files`, a pure
        # reader: the census pointed at the wrong module for the wrong reason.
        #
        # ⚑ THIS IS THE SAME CARVE-OUT `check_known` CASE (3) ALREADY RECORDS one level
        # in — "a file the tool creates then re-reads is not an in-place edit" — and it
        # has to be restated here because that one is about the CALLER's own opens and
        # this is about a SIBLING's teardown. Same principle, two populations; the
        # discriminator is that the argument is a self-owned temp path (`self._tmp`,
        # a `tempfile` binding), not a path that arrived from outside.
        sys.path.insert(0, os.path.join(ROOT, "scratch"))
        from _pycodemod_query import KwIndex, scan

        for form in DESTRUCTIVE_FORMS:
            seen = KwIndex()
            for _p, k, _n, line in scan([p], form, kwseen=seen):
                if k != "call":
                    continue
                arg = (seen.possrc.get((_p, line), {}) or {}).get(0) or ""
                if _TEMP_PATH.search(str(arg)):
                    continue  # its own tempdir — not the caller's content
                return True
    return False


def _local_module_names(rel):
    """{bound_name: module} for imports of a module that lives in THIS tree.

    ⚑ THE POPULATION IS THE TREE, NOT A ROSTER.  `import splitlib as SL` binds `SL` to
    a sibling tool; `import os` binds `os` to the stdlib.  Only the first is a
    delegation this census cannot follow, and the discriminator is whether a file of
    that name exists under `scratch/` or `scripts/` — a fact about the tree, re-derived
    on every call, never a list anyone maintains here.
    """
    src = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
    try:
        import libcst as cst

        tree = cst.parse_module(src)
    except Exception:
        return set()
    names = {}
    for node in tree.body:
        stmt = getattr(node, "body", [node])
        for s in stmt if isinstance(stmt, (list, tuple)) else [stmt]:
            if isinstance(s, cst.Import):
                for a in s.names:
                    mod = a.evaluated_name
                    names[a.evaluated_alias or mod] = mod
    out = {}
    for bound, mod in names.items():
        if "." in mod:
            continue
        for d in DIRS:
            if os.path.exists(os.path.join(ROOT, d, mod + ".py")):
                out[bound] = mod
    return out


def mitigation(rel):
    """(line_or_None, reason) — WHERE `guard()` belongs, or why that is UNDETERMINED.

    ⚑⚑⚑ THE MITIGATION POINT IS NOT THE OFFENDING LINE, AND CONFLATING THEM IS THE
    MEASURED `split_upstream` DEFECT.  The census detects a READ-THEN-WRITE PAIR; the
    guard goes immediately before the FIRST WRITE, which is a different position.  In
    `split_upstream.py` the destructive act is `SL.split(path, apply=True)` while the
    tool's own first write-mode open is ~34 lines later — *"the one file this tool
    destroys first was the one file the snapshot could not recover."*

    ⚑ AND THAT TOOL IS PAID DOWN AS OF 2026-08-26 — `require_at_entry` now precedes
    the split, and `disagreement()` reads `intent=entry / snapshot=entry` on it.  It
    is cited here as the HISTORICAL WITNESS for why the two spans are different
    objects, NOT as a live offender: this docstring is the kind of prose that rots
    into a false present-tense claim, which is the defect `fresh-comments-are-
    hypotheses-too` records, so the status is dated rather than implied.  Re-derive
    with `--sites scratch/split_upstream.py` before quoting it as current.

    ⚑⚑ SO A GUESS IS WORSE THAN A GAP, and this returns `None` rather than a plausible
    line in three cases, each named at the site:

      · a DELEGATED write (a call that writes inside a callee) precedes the first
        open-write — the real first write is in code this census does not follow;
      · the write arms live in MORE THAN ONE enclosing scope — there is no single
        line that dominates them, and the fix is an entry guard, not an insertion;
      · the file is censused with no locatable write at all (a predicate/locator
        disagreement, which is a fact about the instrument and must read as one).

    A returned line is the FIRST STATEMENT of the enclosing scope's write region: the
    guard goes ABOVE the first write, inside the scope that performs it.
    """
    opens = _open_sites(rel)
    writes = [
        (ln, tgt, ctx)
        for ln, tgt, mode, ctx in opens
        if isinstance(mode, str) and mode[:1] in ("w", "a", "x")
    ]
    if not writes:
        return None, (
            'no `open(...,"w")` CALL found by the AST locator, though the '
            "census holds this file — a locator/predicate disagreement, "
            "which is a fact about the instrument, not about the file"
        )
    first_w = writes[0][0]
    scopes = {ctx for _ln, _t, ctx in writes}
    # ⚑ THE DELEGATION CHECK RUNS FIRST, because a delegated write EARLIER than the
    # first open-write makes every later computation answer the wrong question.
    deleg = [(ln, form, ctx) for ln, form, ctx in _delegated_writes(rel) if ln < first_w]
    if deleg:
        w = ", ".join(f"`{f}` at :{ln}" for ln, f, _c in deleg[:3])
        return None, (
            f"a DELEGATED write precedes the first open-write at :{first_w} "
            f"({w}) — the real first write is inside a callee this census "
            f"does not follow, and the `split_upstream` incident is exactly "
            f"this shape. Guard at the tool's ENTRY, not at a write."
        )
    if len(scopes) > 1:
        arms = ",".join(f":{ln}" for ln, _t, _c in writes)
        return None, (
            f"write arms in {len(scopes)} different scopes "
            f"({', '.join(sorted(scopes))}) at {arms} — no single line "
            f"dominates them; the fix is an entry guard, not an insertion"
        )
    return first_w, (
        f"immediately ABOVE the first write in `{writes[0][2]}` "
        f"({len(writes)} write arm(s) in this scope)"
    )


def census():
    """{relpath} for in-place editors that do NOT arm edit_snapshot."""
    keys = set()
    for rel in in_place_editors():
        src = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        if "edit_snapshot" not in src:
            keys.add(rel)
    return keys


def intent_census():
    """{relpath} for armed editors that never consult the contract AT THE DECISION.

    ⚑⚑⚑ ARMING IS NOT STATING, AND THE GAP IS ONE LAYER IN FROM THIS GATE'S OWN.
    `census()` above asks *does this tool snapshot before writing* — 49 of 53 now do,
    because gating beat convention (the docstring records 10 of 59 under convention
    alone).  This asks the next question: *does it consult the mutation contract WHERE
    THE CHOICE IS MADE*.

    MEASURED 2026-08-19: `pycodemod --guarded guard` reports **27 of 64 `guard` call
    sites sit under an `if`**, most of them `if apply:` — so the guard is reached only
    once apply is already TRUE, and the UNSTATED case (the whole population the ratchet
    measures) never reaches it.  Demonstrated live, same environment, one adopted tool
    and one not:

        SUBSTRATE_EXPLICIT_MUTATION=1 drop_dead_renames.py   → exit 2, REFUSED
        SUBSTRATE_EXPLICIT_MUTATION=1 prune_leaf_opens.py    → exit 0, "(dry run)"

    **The strict mode whose entire purpose is refusing an unstated intent does not fire
    on a tool that decides before it guards.**  `edit_snapshot.guard` is correct wherever
    it runs; it simply is not consulted at the decision.

    ⚑⚑ THE PREDICATE IS A TOOL-LEVEL DISJUNCTION, NOT A PER-CALL-SITE ONE.  A tool
    satisfies the contract by EITHER calling `ratchet.mutating_argv` at its decision
    (the general fix) OR passing `intent=` at every `guard` (the fixture/known-path
    escape).  Censusing per call site would flag a tool that legitimately does both in
    different branches — and a false positive banked into a paydown-only baseline is
    debt that can never legitimately be paid, which is the hazard this file's own
    comments record FIVE times.

    ⚑ SCOPED TO ARMED EDITORS ONLY.  A tool with no `edit_snapshot` is already censused
    by `census()`; counting it here too would make one defect appear as two and let the
    same paydown clear both baselines.
    """
    keys = set()
    for rel in in_place_editors():
        src = open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace").read()
        # ⚑⚑ THE POPULATION IS TOOLS THAT CALL `guard`, NOT TOOLS THAT MENTION
        # `edit_snapshot`.  My first cut reused `census()`'s `"edit_snapshot" in src`
        # membership test — which matches an IMPORT, a DOCSTRING, or a ⚑ COMMENT.  That
        # censused `pycodemod`, `toolmodes` and `run_selftests`, none of which call
        # `guard` at all (`--guarded guard` over the three: **0 of 0 call sites**).
        # Three false positives, headed for a paydown-only baseline — the hazard this
        # file's own comments record FIVE times, and I reproduced it on the sixth.
        #
        # ⚑ `census()`'s looser test is CORRECT FOR ITS QUESTION: *is this tool aware of
        # edit_snapshot at all* — a mention is evidence of awareness.  Mine asks *does
        # this tool's guard consult the contract*, which presupposes a guard.  Same
        # string, two questions, and only one of them is about mentions.
        if not re.search(r"\bguard\s*\(", src):
            continue  # no guard here — census()'s question, not mine
        # ⚑⚑ THREE SPELLINGS, ONE CAPABILITY — AND THIS PREDICATE KNEW TWO (Ⓐ44).
        # `require_at_entry` is the ENTRY form of the same authority: it delegates to
        # `edit_snapshot.require_explicit_mutation` and runs BEFORE any mode dispatch,
        # which is strictly earlier than `mutating_argv` at the decision and strictly
        # earlier than an `intent=` at a guard.  Omitting it made this gate report
        # PAID-DOWN tools as offenders — `census-keyed-on-one-spelling`, in the gate whose
        # own docstring names that defect class, against the strongest form of the very
        # contract it measures.  A census that cannot see the best fix scores it as debt.
        #
        # ⚑ AND THE THREE ARE NOT INTERCHANGEABLE, so all three are named rather than
        # collapsed to a substring of one: `mutating_argv` consults at the DECISION,
        # `intent=` states a KNOWN path at a guard, `require_at_entry` demands it at the
        # INVOCATION.  They differ in WHERE, not in what they assert — which is exactly
        # why a predicate keyed on one spelling reads a stronger answer as a missing one.
        if "mutating_argv" in src or "intent=" in src or "require_at_entry" in src:
            continue
        keys.add(rel)
    return keys


def split_census():
    """{relpath} for tools whose intent gate and snapshot have DIFFERENT placements.

    ⚑⚑⚑ THE THIRD DEBT, AND IT IS AN EDGE RATHER THAN A PROPERTY (Ⓐ55
    ⟡scope-fix-last-split).  `census()` asks *does it snapshot*; `intent_census()` asks
    *does it name the contract*.  A tool can pass BOTH and still be unprotected: state
    intent at entry (so `intent_census` scores it compliant) while snapshotting only at a
    pending write, so a read-only mode, a restoring dry run, or a run that finds nothing
    to change never reaches the snapshot.  Neither existing ratchet can see it, because
    each reads ONE guard and nothing read the RELATION.

    ⚑⚑ THE OPERATOR NAMED THE MECHANISM, NOT JUST THE DEFECT (2026-08-25): the snapshot
    *"needs to be triggered at the same place as the gate for live vs dry, else it will
    get missed downstream for the same reason the gate was."*  Co-location is the fix,
    so co-location is what this measures — `require_at_entry(paths=...)` performs both in
    one act, and a tool that does that cannot drift back apart.

    ⚑ IT DELEGATES TO THE EXISTING AUTHORITY AND DOES NOT RE-DERIVE IT.
    `_pycodemod_placement.disagreement` already computes the verdict (it is what
    `pycodemod --unbound-snapshot` prints); a second predicate here would be a fourth
    spelling of the same question, and a ratchet built on a drifting copy reports its own
    skew as the tools' skew — this file's own comments record that hazard six times.

    ⚑ SCOPED TO `SPLIT` ALONE, deliberately.  `snapshot-only` (49 tools) is the
    *unadopted* population that `mutation-intent` already counts, and banking it here too
    would make one defect appear as two and let a single paydown clear both baselines.
    `store` is NOT APPLICABLE by construction and `bound` is the paid-down state.
    """
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    import _pycodemod_placement as _pl

    return {rel for rel, v in _pl.disagreement().items() if v[0] == "SPLIT"}


def _render_guard(k):
    """`✗ <rel>` PLUS the offender span and the mitigation span, on their own lines.

    ⚑⚑⚑ THE CENSUS THAT FIRES PRINTED A BARE FILENAME WHILE THE LOCATOR ALREADY
    EXISTED.  `--sites` computed the read-then-write line specifically so a paydown
    would stop re-deriving the predicate by hand — and the gate that REFUSES the commit
    printed none of it, so a reader met `✗ scratch/split_census.py` and had to know
    that a second mode existed, run it, and then filter its 100 whole-corpus rows down
    to the 3 the census names.  A refusal whose successor is named too imprecisely to
    act on is the route-around invitation, one level in from the rule that forbids it.

    ⚑⚑ AND THE TWO SPANS ARE DIFFERENT OBJECTS, which is the half worth having.  The
    OFFENDER span is the read-then-write pair the predicate matched; the MITIGATION span
    is where `guard()` belongs, immediately before the FIRST write.  In
    `split_upstream.py` those were 34 lines apart and the gap IS the recorded incident
    ("the one file this tool destroys first was the one file the snapshot could not
    recover"), so a census that prints only the first leaves the reader to re-derive the
    one thing that was measurably gotten wrong.

    ⚑ AN UNDETERMINED MITIGATION PRINTS ITS REASON AND NEVER A LINE.  A guessed number
    here would be FOLLOWED, and following it is how the snapshot lands after the
    destruction.
    """
    lines = [f"✗ {k}"]
    for ln, v, text in sites(k):
        lines.append(f"      offender  {k}:{ln}  writes `{v}` (also read)  {text}")
    mit, why = mitigation(k)
    if mit is None:
        lines.append(f"      mitigation: UNDETERMINED — {why}")
    else:
        lines.append(f"      mitigation: insert `edit_snapshot.guard(...)` at {k}:{mit} — {why}")
    return "\n".join(lines)


def _guard_calls(rel):
    """[(line, ctx, conds)] for every `guard`/`_snapshot_once` CALL in `rel`.

    ⚑ THE SPAN FOR THE OTHER TWO CENSUSES IS A CALL SITE, NOT A WRITE.  `snapshot-guard`
    points at a write because its offender IS a write; the intent and split censuses
    point at the guard whose PLACEMENT is wrong, which is a different object again.
    """
    sys.path.insert(0, os.path.join(ROOT, "scratch"))
    from _pycodemod_query import KwIndex, scan

    p = os.path.join(ROOT, rel)
    out = []
    for form in (
        "guard",
        "_snapshot_once",
        "require_at_entry",
        "require_explicit_mutation",
        "mutating_argv",
    ):
        seen = KwIndex()
        for _p, k, _n, line in scan([p], form, kwseen=seen):
            if k != "call":
                continue
            out.append(
                (
                    line,
                    form,
                    seen.contexts.get((_p, line), "<module>"),
                    seen.conds.get((_p, line), []),
                )
            )
    return sorted(out)


def _render_intent(k):
    """`✗ <rel>` PLUS the guard sites and the decision the tool never consults.

    ⚑⚑⚑ THE OFFENDER HERE IS A DECISION POINT, NOT A WRITE, so its span is a
    different object from `snapshot-guard`'s and the mitigation is a different act.
    This census asks *does the tool consult the contract WHERE THE CHOICE IS MADE*;
    the answer is "no" precisely when a `guard` exists but sits under `if apply:` —
    so the useful span is the GUARD SITE plus the CONDITION it hides behind, which
    `KwIndex.conds` already records and nothing printed.

    ⚑ THE MITIGATION IS NAMED, NOT LOCATED.  The fix is a call at the tool's ENTRY —
    a position that does not yet exist in the file — so there is no honest line to
    print, and inventing one would be the guessed-number defect. The row names the
    act (`require_at_entry` at the entry point) and lets the reader place it.
    """
    lines = [f"✗ {k}"]
    for ln, form, ctx, conds in _guard_calls(k):
        cond = f"  under `if {conds[-1]}`" if conds else "  (unconditional)"
        lines.append(f"      guard site  {k}:{ln}  `{form}` in {ctx}{cond}")
    lines.append(
        "      mitigation: NO LINE — the fix creates a position that does "
        "not exist yet. Call `ratchet.mutating_argv(argv, label)` BEFORE "
        "`apply` is bound, or `edit_snapshot.require_at_entry(label, "
        "paths=...)` at the entry point."
    )
    return "\n".join(lines)


def _render_split(k):
    """`✗ <rel>` PLUS BOTH placements — the span here is an EDGE, not a point.

    ⚑⚑⚑ THE OFFENDER IS THE RELATION BETWEEN TWO SITES, so a single span cannot
    express it.  `SPLIT` means the intent gate is at entry and the snapshot is at a
    pending write; naming either alone reads as a property of that one call and sends
    a reader to "fix" whichever it saw.  Both placements are printed, which is what
    makes the DISTANCE between them legible — and the distance is the defect.
    """
    lines = [f"✗ {k}"]
    # ⚑ SCOPED TO THE ONE FILE, NOT THE CORPUS.  `disagreement()` defaults to every
    # `.py` in the tree, so calling it per rendered key re-scanned the whole corpus
    # once per offender — minutes of work on the gate's FAILURE path, which is exactly
    # when a reader is waiting. It accepts a `paths` argument; passing one turns the
    # render into a single-file query.
    row = None
    try:
        sys.path.insert(0, os.path.join(ROOT, "scratch"))
        import _pycodemod_placement as _pl

        row = _pl.disagreement([os.path.join(ROOT, k)]).get(k)
    except Exception:
        row = None
    if row:
        _kind, i, s, _sw = row
        lines.append(f"      intent gate   {i[0]:<12} ({i[1] or '—'})")
        lines.append(f"      snapshot      {s[0]:<12} ({s[1] or '—'})")
    else:
        # ⚑ SAY THAT THE PLACEMENT IS UNAVAILABLE, never omit it silently.  The two
        # placement lines ARE the content of a SPLIT row — the defect is the distance
        # between them — so dropping them leaves a row that looks complete and has
        # lost its subject.  Measured: `disagreement()` keys on its own ROOT, so a
        # file outside that tree yields no row and the renderer degraded to a bare
        # site list with no indication anything was missing.  An absence reported as
        # an absence is a fact; an absence rendered as a shorter answer is a wrong one.
        lines.append(
            "      intent gate / snapshot: PLACEMENT UNAVAILABLE — "
            "`_pycodemod_placement.disagreement()` returned no row for this "
            "path (it keys on its own ROOT). The site list below is still "
            "sound; the RELATION between the two guards is not shown."
        )
    for ln, form, ctx, conds in _guard_calls(k):
        cond = f"  under `if {conds[-1]}`" if conds else "  (unconditional)"
        lines.append(f"      site  {k}:{ln}  `{form}` in {ctx}{cond}")
    lines.append(
        "      mitigation: replace BOTH calls with ONE "
        "`edit_snapshot.require_at_entry(label, paths=<targets>)` at the "
        "entry point — co-location is the fix, so no separate insertion "
        "line is owed."
    )
    return "\n".join(lines)


def _selftest():
    """Counted from len(cases) — the predicate is the whole gate, so test IT."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ⚑⚑⚑ A KNOWN-FALSE-POSITIVE CASE IS RECORDED AS *KNOWN*, NEVER AS A PASS AND
    # NEVER AS A SILENT OMISSION (Ⓐ63, 2026-08-26).  Three shapes below are real
    # defects in `in_place_editors` — each MEASURED on a tool sitting in the
    # `snapshot-guard` baseline that does not rewrite a file it read.  Fixing the
    # predicate would SHRINK a gated census, which is the operator's call and not a
    # paydown agent's; so the finding is banked as an executable statement instead
    # of as prose that no one re-derives.
    #
    # ⚑ IT MUST NOT READ AS GREEN.  An `expectedFailure` that quietly passes is the
    # `@expectedFailure comparing two regexes it wrote` shape this file's own
    # `probe` comment records — a case that can never fail is decoration.  So a
    # `known` case FAILS THE RUN if it starts SUCCEEDING (the defect was fixed and
    # this bookkeeping is now stale), and otherwise prints itself as OPEN DEBT.
    known = []

    def check_known(name, got, want, why):
        ok = got == want
        known.append((name, ok, why))
        if ok:
            cases.append(
                (
                    name + "  [known-false-positive: NOW FIXED — "
                    "promote it to a plain case and delete the carve-out]",
                    False,
                    got,
                    want,
                )
            )

    import tempfile

    # ⚑ THE PROBE RE-IMPLEMENTED THE PREDICATE, SO IT TESTED A REGEX IT DEFINED
    # ITSELF — it could pass while the GATE stayed broken, and it did: the
    # same-variable defect below shipped under a green 5/5.  That is §6c/§7b-bis
    # exactly (an `expectedFailure` comparing two regexes it wrote), reproduced in
    # the gate built to catch guard defects.  It now drives `in_place_editors()`
    # over a real temp DIRS root, so a change to the predicate reaches the cases.
    def probe(body):
        d = tempfile.mkdtemp()
        sub = os.path.join(d, "scratch")
        os.makedirs(sub)
        open(os.path.join(sub, "t.py"), "w", encoding="utf-8").write(body)
        global ROOT, DIRS
        _root, _dirs = ROOT, DIRS
        try:
            ROOT, DIRS = d, ("scratch",)
            return "scratch/t.py" in in_place_editors()
        finally:
            ROOT, DIRS = _root, _dirs

    check(
        "read-then-write to the same var IS in-place",
        probe('s = open(path).read()\nopen(path,"w").write(s)'),
        True,
    )
    # ⚑ THE FALSE POSITIVE THIS GATE ALMOST BANKED.  My first predicate accepted
    # "the var is bound to something ending .agda", which matched a GENERATOR's
    # output-path constant (gen_kat.py:31) and censused two tools that never read
    # their target.  A false positive in a paydown-only baseline is debt that can
    # never legitimately be paid.
    check(
        "a GENERATOR writing a fresh file is NOT in-place",
        probe('RELPATH = "Substrate/Foo.agda"\nopen(path,"w").write(text)'),
        False,
    )
    check(
        "readlines() counts as a read",
        probe('L = open(path).readlines()\nopen(path,"w").write("x")'),
        True,
    )
    check(
        "writing a DIFFERENT var than the one read is not in-place",
        probe('s = open(src).read()\nopen(dst,"w").write(s)'),
        False,
    )
    check("no write at all", probe("s = open(path).read()"), False)
    # ⚑ THE LIVE FALSE POSITIVE, PINNED.  `mdstruct.py` reads `path` and writes a
    # freshly-created TEMPFILE; the old predicate's `{v}\b[^\n]*\)\.readlines\(\)`
    # and `read_text\(\)[^\n]*{v}\b` alternatives matched any line mentioning the
    # var near any read, so it censused a tool that never overwrites its input.
    check(
        "writing a tempfile after reading a source is NOT in-place",
        probe(
            'src = open(path, encoding="utf-8").read()\n'
            'tf = os.path.join(tempfile.mkdtemp(), "n.md")\n'
            'open(tf, "w", encoding="utf-8").write(norm)\n'
        ),
        False,
    )
    # ⚑ AND THE GUARD MUST STILL DISCRIMINATE — a fix that suppresses the class by
    # rejecting everything passes the case above while making the gate useless.
    check(
        "a with-statement in-place editor is still caught",
        probe('with open(path) as fh:\n    s = fh.read()\nopen(path, "w").write(s)\n'),
        True,
    )
    # ⚑ AND THE OPPOSITE OVER-WIDENING, PINNED.  Admitting any `open(v) as fh` as a
    # READ matched `with open(v,"w") as fh` too, re-admitting `gen_kat.py` — the
    # generator this gate's own comment names as the original false positive.
    # Undoing a fix by widening past it is the same defect with the opposite sign.
    check(
        "a WRITE-mode with-statement is not a read",
        probe('with open(out, "w") as fh:\n    fh.write(text)\n'),
        False,
    )
    # ⚑ THE THIRD FALSE-POSITIVE SHAPE: a tool's OWN `_selftest` writing a fixture
    # and reading it back is read-then-write on one var, in code that never touches
    # a source file.  Arming it would snapshot the repo on every suite run.
    check(
        "a read-then-write inside _selftest is not a write path",
        probe('def _selftest():\n    open(p, "w").write("x")\n    s = open(p).read()\n'),
        False,
    )
    # ⚑⚑⚑ THREE MORE FALSE-POSITIVE SHAPES, EACH MEASURED LIVE ON A BANKED
    # OFFENDER (2026-08-26).  All three sat in the `snapshot-guard` baseline as
    # DEBT, and none of them rewrites a file it read — which is debt that can never
    # legitimately be paid, the hazard this file's comments record SIX times and
    # that recurred a seventh, eighth and ninth time under spellings the truncation
    # and the file-level variable test could not see.
    #
    # ⚑ (1) THE SUITE IS NOT ALWAYS SPELLED `_selftest`.  The carve-out above
    # truncates at `^def _selftest\(`, and `_pycodemod_fingerprint.py` spells its
    # suite `_cases(check)` — a module with NO `__main__`, whose cases are counted
    # by a PARENT suite (its own docstring says so).  Its only write is a tempfile
    # fixture at :786.  The carve-out is about the SUITE BOUNDARY, not about one
    # name, so a fixture-shaped write must not be censused because the suite chose
    # a different spelling.  `census-keyed-on-one-spelling`, in the gate whose own
    # comments name that defect class.
    check_known(
        "a fixture write inside a differently-NAMED suite is not a write path",
        probe(
            "def _cases(check):\n"
            '    p = os.path.join(tempfile.mkdtemp(), "f.py")\n'
            '    open(p, "w", encoding="utf-8").write("x")\n'
            "    s = open(p).read()\n"
        ),
        False,
        "scratch/_pycodemod_fingerprint.py:786 — suite spelled `_cases`, "
        "not `_selftest`, so the truncation misses it",
    )
    # ⚑ (2) TWO SCOPES, ONE SPELLING — the read and the write are DIFFERENT
    # VARIABLES.  MEASURED on `split_census.py`: `run_census.log` (:763) is
    # write-only (it is the `.build.log` the tool CREATES and hands to `make` as a
    # stdout sink), while the reads live in `census_from_build.log` (:601) and
    # `log_is_fresh.log` (:307) — three separate bindings in three functions, which
    # `--binding log` reports as such.  The predicate is FILE-LEVEL, so it read
    # "some `log` is written and some `log` is read" as in-place.  This is the
    # file-level-vs-positional correction this file has made three times already,
    # one axis further out: not positional within a line, but SCOPED within a file.
    check_known(
        "a same-named variable in a DIFFERENT function is not the same variable",
        probe(
            "def make(root):\n"
            '    log = os.path.join(root, ".build.log")\n'
            '    with open(log, "w", encoding="utf-8") as fh:\n'
            "        subprocess.call(cmd, stdout=fh)\n"
            "def read_it(p):\n"
            "    log = p\n"
            "    return open(log).read()\n"
        ),
        False,
        "scratch/split_census.py:768 — `run_census.log` is write-only; the "
        "reads are `census_from_build.log` and `log_is_fresh.log`",
    )
    # ⚑ (3) A FILE THE TOOL ITSELF JUST CREATED IS NOT A FILE IT READ.  MEASURED on
    # `_pycodemod_census.discriminates` (:532-534): it writes a `.mutant-<pid>-….py`
    # BESIDE the original (deliberately — a mutant in /tmp cannot resolve its
    # siblings), imports it, and `os.unlink`s it in `finally`.  The import machinery
    # reads it, so read-then-write holds on the variable — but the content
    # destroyed is content this same call wrote one line earlier.  Destructive means
    # overwriting content the tool did NOT author; a snapshot here would record the
    # repo on every mutation sweep and recover nothing that was ever at risk.
    check_known(
        "a file the tool creates then re-reads is not an in-place edit",
        probe(
            'mp = os.path.join(os.path.dirname(path), ".mutant-%d.py" % os.getpid())\n'
            'with open(mp, "w", encoding="utf-8") as fh:\n'
            "    fh.write(mutated)\n"
            "s = open(mp).read()\n"
            "os.unlink(mp)\n"
        ),
        False,
        "scratch/_pycodemod_census.py:534 — the `.mutant-<pid>.py` this call "
        "just wrote, imported, and unlinks in `finally`",
    )

    # ── the SPANS: the AST locator and the mitigation point ──────────────────────
    # ⚑⚑⚑ EVERY CASE HERE IS A SHAPE THE TEXTUAL LOCATOR GOT WRONG OR COULD NOT SEE.
    # `--sites` matched `open(p, "w")` inside PROSE at seven sites, several of them
    # comments WARNING about this defect (`rename_at_source.py:215` reads *"READ FIRST.
    # `open(f,"w").write(...)` truncates the…"*).  A locator that points a reader at the
    # comment explaining the hazard instead of the line committing it reports the METHOD
    # as the SUBSTRATE.
    def sitesprobe(body, fn):
        d = tempfile.mkdtemp()
        sub = os.path.join(d, "scratch")
        os.makedirs(sub)
        open(os.path.join(sub, "t.py"), "w", encoding="utf-8").write(body)
        global ROOT, DIRS
        _root, _dirs = ROOT, DIRS
        try:
            ROOT, DIRS = d, ("scratch",)
            return fn("scratch/t.py")
        finally:
            ROOT, DIRS = _root, _dirs

    def writes_at(rel):
        return [
            ln
            for ln, _t, mode, _c in _open_sites(rel)
            if isinstance(mode, str) and mode[:1] in ("w", "a", "x")
        ]

    # ⚑ THE DEFECT THAT MOTIVATED THE WHOLE CHANGE: a write spelled inside a COMMENT.
    # libcst cannot parse prose into a Call node, so the class is excluded BY
    # CONSTRUCTION rather than by a comment-stripping filter that would still miss a
    # write spelled inside a string literal or a docstring code block.
    check(
        "a write spelled in a COMMENT is not a write site",
        sitesprobe(
            '# READ FIRST. open(f,"w").write(g(open(f).read())) truncates\ns = open(f).read()\n',
            writes_at,
        ),
        [],
    )
    check(
        "...and the REAL write on the next line still is",
        sitesprobe(
            '# warning: open(f,"w") truncates\ns = open(f).read()\nopen(f,"w").write(s)\n',
            writes_at,
        ),
        [3],
    )
    # ⚑ A WRITE INSIDE A DOCSTRING is the same class and would survive a
    # comment-stripping patch — which is why the fix is AST, not a second regex.
    check(
        "a write spelled in a DOCSTRING is not a write site",
        sitesprobe('"""usage: open(p, "w") overwrites."""\ns = open(p).read()\n', writes_at),
        [],
    )
    check(
        "`mode=` by keyword is recognised as a write",
        sitesprobe('s = open(p).read()\nopen(p, mode="w").write(s)\n', writes_at),
        [2],
    )
    # ⚑⚑ THE MITIGATION POINT IS NOT THE OFFENDING LINE, and this is the case that
    # separates them: the guard belongs above the FIRST write, not at the pair the
    # census matched.
    check(
        "the mitigation point is the FIRST write in the scope",
        sitesprobe(
            "def go(p):\n"
            "    s = open(p).read()\n"
            '    open(p,"w").write(s)\n'
            '    open(p,"w").write(s)\n',
            lambda r: mitigation(r)[0],
        ),
        3,
    )
    # ⚑⚑⚑ THE `split_upstream` SHAPE, PINNED — a DELEGATED write before the first
    # open-write.  `SL.split(path, apply=True)` destroyed the monolith at :96 while the
    # tool's own first open-write was 34 lines later, so "guard above the first open"
    # would place the snapshot AFTER the destruction.  UNDETERMINED is the honest
    # verdict; a guessed line here gets FOLLOWED.
    check(
        "a DELEGATED write before the first open-write is UNDETERMINED",
        sitesprobe(
            "import os\n"
            "def go(p, q):\n"
            "    s = open(p).read()\n"
            "    os.replace(q, p)\n"
            '    open(p,"w").write(s)\n',
            lambda r: mitigation(r)[0],
        ),
        None,
    )
    # ⚑ AND A STRING METHOD SHARING THE SPELLING MUST NOT REFUSE.  My first cut listed
    # bare `("split", "replace", …)`, so `s.replace(...)` — a string substitution —
    # made every offender UNDETERMINED: seven of seven rows refused for a reason false
    # at all seven, which is worse than the naive rule it replaced.  The receiver is
    # the discriminator, and `scan`'s dotted form already resolves it.
    check(
        "a STRING method sharing the spelling does not refuse",
        sitesprobe(
            'def go(p):\n    s = open(p).read().replace("a", "b")\n    open(p,"w").write(s)\n',
            lambda r: mitigation(r)[0],
        ),
        3,
    )
    # ⚑ WRITE ARMS IN TWO SCOPES have no dominating line, so the fix is an entry guard
    # and the honest answer names that rather than picking one arm.
    check(
        "write arms in DIFFERENT scopes are UNDETERMINED",
        sitesprobe(
            "def a(p):\n"
            "    s = open(p).read()\n"
            '    open(p,"w").write(s)\n'
            "def b(q):\n"
            '    open(q,"w").write("x")\n',
            lambda r: mitigation(r)[0],
        ),
        None,
    )

    # ⚑⚑ THE OTHER TWO CENSUSES ARE AT ZERO, SO THEIR RENDERERS NEVER FIRE IN A LIVE
    # RUN — which is precisely the `@expectedFailure comparing two regexes it wrote`
    # shape this file's `probe` comment records: a code path that cannot execute is
    # decoration, and it would rot silently until the day a row appears and the gate
    # raises instead of reporting. These drive them on real shapes.
    check(
        "the intent renderer names the guard site AND the condition hiding it",
        "under `if apply`"
        in sitesprobe(
            "def go(p, apply):\n"
            "    s = open(p).read()\n"
            "    if apply:\n"
            '        guard("t", [p])\n'
            '        open(p,"w").write(s)\n',
            _render_intent,
        ),
        True,
    )
    # ⚑ AND IT MUST NOT INVENT A LINE.  The fix is a call at an entry point that does
    # not exist in the file yet, so there is no honest number to print.
    check(
        "the intent renderer prints NO mitigation line number",
        "NO LINE"
        in sitesprobe(
            "def go(p, apply):\n"
            "    s = open(p).read()\n"
            "    if apply:\n"
            '        guard("t", [p])\n'
            '        open(p,"w").write(s)\n',
            _render_intent,
        ),
        True,
    )
    # ⚑ THE SPLIT ROW IS AN EDGE, so BOTH guard sites must appear — naming either alone
    # reads as a property of that one call and sends a reader to fix the wrong half.
    _split_body = (
        "import edit_snapshot as _es\n"
        "def go(p, apply):\n"
        "    s = open(p).read()\n"
        "    if apply:\n"
        '        _es.guard("t", [p])\n'
        '        open(p,"w").write(s)\n'
        'if __name__ == "__main__":\n'
        '    _es.require_explicit_mutation("t")\n'
    )
    check(
        "the split renderer prints BOTH guard sites",
        sitesprobe(
            _split_body,
            lambda r: sum(
                x in _render_split(r) for x in ("`guard`", "`require_explicit_mutation`")
            ),
        ),
        2,
    )
    # ⚑⚑ AND WHEN THE PLACEMENT ROW IS UNAVAILABLE IT MUST SAY SO.  `disagreement()`
    # keys on its own ROOT, so a probe file outside that tree yields no row — and the
    # first cut of this renderer then dropped the two placement lines SILENTLY, leaving
    # a row that looked complete while having lost its entire subject (the RELATION
    # between the guards). Caught only because this case asserted on their presence.
    check(
        "an unavailable placement is REPORTED, not silently omitted",
        "PLACEMENT UNAVAILABLE" in sitesprobe(_split_body, _render_split),
        True,
    )

    # ── the SECOND ratchet: arming is not stating ────────────────────────────────
    # ⚑⚑ EVERY CASE HERE IS A SHAPE THE FIRST CUT GOT WRONG.  I reused `census()`'s
    # `"edit_snapshot" in src` membership test, which matches a MENTION — an import, a
    # docstring, a ⚑ comment — and censused `pycodemod`, `toolmodes` and
    # `run_selftests`, none of which call `guard` at all.  Three false positives headed
    # for a paydown-only baseline: the hazard this file records five times, reproduced
    # by me on the sixth.
    def iprobe(body):
        d = tempfile.mkdtemp()
        sub = os.path.join(d, "scratch")
        os.makedirs(sub)
        # the body must ALSO be an in-place editor, since `intent_census` is scoped to
        # that population — a probe that skips it would test a different predicate
        open(os.path.join(sub, "t.py"), "w", encoding="utf-8").write(
            's = open(path).read()\nopen(path,"w").write(s)\n' + body
        )
        global ROOT, DIRS
        _root, _dirs = ROOT, DIRS
        try:
            ROOT, DIRS = d, ("scratch",)
            return "scratch/t.py" in intent_census()
        finally:
            ROOT, DIRS = _root, _dirs

    check(
        "an armed editor that never states intent IS censused",
        iprobe('import edit_snapshot\nedit_snapshot.guard("t", [path])\n'),
        True,
    )
    # ⚑ THE TWO DISCHARGES, both of which must clear it — a tool satisfies the contract
    # by consulting it at the DECISION or by stating intent at a known path.
    check(
        "consulting the contract at the decision discharges it",
        iprobe(
            'import ratchet\nratchet.mutating_argv(sys.argv, "t")\n'
            'edit_snapshot.guard("t", [path])\n'
        ),
        False,
    )
    check(
        "stating intent= at the guard discharges it",
        iprobe('edit_snapshot.guard("t", [path], intent="apply")\n'),
        False,
    )
    # ⚑⚑ THE FALSE POSITIVE I SHIPPED AND CAUGHT: a MENTION is not a CALL.
    check(
        "a tool that only MENTIONS edit_snapshot is not censused",
        iprobe("# see edit_snapshot for the recovery story\n"),
        False,
    )
    check(
        "...nor is an import with no guard call",
        iprobe("import edit_snapshot  # noqa: F401\n"),
        False,
    )

    # ── the THIRD ratchet: the RELATION between the two guards ───────────────────
    # ⚑ DRIVEN THROUGH `disagreement()` — the authority this gate delegates to — rather
    # than through a predicate re-implemented here.  A probe that defines its own rule
    # tests a regex it wrote itself and can pass while the GATE stays broken, which is
    # the defect this file's own `probe` comment records shipping under a green 5/5.
    def sprobe(body):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "t.py")
        open(p, "w", encoding="utf-8").write(body)
        sys.path.insert(0, os.path.join(ROOT, "scratch"))
        import _pycodemod_placement as _pl

        rows = _pl.disagreement([p])
        return rows.get(os.path.relpath(p, _pl.ROOT), ("absent",))[0]

    # ⚑ THE DANGEROUS SHAPE, PINNED: intent at entry, snapshot at the write.  This is
    # `scope_fix.py` as it stood before Ⓐ55 — the row both other ratchets scored green.
    check(
        "intent at entry + snapshot at the write IS the SPLIT shape",
        sprobe(
            "import edit_snapshot as _es\n"
            'if __name__ == "__main__":\n'
            '    _es.require_explicit_mutation("t")\n'
            "    if apply:\n"
            '        _es.guard("t", paths)\n'
        ),
        "SPLIT",
    )
    # ⚑ AND THE PAID-DOWN SHAPE MUST READ CLEAN, or the gate would refuse its own remedy
    # — the `census-keyed-on-one-spelling` failure `intent_census` records, where a
    # predicate blind to the strongest fix scores it as debt.
    check(
        "one bound call (intent + snapshot in ONE act) is NOT split",
        sprobe(
            "import edit_snapshot as _es\n"
            'if __name__ == "__main__":\n'
            '    _es.require_at_entry("t", paths=args)\n'
        ),
        "bound",
    )

    ok = sum(1 for _, g, _, _ in cases if g)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got {got!r} want {want!r}")
    # ⚑ THE KNOWN FALSE POSITIVES ARE PRINTED, ALWAYS — a suite that swallows them
    # reports the boundary of its own bookkeeping as the boundary of the debt.
    for name, fixed, why in known:
        if not fixed:
            print(f"  KNOWN-FP (open) {name}\n       {why}")
    print(
        f"check_snapshot_guard selftest: {ok}/{len(cases)}"
        + (
            f"; {sum(1 for _, f, _ in known if not f)} known false-positive "
            f"shape(s) still in the predicate — see Ⓐ63"
            if known
            else ""
        )
    )
    return 0 if ok == len(cases) else 1


def main():
    if "--selftest" in sys.argv:
        return _selftest()
    if "--sites" in sys.argv:
        # ⚑ THE PAYDOWN MODE.  `--list` names the offending TOOLS; this names the
        # read-then-write SITES inside one, which is what arming it requires.
        i = sys.argv.index("--sites")
        want = sys.argv[i + 1] if i + 1 < len(sys.argv) else None
        # ⚑⚑ BARE `--sites` NOW ANSWERS THE CENSUS'S POPULATION, NOT THE CORPUS.  It
        # emitted 100 rows over every in-place editor while the gate named 3 offenders,
        # so joining the two meant filtering by hand — the judgement-in-the-turn shape,
        # demanded by the very mode built to remove it.  An ARMED tool's sites are not
        # a paydown target: it already snapshots.  `--sites <rel>` is unchanged and
        # still answers for any file, armed or not, because inspecting one tool is a
        # different question from listing the work.
        rels = [want] if want else sorted(census())
        if not want and not rels:
            print(
                "no offenders — every in-place editor arms edit_snapshot.guard() "
                f"({len(in_place_editors())} in-place editor(s) scanned)"
            )
            return 0
        for rel in rels:
            rows = sites(rel)
            if not rows:
                # ⚑ SAY WHICH ABSENCE THIS IS.  "not censused" and "censused with
                # no site" are different facts, and only one of them is a bug in
                # this mode — collapsing them would report the method as the
                # substrate, which is this file's recurring defect class.
                print(
                    f"{rel}: NOT an in-place editor by this census "
                    f"(so no sites — a fact about the predicate, not the file)"
                )
                continue
            for ln, v, text in rows:
                print(f"{rel}:{ln}  writes `{v}` (also read)  {text}")
            # ⚑ THE INSERTION POINT, BESIDE THE PAIR — the two are different positions
            # and this mode named only the first.
            mit, why = mitigation(rel)
            if mit is None:
                print(f"  → mitigation: UNDETERMINED — {why}")
            else:
                print(f"  → mitigation: insert `edit_snapshot.guard(...)` at {rel}:{mit} — {why}")
        return 0
    rc = ratchet.check_argv(sys.argv, {"--quiet", "--list", "--sites"}, "check_snapshot_guard")
    if rc is not None:
        return rc
    # ⚑ LIFTED — this copy used BOTH hooks, which is why it read as irreducibly
    # special: a `✗` mark per key (render) AND an armed-vs-unguarded breakdown over
    # the population (summary).  Neither needed its own dispatch; the DENOMINATOR
    # is the part worth keeping, since "34 unguarded" means nothing without the 43
    # in-place editors it is measured against — this arc's own report-the-population
    # rule, which the hand-rolled block happened to honour and the authority did not.
    _ed = in_place_editors()
    _un = census()
    rc = ratchet.set_ratchet(
        _un,
        os.path.join(HERE, "snapshot_guard_baseline.txt"),
        "snapshot-guard",
        "--quiet" in sys.argv,
        list_keys="--list" in sys.argv,
        render=_render_guard,
        summary=f"of {len(_ed)} in-place editor(s); {len(_ed) - len(_un)} armed",
        noun="in-place editor(s) with no edit_snapshot.guard()",
        refuse_hint=(
            "This tool rewrites a file it read — the shape that made 33 files "
            "unrecoverable. Arm it: `import edit_snapshot; edit_snapshot.guard(label, paths)` "
            "immediately before the first write. It prints a per-file recovery command and "
            "never restores anything on its own."
        ),
    )
    # ⚑⚑ THE SECOND RATCHET, ONE LAYER IN, OVER THE SAME DISCOVERED POPULATION.
    # `snapshot-guard` asks *does it snapshot before writing*; this asks *does it consult
    # the mutation contract WHERE THE CHOICE IS MADE*.  Separate baselines because they
    # are separate debts with separate paydowns — folding them would let arming a tool
    # clear an intent row it never addressed.
    #
    # ⚑ BOTH RUN, AND THE WORSE EXIT WINS.  Returning early on the first would make the
    # second invisible whenever the first is red — a gate that stops measuring at the
    # first failure reports the boundary of its own run as the boundary of the debt.
    _in = intent_census()
    rc2 = ratchet.set_ratchet(
        _in,
        os.path.join(HERE, "mutation_intent_baseline.txt"),
        "mutation-intent",
        "--quiet" in sys.argv,
        list_keys="--list" in sys.argv,
        render=_render_intent,
        summary=(
            f"of {len(_ed) - len(_un)} armed editor(s); "
            f"{len(_ed) - len(_un) - len(_in)} state intent at the decision"
        ),
        noun="armed editor(s) that decide BEFORE consulting the mutation contract",
        refuse_hint=(
            "`edit_snapshot.guard` runs where it is CALLED, and a quarter of its call "
            "sites sit under `if apply:` — so it never sees the UNSTATED case, which is "
            "the whole population the contract measures. Re-derive the split with "
            "`pycodemod --guarded guard`; a count quoted here rots (this string said "
            "'27 of 64' while the census said 68). ⚑ REFUSAL IS NOW THE DEFAULT "
            "(⟡explicit-mutation-default, 2026-08-25) — an adopted tool exits 2 and an "
            "unadopted one still prints '(dry run)' and exits 0, which is exactly the "
            "debt this row counts. Fix at the DECISION: call "
            "`ratchet.mutating_argv(argv, label)` before binding `apply`, or pass "
            "`intent=` at every guard when the path is known (a fixture, or a branch "
            "already gated on apply)."
        ),
    )
    # ⚑⚑⚑ THE THIRD RATCHET — the RELATION between the two guards, not either one.
    # `snapshot-guard` asks *does it snapshot*, `mutation-intent` asks *does it name the
    # contract*, and a tool can satisfy BOTH while being unprotected in practice.  That
    # shape (`SPLIT`) had no gate at all until Ⓐ55: it was detectable by `pycodemod
    # --unbound-snapshot` and nothing refused it, so it could regrow silently — which is
    # exactly how the 8-tool SPLIT population appeared in the first place, as a
    # side effect of the Ⓐ44 paydown that moved intent gates to entry and left the
    # snapshots behind.
    #
    # ⚑ A DETECTOR WITHOUT A RATCHET IS A MEASUREMENT, NOT A GUARD.  The census existed
    # and was correct; what was missing is the thing that refuses a NEW row.  A defect
    # class that was paid down to zero and left ungated is one commit from returning.
    _sp = split_census()
    rc3 = ratchet.set_ratchet(
        _sp,
        os.path.join(HERE, "snapshot_split_baseline.txt"),
        "snapshot-split",
        "--quiet" in sys.argv,
        list_keys="--list" in sys.argv,
        render=_render_split,
        summary=(
            f"of {len(_ed)} in-place editor(s); the intent gate and the snapshot must be ONE act"
        ),
        noun="tool(s) whose intent gate and snapshot have DIFFERENT placements",
        refuse_hint=(
            "This tool states its mutation intent at entry (so `mutation-intent` scores "
            "it compliant) but snapshots only at a pending write — so a read-only mode, "
            "a dry run that restores, or a run that finds nothing to change is "
            "UNPROTECTED. The operator's rule is co-location: the snapshot must be "
            "'triggered at the same place as the gate for live vs dry, else it will get "
            "missed downstream for the same reason the gate was.' Fix: replace BOTH "
            "calls with one `edit_snapshot.require_at_entry(label, paths=<targets>)` at "
            "the entry point — it checks intent and, on a stated --apply, takes the "
            "snapshot in the same act. Re-derive with `pycodemod --unbound-snapshot`."
        ),
    )
    # ⚑ ALL THREE RUN AND THE WORST EXIT WINS — returning early on the first would make
    # the later ones invisible whenever an earlier one is red, and a gate that stops
    # measuring at the first failure reports the boundary of its own run as the boundary
    # of the debt.
    return rc or rc2 or rc3


if __name__ == "__main__":
    sys.exit(main())
