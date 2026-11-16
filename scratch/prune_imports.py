#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Drop imports a file does not use.

⟡public-policy: the ban forbids `using (…)`, so a sibling cannot narrow WITHIN
an import — but it can decline to import a module it never references.  That
is the ban-compliant way to kill the ambiguity a `using` filter used to mask
(Foundation.Vec.head vs the stream head), and it shrinks the elaboration
closure, which is what the 128MiB cap is actually measuring.

A module with no entries in the definition index is KEPT (unknown provision is
not evidence of non-use); `renaming` targets count as references.

⚑ AN ALIASED IMPORT (`import M as Q`) IS DECIDED, NOT EXEMPT (Ⓠ5ᵇ, 2026-08-20).
It used to return KEEP without looking, lumped in with `renaming`, because a
`Q.name` use site is invisible to the token probe — `agda_lex.body_tokens` splits
on the dot, so `V4.·` becomes two unrelated tokens and the alias link is lost.
That caution was right for the WRITE path and made the class UNMEASURABLE: the
census read 2 unused for a cluster carrying 272 provably-dead aliases, and 857
aliased imports tree-wide sat outside the census that drives every prune.

The evidence is in the RAW TEXT, which is why `should_keep` takes `body_text`:
`agda_defs._alias_refs` reads every `<alias>.name` occurrence, so an aliased
import with ZERO qualified references is decidably unused and one with any
reference is decidably used — neither verdict is a guess. Keep-bias is preserved
at the entry: `body_text is None` means the caller could not supply the evidence,
NOT that there is none, so it returns KEEP.

MEASURED: 236 dead aliases dropped across 272 files in `ExtrudeCoEmitGraded`,
census 238 → 0, with no new build errors.
"""
import re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from agda_defs import def_index

# Mixfix names whose SECTIONS ARE DELIMITERS (`[_,_]`, `⟨_⟩`, `⌊_⌋`) cannot
# survive the whitespace/punct tokenizer used below — they are built from the
# very characters it splits on.  Collect them once from the def-index so the
# body scan can look for them verbatim.  A name qualifies when it contains a
# tokenizer delimiter; plain symbolic operators (`_+_`) are already handled by
# the section reconstruction and are excluded to keep this set small.
_MIXFIX_DELIMS = set("(){}[];,")


def _mixfix_names():
    # ⚑ THE PREDICATE MOVED TO `agda_lex.mixfix_delims`; the def-index is still THIS
    # caller's choice.  Splitting it that way is deliberate: which characters delimit is
    # a LEXICAL fact the lexer owns, while which name-set bounds the scan is a question
    # about this corpus — and pulling `def_index` into `agda_lex` would invert the
    # dependency, since `agda_defs` reads the lexer and not the reverse.
    return agda_lex.mixfix_delims(def_index())
import agda_lex

IMP=re.compile(r"^(open\s+import|import)\s+(\S+)")

def _spans(L):
    """Import statement spans, from the ONE authority (scratch/agda_lex).

    This file previously carried the naive `startswith(" ")` span rule TWICE,
    in one function (the skip-set and the delete loop).  Indentation alone does
    not delimit a statement: inside a nested `module M where` the following
    definitions are indented too, so the naive rule swallows them — and the
    delete loop below then removes a definition along with a dead import.
    MEASURED corpus-wide: 14 statements where the naive rule over-runs, led by
    Discipline.agda:245 (+2, the file whose measured loss motivated the guard)
    and IsPermutation.agda:86 (+25 lines).
    """
    return {s.start:s.end for s in agda_lex.statements(L) if s.kind=="import"}

# Sentinel: "the demand map was consulted and returned NO EVIDENCE either way."
# Distinct from None ("no demand map for this module — fall back to the
# provision index"), because a no-evidence verdict must KEEP the import rather
# than be overturned by the weaker index.
_KEEP=object()

# the sentinel a detail-mode prune returns for a pure aggregation barrel, whose
# imports liveness-by-use CANNOT judge (a module with no body uses nothing by
# construction).  Returned rather than printed so a census cannot silently
# report a refused barrel as "0 unused" — a false zero of the exact kind this
# repo keeps paying for.
_BARREL=("<aggregation-barrel>", None)

def _shared_names(inherited):
    """Names the monolith claimed from MORE THAN ONE module (F30).

    A hit on such a name is evidence for neither import — `[]`/`_∷_` are
    claimed by both Vec and List — so the drop rule judges only on uniquely
    owned names.  Pure in `inherited`; compute once per run, never per import.
    """
    return {n for n,ms in _owners(inherited).items() if len(ms)>1}

def _owners(inherited):
    """name -> {modules that claimed it} in the monolith's own demand map."""
    o={}
    for m,ns in inherited.items():
        for n in ns: o.setdefault(n,set()).add(m)
    return o


