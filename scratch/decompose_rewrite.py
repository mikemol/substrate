#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""DECLARATIVE decomposition rewrite.

State: "module M has been decomposed into leaves."  This rewrites EVERY
importer of M in one pass — it does not discover work from build errors.

The information was always there: `open import M using (a; b; c)` IS a
declaration of demand, and each name resolves to exactly one definer via the
shared index.  So the rewrite is a pure function of (module, definer index):

    open import M using (a; b; c)
      ->  open import <definer of a>
          open import <definer of b>
          open import <definer of c>

An error-driven loop rediscovers this one name per build, and — worse —
deleting the `using` list first DESTROYS the demand declaration, which is
how this session lost eight bindings in one file and then spent eight builds
recovering them.  Read the demand BEFORE removing it.

Names that resolve back to M mean M is not fully decomposed yet: REPORTED,
never guessed.  Routes every edit through agda_imports (topo order +
permutation guard).

Usage:  decompose_rewrite.py <Module> [--prefer <Module.Prefix>] [--apply]
        decompose_rewrite.py --selftest

⚑ `--prefer <prefix>` IS THE AMBIGUITY DECLARATION, and the paragraph above is why it has to be
one. A name defined in several tiers has several homes, and this tool REPORTS rather than
guesses — so without a tie-break every multi-homed name lands in `unresolved` and the rewrite
stalls on exactly the names a decomposition creates. `--prefer` narrows the candidate homes to
those whose module path starts with the prefix, and ONLY when that narrowing is non-empty: a
prefix matching nothing leaves the name unresolved rather than silently dropping it. It is the
operator DECLARING where the decomposition put its names, which is information the tree does not
carry — never an inference the tool is entitled to make on its own."""
import re,sys,glob,collections
sys.path.insert(0,"scratch")
from agda_defs import def_index
from agda_imports import add_import, parse_block
import agda_lex

# ⚑ A continuation line is an INDENTED line that continues the import — but a naive
# `(\n\s+[^\n]*)*` also swallows the indented parameter list of a following
# `module M (a : A) … where` header, deleting the header and the module's whole
# telescope.  Measured: 33 files gutted, Coxeter/Core.agda 76 lines -> 3, found only
# by the build (twice — once by a hand-written copy of this regex, once by this tool).
# A continuation must NOT start a new top-level construct.  An import's real
# continuations are its using/hiding/renaming/public tails and applied-module args.
_STOP = r"(?:module|open|import|data|record|postulate|private|variable|abstract|opaque)"
CONT = r"(?:\n[ \t]+(?!" + _STOP + r"\b)[^\n]*)*"


def drop_import(src, mod):
    """`src` with every top-level `import mod`/`open import mod` statement removed.

    Pure and total: the one function whose failure silently destroys source, so it
    is the one with a regression test (`--selftest`).
    """
    return re.sub(r"^(open\s+)?import\s+" + re.escape(mod) + r"(?![\w.])[^\n]*" + CONT + r"\n",
                  "", src, flags=re.M)


def indented_imports(src, mod):
    """[(lineno, line)] for INDENTED imports of `mod` — the ones `drop_import` leaves.

    Not a defect to hide: an indented import's scope is its enclosing clause, so the
    leaf it should become follows that clause's demand.  Rewriting it from file-level
    demand would be a guess.  Reporting it is the honest half — silence here is what
    leaves a consumer importing a DELETED module until the build says so.
    """
    pat = re.compile(r"^[ \t]+.*\b(?:open\s+)?import\s+" + re.escape(mod) + r"(?![\w.])")
    return [(i, l) for i, l in enumerate(src.split("\n"), 1) if pat.match(l)]


def _selftest():
    """Counted — a hardcoded total once hid an added case (prune_imports.py:332)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    M = "Substrate.Foundation.Eq"

    # THE regression: an import directly above a PARAMETERIZED module header.  The
    # header's telescope is indented, and eating it removed the module itself.
    src = ("{-# OPTIONS --safe #-}\n\n"
           "open import Substrate.Foundation.Eq using (_≡_)\n\n"
           "module Substrate.Groups.Coxeter.Core\n"
           "  (Word : Set)\n"
           "  (_++_ : Word → Word → Word)\n"
           "  where\n\n"
           "body : Set\n")
    got = drop_import(src, M)
    check("parameterized module header SURVIVES the drop",
          "module Substrate.Groups.Coxeter.Core" in got and "(Word : Set)" in got, True)
    check("the import itself is gone", "Foundation.Eq using" in got, False)
    check("body preserved", "body : Set" in got, True)

    # A genuine multi-line import must still be removed whole, tail included.
    multi = ("open import Substrate.Foundation.Eq\n"
             "  using (_≡_; refl)\n"
             "  renaming (trans to ≡tr)\n"
             "next : Set\n")
    g2 = drop_import(multi, M)
    check("multi-line import removed INCLUDING its indented tail", g2, "next : Set\n")

    # A different module must not be touched.
    other = "open import Substrate.Foundation.Nat using (ℕ)\n"
    check("unrelated import untouched", drop_import(other, M), other)

    # ⚑ THE 120-FILE REGRESSION.  The pre-fix rule ate whatever followed the import.
    # Two shapes, both measured, both silent until a full rebuild invalidated the
    # .agdai caches — which is why the damage read as "6 errors" for hours:
    #   (a) a `private` / `variable` BLOCK  -> [NotInScope] ℓ / ℓ0 / ℓO across the tree
    #   (b) a leaf's TYPE SIGNATURE         -> [MissingTypeSignature.Function]
    #       (Foundation/Bool/Properties/AndAssoc.agda lost `∧-assoc : …`, keeping only
    #        its clauses — the split leaves were untracked, so git could not restore
    #        them and they had to be re-split from the monolith.)
    varblk = ("open import Substrate.Foundation.Eq using (_≡_)\n\n"
              "private\n  variable\n    ℓ0 ℓ1 ℓ2 : Level\n\n"
              "rec : Set\n")
    g4 = drop_import(varblk, M)
    check("a following `private variable` block SURVIVES",
          "ℓ0 ℓ1 ℓ2 : Level" in g4 and "private" in g4, True)
    check("the variable block's import is still gone", "Foundation.Eq using" in g4, False)

    sig = ("open import Substrate.Foundation.Eq.Eq\n"
           "∧-assoc : (a b c : Bool) → (a ∧ b) ∧ c ≡ a ∧ (b ∧ c)\n"
           "∧-assoc true  b c = refl\n")
    g5 = drop_import(sig, "Substrate.Foundation.Eq.Eq")
    check("a following TYPE SIGNATURE survives (leaf kept its clauses but lost `: …`)",
          "∧-assoc : (a b c : Bool)" in g5, True)

    # Prefix collision: `Substrate.Foundation.Eq.Cong` is NOT `Substrate.Foundation.Eq`.
    leaf = "open import Substrate.Foundation.Eq.Cong\n"
    check("a LEAF of the module is not mistaken for it", drop_import(leaf, M), leaf)

    # ⚑ KNOWN LIMIT, pinned rather than papered over: `drop_import` is ^-anchored, so an
    # INDENTED import (`f = x where open import M`) is NOT removed.  Removing it blindly
    # would be wrong anyway — an indented import's scope is the enclosing clause, and the
    # leaf it should become depends on that clause's demand, not the file's.  So the tool
    # must REPORT these instead of silently leaving them behind (they were hand-fixed in 4
    # files this arc, which is how the gap was found).  `indented_imports` is that report.
    nested = "f = x\n  where open import Substrate.Foundation.Eq\n"
    check("indented import is LEFT (^-anchored; scope is the clause, not the file)",
          "Foundation.Eq" in drop_import(nested, M), True)
    check("...and is REPORTED so it is never silently missed",
          indented_imports(nested, M), [(2, "  where open import Substrate.Foundation.Eq")])
    check("no false report when there is no indented import",
          indented_imports("open import Substrate.Foundation.Eq\n", M), [])

    ok = sum(1 for _, good, _, _ in cases if good)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"decompose_rewrite selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if "--selftest" in sys.argv:
    sys.exit(_selftest())

