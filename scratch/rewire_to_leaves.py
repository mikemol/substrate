#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Rewire every importer of a just-split module onto its leaves.

The Rewire step of the one-lemma-per-file loop
(.claude/skills/agda-ban-decompose/one-lemma-per-file.md):

    replace  `open import P`                 -> open every leaf of P
             `open import P using (a; b)`    -> open exactly the leaves owning a,b
    keeping  a trailing `public` and a trailing `-- comment`.

The bare form deliberately errs WIDE (open all leaves); `prune_imports.py` then
cuts it to what the consumer actually uses.  That is the whole point of pairing
the two: the rewire never has to know which names a bare importer used.

The name->leaf map is read from each leaf's own `-- Defines:` header, which
split_lemmas.py emits — never hand-written, so it cannot drift from the split.

Run from the REPO ROOT (like prune_imports.py; see F8 in the procedure doc).

    python3 scratch/rewire_to_leaves.py Substrate.Foundation.Nat.Properties.Add [...]
"""
import re, sys, glob, os
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import importable as _importable  # THE self-import predicate (never re-derive)

AG = "agda"



def _split_defines(line):
    """Split a `Defines:` list on separator commas only.

    A comma INSIDE a bracket-mixfix name (`[_,_]`, `⟨_,_⟩`) is part of the name,
    not a separator.  Track bracket depth and split at depth 0 only.
    """
    out, buf, depth = [], "", 0
    for ch in line:
        if ch in "[⟨⌊⌈(":
            depth += 1
        elif ch in "]⟩⌋⌉)":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            if buf.strip():
                out.append(buf.strip())
            buf = ""
        else:
            buf += ch
    if buf.strip():
        out.append(buf.strip())
    return out


from scope_fix import _rename_pairs   # THE renaming-clause parser; never re-derive

# ⚑⚑ `_snapshot_once` WAS DELETED HERE (Ⓐ49 ⟡split-8-unprotected).  Its rationale is
# KEPT AS RESIDUE — it was RIGHT about the danger, wrong only about PLACEMENT:
#
#   "This tool rewrites files it read — the shape that made 33 files unrecoverable
#    (Coxeter/Core.agda 76 lines -> 3).  The write is inside a loop, so a per-file
#    `guard` would arm only the first file AND shell out to `git stash create` on
#    every iteration; arming once per run is both correct and cheap."
#
# ⚑ AND SO IS THE FIXTURE-ESCAPE NOTE IT CARRIED, because that lesson OUTLIVES this
# helper — it is why `require_at_entry` has a `--selftest` carve-out at all:
#
#   "`intent="apply"` IS THE FIXTURE ESCAPE… `_selftest` drives `rewire(apply=True)`
#    against a TEMP FIXTURE, so this call is reached with an argv carrying `--selftest`
#    and neither mutation flag — MEASURED: `--selftest` exited 2 instead of running,
#    which is the 'if moving a guard breaks a selftest, the guard is too early' case
#    landing one level in."
#
# With the write-site call removed the selftest no longer reaches any snapshot at all,
# so the escape is unneeded HERE; VERIFIED `--selftest` -> 8/8 with no mutation flag.
# Leaving the def as dead code would make `--unbound-snapshot` read FALSE-RED, since it
# keys on a `guard` call site being PRESENT, not on it being REACHABLE.


def renaming_plan(stmt_text, m):
    """[(leaf_module, old, new)] for a `renaming (old to new; …)` clause.

    ⚑ THIS TOOL DID NOT PARSE `renaming` AT ALL, and I described that as the
    shape being unparseable — which was wrong and hid the real gap: a SHARED
    parser (`scope_fix._rename_pairs`) already existed and this tool had simply
    never adopted it (user: *"aren't we using a shared parser now?"*).
    `drop_dead_renames` and `demand_imports` both route through it; three tools
    agreeing and one abstaining is the Audit-IV class exactly.

    Returns None when any old-name has no owning leaf — the caller then leaves
    the statement alone and reports it, rather than emitting a half-rewrite.
    """
    pairs = _rename_pairs(stmt_text)
    if not pairs:
        return None
    out = []
    for old, new in pairs:
        # ⚑ RENAME-TO-SELF is pure noise: the alias binds the name to itself, so
        # the clause carries no meaning and only ban debt.  Emit a bare import.
        if old == new:
            if old not in m:
                return None
            out.append((m[old], old, None))
            continue
        if old not in m:
            return None
        out.append((m[old], old, new))
    return out


def _parent_module(parent):
    """A MODULE NAME from either spelling — `Substrate.A.B` or `agda/Substrate/A/B.agda`.

    ⚑⚑ THE TWO SPELLINGS MET HERE AND NEITHER SIDE KNEW. `leaf_map` did
    `os.path.join(AG, parent.replace(".", "/"))`, which is correct for a MODULE NAME and
    produces nonsense for a PATH: `split_pipeline` passes the path it was invoked with, so
    `agda/Substrate/…/SKIShedDuality.agda` became `…/SKIShedDuality/agda` (the extension read
    as a component, its dot replaced) and `AG` prepended `agda/` to a string already carrying
    it — `agda/agda/…/SKIShedDuality/agda`. TWO independent errors in one derived path, and
    the refusal message printed the broken path without either being visible as a cause.

    ⚑ REPORTED BY A PEER SESSION 2026-08-21, measured through the SUPPORTED path with the
    correct argument order — so `--rewire-only` could not reach ANY already-split parent, the
    one case its own docstring says it exists for. The tool refused honestly and the refusal
    named a directory that could never exist.

    ⚑ NORMALISED AT THE BOUNDARY RATHER THAN AT THE CALL SITES. `split_pipeline` is not the
    only caller and a per-caller fix is the "hand sweep is not a transform" shape; a function
    taking a name must accept the name in the spellings its callers have.
    """
    p = str(parent)
    if p.endswith(".agda"):
        p = p[:-5]
        # A path — strip a leading `agda/` if present, then read the module name off it.
        rel = os.path.relpath(os.path.abspath(p), AG)
        return rel.replace(os.sep, ".")
    return p


def leaf_map(parent):
    """name -> leaf-module-name, read from the leaves' `-- Defines:` headers."""
    parent = _parent_module(parent)
    d = os.path.join(AG, parent.replace(".", "/"))
    # ⚑ isdir IS TRUE FOR AN EMPTY DIRECTORY, and that is not a hypothetical:
    # `Algebra/F2/GF256/MulLaws/` holds five nested dirs (`Gmulidentity`,
    # `Gmulzero`, …) from an ABANDONED split under an older naming scheme and
    # ZERO `.agda` files.  The old guard passed, `leaf_map` returned {}, and the
    # caller reported "no leaf provides a name" — which reads as *the leaves do
    # not declare it* and sent me hunting a missing `-- Defines:` header across
    # 2216 files.  The truth was *there are no leaves*.  Say which.
    if not os.path.isdir(d):
        raise SystemExit(f"no leaf directory for {parent} (expected {d})")
    if not glob.glob(f"{d}/*.agda"):
        nested = [x for x in glob.glob(f"{d}/**/*.agda", recursive=True)]
        hint = (f"  ({len(nested)} .agda found in SUBdirectories — leaves are "
                f"expected directly under {d})" if nested else
                f"  (the directory exists but is EMPTY — an abandoned or "
                f"renamed split; {parent}.agda is probably still unsplit)")
        raise SystemExit(f"no leaf FILES for {parent}\n{hint}")
    # ⚑ A parent may have ALREADY had siblings in its namespace before the
    # split (`Algebra/Z.agda` beside 37 modules under `Algebra/Z/`).  Reading
    # `Defines:` from every file in the directory misreads those pre-existing
    # siblings as leaves, and any whose BASENAME collides with a real leaf
    # (`Sub`, `Mul`, `CommRing`, `Euclid`, …) is then excluded from the rewire
    # as a "self-import" — so it keeps importing the deleted parent and shows
    # up as a surviving reference.  Measured: 16 of 39 survivors on
    # Substrate.Algebra.Z.  A genuine leaf carries the splitter's provenance
    # marker; require it.
    marker = f"split horizontally\n-- out of {parent}"
    def _is_leaf(src):
        return ("⟡cap-128-forcing" in src
                and re.search(r"split horizontally\s*--?\s*out of "
                              + re.escape(parent) + r"\b", src))
    # ⚑⚑ CONSTRUCTORS COME FROM `agda_defs`, NOT FROM A HEADER — Ⓒ9′, reported by a peer
    # session 2026-08-21 and measured on both clusters. `-- Defines:` names what a leaf
    # DECLARES; a `data Tm` line declares `Tm` and says nothing about `S`/`K`/`I`, which are
    # INDENTED under it. The signature fallback below misses them for the same reason. So the
    # map had 16 names for 12 leaves and resolved none of the constructors, and 21 importers
    # came back UNMAPPED naming exactly `S`, `K`, `I`.
    #
    # ⚑ THE AUTHORITY ALREADY KNOWS. `agda_defs --provides …SKIShedDuality.Tm` returns
    # `I · K · S · Tm · _∙_ · ∙` — six names, both operator spellings, all three constructors.
    # Its own docstring states the contract this map was violating: *"Indexes top-level
    # definitions, `data`/`record` heads, THEIR CONSTRUCTORS (indented under a data head), and
    # `pattern` synonyms. Operator names are recorded both as written and bare, since a use
    # site spells the bare form."* Teaching THIS file to parse constructors would be a second
    # implementation of a solved problem — the reuse-search's whole point.
    #
    # ⚑ ADDITIVE, NOT REPLACING: the header and signature paths stay. A leaf whose module is
    # not in the def-index (never compiled, just written) still maps by its header, so a fresh
    # split does not depend on a build having happened. `agda_defs` WIDENS the map; it is not
    # a precondition for it.
    #
    # ⚑ AND THE FAILURE MODE THIS CLOSES IS ASYMMETRIC, which is why it blocks `--apply`
    # rather than merely degrading it: a partial rewire converts ONE FileNotFound (loud, one
    # line, obviously the split's fault) into 21 NotInScope errors spread across
    # `Category.UniversalProperty` — quiet-looking, and reading as the consumer's fault.
    m = {}
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import agda_defs as _ad
        _provides = _ad.provides
    except (ImportError, AttributeError):
        # ⚑ A MISSING AUTHORITY IS REPORTED BY ITS ABSENCE FROM THE MAP, never by a silent
        # narrowing that reads as "this leaf exports nothing". The header path still runs.
        _provides = None
    for p in sorted(glob.glob(f"{d}/*.agda")):
        leaf = os.path.basename(p)[:-5]
        if not _is_leaf(open(p).read()):
            continue
        if _provides is not None:
            try:
                for nm in _provides(f"{parent}.{leaf}"):
                    m.setdefault(nm, leaf)
            except Exception:
                pass
        for line in open(p):
            mo = re.match(r"^-- Defines: (.+)$", line.strip())
            if mo:
                # ⚑ THE `Defines:` LINE IS COMMA-SEPARATED, AND A BRACKET-MIXFIX
                # NAME CONTAINS A COMMA.  A bare `.split(",")` shatters `[_,_]`
                # into `[_` + `_]`, so the real name is absent from the map and
                # every consumer naming it is reported UNMAPPED — the rewire then
                # leaves their import pointing at the DELETED module.
                # MEASURED: the Foundation.Sum split reported 5 UNMAPPED files
                # (InternalLogic, DuplicateFree, OrientationSumComm,
                # OrientationDistributor, OrientationHexagon), all for `[_,_]`.
                # FIX: split only on commas OUTSIDE a bracketed run.  Depth is
                # tracked over the mixfix brackets so `[_,_]` and `⟨_,_⟩` stay
                # whole while a genuine `a, b` separator still splits.
                for nm in _split_defines(mo.group(1)):
                    m[nm] = leaf
                break
        else:
            # A hand-written leaf carries no `Defines:` header; fall back to the
            # first top-level signature so hand and generated leaves both map.
            for line in open(p):
                mo = re.match(r"^([^\s:;{}()@|]+)\s*:", line)
                if mo:
                    m[mo.group(1)] = leaf
                    break
        # record FIELDS live in an indented `field` block; a bare import of the
        # record's leaf brings them into scope, so they map to that leaf.
        infield = False
        for line in open(p):
            if re.match(r"^\s+field\b", line):
                infield = True; continue
            if infield:
                mo = re.match(r"^\s+([^\s:;{}()@|]+)\s*:", line)
                if mo:
                    m.setdefault(mo.group(1), leaf)
                elif line.strip() and not line.startswith((" ", "\t")):
                    infield = False
        # data/record CONSTRUCTORS are the same case as fields, one level over:
        # `refl` is a constructor of `_≡_`, never a top-level definition, so the
        # `Defines:` header cannot name it — yet consumers write it in `using`
        # lists constantly.  A bare import of the datatype's leaf brings its
        # constructors into scope, so they map to that leaf.  Without this the
        # rewire REFUSES every consumer naming a constructor: measured on
        # Foundation.Eq, `refl` alone blocked 1371 of 1529 importers.
        indata = False
        for line in open(p):
            if re.match(r"^(data|record)\s", line):
                indata = True
                # `record R … where` may put its constructor on the `constructor` line
            elif indata and re.match(r"^\s+constructor\s+(\S+)", line):
                m.setdefault(re.match(r"^\s+constructor\s+(\S+)", line).group(1), leaf)
            elif indata and re.match(r"^\s+([^\s:;{}()@|]+)\s*:", line):
                m.setdefault(re.match(r"^\s+([^\s:;{}()@|]+)\s*:", line).group(1), leaf)
            elif line.strip() and not line.startswith((" ", "\t")):
                indata = False
    if not m:
        raise SystemExit(f"{parent}: no leaf provides a name")
    return m