def should_keep(mod, txt, toks, idx, prov_cache, inherited, shared,
                body_text=None):
    """THE decision, pure: keep this import or drop it?  No I/O, no file writes.

    Extracted so the rule can be unit-tested on its own.  The dead-store bug
    that discarded the shared-name subtraction (F30, two drafts of two rules
    left stacked, the weaker one winning) lived inside the write path where
    nothing could reach it; as a pure function it is a millisecond assertion.

    Returns True to KEEP.  Every uncertain branch returns True: no evidence is
    never evidence of death, and a false DROP breaks the build immediately.

    THE DEMAND DECLARATION BEATS THE PROVISION INDEX.  `def_index` sees
    top-level defs only — it misses record FIELDS, constructors and pattern
    synonyms — so a partial provision set made this prune DROP a live import
    (measured: `Wedge.Graded using (GradedWedge; recon; gcell)`, where `recon`
    is a record field, so provision∩body was empty and the statement was
    deleted though `recon` is used).  A `using` list is the file's OWN
    statement of what it wants: consult it first, and fall back to the index
    only for a bare import.

    ⚑ SHARED NAMES CARRY NO EVIDENCE (F30).  Within the monolith's own demand
    map `[]`/`_∷_` are claimed by BOTH Vec and List, so a hit on them says
    nothing about which import is live; `_++_`/`map`/`tabulate` are claimed by
    exactly one and are sound evidence.  Judge on the uniquely owned names.
    Unlike the reverted F29 rule this is NOT a guess from provision overlap —
    the monolith SAID which module it wanted each name from.

    ⚑ NO UNIQUE NAME ⇒ NO EVIDENCE ⇒ KEEP, and it must NOT fall through to the
    provision index: that is strictly WEAKER evidence (it sees both modules as
    providers of `[]`, the very ambiguity the demand map exists to resolve), so
    falling through would let the weakest signal overturn a deliberate
    no-evidence verdict.  MEASURED on Enumerate/Perms: its sole Vec name is
    `[]`, shared, so uniq(Vec)={Vec,map,tabulate} and none appear — dropping
    Vec there is a FALSE POSITIVE ([] IS Vec's, at type `Perm zero`).  The
    caller's SIBLING CLOSURE is what supplies the missing evidence.

    ⚑ DO NOT "improve" the probe into a UNIQUE-PROVISION test (tried and
    REVERTED, F29).  Subtracting names a sibling import also provides looks
    like it kills the Vec-vs-List ambiguity, but provision overlap is
    SYMMETRIC: the rule cannot tell which of two overlapping modules the file
    means, so it drops whichever it scans second.  MEASURED: 13 of 20 Enumerate
    leaves broke.  Disambiguation needs the TYPE, which a token scan lacks.
    """
    # ⚑ Ⓠ5ᵇ: AN ALIASED IMPORT IS DECIDABLE, AND THIS KEPT IT UNCONDITIONALLY.
    # `import M as Q` was lumped with `renaming`/`using` and returned KEEP without
    # looking, because a `Q.name` use site is invisible to the bare-token probe
    # below — so dropping one could break the build. That caution is right for the
    # WRITE path and made the whole class UNMEASURABLE: 857 aliased imports
    # tree-wide sit outside the census that drives every prune, including 272
    # provably-unused ones in `ExtrudeCoEmitGraded` that `--alias-trace` reports as
    # `used: []`.
    #
    # The evidence exists: `agda_defs._alias_refs` reads every `<alias>.name` in
    # the text — THE one regex, with two measured boundary rules. So an aliased
    # import with ZERO qualified references is decidably unused, and one with any
    # reference is decidably used. Neither verdict is a guess.
    # ⚑ KEEP-BIASED AT THE ENTRY, NOT JUST IN THE BRANCHES. `body_text is None`
    # means the CALLER could not supply the evidence — not that there is none. My
    # first cut wrote `body_text or ""`, which turns a missing argument into an
    # empty search and therefore a DROP: the omission would decide the verdict.
    # Every uncertain branch here returns keep; an absent input is the most
    # uncertain branch there is.
    m_alias = re.match(r"^\s*(?:open\s+)?import\s+\S+\s+as\s+(\S+)", txt)
    if m_alias and mod.startswith("Substrate") and "renaming" not in txt:
        if body_text is None:
            return True                      # no evidence available ⇒ keep
        import agda_defs as _ad
        return bool(_ad._alias_refs(m_alias.group(1), body_text))
    if not (mod.startswith("Substrate") and "renaming" not in txt and " as " not in txt):
        return True
    u=re.search(r"\busing\s*\(([^)]*)\)",txt)
    demand={t for t in re.split(r"[;\s]+",u.group(1)) if t} if u else None
    if demand is None and inherited and mod in inherited:
        uniq=set(inherited[mod])-(shared or set())
        if not uniq:
            return True                      # no discriminating name ⇒ no evidence ⇒ keep
        demand=uniq
    if demand is None:
        if mod not in prov_cache:
            prov_cache[mod]={n for n,ms in idx.items() if mod in ms}
        demand=prov_cache[mod]
        if not demand: return True           # unknown provision ⇒ keep
    probe={p for n in demand for p in agda_lex.mixfix_forms(n)}
    return bool(probe & toks)