mod=sys.argv[1]; apply="--apply" in sys.argv
# A decomposition DECLARES where its names went; without that, a name defined
# in several tiers is ambiguous and must not be guessed.
prefer=None
if "--prefer" in sys.argv: prefer=sys.argv[sys.argv.index("--prefer")+1]
idx=def_index()
IMPM=re.compile(r"^(open\s+)?import\s+"+re.escape(mod)+r"(?![\w.])(.*)$")

def renames(stmt_text):
    """`renaming (a to b)` — dropping it means body uses of b become a."""
    out={}
    m=re.search(r"renaming\s*\(([^)]*)\)",stmt_text,re.S)
    if m:
        for part in m.group(1).split(";"):
            if " to " in part:
                a,b=part.split(" to ",1); out[b.strip()]=a.strip()
    return out

def demanded(stmt_text):
    """names a statement declares it wants; empty = wants everything"""
    out=[]
    for kw in ("using","renaming","hiding"):
        m=re.search(kw+r"\s*\(([^)]*)\)",stmt_text,re.S)
        if m:
            for part in m.group(1).split(";"):
                part=part.strip()
                if not part: continue
                out.append(part.split(" to ")[0].strip() if " to " in part else part)
    return out

plan=collections.defaultdict(list); unresolved=[]; wildcard=[]; ren={}; qual={}