def rewire(parent, m, paths, apply=True):
    """Rewrite each consumer's `open import <parent>` onto the owning leaves.

    ⚑ `apply` EXISTS BECAUSE THIS TOOL HAD NO PREVIEW MODE AT ALL.  Every other
    write tool in the family gates on `--apply`; this one wrote unconditionally
    on any invocation, and it is the widest-blast-radius member of the set (a
    single run rewrote 272 importers).  A tool with no dry run cannot be
    inspected before it acts, so the only way to learn what it would do was to
    let it do it.
    """
    P = re.escape(parent)
    every = "\n".join(f"open import {parent}.{l}" for l in sorted(set(m.values())))
    # ⚑ THE PATHS, NOT A COUNT.  This returned `touched` as an INT, so the one
    # thing every caller needs next — WHICH consumers did you just widen — was
    # computed and discarded.  `split_pipeline` must prune exactly those files
    # (the rewire errs WIDE by design, `:360-366`), and with only a count it
    # cannot: six standalone rewires left **354 consumers holding ≥5 leaves of one
    # parent** because nothing could name them.  Same class as `split_lemmas`
    # printing a count instead of `--manifest`, where reconstructing the file list
    # took five attempts and produced four wrong verdicts.
    # `len(touched)` is the old value, so every count-consuming caller still reads
    # correctly — this widens the contract without breaking it.
    touched, unmapped = [], {}

    def using(mo, path):
        # group(1) is the leading prefix: pure whitespace, or whitespace plus a
        # block-opening keyword (`where open import …`).  A keyword may be
        # emitted ONCE — repeating `where` on each leaf line would open a second
        # block — so later lines are indented to sit under the first.
        prefix = mo.group(1) or ""
        ind = prefix if not prefix.strip() else " " * len(prefix)
        # ⚑ `using (module ℚ)` names the RECORD's own module (its projections),
        # not a separate definition.  Agda writes it as the two tokens
        # `module` + `ℚ`, and a naive split puts BOTH in the name list: neither
        # is in the map, so the consumer is refused as unmapped and keeps its
        # import of the deleted parent — a surviving reference the build then
        # reports as `[FileNotFound]`.
        # A record's module lives in the same leaf as the record, so dropping
        # the keyword resolves it exactly as the bare name does (`ℚ` → `Rat`).
        # MEASURED: `Algebra/Q/Embeddings.agda:74` was the surviving reference
        # that failed the Q split; 57 `using (… module X …)` sites tree-wide.
        names = [x for x in mo.group(2).replace(";", " ").split()
                 if x and x != "module"]
        pub = " public" if mo.group(3) else ""
        tail = (mo.group(4) or "").strip()
        miss = [x for x in names if x not in m]
        if miss:
            unmapped.setdefault(path, []).extend(miss)
            return mo.group(0)
        leaves = sorted({m[x] for x in names})
        # ⚑ A TRAILING `renaming` CLAUSE IS PART OF THE STATEMENT AND WAS OUTSIDE
        # THE MATCH — the statement-span class, in the one tool whose whole job is
        # rewriting import statements.  The `using(...)` pattern ends at `$`, so
        # `open import P` / `using (…)` / `renaming (…)` on three lines matched
        # only the first two.  The `renaming` line survived VERBATIM, dangling
        # under whichever leaf statement was emitted last, and its alias bound
        # against a module that does not define the name.
        # MEASURED LIVE on the F2 rewire: `N-to-F2-Parity.agda` renames `+-assoc`
        # (owned by `PlusAssoc`) but the orphan landed under `PlusF`; the file
        # failed [NotInScope] `+F-assoc` at :65 — a use site far from its cause.
        # ⚑ AND `renaming_plan` — which computes exactly this per-name routing, is
        # selftested, and was added to this file for exactly this purpose — was
        # NEVER CALLED.  Strong machinery sitting beside the weaker path.
        # `group(5)` is the absorbed clause; `group(4)` remains a `--` comment.
        ren = (mo.group(5) or "").strip() if mo.lastindex and mo.lastindex >= 5 else ""
        per_leaf = {}
        if ren:
            rplan = renaming_plan("open import X " + ren, m)
            if rplan is None:
                # an old-name with no owning leaf: refuse rather than half-rewrite
                # (renaming_plan's own contract), so the consumer is REPORTED.
                unmapped.setdefault(path, []).extend(
                    [o for o, _ in (_rename_pairs(ren) or []) if o not in m])
                return mo.group(0)
            for leaf, old, new in rplan:
                if new is not None:
                    per_leaf.setdefault(leaf, []).append(f"{old} to {new}")
            leaves = sorted(set(leaves) | set(per_leaf))
        out = []
        for i, l in enumerate(leaves):
            stmt = (prefix if i == 0 else ind) + f"open import {parent}.{l}{pub}"
            if l in per_leaf:
                stmt += "\n" + ind + "  renaming (" + "; ".join(per_leaf[l]) + ")"
            out.append(stmt)
        return "\n".join(out) + ("   " + tail if tail else "")

    for p in paths:
        s = o = open(p).read()
        if f"import {parent}" not in s:
            continue
        # ⚑ tolerate ARBITRARY whitespace between the module name and `using`/
        # EOL (hand-aligned import blocks pad with multiple spaces) — a bare
        # single space here silently missed every padded importer.
        # ⚑ The `using (...)` may sit on a CONTINUATION LINE (indented, after the
        # module name).  Matching only single-line forms makes the BARE branch
        # below fire and ORPHAN the using-list onto whichever leaf import lands
        # last — a stale `using` that Agda reports as a warning, not an error
        # (F12).  So allow newline+indent between the module name and `using`.
        # ⚑ INDENTED imports.  An `open import <parent>` inside a `where` /
        # `private` / `module _ … where` body carries leading whitespace, and a
        # column-0 anchor cannot see it — so it survived the rewire, pointed at
        # a now-DELETED module, and had to be hand-fixed after the sweep named
        # it.  A hand fix does not survive a re-run, so capture the indent and
        # rewrite in place (re-emitting each leaf import at the SAME indent, or
        # Agda's layout rule closes the enclosing block).  Measured: the last 2
        # survivors on Substrate.Algebra.Z were both `private`-block imports.
        # ⚑ A KEYWORD, not just whitespace, may precede the import on its line:
        # `where open import M using (…)` is one line whose import starts after
        # `where`.  `^[ \t]*` cannot reach past it, so the rewrite skipped the
        # statement, the split deleted its target, and the build died
        # `[FileNotFound]`.  Capture the prefix and re-emit it on the FIRST
        # leaf import only (repeating `where` would open a second block).
        # MEASURED: `Algebra/Q/Embeddings.agda:74` (`where open import …Q using
        # (module ℚ)`); 15 such `where`-prefixed imports tree-wide.
        # ⚑ group 5 ABSORBS a trailing `renaming (…)` clause, which may sit on its
        # OWN CONTINUATION LINE.  Without it the match ended at the `using(...)`
        # and the `renaming` line survived verbatim as an ORPHAN under whichever
        # leaf was emitted last — see the routing comment in `using()`.
        s = re.sub(rf"^([ \t]*(?:(?:where|private|abstract)[ \t]+)?)open import {P}[ \t]*(?:\n[ \t]+)?[ \t]*using[ \t]*\(([^)]*)\)( public)?([ \t]*--.*)?((?:[ \t]*\n?[ \t]*renaming[ \t]*\([^)]*\))?)$",
                   lambda mo: using(mo, p), s, flags=re.M)
        # bare form: `open import P` [public] [-- comment] — must NOT be followed
        # by an indented continuation (that is the multi-line `using` above).
        # Same keyword-prefix rule as the `using` branch above: emit the keyword
        # once, indent the rest under it.
        def _bare(mo):
            pre = mo.group(1) or ""
            ind = pre if not pre.strip() else " " * len(pre)
            lines = every.split("\n")
            return "\n".join((pre if i == 0 else ind) + ln
                             for i, ln in enumerate(lines)) + (mo.group(2) or "")
        s = re.sub(rf"^([ \t]*(?:(?:where|private|abstract)[ \t]+)?)open import {P}[ \t]*( public)?([ \t]*--.*)?$(?![ \t]*\n[ \t]+\S)",
                   _bare, s, flags=re.M)
        if s != o:
            if apply:
                # ⚑ THE WRITE-SITE `_snapshot_once(p)` IS GONE, NOT MOVED (Ⓐ49).  It sat
                # under `if s != o and apply` — a guard behind BOTH the change test and
                # the decision it gates — so a run that rewrote nothing armed nothing,
                # on a tool whose DEFAULT polarity is apply.  Entry-bound now.
                open(p, "w").write(s)
            touched.append(p)
    return touched, unmapped