def prune(path,idx,prov_cache,inherited=None,shared=None,apply=True,detail=False):
    """`detail=True` returns [(line_no, module)] instead of the count.

    ⚑ ADDED FOR THE CENSUS (`agda_defs --unused-imports`), WHICH NEEDED THE NAMES
    AND WOULD OTHERWISE HAVE RE-DERIVED THE SCAN.  The count contract is
    unchanged for every existing caller — `detail` is opt-in and defaults off.
    This is the alternative to a second implementation of `should_keep`, whose
    docstring records two reverted attempts at exactly that.

    ⚑ THE BARREL REFUSAL IS RETURNED, NOT JUST PRINTED, when detail=True: a
    census that silently reported a refused barrel as "0 unused" would be a false
    zero of exactly the kind this repo keeps paying for.  Refused barrels come
    back as the sentinel `_BARREL` so the caller must decide what to say.
    """
    # ⚑ `shared` is a pure function of `inherited` — hoisted to the caller so it
    # is computed ONCE per run, not once per import statement per file (it was
    # recomputed inside the statement loop below: O(files × imports) rebuilds of
    # the same dict).  Harmless at 20 leaves, not free at tree scale.
    if shared is None and inherited:
        shared=_shared_names(inherited)
    L=open(path).read().split("\n")
    hdr=next(i for i,l in enumerate(L) if l.startswith("module "))
    # tokens from the IMPORT LINES must not count as uses, or an import is
    # kept merely because another import mentions its module name (this kept a
    # bare Foundation.Fin alive next to its own `renaming` twin, reintroducing
    # the _≤_ ambiguity the prune exists to remove).
    # Exclude IMPORT STATEMENTS (head + their indented continuations) from the
    # use-scan: an import kept alive merely because another import mentions its
    # module name reintroduces the ambiguity this prune exists to remove.
    # Excluding all indented lines instead would drop definition CLAUSES and
    # under-count real uses.
    spans=_spans(L)
    skip={k for a,b in spans.items() if a>hdr for k in range(a,b)}
    # ⚑ SIBLING CLOSURE — the prune judged each file ALONE and the splitter did
    # not, which is why passing --demand-from REGRESSED 20/20 to 13/20.
    #
    # `Perms` needs `Foundation.Vec` but names none of Vec's uniquely-owned
    # {Vec, map, tabulate}: its `[]` in `perms zero = [] ∷ []` is Vec's, at type
    # `Perm zero`, and `[]` is shared with List so it is not evidence.  The
    # splitter keeps Vec because Perms imports the SIBLING `Perm`, whose body
    # `Perm n = Vec (Fin n) n` does name Vec (split_lemmas:595, the closure
    # `need[fn] = direct ∪ ⋃ need[sibs]`).  Reading the file alone cannot see
    # that; reading its siblings' bodies can.
    #
    # So: fold every sibling leaf's tokens into this file's token set.  A
    # sibling is a leaf in the SAME directory that this file imports.  This is
    # keep-biased (strictly more tokens ⇒ strictly fewer drops) and it makes the
    # post-hoc prune agree with the splitter instead of competing with it.
    sib_toks=set()
    _dir=os.path.dirname(os.path.abspath(path))
    for k in sorted(skip):
        m2=IMP.match(L[k])
        if not m2: continue
        sib=os.path.join(_dir, m2.group(2).rsplit(".",1)[-1] + ".agda")
        if os.path.abspath(sib)==os.path.abspath(path) or not os.path.isfile(sib):
            continue
        S=open(sib).read().split("\n")
        try: shdr=next(i for i,l in enumerate(S) if l.startswith("module "))
        except StopIteration: continue
        sskip={q for a,b in _spans(S).items() if a>shdr for q in range(a,b)}
        sbody=agda_lex.mask_comments(
            "\n".join(S[q] for q in range(shdr+1,len(S)) if q not in sskip)).replace("\n"," ")
        sib_toks|=set(re.findall(r"[^\s(){}\[\];,]+",sbody))
    # ⚑ MASK COMMENTS BEFORE TOKENIZING.  `split_lemmas` PRESERVES each unit's
    # comment block and attaches it to the leaf, so prose lands in the token
    # set by construction — a comment reading "-- the Vec version of this"
    # keeps Foundation.Vec alive forever.  This file masked nothing; agda_defs
    # masked line comments only.  One authority now, applied here.
    # ⚑ THE MODULE HEADER'S TELESCOPE IS A USE SITE, and this started at hdr+1.
    # `module M (n : ℕ) where` needs whatever binds `ℕ`, but the header line was
    # EXCLUDED from the body, so the import providing it read as unused and was
    # dropped — leaving a file whose own header is [NotInScope].
    # MEASURED: `Groups/Coxeter/Cyclic/InvCanonical.agda:19` is
    # `module … (n : ℕ) where`; a prune removed `Foundation.Nat.Nat` and broke it,
    # along with 4 APPLIED imports (`… .Left n`) that pass the telescope's binder.
    # A parameterized header can also SPAN lines, so take the whole header span,
    # not just its first line (`agda_lex.module_scopes` knows where it ends).
    body=agda_lex.mask_comments(
        "\n".join(L[k2] for k2 in range(hdr,len(L)) if k2 not in skip)).replace("\n"," ")
    # An APPLIED import's ARGUMENTS are real uses (`… ExtrudeCoEmitMonad ℕ`
    # needs Foundation.Nat).  Skipping the whole import line lost them and
    # pruned the module that binds the argument.
    for k2 in sorted(skip):
        m2=IMP.match(L[k2])
        if not m2: continue
        rest=L[k2][m2.end():]
        rest=re.split(r"\b(using|renaming|hiding|public)\b",rest)[0]
        body+=" "+rest
    # ⚑ THE THREE TOKENIZER RECOVERIES MOVED TO `agda_lex.body_tokens` — the qualified
    # HEAD (`Magma._·_` → `Magma`, load-bearing: measured 4088 → 4104 drops without it,
    # all 16 extra false), the standalone punctuation RUN (` , `, without which `_,_`
    # read as dead and the import was dropped), and the verbatim BRACKET-MIXFIX scan
    # (`[_,_]`, without which a correct sibling edge was deleted).  Each incident is
    # recorded at the authority.
    #
    # ⚑⚑ HOISTED BECAUSE `agda_defs --clause-audit` WAS WRITTEN WITHOUT THEM AND
    # IMMEDIATELY REPRODUCED THE `_,_` BUG — reporting a LIVE import as UNUSED at
    # `Quotient/CRT.agda:36` while it is used at :83 and :85.  This file carried all
    # three fixes with their measurements written down, in a file the second author
    # read; documentation in one place is not the same as one implementation.
    toks = agda_lex.body_tokens(body, _mixfix_names())
    # ⚑ SECTION RECONSTRUCTION — the H2 fix, which this tool never had.  An Agda
    # operator is written `_⊔_` at its definition but BARE (`ℓ₁ ⊔ ℓ₂`) at an
    # infix use, so the body yields `⊔` and never `_⊔_`; the def-index holds the
    # underscore form, the two never meet, and the providing import reads as DEAD.
    # MEASURED: the Foundation.Sum split's `Sum` leaf uses `⊔` in `_⊎_`'s type;
    # this prune dropped `Foundation.Level` and the leaf failed [NotInScope] `⊔`
    # in the full build — AFTER passing isolate-check with the import still there.
    # Cover all three sections (infix `_x_`, prefix `x_`, postfix `_x`), exactly
    # as split_lemmas does. Keep-biased: adds tokens, so it can only prevent drops.
    toks |= {f for t in list(toks) for f in ("_" + t + "_", t + "_", "_" + t)}
    toks|=sib_toks   # the closure (above): a sibling's demand is this leaf's demand
    out=[];i=0;dropped=0;drops=[]
    while i<len(L):
        m=IMP.match(L[i])
        if not m: out.append(L[i]); i+=1; continue
        # the DELETE path — the dangerous copy.  Span from the authority, so a
        # dead import inside a nested `module M where` cannot take the
        # following definitions with it (F17, measured live in 14 statements).
        j=spans.get(i, i+1)-1
        stmt=L[i:j+1]; txt=" ".join(stmt); mod=m.group(2)
        # ⚑ Ⓠ5ᵇ: `body` carries the QUALIFIED use sites (`Q.name`), which the token
        # set cannot represent — `body_tokens` splits on the dot, so `V4.·` becomes
        # two tokens and the alias link is lost. The raw text is the only place the
        # evidence survives.
        keep=should_keep(mod, txt, toks, idx, prov_cache, inherited, shared,
                         body_text=body)
        if keep: out.extend(stmt)
        else:
            dropped+=1
            drops.append((i+1, mod))
        i=j+1
    # ⚑ PLAN, then APPLY.  This used to write unconditionally and return only a
    # count: untestable without side effects, and a bad run corrupted the tree
    # with no rollback (the decision was made and the damage written before any
    # verification could run).  `apply=False` makes the decision inspectable.
    # ⚑ NEVER GUT A PURE AGGREGATION BARREL.  A module whose body is EMPTY —
    # nothing but a header and imports — exists to aggregate its leaves, so by
    # construction no name it imports appears in a body that does not exist.
    # Liveness-by-token-use is the wrong question there and answers "drop
    # everything".  MEASURED: `Groups/Coxeter/Cyclic/InvCanonical.agda` is a
    # header plus 4 applied leaf imports and ZERO body lines; a prune removed
    # all of them and left a module that aggregates nothing.
    if dropped and not any(
            l.strip() and not IMP.match(l) and not l.startswith("module ")
            and not l.lstrip().startswith(("{-", "--", "open ", "import "))
            for l in agda_lex.mask_comments("\n".join(L)).split("\n")[hdr+1:]):
        if detail:
            return [_BARREL]
        print(f"   · {path}: pure aggregation barrel (no body) — REFUSING to prune "
              f"{dropped} import(s); liveness-by-use cannot judge a module with no body")
        return 0
    if apply:
        open(path,"w").write("\n".join(out))
    return drops if detail else dropped

