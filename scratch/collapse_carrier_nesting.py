#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Collapse a redundant carrier nesting: Foundation/Bool/Bool.agda -> Foundation/Bool.agda.

WHY: splitting `Foundation/Bool.agda` moved `data Bool` into a leaf
`Foundation/Bool/Bool.agda`. That renames the carrier's module
(Foundation.Bool -> Foundation.Bool.Bool) and, as a side effect, relocates its
"home directory" from `Foundation/Bool/` to `Foundation/Bool/Bool/` — a
directory that does not exist. Every operator over the carrier (`_∧_`, `_∨_`,
`_xor_`) is then a SIBLING of the carrier rather than under it, and the
carrier-locality gate fails on all of them.

The nesting is redundant: `X/X.agda` says nothing `X.agda` does not, and the
parent slot is empty precisely BECAUSE the split vacated it. Collapsing
restores the carrier as the parent of its own subtree, which is what both the
ban (one definition per file) and carrier-locality (operators live with their
carrier) want — no gate is loosened, and the operators do not move.

⚑ NOT a general "flatten leaves" pass. It fires only where the leaf's basename
equals its directory's basename AND the parent slot is free; anything else is a
real module the split created, not a redundancy.

  collapse_carrier_nesting.py <Module.Path.Leaf> [--apply]
              # THE DEFAULT: collapse `X/X.agda` -> `X.agda`. The name is UNCHANGED,
              # which is why it needs no confirmation.

  collapse_carrier_nesting.py <Module.Path.Leaf> --promote [--apply]
              # `X/Leaf.agda` -> `X.agda` where leaf != directory: a PROMOTION, and
              # therefore a RENAME (`Algebra.Z.Int` -> `Algebra.Z`) that every importer
              # sees. ⚑ IT MUST BE ASKED FOR, never inferred: loosening the `X/X` guard
              # to cover this case would let the tool flatten ANY leaf into its parent,
              # which is exactly what that guard prevents. Right when the split vacated
              # the parent slot and the leaf holds the carrier the directory is named for.

  collapse_carrier_nesting.py <Module> --to <Dest.Module> [--apply]
              # RELOCATE to an explicitly-NAMED destination, rewriting every reference.
              # Collapse and promote DERIVE their target from the path; this is for
              # re-homing an operator under its carrier when no nesting relationship
              # exists between the two. ⚑ Check the dependency direction first: moving a
              # module INTO Foundation is sound only if it imports nothing above
              # Foundation, or the move introduces an upward edge and the layering inverts.

  collapse_carrier_nesting.py <Module> --rewrite-refs-to <Dest.Module> [--apply]
              # REPAIR-ONLY: repoint references without moving anything, for a rename
              # whose file-move already landed but whose references were reverted. It
              # REFUSES if <Module> still exists on disk (that is a live module — use
              # `--to`) or if <Dest.Module> does not.

  collapse_carrier_nesting.py --selftest