def _selftest():
    """Counted from len(cases).

    ⚑ THIS MODULE HAD A `--selftest` DISPATCH AND NO `_selftest`.  I wired the flag
    when adding `renaming_plan` and never wrote the function, so any invocation of
    the documented flag crashed with `NameError`.  `run_selftests` did not catch it:
    it DISCOVERS modules that DEFINE `_selftest`, so a module with only the CALL is
    invisible — the same "population only discovers what opted in" gap that hid
    `rename_at_source`'s live bug.
    """
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ── _split_defines: the `Defines:` list is comma-separated AND a bracket
    # mixfix name CONTAINS a comma (measured: the Foundation.Sum split reported 5
    # UNMAPPED files, all for `[_,_]`).
    check("_split_defines: plain names", _split_defines("a, b, c"), ["a", "b", "c"])
    check("_split_defines: a bracket mixfix keeps its comma",
          _split_defines("[_,_], x"), ["[_,_]", "x"])

    # ── renaming_plan: routes through the SHARED parser (scope_fix._rename_pairs);
    # this tool had never adopted it and skipped `renaming` entirely.
    m = {"a": "LeafA", "b": "LeafB"}
    check("renaming_plan: maps each old-name to its owning leaf",
          renaming_plan("open import M renaming (a to x; b to y)", m),
          [("LeafA", "a", "x"), ("LeafB", "b", "y")])
    check("renaming_plan: a rename-to-SELF needs no alias (bare import)",
          renaming_plan("open import M renaming (a to a)", m), [("LeafA", "a", None)])
    check("renaming_plan: an UNMAPPED old-name refuses the whole statement",
          renaming_plan("open import M renaming (zz to q)", m), None)
    check("renaming_plan: no renaming clause -> None",
          renaming_plan("open import M using (a)", m), None)

    # ⚑ END-TO-END THROUGH `rewire`, because the defect was NOT in `renaming_plan`
    # — that function was correct, selftested, and NEVER CALLED.  Every case above
    # passes against the shipped bug, which is precisely how it survived: the
    # `using(...)` pattern ended at `$`, so a `renaming` clause on its own
    # CONTINUATION LINE fell outside the match and survived verbatim, dangling
    # under whichever leaf statement was emitted last.
    # MEASURED LIVE: `N-to-F2-Parity.agda` renames `+-assoc` (owned by `PlusAssoc`)
    # and the orphan landed under `PlusF` → [NotInScope] `+F-assoc` at :65.
    # The fixture uses the THREE-LINE shape on purpose; a single-line `renaming`
    # would go green against the broken pattern and prove nothing.
    import tempfile, shutil
    d = tempfile.mkdtemp()
    try:
        fp = os.path.join(d, "C.agda")
        # ⚑ THE RENAMED NAME MUST NOT APPEAR IN THE `using` LIST.  My first fixture
        # wrote `using (a; b) renaming (b to bb)`; `b` is in the using-list, so its
        # leaf was emitted anyway and the orphan happened to land correctly —
        # 8/8 against the BROKEN code, i.e. the case proved nothing.  The live
        # failure renamed `+-assoc`, which the `using` list did NOT name, so the
        # owning leaf was never emitted and the clause attached to a stranger.
        open(fp, "w", encoding="utf-8").write(
            "module C where\n\nopen import M\n  using (a)\n"
            "  renaming (b to bb)\n\nfoo = bb\n")
        rewire("M", m, [fp], apply=True)
        got = open(fp, encoding="utf-8").read()
        check("a wrapped `renaming` clause rides with the leaf that OWNS the name",
              "open import M.LeafB\n  renaming (b to bb)" in got, True)
        check("...and it is NOT left dangling under an unrelated leaf",
              "open import M.LeafA\n  renaming" in got, False)

    finally:
        shutil.rmtree(d, ignore_errors=True)

    ok = sum(1 for _, g, _, _ in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"rewire_to_leaves selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


# selftest-tenant: sandbox
# ⚑ ⟡tenant-mandatory — reaches a store via `scope_fix→scope_store→store`. SANDBOX: this tool
# rewrites Agda imports tree-wide and errs WIDE by design, so a suite that rehearsed against
# the live corpus would be the wrong-tenant failure with the widest blast radius here.
# Surfaced 2026-08-24 when a deferred `import store` two hops away was hoisted.
if __name__ == "__main__":
    import agda_imports as _ai
    print(_ai.stage_warning('rewire_to_leaves',
                            'It errs WIDE on purpose (opens every leaf) because prune_imports cuts to what is used next.',
                            'stage 4, after the split'))

    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    # ⚑⚑ INTENT IS STATED AT ENTRY, BEFORE THE `apply` DECISION BELOW (Ⓐ44).  The
    # `_snapshot_once` call is deep inside `rewire`'s per-file loop, under `if s != o
    # and apply` — so it fires only once a write is already pending, and NEVER on a run
    # this tool's DEFAULT-APPLY polarity would have written nothing on.  The default is
    # the hazard the entry guard removes: a bare invocation of this tool rewrites the
    # tree, and `apply = "--dry-run" not in sys.argv` reads that silence as consent.
    # Placed AFTER the `--selftest` exit on purpose: a selftest exits before dispatch, so
    # a guard ahead of it would refuse the one invocation that asks the tool to check
    # itself (`require_at_entry` carries that carve-out; it is not repeated here).
    # ⚑⚑⚑ SNAPSHOT BOUND TO THE INTENT STATEMENT (Ⓐ49 ⟡split-8-unprotected), with
    # `paths=` so the UNTRACKED half is reached.  `snapshot()` covers TRACKED content
    # whole-worktree, but `_copy_untracked(paths)` is the ONLY reach to untracked files,
    # and it iterates `paths` — an empty tuple copies none.  That matters most HERE: this
    # tool rewrites across the whole Substrate glob, and a freshly-split sibling module is
    # exactly the untracked file with no other recovery point.
    # ⚑ THE GLOB IS HOISTED ABOVE THE GUARD rather than passing argv: `parents` holds
    # MODULE names, not paths, so `_copy_untracked` would `os.path.isfile`-miss every one
    # and silently copy nothing while still printing "snapshot taken".
    import edit_snapshot as _es
    files = glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)
    _es.require_at_entry("rewire_to_leaves", paths=files)
    # ⚑ DEFAULT IS APPLY, deliberately, and NOT changed here: this tool is
    # invoked by `split_pipeline` mid-chain, where a silent no-op would leave a
    # split half-finished and the build failing far from the cause.  What was
    # missing is the ability to LOOK first, so `--dry-run` is added rather than
    # inverting the polarity of a driver-called step.  (prune_imports went the
    # other way — it is human-invoked and was the lone `--apply` outlier.)
    apply = "--dry-run" not in sys.argv
    parents = [a for a in sys.argv[1:] if not a.startswith("-")]
    # ⚑ `files` was globbed ABOVE, at the entry call, because the snapshot needs the
    # population.  Re-globbing here would be a second read of the tree that can drift.
    for parent in parents:
        # ⚑⚑ NORMALISE ONCE, AT THE TOP OF THE LOOP — AND MY FIRST FIX DID NOT.
        # I repaired the path-vs-module confusion inside `leaf_map` and left the IDENTICAL
        # expression here at what was `:475`, so the directory resolved for the leaf scan and
        # not for anything downstream: `leaves` was built from `agda/agda/…/X/agda`, matched no
        # file, every leaf stayed in `outside`, and `rewire` was handed a `parent` still
        # spelled as a path. Result: "16 names / 12 leaves -> WOULD rewire 0 importer(s)" —
        # leaves FOUND, importers FOUND, none matched, and no error anywhere.
        #
        # ⚑ A HALF-FIXED TWO-SPELLING DEFECT IS WORSE THAN THE ORIGINAL. Before, it refused
        # loudly with a nonsense path in the message. After, it reported a clean zero — which
        # reads as "nothing to do" and would have closed the item. The peer's report named the
        # symptom I then half-cured; the zero is what a reader banks.
        parent = _parent_module(parent)
        m = leaf_map(parent)
        d = os.path.join(AG, parent.replace(".", "/"))
        # Exclude the LEAVES (a leaf importing the parent it was split from is
        # the self-import), NOT the whole directory.  A parent whose namespace
        # already held siblings — `Algebra/Z.agda` beside 37 modules under
        # `Algebra/Z/` — leaves those pre-existing consumers un-rewired, and
        # they surface as "surviving reference(s)" the column-0 sweep then
        # blames on nesting.  Measured: 37 of 39 survivors were plain
        # top-level `open import`s that simply sat inside the leaf dir.
        leaves = {os.path.join(d, l + ".agda") for l in set(m.values())}
        outside = [p for p in files if p not in leaves]
        hit, miss = rewire(parent, m, outside, apply)
        print(f"{parent}: {len(m)} names / {len(set(m.values()))} leaves "
              f"-> {'rewired' if apply else 'WOULD rewire'} {len(hit)} importer(s)"
              + ("" if apply else "   (dry run)"))
        # ⚑ `--manifest` FOR THE SAME REASON `split_lemmas` HAS ONE: the widened
        # consumers are the NEXT stage's population (prune), and a count cannot be
        # handed to it.  Reconstructing this list from `git status` / mtimes is
        # what produced four wrong verdicts during R9-VERIFY.
        if "--manifest" in sys.argv:
            for p in hit:
                print(p)
        for p, names in miss.items():
            print(f"   ⚠ UNMAPPED in {p}: {names}")