def _selftest():
    """Unit-test the DECISION alone — no files, no Agda, milliseconds.

    Each case is a measured regression from this arc.  The A1 dead store (the
    shared-name subtraction computed then overwritten by the full demand set)
    is caught by `shared_names_are_not_evidence`: with the full set the probe
    hits `[]`/`∷` and keeps; with the subtraction it has no evidence and must
    still keep — but for the RIGHT reason (empty uniq), not by accident.
    """
    idx={"Vec":{"Substrate.Foundation.Vec"},"List":{"Substrate.Foundation.List"}}
    cache={}
    inherited={"Substrate.Foundation.Vec":{"Vec","[]","_∷_","map","tabulate"},
               "Substrate.Foundation.List":{"List","[]","_∷_","_++_"}}
    shared=_shared_names(inherited)
    assert shared=={"[]","_∷_"}, shared
    fails=[];ran=0
    def check(name,got,want):
        # ⚑ COUNT the cases rather than hardcoding the total in the summary — a
        # hardcoded "9/9" reported success unchanged when a 10th case was added,
        # so a new regression test looked like it had not run.
        nonlocal ran
        ran+=1
        if got!=want: fails.append(f"{name}: got {got}, want {want}")

    # A1/F30 — THE dead-store regression.  `[]`/`∷` are shared, so they are NOT
    # evidence for Vec.  Under the dead store (full demand set restored) the
    # probe hits {'[]','∷'} and KEEPS — that is the ConcatMapL bug, a dead Vec
    # retained into an [AmbiguousName].  Under the subtraction uniq(Vec) =
    # {Vec,map,tabulate}, none present, so the decision is DROP.
    # ⚑ This asserts False deliberately: on the file's OWN tokens the rule drops,
    # and that is right for ConcatMapL and WRONG for Perms.  What separates them
    # is not this function — it is the caller's SIBLING CLOSURE (next case).
    toks={"[]","∷","concatMapL","List"}
    check("shared_names_are_not_evidence",
          should_keep("Substrate.Foundation.Vec","open import Substrate.Foundation.Vec",
                      toks,idx,cache,inherited,shared), False)
    # Perms: identical own-tokens, but the sibling `Perm` body contributes `Vec`.
    # With the closure folded in, the same rule now KEEPS — the measured
    # difference between the 13/20 regression and 20/20.
    check("sibling_closure_supplies_evidence",
          should_keep("Substrate.Foundation.Vec","open import Substrate.Foundation.Vec",
                      toks|{"Vec","Fin"},idx,cache,inherited,shared), True)
    # ...but List IS discriminated: `_++_` is uniquely List's.
    check("unique_name_is_evidence",
          should_keep("Substrate.Foundation.List","open import Substrate.Foundation.List",
                      {"_++_","xs"},idx,cache,inherited,shared), True)
    # A dead import with a discriminating name absent ⇒ drop.
    check("discriminating_name_absent_drops",
          should_keep("Substrate.Foundation.List","open import Substrate.Foundation.List",
                      {"foo","bar"},idx,cache,inherited,shared), False)

    # ── Ⓠ5ᵇ: an ALIASED import is DECIDABLE, not automatically kept ────────
    # ⚑ `import M as Q` used to return KEEP without looking, because a `Q.name`
    # use site is invisible to the token probe (`body_tokens` splits on the dot,
    # so `V4.·` becomes two tokens and the alias link is lost). Right for the
    # WRITE path; it made the whole class UNMEASURABLE — 857 aliased imports
    # tree-wide outside the census, including 272 in `ExtrudeCoEmitGraded` that
    # `--alias-trace` reports as `used: []`.
    # The evidence is in the RAW TEXT, which is why `body_text` exists.
    check("aliased_import_with_a_qualified_use_is_KEPT",
          should_keep("Substrate.Foundation.Vec",
                      "import Substrate.Foundation.Vec as V",
                      set(),idx,cache,inherited,shared,
                      body_text="f xs = V.map g xs"), True)
    check("⚑ aliased_import_with_NO_qualified_use_is_DROPPABLE",
          should_keep("Substrate.Foundation.Vec",
                      "import Substrate.Foundation.Vec as V",
                      set(),idx,cache,inherited,shared,
                      body_text="f xs = map g xs"), False)
    # ⚑ THE ALIAS IS NOT A SUBSTRING SEARCH. `V.` occurs inside a module PATH
    # (`Substrate.V.Thing`) and inside another alias (`XV.map`); `_alias_pattern`
    # excludes a preceding word char or dot for exactly this reason.
    check("a longer alias sharing the prefix is not mistaken for a use",
          should_keep("Substrate.Foundation.Vec",
                      "import Substrate.Foundation.Vec as V",
                      set(),idx,cache,inherited,shared,
                      body_text="f xs = XV.map g xs"), False)
    # ⚑ KEEP-BIASED STILL: no body text ⇒ no evidence ⇒ keep. A caller that
    # cannot supply the text must not have its imports dropped by that omission.
    check("no body text ⇒ keep (the omission must not decide a drop)",
          should_keep("Substrate.Foundation.Vec",
                      "import Substrate.Foundation.Vec as V",
                      set(),idx,cache,inherited,shared), True)
    # A3: empty uniq must KEEP, never fall through to the provision index.
    inh2={"Substrate.Foundation.Vec":{"[]","_∷_"}}          # all shared with List
    sh2=_shared_names({**inh2,"Substrate.Foundation.List":{"[]","_∷_"}})
    check("empty_uniq_keeps",
          should_keep("Substrate.Foundation.Vec","open import Substrate.Foundation.Vec",
                      {"zzz"},idx,cache,inh2,sh2), True)
    # Uncertain branches all keep.
    check("renaming_untouched",
          should_keep("Substrate.X","open import Substrate.X renaming (a to b)",
                      set(),idx,cache,inherited,shared), True)
    check("non_substrate_untouched",
          should_keep("Agda.Primitive","open import Agda.Primitive",
                      set(),idx,cache,inherited,shared), True)
    check("unknown_provision_keeps",
          should_keep("Substrate.Unknown","open import Substrate.Unknown",
                      set(),idx,cache,None,None), True)
    # B3: the qualified-use first-segment fold is LOAD-BEARING (see the ⚑ at the
    # tokenizer).  A record is both a module and a definition, so `Magma._·_`
    # must register as evidence for `Substrate.Algebra.Magma`.  Removing the fold
    # was measured to cause 16 false-positive drops across 15 files; this pins it.
    _qtoks={"Magma._·_"}
    _qtoks|={t.split(".")[0] for t in list(_qtoks) if "." in t}
    check("qualified_use_is_evidence",
          should_keep("Substrate.Algebra.Magma","open import Substrate.Algebra.Magma",
                      _qtoks,idx,cache,None,None), True)
    # B2: a multi-hole operator must be found by its SEGMENTS.
    inh3={"Substrate.M":{"if_then_else_"}}
    check("multihole_operator_found",
          should_keep("Substrate.M","open import Substrate.M",
                      {"if","then","else","b"},idx,cache,inh3,_shared_names(inh3)), True)
    if fails:
        for f in fails: print("FAIL",f)
        return 1
    print(f"prune_imports selftest: {ran}/{ran} OK")
    return 0