def stmts_of(text):
    """EVERY import statement in the file, not just the leading block: Agda
    permits a top-level import after definitions, and one such import (at
    ExtrudeCoEmitGraded:1328) was invisible to a leading-block-only scan."""
    out=[];cur=None
    for l in text.split("\n"):
        m=re.match(r"^(open\s+)?import\s+(\S+)(.*)$",l)
        if m:
            if cur: out.append(cur)
            cur={"mod":m.group(2),"lines":[l]}
        # ⚑ the SECOND span copy in this file.  `drop_import` above was fixed after the
        # 33-file incident and this one was not — one guarded site beside one naive site
        # is the signature of per-site patching without a shared home, which is how the
        # rule reached fifteen divergent copies.  Both now route through agda_lex.
        elif cur is not None and agda_lex._continues(
                l, agda_lex._depth_after(agda_lex.mask_comments("\n".join(cur["lines"])), 0)):
            cur["lines"].append(l)
        else:
            if cur: out.append(cur); cur=None
    if cur: out.append(cur)
    return out

for p in sorted(glob.glob("agda/Substrate/**/*.agda",recursive=True)):
    body=open(p).read()
    for s in stmts_of(body):
        if s["mod"]!=mod: continue
        text=" ".join(s["lines"])
        m=re.search(r"\bas\s+(\S+)",text)
        if m:                       # banned qualified alias: demand = its A.name uses
            alias=m.group(1); qual[p]=alias
            for n in sorted(set(re.findall(re.escape(alias)+r"\.([A-Za-z0-9_'ₛ⁻¹≈·-]+)",body))):
                homes=[h for h in (idx.get(n) or idx.get("_"+n+"_") or []) if h!=mod]
                if prefer:
                    pr=[h for h in homes if h.startswith(prefer)]
                    if pr: homes=pr
                if len(homes)==1: plan[p].append((n,homes[0]))
                else: unresolved.append((p,alias+"."+n,homes[:4]))
            continue
        names=demanded(text)
        ren.setdefault(p,{}).update(renames(text))
        if not names:
            # ⚑ WILDCARD (`open import M`, no filter).  Ban-COMPLIANT, so these are
            # not debt — but M is gone, so they still must be rewired, and there is
            # no `using` list to read the demand from.  Recover it the only other
            # way it is actually stated: the BODY.  A name M defines that the body
            # mentions is demanded; one it never mentions is not.  This is the same
            # resolve-name-to-definer step as above, sourced from tokens instead of
            # a filter, so it shares `prefer` and the same refuse-on-ambiguity rule.
            #
            # Without this the wildcards are silently left importing a DELETED module
            # (measured: 480 of 649 Foundation.Eq consumers), which surfaces far later
            # as an unresolved-import build failure rather than here.
            # ⚑ A `variable a b c : Level` binder is in the def index but is NOT an
            # export: every leaf inherits the preamble's one-letter level vars, and a
            # one-letter token matches nearly any body.  Scanning them made all 209
            # wildcards ambiguous on `a`/`b` (each "defined" by 4 leaves).  Demand is
            # over REAL exports, so require a name to be either mixfix (`_≡_`) or
            # longer than one character.
            # ...and an Agda KEYWORD is never a demanded name.  `split_lemmas` names a
            # `private` block's unit `Private`, which puts the bare keyword in the index;
            # every body containing a `private` block then "demands" it.
            KW={"private","public","open","import","module","where","record","data",
                "field","postulate","variable","abstract","opaque","instance","let","in"}
            own={n for n,ms in idx.items()
                 if any(h.startswith(mod+".") for h in ms)
                 and (len(n.strip("_"))>1 or "_" in n)
                 and n not in KW}
            toks=set(re.findall(r"[^\s(){}\[\];,]+",body))
            hits=sorted(n for n in own
                        if n in toks or n.strip("_") in toks)
            if not hits: wildcard.append(p); continue
            for n in hits:
                homes=[h for h in (idx.get(n) or idx.get("_"+n+"_") or []) if h!=mod]
                if prefer:
                    pref=[h for h in homes if h.startswith(prefer)]
                    if pref: homes=pref
                if len(homes)==1: plan[p].append((n,homes[0]))
                else: unresolved.append((p,n,homes[:4]))
            continue
        for n in names:
            homes=[h for h in (idx.get(n) or idx.get("_"+n+"_") or []) if h!=mod]
            if prefer:
                pref=[h for h in homes if h.startswith(prefer)]
                if pref: homes=pref
            if len(homes)==1: plan[p].append((n,homes[0]))
            else: unresolved.append((p,n,homes[:4]))

