#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Rename a definition AT ITS SOURCE and update the use sites that mean it.

⟡public-policy.  Under the import ban (no `using` / `renaming` / `hiding` /
`as` / qualifier) two modules cannot both export a name that one file needs.
An `import M using (f)` filter used to hide that; with bare imports the clash
surfaces as ClashingDefinition / AmbiguousName.  The ONLY ban-compliant fix is
to make the name unique where it is DEFINED — this tool does that.

WHICH USE SITES MEAN THIS DEFINITION.  After definition-per-file decomposition
a file that imports the defining leaf and mentions the name means THAT name.
That signal is precise but not total: a file may import the leaf AND use a
same-named definition from elsewhere (measured: 1 of 10 files in the Fin
`suc-injective` rename).  So this tool splits its output:

  RENAMED   — file imports the home module and no other provider of the name
  AMBIGUOUS — file imports the home module AND another provider; left alone
              and reported, because only the typechecker can arbitrate

Never guesses on an AMBIGUOUS file.  Run the build; each surviving error names
a site, and `--site FILE` applies the rename to just that one.
"""
import re,sys,os,glob
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from agda_defs import def_index

IMP=re.compile(r"^(open\s+import|import)\s+(\S+)")

from agda_lex import word   # THE Agda name-boundary authority; never re-derive
# ⚑ `word` was DEFINED here and needed by eight other tools.  Lifted to agda_lex
# (where the other name/span primitives live) and re-exported under this name so
# `spellings`/`apply_spellings` below are untouched.  A rename tool should not be
# the home of a lexical primitive.

def imports_of(path):
    return {m.group(2) for l in open(path).read().split("\n") if (m:=IMP.match(l))}


def spellings(old, new):
    """[(pattern, replacement)] covering BOTH spellings of an Agda operator.

    An operator is written `_≟_` in a signature/section but BARE in an infix
    clause (`zero ≟ zero = …`).  Renaming only the underscore form leaves the
    clauses behind as a separate, undefined operator.

    ⚑ THIS WAS A CLOSURE INSIDE `rename()` AND THEREFORE UNTESTABLE, which is
    exactly how the bug below survived: the module has no `_selftest`, so
    `run_selftests` reported 413/413 green across 11 suites while BOTH call
    sites of this logic were wrong — selection (`W.search`, so a file using
    only the bare-infix form was never even considered) and the write itself
    (`W.sub`, so the clauses kept the old spelling).  Lifted to module level so
    it can be asserted, and so the coming `--unrename` mode shares one
    implementation rather than re-deriving a third.
    """
    subs = [(word(old), new)]
    mo, mn = re.fullmatch(r"_(.+)_", old), re.fullmatch(r"_(.+)_", new)
    if mo and mn:
        o, n = mo.group(1), mn.group(1)
        # ⚑ A SECTION IS A THIRD SPELLING, and omitting it left every section
        # behind.  An operator appears as `_+_` (declaration), bare `+` (infix
        # clause), AND `_+` / `+_` (right/left SECTION — one hole, not two).
        # `word()` cannot match the section forms: it demands a name boundary,
        # and the section's own `_` is not one.  MEASURED: `fix_sections` could
        # not rewrite `cong (_+ x) p` at all until these two patterns existed —
        # its selftest failed 2/5 on exactly the case it was built for.
        subs.append((re.compile(r"\(_" + re.escape(o) + r"(?=\s)"), "(_" + n))
        subs.append((re.compile(r"(?<=\s)" + re.escape(o) + r"_(?=\s*\))"), n + "_"))
        subs.append((word(o), n))
    return subs


def qualified_spellings(text, home, old, new):
    """Ⓠ5 — the FIFTH spelling: `<alias>.name`, for every alias of `home` here.

    ⚑ AN ALIASED IMPORT IS A BLIND SPOT SHARED BY THREE TOOLS, measured today:
    `agda_defs --unused-imports` reads `open import` and cannot see an aliased
    one; `prune_imports` refuses `as` forms BY DESIGN; and this module rewrote the
    four BARE spellings and left `<alias>.name` untouched. One shape, three tools,
    each blind for its own reason — so a rename looked complete and was not.

    MEASURED: Ⓠ6ᵉ renamed `Groups.V4.Operations._·_` → `_·₄_` across 39 files and
    left `V4.·` standing at `SemidirectProduct/V/VOfAxisAnchor.agda:36`. The build
    found it — one file out of the 50 that alias that module — but only because
    scope checking stops at the first error, so "one" was never a safe count.

    ⚑ THE ALIAS IS PER-FILE, so this cannot be a static pattern like the other
    four: it must read the file's own `import … as <alias>` lines. That is why it
    takes `text` and returns spellings for THIS file rather than joining
    `spellings()`.

    ⚑ AND THE REGEX IS `agda_defs._alias_pattern`, NOT A NEW ONE. It carries two
    measured boundary rules — not preceded by a word char or dot (`F2.` occurs
    inside `Substrate.Algebra.F2.Polynomial`), and the name ends at a token
    boundary (a greedy capture on `F2.𝟙 ∷ F2.𝟘` runs past the first name). A
    fourth copy of that pattern is exactly the drift its docstring records.
    """
    import agda_defs as _ad
    bare_old = old.strip("_") or old
    bare_new = new.strip("_") or new
    subs = []
    for m in re.finditer(r"^\s*(?:open\s+)?import\s+(\S+)\s+as\s+(\S+)",
                         text, re.M):
        if m.group(1) != home:
            continue
        alias = m.group(2)
        pat = re.compile(_ad._alias_pattern(alias))

        def _rep(mm, _a=alias, _o=bare_old, _n=bare_new):
            # rewrite ONLY the renamed name; other names through the same alias
            # must survive untouched.
            return f"{_a}.{_n}" if mm.group(1) == _o else mm.group(0)
        subs.append((pat, _rep))
    return subs


def apply_spellings(s, subs):
    for pat, rep in subs:
        s = pat.sub(rep, s)
    return s


def any_spelling(s, subs):
    return any(pat.search(s) for pat, _ in subs)

def classify_file(f, home, home_file, imps, others, self_defines, site=None):
    """'renamed' | 'ambiguous' | 'skip' — the selection decision, PURE.

    ⚑ Ⓠ10: A FILE THAT DEFINES THE NAME ITSELF IS AMBIGUOUS, AND THIS MISSED IT.
    The rule was *"imports the home module and no OTHER PROVIDER"* — checked as
    `imps & others`, i.e. against what the file IMPORTS. A file that is ITSELF one
    of the other providers imports nothing extra, so it fell straight through to
    RENAMED.

    MEASURED, on the rename this was built for: `Algebra.R.Trace.V4FullCocycle`
    defines its own `_·_ : V4Full → V4Full → V4Full` AND imports
    `Groups.V4.Operations`. The rename rewrote the file's OWN operator to `_·₄_` —
    the wrong definition entirely — and corrupted two comment lines into
    `renaming (_·₄_ to _·₄_)`. Recovered from the run's own snapshot.

    ⚑ THIS IS THE DOCUMENTED HAZARD LANDING AS A FALSE POSITIVE RATHER THAN BEING
    CAUGHT. The docstring already says the signal is *"precise but not total"* and
    that a file may use a same-named definition from elsewhere — it just never
    considered ELSEWHERE = HERE. Extracted as a pure function so the decision is a
    millisecond assertion instead of reachable only through a tree-wide write.
    """
    if f == home_file or site:
        return "renamed"
    if home not in imps:
        return "skip"
    if self_defines:
        return "ambiguous"          # Ⓠ10 — the file is its own other provider
    if imps & others:
        return "ambiguous"
    return "renamed"


def rename(home,old,new,apply=False,site=None):
    idx=def_index()
    providers=set(idx.get(old,[]))
    if home not in providers:
        print(f"! {old} is not recorded as defined in {home}; providers={sorted(providers)}")
    others=providers-{home}
    # An Agda operator is written `_≟_` in a signature/section but BARE in an
    # infix clause (`zero ≟ zero = …`).  Renaming only the underscore form left
    # the clauses behind as a separate, undefined operator.
    subs=spellings(old,new)
    apply_subs=lambda s: apply_spellings(s,subs)
    hits=lambda s: any_spelling(s,subs)
    W=word(old)
    home_file="agda/"+home.replace(".","/")+".agda"
    renamed=[];ambiguous=[]
    targets=[site] if site else glob.glob("agda/Substrate/**/*.agda",recursive=True)
    for f in targets:
        s=open(f).read()
        # ⚑ hits(), NOT W.search: same two-spelling reason as the writer below.  A
        # file that uses ONLY the bare-infix form (`x ≟ y`, no underscore form
        # anywhere) was SKIPPED here and never renamed — selection and write had
        # the identical gap, so `hits` was dead alongside `apply_subs`.
        # ⚑ Ⓠ5: SELECTION MUST SEE THE QUALIFIED SPELLING TOO. A file whose ONLY
        # reference is `<alias>.name` has no bare spelling anywhere, so `hits(s)`
        # skipped it and the rename silently left it behind — the same
        # selection/write symmetry the bare-infix bug had. `VOfAxisAnchor` is
        # exactly that file: its one use of the operation is `V4.·`.
        _qsubs = qualified_spellings(s, home, old, new)
        if not (hits(s) or any(p.search(s) for p, _ in _qsubs)): continue
        # ⚑ Ⓠ10: `others` is a set of MODULE NAMES, so membership is tested on the
        # file's own module path — a file can be one of the other providers.
        _mod = f[len("agda/"):-len(".agda")].replace("/", ".") if f.startswith("agda/") else None
        _verdict = classify_file(f, home, home_file, imports_of(f), others,
                                 _mod in others, site)
        if _verdict == "renamed":
            renamed.append(f)
        elif _verdict == "ambiguous":
            ambiguous.append(f)
    if apply:
        # ⚑ Snapshot before the first write (edit_snapshot.py).  A rename touches many
        # importers at once; a wrong one is only visible at the build.
        import edit_snapshot
        # ⚑ `intent="apply"` IS ENTAILED BY THE BRANCH — this is inside `if apply:`,
        # immediately above the rename loop, and `apply` is a PARAMETER of `rename`
        # rather than a read of argv.
        # ⚑⚑ AND THAT PARAMETER IS WHY AN ARGV-READING GATE IS WRONG HERE, NOT MERELY
        # REDUNDANT.  `rename` is called as a LIBRARY by `split_pipeline.py:368,370`
        # (`RAS.rename(home, name, new, apply=True)`) during its collision cure — at
        # which point `sys.argv` belongs to split_pipeline and says nothing about
        # this rename. A `require_at_entry` here would either refuse the pipeline's
        # legitimate cure or read the pipeline's own `--apply` as authorising a
        # rename the caller never spelled; both are the contract answering a
        # question it was not asked. The caller states the intent by PASSING it, and
        # forwarding that is what makes the guard see the same decision the branch
        # made. (The pipeline's own entry gate is where its argv is read.)
        edit_snapshot.guard(f"rename_at_source {old}->{new} @{home}", renamed,
                            intent="apply")
        for f in renamed:
            # READ FIRST.  `open(f,"w").write(sub(open(f).read()))` truncates the
            # file before the inner read runs — it emptied three modules.
            s=open(f).read()
            # ⚑ apply_subs, NOT W.sub.  `subs` carries BOTH spellings (`_≟_` in a
            # signature, bare `≟` in an infix clause) and W is the underscore form
            # only — so W.sub renamed the signature and left the clauses behind as
            # an undefined operator, the exact bug the comment above describes as
            # fixed.  apply_subs was built at :48 and called NOWHERE (measured);
            # the writer never used it.  Dead guard = no guard.
            # ⚑ Ⓠ5: the QUALIFIED spellings are per-file (the alias varies), so
            # they are derived from THIS file's text and applied alongside the
            # four bare ones. Selection above uses the same derivation — the
            # symmetry that was missing when `hits`/`apply_subs` drifted apart.
            open(f,"w").write(apply_spellings(apply_subs(s),
                                              qualified_spellings(s, home, old, new)))
    print(f"{'RENAMED ' if apply else 'WOULD RENAME'} {len(renamed)} file(s)  {old} -> {new}  (home {home})")
    for f in ambiguous:
        print(f"  AMBIGUOUS (left alone, build must arbitrate): {f}")
    return renamed,ambiguous

def _selftest():
    """Counted from len(cases) — a hardcoded total once hid a 10th case
    (prune_imports.py:332).

    ⚑ WHY THIS MODULE HAD NONE, AND WHAT IT COST.  `rename_at_source` REWRITES
    AGDA SOURCE across every importer of a name, and it shipped with no test at
    all.  `run_selftests.py` discovers modules that DEFINE `_selftest`, so this
    one was not failing — it was INVISIBLE, and the suite read 413/413 green
    across 11 suites while two live bugs sat in the write path (selection on
    `W.search`, write on `W.sub`; both missed the bare-infix spelling).  A
    discovered population still only discovers what opted in.
    """
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ── word(): Agda names are not \w ──────────────────────────────────────
    check("word: matches a standalone name", bool(word("suc").search("f suc x")), True)
    check("word: does NOT match inside a longer name",
          bool(word("suc").search("suc-injective")), False)
    check("word: bounded by parens, not word chars",
          bool(word("_+_").search("(_+_)")), True)
    check("word: unicode name matches", bool(word("ℕ").search("n : ℕ")), True)

    # ── spellings(): the MEASURED two-spelling bug ─────────────────────────
    op = spellings("_≟_", "_≟ℕ_")
    # ⚑ CONTRACT WIDENED (2026-08-01): an operator has FOUR spellings, not two.
    # `_≟_` (declaration), bare `≟` (infix clause), and `_≟` / `≟_` (right/left
    # SECTION — one hole).  The section forms were missing, so every section
    # survived a rename as a reference to an operator that no longer exists —
    # the `[NoParseForApplication] … Operators used in the grammar: None` class
    # (`F2/Vector.agda:167`, 590 sites tree-wide).  `word()` cannot match them:
    # it demands a name boundary and a section's own `_` is not one.
    # This case asserted the OLD contract and failed loudly when it changed,
    # which is the suite working — updated deliberately, not silenced.
    check("spellings: an operator yields all FOUR spellings", len(op), 4)
    check("spellings: a RIGHT section is rewritten",
          apply_spellings("cong (_≟ x) p", op), "cong (_≟ℕ x) p")
    check("spellings: a LEFT section too",
          apply_spellings("cong (x ≟_) p", op), "cong (x ≟ℕ_) p")
    check("spellings: underscore form rewritten in a signature",
          apply_spellings("dec : Decidable _≟_", op), "dec : Decidable _≟ℕ_")
    check("spellings: BARE INFIX form rewritten in a clause "
          "(W.sub left these behind — the shipped bug)",
          apply_spellings("zero ≟ zero = yes", op), "zero ≟ℕ zero = yes")
    check("spellings: a file using ONLY the bare form is SELECTED "
          "(W.search skipped it entirely — the shipped bug)",
          any_spelling("zero ≟ zero = yes", op), True)
    plain = spellings("suc", "fsuc")
    check("spellings: a NON-operator yields exactly one spelling", len(plain), 1)
    check("spellings: non-operator rename applies",
          apply_spellings("f suc x", plain), "f fsuc x")
    check("spellings: non-operator does not touch a longer name",
          apply_spellings("suc-injective", plain), "suc-injective")
    # asymmetric: old is an operator, new is not (and vice versa) -> no bare pair
    check("spellings: no bare pair when only ONE side is an operator",
          len(spellings("_+_", "plus")), 1)

    # ── IMP: the import-line matcher imports_of() keys on ──────────────────
    check("IMP: matches `open import`", bool(IMP.match("open import Substrate.Foo")), True)
    check("IMP: matches bare `import`", bool(IMP.match("import Substrate.Foo")), True)
    check("IMP: captures the module name",
          IMP.match("open import Substrate.Foo.Bar using (x)").group(2),
          "Substrate.Foo.Bar")
    check("IMP: an INDENTED import is not matched (col-0 only, by design)",
          bool(IMP.match("  open import Substrate.Foo")), False)

    # ── Ⓠ5 qualified_spellings(): the FIFTH spelling ───────────────────────
    # ⚑ THE SITE THAT SURVIVED A COMPLETED RENAME. Ⓠ6ᵉ rewrote 39 files and left
    # `V4.·` at `VOfAxisAnchor:36`; the build caught it, but only because scope
    # checking halts at the first error — so "one site" was luck, not a count.
    QH = "Substrate.Groups.V4.Operations"
    src = ("import Substrate.Groups.V4.Operations as V4\n"
           "f x y = x V4.· y\n")
    qs = qualified_spellings(src, QH, "_·_", "_·₄_")
    check("⚑ Ⓠ5: an ALIASED import yields a qualified spelling", len(qs), 1)
    check("...and the qualified use site is rewritten",
          apply_spellings(src, qs).splitlines()[1], "f x y = x V4.·₄ y")
    # ⚑ ONLY THE RENAMED NAME. Other names reached through the same alias must
    # survive — a blanket `alias.` substitution would rewrite all of them.
    src2 = ("import Substrate.Groups.V4.Operations as V4\n"
            "g = V4.ε\n"
            "h x y = x V4.· y\n")
    out2 = apply_spellings(src2, qualified_spellings(src2, QH, "_·_", "_·₄_"))
    check("⚑ a DIFFERENT name through the same alias is untouched",
          out2.splitlines()[1], "g = V4.ε")
    check("...while the renamed one still changes",
          out2.splitlines()[2], "h x y = x V4.·₄ y")
    # an alias of a DIFFERENT module must not be rewritten
    src3 = ("import Substrate.Algebra.Magma as V4\n"
            "k x y = x V4.· y\n")
    check("an alias of ANOTHER module yields no spelling",
          len(qualified_spellings(src3, QH, "_·_", "_·₄_")), 0)
    check("a file with no aliased import yields none",
          len(qualified_spellings("open import Substrate.Groups.V4.Operations\n",
                                  QH, "_·_", "_·₄_")), 0)

    # ── Ⓠ10 classify_file(): the SELECTION decision ────────────────────────
    # ⚑ EVERY CASE HERE IS THE DECISION THAT REWROTE THE WRONG DEFINITION. The
    # write path was only reachable through a tree-wide glob, so the rule that
    # picks RENAMED vs AMBIGUOUS had no test at all — it shipped, ran over 92
    # importers, and corrupted the one file that was its own other provider.
    HOME = "Substrate.Groups.V4.Operations"
    HF = "agda/Substrate/Groups/V4/Operations.agda"
    OTH = {"Substrate.Algebra.Magma", "Substrate.Algebra.F2.Op"}
    check("classify: the HOME file itself is always renamed",
          classify_file(HF, HOME, HF, set(), OTH, False), "renamed")
    check("classify: a file not importing home is skipped",
          classify_file("x.agda", HOME, HF, {"Substrate.Other"}, OTH, False),
          "skip")
    check("classify: imports home and nothing else providing → renamed",
          classify_file("x.agda", HOME, HF, {HOME}, OTH, False), "renamed")
    check("classify: imports home AND another provider → ambiguous",
          classify_file("x.agda", HOME, HF,
                        {HOME, "Substrate.Algebra.Magma"}, OTH, False),
          "ambiguous")
    # ⚑ THE Ⓠ10 CASE. `V4FullCocycle` imports home and defines its OWN `_·_`, so
    # it imports no OTHER provider — `imps & others` is empty and the old rule
    # said RENAMED. It is its own other provider.
    check("⚑ Ⓠ10: a file that DEFINES the name itself → ambiguous, not renamed",
          classify_file("x.agda", HOME, HF, {HOME}, OTH, True), "ambiguous")
    check("...and --site still forces the rename, so the escape hatch survives",
          classify_file("x.agda", HOME, HF, {HOME}, OTH, True, site="x.agda"),
          "renamed")

    ok = sum(1 for _, good, _, _ in cases if good)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"rename_at_source selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__=="__main__":
    # ⚑ --selftest must be dispatched BEFORE the arity check, or the suite runner
    # gets usage text and `run_selftests` scores it as a FAILING suite (it treats
    # a missing `selftest: N/M` line as failure, by design).
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    a=[x for x in sys.argv[1:] if not x.startswith("--")]
    site=next((x.split("=",1)[1] for x in sys.argv[1:] if x.startswith("--site=")),None)
    if len(a)<3:
        print(__doc__); print("usage: rename_at_source.py <Home.Module> <old> <new> [--apply] [--site=FILE]")
        sys.exit(2)
    rename(a[0],a[1],a[2],apply="--apply" in sys.argv,site=site)