if __name__=="__main__":
    import agda_imports as _ai
    # ⚑ Ⓠ13: THIS SENTENCE WENT HALF-FALSE AND KEPT PRINTING ON EVERY RUN.
    # It said "refuses renaming/as imports BY DESIGN". `renaming` is still refused
    # (pinned by the `renaming_untouched` case). `as` is NOT, since Ⓠ5ᵇ: an
    # aliased import is now DECIDED — kept when a `<alias>.name` site exists in the
    # body, dropped when none does — because `agda_defs._alias_refs` can read
    # exactly those sites. A tool that misdescribes its own behaviour is the shape
    # this repo keeps paying for, and this one announces itself on every
    # invocation, so the false half had maximum reach.
    print(_ai.stage_warning('prune_imports',
                            'It refuses `renaming` imports BY DESIGN and assumes a rewire has already widened the imports. '
                            '`as` imports ARE decided (Ⓠ5ᵇ): kept when a `<alias>.name` use site exists, dropped when none does.',
                            'stage 5, after the rewire'))

    # --demand-from <path-or-git-rev:path>  (F30): the MONOLITH these leaves
    # were split out of, read from git if it is already deleted on disk.  Its
    # pre-strip `using` lists disambiguate two overlapping bare imports that no
    # token scan can separate.  Optional: without it, behaviour is unchanged.
    argv=sys.argv[1:]; inherited=None
    if "--selftest" in argv: sys.exit(_selftest())
    # ⚑ WRITE IS OPT-IN, like every sibling.  This comment used to claim it
    # "mirrors fix_stale_using's --apply shape" while doing the OPPOSITE: the
    # flag was `--dry-run` and the DEFAULT WAS TO WRITE.  Measured cost, on the
    # author of the finding that flagged the divergence: a bare invocation
    # intended as a preview deleted 12 import lines from a file.  Seven sibling
    # write tools (split_lemmas, split_pipeline, capstone_to_dir,
    # rename_at_source, drop_dead_renames, fix_stale_using, …) all gate on
    # `--apply`; this was the ONE outlier, and an inverted flag is exactly the
    # kind of thing a reader confirms by analogy and gets wrong.
    # `--dry-run` still parses (and is now redundant) so old invocations that
    # asked for a preview still get one.
    apply="--apply" in argv
    argv=[a for a in argv if a not in ("--dry-run","--apply")]
    if "--demand-from" in argv:
        k=argv.index("--demand-from"); ref=argv[k+1]; del argv[k:k+2]
        sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
        import split_lemmas as SL, subprocess
        if os.path.isfile(ref):
            src=open(ref).read().split("\n")
        else:
            src=subprocess.run(["git","show",ref],capture_output=True,text=True).stdout.split("\n")
        # ⚑ STATEMENT-AWARE, not heads-only.  `[l for l in src if IMP.match(l)]`
        # keeps the head and DROPS every indented `using (…)` continuation — and
        # the using-list is the entire content `capture_demand` exists to read,
        # so a wrapped one silently contributed NOTHING to the demand map.  This
        # is the same defect split_lemmas.parse documents at its own line 98.
        imports=[]
        for st in agda_lex.group_statements(src, SL._opens):
            imports.extend(st)
        inherited=SL.capture_demand(imports)
    # ⚑ A DIRECTORY EXPANDS TO ITS .agda FILES.  This took files only, so a
    # cluster-wide prune had to be a shell `xargs` fan-out — a composition the
    # structural-query rule forbids (one-off approval, capability never
    # accumulates), and the census counterpart (`agda_defs --unused-imports`)
    # already accepted a directory.  A writer that cannot take the same argument
    # as its own census forces the operator to compose in the shell.
    _expanded=[]
    for a in argv:
        if os.path.isdir(a):
            _expanded.extend(agda_lex.agda_files(a))
        else:
            _expanded.append(a)
    argv=_expanded
    idx=def_index(); cache={}
    # hoist: pure in `inherited`, so compute once for the whole run (A2).
    shared=_shared_names(inherited) if inherited else None
    # ⚑ ONE ACT: the contract consulted where the snapshot is taken, and NOT under
    # `if apply:`.  The guard this replaces was already WELL PLACED for its own
    # question — it covered the whole expanded file list, before any write, which is
    # more than most sites in this census manage. What it could not do is see the
    # UNSTATED case: it was reached only once `apply` was already True (bound at
    # :494), so a bare invocation walked straight past it and printed "would drop".
    # ⚑ IT SITS HERE, NOT AT :494 BESIDE THE DECISION, BECAUSE `paths` IS NOT KNOWN
    # THERE.  Directory arguments expand to `.agda` files at :519-525, and a snapshot
    # handed a DIRECTORY reaches no untracked leaf inside it — so gating at the
    # decision would state the intent correctly and record the wrong set. This is the
    # earliest point where both halves are answerable, which is what "one act"
    # requires; the two lines between are a pure read.
    import edit_snapshot
    edit_snapshot.require_at_entry(f"prune_imports ({len(argv)} file(s))",
                                   argv=list(sys.argv), paths=argv)
    for f in argv:
        n=prune(f,idx,cache,inherited,shared,apply)
        print(f"{n:3d} {'would drop' if not apply else 'dropped   '}  {f}")
