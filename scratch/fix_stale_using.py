#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Repair `using (...)` lists naming names a module no longer exports.

Post-split, a monolith's names live in sibling leaves.  A consumer's
`using` list still names them; Agda reports -W[no]ModuleDoesntExport and
the name silently fails to bind there (it usually binds via a sibling
bare import, which is why the tree stays green).

Fix, per the ban (bare Substrate imports only): drop the un-exported
names from the `using` list, and add a BARE import of each name's owning
leaf.  Owner is found by scanning for a column-0 declaration in the
module's own directory and its leaf directory.

    python3 scratch/fix_stale_using.py <build.log | _build-dir> [--apply]

⚑ PREFER the per-file logs: `gen_build_makefiles.py` makes every module write
its own `<mod>.agdai.log`.  A `make -j` CONSOLE log interleaves jobs and will
corrupt this parse (a warning block absorbs another job's lines); the per-file
logs are interleave-proof by construction.  Point this at `agda/_build`.
"""
import re, sys, os, glob
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import importable as _importable  # THE self-import predicate (never re-derive)
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive

AG = "agda"

_SNAPPED = []


def _snapshot_once(path):
    """Arm `edit_snapshot` on the first write of a run; a no-op thereafter."""
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        edit_snapshot.guard("fix_stale_using", [path])
    except Exception as e:                      # never block the repair on the guard
        print(f"   ⚠ snapshot unavailable ({e}) — recover via git if needed")


def sites(log):
    """(file, line, module, [names]) from -W[no]ModuleDoesntExport blocks.

    `log` is a single log file, or a directory of per-module `*.agdai.log`
    (preferred: one job per file, so blocks cannot interleave)."""
    if os.path.isdir(log):
        out = []
        for p in sorted(glob.glob(f"{log}/**/*.agdai.log", recursive=True)):
            out += sites(p)
        return _dedupe(out)
    txt = open(log, errors="replace").read().split("\n")
    logpath = log
    out, i, stale = [], 0, []
    hdr = re.compile(r"^(/\S+\.agda):(\d+)\.[\d.-]+: warning: -W\[no\]ModuleDoesntExport")
    while i < len(txt):
        m = hdr.match(txt[i])
        if not m:
            i += 1; continue
        f, ln = m.group(1), int(m.group(2))
        # "The module <M>\ndoesn't export the following:" (M may wrap).
        # ⚑ A `make -j` log INTERLEAVES blocks between jobs, so bail out of a
        # block the moment a foreign line appears rather than swallowing it.
        def foreign(s):
            return (s.startswith("/") or s.lstrip().startswith(("Checking", "membudget"))
                    or "warning:" in s or "error:" in s)
        j, mod = i + 1, ""
        while (j < len(txt) and "doesn't export" not in txt[j]
               and j - i <= 3 and not foreign(txt[j])):
            mod += txt[j].strip() + " "; j += 1
        if j >= len(txt) or "doesn't export" not in txt[j]:
            i += 1; continue
        mod += txt[j].split("doesn't export")[0]
        mod = mod.replace("The module", "").strip()
        j += 1
        while j < len(txt) and txt[j].strip() in ("following:", "the following:"):
            j += 1
        names = []
        while (j < len(txt) and txt[j].startswith(" ") and txt[j].strip()
               and not foreign(txt[j])
               and not txt[j].lstrip().startswith("when scope")):
            ln_ = re.sub(r"\(did you mean.*", "", txt[j])
            # ⚑ THE HINT WRAPS.  `(did you mean 'X' or 'y'?)` may continue onto
            # the NEXT log line, where the opening paren is long gone — so the
            # sub above strips nothing and `'X'`, `or`, `'y'?)` enter `names` as
            # if they were exported names.  MEASURED at
            # Category/UniversalProperty/Phase1.agda:70, which yielded
            # ["'L0-Source'", 'or', "'on-source'?)", …] and 6 downstream
            # `no owner found` warnings.  Benign there only because junk never
            # matches a real `using` entry — one log-format shift from dropping
            # a live name.  An Agda name is never quoted and never ends in `?)`;
            # reject the hint's debris explicitly rather than hoping.
            toks = [x for x in ln_.split() if x]
            toks = [x for x in toks
                    if not x.startswith(("'", '"'))
                    and not x.endswith(("?)", "?", ")"))
                    and x not in ("or", "did", "mean", "you")]
            names += toks
            j += 1
        if mod.startswith("Substrate.") and " " not in mod and names:  # noqa: E501
            # ⚑ REFUSE A STALE COORDINATE — A STANDALONE-INVOCATION GUARD.
            # ⚑⚑ CONTEXT THAT CHANGES WHAT THIS IS (user, 2026-08-01): *"the
            # pipeline tools aren't MEANT to be run independently."*  Inside
            # `split_pipeline` this module is the LAST stage, run AFTER the
            # build (`split_pipeline.py:486-498`), so its logs are fresh BY
            # CONSTRUCTION and staleness cannot arise; the pipeline calls only
            # `sites()` to report, then `die()`s with the repair command.  The
            # risk lives entirely in the hand-run repair path — which is the one
            # a human reaches for when the pipeline tells them to.  So the guard
            # is not a correction to the design; it makes the STANDALONE path
            # safe to reach for, which the pipeline's own die() message invites.  This tool edits the source at a LINE
            # NUMBER the log reported; if the source has been touched since the
            # log was written, that line number describes a file that no longer
            # exists.  `stmt_span` searches ±3 lines, so a small drift does not
            # fail loudly — it lands on a DIFFERENT import of the same module and
            # rewrites it from the stale name list, deleting `using` entries that
            # are now live.  MEASURED on the mid-decomposition tree: the great
            # majority of sources have no usable log at all, and the arc rewrote
            # ~7000 imports after these logs were written.
            try:
                if os.path.getmtime(f) > os.path.getmtime(logpath):
                    stale.append((f, ln, mod))
                    i = j
                    continue
            except OSError:
                pass
            out.append((f, ln, mod, names))
        i = j
    return _dedupe(out)

def _dedupe(out):
    seen, uniq = set(), []
    for s in out:
        k = (s[0], s[1], s[2])
        if k in seen: continue
        seen.add(k); uniq.append(s)
    return uniq

_INDEX = None
def _index():
    global _INDEX
    if _INDEX is None:
        _INDEX = [(p, open(p, errors="replace").read())
                  for p in glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)]
    return _INDEX

_DEFIDX = None
def _def_index():
    """THE name -> {exporting module} authority (`agda_defs.def_index`), cached.

    Cached because `owner()` is called once per dropped name and `def_index`
    walks the whole tree; the previous glob was re-globbing per call anyway, so
    this is strictly cheaper as well as strictly more correct.
    """
    global _DEFIDX
    if _DEFIDX is None:
        import agda_defs
        _DEFIDX = agda_defs.def_index()
    return _DEFIDX

_IMPS = None
def _imports(mod):
    """Direct `open import` targets of a module (cached, whole tree)."""
    global _IMPS
    if _IMPS is None:
        _IMPS = {}
        for p, src in _index():
            m = module_path(p, AG)
            _IMPS[m] = set(re.findall(r"^\s*(?:open\s+)?import\s+(Substrate[\w.-]+)",
                                      src, re.M))
    return _IMPS.get(mod, set())

def _would_cycle(owner, self_mod):
    """True if `owner` transitively imports `self_mod` (adding it would cycle)."""
    if not self_mod:
        return False
    seen, stack = set(), [owner]
    while stack:
        m = stack.pop()
        if m == self_mod:
            return True
        if m in seen:
            continue
        seen.add(m)
        stack.extend(_imports(m))
    return False

def _near(cands, mod):
    """Pick the candidate module sharing the longest dotted prefix with mod."""
    def score(m):
        a, b = m.split("."), mod.split(".")
        n = 0
        while n < min(len(a), len(b)) and a[n] == b[n]: n += 1
        return (n, -len(a))
    return max(cands, key=score)

def owner(name, mod):
    """Module EXPORTING `name`, resolved through `agda_defs.def_index`.

    ⚑ THIS WAS A GLOB WITH AN INDENT-TOLERANT REGEX, AND IT EMITTED IMPORTS OF
    MODULES THAT DO NOT EXPORT THE NAME.  The history is worth keeping because
    the second defect was introduced BY the fix for the first:

      * originally `^` with no whitespace allowance — column-0 only — so an
        indented `data`/`record` head and every record FIELD were invisible
        (7 `no owner found for refl` warnings; `refl` is a constructor of an
        indented `data _≡_`).  Real gap, correctly identified.
      * the repair widened the anchor to `^\\s*` — which cannot distinguish
        *indented because nested in a record/data block* (EXPORTED) from
        *indented because local to a `where`/`private` block* (NOT exported).

    MEASURED WITNESS: `Algebra/Semiring/SPPFUP.agda` needs `_⊕_` from
    `Semiring/NatInf.agda:88` (column 0).  `owner()` returned
    `Semiring.Contraction`, where `_⊕_` is declared at 4-space indent INSIDE a
    local block (`Contraction.agda:39-41`) — `def_index` does not list
    `Contraction` among the name's 9 homes at all.  Tree-wide: **39 sites where
    the glob named a module `def_index` does not record as a home.**

    `agda_defs.def_index` already answers exactly this question and gets BOTH
    halves right — verified: it resolves `refl`, `head~`, `fzero` (the indented
    cases the widening was for) AND excludes `Contraction` (the local-block
    false positive).  A regex over raw text cannot separate those two; a scanner
    that tracks block structure can.  Route through the authority.

    `_near` survives only as a TIEBREAK among genuine homes — 565 of 3378
    using-list names are multi-homed, so a tiebreak is still needed; what it must
    never do is choose among candidates that are not homes at all.
    """
    homes = _def_index().get(name)
    if not homes:
        return None
    if len(homes) == 1:
        return next(iter(homes))
    # Prefer a home the consumer can actually reach, then dotted-prefix proximity.
    # (Proximity alone is a guess; it is the last resort, not the first.)
    return _near(sorted(homes), mod)

def stmt_span(lines, start, mod):
    """Span of the import statement for `mod` at/near line `start` (0-based)."""
    pat = re.compile(rf"^\s*(?:open\s+)?import\s+{re.escape(mod)}(?![\w.])")
    for i in range(max(0, start - 3), min(len(lines), start + 3)):
        if pat.match(lines[i]):
            # A continuation is an indented line that is NOT itself a new
            # statement.  Inside a nested `module M where`, the FOLLOWING
            # import is indented too, so a bare startswith-space test swallows
            # it and the rewrite DELETES a valid, unrelated import.  Measured:
            # Discipline.agda's `module Demo where` had three imports; fixing
            # a stale name in the first deleted all three, and the build
            # reported [NotInScope] F2³-Puncturing-Cocycle for the second.
            # Indentation alone cannot delimit a statement — stop at any line
            # that opens a new one.
            NEXT = re.compile(r"\s*(?:open\s+import|import|open|module|private|"
                              r"postulate|infix|infixl|infixr|record|data|\{-#)\b")
            j = i + 1
            while (j < len(lines) and lines[j].startswith((" ", "\t"))
                   and lines[j].strip() and not NEXT.match(lines[j])):
                j += 1
            return i, j
    return None

def fix(path, ln, mod, names, apply):
    # the importing file's OWN module — an owner equal to it is a self-import
    # (Agda: CyclicModuleDependency).  Owner search can land here when the name
    # is ALSO declared locally, so guard explicitly.
    i_ag = path.find("/" + AG + "/")
    self_mod = (path[i_ag + len(AG) + 2:-5].replace("/", ".") if i_ag >= 0 else "")
    lines = open(path).read().split("\n")
    sp = stmt_span(lines, ln - 1, mod)
    if not sp:
        print(f"   ⚠ no import statement for {mod} near {path}:{ln}"); return 0
    i, j = sp
    body = "\n".join(lines[i:j])
    m = re.search(r"using\s*\(([^)]*)\)", body, re.S)
    if not m:
        print(f"   ⚠ no using-list at {path}:{ln}"); return 0
    have = [x for x in re.split(r"[;\s]+", m.group(1)) if x]
    keep = [x for x in have if x not in names]
    owners = []
    for n in names:
        o = owner(n, mod)
        if o and (o == self_mod or self_mod.startswith(o + ".")
                  or _would_cycle(o, self_mod)):
            print(f"   ⚠ owner for {n} ({o}) would CYCLE back to {self_mod} — skipped")
            o = None
        if o and o not in owners and o != mod:
            owners.append(o)
        elif not o:
            # ⚑ `None` HAS TWO MEANINGS AND ONLY ONE IS A PROBLEM.  `def_index`
            # indexes `agda/Substrate/` only, so a name owned by `Agda.Primitive`
            # or the stdlib resolves to None and is NOT an unknown name.
            # MEASURED over all 16457 using-names: 918 resolve to None, and the
            # head is `[]` (450), `Level` (192), `_⊔_` (91) — non-Substrate
            # names, correctly outside the index.  Dropping one of those from a
            # `using` list and emitting no replacement is a real break, so say
            # WHICH case this is rather than warning identically for both.
            where = ("not a Substrate name (Agda.Primitive/stdlib?) — the "
                     "`using` entry is left ALONE"
                     if "." not in n and not _def_index().get(n)
                     else "no Substrate module exports it")
            print(f"   ⚠ no owner for {n}: {where}")
            keep.append(n)   # never drop a name we could not re-home
    # ⚑ WE DO NOT RETAIN `public`.  A `public` on an IMPORT makes this module
    # export names it does not define — the conduit P2/F23 exist to remove, and
    # a split MULTIPLIES it (the parent's prelude is copied into every leaf).
    # So the repair NEVER re-emits `public`: it binds the owner bare, and any
    # consumer that was reaching a name THROUGH this module must be rewired to
    # bind at the owner too (that rewire is the P3 contagion, not a reason to
    # keep the conduit alive).
    # ⚑ AND THAT REWIRE IS A PIPELINE STAGE, NOT AN EXERCISE FOR THE READER.
    # A risk audit read "drops `public`" as an unrecoverable export-surface
    # change; that is true STANDALONE and false in the pipeline, where
    # `rewire_to_leaves` re-binds the consumers immediately after.  Judging a
    # pipeline stage by what it does alone is judging it against a usage it was
    # never designed for — the same error as scoring decomposition on whether it
    # moved the renaming census.
    # MEASURED: V4-Normality's `open import …S4-Iso using (V₄-normal-compositional)
    # public` was a DEAD conduit — the module also imported S4-Iso.V4Normal bare
    # for its own body, its sole consumer (Subgroup) wants the locally-DEFINED
    # `V₄-normal`, and deleting the statement outright left both isolate-clean.
    # An earlier cut of this code preserved the flag and merely re-pointed it at
    # the owning leaf; that is a correct conduit, which is still a conduit.
    pub = ""

    # Drop owners the file ALREADY imports.  A parameterized module imported
    # twice is APPLIED twice and elaborated twice, so a duplicate import is a
    # real cap cost, not cosmetic.  Scan every line except the statement we are
    # about to replace (a bare `open import O` anywhere counts as having it).
    others = lines[:i] + lines[j:]
    already = {m2.group(1) for m2 in
               (re.match(r"\s*open\s+import\s+(\S+)", l) for l in others) if m2}
    dropped = [o for o in owners if o in already]
    owners = [o for o in owners if o not in already]
    for o in dropped:
        print(f"   · {o} already imported{pub} — not re-emitted")

    ind = re.match(r"\s*", lines[i]).group(0)
    # ⚑ DO NOT EMIT A HEAD THAT CARRIES NOTHING.  If every name was dropped
    # (`keep` empty) then this statement's only remaining content is the module
    # itself — and when it is `public`, keeping it re-exports a module that no
    # longer provides the name the re-export existed for: exactly the conduit
    # F23/P2 remove.  Keep the head only when it still carries names, or when
    # it is the sole surviving import (dropping it too would lose the module).
    new = []
    if keep:
        new.append(head_line := f"{ind}open import {mod}{pub}"
                   + f"\n{ind}  using ({'; '.join(keep)})")
    elif not owners and not dropped:
        new.append(f"{ind}open import {mod}{pub}")
    new += [f"{ind}open import {o}{pub}" for o in owners]
    if not new:                       # every name re-homed elsewhere ⇒ drop it
        new = []
    if apply:
        # ⚑ SNAPSHOT BEFORE THE FIRST WRITE.  This tool DELETES WHOLE IMPORT
        # STATEMENTS (`new = []` above when every name is re-homed) and drops
        # `public` re-exports — the least recoverable edit shape in the family —
        # and it was the ONLY write tool with no snapshot (`rename_at_source:102`
        # has had one).  Idempotent per run: `guard` is a no-op once armed.
        _snapshot_once(path)
        lines[i:j] = "\n".join(new).split("\n")
        open(path, "w").write("\n".join(lines))
    print(f"   {path[len(AG)+1:]}:{ln} {mod} -{len(names)} name(s) → {len(owners)} leaf import(s)")
    return 1

def check_cycles():
    """Standing guard: report every import that transitively imports its importer.

    A leaf that imports its own barrel parent (which imports its leaves) is the
    recurring shape; any codemod that resolves a name to an owner can introduce
    one, and Agda only reports it when that module is next typechecked."""
    bad = []
    for p, src in _index():
        self_mod = module_path(p, AG)
        for i, l in enumerate(src.split("\n")):
            m = re.match(r"\s*(?:open\s+)?import\s+(Substrate[\w.-]+)\s*$", l)
            if m and m.group(1) != self_mod and _would_cycle(m.group(1), self_mod):
                bad.append((p, i + 1, m.group(1), self_mod))
    for p, i, o, sm in bad:
        print(f"CYCLE {p}:{i}  {o} -> {sm}")
    print(f"{len(bad)} cycle edge(s)")
    return 1 if bad else 0

def _selftest():
    """Counted from len(cases) — a hardcoded total once hid an added case.

    ⚑ THIS TOOL HAD NO SELFTEST, AND THAT IS PART OF WHY R1 SHIPPED.  It is a
    WRITE-PATH tool: it rewrites `using` lists and emits replacement imports.
    `run_selftests` DISCOVERS modules that define `_selftest`, so a tool with
    none is invisible rather than failing — the same gap that let
    `rename_at_source` ship a live two-spelling bug through a green suite.

    These cases drive `owner()` against the LIVE tree, because the defect was
    exactly a disagreement between this resolver and `agda_defs.def_index`; a
    fixture with an invented module name cannot express that.
    """
    cases = []
    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ⚑ THE R1 WITNESS.  `_⊕_` is declared at 4-space indent inside a LOCAL block
    # in `Semiring/Contraction.agda:39-41` and at column 0 in `Semiring/NatInf.agda:88`.
    # The glob resolver matched the indented one and emitted `open import
    # …Contraction` — a module that does not export the name.  `def_index` does
    # not list Contraction among the 9 homes at all.
    check("R1: a module-LOCAL indented def is NOT the owner",
          owner("_⊕_", "Substrate.Algebra.Semiring.SPPFUP"),
          "Substrate.Algebra.Semiring.NatInf")

    # ⚑ AND THE CASE THE BROKEN WIDENING WAS ADDED FOR MUST STILL PASS — the
    # first repair was correct about a real gap (`refl` is a constructor of an
    # INDENTED `data _≡_`; column-0-only matching missed it and produced 7 `no
    # owner found` warnings). A fix that re-broke this would be the same
    # correction oscillating, not converging.
    check("the indented-CONSTRUCTOR case still resolves",
          owner("refl", "Substrate.Algebra.Semiring.SPPFUP"),
          "Substrate.Foundation.Eq")
    check("the record-FIELD case still resolves",
          owner("head~", "Substrate.Algebra.R.Trace.Bisim.Op"),
          "Substrate.Algebra.R.Trace.Bisim.Op")

    # A name no Substrate module exports must return None, never a guess — the
    # caller keeps such a name in the `using` list rather than dropping it.
    check("an unknown name resolves to None, not a near-miss",
          owner("zzz-definitely-not-a-name", "Substrate.Algebra.Semiring.SPPFUP"),
          None)

    ok = sum(1 for _, g, _, _ in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"fix_stale_using selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    import agda_imports as _ai
    print(_ai.stage_warning('fix_stale_using',
                            'It DELETES `public` conduits because rewire_to_leaves re-binds the consumers next, and reads BUILD LOGS that the pipeline guarantees are fresh.',
                            'stage 11, after the build'))

    if "--check-cycles" in sys.argv:
        sys.exit(check_cycles())
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    # ⚑ THE TARGETS ARE NOT ARGV HERE — argv[0] is a LOG (or a log DIRECTORY) and
    # the files this rewrites are whatever `sites()` resolves out of it.  So the
    # sites are computed FIRST and their paths handed to the snapshot, because a
    # snapshot keyed on argv would copy a build log and none of the sources.
    # ⚑ ONE ACT, and BEFORE `apply` is bound.  `_snapshot_once` is correct where it
    # runs but runs at the first pending write — a run whose every site is skipped
    # (`no using-list`, `no import statement`) never reaches it, and this tool
    # DELETES WHOLE IMPORT STATEMENTS, the least recoverable edit shape here.
    _sites = sorted(sites(args[0]), key=lambda s: (s[0], -s[1]))
    import edit_snapshot as _es
    _es.require_at_entry("fix_stale_using", paths=sorted({s[0] for s in _sites}))
    apply = "--apply" in sys.argv
    n = 0
    for f, ln, mod, names in _sites:
        n += fix(f, ln, mod, names, apply)
    print(f"{'applied' if apply else 'dry-run'}: {n} site(s)")