print(f"=== {mod}: {len(plan)} importers with resolvable demand")
for p,items in sorted(plan.items()):
    print(f"  {p[15:]}")
    for n,h in items: print(f"      {n:22s} -> {h}")
if wildcard: print(f"--- {len(wildcard)} unfiltered importer(s) (demand unstated): "+", ".join(w[15:] for w in wildcard[:5]))
if unresolved:
    print(f"--- {len(unresolved)} unresolved (M not fully decomposed, or ambiguous):")
    for p,n,h in unresolved[:10]: print(f"      {p[15:]}  {n} -> {h}")

if apply:
    # ⚑ Snapshot BEFORE the first write (see edit_snapshot.py): a rewrite tool that
    # damages a file cannot be un-damaged by noticing later.  Whole-worktree, because
    # the case that needs recovering is precisely the file the tool did not mean to
    # touch.  Never restores — records how to.
    import edit_snapshot
    edit_snapshot.guard(f"decompose_rewrite {mod}", list(plan))
    for p,items in plan.items():
        s=open(p).read()
        # ⚑ A continuation line is an INDENTED line that continues the import — but
        # `(\n\s+[^\n]*)*` also swallows the indented parameter list of a following
        # `module M (a : A) … where` header, deleting the header and the module's whole
        # telescope.  Measured: 33 files gutted, Coxeter/Core.agda 76 lines -> 3, found
        # only by the build.  A continuation must therefore NOT start a new top-level
        # construct; `module`/`open`/`import`/`data`/`record`/`postulate` and a `{-# … #-}`
        # pragma all terminate the statement.  (An import's real continuations are its
        # `using`/`hiding`/`renaming`/`public` tails and applied-module arguments.)
        s=drop_import(s,mod)
        for new,old in ren.get(p,{}).items():          # drop rename -> restore original name
            s=re.sub(r"(?<![\w'-])"+re.escape(new)+r"(?![\w'-])",old,s)
        if p in qual:                                  # drop qualifier -> bare name
            s=re.sub(re.escape(qual[p])+r"\.","",s)
        open(p,"w").write(s)
        for n,h in items:
            args="Axis" if ".Symmetric." in h else ""
            add_import(p,h,args)
        print("rewrote",p[15:])