⚑ EVERY MODE IS DRY BY DEFAULT; `--apply` writes.
"""
import os, re, sys, subprocess
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import importable as _importable  # THE self-import predicate (never re-derive)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AG = os.path.join(ROOT, "agda")


def die(msg):
    print(f"REFUSING: {msg}", file=sys.stderr)
    sys.exit(1)


def _defines(path):
    """Top-level names a module defines (data/record/module heads + signatures),
    including operator sections so `_∧_` is found however it is written."""
    names = set()
    try:
        src = open(path).read()
    except OSError:
        return names
    # ⚑ `data`/`record` and `module` need SEPARATE flags, and the module one must
    # be gated on the head being at COLUMN 0.  With one shared flag, a NESTED
    # `module Inner where` set it and every indented `name :` for the rest of the
    # file was registered as a top-level export of the FILE — measured: 3368
    # over-claimed names across 620 files.  `rewire_using` then emits
    # `open import <sibling>` for a name that sibling does not export at top
    # level.  `agda_defs.def_index` already carries exactly this distinction
    # (in_data vs in_module, the latter gated on `not l[0].isspace()`, because a
    # col-0 `module X where` body IS exported by the repo's `open X public`
    # idiom while a nested one is not); mirror it rather than re-deriving.
    indata = False; inmodule = False
    for l in src.split("\n"):
        # ⚑ INDENTED heads count.  A `data`/`record` may sit inside a
        # parameterized `module _ (L : Set) where` (the ⟡set1-paydown idiom) —
        # `agda_defs.def_index` was fixed for exactly this (measured: Wedge.Graded
        # provided neither `GradedDivStr` nor `recon`, so prune read the import as
        # dead and dropped it).  Anchoring at column 0 loses the head AND all its
        # fields: ExpLogCodec's `expL`/`exp-⊕`/`exp-𝟘` are 6-space-indented
        # fields of an indented record.
        m = re.match(r"^\s*(?:data|record)\s+([^\s({:]+)", l)
        if m:
            names.add(m.group(1)); indata = True; inmodule = False; continue
        m = re.match(r"^(\s*)module\s+([^\s({:]+)", l)
        if m:
            if not m.group(1):                     # col-0 submodule: exported
                names.add(m.group(2)); inmodule = True; indata = False
            # ⚑ A NESTED `module` head is passed over WITHOUT clearing
            # `inmodule`: its own body sits deeper than the ≤2-space shallow
            # rule below, so it is excluded by INDENT, and clearing the flag
            # here would also lose the enclosing col-0 module's later shallow
            # definitions (measured on a nested fixture: `shallow` vanished).
            # Losing a provision is the FALSE-POSITIVE direction — it drops a
            # live import — so the flag must survive the nested head.
            continue
        m = re.match(r"^([^\s:;{}()@|]+)\s*:", l)
        if m:
            names.add(m.group(1)); indata = False; continue
        # ⚑ CONSTRUCTORS and record FIELDS are exported by the module that
        # declares their type, but they are INDENTED — a top-level-only scan
        # misses them, so `true`/`false` (constructors of `data Bool`) looked
        # like names no module owned. They fell through to "keep" by accident,
        # which is the right placement for the wrong reason: a name the scan
        # cannot see is indistinguishable from one a sibling owns, and the next
        # carrier whose constructors DID move would be mis-routed silently.
        if indata:
            mo = re.match(r"^\s+([^\s:;{}()@|]+)\s*:", l) or \
                 re.match(r"^\s+constructor\s+(\S+)", l)
            if mo:
                names.add(mo.group(1))
            elif l.strip() and not l.startswith((" ", "\t")):
                indata = False
        elif inmodule:
            # SHALLOW body only (≤2 spaces): deeper indentation is a definition's
            # own `where`-locals, which are NOT provisions (agda_defs:70-72).
            mo = re.match(r"^(\s{1,2})([^\s:;{}()@|]+)\s*:(?!:)", l)
            if mo:
                names.add(mo.group(2))
            elif l.strip() and not l.startswith((" ", "\t")):
                inmodule = False
    return names


def rewire_using(dest_mod, apply):
    """After a collapse/promote, repoint each consumer's `using (…)` names at the
    module that actually OWNS them.

    ⚑ THE DEFECT THIS CLOSES: renaming a module rewrites the PATH but not the
    name-set. `Foundation/Bool.agda` used to hold `data Bool` AND `_∧_`/`_∨_`;
    after the collapse it holds only `Bool`, and the operators live in sibling
    leaves (`Bool/And.agda`, …). A consumer's `open import Substrate.Foundation.Bool
    using (Bool; _∧_)` then names something the module no longer exports — which
    Agda reports only as a WARNING at the import, surfacing far away as a bare
    [NotInScope] at the USE site (GUnit/Base.agda:37 `_∧_`). Silent at the point
    of damage: exactly the class the ban's stale-`using` sweep exists for.

    For each consumer of `dest_mod`, split its `using` list by owner: names the
    module still defines stay; each name defined by a sibling leaf gets its own
    bare `open import <sibling>` (bare, per the ban — no `using` filter)."""
    dest_dir = os.path.join(AG, dest_mod.replace(".", "/"))
    dest_file = dest_dir + ".agda"
    own = _defines(dest_file)
    # sibling leaves that could own the displaced names
    sib = {}
    if os.path.isdir(dest_dir):
        for fn in sorted(os.listdir(dest_dir)):
            if fn.endswith(".agda"):
                leaf = dest_mod + "." + fn[:-5]
                for n in _defines(os.path.join(dest_dir, fn)):
                    sib.setdefault(n, leaf)
    pat = re.compile(r"^([ \t]*)open import " + re.escape(dest_mod) +
                     r"[ \t]*using[ \t]*\(([^)]*)\)([ \t]*public)?[ \t]*$", re.M)
    touched = []

    def fix(mo):
        ind, names, pub = mo.group(1), mo.group(2), mo.group(3) or ""
        want = [x for x in names.replace(";", " ").split() if x]
        keep = [n for n in want if n in own or n not in sib]
        move = sorted({sib[n] for n in want if n not in own and n in sib})
        out = []
        if keep or not move:
            out.append(f"{ind}open import {dest_mod}{pub}")
        out += [f"{ind}open import {m}{pub}" for m in move]
        return "\n".join(out)

    for dirpath, _d, fnames in os.walk(os.path.join(AG, "Substrate")):
        for fn in fnames:
            if not fn.endswith(".agda"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                s = open(p).read()
            except OSError:
                continue
            if dest_mod not in s:
                continue
            # ⚑ Self-import guard (agda_imports.importable): the leaf that DEFINES a
            # moved name must not be repointed at itself.  Agda hard-errors
            # [CyclicModuleDependency], which reads like a real structural cycle.
            # Measured 10× in one arc, from a sibling tool with the same shape.
            def _guarded(mo, _here=p):
                keep = []
                for l in fix(mo).split("\n"):
                    m = re.match(r"^\s*open import\s+(\S+)", l)
                    if m and not _importable(_here, m.group(1)):
                        continue          # would be a self-import; drop the line
                    keep.append(l)
                return "\n".join(keep)

            new = pat.sub(_guarded, s)
            if new != s:
                touched.append(p)
                if apply:
                    # ⚑ recoverable-by-construction: this rewrites a file it read.
                    import edit_snapshot as _es; _es.guard("collapse_carrier_nesting", [p])
                    open(p, "w").write(new)
    print(f"  using-rewire: {len(touched)} consumer(s) repointed to owning leaves")
    return touched


def rewrite_refs(mod, dest_mod, apply):
    """Rewrite every reference to module `mod` into `dest_mod`, tree-wide.

    ⚑ Factored OUT of relocate so it can run WITHOUT moving a file. A rename
    has two halves — moving the file, and repointing the references — and they
    can come apart: a revert that restores an old import line leaves the tree
    naming a module whose file has already moved (`[FileNotFound]`, far from
    the rename that caused it). Repairing that by hand re-fixes one line and
    leaves the class; running the SAME rewriter the rename used fixes every
    stale reference by construction.

    ⚑ The right boundary is load-bearing: `Foundation.Nat.Mod` must not match
    inside `Foundation.Nat.ModEquiv`.

    ⚑ COMMENTS ARE NOT REFERENCES. A module name in prose ("split out of
    Substrate.Foundation.Negation") names the module's HISTORY; rewriting it
    silently falsifies the record, and for a leaf whose comment names its own
    former parent it would make the file claim to come from itself. MEASURED:
    of 7 files matching `Foundation.Negation`, 6 were comment-only and exactly
    1 was a live import. A rewriter that edits all 7 is not more thorough — it
    is wrong in 6 places, and the 6 are invisible because prose does not fail
    to typecheck."""
    pat = re.compile(re.escape(mod) + r"(?![\w.])")
    touched = []
    for dirpath, _d, fnames in os.walk(os.path.join(AG, "Substrate")):
        for fn in fnames:
            if not fn.endswith(".agda"):
                continue
            p = os.path.join(dirpath, fn)
            try:
                s = open(p).read()
            except OSError:
                continue
            if mod not in s:
                continue
            out, changed = [], False
            for line in s.split("\n"):
                code, sep, cmt = line.partition("--")
                new_code = pat.sub(dest_mod, code)
                if new_code != code:
                    changed = True
                out.append(new_code + sep + cmt)
            if changed:
                touched.append(p)
                if apply:
                    open(p, "w").write("\n".join(out))
    return touched


def relocate(mod, dest_mod, apply):
    """Move a module to an explicitly-named new module path, rewriting every
    reference. Unlike collapse/promote (which DERIVE the target from the path),
    the destination is given — used to re-home an operator under its carrier
    when no nesting relationship exists between the two.

    ⚑ Check the dependency direction before calling: moving a module INTO
    Foundation is only sound if it imports nothing above Foundation, or the
    move introduces an upward edge and the layering inverts."""
    src = os.path.join(AG, mod.replace(".", "/") + ".agda")
    dst = os.path.join(AG, dest_mod.replace(".", "/") + ".agda")
    if not os.path.isfile(src):
        die(f"{mod} does not exist")
    if os.path.exists(dst):
        die(f"{dest_mod} already exists")
    touched = rewrite_refs(mod, dest_mod, apply)
    print(f"{mod} -> {dest_mod}   ({len(touched)} file(s) reference it)")
    if apply:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        subprocess.run(["git", "mv", src, dst], cwd=ROOT, capture_output=True)
        if not os.path.exists(dst):
            os.rename(src, dst)
        d = os.path.dirname(src)
        if os.path.isdir(d) and not os.listdir(d):
            os.rmdir(d)
        rewire_using(dest_mod, apply)
        print("  APPLIED")
    else:
        print("  (dry run — pass --apply)")
    return 0


def classify_occupied(mod, parent_mod):
    """('barrel'|'real-module', uncovered_names) when the parent slot is TAKEN.

    ⚑ THE REFUSAL MUST NAME THE ROUTE (user, 2026-08-01: *"there exists collapse
    machinery in the pipeline designed specifically to deal with things like
    that"*).  I had filed `Algebra.F2.Linear` / `.Linear.Linear` as "blocked until
    its dependency compiles" WITHOUT ASKING THIS TOOL — and when I did ask, its
    refusal told me the parent slot was occupied and nothing about what to do
    instead.  A tool that owns a shape should classify the cases it declines, from
    data already on disk; otherwise every caller re-derives the judgement by hand,
    which is how the same barrel sat in the worklist for a day mis-labelled.

    The two occupied cases want OPPOSITE moves:
      · the parent defines nothing a leaf does not  ⇒ a CONSUMED BARREL the split
        never retired.  Rewire consumers to the leaves, then delete it (R2).
      · the parent still owns names of its own      ⇒ a REAL MODULE sharing a
        directory.  Nothing to collapse; a shared name is a genuine collision.
    """
    src = os.path.join(AG, mod.replace(".", "/") + ".agda")
    dst = os.path.join(AG, parent_mod.replace(".", "/") + ".agda")
    # ⚑ A MODULE'S OWN HEADER IS NOT A NAME IT DEFINES.  `_defines` collects
    # `module X where` heads (it must — the repo's `open X public` idiom makes a
    # col-0 inner module a real export), and that includes the FILE's own header.
    # MEASURED: `F2/Linear.agda` first reported 1 uncovered name and it was
    # `Substrate.Algebra.F2.Linear` — itself.  Left in, EVERY barrel shows one
    # uncovered name and classifies as "a real module": the barrel branch would be
    # UNREACHABLE, and a guard whose positive case cannot fire is decoration.
    own_parent = _defines(dst) - {parent_mod}
    uncovered = own_parent - (_defines(src) - {mod})
    sibdir = os.path.join(AG, parent_mod.replace(".", "/"))
    if os.path.isdir(sibdir):
        for fn in sorted(os.listdir(sibdir)):
            if fn.endswith(".agda"):
                uncovered -= _defines(os.path.join(sibdir, fn))
    return ("real-module" if uncovered else "barrel"), sorted(uncovered)


def _selftest():
    """Counted from len(cases)."""
    import tempfile
    cases = []

    def check(n, got, want):
        cases.append((n, got == want, got, want))

    global AG
    _ag = AG
    d = tempfile.mkdtemp()
    try:
        AG = d
        base = os.path.join(d, "Substrate", "Pkg")
        os.makedirs(os.path.join(base, "Thing"))

        def w(rel, body):
            open(os.path.join(base, rel), "w", encoding="utf-8").write(body)

        # a CONSUMED BARREL: the parent's names all live in leaves
        w("Thing.agda", "module Substrate.Pkg.Thing where\nfoo : Set\nbar : Set\n")
        w(os.path.join("Thing", "Thing.agda"),
          "module Substrate.Pkg.Thing.Thing where\nfoo : Set\n")
        w(os.path.join("Thing", "Bar.agda"),
          "module Substrate.Pkg.Thing.Bar where\nbar : Set\n")
        kind, unc = classify_occupied("Substrate.Pkg.Thing.Thing",
                                      "Substrate.Pkg.Thing")
        check("a fully-covered parent is a CONSUMED BARREL", kind, "barrel")
        # ⚑ THE HEADER CASE, PINNED.  Before the `- {parent_mod}` fix this returned
        # ['Substrate.Pkg.Thing'] — the module's OWN name — so every barrel read as
        # a real module and the barrel branch could never fire.
        check("...and its own module header is not an uncovered name", unc, [])

        # a REAL MODULE: the parent still owns something no leaf provides
        w("Thing.agda",
          "module Substrate.Pkg.Thing where\nfoo : Set\nbar : Set\nonly-here : Set\n")
        kind2, unc2 = classify_occupied("Substrate.Pkg.Thing.Thing",
                                        "Substrate.Pkg.Thing")
        check("a parent owning an uncovered name is a REAL MODULE",
              (kind2, unc2), ("real-module", ["only-here"]))
    finally:
        AG = _ag

    ok = sum(1 for _n, g, _a, _b in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"collapse_carrier_nesting selftest: {ok}/{len(cases)}")
    return ok == len(cases)


def main(argv):
    if "--selftest" in argv:
        return 0 if _selftest() else 1
    if len(argv) < 2:
        die("usage: collapse_carrier_nesting.py <Module> [--promote|--to <Dest>] [--apply]")
    mod = argv[1]
    # ⚑ ONE ACT: state the intent AND snapshot, BEFORE `apply` is bound.  The
    # `guard` this supersedes sat inside the using-rewire loop under `if apply:`,
    # and `rewrite_refs`/`relocate` wrote with NO guard at all — a tool the
    # `snapshot-guard` census scores as ARMED because it mentions `edit_snapshot`
    # in one of its four write paths.
    # ⚑ `paths=` IS THE MODULE'S OWN FILE, NOT THE REFERENCE SET.  This tool
    # rewrites references TREE-WIDE (`rewrite_refs` walks all of agda/Substrate),
    # which is not enumerable before the walk — `snapshot()` covers that population
    # whole-worktree because it is TRACKED.  What tracked-snapshot cannot reach is
    # an UNTRACKED leaf, and the module being collapsed is the one file here that
    # can plausibly be one (a fresh split leaf), so it is what `paths` names.
    # Naming a set that is neither complete nor the untracked-reaching one would be
    # a false assurance; naming this one is the honest partial.
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import edit_snapshot as _es
    _es.require_at_entry("collapse_carrier_nesting",
                         paths=[os.path.join(AG, mod.replace(".", "/") + ".agda")])
    apply = "--apply" in argv
    if "--rewrite-refs-to" in argv:
        # Repair-only: repoint references without moving anything. For a rename
        # whose file-move already landed but whose references were reverted.
        dest = argv[argv.index("--rewrite-refs-to") + 1]
        if os.path.isfile(os.path.join(AG, mod.replace(".", "/") + ".agda")):
            die(f"{mod} still exists — this is a live module, not a stale "
                f"reference. Use --to to relocate it.")
        if not os.path.isfile(os.path.join(AG, dest.replace(".", "/") + ".agda")):
            die(f"{dest} does not exist — the destination must be the module "
                f"the references should point at.")
        t = rewrite_refs(mod, dest, apply)
        print(f"{mod} -> {dest}   ({len(t)} file(s) reference it)")
        for p in t:
            print("   ", os.path.relpath(p, AG))
        print("  APPLIED" if apply else "  (dry run — pass --apply)")
        return 0
    if "--to" in argv:
        return relocate(mod, argv[argv.index("--to") + 1], apply)
    rel = mod.replace(".", "/") + ".agda"
    src = os.path.join(AG, rel)
    if not os.path.isfile(src):
        die(f"{rel} does not exist")

    leaf = mod.rsplit(".", 1)[-1]
    parent_mod = mod.rsplit(".", 1)[0]
    parent_leaf = parent_mod.rsplit(".", 1)[-1]
    # ⚑ Two distinct operations, kept distinct on purpose:
    #   X/X.agda -> X.agda        a REDUNDANT NESTING; the name is unchanged.
    #   X/Leaf.agda -> X.agda     a PROMOTION; the module is RENAMED (Algebra.Z.Int
    #                             -> Algebra.Z), which every importer sees.
    # Promotion is the right move when the split vacated the parent slot and the
    # leaf holds the carrier the directory is named for (`data ℤ` in `Z/Int.agda`)
    # — but it is a rename, so it must be asked for explicitly rather than
    # inferred. Loosening the X/X guard to cover it would let the tool flatten
    # any leaf into its parent, which is exactly what the guard prevents.
    if leaf != parent_leaf and "--promote" not in argv:
        die(f"not a redundant nesting: leaf `{leaf}` != directory `{parent_leaf}`.\n"
            f"  This would RENAME {mod} -> {parent_mod} (every importer sees it).\n"
            f"  If that is intended (the leaf holds the carrier `{parent_leaf}` is "
            f"named for), pass --promote.")

    dst = os.path.join(AG, parent_mod.replace(".", "/") + ".agda")
    if os.path.exists(dst):
        # ⚑ THE REFUSAL MUST NAME THE ROUTE, NOT JUST THE OBSTACLE (user,
        # 2026-08-01: *"there exists collapse machinery in the pipeline designed
        # specifically to deal with things like that"* — I had recorded
        # `Algebra.F2.Linear` / `.Linear.Linear` as "blocked until its dependency
        # compiles" without asking this tool at all).  It refuses correctly, and
        # the bare refusal is still a dead end: an operator learns the parent slot
        # is occupied and nothing about WHICH operation applies instead.  So the
        # tool that owns the shape classifies it, from data already on disk.
        #
        # Two ways a parent can be occupied, and they want OPPOSITE moves:
        #   · the parent DEFINES nothing the leaf does not — a consumed BARREL the
        #     split never retired.  Route: rewire consumers to the leaves, then
        #     delete it (R2's route; `split_pipeline --rewire-only`).
        #   · the parent defines names of its OWN — a real module that happens to
        #     share a directory.  Nothing to collapse; the duplicate name is a
        #     genuine collision for `rename_at_source`.
        kind, uncovered = classify_occupied(mod, parent_mod)
        own_parent = _defines(dst) - {parent_mod}
        hint = (
            f"\n  The parent defines {len(own_parent)} name(s); "
            f"{len(uncovered)} are NOT covered by any leaf."
        )
        if kind == "barrel":
            hint += (
                f"\n  ⇒ CONSUMED BARREL — every name it defines lives in a leaf, so "
                f"this is\n     R2's route, not a collapse:\n"
                f"       python3 scratch/split_pipeline.py {parent_mod} --rewire-only --apply\n"
                f"     then delete {os.path.relpath(dst, AG)} once 0 references remain."
            )
        else:
            hint += (
                f"\n  ⇒ A REAL MODULE, not a barrel — it still owns: "
                f"{', '.join(uncovered[:6])}"
                f"{'…' if len(uncovered) > 6 else ''}\n"
                f"     Nothing to collapse.  If the shared NAME is the problem, that "
                f"is a genuine\n     collision for rename_at_source (check the provider "
                f"for a pattern synonym first)."
            )
        die(f"{os.path.relpath(dst, AG)} already exists — the parent slot is "
            f"occupied, so this is not the vacated-by-split case." + hint)

    # Every reference to the nested module becomes a reference to the parent.
    # ⚑ THIS IS `rewrite_refs`, NOT A SECOND COPY OF IT (F28, second instance).
    # This path used to re-implement the substitution inline WITHOUT the
    # comment mask, so a collapse rewrote module names in prose as well as in
    # code. MEASURED over the 19 modules carrying a splitter provenance marker:
    # 420 (module, file) pairs whose ONLY match is inside a comment; the worst
    # (ExtrudeCoEmitGraded) had 0 code references and 272 comment-only ones, so
    # the run rewrote 272 files of history and 0 lines of code while reporting
    # 272 files "referencing it".
    # ⚑ AND IT CORRUPTED THE F18 GUARD: every leaf header reads
    # `split horizontally -- out of <parent>`, which `rewire_to_leaves.leaf_map`
    # uses as the provenance test. Rewriting that marker makes a leaf claim to
    # be split out of itself, silently falsifying the input to the check built
    # to fix F18. The two failures are coupled through the comment half.
    touched = rewrite_refs(mod, parent_mod, apply)

    print(f"{mod} -> {parent_mod}")
    print(f"  files referencing it: {len(touched)}")
    print(f"  move: {os.path.relpath(src, AG)} -> {os.path.relpath(dst, AG)}")
    if apply:
        subprocess.run(["git", "mv", src, dst], cwd=ROOT,
                       capture_output=True)  # falls back below if untracked
        if not os.path.exists(dst):
            os.rename(src, dst)
        # the now-empty directory is residue of the split; drop it if bare
        d = src[:-5]
        parent_dir = os.path.dirname(src)
        if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
            os.rmdir(parent_dir)
        rewire_using(parent_mod, apply)
        print("  APPLIED")
    else:
        print("  (dry run — pass --apply)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
