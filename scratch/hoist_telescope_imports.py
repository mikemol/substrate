#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Hoist imports that a module's TELESCOPE needs above its module header.

THE DEFECT.  A parameterized module header

    module M (Word : Set) (_++_ : Word → Word → Word)
      (++-assoc : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
      where
    open import Substrate.Foundation.Eq        -- TOO LATE

is scope-checked BEFORE anything inside `where`.  An import below the header does
not exist yet as far as the telescope is concerned, so a name it mentions is
unbound — and if that name is an OPERATOR, its fixity is also absent from the
grammar, which surfaces as `[NoParseForApplication]` rather than `[NotInScope]`.

MEASURED LIVE: `Groups/Coxeter/Core.agda` used `≡` in `++-assoc` with
`open import Substrate.Foundation.Eq` on the LAST LINE of the file.  Substrate's
`_≡_` is `infix 4` (`Foundation/Eq.agda:17`), so with the import out of reach the
parser could not place `≡` against `++` and rejected the telescope.
`Groups/Coxeter/GroupAdapter.agda` carries the IDENTICAL unparenthesized telescope
and compiles — because its `Foundation.Eq` import sits ABOVE its header.
⚑ I first diagnosed this as "fixity does not cross the module-parameter boundary"
and filed it as a new class; that is RETRACTED (plan §30).  The mechanism is
positional, and this tool is the repeatable form of the repair.

WHY A TRANSFORM AND NOT A GATE (user, 2026-08-01: *"a gate cannot fix code. Agda
code must be fixed by codegen in order for it to be repeatable, reliable"*):
a gate reports N sites and leaves N hand-edits.  The first pass over these 11 files
WAS a hand-edit — an ad-hoc script that no longer exists, so the repair could not be
re-run, reviewed, or applied to the next file that acquires the shape.  This tool is
the artifact that survives.

NOT AN EMISSION FIX.  `split_lemmas` emits `module <Name> where` with NO telescope
(verified: 0 of the split-emitted leaves carry a top-level parameter list), so the
splitter cannot produce this shape.  Every site is HAND-WRITTEN, which is exactly
why a transform — runnable over the tree on demand — is the right home.

    hoist_telescope_imports.py <file-or-dir> ...            # report (default)
    hoist_telescope_imports.py agda --apply                 # rewrite

⚑ THIS IS A REPAIR STAGE OF THE SPLIT/TELESCOPE FAMILY, AND IT DID NOT SAY SO.
It is provoked BY a split (or any hand-written telescope) and is absent from
`split_pipeline`'s chain, so nothing routed a reader here: it has ZERO importers and
was reachable only by knowing this filename.  `toolmodes --find telescope` answered
with LIBRARY FUNCTIONS and never named this tool, which is the measured loop the
operator described — *"some of the tools got built AFTER the LLMs forgot the pipeline
existed; that kept happening."*

The family map — every sibling and the precondition that selects it:

    .claude/skills/agda-ban-decompose/telescope-family.md   (agda_imports.TELESCOPE_MAP)

⚑ THE DOCUMENT IS NOT THE MECHANISM; THE REFUSAL THAT NAMES IT IS.  `split_lemmas`'
telescoped-root decline prints that path — a document nobody is routed to loses to a
refusal by construction.  This banner is the second edge, for the reader who arrives
at the repair without having been refused first.
"""
import re, sys, os

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
import agda_lex                      # THE span / positional authority; never re-derive
import agda_defs                     # THE name -> home authority

AG = "agda"

_SNAPPED = []


def _snapshot_once(path):
    """Arm edit_snapshot on the FIRST write of a run; a no-op thereafter."""
    if _SNAPPED:
        return
    _SNAPPED.append(True)
    try:
        import edit_snapshot
        edit_snapshot.guard('hoist_telescope_imports', [path])
    except Exception as e:
        print(f"   ⚠ snapshot unavailable ({e}) — recover via git if needed")


_DEFIDX = None


def _homes(name):
    global _DEFIDX
    if _DEFIDX is None:
        _DEFIDX = agda_defs.def_index()
    return set(_DEFIDX.get(name, ()))


# Symbols worth resolving: an operator used in a telescope needs BOTH its binding
# and its fixity, and those are what the parse error is really about.  Keyed by the
# spelling that appears in source (`≡`) mapping to the indexed name (`_≡_`).
def _symbols(text):
    """Bare operator/name tokens in `text`, each paired with its `_x_` spelling."""
    out = {}
    for t in re.findall(r"[^\s(){}\[\];,]+", text):
        if not t or t in ("→", ":", "=", "∀", "where", "module"):
            continue
        out.setdefault(t, "_" + t + "_")
    return out


def needed(path):
    """[(name, home)] the telescope references but no PRECEDING import provides.

    Returns [] when the file has no telescope, when everything already resolves, or
    when a name has no single unambiguous home (reported, never guessed at).
    """
    src = open(path, encoding="utf-8", errors="replace").read()
    span = agda_lex.telescope_span(src)
    if span is None:
        return []
    start, end = span
    lines = agda_lex.mask_comments(src).split("\n")
    tel = "\n".join(lines[start:end + 1])
    # a parameter BINDS its own name; those are not imports to hoist
    bound = set()
    for grp in re.findall(r"[({]\s*([^:(){}]+?)\s*:", tel):
        bound.update(grp.split())
    have = agda_lex.imports_before(src, start)
    out = []
    for bare, mixfix in _symbols(tel).items():
        if bare in bound or mixfix in bound:
            continue
        homes = _homes(mixfix) or _homes(bare)
        if not homes or (homes & have):
            continue
        if len(homes) > 1:
            # AMBIGUOUS: refuse rather than pick.  `owner()`'s `_near` tiebreak is a
            # guess, and a wrong import here is a silent miscompile, not a warning.
            out.append((bare, None))
            continue
        out.append((bare, next(iter(homes))))
    return out


def hoist(path, apply=False):
    """Insert the missing imports above the header. Returns (added, ambiguous)."""
    want = needed(path)
    amb = [n for n, h in want if h is None]
    mods = sorted({h for _n, h in want if h})
    if not mods:
        return [], amb
    src = open(path, encoding="utf-8", errors="replace").read()
    start, _end = agda_lex.telescope_span(src)
    raw = src.split("\n")
    note = [
        "-- ⛑ A NAME USED IN THE TELESCOPE MUST BE IMPORTED ABOVE THE HEADER.",
        "-- The parameter list is scope-checked before anything inside `where`, so an",
        "-- import below the header is too late; for an OPERATOR its fixity is missing",
        "-- from the grammar too, which surfaces as [NoParseForApplication].",
    ]
    ins = note + [f"open import {m}" for m in mods] + [""]
    out = raw[:start] + ins + raw[start:]
    if apply:
        _snapshot_once(path)
        open(path, "w", encoding="utf-8").write("\n".join(out))
    return mods, amb


def _selftest():
    """Counted from len(cases).

    Cases run against the LIVE tree: the defect is a disagreement between a
    positional predicate and the typechecker, which a fixture with an invented
    module name cannot express (five such fixtures failed to reproduce it — §30).
    """
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ⚑ `telescope_span` must return None for a plain `module X where` — every
    # split-emitted leaf has that shape, and reporting one would be a false
    # positive in a population the splitter cannot fix.
    check("a where-terminated header has NO telescope",
          agda_lex.telescope_span("{-# OPTIONS #-}\nmodule M where\nfoo = 1\n"), None)

    # ⚑ A multi-line telescope spans to its `where`, paren-depth aware.
    src = ("module M (W : Set)\n"
           "  (_++_ : W → W → W)\n"
           "  where\n"
           "open import X\n")
    check("a wrapped telescope spans header..where", agda_lex.telescope_span(src), (0, 2))

    # ⚑ THE POSITIONAL POINT: an import BELOW the header is not `imports_before`.
    check("an import below the header is not available to the telescope",
          "X" in agda_lex.imports_before(src, 0), False)

    # ⚑ …and one above it is.
    src2 = "open import X\n" + src
    check("an import above the header IS available",
          "X" in agda_lex.imports_before(src2, 1), True)

    # ⚑ A parameter BINDS its own name — `_++_` above must not be reported as a
    # missing import, or the tool would hoist an import for the very thing the
    # telescope declares.
    import tempfile, shutil
    d = tempfile.mkdtemp()
    try:
        p = os.path.join(d, "M.agda")
        open(p, "w", encoding="utf-8").write(src)
        check("a telescope-bound operator is never reported missing",
              [n for n, _h in needed(p) if n == "++"], [])
    finally:
        shutil.rmtree(d, ignore_errors=True)

    ok = sum(1 for _n, g, _got, _w in cases if g)
    for n, g, got, w in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {w!r}")
    print(f"hoist_telescope_imports selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(0 if _selftest() else 1)
    args = [a for a in sys.argv[1:] if not a.startswith("-")] or [AG]
    files = []
    for t in args:
        files.extend(agda_lex.agda_files(t) if os.path.isdir(t) else [t])
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound, and AFTER
    # the directory arguments have been EXPANDED — a bare run defaults to the whole
    # `AG` tree, so a snapshot keyed on argv would name a directory where
    # `_copy_untracked` expects files.
    # ⚑ `_snapshot_once` sits under `if apply:` inside `hoist`, so it is consulted
    # after the decision and never at all on a run where no telescope is missing an
    # import — which, on a tree-wide sweep, is the common case.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("hoist_telescope_imports", paths=sorted(files))
    apply = "--apply" in sys.argv
    hit = amb_n = 0
    for f in sorted(files):
        mods, amb = hoist(f, apply)
        if mods:
            hit += 1
            print(f"  {'hoisted' if apply else 'WOULD hoist'} {', '.join(mods)}  {f}")
        for a in amb:
            amb_n += 1
            print(f"  ⚠ {f}: `{a}` has SEVERAL homes — refusing to guess; import it by hand")
    print(f"{'hoisted in' if apply else 'would hoist in'} {hit} file(s)"
          f"{f'; {amb_n} ambiguous name(s) left alone' if amb_n else ''}"
          + ("" if apply else "   (dry run — pass --apply to execute)"))
