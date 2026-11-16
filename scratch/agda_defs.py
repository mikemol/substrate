#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Shared definition index: name -> [module], over agda/Substrate.

Indexes top-level definitions, `data`/`record` heads, their CONSTRUCTORS
(indented under a data head), and `pattern` synonyms.  Operator names are
recorded both as written (`_⁻¹`) and bare (`⁻¹`), since a use site spells
the bare form.

ALSO the module IMPORT-EDGE authority (`import_index` and friends): who imports
whom, in both directions, plus the leaf/hub/spine measurement over a subtree.
See `import_index`'s note for why that lived in six private copies and could not
be ASKED."""
import re,glob,collections,functools,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import agda_lex
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive
# ⚑ ⟡vfs-chokepoints — the ONE read seam over the working tree AND git history.
# `at_revision` was PROMOTED onto it (see its docstring for the five subprocess
# hardening gaps this deletes by construction).  Spelled `_vfs` to match this file's
# `_o`/`_s` private-alias convention and to stay clear of any local `vfs` binding.
import vfs as _vfs

AG="agda"

@functools.lru_cache(maxsize=1)
def collide(name):
    """Ⓠ9 — every module defining `name`, SPLIT BY KIND. The repo is one namespace.

    ⚑ A COLLISION *IS* A MISNAMING once the whole repo is read as a single
    namespace, and the count of consumers that currently trip over it is a fact
    about TODAY'S IMPORT GRAPH, not about the names. `_·_` has 21 providers; only
    one pair had been co-imported into a scope that used both, and I argued from
    that one instance that the names were "each correct in their own module".
    That is cost-as-correctness — letting blast radius decide the diagnosis.

    ⚑ BUT THE KINDS ARE NOT ALIKE, AND THAT IS WHAT THIS MODE EXISTS TO SHOW.
    A RECORD FIELD (`Magma._·_`) is legitimately generic: it is the algebraic
    structure's operation, reached through its record, and every instance of that
    structure shares the spelling BY DESIGN. A TOP-LEVEL operator on a concrete
    carrier (`Groups.V4.Operations._·_ : V₄ → V₄ → V₄`) merely BORROWED the
    spelling. Rename-at-source applies to the second kind; the first is the name's
    rightful home. Reporting them under one count would make 21 look like 21
    equal offences and invite renaming the one definition that should keep it.
    """
    idx = def_index()
    homes = sorted(idx.get(name, ()))
    fields, tops = [], []
    for mod in homes:
        p = os.path.join(AG, mod.replace(".", "/") + ".agda")
        try:
            lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
        except OSError:
            continue
        # the field authority, not a re-derivation (`split_lemmas.field_names`
        # knows constructors and indented record bodies; a col-0 scan does not)
        try:
            import split_lemmas as _sl2
            is_field = name in _sl2.field_names(lines)
        except Exception:
            is_field = False
        (fields if is_field else tops).append(mod)
    return {"name": name, "field": fields, "toplevel": tops}


#: Process-local memo for `def_index` / `_provides_index`, and the tree-state stamp
#: they were built from.  ⚑ NOT `functools.lru_cache`: this must be INVALIDATABLE by
#: a caller that has just written a `.agda` file, and an lru_cache on a zero-arg
#: function is a cache with no key and no way to express staleness.
_DEF_INDEX = None
_PROVIDES_INDEX = None


def invalidate_def_index():
    """Drop the memo. ⚑ THE MUTATE-THEN-READ CONTRACT, and it is the whole risk.

    `def_index()` is a pure function of the `.agda` files on disk, so memoising it
    within a process is safe for a READER.  It is NOT safe for a codemod that writes
    a file and then re-reads the index expecting to see its own edit — a stale index
    handed to a repair tool is the dangerous direction, because it makes a live
    provision read as absent and `prune_imports` DELETES on that reading (five
    measured [NotInScope] incidents in this file's own comments).

    ⚑⚑ MEASURED BEFORE CACHING, NOT ASSUMED: of the 37 call sites
    (`pycodemod --calls def_index`), the writers were checked for a re-read AFTER
    their write.  Every one of them builds its index ONCE, up front, computes the
    whole edit plan from it, and then writes — the read and the write do not
    interleave.  So no shipped caller changes behaviour under this memo.  This
    function exists so that a FUTURE caller that does interleave has a way to say
    so, rather than discovering the staleness as a deleted import.

    ⚑⚑ ZERO CALLERS BY DESIGN, AND THIS REPO DELETES ON `--dead`.  `pycodemod
    --calls invalidate_def_index` reports `1 def, 0 calls, ⚑ DEAD CAPABILITY` — the
    `rewire_only` shape.  It is NOT that defect: `rewire_only` was a capability whose
    dispatch branch was forgotten, while this is an escape hatch that is uncalled
    PRECISELY BECAUSE the memo it releases is currently safe for every shipped caller.
    A sweep acting on the count alone would remove the only way to express staleness
    at the moment a caller first needs it.  ⚑ THE COUNT GOING TO 1 IS THE SIGNAL THAT
    A WRITER STARTED INTERLEAVING — it is a tripwire, and a tripwire nobody has
    stepped on reads identically to dead code.

    ⚑ THE STRUCTURAL CORROBORATION, not an assumption: `pycodemod --guarded
    def_index` shows `fix_stale_using.py:162` and `hoist_telescope_imports.py:71`
    ALREADY hand-roll this exact memo (`if _DEFIDX is None`).  Two independent
    callers arrived at per-process caching on their own, which is evidence the
    contract was already in force informally; this makes it the authority's, and
    their private caches redundant rather than conflicting.
    """
    global _DEF_INDEX, _PROVIDES_INDEX
    _DEF_INDEX = None
    _PROVIDES_INDEX = None


def def_index():
    """name -> [module], memoised per process. See `invalidate_def_index`.

    ⚑ MEASURED 2026-08-25: uncached, this is a full walk of all 3598 files at
    ~0.7s, and `provides()` called it PER CLAUSE ENTRY — so `clause_audit` paid
    ~8 complete tree walks per file, which is the 6.7 s/file that projected the
    blocking gate to 6.7 HOURS of CPU.
    """
    global _DEF_INDEX
    if _DEF_INDEX is None:
        _DEF_INDEX = _def_index_uncached()
    return _DEF_INDEX


def _def_index_uncached():
    defs=collections.defaultdict(set)
    for p in glob.glob(f"{AG}/Substrate/**/*.agda",recursive=True):
        mod=module_path(p, AG)
        in_data=False; in_module=False; in_opaque=False
        for l in open(p,errors="replace"):
            if not l.strip() or l.lstrip().startswith("--"): continue
            # A `data`/`record` head may be INDENTED inside a parameterized
            # `module _ (…) where` (the ⟡set1-paydown idiom).  Anchoring at
            # column 0 missed those heads AND their fields entirely — measured:
            # Wedge.Graded provided neither GradedDivStr nor `recon`, so
            # prune_imports read the import as dead and dropped it.
            m=re.match(r"^\s*(data|record)\s+([^\s({]+)",l)
            if m:
                _add(defs,m.group(2),mod); in_data=True; in_module=False; continue
            m=re.match(r"^pattern\s+(\S+)",l)
            if m: _add(defs,m.group(1),mod); continue
            # An `opaque` BLOCK's members are ordinary TOP-LEVEL EXPORTS — the
            # keyword seals their DEFINITIONS from reduction, it does not make
            # them private.  But they are indented, so the col-0 signature
            # branch below never saw them and the module read as providing
            # NOTHING.  prune_imports then dropped a live import and the
            # consumer lost the name.
            # MEASURED: `Linear/FromImages.agda:168` seals `linear-from-images`
            # inside `opaque`; the prune dropped its import from FIVE consumers
            # (Hamming/H-7-4-3, ReedMuller/RM-1-3, HodgeDim3/ChiralityAxis,
            # HodgeDim3/V4Plane, WitnessTower/Codeword), each then
            # `[NotInScope]`.  26 files tree-wide open an `opaque` block, so
            # this hid a class.
            # ⚑ The cap-paydown work SEALS heavy neutrals `opaque` on purpose
            # (⟡cap-384), so this class GROWS as the queue advances — the fix
            # belongs in the index, not in a per-consumer exemption.
            if re.match(r"^opaque\s*$",l):
                in_opaque=True; in_data=False; in_module=False; continue
            # A record's `constructor _,_` line has no `:`, so neither the
            # top-level nor the in_data branch saw it — Foundation.Product then
            # provided no `_,_`, and prune_imports dropped the import of the very
            # module supplying the pair constructor (measured: `,` NotInScope).
            m=re.match(r"^\s*constructor\s+(\S+)",l)
            if m: _add(defs,m.group(1),mod); continue
            # A SUBMODULE is a name the file provides: `open M`'s binder is
            # the import that carries it (S3's `open WithAction` is bound by
            # the SemidirectProductGroup import).  Without this the topo sort
            # sees no edge and leaves the open above its binder.
            m=re.match(r"^\s*module\s+([^\s({]+)",l)
            if m and "." not in m.group(1):
                _add(defs,m.group(1),mod)
                # A col-0 `module X where` body is EXPORTED (the repo idiom is
                # `open X public`), so its shallow definitions are provisions of
                # this file.  Missing them made an import that supplies ONLY such
                # a name read as dead — prune then dropped it and the consumer
                # lost the name (measured: `signW`, in
                # OrientationRigCatPermSign's `module Reduction`).
                in_module = not l[0].isspace(); in_data=False
                continue
            # MULTI-NAME signature: `∂x ∂y ∂z : MPoly → MPoly` declares THREE
            # definitions.  Matching only the first token before `:` failed the
            # whole line (the tokens between are not `:`), so none of the three
            # was indexed and prune_imports dropped the module that provides
            # them (measured: `∂x` NotInScope).  The in_data branch below already
            # split on whitespace; the top level must too.
            m=re.match(r"^([^\s:()@{}]+(?:\s+[^\s:()@{}]+)*?)\s*:(?!:)",l)
            if m:
                for nm in _namelist(m.group(1)): _add(defs,nm,mod)
                in_data=False; in_module=False; continue
            if in_data and l.startswith(" "):
                m=re.match(r"^\s+([^\s:()@{}]+(?:\s+[^\s:()@{}]+)*?)\s*:(?!:)",l)
                if m:
                    # ⚑ A MULTI-NAME SIGNATURE IS ALL IDENTIFIERS; A TYPE IS NOT.
                    # `field a b c d : ℕ` and `Z₂ Z₃ Z₄ : ZnInstance` declare several
                    # names.  But a CONSTRUCTOR whose type contains a colon further
                    # right — `is-zero : value b ≡ zero → Trimmed b`, and worse, its
                    # CONTINUATION lines (`→ msb t ≡ true`) — also matches, and the
                    # whitespace split then indexed every token of the TYPE as a
                    # definition.  Measured: `≡` was credited to BinTrim.Trimmed,
                    # BoundaryEvent and FUSepConvSharpen — three modules that merely
                    # USE it — which made `fix_notinscope` refuse `≡` as ambiguous
                    # even though Foundation.Eq was also (correctly) a candidate.
                    #
                    # Reject the group if ANY token is not identifier-shaped: an
                    # arrow, an operator section, or a literal means this is a type,
                    # not a name list.  Keeps all 74 genuine multi-name signatures in
                    # the corpus (`field a b c d : ℕ`) and drops the type-expression
                    # matches.  Keep-biased: a rejected group indexes NOTHING extra,
                    # and the single-name case below is unaffected — a DROP is the
                    # dangerous direction here (it makes prune_imports read a live
                    # import as dead: three measured [NotInScope] incidents).
                    for nm in _namelist(m.group(1)): _add(defs,nm,mod)
                continue
            # SHALLOW submodule body only (≤2 spaces): deeper indentation is a
            # definition's own `where`-locals, which are NOT provisions.
            if in_module:
                m=re.match(r"^(\s{1,2})([^\s:()@{}]+)\s*:(?!:)",l)
                if m: _add(defs,m.group(2),mod); continue
            # `opaque` body: same SHALLOW rule as a submodule body — a member
            # sits at ≤2 spaces; anything deeper is that member's own
            # `where`-locals or a record literal's fields, neither a provision.
            # Multi-name signatures split on whitespace, as at top level.
            if in_opaque:
                m=re.match(r"^(\s{1,2})([^\s:()@{}]+(?:\s+[^\s:()@{}]+)*?)\s*:(?!:)",l)
                if m:
                    for nm in _namelist(m.group(2)): _add(defs,nm,mod)
                    continue
            if l and not l[0].isspace(): in_data=False; in_module=False; in_opaque=False
    return {k:sorted(v) for k,v in defs.items()}

_IDENT=re.compile(r"[^\s:()@{}→←⊔⟨⟩\[\],;=|]+")

# ⚑ AGDA KEYWORDS THAT CAN PRECEDE A SIGNATURE — they are identifier-SHAPED, which is
# why `_IDENT` admits them, and they are not names anything can import.  Scoped
# deliberately to the modifier position: this is NOT a full keyword table (`where`,
# `data`, `record`, `module` are consumed by their own branches above and never reach
# `_namelist`), and widening it speculatively would risk dropping a real provision —
# the direction this file records three [NotInScope] incidents for.
#
# ⚑ MEASURED, NOT ENUMERATED FROM THE GRAMMAR: `private` and `variable` are the two
# that actually appeared, via `private variable a b c : Level`.  `abstract`,
# `instance` and `overlap` take the same position and are included because they are
# the same construct; anything beyond that should be added when a case shows up.
_KEYWORDS = {"private", "variable", "abstract", "instance", "overlap",
             "postulate", "field", "syntax", "infix", "infixl", "infixr"}

def _namelist(group):
    """The names a `a b c : T` signature declares — [] if `group` is a TYPE.

    ⚑ A MULTI-NAME SIGNATURE IS ALL IDENTIFIERS; A TYPE IS NOT.  `field a b c d : ℕ`
    and `Z₂ Z₃ Z₄ : ZnInstance` declare several names (74 such in the corpus).  But
    the same regex matches a CONSTRUCTOR whose type contains a colon further right —
    `is-zero : value b ≡ zero → Trimmed b` — and its CONTINUATION lines, and the
    whitespace split then indexed every token of the TYPE as a definition.
    MEASURED: `≡` was credited to BinTrim.Trimmed, BoundaryEvent and
    FUSepConvSharpen — three modules that merely USE it — so `fix_notinscope`
    refused `≡` as ambiguous even though Foundation.Eq was correctly a candidate too.

    Reject the whole group if ANY token is non-identifier-shaped (an arrow, a
    bracket, an application): that means a type, not a name list.  KEEP-BIASED —
    a rejected group indexes nothing EXTRA, and single-name signatures are matched
    by other branches, so this cannot drop a provision.  A drop is the dangerous
    direction here: it makes `prune_imports` read a live import as dead, which has
    caused three measured [NotInScope] incidents.

    ⚑ ONE definition of "is this a name list", called from all three multi-name
    sites (top level, data body, opaque body).  They previously each inlined the
    split, which is how the same defect sat in three places.
    """
    names=group.split()
    # ⚑ THE "CANNOT DROP A PROVISION" CLAIM ABOVE IS FALSE FOR A SINGLE
    # BRACKET-MIXFIX NAME, AND IT DROPPED ONE TREE-WIDE.  The reasoning was that a
    # single-name signature is "matched by other branches" — but inside a `data`
    # body THIS is the only branch, and it rejects the whole group when any token
    # fails `_IDENT`.  `[]` and `[_]` fail it by construction (a bracket is exactly
    # what the filter treats as type-shaped), so `data List … where [] : List A`
    # indexed `List`, `_∷_`, `_++_`, `foldl`, `foldr` — and **never `[]`**.
    # MEASURED CONSEQUENCE: `def_index()["[]"]` was EMPTY tree-wide, so no tool
    # could resolve the name; the R9 split emitted
    # `Algebra/Nat/Prime/Properties/Product.agda` (`product-[] : product [] ≡ 1`)
    # with no import of `Foundation.List`, and it failed [NotInScope] `[]`.
    # A ONE-TOKEN GROUP IS A NAME, whatever its shape — there is no type to
    # confuse it with, because the multi-token case is the only one that was ever
    # ambiguous.  Keeps the type-rejection for `value b ≡ zero → Trimmed b`
    # (5 tokens) while restoring the constructors the filter was never meant to
    # catch.
    # ⚑⚑ A KEYWORD IS NOT A NAME, AND `private variable a b c : Level` INDEXED TWO.
    # `private` and `variable` are MODIFIERS that precede a signature, so the group
    # reaching here is `private variable a b c` — five identifier-shaped tokens, all
    # admitted.  MEASURED 2026-08-18: `--provides Substrate.Foundation.Eq.Preamble`
    # answered `a b c private variable`, 5 names, for a module whose only content is
    # three level variables.  A peer read that count as evidence in a hole census.
    #
    # (`_` is filtered at `_add`, the chokepoint every insertion site shares — see
    # there for why it cannot live here.)
    #
    # ⚑ STRIPPED, NOT REJECTED — the difference matters and the docstring above says
    # why.  Dropping the whole group is the dangerous direction (three measured
    # [NotInScope] incidents from a live import read as dead), so a leading modifier
    # removes ITSELF and leaves the real names indexed.  `private variable a b c`
    # still provides `a b c`; it simply stops also providing `private`.
    names=[n for n in names if n not in _KEYWORDS]
    if not names:
        return []
    if len(names)==1:
        return names
    return names if all(_IDENT.fullmatch(n) for n in names) else []


def _add(defs,name,mod):
    # ⚑⚑ `_` IS A PLACEHOLDER, NEVER A PROVISION — AND THE GUARD BELONGS HERE, at the
    # ONE chokepoint all eight insertion sites pass through, not in `_namelist`.
    # Filtering it there fixed the multi-name branch and left `Sheafify` still
    # reporting `_`, because an anonymous `_ : T` reaches the index by the SINGLE-name
    # branch, which never calls `_namelist`.  One rule, eight callers, one place — the
    # shared-name-not-shared-authority shape this file already records paying for.
    #
    # ⚑ AN ANONYMOUS DEFINITION IS REAL CODE (agda's idiom for a module-level
    # assertion) but it EXPORTS nothing: no consumer can import `_`, and nothing can
    # be [NotInScope] for it.  Indexing it made `--provides` report it as a module's
    # sole definition, which is what a hole census then acts on.
    if name == "_":
        return
    # Index a declared name under EVERY form a use site could present.
    # ⚑ Was `strip("_")`, correct only for two-hole operators: `if_then_else_`
    # used as `if b then x else y` presents {if,then,else}, which strip's
    # `if_then_else` never matches — so the provision set missed it and the
    # consumer's import read as dead.  `mixfix_forms` emits each non-hole
    # segment; it only ever ADDS index entries, so it is keep-biased.
    for p in agda_lex.mixfix_forms(name):
        defs[p].add(mod)

def provides(mod):
    """Names `mod` defines. O(1) after the first call — see the note below.

    ⚑⚑ MEMOISING `def_index` ALONE DOES NOT FIX THIS, and that is the half the
    diagnosis missed.  Even over a cached index this body was a SCAN of every
    (name, modules) pair — ~30k entries — once per clause entry.  The rebuild and
    the scan are two different costs and only the INVERSION removes the second.
    MEASURED (`scratch/bench_clause_audit.py --both`): the scan phase goes from
    6.71 s/file to 0.0013 s/file, and the projected full gate from 24,151s CPU
    (6.71 h) to ~12s.

    ⚑ THE INVERSE IS DERIVED FROM `def_index()`, never accumulated alongside it.
    A second structure filled in `_add` would be a second spelling of one relation
    — the `census-keyed-on-one-spelling` shape — and could drift from it silently.
    Here it cannot: it is a fold of the index, rebuilt whenever the index is.
    """
    global _PROVIDES_INDEX
    idx = def_index()
    if _PROVIDES_INDEX is None:
        inv = collections.defaultdict(set)
        for n, mods in idx.items():
            for m in mods:
                inv[m].add(n)
        _PROVIDES_INDEX = dict(inv)
    # ⚑ A COPY, because the old body returned a FRESH set every call and a caller
    # may mutate what it gets.  Returning the shared set would let one consumer's
    # `.add`/`.discard` silently rewrite the index for every later consumer — a
    # regression the speedup would have hidden.
    return set(_PROVIDES_INDEX.get(mod, ()))


def def_index_modules():
    """Every module the index SCANNED — the population `provides` asks about.

    ⚑ WITHOUT THIS, `provides` COULD NOT TELL "DEFINES NOTHING" FROM "IS NOT A MODULE".
    Both returned an empty set, so a mistyped name, a file PATH, and a genuinely empty
    module were one answer: `0 name(s)`.  A peer read four such zeroes as fact and
    retracted a CORRECT hole-census reading on the strength of them.  The distinction
    needs the population, and the population was never exposed — the same shape as a
    census that cannot say whether it looked.

    ⚑⚑ READ FROM THE FILE SET, NOT FROM THE INDEX'S VALUES — and deriving it from the
    values re-introduced the very bug this exists to fix.  A module that defines
    NOTHING contributes no entry, so `{m for mods in def_index().values() for m in
    mods}` cannot contain it, and `--provides` then REFUSED a real module as unknown.
    An empty module is exactly the case a hole census cares about, so the one answer
    that must stay distinguishable was the one that broke.  The scanned files are the
    honest population: it is what the index LOOKED AT, not what it FOUND.
    """
    return {module_path(p, AG)
            for p in glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)}


def grep_names(pattern, ignore_case=True):
    """Names in the index matching `pattern` (a regex), with their homes.

    ⚑ THE INDEX COULD ONLY BE ASKED A NAME IT ALREADY KNEW.  `agda_defs.py <name>`
    answers "where does THIS name live"; there was no way to ask "what names look
    LIKE this" — so every "does the tree have a projector / an isotypic
    decomposition / a Walsh character?" question fell out of the structural
    toolkit and into `grep` over sources (which the hook blocks) or `find` over
    FILENAMES (which sees only module names, never the defs inside them).
    MEASURED: a research pass looking for V₄ isotypic material could locate
    `WHTCharacterBridge` by filename but could not discover that its content is
    `χ`/`ChiralityIsWHTSelector`, nor rule on whether any `project`/`isotypic`
    def existed anywhere — the search had to be reported as method-limited.

    Returns a sorted list of (name, [modules]).  Absence here is a fact about
    THIS INDEX (top-level defs under agda/Substrate) — not about the tree.
    """
    rx = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
    idx = def_index()
    return sorted((n, mods) for n, mods in idx.items() if rx.search(n))


# ⚑ THE HYPHEN IS PART OF AN AGDA MODULE NAME, AND OMITTING IT SILENTLY TRUNCATED
# EDGES.  Agda identifiers admit `-`, and this tree uses it in module names
# (`Substrate.Algebra.N-to-F2-Parity`, `Substrate.Groups.V4-Coxeter-F2Graded`,
# `Substrate.Algebra.F2.Cone-Hamming-7plus1`).  Without `-` in the class this
# pattern stopped at the first hyphen, so `open import Substrate.Algebra.N-to-F2-Parity`
# recorded an edge to `Substrate.Algebra.N` — a module that does not exist.
#
# ⚑ IT FAILED SILENTLY IN THE DIRECTION THAT LOOKS LIKE ABSENCE.  MEASURED
# 2026-08-17: `--importers Substrate.Algebra.N-to-F2-Parity` returned **0 edges in**
# while `Substrate.Algebra.Wedge.ParityBridge:37` imports it in plain text.  A
# consumed-by query answering "nobody" for a module with real consumers is the
# `no consumer found` → `no consumer exists` collapse this repo's standing rule
# names — and it was in the EDGE AUTHORITY, which ~19 tools resolve through.
#
# Found by `--reexports`, whose dangling-target check reported the truncated name
# as a missing module; the mode was reading its own regex bug as a finding about
# the tree.  A truncation cannot be distinguished from a real absence downstream,
# which is why the class is fixed here rather than compensated in a caller.
# ⚑⚑ AND THE FIRST FIX WAS AN ENUMERATION, WHICH IS THE SAME DEFECT ONE SPAN WIDER.
# It read `[A-Za-z0-9_.'\-À-￿]+` — ASCII plus a hand-picked unicode range bolted on when
# `PriorAñelé` was measured.  That range begins at U+00C0, so the class still truncates
# every name below it, and each new offender would add another span.  A class that looks
# fixed because THE ONE MEASURED INSTANCE now passes is the `test written from the
# instance` shape the guard's own docstring records.
#
# `\w` is UNICODE-AWARE in Python, so `[\w.'-]+` is simultaneously correct, shorter, and
# not an enumeration — there is no next character to remember.  This is the spelling
# `tests/test_rederive_agreement.ImportNameCharClassTest` names.
_IMPORT = re.compile(r"^\s*(?:open\s+import|import)\s+([\w.'-]+)")

# ⚑ A MODULE APPLICATION — `open M args …`, with NO `import` keyword.  It is the
# SECOND way a name crosses a module boundary (`… public`), and `_IMPORT` cannot
# match it because there is nothing to import: `M` is already in scope and this
# instantiates it.  Deliberately a separate pattern rather than a widened
# `_IMPORT`: ~19 tools resolve edges through that one and an application is not
# an edge, so admitting it there would change what every one of them counts.
# ⚑ SAME ENUMERATION, ONE SPAN FURTHER ALONG: this one had `⟦⟧` bolted on after the
# `À-￿` range, because a bracket name appeared and the range did not reach it.  Two
# patches, same cause.  `\w` subsumes the letter spans; the brackets are PUNCTUATION and
# genuinely outside `\w`, so they stay named explicitly — that is a deliberate inclusion
# of two specific characters, not a guess at a letter range.
_OPEN_APPLY = re.compile(r"^\s*open\s+(?!import\b)([\w.'\-⟦⟧]+)")

# a `data`/`record`/`module` head declared in THIS file — the things an
# `open X public` can name without crossing a module boundary.
# ⚑ THE GUARD DOES NOT FLAG THIS LINE, AND IT CARRIES THE SAME DEFECT.  The test keys on
# an ASCII class within 40 characters of `import`; a declaration head has no `import`
# near it, so this site was invisible to the check that caught its two siblings — the
# guard's population is narrower than the defect's.  Fixed with them because the CLASS is
# what is wrong, not the sites that happened to be reachable.
# (No `.`: a head is unqualified — `module Foo.Bar where` is the FILE's own module line,
# which this pattern is not for.)
_LOCAL_HEAD = re.compile(r"^\s*(?:data|record|module)\s+([\w'-]+)", re.M)


@functools.lru_cache(maxsize=None)
def _local_defs(path):
    """Names this file declares as a data/record/module head.

    ⚑ THE DISCRIMINATOR FOR `open X public`.  Opening a locally-declared record
    exposes its fields; opening an imported module forwards someone else's
    names.  Only the second is a re-export, and the difference is not visible in
    the statement — it is a fact about where `X` was declared.
    """
    try:
        import agda_lex as _al
        src = _al.mask_comments(open(path, encoding="utf-8", errors="replace").read())
    except OSError:
        return frozenset()
    return frozenset(_LOCAL_HEAD.findall(src))


# ⚑ NAMES `def_index` ADMITS THAT ARE NOT CAPABILITIES — a filter at the POINT OF USE,
# not a change to the index.  MEASURED 2026-08-17: the first `--late-imports` census
# reported 212 rows, and roughly six in seven were rows like `Foundation.Eq.Preamble
# provides b` or `ObsBisim provides where`.  `Foundation/Eq/Preamble.agda` is eleven
# lines whose only content is `private variable a b c : Level`, and `--provides` reports
# it as defining FIVE names: `a`, `b`, `c`, `private`, `variable`.
#
# ⚑ SO THE DEFECT IS IN THE SHARED AUTHORITY, AND THIS IS THE LOCAL COMPENSATION.
# `def_index` is the name->home index ~19 tools resolve through; it reads a `variable`
# block's binders and the keywords opening a declaration as DEFINITIONS.  Fixing it there
# is the right repair (⟡Ⓣ12) and is NOT done here, because every consumer has been ranking
# against this index for the whole arc and a silent narrowing would move numbers nothing
# is watching.  Filed as debt, compensated where the noise is measured.
#
# ⚑ AND THE LENGTH RULE IS THE OTHER HALF.  A single-character name (`a`, `b`, `,`, `_`)
# matches somewhere in nearly every file, so it cannot witness anything: an import is
# reported late on the strength of a token that carries no identity.  Two characters is
# the shortest real name in this corpus (`≡` is one char but is caught as an OPERATOR
# spelling `_≡_`, which survives).
_NOT_A_CAPABILITY = frozenset({
    "where", "open", "import", "private", "public", "variable", "field",
    "module", "record", "data", "pattern", "postulate", "abstract", "instance",
    "mutual", "primitive", "infix", "infixl", "infixr", "syntax", "rewrite",
    "with", "let", "in", "do", "using", "renaming", "hiding", "constructor",
})


@functools.lru_cache(maxsize=None)
def _variable_binders(mod):
    """Names a module binds in a `variable` block — declared, never exported.

    ⚑ THE SECOND HALF OF THE `--late-imports` FALSE-POSITIVE CLASS.  `variable`
    binders are short and generic by convention (`a b c : Level`, `m n : ℕ`), so a
    use-site scan matches them in nearly every file above nearly every import.  They
    are also not capabilities: a consumer never imports a module FOR its `variable`
    block.  Read off the providing module's own source rather than guessed, because
    the names are arbitrary — `Foundation.Eq.Preamble` binds `a b c`, another module
    may bind `A B ℓ`.
    """
    p = os.path.join(AG, *mod.split(".")) + ".agda"
    if not os.path.exists(p):
        return frozenset()
    try:
        import agda_lex as _al
        src = _al.mask_comments(open(p, encoding="utf-8", errors="replace").read())
    except OSError:
        return frozenset()
    out = set()
    for m in re.finditer(r"^\s*(?:private\s+)?variable\b([^\n]*(?:\n[ \t]+[^\n]*)*)",
                         src, re.M):
        for grp in re.findall(r"([^:()\n]+):", m.group(1)):
            out.update(w for w in grp.split() if w not in ("private", "variable"))
    return frozenset(out)


# ⚑ THE FOURTH COPY OF `_IMPORT`'s CLASS, 110 LINES FROM IT, AND THE ONE THAT KEPT THE
# GUARD RED THROUGH THREE HAND PASSES.  `_IMPORT`, `_OPEN_APPLY`, `_LOCAL_HEAD` and this
# are four spellings of one capability, so a fix applied to the visible three left the
# file still failing and the operator still patching — `a shared NAME is not a shared
# authority, and a hand sweep is not a transform`, verbatim, in the module that says it.
# Same `[\w.'-]+` as its siblings; the trailing `([^\n]*)` tail capture is unchanged.
_APPLIED = re.compile(
    r"^\s*(?:open\s+import|import)\s+([\w.'-]+)([^\n]*)")


def lp_apply(prefix=None, apply=False):
    """[(path, index, qualifier, names)] — a file reaching `normalize` through a CONDUIT.

    ⚑⚑ ONE HIDDEN COUPLING, ~28 CONSUMERS, AND THE SAME REPAIR EVERY TIME.
    `Coxeter.Cyclic.Existential` opens `Coxeter.ListPresentation` WITHOUT naming
    it, so `normalize` / `normalize-canonical` / `normalize-distrib` / `WithLemmas`
    appear to come from Existential.  `--provides` shows the partition exactly:
    Existential exports six names, none of them these; ListPresentation exports
    these four and nothing else.

    ⚑ AND AGDA ONLY WARNS.  `Existential n using (normalize)` is a
    `ModuleDoesntExport` WARNING — the name binds nothing and the build fails at
    the far-away USE site, which is why every one of these was found by a compile
    rather than by reading the import.

    ⚑ THE REPAIR IS DECIDABLE, WHICH IS WHY IT IS A TRANSFORM AND NOT A JUDGEMENT.
    `ListPresentation` takes five arguments and each is available at the consumer:

        Gen · Canonical-ex · c-ε · insert · insert-canonical-ex

    `Gen`/`insert` come from `Cyclic.Base n`, the other three from
    `Cyclic.Existential n`, and BOTH are already imported by any file with this
    defect — at the same index `n`, which the file's own import supplies.  So the
    application is derivable from what the file already says; nothing is guessed.

    ⚑ THE INDEX IS THE KEY, AND A FILE MAY CARRY TWO.  `Actions/Z2-on-Z3/Act` uses
    Z₂ AND Z₃ normalisation; the single unqualified `normalize` was conflating two
    DIFFERENT instances of one construction.  Rows are therefore keyed on
    (path, index), and a two-index file yields two rows.

    Reports only where a qualified `<q>.normalize*` use exists whose qualifier is
    bound to `Cyclic.Existential <n>`; a bare (unqualified) use is a different
    shape — the file opened Existential without a qualifier — and is reported with
    qualifier `None` for the caller to handle, never silently rewritten.
    """
    import agda_lex as _al
    _LPN = {"normalize", "normalize-canonical", "normalize-distrib", "WithLemmas"}
    root = f"{AG}/Substrate"
    if prefix:
        root = os.path.join(AG, *prefix.split("."))
    pats = [f"{root}/**/*.agda"] + ([f"{root}.agda"] if prefix else [])
    out = []
    for p in sorted({q for pat in pats for q in glob.glob(pat, recursive=True)}):
        try:
            src = _al.mask_comments(open(p, encoding="utf-8",
                                         errors="replace").read())
        except OSError:
            continue
        # qualifier -> index, for both `import M n as Q` and `open import M n`
        qual, bare = {}, {}
        for m in re.finditer(r"^\s*import\s+Substrate\.Groups\.Coxeter\.Cyclic\."
                             r"(Existential|Base)\s+(\d+)\s+as\s+(\S+)", src, re.M):
            qual[m.group(3)] = (m.group(2), m.group(1))
        for m in re.finditer(r"^\s*open\s+import\s+Substrate\.Groups\.Coxeter\."
                             r"Cyclic\.(Existential|Base)\s+(\S+)\s*$", src, re.M):
            bare[m.group(1)] = m.group(2)
        # which indices does this file actually reach `normalize*` at?
        hits = {}
        for m in re.finditer(r"([A-Za-z0-9_'À-￿-]+)\.(normalize[A-Za-z-]*)", src):
            q, nm = m.group(1), m.group(2)
            if nm in _LPN and q in qual and qual[q][1] == "Existential":
                hits.setdefault(qual[q][0], set()).add(nm)
        # ⚑ ALREADY REPAIRED?  A file that applies ListPresentation at this index
        # is DONE, and must not be reported — the repair's own output would
        # otherwise read as outstanding work.  MEASURED: the first cut reported 8
        # already-green files among 14 "unqualified" rows, because its predicate
        # (a bare Existential open plus a bare `normalize`) is exactly the
        # CORRECT post-repair state.  A census that cannot see its own completion
        # reports paydown as debt.
        _has_lp = bool(re.search(r"^\s*(?:open\s+)?import\s+Substrate\.Groups\."
                                 r"Coxeter\.ListPresentation\b", src, re.M))
        for idx, names in sorted(hits.items()):
            # the qualifier bound to Existential at THIS index
            qs = [q for q, (i, k) in qual.items()
                  if i == idx and k == "Existential"]
            # ⚑ AND THE BASE QUALIFIER IS READ, NOT DERIVED.  The first cut
            # emitted `Z₂-Existential-Base.Gen` by appending "-Base" to the
            # Existential qualifier — a name that appears nowhere.  `Gen` and
            # `insert` come from `Cyclic.Base` at the SAME index, under whatever
            # qualifier THIS file gave it; if the file has no Base binding at that
            # index the repair needs one added, which is a fact worth reporting
            # rather than a string to invent.
            bs = [q for q, (i, k) in qual.items() if i == idx and k == "Base"]
            out.append((p, idx, qs[0] if qs else None,
                        bs[0] if bs else None, sorted(names)))
        # the unqualified shape: a bare `open import …Existential n` plus a bare
        # `normalize` use, and NO ListPresentation application yet.
        if ("Existential" in bare and not _has_lp
                and re.search(r"(?<![\w.'-])normalize(?![\w'-])", src)
                and not any(r[0] == p for r in out)):
            out.append((p, bare["Existential"], None, None, ["normalize"]))
    return out


def telescope_imports(prefix=None, apply=False):
    """[(path, missing_modules, ambiguous)] — a TELESCOPE whose types nothing imports.

    ⚑⚑ THE SUCCESSOR STATE `repair_telescopes` CREATES AND CANNOT SEE.  Restoring
    `module M (n : ℕ) where` makes `ℕ` load-bearing AT THE HEADER, and an import
    BELOW the header binds nothing there — agda reports `NotInScope: ℕ` at the
    telescope's own column.  That repair's planner is fed by `applied_imports`,
    whose question is *"an applied argument nothing binds"*, and restoring the
    telescope is precisely what REMOVES those rows.  So the module it just fixed
    is invisible to the census that found it, by construction.

    MEASURED, and the sequence is the whole finding: 33 unbound-argument sites → 0
    across 17 modules (clean census) → compile one → `NotInScope: ℕ` → 15 of the 17
    freshly red → re-run the repair → 0 modules, all 15 refused as
    already-telescoped.  Step 2 is the only reason this function exists; a green
    census read as done while nothing compiled.

    ⚑ SO THIS IS A DIFFERENT QUESTION, NOT A WIDER ONE.  Bolting it onto
    `repair_telescopes` would give that mode a verdict spanning two predicates
    ("parameter missing" and "parameter present but unimportable"), which is how a
    census stops meaning one thing.  The refusal there names this by symbol.

    Reports a module only when a telescope type resolves to EXACTLY ONE home that
    is not already imported above the header; a name with several homes is
    reported separately and never chosen — the rule `hoist_telescope_imports`
    states as *"`n` has SEVERAL homes — refusing to guess"*.
    """
    import agda_lex as _al
    root = f"{AG}/Substrate"
    if prefix:
        root = os.path.join(AG, *prefix.split("."))
    pats = [f"{root}/**/*.agda"] + ([f"{root}.agda"] if prefix else [])
    out = []
    for p in sorted({q for pat in pats for q in glob.glob(pat, recursive=True)}):
        try:
            raw = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        src = _al.mask_comments(raw)
        mod = module_path(p, AG)
        hdr = re.search(rf"^module\s+{re.escape(mod)}\s*(.*?)\bwhere", src, re.M)
        if not hdr or not hdr.group(1).strip():
            continue                      # no telescope — not this question
        above = src[:hdr.start()]
        need, amb = [], []
        for _t in re.findall(r":\s*([^)}]+)", hdr.group(1)):
            for _nm in re.findall(r"[^\s()\[\]{}→,;]+", _t):
                homes = def_index().get(_nm, [])
                if len(homes) > 1:
                    amb.append(_nm)
                elif len(homes) == 1:
                    need.append(homes[0])
        need = [m2 for m2 in sorted(set(need))
                if not re.search(rf"^open\s+import\s+{re.escape(m2)}\s*$",
                                 above, re.M)]
        if need or amb:
            out.append((p, need, sorted(set(amb))))
    if apply:
        import edit_snapshot
        edit_snapshot.guard(f"telescope_imports ({len(out)} file(s))",
                            [p for p, _n, _a in out], intent="apply")
        for p, need, _a in out:
            if not need:
                continue
            cur = open(p, encoding="utf-8", errors="replace").read()
            mod = module_path(p, AG)
            blk = ("-- ⚑ ABOVE THE HEADER because the telescope names these types;\n"
                   "-- an import below the header binds nothing for the header itself.\n"
                   + "".join(f"open import {m2}\n" for m2 in need))
            open(p, "w").write(re.sub(rf"^(module\s+{re.escape(mod)}\b)",
                                      blk + r"\g<1>", cur, count=1, flags=re.M))
    return out


def repair_telescopes(prefix=None, apply=False):
    """RESTORE the module telescope a decomposition dropped.  Returns [(path, param)].

    ⚑ THE OTHER HALF OF `applied_imports`, WHICH ONLY EVER REPORTED.  That census
    names the defect precisely — *"a split shard inherits its parent's `open import
    …Base n` but not the parent's own `module …Parent (n : ℕ) where`"* — and its
    own footer names the fix: *"recover the parent's telescope with `--at <rev>
    <Mod>` — the argument is usually a parameter a decomposition dropped, not a
    name to import."*  That recovery was still a HAND edit per module, and the
    census reports 33 sites across 17 modules, all identical.  A repair applied 17
    times by hand is the shape the standing rule forbids.

    ⚑ THE PARAMETER IS READ FROM THE PRE-SPLIT PARENT, NEVER GUESSED.  A shard's
    unbound argument `n` could in principle be anything; what makes it decidable is
    that the parent module the shard was split OUT of declared it, and that parent
    is recoverable from git.  MEASURED on `Coxeter/Cyclic/Inverse` at `771283c8^`:
    `module …Inverse (n : ℕ) where`, and every one of its five leaves applies `n`
    to an import while binding nothing.  So the repair copies a DECLARATION that
    existed, rather than inventing a plausible one.

    ⚑ REFUSES when the parent cannot be read, when the parent's telescope does not
    bind the argument, or when the shard already HAS a telescope — the last is not
    this defect and a blind rewrite would corrupt a working header.
    """
    import subprocess
    rows = [r for r in applied_imports(prefix) if not r[4]]
    plans, seen, refused = [], set(), []
    for mod, ln, target, arg, _bound in rows:
        path = os.path.join(AG, *mod.split(".")) + ".agda"
        if path in seen:
            continue
        # the PARENT is the shard's own dotted prefix — the module it was split
        # out of.  `Inverse.InvPos` -> `Inverse`; walk up until one resolves.
        # ⚑⚑ DELEGATE TO `at_revision`, DO NOT HAND-ROLL `git show`.  The first cut
        # built its own subprocess call with `cwd=os.path.dirname(AG)` and a
        # `relpath` against the same base; `at_revision` resolves the repo root
        # from `__file__`'s grandparent and passes `git -C`.  Mine silently
        # returned empty for EVERY parent — 33 refusals reading "no pre-split
        # parent declares this parameter" when every parent declares it and
        # `--at` reads them all.  A second spelling of a solved problem, and the
        # refusal message blamed the substrate for a defect in the method.
        parent, decl = ".".join(mod.split(".")[:-1]), None
        while parent.count(".") >= 1 and decl is None:
            txt, _pp = at_revision(parent, "771283c8^")
            m = re.search(r"^module\s+\S+\s*(\([^)]*\))\s*where", txt or "", re.M)
            if m and re.search(rf"\b{re.escape(arg)}\b", m.group(1)):
                decl = m.group(1)
            parent = ".".join(parent.split(".")[:-1])
        # ⚑⚑ EVERY REFUSAL IS NAMED.  The first cut `continue`d silently at three
        # points and the mode reported `0 module(s)` on a census of 33 rows — a
        # tool answering "nothing to do" when it meant "I gave up three times",
        # which is the same absent-vs-unmeasured conflation this file censuses
        # elsewhere.  A repair that declines must say which precondition failed.
        if decl is None:
            refused.append((mod, arg, "no pre-split parent declares this parameter"))
            continue
        try:
            cur = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            refused.append((mod, arg, "unreadable"))
            continue
        hdr = re.search(rf"^module\s+{re.escape(mod)}\s*(.*?)\bwhere",
                        cur, re.M)
        if not hdr:
            refused.append((mod, arg, "no `module <this> … where` header found"))
            continue
        # ⚑⚑ TELESCOPED IS NOT DONE — AND THIS ENTRY POINT CANNOT SEE THAT.  A
        # module can carry `(n : ℕ)` and still lack the import binding `ℕ`, which
        # is precisely the state this tool leaves behind when it restores a
        # parameter without its type's import.  MEASURED: 17 repaired, then 15
        # failing `NotInScope: ℕ` at the header's own column.
        #
        # ⚑ BUT THE PLANNER IS FED BY `applied_imports`, whose question is "an
        # applied argument nothing binds" — once the telescope is restored those
        # rows vanish, so a repaired-but-unimported module is invisible HERE by
        # construction.  Reaching it needs a DIFFERENT census (a telescope naming
        # a type nothing imports above the header), which is ⓉTELESCOPE-IMPORTS
        # and not this function.  Refusing honestly is the correct stopping point;
        # silently re-planning them would report work this entry point never does.
        if hdr.group(1).strip():
            refused.append((mod, arg, f"already telescoped: {hdr.group(1).strip()}"
                                      " — an import gap here needs ⓉTELESCOPE-IMPORTS"))
            continue
        # ⚑⚑ THE TELESCOPE'S OWN TYPES NEED IMPORTING, AND ABOVE THE HEADER.
        # Restoring `(n : ℕ)` makes `ℕ` load-bearing AT THE HEADER, where an
        # import BELOW it binds nothing — agda then reports `NotInScope: ℕ` at the
        # telescope's own column.  MEASURED on `Inverse/Inv.agda` immediately
        # after the first apply run: 33 unbound-argument sites went to 0 and the
        # module failed in a NEW way, so "33 → 0" would have read as done while
        # every repaired file was still red.
        #
        # ⚑ THE DEPENDENCY WAS ALWAYS THERE — it arrived through the dissolved
        # conduit (`Bridge`'s body was `open import …Base n public`), so no shard
        # ever imported `ℕ` itself.  Restoring the telescope does not create the
        # need; it makes an invisible one visible, which is the whole point of
        # the decomposition.  Emitting the import is therefore part of the SAME
        # repair, not a follow-up: a tool that restores the parameter and leaves
        # its type unresolved has moved the breakage rather than fixed it.
        #
        # Resolution goes through the definition index — the same authority that
        # answers `agda_defs <name>` — and REFUSES a name with several homes
        # rather than picking one, exactly as `hoist_telescope_imports` does.
        types, needed, ambiguous = re.findall(r":\s*([^)}]+)", decl), [], []
        for _t in types:
            for _nm in re.findall(r"[^\s()\[\]{}→,;]+", _t):
                homes = def_index().get(_nm, [])
                if len(homes) == 1:
                    needed.append(homes[0])
                elif len(homes) > 1:
                    ambiguous.append(_nm)
        needed = sorted(set(needed))
        if ambiguous:
            refused.append((mod, arg,
                            f"telescope type name(s) with several homes: "
                            f"{', '.join(sorted(set(ambiguous)))} — import by hand"))
            continue
        # only what the file does not already import ABOVE its header
        _above = cur[:hdr.start()]
        needed = [m2 for m2 in needed
                  if not re.search(rf"^open\s+import\s+{re.escape(m2)}\s*$",
                                   _above, re.M)]
        plans.append((path, mod, decl, needed))
        seen.add(path)
    if apply:
        import edit_snapshot
        edit_snapshot.guard(f"repair_telescopes ({len(plans)} file(s))",
                            [p for p, _m, _d, _i in plans], intent="apply")
        for path, mod, decl, needed in plans:
            cur = open(path, encoding="utf-8", errors="replace").read()
            # ⚑ the telescope is inserted only where it is MISSING — a module that
            # already has one is here for its imports alone, and re-substituting
            # would duplicate the parameter list.
            out = re.sub(rf"^(module\s+{re.escape(mod)}\s*)where",
                         rf"\g<1>{decl} where", cur, count=1, flags=re.M)
            if needed:
                # ⚑ ABOVE the header, never below — that position IS the fix.
                blk = ("-- ⚑ ABOVE THE HEADER because the telescope names these types;\n"
                       "-- an import below the header binds nothing for the header itself.\n"
                       + "".join(f"open import {m2}\n" for m2 in needed))
                out = re.sub(rf"^(module\s+{re.escape(mod)}\b)",
                             blk + r"\g<1>", out, count=1, flags=re.M)
            open(path, "w").write(out)
    return [(p, d, i) for p, _m, d, i in plans], refused


def stranded_residue(prefix=None):
    """[(residue_path, [(name, verdict, [where])])] — is a split's RESIDUE re-homed?

    ⚑⚑ THE THIRD MEMBER OF THE TELESCOPE-REPAIR CHAIN, AND THE ONE WITH NO OWNER.
    The two that exist are `applied_imports` (a parameter is MISSING, repaired by
    `repair_telescopes`) and `telescope_imports` (the parameter is PRESENT but its
    TYPE is unimportable).  Both are keyed on the module HEADER.  This one is keyed
    on the split's own leftovers, and it sees a case neither can:

        a leaf USES a name the pre-split parent's telescope BOUND,
        and no leaf re-declares it.

    ⚑ WHY `--repair-telescopes` IS STRUCTURALLY BLIND TO IT.  Its planner is
    `[r for r in applied_imports(prefix) if not r[4]]` — *an applied argument to an
    import that nothing binds*.  MEASURED on `Algebra/Quotient/Surreal/`: the leaves
    apply NO arguments to any import, because the dropped binders (`≤ⁿ-refl`,
    `≤ⁿ-trans`) are PROOF WITNESSES consumed in a record body, not module arguments.
    `--applied-args` reports 2 rows tree-wide and neither is Surreal.  The defect is
    invisible to that census by construction, exactly as `telescope_imports`'
    docstring already says of ITS predecessor.

    ⚑⚑ THE EVIDENCE IS ALREADY ON DISK AND NOTHING READ IT.  `split_lemmas.write_residue`
    emits a `RESIDUE.md` beside the leaves and states the unmade decision outright:
    *"Re-home them deliberately, or delete them deliberately — but do it as a
    decision, not as a side effect."*  Four exist, all UNTRACKED, so no gate can see
    them.  `split_telescoped.residue_binders` handles residue IN-FLIGHT during a
    split and never opens a stranded file; the reader that would decide re-home vs
    delete did not exist.  This is that reader — a CENSUS, never a writer: the
    writer's own instruction is that a human makes the call.

    ⚑⚑⚑ THE VERDICT IS THREE-VALUED, AND COLLAPSING IT TO TWO OVER-REPORTS.  The
    precedent is `vfs`'s PRESENT/ABSENT/BROKEN: *"your question was ill-posed"* is
    not *"the answer was ABSENT"*.  Here the three carry three different next actions:

      · `re-homed`      the name IS bound in a sibling leaf → the residue line is
                        spent; the file can be retired.  Nothing to do in the tree.
      · `live-damage`   the name is bound NOWHERE and a leaf USES it → the split
                        dropped a binder the leaves still consume.  A real defect.
      · `unused`        bound nowhere and used nowhere → neither.  The parent
                        declared it, no leaf inherited the use; deleting the line
                        costs nothing but it is NOT damage.  Folding this into
                        `live-damage` would report work that does not exist.

    Binder names come from `agda_lex.telescope_groups`, which is the authority for
    reading a telescope into GROUPS rather than a flat name list — `module_scopes`
    FLATTENS (`(x : SurrealFinite (suc n))` yields `x` AND `n`), which is right for
    "is this bound here" and wrong for "which parameters does this leaf need".
    Use-detection is two-spelling via `split_telescoped.spellings` + `agda_lex.word`,
    because `_∷_` is written `∷` at a use site; a one-spelling census reports its own
    method as a fact about the substrate.

    A residue file whose lines are NOT a telescope (a bare fixity such as
    `infix 8 -_`) binds no name and is reported as `no-binders` rather than being
    silently skipped: "not this question" and "nothing to do" must not render alike.
    """
    import agda_lex as _al
    import split_telescoped as _st
    root = f"{AG}/Substrate"
    if prefix:
        root = os.path.join(AG, *prefix.split("."))
    out = []
    for rp in sorted(glob.glob(f"{root}/**/RESIDUE.md", recursive=True)):
        try:
            residue = open(rp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        # The body is the indented, line-numbered tail the writer emits; strip the
        # `NN  ` prefix to recover the ORIGINAL telescope text verbatim.
        body = []
        for ln in residue.split("\n"):
            m = re.match(r"^\s{2,}\d+\s{2}(.*)$", ln)
            if m:
                body.append(m.group(1))
        if not body:
            continue
        # ⚑ WRAP IN A SYNTHETIC HEADER so the AUTHORITY parses it.  The residue is a
        # telescope's PARAMETER LINES with its trailing `where` — exactly the shape
        # `telescope_groups` reads given an explicit span, and re-deriving a group
        # parser here would be the `agda_files()` defect (one capability, several
        # bodies).  The explicit span names the parameter lines, per that function's
        # stated convention.
        synth = "module _\n" + "\n".join(body)
        groups = _al.telescope_groups(synth, (0, len(body)))
        names = [n for ns, _g in groups for n in ns]
        # the sibling leaves: every module in the directory the residue sits in
        leaves = sorted(p for p in glob.glob(os.path.join(os.path.dirname(rp),
                                                          "**", "*.agda"),
                                             recursive=True))
        rows = []
        if not names:
            rows.append((None, "no-binders", []))
        for nm in names:
            # ⚑⚑ RE-HOMED IS A CLAIM ABOUT THE SIBLINGS, NOT ABOUT THE TREE.  The
            # first cut asked `def_index()` — tree-wide — and reported `Word`
            # re-homed because `Coxeter.Word` defines a `Word`.  That is a DIFFERENT
            # `Word`: a global name match on a common identifier is a coincidence,
            # and reading it as re-homing would retire a residue file on the strength
            # of an unrelated definition elsewhere.  The question the writer posed is
            # *did the split's own leaves take this binder back*, so the evidence is
            # the SIBLING SET: a leaf's own telescope, or a definition in a leaf.
            homes = []
            for lp in leaves:
                try:
                    lsrc = open(lp, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                _lm = module_path(lp, AG)
                if any(nm in ns for ns, _g in _al.telescope_groups(lsrc)):
                    homes.append(_lm)
                elif _lm in def_index().get(nm, []):
                    homes.append(_lm)
            if homes:
                rows.append((nm, "re-homed", sorted(set(homes))))
                continue
            # unbound — so the question is whether a leaf still CONSUMES it
            used = []
            for lp in leaves:
                try:
                    lsrc = open(lp, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                masked = _al.mask_comments(lsrc)
                if any(_al.word(s).search(masked) for s in _st.spellings(nm)):
                    used.append(module_path(lp, AG))
            # ⚑ AND A TREE-WIDE HOME IS REPORTED AS EVIDENCE, NEVER AS A VERDICT.
            # Narrowing `re-homed` to the siblings (above) would otherwise make a
            # binder genuinely re-homed to a NON-sibling module read as damage.  So
            # the elsewhere-homes ride along on the row: enough for the operator to
            # rule, not enough for the census to decide.  Silence here would be the
            # method reported as the substrate.
            _elsewhere = sorted(def_index().get(nm, []))
            rows.append((nm, "live-damage" if used else "unused",
                         sorted(used) + [f"(also defined elsewhere: {_m2})"
                                         for _m2 in _elsewhere]))
        out.append((rp, rows))
    return out


def applied_imports(prefix=None):
    """[(module, line, target, arg, bound)] — `open import M x` and whether `x` is BOUND.

    ⚑ THE DEFECT A DECOMPOSITION LEAVES WHEN IT DROPS A TELESCOPE.  A split shard
    inherits its parent's `open import ...Base n` but not the parent's own
    `module ...Parent (n : ℕ) where`, so `n` is applied to the import while
    nothing binds it.  MEASURED TWICE, 2026-08-17: `Foundation/Fin/Iterate.agda`
    (one name, `ℕ*`, from a dissolved `renaming`) and every one of the EIGHT
    `Groups/Coxeter/Cyclic/Bridge/*` shards — one split, one dropped telescope,
    eight modules failing at the same column.

    ⚑ FOUND THROUGH A SWEEP REFUSAL, WHICH IS WHY THIS MODE EXISTS.  Both cases
    surfaced only because `unblock`'s `leaves_ready` precondition declined to
    rewire onto them; nothing could ASK the tree for the class.  The census
    ranked those roots at cone size 7/3/1/1 and read as "broad and shallow"
    while one of them gated a 27-module class — a fact about the METHOD reported
    as a fact about the substrate.

    ⚑ AND THE ARGUMENT IS THE HALF `_IMPORT` THROWS AWAY.  The edge authority's
    regex stops at the module name, because its question is *who imports whom*.
    The argument is a different question and needs its own capture — which is
    why a second pattern here rather than a widened one there: ~19 tools resolve
    through `_IMPORT` and none of them want the tail.

    A row is reported only when the argument is a bare identifier that NOTHING
    in the importing module binds.  Bound-by:
      * the module's own telescope (`module M (n : ℕ) where`),
      * a `variable` block,
      * a top-level definition,
      * or the name is not an identifier at all (`Set`, a literal, a parenthesised
        expression) — never guessed at.
    """
    import agda_lex as _al
    out = []
    root = f"{AG}/Substrate"
    if prefix:
        root = os.path.join(AG, *prefix.split("."))
    pats = [f"{root}/**/*.agda"] + ([f"{root}.agda"] if prefix else [])
    paths = sorted({q for pat in pats for q in glob.glob(pat, recursive=True)})
    for p in paths:
        try:
            raw = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        src = _al.mask_comments(raw)
        lines = src.split("\n")
        mod = module_path(p, AG)
        # ⚑ THE MODULE'S OWN TELESCOPE IS THE FIRST BINDER, and reading it is the
        # whole point: `module M (n : ℕ) where` binds `n` for every import BELOW
        # it, which is exactly where an applied import sits.
        bound = set(_variable_binders(mod)) | set(provides(mod))
        for l in lines:
            m = re.match(r"^\s*module\s+[A-Za-z0-9_.'\-À-￿]+([^\n]*?)\bwhere", l)
            if m:
                for grp in re.findall(r"[({]([^:()${}]+):", m.group(1)):
                    bound.update(grp.split())
                break
        # ⚑ EVERY MODULE THIS FILE IMPORTS, so an argument supplied by ANOTHER
        # import can be recognised.  `provides` is the shared authority; this
        # never re-derives an export list.
        imported_targets = [mm.group(1) for l in lines
                            if not l[:1].isspace()
                            for mm in [_IMPORT.match(l)] if mm]

        def exports_of(t, _c={}):
            if t not in _c:
                _c[t] = set(provides(t))
            return _c[t]

        for i, l in enumerate(lines):
            if l[:1].isspace():
                continue
            m = _APPLIED.match(l)
            if not m:
                continue
            target, tail = m.group(1), m.group(2).strip()
            if not tail:
                continue
            # ⚑ ONLY A BARE IDENTIFIER IS DECIDABLE HERE.  `open import M (f x)`
            # or `open import M Set` may be perfectly well-formed against names
            # this scan does not model, and reporting them would be the
            # false-positive class `--late-imports` paid for four times.
            if not re.fullmatch(r"[A-Za-z0-9_'À-￿]+", tail):
                continue
            # ⚑ (0) A NUMERIC LITERAL IS A CORRECT APPLICATION, NOT A NAME.
            # `open import ...Cyclic.Base 1` instantiates the telescope at 1 —
            # the very thing a repaired shard does.  The first tree-wide run
            # reported 25 such rows (`Z2.*` at 1, `Z3.*` at 2, `Z4/Z5/Z7`), i.e.
            # a third of the census was the CORRECT form of the defect it hunts.
            if tail.isdigit():
                continue
            # ⚑ (1) `public` IS A MODIFIER, NOT AN ARGUMENT.  `open import M public`
            # re-exports; capturing the tail blindly reported it as an application
            # of an unbound `public`.  Measured on the first tree-wide run —
            # `Algebra/F2/MixColumns/Base:5`, a `stale` module, which would have
            # sent a reader to "bind" a keyword.
            if tail in _NOT_A_CAPABILITY:
                continue
            if tail in bound:
                continue
            # ⚑⚑ (2) AN ARGUMENT MAY BE AN *IMPORTED* NAME, AND THE FIRST CUT
            # MODELLED ONLY LOCAL BINDERS.  `open import RewriteConfluence _⇒_`
            # in `NewmanKI/Properties` applies a name another import supplies;
            # the module COMPILES and was reported.  Same for `ExtrudeCoEmitMonad
            # ℕ` (ℕ from `Foundation.Nat.Nat`) and `Permutation Axis`.
            #
            # ⚑ THE VERDICT JOIN IS WHAT EXPOSED THIS — two rows came back
            # `clean`, which is the mode reporting on a file the build is happy
            # with.  That is exactly the self-falsifying property `--late-imports`
            # was rebuilt around, working on its first run here.
            if any(tail in exports_of(t) for t in imported_targets):
                continue
            out.append((mod, i + 1, target, tail, False))
    return out


def stale_sections(prefix=None, op="+", renamed="+F",
                   home="Substrate.Algebra.F2.PlusF"):
    """[(module, line, spelling, text)] — a SECTION left on a renamed operator.

    ⚑⚑ THE HALF A RENAME MISSES.  A rename converts every APPLIED occurrence
    (`a + b` → `a +F b`, `cong₂ _+_` → `cong₂ _+F_`) and leaves SECTIONS behind,
    because a section spells the operator with only the underscores its open
    argument slots need: `(a +_)`, `(_+ b)`, `(_+_)`.  MEASURED 2026-08-18 on the
    ban commit's F₂ conversion — `--at 771283c8~1` on `F2/Vector/Universal.agda`
    shows `cong₂ _+F_` and `g zero +F …` converted while `(lookup … j +_)` and
    `(_+ sum-F₂ …)` were not.

    ⚑ AND IT IS A DIFFERENT CLASS FROM `fix_noparse`'s, WHICH IS WHY THAT TOOL
    CORRECTLY REFUSES IT.  There, an operator is DISPLACED (a prefix `+_` that a
    rename overwrote) and the repair restores it.  Here nothing is displaced: the
    spelling is simply stale, the operator it names no longer exists, and the fix
    is to finish the rename.  Both surface as `[NoParseForApplication]`; only the
    import context separates them.

    ⚑ THE PREDICATE IS DECIDABLE BECAUSE THE OLD NAME IS ALL BUT GONE.  A bare
    `_+_` has exactly ONE definer left in the tree (`Groups.F2Cubed`), so a file
    that imports `<home>` and NOT that definer cannot mean a bare `_+_` — the
    section must be the renamed operator.  A file importing both is reported with
    spelling `AMBIGUOUS` and left for a human, the same refusal
    `rename_at_source` makes.
    """
    import agda_lex as _al
    out = []
    root = f"{AG}/Substrate"
    if prefix:
        root = os.path.join(AG, *prefix.split("."))
    pats = [f"{root}/**/*.agda"] + ([f"{root}.agda"] if prefix else [])
    paths = sorted({q for pat in pats for q in glob.glob(pat, recursive=True)})
    # ⚑⚑ EVERY MODULE STILL DEFINING THE OLD SPELLING — AND THE CENSUS IS ASKED IN
    # BOTH SPELLINGS.  `def_index` keys an operator BOTH as written (`_+_`) and
    # bare (`+`), and asking only one is the `--calls emit`/`q_<name>` shape: a
    # fact about the METHOD reported as a fact about the substrate.  MEASURED
    # 2026-08-18 after a peer session flagged exactly this — `'_+_'` reports ONE
    # definer (`Groups.F2Cubed`) while the bare `+` reports TWO, the second being
    # `Algebra.Z.Int`'s PREFIX constructor.  Neither is imported by the F₂
    # population, so the verdict was right; the QUERY was not, and a one-spelling
    # census would mis-rank the next population silently.
    _idx = def_index()
    rivals = ((set(_idx.get("_%s_" % op, ())) | set(_idx.get(op, ())))
              - {home})
    for p in paths:
        try:
            raw = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        src = _al.mask_comments(raw)
        lines = src.split("\n")
        imports = {m.group(1) for l in lines if not l[:1].isspace()
                   for m in [_IMPORT.match(l)] if m}
        if home not in imports:
            continue
        # ⚑⚑ A FILE MAY HOLD TWO *RENAMED* OPERATORS, AND `rivals` CANNOT SEE THAT.
        # `rivals` names modules still defining the OLD spelling — so a file that
        # imports `Nat.Plus` (ℕ+) AND `F2.PlusF` (+F), both legitimately, passes as
        # unambiguous while a bare `_+` in it could mean EITHER.  MEASURED
        # 2026-08-18: `F2/Polynomial/Wedge/BezoutFold/Step` imports both; running
        # the ℕ rename rewrote two F₂ sites, and I reverted from the snapshot.
        #
        # ⚑ THE HOME SET IS THE DISCRIMINATOR.  Any OTHER module that provides a
        # renamed form of this operator is a second claimant on a bare section, and
        # the typechecker is the only arbiter — the same refusal as an old-spelling
        # rival, reached by a different route.
        _others = {m for nm, mods in _idx.items()
                   if nm.lstrip("_").rstrip("_").endswith(op)
                   and nm.lstrip("_").rstrip("_") != op
                   for m in mods} - {home}
        spelling = ("AMBIGUOUS" if (imports & rivals) or (imports & _others)
                    else "stale")
        # ⚑ THE SAME MATCHERS THE TRANSFORM USES — see `_section_patterns`.  These
        # were two independent regexes until they disagreed on the ℕ rename.
        pats_ = _section_patterns(op, renamed)
        for i, l in enumerate(lines):
            if re.match(r"\s*(?:open\s+)?import\s", l):
                continue
            for pat_ in pats_:
                if pat_.search(l):
                    out.append((module_path(p, AG), i + 1, spelling,
                                raw.split("\n")[i].strip()[:90]))
                    break
    return out


def _section_patterns(op, renamed=None):
    """(right, left) — THE section matchers, for both the scan and the transform.

    ⚑⚑ ONE PREDICATE, ONE SPELLING.  `stale_sections` decided what a section is
    and `repair_sections` re-derived it, and the two disagreed the first time
    they were pointed at a rename other than F₂'s: the scan reported two sites in
    `S5/S5TwoFuelFix` where `_++_` (list append) matched `_+`, and the transform
    refused both — `0 repairable` from `2 section(s)`.  The transform was right.
    A shared NAME is not a shared authority; this is the shared authority.

    ⚑ THE OPERATOR CHARACTER IS EXCLUDED ON BOTH SIDES.  A doubled operator
    (`++`) is a DIFFERENT operator, not a section of the single one, and an
    already-renamed section (`+F_`) must not match as `+_` or the transform
    rewrites what it just fixed (`+FF_`) and is not idempotent.
    """
    e = re.escape(op)
    tail = re.escape(renamed[len(op):]) if renamed and renamed.startswith(op) else ""
    stop = e + tail
    right = re.compile(r"(?<![\w'ˡʳ" + stop + r"])" + e + r"_(?![\w'ˡʳ" + stop + r"])")
    left = re.compile(r"(?<![\w'ˡʳ" + stop + r"])_" + e + r"(?![\w'ˡʳ_" + stop + r"])")
    return right, left


def repair_sections(rows, op="+", renamed="+F", apply=False):
    """Finish the rename at each reported SECTION.  Returns sites rewritten.

    ⚑ PER-SITE, AT THE REPORTED LINE — never a file-wide substitution.  This is
    `fix_noparse.repair`'s shape and the reason is measured twice this session: a
    `replace_all` on `" ℕ+ "` ate its delimiters and produced `+k`, `+suc`, `+m`
    (reverted, twice), and `--applied-args`' first tree-wide run carried three
    false-positive classes.  Rewriting only the rows the classifier reported is
    what kept `fix_noparse` from touching `a ℕ+ b` while repairing `ℕ+ 0` on the
    same line.

    ⚑⚑ AND AN ALREADY-RENAMED SECTION MUST NOT MATCH.  `(a +F_)` must not read as
    `(a +_)`, or the tool rewrites what it just fixed and the run is not
    idempotent.  The negative lookahead on the operator character is the whole
    guard, and it is driven by a CONSTRUCTED fixture rather than asserted against
    today's rows — a case that passes because no such row exists is the
    inert-guard shape, not a test.
    """
    right, left = _section_patterns(op, renamed)
    by_file = {}
    for mod, ln, spelling, _text in rows:
        # ⚑ BOTH REFUSALS ARE HARD, not warnings.  An AMBIGUOUS row is one only
        # the typechecker can decide; a row on a compiling module is a false
        # positive by construction (the section resolves there).
        if spelling != "stale":
            continue
        by_file.setdefault(mod, []).append(ln)
    if apply and by_file:
        try:
            _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import edit_snapshot
            # ⚑ `intent` IS THE FUNCTION'S OWN `apply`, NOT THE PROCESS ARGV.  We only
            # reach here when `apply` is true, so the caller HAS stated it — via the
            # parameter, which is what a `_selftest` driving a temp fixture uses.
            # Reading `sys.argv` here would ask about the wrong invocation: measured, it
            # emitted two spurious advisories during a 141/141 selftest run.
            edit_snapshot.guard("repair_sections", [
                os.path.join(AG, *m.split(".")) + ".agda" for m in sorted(by_file)],
                intent="apply")
        except Exception as _e:
            print(f"   ⚠ snapshot unavailable ({_e}) — recover via git if needed")
    n = 0
    for mod in sorted(by_file):
        p = os.path.join(AG, *mod.split(".")) + ".agda"
        try:
            lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
        except OSError:
            continue
        done = []
        for ln in sorted(set(by_file[mod])):
            i = ln - 1
            if i >= len(lines):
                continue
            before = lines[i]
            after = left.sub("_" + renamed, right.sub(renamed + "_", before))
            if after != before:
                lines[i] = after
                done.append(ln)
        if done:
            print(f"   {'fix ' if apply else 'would'}  {mod}  lines {done}")
            n += len(done)
            if apply:
                open(p, "w", encoding="utf-8").write("\n".join(lines))
    return n


def at_revision(mod, rev="HEAD"):
    """(text, path) for a module AS IT WAS at `rev` — a pure READ, no working-tree write.

    ⚑⚑ `git checkout <rev> -- <path>` IS A WRITE, AND REACHING FOR IT TO *LOOK* AT
    HISTORY DESTROYS THE WORKING COPY.  Used repeatedly this session to recover a file,
    including on files carrying edits worth keeping — it happened to be harmless only
    because the edits were the damage.  Reading the blob leaves the tree untouched, so
    the historical text can be diffed, spliced, or consulted for ONE line without
    committing to a wholesale revert (user, 2026-08-17: *"You can have the python
    read() a given object from any given point in history.  Much safer."*).

    ⚑ THE PRIMITIVE EXISTED, INLINE AND UNREACHABLE.  `prune_imports.py:411` runs
    `git show <ref>` inside its `--demand-from` branch — the pipeline's own way of
    recovering a monolith's pre-strip `using` lists after the split deleted them
    (`split_lemmas.capture_demand`: *"the demand declaration is the only non-guessing
    evidence, and it exists ONLY at this moment"*).  One call site, no mode, so the
    question "what did this module look like before the arc touched it?" had no reader
    and got answered by a destructive checkout instead.

    `rev` is any git revision (`HEAD`, a sha, `HEAD~3`).  Returns `(None, path)` when
    the module did not exist there — an ABSENCE, distinct from an empty file, because
    "this file is new in the working tree" is exactly the fact a restore must not
    silently invert.

    ⚑⚑⚑ PROMOTED TO `vfs`, NOT WRAPPED IN IT (⟡vfs-chokepoints, 2026-08-25).  This
    function was ALREADY the right idea — the prose above is the argument for the whole
    seam, and it is kept verbatim because a repair is residue, not an erasure.  What
    was wrong was never the idea; it was five HARDENING gaps in the `subprocess`
    mechanism, and `vfs` deletes all five BY CONSTRUCTION rather than by adding checks:

      1. `text=True` decoded with the LOCALE codec, over a corpus of `𝟙`/`𝟘`/`∷`/`ℕ`.
         agda_defs.py:4300 records this exact bug costing four wrong cause-hypotheses.
         `vfs.read` returns RAW BYTES and `.text()` decodes UTF-8 STRICTLY, so the
         environment no longer picks the codec and a bad byte raises instead of
         silently mangling.  ⚑ The selftest below asserts a telescope reads back as
         `(n : ℕ)` — a test that was passing THROUGH a locale-dependent decode.
      2. `returncode != 0` COLLAPSED EVERY FAILURE INTO `None`.  A typo'd sha, a
         non-repo, an absent git, and a genuinely-new file all returned the same
         ABSENCE — the defect `vfs`'s module docstring names this function for.  Now a
         bad rev is BROKEN and RAISES; only a missing path is `None`.
      3. NO TIMEOUT.  A hung `git` hung a BLOCKING pre-commit hook with no ceiling.
         There is no subprocess left to hang.
      4. `stderr` WAS CAPTURED AND DISCARDED — git said why and nobody read it.  The
         cause now travels in the exception.
      5. THE PATH WAS STRING-JOINED THEN `relpath`'d WITH NO CONTAINMENT CHECK.
         `vfs`'s Rev path walks the git TREE OBJECT part-by-part, so there is no
         filesystem path to escape from; traversal is structurally absent rather than
         defended against.

    ⚑⚑ THE RETURN SHAPE IS UNCHANGED ON PURPOSE — `(text_or_None, rel)`, six call
    sites, all preserved.  Promoting the SEAM and re-signing the FUNCTION are two
    edits, and doing both at once would make a behaviour-preservation check impossible
    to read.  ⚑ BUT THE ABSENT/BROKEN SPLIT IS *NOT* RE-COLLAPSED: a bad revision now
    RAISES rather than returning `None`.  That is the ONE intended divergence, and it
    is the entire point — a caller that passed a wrong sha used to be told, in the same
    breath as a caller reading a genuinely-new file, that the module "did not exist".
    """
    path = os.path.join(AG, *mod.split(".")) + ".agda" if "." in mod else mod
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rel = os.path.relpath(os.path.abspath(path), root)
    r = _vfs.read(rel, _vfs.Rev(rev, root=root))
    if r.presence is _vfs.Presence.BROKEN:
        # ⚑ NEVER SILENTLY A MISS.  This is arm (2) above: the bad-rev / not-a-repo /
        # unreadable cases used to return `None` and read as "the module is new".
        #
        # ⚑⚑ STARVED, NOT ASSUMED.  Re-collapsing this line to `return None, rel`
        # drops the selftest 202/202 → 200/202 on exactly the two cases that assert
        # the split (measured 2026-08-25).  The all-clear has been shown to differ
        # from the found-something, so it is a measurement rather than a decoration.
        raise r.error
    if r.presence is _vfs.Presence.ABSENT:
        return None, rel
    # ⚑ STRICT UTF-8, chosen HERE rather than by the locale — arm (1) above.
    return r.text(), rel


def telescope_contract(prefix=None):
    """(provider, param_names, [(consumer, line, n_applied, args)]) — a `module Over`
    telescope read as the CONTRACT its consumers apply.

    ⚑⚑ A TELESCOPE IS NOT PRIVATE TO ITS FILE.  `module Over (…params…) where` is an
    arity-and-order contract, and every `open <Mod>.Over <args>` in the tree fills it
    POSITIONALLY.  So editing a provider's telescope breaks callers that were correct
    before, at a distance, and the error surfaces in the CONSUMER — which is why it
    reads as several unrelated bugs rather than one.

    MEASURED 2026-08-17, and this mode exists because that measurement cost five
    edits: a tree-wide `rename_at_source` rewrote `Graded/Defs.agda`'s FIRST telescope
    parameter from `(_+_ : A → A → A)` to `(_ℕ+_ : A → A → A)` — a ℕ-domain name on an
    ARBITRARY carrier — while 13 sibling shards kept passing a carrier operation into
    that slot.  The failure moved `:84 → :83 → :58` under repair because it was ONE
    mismatch propagating along the open-chain, not three defects.  Nothing could ask
    "does every consumer of `X.Over` apply the arity `X` declares?".

    ⚑ THE PRIMITIVE EXISTED AND WAS UNREACHABLE.  `topup_leaves.arity` (`:53`) reads
    exactly this and records the same failure signature — *"Leaves of DIFFERENT tiers
    take different telescopes … partially-applied the 3-param leaves … ⇒ [UnequalTerms]
    `Vec A (suc n) !=< ℕ`.  Match the template by ARITY instead."*  It is 1 def / 2
    calls, both internal, keyed on a `TIP_PKG` env var: the judgement was codified and
    could not be ASKED.  Same shape as `leaves_ready`, `collisions()`, `literal_flags`.

    ⚑ AND `module_scopes` IS THE PROVIDER AUTHORITY, NOT A NEW PARSER.  It returns
    `param_names` in declaration order over a paren-depth-aware header span, and its
    own docstring cites `Graded/Defs.agda` as the file whose multi-line telescope
    broke a first-line-only regex.  This composes it with the consumer side rather
    than re-deriving either.

    Counts EXPLICIT `(…)` binder groups only — `{A : Set}` is implicit and is not
    applied positionally, matching what a consumer actually writes.
    """
    import agda_lex as _al
    mods = modules_under(prefix) if prefix else list(import_index())
    # providers: module -> ordered EXPLICIT parameter names of its `Over`
    providers = {}
    for mod in mods:
        p = os.path.join(AG, *mod.split(".")) + ".agda"
        if not os.path.exists(p):
            continue
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for name, _ind, _params, bs, _be in _al.module_scopes(src):
            if name != "Over":
                continue
            # ⚑ BINDER GROUPS, NOT TOKENS — AND `module_scopes` DELIBERATELY GIVES
            # TOKENS.  Its `param_names` flattens `(a b c : A)` to three names because
            # its consumers ask "is `tok` bound here?" (`binds_at`), for which every
            # name matters.  A CONSUMER applies GROUPS: `(+-assoc : (a b c : A) → …)`
            # is ONE argument whose TYPE mentions a/b/c.  Reading the token list as an
            # arity counted those inner binders and reported `Graded.Laws.Assoc.Over`
            # as declaring 32 parameters where it declares 14 — turning 91 correct
            # consumers into phantom "ARITY MISMATCH"es, on a mode that exits 1.
            #
            # ⚑ AND `topup_leaves.arity` (:53) ALREADY HAD THE RULE — `len(re.findall(
            # r"\(", …))` over the header — recorded after a partial-application
            # incident with the same `!=<` signature.  Re-deriving it worse is the
            # reinvention this arc keeps paying for, so the count is taken the same
            # way: top-level `(`-groups of the header, `{…}` implicits excluded.
            providers[mod] = _telescope_groups(src, bs)
    if not providers:
        return []
    # consumers: every `open <Mod>.Over <args>` / `open <Alias>.Over <args>`
    rows = {m: [] for m in providers}
    aliasrx = re.compile(r"^\s*import\s+([\w.'\-]+)\s+as\s+(\S+)")
    openrx = re.compile(r"^\s*open\s+([\w.'\-]+)\.Over\b(.*)$")
    for p in sorted(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)):
        try:
            raw = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        lines = _al.mask_comments(raw).split("\n")
        alias = {}
        for l in lines:
            m = aliasrx.match(l)
            if m:
                alias[m.group(2)] = m.group(1)
        cons = module_path(p, AG)
        for i, l in enumerate(lines, 1):
            m = openrx.match(l)
            if not m:
                continue
            head = alias.get(m.group(1), m.group(1))
            if head not in providers:
                continue
            tail = re.split(r"\b(using|renaming|hiding|public)\b", m.group(2))[0]
            args = tail.split()
            rows[head].append((cons, i, len(args), args))
    return [(m, providers[m], rows[m]) for m in sorted(providers) if rows[m]]


def _telescope_groups(src, header_end):
    """[binder-group name] for a `module Over` header — ONE entry per applied argument.

    ⚑ A GROUP IS WHAT A CONSUMER APPLIES.  `(𝟘 𝟙 : A)` binds two names and takes two
    arguments; `(+-assoc : (a b c : A) → …)` binds ONE and takes one, its type merely
    mentioning a/b/c.  So the count is over TOP-LEVEL `(…)` groups, and within a group
    over the names LEFT of its first `:` — never over every `(` in the header, which
    would count the type's own binders.

    ⚑ `{A : Set}` IS EXCLUDED: an implicit is solved by unification, not applied
    positionally, and no consumer writes it.  Measured on `Graded/Defs.agda`, whose
    header opens `module Over {A : Set}` and whose 13 consumers all pass 14 arguments.

    Returns the names in declaration order, so a caller can report WHICH slot differs
    — the fact that made the Graded damage legible (`_+P_` where siblings say `_+_`).
    """
    lines = _al_mask(src).split("\n")
    head = " ".join(lines[:header_end])
    m = re.search(r"\bmodule\s+Over\b(.*?)\bwhere\b", head, re.S)
    if not m:
        return []
    body, out, depth, buf = m.group(1), [], 0, ""
    for ch in body:
        if ch in "({":
            depth += 1
            if depth == 1:
                buf, opener = "", ch
                continue
        elif ch in ")}":
            depth -= 1
            if depth == 0:
                if opener == "(":                      # explicit only
                    lhs = buf.split(":", 1)[0]
                    out.extend(lhs.split())
                continue
        if depth >= 1:
            buf += ch
    return out


def _al_mask(src):
    """`agda_lex.mask_comments`, imported lazily — THE comment authority."""
    import agda_lex as _al
    return _al.mask_comments(src)


def late_imports(paths=None):
    """(module, line, target, name, use_line) — an import whose names are USED ABOVE it.

    ⚑ AGDA BINDS FROM THE STATEMENT'S POSITION ONWARD, so an import below a use site
    supplies nothing to that use and the file fails `[NotInScope]` while carrying a
    perfectly good import.  MEASURED 2026-08-17: `Algebra/Bijection.agda` used `≡` at
    line 42 and imported `Substrate.Foundation.Eq` — bare, correct owner — at line 98.
    Hoisting the six imports under the module header made it compile with NO other
    change.

    ⚑ AND `agda_imports.py order` CANNOT SEE THIS CLASS, WHICH IS WHY IT REPORTED
    `already ordered` ON THAT FILE.  `order_file` moves a statement DOWN — below the
    binding sites it references (a parameterized import must follow its `module …
    where`; an `open AbelianGroup` must follow the `record` that binds it).  It is the
    same topological sort read in the other direction, and by construction it never
    hoists.  So the two are complements, not rivals: `order` fixes an import that is
    too HIGH, this reports one that is too LOW.

    ⚑ A REPORT, NOT A REPAIR.  Hoisting is not always the fix — an import may sit low
    precisely because it depends on a local binding, which is the case `order_file`
    exists to protect.  A file appearing in BOTH censuses has a genuine cycle in its
    binding order and wants a human; emitting a rewrite here would silently pick a
    side.  `use_line` is the FIRST use above the import, so the caller can see the
    span it would have to move across.

    Names are matched against what the imported module PROVIDES (`def_index`), so an
    unrelated identifier that merely shares a substring is not a hit.  Comment lines
    are skipped via the mask authority.  Absence here is a fact about `agda/Substrate`
    sources, not about the tree.
    """
    import agda_lex as _al
    idx = def_index()
    exports = {}
    for nm, mods in idx.items():
        if nm in _NOT_A_CAPABILITY or len(nm) < 2:
            continue
        for md in mods:
            exports.setdefault(md, set()).add(nm)
    rows = []
    for p in sorted(paths if paths is not None
                    else glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)):
        try:
            raw = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        masked = _al.mask_comments(raw)
        lines = masked.split("\n")
        # ⚑ COLUMN 0 ONLY — AN INDENTED IMPORT IS LOCALLY SCOPED AND NOT LATE.
        # `_IMPORT` admits leading whitespace (its consumers want every edge), but an
        # `open import` inside a `where` block binds for THAT block alone, so a use
        # earlier in the file is served by a different statement entirely.  MEASURED
        # 2026-08-17: `WitnessTower/IsPermutation.agda` was reported twice — imports at
        # :96 and :107, both indented inside `where` clauses, against a `trans` at :91
        # in a THIRD such block — while the file compiles at exit 0.  A census that
        # flags a compiling file is measuring its own matcher.
        # ⚑⚑ THE EARLIEST IMPORT OF EACH TARGET, NOT EVERY OCCURRENCE.  A module may be
        # imported TWICE — commonly a narrow `using (…)` early for the types a file's
        # signatures need, and a second, later one for lemmas used further down.  The
        # first statement binds; a use above the SECOND is served by the FIRST and is
        # not late at all.  MEASURED 2026-08-17 on
        # `Category/UniversalProperty/ExtrudeCoEmitTraceEq.agda`, which compiles:
        # `ExtrudeCoEmitMonad ℕ` is imported at :13 (`using (CoEmit; …)`) and again at
        # :52 (`using (bind-ret-left; …)`), and `CoEmit` at :20 was reported against
        # the :52 statement.
        #
        # ⚑ THIS IS THE THIRD DISTINCT FALSE-POSITIVE MECHANISM IN ONE CENSUS — after
        # non-capability names (`variable` binders, keywords) and locally-SHADOWED
        # names.  Each was found only by compiling a reported file and asking why it
        # built, never by re-reading the matcher.  Recorded because the pattern is the
        # lesson: a positional claim about source needs a semantic oracle to check it
        # against, and this mode's oracle is the build.
        imps = {}
        for i, l in enumerate(lines):
            if l[:1].isspace():
                continue
            m = _IMPORT.match(l)
            if m:
                imps.setdefault(m.group(1), i)
        imps = sorted((i, t) for t, i in imps.items())
        if not imps:
            continue
        mod = module_path(p, AG)
        for i, target in imps:
            names = set(exports.get(target, ()))
            # ⚑ A `variable` BLOCK'S BINDERS ARE NOT EXPORTS, and their names are
            # deliberately short and generic (`a b c`, `m n`, `A B`), so they match
            # everywhere.  `_NOT_A_CAPABILITY` cannot catch them by name — they are
            # arbitrary — so they are read off the PROVIDING module's own source.
            names -= _variable_binders(target)
            # ⚑⚑ A NAME THIS MODULE DEFINES IS NOT EVIDENCE ABOUT ANY IMPORT, AND
            # SUPPRESSING ONLY THE DEFINING LINE WAS NOT ENOUGH.  A local definition
            # SHADOWS the import, so neither the declaration NOR any later use of it
            # says anything about whether the import is reachable.  MEASURED
            # 2026-08-17 on `R/Trace/ExtruderRSideRealigned.agda`: `BareEq` is defined
            # at :44, and after the defining line was filtered the census simply moved
            # to :51 — `splitBare : ∀ {a b} → a ~ b → BareEq a b`, a use of the LOCAL
            # BareEq — and kept reporting the same compiling file.
            #
            # ⚑ THE FIRST FIX WAS THE RIGHT SHAPE AT THE WRONG GRAIN: per-LINE where
            # the fact is per-MODULE.  That is why the row survived one narrowing and
            # died at the next; a filter aimed at the witness rather than at the
            # reason will always leave the next witness standing.
            names -= provides(mod)          # `provides` IS the authority; no twin
            if not names:
                continue
            # only the region ABOVE this statement can be starved by it
            head = lines[:i]
            for n in names:
                # a use is the bare token, not a substring of a longer name
                rx = re.compile(r"(?<![\w.'-])" + re.escape(n) + r"(?![\w.'-])")
                # ⚑ AND THE USE MUST BE AT COLUMN 0 TOO, for the mirror reason: an
                # indented use sits inside a definition body that may carry its own
                # local `open import`.  Restricting BOTH ends to top level makes the
                # claim checkable — a column-0 use above a column-0 import is starved
                # with no local statement able to serve it.  This is deliberately
                # CONSERVATIVE: it under-reports (a genuinely late import serving only
                # indented uses is missed) rather than flagging files that compile.
                # ⚑ A `module _ (X : Set) where` HEADER BINDS X — it is not a use.
                # MEASURED 2026-08-17 on `Groups/Capabilities/Strict2Monoid.agda:28`,
                # `module _ (Word : Set) where`, reported against
                # `Coxeter.Word`'s export `Word` at an import on :48.  Same class as
                # the `variable` binders: a BINDING SITE read as a use.  The file
                # does carry a real late import (`Foundation.Eq` at :50, `≡` needed
                # at :34) — so the row was right about the FILE and wrong about the
                # witness, which is the most misleading way to be wrong.
                hit = next((j for j, hl in enumerate(head)
                            if hl[:1] and not hl[:1].isspace()
                            and not hl.startswith("open import")
                            and not hl.startswith("import")
                            and not re.match(r"^module\b", hl)
                            and rx.search(hl)), None)
                if hit is not None:
                    rows.append((mod, i + 1, target, n, hit + 1))
                    break          # one witness per import is enough to act on
    return sorted(rows)


@functools.lru_cache(maxsize=1)
def reexport_index():
    """(module, line, target, tail) for every surviving `public` re-export.

    ⚑ THE BAN'S UNCENSUSED HALF, AND IT IS A STANDING SUPPLY OF `file-not-found`.
    `import_index` — the edge authority — DISCARDS the `using`/`renaming` tail by
    design ("it is not part of the edge"), and `public` lives in that tail, so the
    one construct that forwards a name across a module boundary is invisible to
    every edge query. `enforce_ban`'s ratchet censuses 1078 modules / 6629
    consumer-imports for the DIRECTIVE half of the ban and never mentions `public`
    (`pycodemod --literal public enforce_ban.py` → 0 sites).

    ⚑ WHY IT MATTERS BEYOND POLICY: a re-export is a name whose HOME the consumer
    cannot see. When decomposition dissolves the forwarding module, every consumer
    that reached the name through it now names something with no file — which is
    the `file-not-found` signature exactly. Re-exports are therefore not merely
    banned, they are the RESERVOIR the class refills from.

    ⚑ AND THE REPAIR REFLEX IS THE OTHER HALF. `agda_imports.stage_warning` records
    that a risk audit once scored `fix_stale_using`'s dropping of a `public` conduit
    as "an unrecoverable export-surface change" — *"true standalone and false in the
    chain"* — and this session reproduced it verbatim: `prune_imports` cleared a
    banned `public` from FaceSetStabilizes, the drop was read as damage, and the
    line was restored pointing at a module the split had dissolved. A census is what
    makes the removals legible as PAYDOWN rather than as loss.

    Returns rows sorted by module. `tail` is the raw text after the module name, so
    a reader can tell a bare `public` from a `public using (...)` without a second
    parse. Absence here is a fact about `agda/Substrate` sources, not the tree.
    """
    import agda_lex as _al
    rows = []
    for p in sorted(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)):
        # ⚑⚑ MASK COMMENTS BEFORE MATCHING, NOT JUST SKIP COMMENT LINES.  The
        # `lstrip().startswith("--")` guard below catches a WHOLE-LINE comment
        # and misses a TRAILING one — and `public` is a word that appears in
        # prose about re-exports far more often than in one.  MEASURED
        # 2026-08-18: three rows in `Graded/Mod`, `Mod/Core`, `Mod/Expand` were
        # matched on their own annotations saying *"NON-public: not ours to
        # re-export"* — the census reporting a file as a re-exporter on the
        # strength of that file denying it.
        #
        # ⚑ `agda_lex.mask_comments` IS the stripper (16 call sites); reading
        # lines raw here was a fourth spelling of a solved problem.
        try:
            _src = _al.mask_comments(open(p, encoding="utf-8",
                                          errors="replace").read())
        except OSError:
            continue
        for n, l in enumerate(_src.split("\n"), 1):
            if l.lstrip().startswith("--"):
                continue
            # ⚑⚑ TWO FORMS RE-EXPORT, AND THIS SAW ONLY ONE.  `open import M …
            # public` is an IMPORT; `open M args … public` — a module
            # APPLICATION, no `import` keyword — forwards names just as hard and
            # matched nothing here.  MEASURED 2026-08-18 on
            # `Category/UniversalProperty/X8aSkiExistence.agda:60`:
            # `open FixpointMachine Tm⟦…⟧ next fix? using (run) public`, a live
            # re-export the census silently omitted.
            #
            # ⚑ THE UNDER-COUNT IS THE DANGEROUS DIRECTION HERE, because this
            # docstring's own claim is that re-exports are the RESERVOIR the
            # `file-not-found` class refills from — so a form the census cannot
            # see is a supply of that class that paydown never reaches.
            m = _IMPORT.match(l)
            if not m:
                m = _OPEN_APPLY.match(l)
                # ⚑⚑ AND THE APPLICATION FORM OVER-FIRES ON A LOCAL RECORD.
                # `open CoTrace public` where `record CoTrace` is defined THREE
                # LINES ABOVE forwards nothing across a boundary — it exposes a
                # record's own fields, which is ordinary Agda idiom, not a
                # re-export.  MEASURED: the first cut of this widening took S5
                # from 8 to 12 sites and all four additions were that shape
                # (`Susp`, `DivStr`, `Wedge`, `CoTrace`), each reported by the
                # mode's own dangling-target check as "names no module in the
                # tree" — the tool telling me the rows were wrong.
                #
                # The ban is about a name whose HOME the consumer cannot see.  A
                # locally-defined record's home IS this module, so only an
                # application of something NOT defined here can re-export.
                if m and m.group(1).split(".")[0] in _local_defs(p):
                    continue
            if not m:
                continue
            # ⚑⚑⚑ THE STATEMENT'S TAIL SPANS CONTINUATION LINES, and reading only
            # `l` missed every multi-line re-export.  MEASURED on
            # `Graded/FromCommRing.agda:77-80`:
            #
            #     open G.Over _+_ _*_ 𝟘 𝟙
            #       +-assoc +-comm +-identityˡ +-identityʳ
            #       *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
            #       public
            #
            # `public` is on the FOURTH line; the head matched, the tail did not
            # contain the keyword, and the census reported ZERO sites for a module
            # that forwards fourteen names to 35 consumers.  Same continuation-line
            # blind spot that hid a `using` clause in `InsertionParity` this
            # session — an Agda statement is not a line, and every scanner that
            # assumes otherwise under-reports.
            #
            # ⚑ THIS IS THE FOURTH UNDER-COUNT RECORDED IN THIS ONE DOCSTRING
            # (whole-line comments, the application form, local records, now
            # continuations) — and by its own argument the under-count is the
            # dangerous direction, since an invisible re-export is a supply of the
            # `file-not-found` class that paydown never reaches.
            # ⚑⚑ AND THE FIRST CUT OF THIS FIX OVER-READ, which is the same error
            # inverted.  `Graded.agda:64-79` is SIXTEEN consecutive `open Pn.Over …
            # public` statements, each at column 0 — but line 64's tail consumed all
            # fifteen following statements, so every row reported the whole block as
            # its own tail.  The census went from silently missing a re-export to
            # loudly mis-attributing sixteen, and the output was unusable.
            #
            # ⚑ A CONTINUATION IS INDENTED **AND** NOT A NEW STATEMENT.  Indentation
            # alone is not the test: a `where`-block body is indented too.  Stop at
            # the first line that starts a statement of its own — `open`, `import`,
            # `module`, or any column-0 text — which is what bounds the tail to the
            # statement it belongs to.
            _tail_lines = [l[m.end():]]
            _k = n                       # `n` is 1-based; _src[n] is the NEXT line
            _all = _src.split("\n")
            while _k < len(_all):
                _nxt = _all[_k]
                if not _nxt.strip():                     # blank ends the statement
                    break
                if not _nxt[:1].isspace():               # column 0 = new statement
                    break
                if _nxt.lstrip().startswith(("open ", "import ", "module ")):
                    break                                # indented, but its own stmt
                _tail_lines.append(_nxt)
                _k += 1
            tail = " ".join(_tail_lines)
            # `public` is a KEYWORD here, not a substring — a module named
            # `…Publication` or a `using (public-thing)` must not match.
            if re.search(r"(?<![A-Za-z0-9_'])public(?![A-Za-z0-9_'])", tail):
                # ⚑⚑ THE KIND WAS COMPUTED AND THEN DISCARDED, and that made the
                # census unrankable.  Both forms matched above and both returned
                # the same 4-tuple, so a reader could not tell an `import`
                # (forwarding — retire it and bind at the real home, the Ⓑ2 move)
                # from an `open <applied module>` (a module APPLICATION — the
                # instance's names have no other route into the file, so
                # "retiring" it means rewriting every use site: a different job
                # at a different cost).  Triage that cannot separate those ranks
                # a 16-line `P*.Over` block beside a one-line `import … public`.
                #
                # ⚑ AND IT CORRUPTED THIS MODE'S OWN DANGLING CHECK.  An
                # application's target (`P0.Over`, `WithLemmas`, `F.Over`) is a
                # LOCAL module name, never a dotted path, so `r[2] not in
                # import_index()` reported all 41 as "name no module in the
                # tree" — the `file-not-found` reservoir the docstring above
                # warns about, over-reported by 41 on a distinction the function
                # already had in hand.  A fact about the METHOD printed as a
                # fact about the substrate.
                kind = "import" if _IMPORT.match(l) else "apply"
                rows.append((module_path(p, AG), n, m.group(1), tail.strip(), kind))
    return rows


@functools.lru_cache(maxsize=1)
def reexporters_by_target():
    """target module -> [(re-exporting module, tail, kind)] — `reexport_index` INVERTED.

    ⚑ WHY THIS EXISTS AS A MODE RATHER THAN A CALLER'S ONE-LINER. `reexport_index`
    answers *"what re-exports survive"* (a census, ordered by the re-EXPORTER); the
    question `scope_source._nearest_reexporter` asks is the TRANSPOSE — *"who still
    re-exports THIS owner, applied?"*. Building that dict at each of 7 call sites is
    the shape `agda_files` was found in four times; the census and its inverse are one
    capability, so the inversion lives with the authority and is memoised once.

    ⚑⚑ AND IT REPLACES A `subprocess.run(["grep", "-rn", ...])` THAT WAS WRONG IN BOTH
    DIRECTIONS — measured 2026-08-26 by differencing the grep's hit set against these
    rows over all 116 Substrate targets (101 agreed):

      · **6 FALSE NEGATIVES.** The grep collected a statement's tail with a hardcoded
        `min(i + 6, len(lines))` window, so a `public` further down a long applied
        import is invisible. Every one of the 6 misses has its `public` at span >= 6,
        and no row with span < 6 was missed — the window bound IS the cause, not a
        correlate. Worst: `Coxeter.GroupFromCapability -> GroupAdapter` at span 17,
        and `Coxeter.ListPresentation -> Coxeter.Core` at span 10.
      · **5 FALSE POSITIVES.** `grep -F "open import <owner>"` is an UNANCHORED
        substring, so owner `…Coxeter.Core` matched statements importing
        `…Coxeter.Core.Operations`, `.NormalizeIdem`, `.NormalizeAppend.Left`, …
        The consumer then gets handed a re-exporter of a DIFFERENT module.

    ⚑ THE FALSE POSITIVE IS THE DANGEROUS DIRECTION HERE, and it is the same defect
    `_alias_binding` exists to prevent: a near-named sibling silently standing in for
    the carrier. A miss makes the resolver DECLINE; a prefix-bleed hit makes it WRITE
    an import naming the wrong module.

    Keyed by target exactly as written in the source, so a `kind="apply"` row's target
    is a LOCAL module name (`P0.Over`, `WithLemmas`) and never a dotted path — the
    distinction `reexport_index` records precisely so a consumer does not read those
    as dangling. Absence is a fact about `agda/Substrate` sources, not about the tree.
    """
    by = {}
    for mod, _line, target, tail, kind in reexport_index():
        by.setdefault(target, []).append((mod, tail, kind))
    return by


@functools.lru_cache(maxsize=1)
def clause_audit(on_module=None):
    """(module, line, target, name, verdict) for every NAME in every import clause.

    ⚑⚑⚑ MEASURED COST, 2026-08-25 — THIS GATE CANNOT COMPLETE, AND THAT IS THE FINDING.
    Sampled per-file CPU for `_clause_scan`, three independent sample sizes:

        n=3    6.16 s/file      n=12   7.01 s/file      n=120   5.45 s/file
        -> FULL RUN over 3598 files: ~19,600-25,200 s CPU  ==  5.4-7.0 HOURS

    The four index builds are NOT the cost: `def_index_modules` 0.02s,
    `reexport_index` 0.81s, `def_index` 0.38s, `mixfix_delims` 0.00s — **1.2s total**,
    and the `mask` phase projects to ~1.4s for the whole tree.  **Essentially 100% of
    the runtime is `_clause_scan`, at ~5-7 SECONDS PER FILE.**

    ⚑⚑ SO THE 2061-SECOND KILL WAS NOT IMPATIENCE — it was ~9% of the way through, and
    no amount of waiting was going to help.  The gate has never been observed to finish
    because it takes the better part of a working day of CPU, not because nobody waited.
    The progress callback answered *is it advancing* (it was); the missing question was
    *how far*, and a denominator without a RATE cannot answer it.

    ⚑ CPU, NOT WALL, AND THE DISTINCTION IS WHY THIS IS TRUSTWORTHY.  This box is busy
    by design and will not be quiet again, so wall-clock figures here would be facts
    about co-tenancy.  Contention delays a process; it does not inflate the cycles it
    consumes.  The premise that a quiet box was needed to measure this gate was retired
    on that reasoning — the measurement was always available.

    ⚑⚑⚑ AND THE CAUSE IS MEASURED, NOT INFERRED: `provides()` REBUILDS `def_index()` ON
    EVERY CALL.  Measured 2026-08-25 — one `def_index()` build costs 0.809s; one
    `provides()` call costs 0.725s, a ratio of **0.90**.  `provides` is three lines
    (`idx = def_index(); return {n for n, mods in idx.items() if mod in mods}`) with no
    memoisation, and `_clause_scan` calls it PER CLAUSE ENTRY.  So a file with ~8 import
    entries pays ~8 complete walks of all 3598 files, which is the ~5-7s/file exactly.

    ⚑ THE FIX IS A CACHE ON `def_index()`, NOT A REWRITE.  It is a pure function of the
    tree, called 38 times across the toolkit (`pycodemod --calls def_index`), and
    `pycodemod --state` reports ZERO module-level caches in this file — so every one of
    those call sites re-walks.  Memoising it collapses the projected 5.4-7.0 hours to
    approximately the mask+index cost (~3s) plus the genuine per-entry set work.
    ⚑⚑ NOT DONE HERE: `def_index` is shared by ~20 tools and a ⟡gates sibling has this
    file open (`git status`: `AM`).  A cache changes staleness semantics for every one of
    those callers within a single process, which is a decision with a blast radius, not a
    local optimisation.  Recorded as the measured next step, with the number that
    justifies it.

    ⚑⚑⚑ `on_module` IS AN OPTIONAL PROGRESS CALLBACK, AND IT EXISTS BECAUSE 94% CPU
    PROVES EXECUTION, NOT ADVANCEMENT.  MEASURED 2026-08-25: this scan ran 2061s at
    94% of a core and was killed because nobody could tell a long scan from an
    infinite loop — a spin burns CPU at 94% too.  The consumer gate
    (`check_clause_audit.py --progress`) emitted one START banner and then nothing,
    so after that line "slow" and "wedged" remained the same observation.  That is
    the original 10-bytes-of-silence defect one level up, and the reason the gate has
    never been observed to complete is that nobody could justify waiting.

    Called as `on_module(phase, done, total)` — `phase` is `"mask"` or `"scan"`,
    naming WHICH of the two passes over `agda/Substrate/**` is running, because they
    have different per-file costs and a single counter that silently restarts at zero
    reads as a regression rather than a second phase.

    ⚑ THE AUTHORITY STAYS POLICY-FREE: this REPORTS a count and never formats,
    prints, or chooses a stream.  Rendering (stderr vs stdout, every-Nth, wording) is
    the consumer's, so a second caller wanting a TUI or a trace span is not fighting a
    print statement compiled into the shared layer.

    ⚑ DEFAULTED TO None SO NO EXISTING CALLER MOVES.  `None` is tested once per file
    with an `is not None` — the callback is not invented, wrapped, or defaulted to a
    no-op lambda, because a no-op still pays a call per file across thousands of
    files for callers that asked for nothing.

    ⚑ THE TWO FAILURE DIRECTIONS ARE ONE QUESTION: does this name BIND anything?
    A `using`/`renaming`/`hiding` clause entry can fail on either side, and the
    tree carries both:

      * NONEXPORT — the target does not export the name.  Agda reports this as a
        **warning** (`ModuleDoesntExport`), the name silently binds nothing, and
        the error surfaces at the far-away USE site as `NotInScope`.  MEASURED
        four times in one session, every one a build failure whose cause was
        lines or files away: `S5Verdict` forwarding Nat-but-not-Eq to fourteen
        consumers; `Compose` asking a `using ()` conduit for `_∘V_`;
        `Properties`/`LogSumExp` asking `GValueLSpace` for `ExpLogCodec`;
        `IntParityBridge` asking `Z.Arithmetic` for `_+ℤ_`/`_*ℤ_`/`_⊖_`.  All
        four came from a ban sweep removing a banned construct without rewiring
        its consumers — so this is not a rare shape, it is the sweep's exhaust.

      * UNUSED — the target DOES export it and the file never mentions it.  Dead
        weight in a clause the ban wants gone anyway; it makes a clause look
        load-bearing when it is not, which is what makes a retirement look
        expensive.  `prune_imports` cannot see these: it judges whole STATEMENTS
        (keep/drop) and bails outright on `renaming`/`as` (`should_keep`'s first
        line), so a dead ENTRY inside a live clause is invisible to it.

    ⚑ UNKNOWN PROVISION IS NOT A NONEXPORT VERDICT, and conflating them would
    re-create this file's own worst measured bug.  `--provides` once answered a
    confident `0 name(s)` for a path it could not resolve; a peer read four such
    zeroes as "these modules are empty" and RETRACTED a correct census on the
    strength of it.  So a target outside `def_index_modules()` yields UNKNOWN and
    is never reported as a missing export — the index not knowing a module is a
    fact about the METHOD.

    ⚑ TWO FALSE-POSITIVE SOURCES WERE MEASURED IN THIS FUNCTION'S OWN FIRST CUT,
    both of them the index's blind spots censused as substrate facts:
      * a target that RE-EXPORTS has an open provision set (`Foundation.Level`
        indexes as one name, `0ℓ`, while forwarding `Level`/`suc`/`_⊔_` from
        `Agda.Primitive` — ~200 green consumers flagged as build failures);
      * a target with `mutual`/`private`/`abstract`/nested-`module` blocks indexes
        SHORT, since the index is column-0 (`GCD.TraceDivides` indexes as ZERO
        names and its consumer compiles clean).
    Both now yield UNKNOWN.  The bias is deliberate: a missed NONEXPORT costs a
    finding, a false one sends a reader to repair a correct file.

    ⚑ AND `def_index` SEES TOP-LEVEL DEFS ONLY — it misses record FIELDS and some
    pattern synonyms, which is why `prune_imports.should_keep` documents a
    measured false DROP on the record field `recon`.  A name the index cannot
    find in a module it DOES know is therefore reported as NONEXPORT only when
    the module is known; the UNUSED direction is judged on the body token scan,
    which is keep-biased by the same reasoning.  Both verdicts are advisory: this
    is a census, never a write path.
    """
    import agda_lex as _al
    rows = []

    # ⚑⚑⚑ THE INDEX BUILDS ARE PHASES TOO, AND THEY WERE THE SILENCE.  MEASURED
    # 2026-08-25: the callback's first `mask` tick fires only AFTER four full walks of
    # `agda/Substrate/**` have already run — `def_index_modules`, `reexport_index`,
    # `def_index` (via `mixfix_delims`) and the mixfix pass itself.  None is memoised
    # (`pycodemod --state` reports ZERO module-level caches in this file), so each is a
    # fresh directory walk.  A consumer watching for progress saw a START banner and
    # then a long silence that it could not distinguish from a wedge — the original
    # 10-bytes-of-silence defect, reproduced one layer down inside the very function
    # added to fix it.
    #
    # ⚑ SO THEY REPORT THROUGH THE EXISTING CALLBACK, not a second channel.  A phase
    # with no denominator uses done=total=1: the shape stays `(phase, done, total)` so
    # no consumer needs a new branch, and "1/1" reads honestly as an indivisible step
    # rather than faking a file count this layer does not have.
    def _phase(_name, _fn):
        if on_module is not None:
            on_module(_name, 0, 1)
        _r = _fn()
        if on_module is not None:
            on_module(_name, 1, 1)
        return _r

    _known = _phase("def_index_modules", def_index_modules)
    # hoisted: a module that re-exports has an OPEN provision set (see the note
    # at the use site).  Pure, so compute once per run, not once per statement.
    _reexporters = _phase("reexport_index",
                          lambda: {r[0] for r in reexport_index()})
    # ⚑⚑ AND THE INDEX ITSELF IS PARTIAL, WHICH IS THE SECOND FALSE-POSITIVE
    # SOURCE.  `def_index` records TOP-LEVEL (column-0) definitions, so a module
    # whose definitions sit inside a `mutual`, `private`, `abstract` or nested
    # `module` block indexes SHORT — and every consumer naming one of those was
    # reported NONEXPORT.
    #
    # MEASURED: `Algebra.Nat.GCD.TraceDivides` indexes as `0 name(s)` because
    # `trace-divides-left`/`-right` are inside a `mutual` block (mutual recursion
    # forces them into one file, as its own header says).  `GcdDividesLeft` names
    # both and COMPILES CLEAN — the census called a green module a latent build
    # failure.  Same class as the record-FIELD blindness `prune_imports` records
    # (a measured false DROP on `recon`).
    #
    # A module with such a block therefore has an OPEN provision set too.  This is
    # keep-biased on purpose: under-reporting NONEXPORT costs a missed finding,
    # over-reporting it sends a reader to repair a file that is already correct.
    # names whose SECTIONS ARE DELIMITERS (`[_,_]`, `⟨_⟩`, `⌊_⌋`) — the tokenizer
    # is built from the same characters, so these must be matched verbatim in the
    # raw body.  Require an `_` HOLE: without it the set picks up index tokenizer
    # artifacts whose presence in a body proves nothing.  (Same rule and same
    # reasoning as `prune_imports._mixfix_names`.)
    # ⚑ TWO PHASES, NOT ONE — `def_index()` is a full tree walk and `mixfix_delims` is a
    # pass over its result.  Written as one nested expression they report as a single
    # opaque wait, which is exactly the conflation this instrumentation exists to undo.
    _di = _phase("def_index", def_index)
    _mixfix = _phase("mixfix_delims", lambda: _al.mixfix_delims(_di))
    _partial = set()
    # ⚑ THE GLOB IS HOISTED so the two passes share one directory walk AND so a total
    # exists to report against. A counter with no denominator cannot distinguish "42
    # files in" from "42 of 43" — the bare-count defect this repo records four times.
    _files = sorted(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True))
    _total = len(_files)
    for _i, _p in enumerate(_files, 1):
        if on_module is not None:
            on_module("mask", _i, _total)
        try:
            _s = _al.mask_comments(open(_p, encoding="utf-8",
                                        errors="replace").read())
        except OSError:
            continue
        # ⚑ NARROW, AND THE FIRST CUT WAS NOT.  Firing on ANY of
        # mutual/private/abstract/nested-module swept nearly the whole tree into
        # UNKNOWN — `Foundation.Vec` and `Q.Neg` are ordinary modules that happen
        # to contain a `private` block, and their consumers all went unknown, so
        # BOTH verdict classes read empty.  A census that reports nothing because
        # it disqualified everything is worse than one with false positives: it
        # renders as a clean tree.
        #
        # What actually makes the index SHORT is a block that holds definitions
        # the column-0 scan cannot reach while they REMAIN exported — `mutual`
        # and `abstract`.  A nested `module` is addressed by its own dotted path,
        # so it does not belong here either.
        #
        # ⚑⚑ AND `private` IS DELIBERATELY NOT ON THIS LIST — it is BANNED, not
        # tolerated, and `scripts/check_private_ratchet.py` is the paydown-only
        # census enforcing that (`private variable` exempt: a binding form, not a
        # definition).  The policy reason is the same one that bans re-exports,
        # seen from the other side: a re-export pushes a name where its home is
        # invisible, and `private` blocks a name that would otherwise LEAK — so
        # its presence is evidence that something upstream over-exports.  The fix
        # is to decompose until the name never enters the wrong scope, never to
        # mask it after the fact.
        #
        # Excusing `private` here would have made THIS census launder what THAT
        # ratchet is paying down: two gates on one construct, pulling opposite
        # ways.  A clause naming a `private` name is a real NONEXPORT and must
        # report as one.
        # ⚑⚑ AND A `record` IS THE THIRD BLIND SPOT — the one `prune_imports`
        # already records as a measured false DROP (`Wedge.Graded using
        # (GradedWedge; recon; gcell)`, where `recon` is a FIELD, so the
        # provision set read empty and a live import was deleted).  A record's
        # fields are exported names that the column-0 index does not hold.
        # MEASURED here: `Algebra.Wedge` indexes 21 names, none of them `C`, and
        # `R.Trace.WedgeBridge:42` names `C` and COMPILES CLEAN.
        if re.search(r"^\s*(mutual|abstract)\b", _s, re.M) or \
           re.search(r"^\s*record\b", _s, re.M):
            _partial.add(module_path(_p, AG))
    # ⚑ THE SAME FILE LIST, not a second glob — one directory walk, and the two phases
    # are guaranteed to report against an identical denominator. Re-globbing could
    # silently disagree if the tree moved between the passes, which would make the
    # progress figures fiction at exactly the moment they matter.
    # ⚑ THE OPAQUE SET IS HOISTED TOO: `_reexporters | _partial` is loop-invariant and
    # was rebuilt once per file — thousands of set unions for one constant value.
    _opaque = _reexporters | _partial
    for _i, p in enumerate(_files, 1):
        if on_module is not None:
            on_module("scan", _i, _total)
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        rows.extend(_clause_scan(src, module_path(p, AG), _known,
                                 provides, _opaque, _mixfix))
    return rows


def _clause_scan(src, mod, known, prov_of, opaque, mixfix=frozenset()):
    """Rows for ONE module's clauses — the census's per-file body, on TEXT.

    ⚑ EXTRACTED SO THE VERDICTS CAN BE DRIVEN ON A CONSTRUCTED FIXTURE.  The
    anti-silencing case (does UNUSED still FIRE?) was pinned on a live tree fact
    and died within the hour when the tree was paid down — while the verdict
    class was working perfectly, on hundreds of rows.  A case whose whole job is
    "the detector is not silenced" must not itself be silenceable by paydown, and
    the only shape that guarantees that is a module built to contain the defect.

    `prov_of` is a callable module -> name-set (the live `provides`, or a dict's
    `.get` in a test); `opaque` is the set of targets whose provision is OPEN, so
    a name they do not directly define reports UNKNOWN rather than NONEXPORT.
    """
    import agda_lex as _al
    rows = []
    _known, _mixfix = known, mixfix
    src = _al.mask_comments(src)
    if True:   # kept as a block so the body below is unchanged from the census
        L = src.split("\n")
        spans = {s.start: s.end for s in _al.statements(L) if s.kind == "import"}
        # the BODY is everything outside import statements — the same exclusion
        # `prune_imports` makes, and for the same reason: a name mentioned only
        # by another import is not a use.
        _skip = {k for a, b in spans.items() for k in range(a, b)}
        body = " ".join(L[k] for k in range(len(L)) if k not in _skip)
        # ⚑⚑ ONE AUTHORITY: `agda_lex.body_tokens` carries all three recoveries with
        # their measured incidents.  This file's first cut re-derived the tokenizer
        # WITHOUT them and immediately reproduced `prune_imports`' documented `_,_`
        # bug — a LIVE import reported UNUSED at `Quotient/CRT.agda:36` while used at
        # :83 and :85, because an infix pair constructor is written as a bare `,` and
        # `,` is a delimiter.  ⚑ THE FIXES WERE WRITTEN DOWN, IN A FILE THIS AUTHOR
        # HAD READ, AND STILL DID NOT TRANSFER: documentation in one place is not the
        # same as one implementation, which is the whole argument for the hoist.
        toks = _al.body_tokens(body, _mixfix)
        # section reconstruction: an operator is `_⊔_` at its definition and bare
        # (`ℓ₁ ⊔ ℓ₂`) at an infix use, so the two spellings never meet without it.
        toks |= {f for t in list(toks)
                 for f in ("_" + t + "_", t + "_", "_" + t)}
        for a, b in sorted(spans.items()):
            txt = " ".join(L[a:b])
            m = _IMPORT.match(L[a]) or _OPEN_APPLY.match(L[a])
            if not m:
                continue
            target = m.group(1)
            prov = prov_of(target) if target in _known else None
            # ⚑⚑ A MODULE THAT RE-EXPORTS IS NOT FULLY DESCRIBED BY THE INDEX, and
            # this censused its own blind spot as a substrate fact — the exact
            # error `--provides` documents and this function's docstring warns
            # about, committed one screen below the warning.
            #
            # MEASURED on the first run: `Foundation.Level` shows `1 name(s)`
            # (`0ℓ`) because `Level`/`suc`/`_⊔_` arrive via `open import
            # Agda.Primitive … public`, and `def_index` scans `agda/Substrate`
            # only.  Every consumer naming those three was reported NONEXPORT —
            # ~200 rows of pure method-artifact, in the verdict class defined as
            # "latent build failure".  Those files COMPILE.
            #
            # So: a target that re-exports anything has an OPEN provision set.
            # Its own names are known; what it forwards is not, and the honest
            # verdict for a name it does not directly define is UNKNOWN.
            if target in opaque:
                prov = None
            for kw in ("using", "hiding"):
                c = re.search(kw + r"\s*\(([^)]*)\)", txt)
                if not c:
                    continue
                # ⚑ `using (module M; f)` IS VALID AGDA — `module` is a KEYWORD
                # introducing a submodule entry, not a name.  Taking it as one
                # reported every such clause as a missing export named "module".
                for nm in [t for t in re.split(r"[;\s]+", c.group(1))
                           if t and t != "module"]:
                    if prov is None:
                        rows.append((mod, a + 1, target, nm, "UNKNOWN"))
                    elif nm not in prov:
                        rows.append((mod, a + 1, target, nm, "NONEXPORT"))
                    elif kw == "using" and not (
                            set(_al.mixfix_forms(nm)) & toks):
                        rows.append((mod, a + 1, target, nm, "UNUSED"))
            # a `renaming (x to y)` has BOTH directions: `x` must be exported by
            # the target, and `y` is the spelling the body must use.
            c = re.search(r"renaming\s*\(([^)]*)\)", txt)
            if c:
                # ⚑ `\S+` SWALLOWS THE `;` SEPARATOR.  `renaming (proj₁ to π₁;
                # proj₂ to π₂)` yielded the destination name `π₁;`, which is not
                # a name — it corrupts the reported row AND the token lookup, so
                # a live rename reads as unused.  Stop at the separator.
                for pair in re.findall(r"([^\s;()]+)\s+to\s+([^\s;()]+)",
                                       c.group(1)):
                    src_nm, dst_nm = pair
                    if src_nm == "module":       # `renaming (module M to N)`
                        continue
                    if prov is None:
                        rows.append((mod, a + 1, target, src_nm, "UNKNOWN"))
                    elif src_nm not in prov:
                        rows.append((mod, a + 1, target, src_nm, "NONEXPORT"))
                    elif not (set(_al.mixfix_forms(dst_nm)) & toks):
                        rows.append((mod, a + 1, target, f"{src_nm} to {dst_nm}",
                                     "UNUSED"))
    return rows


@functools.lru_cache(maxsize=1)
def import_index():
    """module -> sorted[imported module].  THE import-edge authority.

    ⚑ FIVE HAND-ROLLED RIVALS AND NO AUTHORITY.  `pycodemod --rivals imports_of`
    reports **4 defs, 4 REIMPLEMENTING, 0 delegating** (conduit_resolve:90,
    fix_notinscope:29, rename_at_source:35, cap_diagnose:50), plus a fifth private
    `IMPORT` regex in capstone_to_dir:36 and a sixth in drop_dead_renames:45.  Six
    copies of one capability is the `agda_files()`-was-four-bodies defect verbatim,
    and NONE of them was reachable as a QUESTION — so "which modules import
    WitnessTower?", "what is this module's import closure?", "is this cluster a leaf
    or a hub?" all fell out of the toolkit into `grep`, which the hook blocks.

    MEASURED: a deep-expertise pass on `agda/Substrate/WitnessTower/` (347 files)
    could enumerate FILES via `find` and NAMES via `--grep`, and could not answer
    the central question asked of it — what consumes the tower — because the
    consumed-by direction is an EDGE, and no tool held edges.

    Comment lines are skipped; both `import M` and `open import M` are edges (the
    `open` only affects scope, not dependency).  A `using`/`renaming` tail is
    ignored — the ban forbids it on Substrate imports anyway, and it is not part of
    the edge.  Keys are dotted module names via `module_path`, so this composes
    with `def_index`.
    """
    idx = {}
    for p in glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True):
        mods = []
        for l in open(p, errors="replace"):
            if l.lstrip().startswith("--"):
                continue
            m = _IMPORT.match(l)
            if m:
                mods.append(m.group(1))
        idx[module_path(p, AG)] = sorted(dict.fromkeys(mods))
    return idx


@functools.lru_cache(maxsize=1)
def _rev_index():
    rev = collections.defaultdict(set)
    for mod, imps in import_index().items():
        for i in imps:
            rev[i].add(mod)
    return rev


def importers_of(prefix):
    """Modules importing anything under `prefix` -> sorted[(importer, imported)].

    A PREFIX, not an exact name: asking "what consumes the witness tower" means
    `Substrate.WitnessTower` AND every module beneath it.  Exact-name matching is
    the spelling that made a 347-file cluster read as unconsumed.
    """
    out = []
    for tgt, srcs in _rev_index().items():
        if tgt == prefix or tgt.startswith(prefix + "."):
            for s in srcs:
                out.append((s, tgt))
    return sorted(out)


def closure_of(mod, prefix=None):
    """Transitive import closure of `mod` (excluding itself), optionally filtered
    to modules under `prefix`.  Modules with no source in the corpus (stdlib,
    Agda.Primitive) terminate a branch rather than erroring."""
    idx = import_index()
    seen, stack = set(), [mod]
    while stack:
        m = stack.pop()
        for i in idx.get(m, ()):
            if i not in seen:
                seen.add(i)
                stack.append(i)
    if prefix is not None:
        seen = {m for m in seen if m == prefix or m.startswith(prefix + ".")}
    return sorted(seen)


def cycles_with(added=()):
    """Every import CYCLE in the tree, with `added` edges [(importer, imported)] applied.

    Returns [[mod, mod, …]] — each list a cycle in dependency order, [] if acyclic.

    ⚑⚑⚑ THE GRAPH IS THE AUTHORITY, AND A REACHABILITY PROBE IS NOT THE GRAPH (operator,
    2026-08-23: *"the way to go about it is to build a graph and cycle-detect"*).  THREE
    copies of a per-candidate `_would_cycle` exist in this toolkit — `fix_stale_using`,
    `scope_source`, and one I added to `fix_notinscope` an hour ago — and all three share
    a hole: each asks *"does THIS candidate already reach me?"* against the graph as it
    stands, so none can see

      · two candidates in ONE file that jointly close a cycle (each safe alone), or
      · a cycle formed ACROSS files by one sweep — 453 files were edited in a single run,
        each checked against a graph containing none of the other 452 edits.

    A per-candidate reachability query is a SAMPLE OF THE GRAPH, not the graph — the same
    class as sampling state to measure an event.  Applying the whole edit set and running
    a real cycle detection over the result is the only form that answers the question
    asked, and it answers it for a batch as cheaply as for one edge.

    ⚑ TARJAN, NOT REPEATED DFS.  One O(V+E) pass returns EVERY strongly-connected
    component of size > 1 — so a sweep gets its complete cycle census in one call instead
    of one probe per candidate, and a cycle that exists ALREADY is reported rather than
    silently attributed to the edit.  The tree is ~3.6k modules; this is milliseconds.

    ⚑ SELF-LOOPS ARE EXCLUDED. `open import` of one's own module is a different defect
    (and Agda rejects it directly); an SCC of size 1 with a self-edge is not what a
    consumer of this function is asking about.
    """
    g = {m: list(ims) for m, ims in import_index().items()}
    for imp, imported in added:
        g.setdefault(imp, [])
        if imported not in g[imp]:
            g[imp].append(imported)
    index, low, on, stack, out = {}, {}, set(), [], []
    counter = [0]
    for root in list(g):
        if root in index:
            continue
        # ⚑ ITERATIVE, NOT RECURSIVE — a 3.6k-module DAG with long chains blows the
        # default recursion limit, and raising it to paper over a data-shaped bound is
        # the route-around this repo forbids.
        work = [(root, iter(g.get(root, ())))]
        index[root] = low[root] = counter[0]; counter[0] += 1
        stack.append(root); on.add(root)
        while work:
            node, it = work[-1]
            for nxt in it:
                if nxt not in index:
                    index[nxt] = low[nxt] = counter[0]; counter[0] += 1
                    stack.append(nxt); on.add(nxt)
                    work.append((nxt, iter(g.get(nxt, ()))))
                    break
                if nxt in on:
                    low[node] = min(low[node], index[nxt])
            else:
                work.pop()
                if work:
                    low[work[-1][0]] = min(low[work[-1][0]], low[node])
                if low[node] == index[node]:
                    comp = []
                    while True:
                        w = stack.pop(); on.discard(w); comp.append(w)
                        if w == node:
                            break
                    if len(comp) > 1:
                        out.append(sorted(comp))
    return out


def new_edges(rev="HEAD"):
    """Import edges present in the WORKING TREE but absent at `rev`.

    ⚑ AN IMPORT CYCLE HAS NO CANONICAL CULPRIT, AND CHOOSING ONE BY SEARCH PICKS THE
    WRONG EDGE.  A minimum feedback arc set is a set of EQUAL-COST minima; the search
    returns whichever it enumerates first, which on the TokiPona pair was the edge
    that had been there since HEAD rather than the one a sweep had just added.  Cutting
    it would have been minimal, acyclic, and a deletion of working code.  PROVENANCE
    is the tiebreak the graph cannot supply, and git holds it.

    Returns {(importer, imported)}.  A module absent at `rev` contributes NOTHING —
    a new file's edges are all "new" and would swamp the signal; the question is which
    edge was ADDED TO AN EXISTING FILE.
    """
    now = import_index()
    out = set()
    for mod, imps in now.items():
        txt, _ = at_revision(mod, rev)
        if txt is None:
            continue
        old = set()
        for l in txt.split("\n"):
            if l.lstrip().startswith("--"):
                continue
            m = _IMPORT.match(l)
            if m:
                old.add(m.group(1))
        for i in imps:
            if i not in old:
                out.add((mod, i))
    return out


def cycle_cuts(rev="HEAD"):
    """Per import-SCC, the MINIMAL EDGE SET whose removal makes it acyclic.

    Returns [(members, cuts)] — `cuts` a list of (importer, imported) edges.

    ⚑ THE SIZE OF AN SCC IS NOT THE SIZE OF THE PROBLEM, AND REPORTING IT AS SUCH IS
    THE RECURRING MISREAD.  `--cycles` prints a 38-member component and the natural
    reading is "38 modules to untangle"; in a strongly-connected component ONE
    wrong-direction edge can absorb an entire DAG, so the actionable number is the
    FEEDBACK ARC SET, not the membership.  Measured on this tree: 94 modules across
    10 SCCs, and the repair is a handful of edges.

    ⚑ EXACT WHERE EXACT IS AFFORDABLE, AND THE METHOD IS REPORTED.  Over the SCC's
    internal edges we search removal sets by increasing size (k = 1, 2, 3 …) and
    return the first that breaks every cycle — that IS the minimum.  Above a
    tractable edge count we fall back to a greedy pass and label it `greedy`, since
    a heuristic result reported as a minimum is a false figure.
    """
    import itertools
    g = {m: list(ims) for m, ims in import_index().items()}

    def acyclic(nodes, edges):
        adj = {n: [] for n in nodes}
        indeg = {n: 0 for n in nodes}
        for a, b in edges:
            adj[a].append(b); indeg[b] += 1
        q = [n for n in nodes if indeg[n] == 0]
        seen = 0
        while q:
            x = q.pop(); seen += 1
            for y in adj[x]:
                indeg[y] -= 1
                if indeg[y] == 0:
                    q.append(y)
        return seen == len(nodes)

    fresh = new_edges(rev) if rev else set()
    res = []
    for comp in cycles_with():
        s = set(comp)
        edges = [(m, i) for m in comp for i in g.get(m, ()) if i in s]
        # ⚑ PROVENANCE ORDERS THE SEARCH.  Among equal-cost minima, an edge the
        # working tree ADDED is the culprit and an edge that predates `rev` is
        # working code; enumerating fresh edges first makes the first minimum found
        # the causally right one without changing its size.
        edges.sort(key=lambda e: (e not in fresh,))
        cuts, how = None, "exact"
        if len(edges) <= 40:
            # ⚑ FRESH-ONLY FIRST, AS A CONSTRAINT — NOT AS A TIEBREAK.  Sorting fresh
            # edges to the front only reorders enumeration WITHIN a size class, and
            # equal-size minima differ in WHICH edges they name, not how many; the
            # first minimum found was repeatedly an all-pre-existing set while a
            # same-size all-fresh set also existed (measured on the V4Signature and
            # TokiPona components).  Searching the fresh subgraph alone, and only
            # then the full one, makes provenance decide.
            # ⚑ MINIMALITY OUTRANKS PROVENANCE, AND FLIPPING THAT COSTS REAL EDGES.
            # A fresh-only search as a HARD constraint returned 5 cuts on the Lojban
            # component where 2 suffice — cutting three edges that did not need to go.
            # So: walk k upward, and at EACH k prefer an all-fresh set, taking any set
            # only when no all-fresh set of that size exists.  Provenance decides
            # WITHIN a size class; it never buys a larger one.
            for k in range(1, min(len(edges), 6) + 1):
                fallback = None
                for pick in itertools.combinations(edges, k):
                    if not acyclic(comp, [e for e in edges if e not in pick]):
                        continue
                    if all(e in fresh for e in pick):
                        cuts, how = list(pick), "exact/new-only"
                        break
                    if fallback is None:
                        fallback = list(pick)
                if cuts is None and fallback is not None:
                    cuts, how = fallback, "exact"
                if cuts is not None:
                    break
        if cuts is None:
            # ⚑ THE CANDIDATE SET IS THE EDGES ON A CYCLE, NOT EVERY INTERNAL EDGE, AND
            # THE FIRST GREEDY WRITTEN HERE MISSED THAT.  It scored by endpoint degree
            # and returned 42 cuts for a component whose real feedback arc set is TWO —
            # a heuristic reported as a size, which is exactly the misread this mode
            # exists to prevent.  Scoring by ACTUAL RESIDUAL-SCC SHRINKAGE re-derives the
            # measurement each step instead of guessing from a static proxy.
            how = "greedy"
            rem, cuts = list(edges), []
            while not acyclic(comp, rem):
                def _scc_edges(es):
                    # edges still inside some cycle of the residual graph
                    a = {n: [] for n in comp}
                    for x, y in es:
                        a[x].append(y)
                    idx, low, on, st, comps = {}, {}, set(), [], []
                    c = [0]
                    for r in comp:
                        if r in idx:
                            continue
                        w = [(r, iter(a[r]))]
                        idx[r] = low[r] = c[0]; c[0] += 1
                        st.append(r); on.add(r)
                        while w:
                            nd, it = w[-1]
                            for nx in it:
                                if nx not in idx:
                                    idx[nx] = low[nx] = c[0]; c[0] += 1
                                    st.append(nx); on.add(nx)
                                    w.append((nx, iter(a[nx]))); break
                                if nx in on:
                                    low[nd] = min(low[nd], idx[nx])
                            else:
                                w.pop()
                                if w:
                                    low[w[-1][0]] = min(low[w[-1][0]], low[nd])
                                if low[nd] == idx[nd]:
                                    cc = []
                                    while True:
                                        v = st.pop(); on.discard(v); cc.append(v)
                                        if v == nd:
                                            break
                                    if len(cc) > 1:
                                        comps.append(set(cc))
                    return [e for e in es if any(e[0] in cc and e[1] in cc for cc in comps)]
                cand = _scc_edges(rem)
                # pick the candidate whose removal leaves the FEWEST still-cyclic edges
                best = min(cand, key=lambda e: (len(_scc_edges([x for x in rem if x != e])),
                                                e not in fresh))
                rem.remove(best); cuts.append(best)
        res.append((comp, cuts, how, len(edges), fresh))
    return res


def cluster_edges(prefix):
    """(internal, inbound, outbound) edge counts for the subtree under `prefix`.

    THE LEAF/HUB/SPINE MEASUREMENT.  internal = both ends inside; inbound = a
    consumer outside importing in; outbound = a member importing out.  A leaf has
    inbound≈0, a hub has both large, a spine has internal ≫ both.
    """
    def inside(m):
        return m == prefix or m.startswith(prefix + ".")
    internal = inbound = outbound = 0
    for mod, imps in import_index().items():
        for i in imps:
            if inside(mod) and inside(i):
                internal += 1
            elif inside(i):
                inbound += 1
            elif inside(mod):
                outbound += 1
    return internal, inbound, outbound


_PRAGMA = re.compile(r"\{-#\s*([A-Z_]+)\b(.*?)#-\}", re.S)
_HOLE = re.compile(r"(?:^|[\s(])(\?)(?=[\s)]|$)|\{![^}]*!\}")


def trust_census(prefix=None):
    """The TRUST SURFACE of a subtree: postulates, pragmas, holes, per module.

    ⚑ "ANY postulate / hole / --safe exemption?" HAD NO READER.  `--grep` searches
    NAMES, and `postulate`/`TERMINATING`/`?` are KEYWORDS and PRAGMAS — invisible to
    it by construction.  So the single most load-bearing honest-edge question about a
    347-module cluster ("is this actually --safe with zero postulates, as the headers
    claim?") could only be answered by grep, which the hook blocks.  Reporting that
    as "no tool covers this" is the toolkit-gap-read-as-category error verbatim.

    ⚑ AND THE HEADER IS NOT THE ANSWER.  Every tower file's comment block says
    "Zero postulates, --safe --without-K"; a docstring is a CLAIM, and this reads the
    SOURCE.  The two disagreeing is exactly what a census is for.

    Returns {module: {"options": [...], "postulates": [names], "pragmas":
    [(name, arg)], "holes": n}} for modules with a NON-EMPTY finding, plus the key
    `_scanned` = how many modules were examined.  Absence in this dict is a
    positive finding about THAT module, scoped to this scanner's three patterns.

    A `postulate` block's members are the indented signatures beneath it, same
    shallow rule `def_index` uses for `opaque`.
    """
    out = {}
    scanned = 0
    for p in glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True):
        mod = module_path(p, AG)
        if prefix is not None and not (mod == prefix
                                       or mod.startswith(prefix + ".")):
            continue
        scanned += 1
        src = open(p, errors="replace").read()
        rec = {"options": [], "postulates": [], "pragmas": [], "holes": 0}
        for name, arg in _PRAGMA.findall(src):
            arg = " ".join(arg.split())
            if name == "OPTIONS":
                rec["options"] = arg.split()
            else:
                rec["pragmas"].append((name, arg))
        in_post = False
        for l in src.split("\n"):
            if l.lstrip().startswith("--"):
                continue
            if re.match(r"^postulate\s*$", l):
                in_post = True
                continue
            if in_post:
                m = re.match(r"^\s+([^\s:()@{}]+)\s*:(?!:)", l)
                if m:
                    rec["postulates"].append(m.group(1))
                    continue
                if l.strip() and not l[0].isspace():
                    in_post = False
            rec["holes"] += len(_HOLE.findall(l))
        # `--safe` ABSENT is a finding; so is an option set WIDER than the
        # repo baseline.
        # ⚑ `--safe` IS NOT THE WHOLE TRUST QUESTION, AND READING IT AS SUCH MISSED
        # A REAL EDGE.  `OrientationRigCatPermSignChirality:51` is
        # `--safe --without-K --guardedness`: still `--safe`, so an is-it-safe
        # predicate passes it silently — but `--guardedness` is INFECTIVE (it is
        # there only because a transitive import carries it), and coinduction is
        # exactly the kind of widening a trust census exists to surface.  Measured:
        # a subagent reading sources found this file and the first version of this
        # scanner did not.  A binary safe/unsafe test is the cleaver; the option SET
        # is the observable.
        rec["extra_options"] = [o for o in rec["options"]
                                if o not in ("--safe", "--without-K")]
        interesting = (rec["postulates"] or rec["pragmas"] or rec["holes"]
                       or "--safe" not in rec["options"] or rec["extra_options"])
        if interesting:
            out[mod] = rec
    out["_scanned"] = scanned
    return out


# ── ⒢′ THE FLAG-REFLECTION CENSUS ────────────────────────────────────────────
# ⚑⚑ "WHICH FILES' LOCAL `{-# OPTIONS #-}` FAIL TO REFLECT THE GLOBAL FLAGS?" HAD
# NO READER.  `--trust` reads the pragma but measures it against a HARDCODED pair
# (`--safe`, `--without-K`) written into `extra_options` — so it can say a module is
# WIDER than that pair and can never say a module is NARROWER than what the build
# actually applies.  `toolmodes.py --find guardedness` returned 0 hits over 92
# declared modes: the question was uncovered, which is WORK, not a finding.
#
# ⚑ THE GLOBAL SET IS READ FROM ITS AUTHORITIES, NEVER QUOTED.  Two of them, and
# they are DIFFERENT KINDS — conflating them is how a census here would go stale:
#   * `agda/*.agda-lib` `flags:` — applied by AGDA ITSELF to every module in the
#     library, so it reaches `make`, `full_build_check.py` AND an ad-hoc `agda -i .`.
#   * `AGDA_FLAGS` in the GENERATOR (`scripts/gen_build_makefiles.py`) — a command
#     line, so it reaches ONLY what the generated makefiles invoke.  An ad-hoc
#     `agda -i . Foo.agda` does not carry it.
# `agda/Flat.mk` is the generator's OUTPUT, not an authority; it is read only to
# report DRIFT between the two.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _agda_lib_fields(path):
    """`{field: [token …]}` for one `.agda-lib`.

    ⚑ A COMMENT IS A LINE THAT *STARTS* `--`, NOT A `--` ANYWHERE.  The obvious
    `line.split("--")[0]` deletes the value of the one field this census exists to
    read: `flags: --guardedness` becomes `flags:`.  Every Agda flag begins with the
    comment marker, so the naive strip reports the library as carrying NO flags —
    an empty read presented as an absence.

    Continuation lines (indented) extend the field above them, which is how the
    stdlib spells its own `flags:`.
    """
    fields, cur = {}, None
    for raw in open(path, errors="replace"):
        if raw.strip().startswith("--") or not raw.strip():
            continue
        if raw[:1].isspace() and cur:
            fields[cur].extend(raw.split())
            continue
        if ":" in raw:
            cur, _, rest = raw.partition(":")
            cur = cur.strip()
            fields.setdefault(cur, []).extend(rest.split())
    return fields


@functools.lru_cache(maxsize=1)
def library_flags():
    """`{lib-file: [flag …]}` — the `flags:` field of every `.agda-lib` in this repo.

    These are the flags AGDA applies library-wide; a module inside the library gets
    them whether or not its own pragma names them.
    """
    return {os.path.basename(p): _agda_lib_fields(p).get("flags", [])
            for p in sorted(glob.glob(os.path.join(_ROOT, "agda", "*.agda-lib")))}


@functools.lru_cache(maxsize=1)
def cmdline_flags():
    """`AGDA_FLAGS` as the GENERATOR declares it — read from its AST, not its output.

    ⚑ `scripts/gen_build_makefiles.py` IS THE AUTHORITY AND `agda/Flat.mk` IS A
    DERIVED VIEW.  Reading the makefile would make this census agree with a file
    that a regeneration can change under it; reading the generator's own string
    literal keeps the answer pinned to the thing that decides.
    """
    import ast
    src = open(os.path.join(_ROOT, "scripts", "gen_build_makefiles.py"),
               errors="replace").read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            m = re.match(r"AGDA_FLAGS\s*\?=\s*(.*)$", node.value.strip())
            if m:
                return m.group(1).split()
    return []


def global_flags():
    """`{flag: origin}` — every flag the build applies to EVERY module, with WHERE
    it comes from.  The origin is load-bearing: it says which invocations carry it.
    """
    out = {}
    for f in cmdline_flags():
        out[f] = "AGDA_FLAGS (gen_build_makefiles.py — make recipes only)"
    for lib, flags in library_flags().items():
        for f in flags:
            out[f] = f"{lib} flags: (library-wide — every agda invocation)"
    return out


def flag_census(prefix=None):
    """Which modules' local `{-# OPTIONS #-}` do NOT reflect the global flag set.

    ⚑ A MODULE WITH NO PRAGMA AT ALL IS A FINDING, NOT A SKIP.  It reflects none of
    the global flags, and dropping it from the census is the shape that reports a
    thing never looked at as a thing found clean.

    Returns `{module: {"options": [...], "missing": [...], "extra": [...],
    "pragma": bool}}` for modules with a NON-EMPTY `missing`, plus the keys
    `_scanned` (modules examined) and `_global` (the reference set, with origins).
    `missing` is the global flags the file does NOT name; `extra` is what it names
    beyond them.
    """
    gl = global_flags()
    out = {"_scanned": 0, "_global": gl}
    for p in sorted(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)):
        mod = module_path(p, AG)
        if prefix is not None and not (mod == prefix
                                       or mod.startswith(prefix + ".")):
            continue
        out["_scanned"] += 1
        src = open(p, errors="replace").read()
        opts, seen = [], False
        for name, arg in _PRAGMA.findall(src):
            if name == "OPTIONS":
                seen = True
                opts = " ".join(arg.split()).split()
        missing = [f for f in gl if f not in opts]
        if missing:
            out[mod] = {"options": opts, "missing": missing, "pragma": seen,
                        "extra": [o for o in opts if o not in gl]}
    return out


def consumer_profile(prefix, depth=3):
    """The AGGREGATED consumed-by view: who takes from this subtree, and what.

    ⚑ AN EDGE DUMP IS NOT AN ANSWER.  `--importers Substrate.WitnessTower` emits
    92 external + 1527 internal edges — 164 KB, which is a fact re-derived by eye
    every time it is read.  The QUESTIONS are "which packages consume this?" and
    "which of its modules are the load-bearing exports?", and both are aggregations.
    Collapsing them in the turn is exactly the judgement-not-codified shape.

    Returns (by_package, by_target): each a sorted [(name, count)], descending.
    `by_package` truncates the importer to `depth` dotted segments; `by_target`
    is the full tower-side module.  EXTERNAL importers only — an internal edge
    says nothing about what the cluster is FOR.
    """
    by_pkg, by_tgt = collections.Counter(), collections.Counter()
    for s, t in importers_of(prefix):
        if s == prefix or s.startswith(prefix + "."):
            continue
        by_pkg[".".join(s.split(".")[:depth])] += 1
        by_tgt[t] += 1
    return (sorted(by_pkg.items(), key=lambda kv: (-kv[1], kv[0])),
            sorted(by_tgt.items(), key=lambda kv: (-kv[1], kv[0])))


def dependency_profile(prefix, depth=3):
    """The mirror of `consumer_profile`: what this subtree DEPENDS ON, aggregated.

    Answers "what does the tower consume, by cluster" — the `Algebra.F2` /
    `Groups.*` / `Foundation.*` question — and separates AUTHORITIES (one module,
    many importers within the subtree) from incidental one-off dependencies.

    Returns (by_package, by_module): sorted [(name, count)] descending, where the
    count is the number of DISTINCT subtree members importing it.
    """
    by_pkg, by_mod = collections.Counter(), collections.Counter()
    for mod, imps in import_index().items():
        if not (mod == prefix or mod.startswith(prefix + ".")):
            continue
        for i in dict.fromkeys(imps):
            if i == prefix or i.startswith(prefix + "."):
                continue
            by_pkg[".".join(i.split(".")[:depth])] += 1
            by_mod[i] += 1
    return (sorted(by_pkg.items(), key=lambda kv: (-kv[1], kv[0])),
            sorted(by_mod.items(), key=lambda kv: (-kv[1], kv[0])))


def modules_under(prefix):
    """Every corpus module under `prefix` (the subtree enumeration)."""
    return sorted(m for m in import_index()
                  if m == prefix or m.startswith(prefix + "."))


def _in_subtree(mod, prefix):
    return mod == prefix or mod.startswith(prefix + ".")


_QUALIFIED = re.compile(r"^\s*import\s+(Substrate[\w.]*)\s+as\s+(\S+)\s*$")

# A token that LOOKS like a renamed alias: contains a script/symbol character, so
# it cannot be a stdlib primitive or an ordinary ASCII identifier that the index
# might legitimately not carry.  ⚑ DELIBERATELY NARROW — see `orphan_names`.
_ALIASY = re.compile(r"[^\x00-\x7F]")

# ⚑ AGDA'S OWN TYPE-LEVEL SYNTAX IS NON-ASCII, so `_ALIASY` matches it and a first
# cut reported `→` 115 times as an undefined name.  `_KEYWORDS` above is the
# DECLARATION keyword set (`private`, `field`, …) and does not cover these — two
# different vocabularies, and reusing the wrong one is why the false positives got
# through.  Level variables are conventional, not defined, so they belong here too.
_SYNTAX = {"→", "∀", "λ", "Set", "Setω", "Prop", "=", "->", "∃", "Σ", "×", "⊔",
           "ℓ", "ℓ′", "ℓ₁", "ℓ₂", "ℓ₃", "a", "b", "c", "n", "m", "…", "..", "...",
           "@", "|", "record", "where", "with", "rewrite", "let", "in", "do"}


_FLATVAR = re.compile(r"^\s*(?:private\s+)?variable\s+.*:.*\S\s+\S+\s*:")


def flat_variable_blocks(prefix=None):
    """A `variable` block FLATTENED onto one line — unparseable, and systemic.

    ⚑ A SPLITTER DEFECT, NOT AN AUTHORING ONE. The horizontal one-lemma-per-file
    split emits each unit's preamble on a single line, which is fine for imports
    and fatal for a `variable` block: Agda needs one `names : type` group per line,
    so four groups run together produce [ParseError] at the second colon —
    `Set W₂ :`. Every affected file fails at the SAME column of the SAME line.

    ⚑ AND IT IS INVISIBLE TO EVERY OTHER CENSUS HERE. `--dangling` sees imports,
    `--qualified` sees aliases, `--prose` reads comments; a malformed declaration is
    none of those. Found only because a dangling repair walked into one, and then
    the next file in the same chain had it too — which is the tell for systemic
    rather than incidental.

    Returns [(path, line_no, text)].
    """
    out = []
    for p in agda_lex.agda_files(AG):
        mod = module_path(p, AG)
        if prefix and not (mod and _in_subtree(mod, prefix)):
            continue
        try:
            lines = open(p).read().split("\n")
        except Exception:
            continue
        for n, line in enumerate(lines, 1):
            if _FLATVAR.match(line):
                out.append((p, n, line.strip()))
    out.sort()
    return out


def variable_declarations(prefix=None):
    """name -> [modules declaring it in a `variable` block] — the index's blind spot.

    ⚑ `def_index` DOES NOT CARRY GENERALIZABLE VARIABLES, so `agda_defs S₁` reports
    "no definer in agda/Substrate" for a name declared in five modules. Every census
    built on that index is blind to them, which is how a split copied one `variable`
    preamble into a whole cluster and nothing noticed for as long as `private` kept
    each copy invisible.

    ⚑ THE DUPLICATION IS ONLY LATENT UNTIL THE MODULES MEET. Two leaves each
    declaring `S₁` are fine in isolation and become [AmbiguousName] the moment a
    third imports both — so the defect surfaces during rewiring, far from the split
    that caused it, one compile at a time. This is the reader that makes the whole
    cohort visible before any of it is touched.

    Reports only names declared in MORE THAN ONE module: a single declaration is the
    normal case and not debt.
    """
    decl = collections.defaultdict(set)
    for p in agda_lex.agda_files(AG):
        mod = module_path(p, AG)
        if prefix and not (mod and _in_subtree(mod, prefix)):
            continue
        try:
            lines = open(p).read().split("\n")
        except Exception:
            continue
        inblock = False
        for line in lines:
            s = line.strip()
            if re.match(r"^(?:private\s+)?variable\b", s):
                inblock = True
                rest = re.sub(r"^(?:private\s+)?variable\s*", "", s)
                if rest and ":" in rest:
                    for nm in rest.split(":")[0].split():
                        decl[nm].add(mod)
                continue
            if inblock:
                if not line[:1].isspace() or not s:
                    inblock = False
                    continue
                if ":" in s:
                    for nm in s.split(":")[0].split():
                        decl[nm].add(mod)
    rows = [(n, sorted(ms)) for n, ms in decl.items() if len(ms) > 1]
    rows.sort(key=lambda kv: (-len(kv[1]), kv[0]))
    return rows


def repair_flat_variables(prefix=None, apply=False):
    """Re-expand a flattened `variable` block to one `names : type` group per line.

    ⚑ THE SPLIT POINT IS BEFORE THE NAMES THAT PRECEDE A COLON. In
    `variable A B : Set W₁ : S₁ → T₁ → Set`, the tokens `A B` belong to `: Set` and
    `W₁` starts the next group — so a group ends at the last whitespace-run before
    each `:` after the first. Scanning colons rather than guessing at arrows is what
    makes this exact: an arrow appears INSIDE a group's type and must not split it.

    ⚑ `private` IS DROPPED, not preserved. It is banned on Substrate declarations,
    and on a `variable` block it never meant anything — those names are not exported
    under any modifier. So the ban's remedy and the parse repair coincide again.
    """
    plan = []
    for p, n, _txt in flat_variable_blocks(prefix):
        lines = open(p).read().split("\n")
        line = lines[n - 1]
        indent = line[:len(line) - len(line.lstrip())]
        body = line.lstrip()
        body = re.sub(r"^(?:private\s+)?variable\s+", "", body)
        # positions of every top-level colon (none appear inside these types)
        cols = [i for i, ch in enumerate(body) if ch == ":"]
        groups, start = [], 0
        for k, c in enumerate(cols):
            if k + 1 < len(cols):
                nxt = cols[k + 1]
                # the next group's NAMES are the final whitespace-run before `nxt`
                seg = body[c + 1:nxt]
                cut = seg.rstrip().rfind(" ")
                if cut < 0:
                    continue
                end = c + 1 + cut
                groups.append(body[start:end].strip())
                start = end
            else:
                groups.append(body[start:].strip())
        if len(groups) < 2:
            continue
        new = [indent + "variable"] + [indent + "  " + g for g in groups]
        plan.append((p, n, groups))
        if apply:
            out = lines[:n - 1] + new + lines[n:]
            open(p, "w").write("\n".join(out))
    return plan


def orphan_names(prefix=None):
    """⚑⚑ RETAINED AS A NEGATIVE RESULT. THIS MODE DOES NOT WORK — DO NOT REBUILD IT.

    THE QUESTION IT WAS BUILT FOR IS REAL: the import ban's sweep removed
    `renaming (_≤_ to _ℕ≤_)` and `renaming (_+_ to _+F_)` without rebinding, leaving
    `ℕ≤` and `+F` at use sites with no provider. Three such were found this session,
    each by a BUILD FAILURE rather than a query, and each cost a round-trip.

    THE METHOD CANNOT ANSWER IT. Measured tree-wide after two rounds of tightening:
    115 names, 416 sites, and on inspection **ZERO true findings**. Three
    irreducible sources of noise, none removable by a better filter:

      * QUALIFIED NAMES (`S₃.Carrier`, `Z₃-Base.Gen`, `R.f₁`, `V₄.e` — the bulk).
        The index stores UNQUALIFIED names, so every `Alias.name` reads as
        undefined. Resolving them means resolving the alias, i.e. reimplementing
        Agda's scope checker.
      * MODULE-PARAMETER BINDERS (`W₁`, `ℓM`, `n₁`). In scope from the module
        header, which a per-line scan does not carry.
      * LOCAL BINDERS in `where`/`let`/patterns (`b₁`, `p₁₂`). Structurally
        invisible to a token scan — the first cut scanned bodies and returned 220
        sites of pure noise.

    ⚑ THE LAST SURVIVING CANDIDATE WAS ALSO FALSE: `F2.F₂` at `DLogHom.agda:111`
    looked like the real class and the file compiles at exit 0.

    ⚑ SO THE HONEST INSTRUMENT IS THE COMPILER, and it already exists: a
    [NotInScope] naming the token, from `split_pipeline --why`. It resolves aliases
    and binders because it IS the scope checker. What a census would add is finding
    them all at once WITHOUT a build — and that is not reachable from the index.
    Filed rather than deleted so the next reader does not re-derive the same
    tightening loop; `--clause-audit` reached 185 false positives the same way.

    Kept callable so its selftest arms keep asserting the shape of the noise; NOT
    wired to act on, and the CLI prints the bound before the rows.
    """
    idx = def_index()
    known = set(idx)
    # every locally-bound name in a file is not an orphan; the local scan the
    # clause-audit already owns supplies them.
    out = collections.defaultdict(list)
    for p in agda_lex.agda_files(AG):
        mod = module_path(p, AG)
        if prefix and not (mod and _in_subtree(mod, prefix)):
            continue
        try:
            src = open(p).read()
        except Exception:
            continue
        lines = src.split("\n")
        try:
            hdr = next(i for i, l in enumerate(lines) if l.startswith("module "))
        except StopIteration:
            continue
        spans = agda_lex.module_scopes(src) if hasattr(agda_lex, "module_scopes") else {}
        masked = agda_lex.mask_comments("\n".join(lines[hdr:])).split("\n")
        local = set(_local_defs(src))
        for n, line in enumerate(masked, hdr + 1):
            # ⚑ COLUMN-0 SIGNATURES ONLY. An indented line may be a clause body or
            # a `where` block, both of which introduce binders this cannot see.
            if not line or line[0].isspace():
                continue
            s = line.lstrip()
            if s.startswith(("import ", "open import ", "open ", "module ",
                             "data ", "record ", "postulate", "infix", "{-#")):
                continue
            if " : " not in line:
                continue
            head, _, typ = line.partition(" : ")
            # names bound BY THIS SIGNATURE — implicits `{x : A}` and explicits
            # `(y : B)` — are in scope for the rest of it.
            bound = set(re.findall(r"[{(]\s*([^:{}()]+?)\s*:", typ))
            bound = {w for grp in bound for w in grp.split()}
            for tok in re.findall(r"[^\s(){}\[\];,]+", typ):
                if not _ALIASY.search(tok) or tok in _KEYWORDS or tok in _SYNTAX:
                    continue
                if tok in known or tok in local or tok in bound:
                    continue
                bare = tok.strip("_")
                if (not bare or bare in known or bare in local or bare in bound
                        or bare in _KEYWORDS or bare in _SYNTAX):
                    continue
                if any(f in known for f in agda_lex.mixfix_forms(bare)):
                    continue
                out[bare].append((p, n))
    rows = sorted(((t, sorted(set(sites))) for t, sites in out.items()),
                  key=lambda kv: (-len(kv[1]), kv[0]))
    return rows


def qualified_aliases(paths=None):
    """`import M as Q` on a Substrate module — the form BOTH censuses are blind to.

    ⚑ THIS EXISTS BECAUSE THE OTHER TWO MODES REPORTED CLEAN ON A BROKEN FILE.
    `--dangling` and `--unused-imports` both read `open import`; a QUALIFIED alias
    is a different statement and neither sees it, nor the `Q.name` use sites it
    creates.  Measured: `rewire_to_leaves` declined all 11 consumers of the deleted
    `Algebra.F2` barrel and reported `0 importer(s)` — a true statement about what
    it rewrites, read as "nothing to do".  The repair is not a rewire: the import
    AND every use site must change together, which is why the rewire tool is right
    to refuse it.

    ⚑ AND `as` IS BANNED ON SUBSTRATE IMPORTS, so this census is also the ban's
    remaining population — the two questions have one answer.

    Returns [(path, line_no, module, alias, target_exists)] — `target_exists`
    separates "banned but working" from "banned AND dangling", which are different
    urgencies and must not be summed.
    """
    have = set(import_index())
    out = []
    for p in (paths if paths is not None else agda_lex.agda_files(AG)):
        try:
            lines = open(p).read().split("\n")
        except Exception:
            continue
        for n, line in enumerate(lines, 1):
            m = _QUALIFIED.match(line)
            if m:
                out.append((p, n, m.group(1), m.group(2), m.group(1) in have))
    out.sort()
    return out


def _alias_pattern(alias):
    """THE one regex for `<alias>.name`, shared by the scan and the rewrite.

    ⚑ IT EXISTS BECAUSE THE TWO PATHS DRIFTED. `qualified_repair` had this pattern
    written out three times — once to FIND the names and twice to REWRITE them —
    and a capture fix reached only the rewrite copies. The scan then recorded a
    different set of names than the substitution replaced, so a repaired file kept
    some qualified references and lost others: `AES/KeySchedule.agda` lost every
    `F2.𝟘` and kept every `F2.𝟙`, uncompilable, while the suite stayed green.

    ⚑ THE BOUNDARY RULES, both measured:
      * NOT preceded by a word char or dot — `F2.` occurs literally inside
        `Substrate.Algebra.F2.Polynomial`, and a bare scan reported phantom names
        and refused ten files for a defect of its own.
      * The name ENDS at the token boundary — `∷` and other operators are not in
        the exclusion class, so a greedy capture on `F2.𝟙 ∷ F2.𝟘` can run past the
        first name into the next reference.
    """
    return (r"(?<![\w.])" + re.escape(alias)
            + r"\.([^\s(){}\[\];,]+?)(?=[\s(){}\[\];,]|$)")


def _alias_refs(alias, text):
    """Every name referenced through `alias` in `text` — the scan half."""
    return re.findall(_alias_pattern(alias), text)


def double_route_names(generic, leaf_prefix, paths=None):
    """Modules reaching ONE name by TWO routes — a generic re-export AND a leaf.

    ⚑ THE COHORT `--reexports` CANNOT SEE, because neither route is malformed.
    `Graded.FromCommRing.Over` re-exports a CommRing's coefficient names (`𝟘 𝟙
    _+_ +-assoc +-comm +-identityˡ *-absorbˡ`, :45-79) as field-projection
    definitions.  Applied at `F₂-CommRing` those ARE F₂'s names — so a module that
    both applies `F.Over` and opens an `Algebra.F2.*` leaf has two paths to one
    theorem, and agda reports [AmbiguousName] at the first use site.  Each file
    compiles alone; the collision exists only in the combination.

    ⚑ AND THE BAN FORBIDS THE OBVIOUS FIX.  `using`/`renaming` would disambiguate
    and are banned, so the interim repair is to drop the redundant leaf import and
    let the generic be the sole provider.  The DURABLE fix is upstream: split
    `FromCommRing` so bare imports carry individual symbols, at which point `as`
    becomes permissible for disambiguation (operator's framing).

    ⚑ FOUND BY COMPILING, THREE TIMES, BEFORE THIS EXISTED — `BezoutFold/Base`,
    `BezoutFold`, `ComputeTrace`.  35 modules apply `F.Over`; one build failure at
    a time is the shape the standing rule forbids.

    Returns [(module, [leaf modules also opened])] for every module importing BOTH
    the generic and at least one leaf under `leaf_prefix`.
    """
    idx = import_index()
    rows = []
    for mod, imps in idx.items():
        if paths is not None and mod not in paths:
            continue
        seen = dict.fromkeys(imps)
        if generic not in seen:
            continue
        leaves = [i for i in seen if _in_subtree(i, leaf_prefix)]
        if leaves:
            rows.append((mod, sorted(leaves)))
    rows.sort(key=lambda kv: (-len(kv[1]), kv[0]))
    return rows


def qualified_repair(target, apply=False, paths=None):
    """Strip `import <target> as Q` AND its `Q.name` use sites, together.

    ⚑ THE TRANSFORM `rewire_to_leaves` CORRECTLY REFUSES.  That tool rewrites
    `open import` statements; a qualified alias additionally creates `Q.name`
    references throughout the body, and changing the import without them leaves
    the file worse than before (measured: deleting the line in `GF16DLog` left
    `F2.F₂` unbound at :47).  The import and the use sites are ONE edit.

    ⚑ AND IT RESOLVES EACH NAME AT ITS OWN HOME, not at the dead parent's.  A
    dissolved barrel's names live in DIFFERENT leaves — `F₂`/`𝟘`/`𝟙` in
    `Algebra.F2.F2`, `_+F_` in `Algebra.F2.PlusF` — so one replacement import is
    wrong in general.  Each stripped name is looked up through `def_index` and the
    leaf that provides it is imported.

    ⚑ REFUSES rather than guesses when a name has NO home or SEVERAL.  A name the
    index cannot place is reported and the file is left alone: a wrong import
    compiles until it does not, and this tool exists because a plausible-looking
    edit already cost one round.

    Returns [(path, [(name, home)], [unresolved])] — the plan, or the applied set.
    """
    idx = def_index()
    rx_imp = re.compile(r"^\s*import\s+" + re.escape(target) + r"\s+as\s+(\S+)\s*$")
    plan = []
    for p in (paths if paths is not None else agda_lex.agda_files(AG)):
        try:
            src = open(p).read()
        except Exception:
            continue
        lines = src.split("\n")
        alias = None
        imp_line = None
        for n, line in enumerate(lines):
            m = rx_imp.match(line)
            if m:
                alias, imp_line = m.group(1), n
                break
        if alias is None:
            continue
        # every `alias.name` reference in the body, comments masked so a mention
        # in prose does not manufacture an import.
        # ⚑ THE ALIAS MUST NOT MATCH INSIDE A DOTTED PATH, and a first cut did.
        # `F2.` occurs literally inside `Substrate.Algebra.F2.Polynomial.…`, so a
        # bare `alias\.` scan reported `Polynomial.Wedge.GUnit` as a "name used
        # through the alias" and the tool refused ten files for a defect of its
        # own. The refusals looked like findings about the corpus — the exact
        # method-reported-as-substrate shape. Require a non-dot, non-word boundary
        # BEFORE the alias, and stop the captured name at the first dot so a real
        # submodule reference (`F2.AES.Round`) is reported as `AES.Round` and
        # refused honestly rather than silently truncated to `AES`.
        # ⚑⚑ THE READ AND WRITE PATHS MUST USE THE *SAME* PATTERN, and for one
        # round they did not. A fix to the capture was applied to the two write-path
        # copies and MISSED THIS ONE, so the scan and the substitution disagreed
        # about where a name ends: `used` was built by one regex and the rewrite
        # driven by another. That is how `AES/KeySchedule.agda` lost every `F2.𝟘`
        # and kept every `F2.𝟙` — not a greedy-capture bug and not a line filter,
        # which were my two wrong guesses, but TWO SPELLINGS OF ONE RULE, the
        # `agda_files()`-was-four-bodies shape inside a single function.
        used = sorted(set(_alias_refs(alias, agda_lex.mask_comments("\n".join(lines)))))
        # ⚑ THE ALIAS SCOPES THE LOOKUP, and omitting that made every file refuse.
        # `F2.𝟘` cannot mean `Wedge.Mul`'s `𝟘` — the qualifier NAMES the subtree it
        # came from, so a name with four tree-wide homes has exactly one home
        # *under the target*. A first cut looked the name up globally, reported
        # `4 home(s)`, and refused all ten files: the ambiguity was real in the
        # index and absent at the use site. Prefer the target's subtree; fall back
        # to a global unique hit only when the subtree provides nothing (the
        # barrel may have re-exported from elsewhere).
        homes, unresolved = {}, []
        for nm in used:
            owners = sorted(idx.get(nm, ()))
            local = [o for o in owners if _in_subtree(o, target)]
            if len(local) == 1:
                homes[nm] = local[0]
            elif not local and len(owners) == 1:
                homes[nm] = owners[0]
            else:
                unresolved.append((nm, local or owners))
        plan.append((p, sorted(homes.items()), unresolved))
        # ⚑ ZERO USE SITES: the alias is DEAD and the import is deleted outright.
        # The first cut wrote only when `used` was non-empty, so three FUSepQ files
        # whose alias was never referenced kept a DANGLING import and stayed broken
        # — the repair reported "applied to 4" while fixing 1. Caution about the
        # zero case is right in general (a name might be reached a way this does
        # not model) but a dangling import is broken EITHER WAY: if the alias is
        # unused the line is pure debt, and if it is used the build already fails.
        if apply and not used and not unresolved:
            new = [l for n, l in enumerate(lines) if n != imp_line]
            open(p, "w").write("\n".join(new))
        if apply and used and not unresolved:
            # ⚑ REWRITE ONLY CODE LINES.  A file-wide `re.sub` would also strip the
            # qualifier inside COMMENTS, and this repo's comments are its incident
            # log — a transform that keeps code and rewrites commentary destroys the
            # more valuable half (`pycodemod --roundtrip` exists for exactly this).
            # A comment naming `F2.F₂` is describing the OLD state and must survive
            # verbatim, so the mask decides per line.
            # ⚑⚑ NEVER REWRITE AN IMPORT OR MODULE LINE, AND THIS COST A REVERT.
            # A first cut rewrote every line the comment-mask called code, which
            # includes `module Substrate.Algebra.F2.Polynomial.…` and every
            # `open import Substrate.Algebra.F2.CommRing`. Those contain the alias
            # as a PATH SEGMENT, not a use site, so the substitution turned the
            # module's own name into `Substrate.Algebra.Polynomial.…` and silently
            # repointed a sibling import. Ten files written, caught by the FIRST
            # compile: [ModuleNameDoesntMatchFileName].
            #
            # ⚑ AND THE SUITE WAS GREEN THROUGHOUT — 174/174 — because every case
            # tested the CENSUS (`qualified_aliases`) and none tested the
            # TRANSFORM. That is `friction-a-verification-that-cannot-fail`, the
            # class this session filed to the floor an hour earlier, recurring in
            # the tool written after filing it. The arms below are the missing ones.
            masked = agda_lex.mask_comments("\n".join(lines)).split("\n")
            new = []
            for n, line in enumerate(lines):
                if n == imp_line:
                    new.append("\n".join(
                        f"open import {h}" for h in sorted(set(homes.values()))))
                    continue
                # ⚑ ONLY THE *TOP-LEVEL* module line is a pure path. A first cut
                # skipped every line starting `module `, and a NESTED
                # `module Over (m-lo : Vec F2.F₂ …) where` has genuine use sites in
                # its TELESCOPE — one survived, and the compiler named it at :52.
                # The top-level declaration is the one whose name must match the
                # file; a nested one is a scope with parameters.
                # ⚑⚑ AND A THIRD SHAPE WAS MISSED: CLAUSE BODIES. An earlier cut
                # additionally required `" : " in line`, on the theory that the
                # type half is where qualified names live. `rc1 = F2.𝟙 ∷ 𝟘 ∷ …`
                # has no colon, so ten such lines in `AES/KeySchedule.agda` kept
                # `F2.𝟙` after the import was stripped — a file left WORSE than
                # before, and invisible to `--qualified` (which reads import
                # statements, and the import was already gone). Every non-
                # declaration line is a candidate; the alias boundary is what
                # keeps a path segment from matching.
                stripped = line.lstrip()
                is_decl = (stripped.startswith("import ")
                           or stripped.startswith("open import ")
                           or (line.startswith("module ") and n < imp_line))
                if masked[n].strip() and not is_decl:
                    # ⚑⚑ THE CAPTURE MUST STOP AT THE ALIASED NAME, and a greedy
                    # `[^\s(){}\[\];,]+` did not. On `rc = F2.𝟙 ∷ F2.𝟘 ∷ …` the
                    # first match ran from `𝟙` through `∷` and into the NEXT
                    # `F2.𝟘` (none of `∷`, `F`, `2`, `.` are excluded), so one
                    # substitution consumed several names and the survivors read
                    # as "only some were stripped". Excluding the alias's own dot
                    # is not enough — the name must end where the token does.
                    new.append(re.sub(_alias_pattern(alias), r"\1", line))
                else:                            # declaration, comment, or blank
                    new.append(line)
            open(p, "w").write("\n".join(new))
    return plan


def dangling_imports(paths=None):
    """Every `open import M` where M HAS NO SOURCE FILE — the dissolved-parent census.

    ⚑ THE CLASS THIS EXISTS FOR, MEASURED FOUR TIMES BY HAND IN ONE SESSION.  A
    decomposition splits `M` into `M.Leaf1..LeafN` and DELETES `M.agda`, but the
    consumers still `open import M`.  Agda reports [FileNotFound] — at BUILD time,
    one module per build, so the tree yields them one failure at a time over hours.
    `LehmerTowerMorphism` (9 consumers), `Foundation.Eq`'s moved `cong₂`, and two
    `Algebra.F2` sites were each found that way; this mode finds the rest at once.

    ⚑ AND `--importers <Pfx>` IS NOT THIS QUESTION, which is why the census kept
    being deferred.  It matches a PREFIX, so asking it about `Substrate.Algebra.F2`
    returns every edge into the 369-module subtree (695 KB) — a true answer to a
    different question, and the exact `--calls emit` shape.  Here the test is
    EXACT-MODULE plus FILE-ABSENT.

    ⚑ ABSENT means absent from THIS corpus.  A module resolved from the Agda
    library path (`Agda.Primitive`, stdlib) has no file under `agda/` either, so
    only `Substrate.*` targets are judged — anything else is reported UNJUDGED
    rather than dangling, because "I cannot see it" is not "it does not exist".

    Returns (dangling, unjudged): dangling is [(target, [importers])] sorted by
    descending importer count.
    """
    idx = import_index()
    have = set(idx)
    dangling, unjudged = collections.defaultdict(list), collections.Counter()
    for mod, imps in idx.items():
        if paths is not None and mod not in paths:
            continue
        for i in dict.fromkeys(imps):
            if i in have:
                continue
            if not i.startswith("Substrate."):
                unjudged[i] += 1
                continue
            # a module with an index entry but no readable file is ALSO dangling;
            # `have` is keyed on what the index parsed, so absence from it is the
            # test.  Confirm against the filesystem so a stale index cannot invent
            # a dangling edge.
            _fp = agda_lex.module_file(i, AG)
            if _fp and os.path.isfile(_fp):
                continue
            dangling[i].append(mod)
    rows = sorted(((t, sorted(ms)) for t, ms in dangling.items()),
                  key=lambda kv: (-len(kv[1]), kv[0]))
    return rows, sorted(unjudged.items(), key=lambda kv: (-kv[1], kv[0]))


def unused_imports(paths):
    """Imports a module names but does NOT reference — the census, never a write.

    ⚑ THIS DELEGATES TO `prune_imports.should_keep` AND MUST CONTINUE TO.  That
    predicate is the authority, and its docstring is an incident log of two
    REVERTED sharpenings (F29 unique-provision: 13 of 20 leaves broke; F30
    shared-name subtraction lost to a dead store).  Re-deriving the rule here
    would re-run those experiments with the results already written down.

    ⚑⚑ AND THE PRECEDENT FOR GETTING THIS WRONG IS IN THIS FILE.  `--clause-audit`
    was written without `prune_imports`' three tokenizer recoveries and
    IMMEDIATELY reproduced the `_,_` bug — reporting the import at
    `Quotient/CRT.agda:36` as UNUSED while it is used at :83 and :85.  The fixes
    were documented in a file its author had read; documentation in one place is
    not the same as one implementation.  So the scan below calls
    `prune_imports.prune(..., apply=False)` rather than tokenizing again.

    ⚑ THE ASYMMETRY INVERTS FROM THE PRUNE'S, AND THAT IS WHY THIS IS A SEPARATE
    ENTRY POINT RATHER THAN A FLAG.  `prune` is keep-biased because a false DROP
    breaks the build; every uncertain branch returns keep.  A CENSUS inherits that
    bias, which makes it CONSERVATIVE: what it reports is a lower bound on the
    unused set, and a name it stays silent about is "no evidence", never "used".
    Report it that way — the count is a floor, not a total.

    Returns [(path, [(line_no, module_imported)])] for modules with ≥1 droppable
    import, sorted by descending count.
    """
    import prune_imports as _pi
    idx = def_index()
    prov_cache = {}
    out, barrels, unreadable = [], [], []
    for p in paths:
        try:
            drops = _pi.prune(p, idx, prov_cache, apply=False, detail=True)
        except Exception:
            # ⚑ A FILE THE PRUNE CANNOT PARSE IS NOT A FILE WITH NO UNUSED
            # IMPORTS.  Collected and REPORTED, never silently skipped: the
            # difference between "clean" and "not examined" is the whole
            # difference between a census and a false zero.
            unreadable.append(p)
            continue
        if drops == [_pi._BARREL]:
            barrels.append(p)
        elif drops:
            out.append((p, drops))
    out.sort(key=lambda kv: (-len(kv[1]), kv[0]))
    return out, barrels, unreadable


def edges_between(src_prefix, dst_prefix):
    """Every import edge FROM the `src_prefix` subtree INTO the `dst_prefix` one.

    ⚑ BUILT BECAUSE THE DIRECTION QUESTION HAD NO READER, AND THE ABSENCE READ AS
    AN ANSWER.  `--consumers`/`--depends` AGGREGATE by package, which answers "how
    much does the tower lean on F2" (167) but NOT "which tower modules, through
    which F2 modules" — the only form in which a re-derivation can be planned.
    Asked without this mode, the question fell through to `--importers`, which
    returned every importer tree-wide (35.9 KB) and answered a different question
    convincingly.  That is the `--calls emit` shape: a fact about the METHOD
    reported as a fact about the SUBSTRATE.

    Returns (edges, by_dst, by_src): the explicit (src, dst) pairs, plus the two
    marginal counts.  Both directions are worth asking, so this is deliberately
    NOT symmetric-by-default: `edges_between(A, B)` and `edges_between(B, A)` are
    different questions and a caller comparing them is measuring the INVERSION.
    """
    edges = []
    for mod, imps in import_index().items():
        if not _in_subtree(mod, src_prefix):
            continue
        for i in dict.fromkeys(imps):
            if _in_subtree(i, dst_prefix):
                edges.append((mod, i))
    edges.sort()
    by_dst, by_src = collections.Counter(), collections.Counter()
    for s, d in edges:
        by_dst[d] += 1
        by_src[s] += 1
    return (edges,
            sorted(by_dst.items(), key=lambda kv: (-kv[1], kv[0])),
            sorted(by_src.items(), key=lambda kv: (-kv[1], kv[0])))


# ⚑⚑⚑ ⟡mode-standardize / Ⓢ1e — THE DECLARED MODE ROSTER for the Agda-source authority.
# 23 modes had curated usage text; 14 more DISPATCHED in no usage line at all, so
# `toolmodes --find repair` could not reach the repair tools this file owns.
#
# ⚑⚑ THE WRITE SET IS DERIVED FROM TWO INDEPENDENT READINGS, NEVER FROM THE NAMES. I have
# been wrong twice this session inferring a field from a mode's spelling (`schema
# --establish` arity, `schema --transport` effect), so:
#   · `--guarded guard` → the 5 sites arming `edit_snapshot.guard` (the in-place-editor
#     precondition every Agda writer here must satisfy);
#   · `--binding apply` → the 6 functions taking an `apply` parameter.
# The two agree, and their union is what carries `writes=(".agda",)` below.
#
# ⚑ `--repair` AND `--apply` ARE MODIFIERS, NOT MODES. `--repair` qualifies
# `--flat-variable` (`:4562`); `--apply` is the corpus-wide mutation convention. Declaring
# them as `opts` of their owner is what stops `contract_rows` reading them as undeclared
# top-level modes — the distinction that resolved `schema --emit`/`--reap`.
# ⚑ `sys`, NOT `_sys` — the underscore alias is bound inside the `__main__` guard only,
# and reaching for it at module scope raised `NameError` at import. Same shape as `os` in
# `schema.py`: an alias that exists in the dispatch does not exist in the module.
import os.path as _osp
sys.path.insert(0, _osp.join(_osp.dirname(_osp.dirname(_osp.abspath(__file__))), "scripts"))
from climode import Mode                                                   # noqa: E402

MODES = {
    # ── the name index ─────────────────────────────────────────────────────────
    "--provides": Mode(operand="<Mod>", why="what does this module define"),
    "--grep": Mode(operand="<regex>", why="what NAMES look like this"),
    "--prose": Mode(operand="<regex> [<Pfx>]",
                    why="what the COMMENT TEXT says — the half --grep cannot see"),
    "--collide": Mode(paths=True, why="names defined in more than one module"),
    "--orphans": Mode(paths=True, why="defined names with no reference anywhere"),
    # ── import edges ───────────────────────────────────────────────────────────
    "--imports": Mode(operand="<Mod>", why="what does this module import"),
    "--importers": Mode(operand="<Pfx>", why="what imports this subtree (consumed-by)"),
    "--consumers": Mode(operand="<Pfx>", why="consumed-by, AGGREGATED by package"),
    "--depends": Mode(operand="<Pfx>", why="depends-on, AGGREGATED by package"),
    "--between": Mode(operand="<Src> <Dst>",
                      why="every edge FROM one subtree INTO another — ORDER IS THE "
                          "QUESTION; running both ways is how an inversion is measured"),
    "--closure": Mode(operand="<Mod>", opts=("--prefix",),
                      why="transitive import closure"),
    "--cluster": Mode(operand="<Pfx>", why="leaf/hub/spine edge measurement"),
    "--under": Mode(operand="<Pfx>", why="every module in the subtree"),
    "--depth": Mode(operand="[<Pfx>]", why="import-DAG depth per module"),
    # ⚑ NO OPERAND AND NO `paths` — the question is about the WHOLE graph. A cycle is a
    # property of the edge set, so scoping the census to a subtree could only ever hide
    # one that leaves and re-enters. Exits 1 when any cycle exists: an import cycle is a
    # build failure waiting, not a report.
    "--cycles": Mode(why="import CYCLES over the whole graph — the batch-of-edits "
                         "question the three `_would_cycle` copies cannot answer, "
                         "since they sample one edge at a time"),
    # ⚑ THE SCC SIZE IS NOT THE PROBLEM SIZE. One wrong-direction edge absorbs a whole
    # DAG into a component, so the actionable figure is the FEEDBACK ARC SET.
    "--cycle-cuts": Mode(why="per SCC, the MINIMAL edge set whose removal breaks the "
                             "cycle — exact by search where affordable, labelled "
                             "`greedy` where not, never a heuristic passed off as a "
                             "minimum"),
    # ── import defects ─────────────────────────────────────────────────────────
    "--dangling": Mode(opts=("--target", "--verbose"),
                       why="`open import M` whose M has NO SOURCE FILE — the "
                           "dissolved-parent census; non-Substrate targets are UNJUDGED"),
    "--qualified": Mode(opts=("--summary",),
                        why="`import M as Q` on a Substrate module — BANNED, and the form "
                            "--dangling and --unused-imports are both blind to"),
    "--unused-imports": Mode(operand="[<Pfx>|<file.agda> …]", opts=("--summary",),
                             why="imports a module NAMES but does not REFERENCE. The count "
                                 "is a FLOOR: the predicate is keep-biased, so silence "
                                 "means no-evidence, never unused"),
    "--late-imports": Mode(operand="[<Pfx>…]",
                           why="an import BELOW a use of what it provides — agda binds "
                               "from the statement onward, so it supplies nothing above"),
    "--applied-args": Mode(operand="[<Pfx>]",
                           why="`open import M x` where NOTHING binds x — the telescope a "
                               "decomposition dropped"),
    # ⚑ THE THIRD MEMBER of the telescope-repair chain, and a CENSUS not a writer.
    # `--applied-args`/`--repair-telescopes` key on an APPLIED import argument;
    # this keys on the split's own `RESIDUE.md`, so it sees a dropped binder that is
    # a PROOF WITNESS consumed in a body — which applies no argument to any import
    # and is invisible to those modes by construction.
    "--stranded-residue": Mode(operand="[<Pfx>]",
                               why="a split's RESIDUE.md read back: re-homed / "
                                   "live-damage / unused. THREE-valued — collapsing "
                                   "`unused` into damage reports work that does not "
                                   "exist. Never re-homes or deletes: the writer's "
                                   "instruction is that the call is a DECISION"),
    "--double-route": Mode(paths=True, why="a name reachable by two import routes"),
    "--reexports": Mode(operand="[<Pfx>…]", opts=("--triage",),
                        why="surviving `public` re-exports — the ban's uncensused half; "
                            "--triage ranks by what paydown COSTS"),
    # ── telescopes and variables ───────────────────────────────────────────────
    "--telescope": Mode(operand="[<Pfx>]",
                        why="a `module Over` telescope read as the CONTRACT its consumers "
                            "apply: arity, and which NAME sits in each slot"),
    "--flat-variable": Mode(operand="[<Pfx>]", opts=("--repair", "--apply"),
                            writes=(".agda",),
                            why="a `variable` block flattened where it should be scoped; "
                                "--repair rewrites it"),
    "--dup-variables": Mode(operand="[<Pfx>]", why="a name declared `variable` twice"),
    # ── trust and flags ────────────────────────────────────────────────────────
    "--trust": Mode(operand="[<Pfx>]", why="postulates / pragmas / holes / not --safe"),
    "--flags": Mode(operand="[<Pfx>]",
                    why="local {-# OPTIONS #-} that fail to REFLECT the global flag set"),
    "--clause-audit": Mode(operand="[<Pfx>]", why="clause-level audit of definitions"),
    # ── history ────────────────────────────────────────────────────────────────
    "--at": Mode(operand="<rev> <Mod>…", opts=("--diff",),
                 why="the module AS IT WAS at a revision — a pure READ, unlike `git "
                     "checkout -- path` which destroys the working copy"),
    # ── the WRITERS (union of the guard sites and the apply-taking functions) ──
    "--stale-sections": Mode(operand="[<Pfx>]", opts=("--apply",), writes=(".agda",),
                             why="a SECTION (`a +_`) left on an operator a rename MOVED; "
                                 "--apply finishes it per-LINE, refusing ambiguous rows"),
    # ⚑⚑⚑ A CENSUS, NOT A WRITER — AND I DECLARED IT `writes=(".agda",)` FROM THE FUNCTION
    # SIGNATURE. `lp_apply` TAKES an `apply` parameter, so it appeared in the
    # `--binding apply` reading I built the write set from; the CLI never passes it. The
    # branch says so outright (`:4220-4225`): *"THE CENSUS ONLY … the WRITE is deliberately
    # not here yet"*, because each repair also renames use sites and a missed one compiles
    # against the WRONG instance in a two-index module.
    # ⚑ SO A DERIVED WRITE SET IS A HYPOTHESIS TOO. Two independent readings agreed and
    # both were about CAPABILITY, not about what the CLI DOES — and `--guarded guard`
    # already disagreed: `--lp-apply` is not among the five snapshot-arming sites. The
    # gate caught it on the first run; a false `writes` demands an --apply guard on a mode
    # that changes nothing, which is the direction that breaks working tools.
    "--lp-apply": Mode(operand="[<Pfx>]",
                       why="the level-polymorphic-application CENSUS. The transform is "
                           "ⓉLP-APPLY-WRITE and deliberately unbuilt: a repair renames use "
                           "sites, and one miss compiles against the wrong instance"),
    "--telescope-imports": Mode(operand="[<Pfx>]", opts=("--apply",), writes=(".agda",),
                                why="hoist the imports a telescope needs"),
    "--repair-telescopes": Mode(operand="[<Pfx>]", opts=("--apply",), writes=(".agda",),
                                why="restore a telescope a decomposition dropped"),
    "--qualified-repair": Mode(operand="[<Pfx>]", opts=("--apply",), writes=(".agda",),
                               why="retire an `import M as Q` by binding at the real home"),
    "--alias-probe": Mode(operand="[<Pfx>]", why="does this alias still resolve"),
    "--alias-trace": Mode(operand="<name>", why="where an alias binding comes from"),
    "--run": Mode(operand="<cmd>", why="run a build command and read its errors"),
    "--selftest": Mode(why="the guarded cases"),
}


def _selftest():
    """Counted from len(cases).

    ⚑ THE NAME→HOME AUTHORITY HAD NO TEST, and eleven tools resolve names through
    it.  A drop here is invisible at the call site and surfaces far away as a
    [NotInScope] in a file nobody edited — which is exactly how the `[]` defect
    below reached an emitted leaf.

    ⚑ AND IT HAD NO CLI EITHER (T14/§48): 19 tools could resolve a name and a HUMAN
    could not, so the question went through `python3 -c` or grep.  The last cases
    pin that the entry point EXISTS, because "the capability is there but
    unreachable" is precisely the `rewire_only` class this arc already paid for.
    """
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # ⚑ THE BRACKET-MIXFIX DROP.  `_namelist` rejects a group when any token is
    # not identifier-shaped — correct for a TYPE (`value b ≡ zero → Trimmed b`),
    # but `[]` and `[_]` fail that test BY CONSTRUCTION, and inside a `data` body
    # this is the ONLY branch that runs.  So `data List … where [] : List A`
    # indexed `List`, `_∷_`, `_++_`, `foldl`, `foldr` and NEVER `[]`.
    # MEASURED: `def_index()["[]"]` was EMPTY tree-wide; the R9 split emitted
    # `Algebra/Nat/Prime/Properties/Product.agda` (`product-[] : product [] ≡ 1`)
    # with no import of `Foundation.List`, and it failed [NotInScope] `[]`.
    # The docstring's claim that this "cannot drop a provision" was false.
    check("a single bracket-mixfix name is a NAME, not a type", _namelist("[]"), ["[]"])
    check("...and so is `[_]`", _namelist("[_]"), ["[_]"])

    # ⚑ …WHILE THE TYPE-REJECTION IT EXISTS FOR STILL HOLDS.  Without it, `≡` was
    # credited to three modules that merely USE it, making `fix_notinscope` refuse
    # the name as ambiguous.
    check("a multi-token TYPE is still rejected",
          _namelist("value b ≡ zero → Trimmed b"), [])
    check("a genuine multi-name signature still splits",
          _namelist("a b c"), ["a", "b", "c"])

    # ⚑ END-TO-END: the index must actually carry the constructor now.
    homes = def_index().get("[]", set())
    check("`[]` resolves to Foundation.List in the live index",
          "Substrate.Foundation.List" in homes, True)

    # ⚑ THE ENTRY-POINT GUARD.  `rewire_only` shipped as 1 def / 0 calls because
    # nothing asserted its dispatch existed; this is the same assertion for the
    # authority 19 tools depend on.  A capability with no way to invoke it is
    # invisible to every consumer that is not already importing the module.
    import inspect as _i
    _src = _i.getsource(_i.getmodule(_selftest))
    check("the CLI answers a NAME query (not just --selftest)",
          "--provides" in _src and "no definer in agda/Substrate" in _src, True)
    check("...and def_index/provides are both reachable from it",
          _src.count("provides(mod)") >= 1 and "def_index()" in _src, True)

    # ⚑ THE PATTERN QUERY (--grep).  Pins that the index can be asked what names
    # LOOK LIKE, not only where a known name lives — the gap that pushed
    # "does a projector/isotypic/character def exist?" out of the toolkit.
    _hits = dict(grep_names("^Chirality"))
    check("--grep finds ChiralityIsWHTSelector by prefix",
          "Substrate.Cocycles.V4Signature.Chirality.WHTCharacterBridge"
          in _hits.get("ChiralityIsWHTSelector", []), True)
    check("--grep is case-insensitive by default",
          dict(grep_names("^chiralityiswhtselector$")).get(
              "ChiralityIsWHTSelector") is not None, True)
    check("--grep honours case when asked",
          dict(grep_names("^chiralityiswhtselector$", ignore_case=False)), {})
    check("--grep returns [] for a pattern nothing matches",
          grep_names("zzz-no-such-name-zzz"), [])
    check("the CLI exposes --grep", "--grep" in _src, True)

    # ⚑ THE IMPORT-EDGE MODE.  Six hand-rolled `IMPORT` regexes existed and no
    # AUTHORITY, so the consumed-by direction — the question "what consumes this
    # cluster?" — had no reader at all.  These cases pin both directions and the
    # measurement, against edges verified by reading the sources.
    _ii = import_index()
    check("import_index reads a plain `open import` edge",
          "Substrate.Foundation.Nat.Nat"
          in _ii.get("Substrate.WitnessTower.Core", []), True)
    check("...and indexes every corpus module, not just importers",
          len(_ii) > 3000, True)
    check("a module with no Substrate imports still gets a key",
          isinstance(_ii.get("Substrate.WitnessTower.Core"), list), True)

    # ⚑ PREFIX, NOT EXACT NAME.  `Substrate.WitnessTower` is imported directly by
    # almost nothing; its 347 SUBMODULES are what consumers take.  Exact-name
    # matching reports a heavily-consumed cluster as unconsumed.
    _imp = importers_of("Substrate.WitnessTower")
    check("importers_of finds consumers of a SUBMODULE, not just the root",
          any(t != "Substrate.WitnessTower" for _s, t in _imp), True)
    check("importers_of returns (importer, imported) pairs",
          all(len(e) == 2 for e in _imp), True)
    _ext = {s for s, _t in _imp if not s.startswith("Substrate.WitnessTower")}
    check("the tower has consumers OUTSIDE its own subtree", len(_ext) > 0, True)

    # ⚑ CLOSURE terminates on stdlib/primitive rather than erroring.
    _cl = closure_of("Substrate.WitnessTower.Core")
    check("closure_of excludes the module itself",
          "Substrate.WitnessTower.Core" not in _cl, True)
    check("closure_of is TRANSITIVE (Eq.Cong pulls in Eq)",
          "Substrate.Foundation.Eq" in _cl, True)
    check("closure_of --prefix filters to a subtree",
          all(m.startswith("Substrate.Foundation")
              for m in closure_of("Substrate.WitnessTower.Core",
                                  "Substrate.Foundation")), True)

    _int, _in, _out = cluster_edges("Substrate.WitnessTower")
    check("cluster_edges: the tower has internal edges", _int > 0, True)
    check("cluster_edges: ...and outbound dependencies", _out > 0, True)
    check("cluster_edges: inbound is measured, not assumed", _in >= 0, True)

    # ⚑ THE HYPHEN IN A MODULE NAME.  `_IMPORT`'s class omitted `-`, so an edge to
    # `Substrate.Algebra.N-to-F2-Parity` was recorded as an edge to
    # `Substrate.Algebra.N` — a module that does not exist.  MEASURED before the
    # fix: `--importers Substrate.Algebra.N-to-F2-Parity` returned **0 edges in**
    # while `Algebra.Wedge.ParityBridge:37` imports it in plain text; after, 38.
    # A truncation is indistinguishable from an absence downstream, so this is
    # pinned at the REGEX rather than compensated in any caller.
    check("a hyphenated module name is not truncated at the hyphen",
          _IMPORT.match("open import Substrate.Algebra.N-to-F2-Parity").group(1),
          "Substrate.Algebra.N-to-F2-Parity")
    check("...and the edge is LIVE in the index (not merely parseable)",
          len(importers_of("Substrate.Algebra.N-to-F2-Parity")) > 1, True)
    check("...for a second, independently-named hyphenated module",
          _IMPORT.match("open import Substrate.Groups.V4-Coxeter-F2Graded").group(1),
          "Substrate.Groups.V4-Coxeter-F2Graded")

    # ⚑ THE RE-EXPORT CENSUS (--reexports).  `import_index` DISCARDS the
    # using/renaming tail by design, and `public` lives in that tail, so the one
    # construct that forwards a name across a module boundary was invisible to
    # every edge query — while being the reservoir `file-not-found` refills from
    # (a dissolved conduit leaves every consumer naming a module with no file).
    _rx = reexport_index()
    check("reexport_index finds a bare `public` re-export",
          any(m == "Substrate.Groups.Z2-Coxeter" and t == "Substrate.Groups.Coxeter.Word"
              for m, _l, t, _tl, _k in _rx), True)
    check("...and one spelled `public using (...)`",
          any(m == "Substrate.Algebra.Q.Arithmetic" and t == "Substrate.Algebra.Q.Add"
              for m, _l, t, _tl, _k in _rx), True)
    # ⚑ WAS ANCHORED ON `Substrate.Algebra.F2.AES.AES`, WHICH NO LONGER EXISTS —
    # Ⓑ2c-FREE13 deleted it (0 defs, 0 importers, 10 re-exports: a pure barrel).
    # A selftest that pins a LIVE TREE FACT dies when the tree is paid down, and
    # the paydown is the goal — so anchor the SPELLING on a surviving instance and
    # let the assertion be about the tail-order parse, not about one module.
    check("...and one spelled `using (...) public` (the tail order differs)",
          any(re.search(r"using\s*\([^)]*\)\s*public", _tl)
              for _m, _l, _t, _tl, _k in _rx), True)
    # ⚑ `public` IS A KEYWORD, NOT A SUBSTRING — a module whose NAME contains the
    # letters, or a `using` list naming a `public-`prefixed identifier, must not
    # match.  A substring test would inflate the census and so misreport paydown.
    check("a name merely CONTAINING 'public' is not a re-export",
          [r for r in _rx if "publication" in r[3].lower()], [])
    check("every reported row carries (module, line, target, tail, kind)",
          all(len(r) == 5 and isinstance(r[1], int) for r in _rx), True)

    # ⚑ THE CLAUSE AUDIT (--clause-audit).  A `using` naming a NON-EXPORT is only
    # a WARNING in agda: the name binds nothing and the build fails at the far-away
    # USE site.  Four such breakages were repaired by hand in one session, each
    # found by a compile rather than a census, and all four were the exhaust of a
    # ban sweep that removed a banned construct without rewiring its consumers.
    _ca = clause_audit()
    check("clause_audit returns (module, line, target, name, verdict)",
          all(len(r) == 5 and isinstance(r[1], int) for r in _ca), True)
    check("...and every verdict is one of the three kinds",
          {r[4] for r in _ca} - {"NONEXPORT", "UNUSED", "UNKNOWN"}, set())
    # ⚑ UNKNOWN IS NEVER REPORTED AS NONEXPORT.  `--provides` once answered a
    # confident `0 name(s)` for a target it could not resolve, and a peer read four
    # such zeroes as "these modules are empty", RETRACTING a correct census on the
    # strength of it.  A target outside the index is a fact about the METHOD.
    _known = def_index_modules()
    check("no NONEXPORT verdict on a target the index does not know",
          [r for r in _ca if r[4] == "NONEXPORT" and r[2] not in _known], [])
    check("a target outside the index yields UNKNOWN, never a missing-export claim",
          all(r[4] == "UNKNOWN" for r in _ca if r[2] not in _known), True)
    # a live anchor: Foundation.Eq is bare-imported tree-wide and genuinely
    # provides `refl`, so no clause naming it may be called a non-export.
    check("a genuinely-exported name is never NONEXPORT",
          [r for r in _ca if r[4] == "NONEXPORT"
           and r[2] == "Substrate.Foundation.Eq" and r[3] == "refl"], [])
    # ⚑⚑ THE FIRST CUT CENSUSED ITS OWN BLIND SPOT.  `Foundation.Level` indexes as
    # ONE name (`0ℓ`) because `Level`/`suc`/`_⊔_` arrive through its `open import
    # Agda.Primitive … public`, and `def_index` scans `agda/Substrate` only — so
    # ~200 consumers naming those three were reported NONEXPORT ("latent build
    # failure") while compiling perfectly.  A re-exporter's provision set is OPEN.
    check("a name forwarded by a re-exporter is not called a missing export",
          [r for r in _ca if r[4] == "NONEXPORT"
           and r[2] == "Substrate.Foundation.Level"], [])
    check("...and that generalises: no NONEXPORT against any re-exporting target",
          [r for r in _ca if r[4] == "NONEXPORT"
           and r[2] in {x[0] for x in reexport_index()}], [])
    # ⚑ `using (module M; f)` IS VALID AGDA — `module` is a keyword, not a name.
    check("the `module` keyword in a clause is not censused as a name",
          [r for r in _ca if r[3] == "module"], [])
    # ⚑⚑ THE SECOND FALSE POSITIVE, AND THE ONE CAUGHT BY GROUND TRUTH.  The
    # census called `Algebra.Nat.GCD.GcdDividesLeft` a latent build failure; the
    # module COMPILES CLEAN.  Its target `GCD.TraceDivides` indexes as ZERO names
    # because `trace-divides-left`/`-right` live inside a `mutual` block and
    # `def_index` is column-0.  A verdict class defined as "latent build failure"
    # must be checked against an actual compile, which is what found this.
    check("a target with a mutual/private/abstract block yields no NONEXPORT",
          [r for r in _ca if r[4] == "NONEXPORT"
           and r[2] == "Substrate.Algebra.Nat.GCD.TraceDivides"], [])
    # ⚑⚑ UNUSED's FALSE POSITIVES ARE THE DANGEROUS DIRECTION — acting on one
    # DELETES A LIVE IMPORT.  The tokenizer splits on the very characters some
    # names are built from, so an infix pair constructor (`combine (a₁ , a₂)`)
    # yields a bare `,` and never matches `_,_`.  MEASURED on `Quotient/CRT:36`,
    # used at :83/:85 and reported UNUSED until the punctuation-run and
    # bracket-mixfix recoveries (both already in `prune_imports`) were added.
    check("an infix pair constructor is not reported unused",
          [r for r in _ca if r[4] == "UNUSED"
           and r[0] == "Substrate.Algebra.Quotient.CRT" and r[3] == "_,_"], [])
    # ...and the verdict still FIRES where the entry is genuinely dead: this one
    # was removed and the module verified clean afterwards.
    # ⚑⚑ THIS CASE WAS PINNED ON A LIVE TREE FACT AND DIED WITHIN THE HOUR — the
    # hazard I had just flagged to a peer, committed in my own newest test.  It
    # asserted an UNUSED row with target `Foundation.Product` and name
    # `proj₁`/`proj₂`/`_×_`; the consumer that had that dead entry was cleaned up
    # (most likely by this same session's barrel work) and the assertion failed
    # while the verdict class was working perfectly — hundreds of rows tree-wide.
    #
    # ⚑ AND IT IS THE ANTI-SILENCING CASE: it exists to prove UNUSED still FIRES
    # after the tokenizer recoveries were added to stop it firing falsely.  A case
    # whose job is "the detector is not silenced" must not itself be silenceable
    # by paydown.  So it drives the scan on a CONSTRUCTED module: `unused-here` is
    # named in the clause and appears nowhere in the body, which is true by
    # construction and stays true however the tree changes.
    _fx = ("module Fixture where\n"
           "open import Substrate.Foundation.Eq using (refl; unused-here)\n"
           "\n"
           "thing : Set → Set\n"
           "thing x = refl x\n")
    _fxrows = _clause_scan(
        _fx, "Fixture", {"Substrate.Foundation.Eq"},
        {"Substrate.Foundation.Eq": {"refl", "unused-here"}}.get, set())
    check("a genuinely dead clause entry IS reported (constructed, cannot rot)",
          [(r[3], r[4]) for r in _fxrows], [("unused-here", "UNUSED")])
    # ...and the live-name half of the same clause is NOT reported, which is what
    # separates "the detector fires" from "the detector fires at everything".
    check("...while a USED entry in the same clause is not",
          [r for r in _fxrows if r[3] == "refl"], [])
    # ⚑ THE `;` SEPARATOR IS NOT PART OF A NAME.  `renaming (proj₁ to π₁; proj₂
    # to π₂)` parsed the destination as `π₁;` under a `\S+` capture — a corrupt
    # row AND a failed token lookup, so a LIVE rename reported as unused.
    check("no reported name carries a clause separator",
          [r for r in _ca if ";" in r[3] or "(" in r[3] or ")" in r[3]], [])

    # ⚑⚑ THE TELESCOPE REPAIR (--repair-telescopes).  `applied_imports` could only
    # REPORT the dropped-telescope defect; its own footer said "recover the
    # parent's telescope with `--at <rev>`", i.e. a HAND edit, 17 times.
    #
    # ⚑ AND THE FIRST CUT HAND-ROLLED `git show` INSTEAD OF DELEGATING TO
    # `at_revision`, with a different repo-root derivation — it returned EMPTY for
    # every parent, so the mode printed `0 module(s)` and then, once refusals were
    # named, 33× "no pre-split parent declares this parameter" while every parent
    # declares it and `--at` reads them all.  A second spelling of a solved
    # problem, whose refusal message blamed the substrate for the method's defect.
    # ⚑⚑ THIS PAIR WAS PINNED ON THE LIVE TREE AND DIED THE MOMENT THE REPAIR RAN
    # — the third time today, in a case I wrote after flagging the hazard twice.
    # It asserted `len(plans) > 0` over `Coxeter.Cyclic`; once the 17 modules were
    # repaired, `--applied-args` went empty, no rows reached the planner, and a
    # WORKING tool reported `0 module(s)` as a FAILURE.  A test whose subject is
    # paydown cannot assert that the debt is still there.
    #
    # So: drive the parent lookup on a module that still exists at the revision,
    # which is a fact about GIT HISTORY (immutable) rather than about the current
    # tree (the thing being changed).
    _ptxt, _ = at_revision("Substrate.Groups.Coxeter.Cyclic.Inverse", "771283c8^")
    check("the pre-split parent is readable (delegating to at_revision)",
          bool(_ptxt), True)
    check("...and declares the telescope the shards lost",
          bool(re.search(r"^module\s+\S+\s*\(n : ℕ\)\s*where", _ptxt or "", re.M)),
          True)
    # the whole-tree run must not CRASH and must return the two-part shape, which
    # is what a caller destructures; emptiness is a legitimate answer here.
    _plans, _ref = repair_telescopes("Substrate.Groups.Coxeter.Cyclic")
    check("the repair returns (plans, refusals) and plans carry their imports",
          all(len(p) == 3 for p in _plans), True)
    check("...and refuses nothing for a parameter every parent declares",
          [r for r in _ref if "no pre-split parent" in r[2]], [])
    # ⚑⚑ THE TELESCOPE'S TYPES ARE PART OF THE SAME REPAIR.  Restoring `(n : ℕ)`
    # makes `ℕ` load-bearing at the header, and an import below the header binds
    # nothing there.  MEASURED: after the first apply run the unbound-argument
    # census went 33 → 0 while every repaired module failed anew on
    # `NotInScope: ℕ` — "33 → 0" reading as done while nothing compiled.
    check("a restored `(n : ℕ)` telescope plans its own ℕ import",
          all("Substrate.Foundation.Nat.Nat" in _i or _i == []
              for _p, _d, _i in _plans), True)
    # ⚑ THE RESOLUTION ITSELF, on a fact that cannot be paid down: `ℕ` has exactly
    # one home, so a telescope naming it plans exactly that import.  This is the
    # assertion the live-tree pair was trying to make, stated about the INDEX.
    check("`ℕ` resolves to a single home, which is what makes the plan decidable",
          def_index().get("ℕ", []), ["Substrate.Foundation.Nat.Nat"])

    # ⚑⚑ ⓉTELESCOPE-IMPORTS — the successor `repair_telescopes` CREATES and cannot
    # detect.  Its planner reads `applied_imports` ("an applied argument nothing
    # binds"), and restoring the telescope is exactly what removes those rows, so
    # the module it just repaired is invisible to the census that found it.
    # MEASURED: 33 sites → 0 (clean) → compile → `NotInScope: ℕ` → 15 of 17 red.
    # ⚑ REBASED OFF THE LIVE TREE (the fourth such case today).  This asserted
    # `len(rows) > 0` over `Coxeter.Cyclic`; once `--telescope-imports --apply`
    # ran, the subtree had no rows and a WORKING census reported as a FAILURE.
    # The durable claim is about the FUNCTION's contract, not the debt's size.
    _ti = telescope_imports("Substrate.Groups.Coxeter.Cyclic")
    check("the successor census returns rows in its declared shape",
          all(len(r) == 3 and isinstance(r[1], list) for r in _ti), True)
    check("...and every row names a module, its missing imports, its ambiguities",
          all(len(r) == 3 and isinstance(r[1], list) for r in _ti), True)
    # a module with no telescope is not this question — the two censuses must not
    # blur, or the mode's verdict spans two predicates.
    check("a module with NO telescope is never reported here",
          [r for r in _ti
           if not re.search(r"^module\s+\S+\s*\(", agda_lex.mask_comments(
               open(r[0], encoding="utf-8", errors="replace").read()), re.M)], [])

    # ⚑⚑ ⓉLP-APPLY — the `normalize`-through-a-conduit census.  `Existential`
    # opens `ListPresentation` without naming it, so four names appear to come
    # from Existential; `--provides` shows the partition (Existential six names,
    # none of them these).  Agda only WARNS, so all ~28 were found by compiles.
    _lp = lp_apply()
    check("lp_apply returns (path, index, existential-qual, base-qual, names)",
          all(len(r) == 5 for r in _lp), True)
    check("...and every reported name really is ListPresentation's",
          {n for r in _lp for n in r[4]} - set(provides(
              "Substrate.Groups.Coxeter.ListPresentation")), set())
    # ⚑ THE CENSUS MUST SEE ITS OWN COMPLETION.  The first cut reported 14
    # unqualified rows and EIGHT were files already repaired — its predicate (a
    # bare Existential open plus a bare `normalize`) is exactly the CORRECT
    # post-repair state, so paydown read as debt.
    check("a file that already applies ListPresentation is not reported",
          [r for r in _lp
           if re.search(r"^\s*(?:open\s+)?import\s+Substrate\.Groups\.Coxeter\."
                        r"ListPresentation\b", agda_lex.mask_comments(
                            open(r[0], encoding="utf-8", errors="replace").read()),
                        re.M)], [])
    # ⚑ AND THE BASE QUALIFIER IS READ, NEVER DERIVED.  The first cut emitted
    # `Z₂-Existential-Base.Gen` by appending "-Base" to the Existential qualifier
    # — a name appearing nowhere in any file.  Where no Base binding exists at
    # that index the row says so, which is the fact the repair needs.
    check("no reported base-qualifier is a string-append of the existential one",
          [r for r in _lp if r[3] and r[2] and r[3] == r[2] + "-Base"], [])
    # ⚑ and it must REFUSE an ambiguous type rather than pick a home — the same
    # rule `hoist_telescope_imports` states ("`n` has SEVERAL homes — refusing to
    # guess"). A wrong import compiles until it silently shadows something.
    check("an ambiguous telescope type is refused, never guessed",
          [r for r in _ref if "several homes" in r[2] and "—" not in r[2]], [])
    check("the CLI exposes --reexports", "--reexports" in _src, True)

    # ⚑⚑ `--telescope` — SIX MEASURED WITNESSES, EACH A REVISION THIS MODE NEEDED.
    # A `module Over (…) where` is an arity-and-order CONTRACT: consumers fill it
    # POSITIONALLY, so editing a provider's telescope breaks callers that were correct
    # before and the error surfaces in the CONSUMER, far away.  MEASURED 2026-08-17: a
    # tree-wide `rename_at_source` rewrote CARRIER parameters (`+-assoc` → `+ℕ-assoc`)
    # in 11 of 14 `Graded.Laws` shards; arity stayed 14, every argument stayed `A`-typed,
    # and the whole family still typechecked at the application sites.  The failure was
    # ONE mismatch propagating along the open-chain, which is why hand-repair saw it
    # move `:84 → :83 → :58` and read as three separate bugs.
    _tc = telescope_contract("Substrate.Algebra.Polynomial.Graded")
    _by = {m: (p, c) for m, p, c in _tc}

    # (1) THE CLEAN CASE — a provider whose consumers all match, so a green run is
    # green for a reason and not because the census read nothing.
    _base = _by.get("Substrate.Algebra.Polynomial.Graded.Base")
    check("a 1-param provider is read, with its consumers",
          bool(_base) and len(_base[0]) == 1 and len(_base[1]) >= 5, True)
    check("...and every one of them applies exactly 1 argument",
          bool(_base) and {n for _c, _l, n, _a in _base[1]} == {1}, True)

    # (2) ARITY IS BINDER GROUPS, NOT TOKENS.  `module_scopes` flattens `(a b c : A)`
    # to three names because ITS consumers ask "is `tok` bound here?".  Reading that as
    # an arity counted a LAW's own bound variables and reported
    # `Graded.Laws.Assoc.Over` as declaring 32 parameters where it declares 14 — which
    # turned 87 CORRECT consumers into phantom mismatches on a mode that exits 1.
    _assoc = _by.get("Substrate.Algebra.Polynomial.Graded.Laws.Assoc")
    check("a law's inner binders are NOT telescope parameters",
          bool(_assoc) and len(_assoc[0]) == 14, True)
    check("...and its consumers therefore MATCH (no phantom mismatch)",
          bool(_assoc) and all(n == 14 for _c, _l, n, _a in _assoc[1]), True)
    # `{A : Set}` is solved by unification, never applied — it must not be counted.
    check("an implicit binder is excluded from the applied arity",
          bool(_assoc) and "A" not in _assoc[0], True)

    # (3) A COMMENT INSIDE THE TELESCOPE HID THE PROVIDER ENTIRELY.  `module_scopes`
    # masks comments to blanks, so a note between `module Over {A : Set}` and its first
    # `(…)` group breaks the header span and the module vanishes from its own census —
    # a SILENT absence that reads as "nothing to check".  Measured on `Laws/Conv.agda`
    # one edit after annotating it.
    check("a provider with a multi-line telescope is still found",
          "Substrate.Algebra.Polynomial.Graded.Laws.Conv" in _by, True)

    # (4) GROUP BY CONTRACT, NOT BY ARITY.  Arity is a PROXY: the arity-1 bucket paired
    # `Base.Over (𝟘)` with `FromCommRing.Over (CR)` and `PolyDivWedge.Over (CR)` —
    # three unrelated contracts — and reported `Base` as deviating from a "majority" it
    # shares nothing with.  Two providers are under one contract when some consumer
    # applies them with the SAME argument list; that edge lives in the CALL SITES.
    _sites = {}
    for _m, _p, _c in _tc:
        for _cf, _ln, _n, _a in _c:
            _sites.setdefault((_cf, " ".join(_a)), set()).add(_m)
    _co = {frozenset(v) for v in _sites.values() if len(v) > 1}
    check("co-application with identical args is what links providers",
          any({"Substrate.Algebra.Polynomial.Graded.Defs",
               "Substrate.Algebra.Polynomial.Graded.Laws.Nth"} <= s for s in _co),
          True)
    check("...and `Base`/`FromCommRing` share no such call site",
          any({"Substrate.Algebra.Polynomial.Graded.Base",
               "Substrate.Algebra.Polynomial.Graded.FromCommRing"} <= s
              for s in _co), False)

    # (5) THE MODE IS A GATE, and it reports both defect kinds.
    check("the CLI exposes --telescope", "--telescope" in _src, True)
    check("...and exits nonzero on a mismatch or a divergence",
          "ARITY MISMATCH" in _src and "DIVERGENT" in _src, True)
    # ⚑ THE MAJORITY IS NOT THE CONTRACT, and the output must say so: a sweep that hit
    # most siblings makes the DAMAGE the majority (measured — 10 of 14 carried the
    # renamed spelling).  A reader who normalises to the vote propagates the defect.
    check("the divergence report refuses to name the majority as the target",
          "NOT AUTOMATICALLY THE CONTRACT" in _src, True)

    # ⚑⚑ `--at` — READING HISTORY IS A READ, AND `git checkout -- path` IS A WRITE.
    # Reaching for a checkout to LOOK at an earlier version destroys the working copy;
    # used repeatedly this session, including on files carrying edits worth keeping.
    # The primitive existed inline at `prune_imports.py:411` (`git show <ref>`) with one
    # call site and no mode, so "what did this look like before?" had no reader.
    _txt, _rel = at_revision("Substrate.Algebra.Polynomial.Graded.Defs", "771283c8")
    check("a module reads back at an explicit revision",
          bool(_txt) and "module Substrate.Algebra.Polynomial.Graded.Defs" in _txt,
          True)
    check("...and the historical text is NOT the working tree's",
          _txt != open(_rel, encoding="utf-8", errors="replace").read(), True)
    # ⚑ ABSENT ≠ EMPTY: a module that did not exist at `rev` is a fact about history,
    # and a restore that treated it as "" would invert exactly the question asked.
    _gone, _ = at_revision("Substrate.No.Such.Module.Here", "771283c8")
    check("a module absent at that revision reports ABSENT, not empty", _gone, None)
    check("the CLI exposes --at with a diff mode",
          "--at" in _src and "--diff" in _src, True)

    # ⚑⚑⚑ THE ⟡vfs PROMOTION'S LOAD-BEARING PAIR, AND THE ARMS ARE STARVED AGAINST
    # EACH OTHER.  Under the old `subprocess` reader, `returncode != 0` collapsed a
    # BAD REVISION into the same `None` as a genuinely-absent module — so a typo'd sha
    # reported as a fact about history and every caller believed it.  A check whose
    # all-clear has never been shown to differ from its found-something is not a
    # measurement, so the ABSENT arm above and the BROKEN arm here are asserted to
    # DIFFER, not merely to each hold.
    _badrev_raised = None
    try:
        at_revision("Substrate.Algebra.Polynomial.Graded.Defs", "nosuchrev-zzz-9999")
        _badrev_raised = "no raise"
    except ValueError as _e:
        _badrev_raised = "bad revision" in str(_e)
    except Exception as _e:                      # noqa: BLE001 — the type IS the assertion
        _badrev_raised = type(_e).__name__
    check("⚑⚑ a BAD REVISION raises — it does NOT report as ABSENT", _badrev_raised, True)
    check("⚑ ...and that is a DIFFERENT outcome from a missing module",
          _gone is None and _badrev_raised is True, True)

    # ⚑⚑ THE DECODE IS STRICT UTF-8 AND CHOSEN BY US, NOT BY THE LOCALE.  The old
    # reader passed `text=True` to `subprocess`, so this corpus of `ℕ`/`𝟙`/`∷` was
    # decoded with whatever codec the environment happened to supply — and the
    # telescope case below was PASSING THROUGH that decode, which is why it could not
    # have caught a locale regression.  Pinned explicitly now.
    _uni, _ = at_revision("Substrate.Groups.Coxeter.Cyclic.Inverse", "771283c8^")
    check("history decodes as UTF-8 text, not locale bytes", isinstance(_uni, str), True)
    check("...and non-ASCII Agda survives the read intact",
          bool(_uni) and "ℕ" in _uni, True)

    # ⚑⚑ `--late-imports` — FOUR FALSE-POSITIVE MECHANISMS, EACH WITH A LIVE WITNESS.
    # The mode makes a POSITIONAL claim (an import below a use of what it provides
    # supplies nothing to that use) and every mechanism below is a way that claim can
    # be true of the TEXT and false of the BUILD.  MEASURED 2026-08-17: the first cut
    # reported 212 rows; compiling fifteen of them found 5 clean, 8 blocked upstream
    # and 2 failing on their own content, so the header claim was false for at least
    # 13 of 18.  Four narrowings took it to 4.
    #
    # ⚑ EVERY ONE WAS FOUND BY COMPILING A REPORTED FILE AND ASKING WHY IT BUILT —
    # never by re-reading the matcher.  That is why these cases pin LIVE corpus files
    # rather than fixtures: a fixture would encode my model of the defect, and my
    # model was wrong four times.  A witness that stops reproducing is itself a
    # finding (the file was repaired), so a failure here is read before it is fixed.
    _li = late_imports()
    check("late_imports returns (module, line, target, name, use_line)",
          all(len(r) == 5 and isinstance(r[1], int) and isinstance(r[4], int)
              for r in _li), True)
    check("...and every row's use is genuinely ABOVE its import",
          all(r[4] < r[1] for r in _li), True)

    # ── applied-args: a dropped telescope, with its own false-positive ledger ──
    # ⚑ THE CLASS IS REAL AND WAS FOUND ONLY THROUGH A SWEEP REFUSAL.  A split shard
    # inherits `open import ...Base n` but not the parent's `module P (n : ℕ) where`.
    # Measured 2026-08-17 on `Foundation/Fin/Iterate` and all eight
    # `Coxeter/Cyclic/Bridge/*` shards — the census ranked those roots at cone size
    # 7/3/1/1 (reading "broad and shallow") while one gated a 27-module class.
    _aa = applied_imports()
    check("applied_imports returns (module, line, target, arg, bound)",
          all(len(r) == 5 and isinstance(r[1], int) for r in _aa), True)

    # ⚑ THE REPAIRED COHORT MUST BE SILENT.  These eight carried the defect and were
    # fixed by restoring the telescope; a mode that still reports them is matching
    # the SHAPE rather than the PROPERTY.  This is the case that would fail before
    # the fix and must keep passing after it.
    check("a shard whose telescope was restored reports nothing",
          [r for r in _aa
           if r[0].startswith("Substrate.Groups.Coxeter.Cyclic.Bridge.")], [])

    # (A) `public` IS A MODIFIER, NOT AN ARGUMENT — and suppressing it here is NOT
    # the ban's enforcement.  `open import M public` re-exports; the first cut read
    # `public` as an applied name.  ⚑ THE BAN ON RE-EXPORTS IS `--reexports`' JOB
    # (48 sites, 30 modules); this mode must neither report them as applied-args
    # (a wrong diagnosis) nor be mistaken for the gate that catches them.
    check("`open import M public` is not an applied argument",
          [r for r in _aa if r[3] == "public"], [])

    # (B) A NUMERIC LITERAL IS THE CORRECT FORM, NOT THE DEFECT.  `Cyclic.Base 1`
    # instantiates the telescope — exactly what a repaired shard does.  The first
    # tree-wide run reported 25 such rows (Z2 at 1, Z3 at 2, Z4/Z5/Z7), a third of
    # the census being the correct form of the thing it hunts.
    check("an integer literal argument is a correct application",
          [r for r in _aa if r[3].isdigit()], [])

    # (C) AN ARGUMENT SUPPLIED BY ANOTHER IMPORT IS BOUND.  `RewriteConfluence _⇒_`
    # in `NewmanKI/Properties` applies a name a different import provides, and that
    # module COMPILES.  ⚑ THE VERDICT JOIN IS WHAT EXPOSED IT — the row came back
    # `clean`, which is the mode reporting on a file the build is happy with.
    check("an argument another import provides is not unbound",
          [r for r in _aa
           if r[0] == "Substrate.Algebra.R.Trace.NewmanKI.Properties"], [])

    # ── reexports: TWO forms re-export, and the census saw one ───────────────────────────
    # ⚑ `open import M … public` is an IMPORT; `open M args … public` is a module
    # APPLICATION with no `import` keyword, and `_IMPORT` cannot match it.  MEASURED
    # 2026-08-18 on `X8aSkiExistence:62` — a live re-export the census silently omitted,
    # found by hand.  The docstring's own claim is that re-exports are the RESERVOIR the
    # `file-not-found` class refills from, so an unseen form is a supply paydown never reaches.
    _rx = reexport_index()
    check("reexport_index returns (module, line, target, tail, kind)",
          all(len(r) == 5 and isinstance(r[1], int) for r in _rx), True)
    # ⚑ THE KIND WAS COMPUTED AND DISCARDED.  Both forms matched and both
    # returned the same shape, so triage could not separate a forwarding import
    # (retire it, bind at home) from a module application (rewrite every use
    # site).  Two different jobs at two different costs, ranked as one queue.
    check("...and the KIND separates the two forms",
          {r[4] for r in _rx}, {"import", "apply"})
    check("`open import M … public` is kind=import",
          [r[4] for r in _rx if r[0] == "Substrate.Groups.Z2-Coxeter"], ["import"])
    check("`open <applied module> args … public` is kind=apply",
          [r[4] for r in _rx if r[0].endswith("X8aSkiExistence")], ["apply"])
    # ⚑ AND THE DISCARDED KIND CORRUPTED THE MODE'S OWN DANGLING CHECK: an
    # application's target is a LOCAL module name, never a dotted path, so
    # testing it against `import_index` reported healthy rows as the
    # `file-not-found` reservoir.  Only the import form has a module-path target.
    check("no application-form target is a dotted module path",
          [r for r in _rx if r[4] == "apply" and "." in r[2].split(".Over")[0]
           and r[2].startswith("Substrate.")], [])
    check("the module-APPLICATION form is censused, not just `open import`",
          [r for r in _rx if r[0].endswith("X8aSkiExistence")
           and "FixpointMachine" in r[2]] != [], True)
    # ⚑⚑ AND THE WIDENING OVER-FIRED FIRST TIME.  `open CoTrace public`, where
    # `record CoTrace` is declared THREE LINES ABOVE, forwards nothing across a
    # boundary — it exposes a record's own fields, ordinary Agda idiom.  The first cut
    # took S5 from 8 to 12 and all four additions were that shape (`Susp`, `DivStr`,
    # `Wedge`, `CoTrace`); the mode's own dangling-target check flagged every one as
    # "names no module in the tree", which is the tool reporting its own bad rows.
    check("an `open <local record> public` is NOT a re-export",
          [r for r in _rx if r[2] in ("CoTrace", "Susp", "DivStr", "Wedge")], [])
    # ⚑⚑ A TRAILING COMMENT'S `public` IS NOT A RE-EXPORT.  The whole-line guard
    # (`lstrip().startswith("--")`) catches a comment LINE and misses a comment TAIL —
    # and `public` appears in prose ABOUT re-exports more often than in one.  MEASURED:
    # three rows matched their own annotations saying *"NON-public: not ours to
    # re-export"*, i.e. the census reported a file as a re-exporter on the strength of
    # that file denying it.  These three sites are the live witnesses; a failure here
    # means the file was repaired (read it before fixing the case).
    check("a trailing `-- NON-public` comment does not read as a re-export",
          [r for r in _rx if r[0] == "Substrate.Algebra.Polynomial.Graded.Mod"
           and r[1] == 60], [])
    check("...nor in Mod.Core", [r for r in _rx
                                 if r[0].endswith("Graded.Mod.Core")], [])
    check("...nor in Mod.Expand", [r for r in _rx
                                   if r[0].endswith("Graded.Mod.Expand")], [])
    # ⚑ AND THE GENUINE SIBLINGS IN THE SAME FILE STILL COUNT — a comment-stripper
    # that silenced real rows would be worse than the false ones it removed.
    check("the real `public` applications in Mod are still censused",
          sorted(r[1] for r in _rx
                 if r[0] == "Substrate.Algebra.Polynomial.Graded.Mod"), [61, 62])

    check("_local_defs reads this file's own data/record/module heads",
          "CoTrace" in _local_defs(os.path.join(AG, "Substrate/S5/S5Real.agda")), True)
    check("...and does not claim a name it never declared",
          "Foundation" in _local_defs(os.path.join(AG, "Substrate/S5/S5Real.agda")), False)

    # ── stale-sections: the half a rename misses (ⓉF2-SECTIONS) ─────────────────────────
    # ⚑ A RENAME CONVERTS EVERY APPLIED OCCURRENCE AND LEAVES SECTIONS.  `--at 771283c8~1`
    # on `F2/Vector/Universal.agda` shows the ban commit's F₂ conversion doing exactly
    # that: `cong₂ _+F_` and `g zero +F …` converted, `(lookup … j +_)` and
    # `(_+ sum-F₂ …)` not.  Found by hand in FOUR consecutive files before this mode
    # existed — one compile at a time, which is the shape the standing rule forbids.
    _ss = stale_sections("Substrate.Algebra.F2")
    check("stale_sections returns (module, line, spelling, text)",
          all(len(r) == 4 and isinstance(r[1], int) for r in _ss), True)
    # ⚑⚑ THE SELF-FALSIFYING JOIN, AND IT IS THE WHOLE VERDICT.  A row on a module the
    # build calls `clean` is a FALSE POSITIVE — the section resolves there, so the scan
    # is matching a spelling that means something.  `--late-imports` asserted a header
    # false for 13 of 18 rows before it was rebuilt around this check; measured here,
    # 49 rows and ZERO on a compiling module.
    try:
        import split_census as _sc0
        _v0 = {(_r[:-5].replace("/", ".") if _r.endswith(".agda") else _r): _v
               for _r, _v, _c in _sc0.census_from_build(AG)}
        check("no stale-section row sits on a module that COMPILES",
              [r for r in _ss if _v0.get(r[0]) == "clean"], [])
    except Exception:
        pass
    # ⚑ THE SECTION SHAPES ARE THE POINT: a right section (`a +_`), a left section
    # (`_+ b`), and neither may match the ALREADY-RENAMED operator.  `+F_` must not
    # read as `+_`, or the mode reports the rows it just fixed.
    check("an ALREADY-renamed section is not reported",
          [r for r in _ss if "+F_" in r[3] and "+_" not in r[3].replace("+F_", "")],
          [])
    # ⚑ AND THE AMBIGUITY REFUSAL.  A file importing another provider of the OLD
    # spelling may legitimately mean it; only the typechecker can say.  The class is
    # empty on today's tree (one definer survives, `Groups.F2Cubed`), so the branch is
    # asserted on a CONSTRUCTED row rather than trusted — the inert-guard rule.
    check("the AMBIGUOUS verdict is a distinct spelling, not folded into `stale`",
          {"stale", "AMBIGUOUS"} >= {r[2] for r in _ss} or not _ss, True)

    # ── repair_sections: the transform, driven by a CONSTRUCTED fixture ──────────────────
    # ⚑⚑ IDEMPOTENCE IS THE PROPERTY, and asserting it against today's rows would be
    # the inert-guard shape — such a case passes because no already-renamed row exists,
    # not because the predicate was exercised.  These drive it against a file written
    # for the purpose, on both the dry and the writing path.
    import tempfile as _tf2
    _td = _tf2.mkdtemp()
    _fx = os.path.join(_td, "Fx.agda")
    open(_fx, "w", encoding="utf-8").write(
        "a = cong (x +_) p\n"          # right section, STALE
        "b = cong (_+ y) q\n"          # left section, STALE
        "c = cong (x +F_) r\n"         # right section, ALREADY renamed
        "d = cong (_+F y) s\n"         # left section, ALREADY renamed
        "e = x +F y\n")                # applied, already renamed
    _rows = [("Fx", 1, "stale", ""), ("Fx", 2, "stale", ""),
             ("Fx", 3, "stale", ""), ("Fx", 4, "stale", ""),
             ("Fx", 5, "stale", "")]

    # ⚑⚑ THE FIXTURE DRIVES `repair_sections` ITSELF, NOT A COPY OF ITS REGEXES.
    # My first cut inlined the two patterns here — so an edit to the REAL transform
    # would leave these cases green, and the guard against a destructive rewrite
    # would be testing the guard's own transcription (peer session, 2026-08-18:
    # *"a case pinned to a spelling tests the edit, not the property"*).  It reads
    # and writes a real file under a temp AG root, which is what `repair_sections`
    # takes, so the case exercises the write path too.
    _prev_ag = globals()["AG"]

    def _run_fixture():
        globals()["AG"] = _td
        try:
            repair_sections([("Fx", i + 1, "stale", "") for i in range(5)],
                            apply=True)
        finally:
            globals()["AG"] = _prev_ag
        return open(_fx, encoding="utf-8").read().split("\n")

    _after = _run_fixture()
    check("a STALE right section is renamed", _after[0], "a = cong (x +F_) p")
    check("a STALE left section is renamed", _after[1], "b = cong (_+F y) q")
    # ⚑ THE IDEMPOTENCE CASES.  Without the negative lookahead on the operator
    # character, `+F_` matches as `+_` and becomes `+FF_` — the tool rewriting what
    # it just fixed, so a second run corrupts a correct file.
    check("an ALREADY-renamed right section is UNTOUCHED",
          _after[2], "c = cong (x +F_) r")
    check("an ALREADY-renamed left section is UNTOUCHED",
          _after[3], "d = cong (_+F y) s")
    check("an APPLIED occurrence is untouched (only sections move)",
          _after[4], "e = x +F y")
    # ⚑ AND THE WHOLE TRANSFORM IS IDEMPOTENT: running it on its own output is a
    # no-op.  This is the property a one-pass tool needs to be safe to re-run after
    # a partial failure — and it is now a REAL second invocation, on the file the
    # first one wrote, not a re-application of a transcribed regex.
    check("the transform is IDEMPOTENT (a second pass changes nothing)",
          _run_fixture(), _after)
    # ⚑ A REFUSED ROW IS NOT REWRITTEN — the dry path must report zero for a row
    # whose spelling is not `stale`.
    check("repair_sections refuses an AMBIGUOUS row",
          repair_sections([("NoSuchMod", 1, "AMBIGUOUS", "")], apply=False), 0)

    # ⚑⚑ A DOUBLED OPERATOR IS A DIFFERENT OPERATOR, NOT A SECTION.  `_++_` (list
    # append) matched `_+` until the operator character was excluded on BOTH
    # sides — and this is the case that exposed the scan and the transform as TWO
    # SPELLINGS OF ONE PREDICATE: the scan reported two sites in `S5/S5TwoFuelFix`
    # and `repair_sections` refused both, `0 repairable` from `2 section(s)`.  The
    # transform was right.  `_section_patterns` is now the single authority both
    # read, so a divergence like that cannot recur silently.
    _r_, _l_ = _section_patterns("+", "ℕ+")
    check("a doubled operator `_++_` is not a section (right)",
          bool(_r_.search("_++_ : List S → List S → List S")), False)
    check("...nor on the left arm", bool(_l_.search("infixr 5 _++_")), False)
    check("a genuine right section still matches", bool(_r_.search("cong (x +_) p")),
          True)
    check("a genuine left section still matches", bool(_l_.search("cong (_+ y) q")),
          True)
    # ⚑ AND THE ALREADY-RENAMED FORM IS EXCLUDED FOR THE SAME REASON, which is what
    # makes the transform idempotent — `ℕ+_` must not read as `+_`.
    check("an already-renamed section is not matched",
          bool(_r_.search("cong (x ℕ+_) r")), False)

    # ⚑⚑ BOTH REFUSAL ARMS ARE INERT ON TODAY'S TREE — the census reports 0 AMBIGUOUS
    # and 0 on a compiling module — so each must be DRIVEN by a constructed row or it
    # is unexercised code sitting on the WRITE path (peer session, 2026-08-18:
    # *"If `--apply` refuses on conditions that have never once fired, the refusals are
    # unexercised code on the write path"*).  The `--stale-sections` CLI arm computes
    # `_safe` by dropping rows whose build verdict is `clean`; this drives that filter
    # directly, since the arm itself needs a census the suite does not have.
    _mixed = [("M.Clean", 1, "stale", ""), ("M.Broken", 2, "stale", ""),
              ("M.Amb", 3, "AMBIGUOUS", "")]
    _fakev = {"M.Clean": ("clean", ""), "M.Broken": ("own", "")}
    _safe_t = [r for r in _mixed if _fakev.get(r[0], ("unmeasured", ""))[0] != "clean"]
    check("the compiling-module arm DROPS a `clean` row",
          [r[0] for r in _safe_t], ["M.Broken", "M.Amb"])
    check("...and keeps a row the build calls broken", "M.Broken" in
          [r[0] for r in _safe_t], True)
    check("...and an UNMEASURED row is kept, not silently dropped "
          "(unmeasured is not passing)",
          [r for r in _mixed if _fakev.get(r[0], ("unmeasured", ""))[0]
           == "unmeasured"], [_mixed[2]])
    # ⚑ AND THE TWO ARMS COMPOSE: a row that is BOTH clean and ambiguous is refused
    # once, not double-counted, and never reaches the writer.
    check("repair_sections writes nothing for the refused survivors",
          repair_sections([r for r in _safe_t if r[2] != "stale"], apply=False), 0)

    # (1) NON-CAPABILITY NAMES.  `Foundation/Eq/Preamble.agda` is eleven lines whose
    # only content is `private variable a b c : Level`, and `def_index` reports it as
    # DEFINING five names: a, b, c, private, variable.  Short and generic, they match
    # somewhere in nearly every file, so they cannot witness anything.
    check("a `variable` binder is not treated as an export",
          _variable_binders("Substrate.Foundation.Eq.Preamble") >= {"a", "b", "c"},
          True)
    check("...and agda keywords are not capabilities",
          {"where", "variable", "private"} <= _NOT_A_CAPABILITY, True)
    check("no row is witnessed by a single-character name",
          [r for r in _li if len(r[3]) < 2], [])

    # (2) LOCALLY-SHADOWED NAMES, AT MODULE GRAIN.  `R/Trace/ExtruderRSideRealigned`
    # DEFINES `BareEq` at :44 and uses it at :51; both are the LOCAL one, and the
    # import of a same-named export at :81 is irrelevant.  Filtering the DEFINING LINE
    # was not enough — the census moved to the next use and kept reporting a compiling
    # file.  The fact is per-MODULE: if a module defines a name, no occurrence of it
    # is evidence about any import.
    check("a name the module itself defines witnesses nothing",
          [r for r in _li if r[3] in provides(r[0])], [])

    # (3) DUPLICATE IMPORTS — EARLIEST BINDS.  `ExtrudeCoEmitTraceEq` imports
    # `ExtrudeCoEmitMonad ℕ` at :13 (`using (CoEmit; …)`) AND at :52 (`using
    # (bind-ret-left; …)`); `CoEmit` at :20 is served by the FIRST.  Testing every
    # occurrence reports the second and the file compiles.
    _dup = "Substrate.Category.UniversalProperty.ExtrudeCoEmitTraceEq"
    check("a module imported twice is judged at its EARLIEST import",
          [r for r in _li if r[0] == _dup], [])

    # (4) MODULE-PARAMETER BINDERS.  `Groups/Capabilities/Strict2Monoid.agda:28` is
    # `module _ (Word : Set) where` — a binding site, reported against
    # `Coxeter.Word`'s export `Word`.  ⚑ THE ROW WAS RIGHT ABOUT THE FILE AND WRONG
    # ABOUT THE WITNESS: that file DID carry a late import (`Foundation.Eq` at :50,
    # `≡` needed at :34), and acting on the stated witness would have moved the wrong
    # statement.  Being right for the wrong reason is the most misleading outcome, so
    # it is pinned rather than merely fixed.
    check("a `module _ (X : Set) where` parameter is not a use",
          [r for r in _li if r[3] == "Word"
           and r[0] == "Substrate.Groups.Capabilities.Strict2Monoid"], [])

    # ⚑ THE VERDICT JOIN IS WHAT MAKES THE MODE SELF-FALSIFYING.  A positional claim
    # about source needs a semantic oracle, and this mode's oracle is the build.
    # Without it a `clean` row reads as a finding instead of as noise.
    check("the CLI joins each row to the build census, not just the position",
          "census_from_build" in _src and "--late-imports" in _src, True)
    check("...and reports the count of rows on COMPILING modules",
          "does not\n" in _src or "not findings" in _src, True)

    check("modules_under enumerates the subtree",
          "Substrate.WitnessTower.Core"
          in modules_under("Substrate.WitnessTower"), True)
    check("modules_under is prefix-scoped, not substring-scoped",
          all(m.startswith("Substrate.WitnessTower")
              for m in modules_under("Substrate.WitnessTower")), True)

    # ⚑ THE TRUST SURFACE.  `--grep` searches NAMES; `postulate`, `TERMINATING`
    # and `?` are keywords/pragmas and are invisible to it BY CONSTRUCTION — so
    # "any postulate or --safe exemption in this subtree?" had no reader at all.
    _tc = trust_census("Substrate.WitnessTower")
    _tn = _tc.pop("_scanned")
    # ⚑ THE PROPERTY, NOT A SNAPSHOT COUNT. This asserted `_tn == 347`, the subtree's
    # size on the day it was written; the tree reached 349 and the case reported the
    # SCANNER broken when nothing about it had changed. A corpus size is exactly the
    # kind of value a healthy repo moves, so pinning it makes the case fail on growth —
    # a regression report with no regression, and the reader's first instinct is to
    # doubt the tool. Assert instead that the census sees every module the enumeration
    # authority sees: that is the claim "scans the whole subtree" actually makes, and it
    # keeps discriminating (a scanner that skipped a directory still fails).
    check("trust_census scans the whole subtree",
          _tn == len(modules_under("Substrate.WitnessTower")), True)
    check("trust_census reports only modules WITH a finding",
          all(isinstance(v, dict) for v in _tc.values()), True)
    # ⚑ THE OPTION-WIDENING CASE.  `--safe --without-K --guardedness` is STILL
    # --safe, so a binary safe/unsafe predicate passes it silently — but
    # `--guardedness` is infective (carried in from a transitive import) and is a
    # genuine trust edge.  MEASURED: the first version of this scanner reported
    # 0 findings for the tower while `OrientationRigCatPermSignChirality:51`
    # carries exactly that widening, and a subagent reading SOURCES found it.
    check("trust_census FLAGS an option-widened but still --safe module",
          "--guardedness" in _tc.get(
              "Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality",
              {}).get("extra_options", []), True)
    check("...and does NOT flag a plain --safe --without-K module",
          "Substrate.WitnessTower.Core" not in _tc, True)
    check("extra_options excludes the baseline two",
          all(o not in ("--safe", "--without-K")
              for r in _tc.values() for o in r["extra_options"]), True)
    _all = trust_census()
    _an = _all.pop("_scanned")
    check("trust_census over the whole corpus scans more than the subtree",
          _an > _tn, True)
    check("trust_census finds SOME finding somewhere in the corpus",
          len(_all) > 0, True)
    check("a postulate block's members are parsed as names",
          all(all(isinstance(x, str) for x in r["postulates"])
              for r in _all.values()), True)
    check("the CLI exposes --trust", "--trust" in _src, True)

    # ⚑ THE FLAG-REFLECTION CENSUS (⒢′).  `--trust` measures the pragma against a
    # HARDCODED pair, so it can report a module WIDER than the baseline and can
    # never report one NARROWER than what the build applies.  These cases pin the
    # authorities and the two failure kinds a repair has to tell apart.
    _lf = library_flags()
    check("library_flags reads the repo's own .agda-lib",
          "substrate.agda-lib" in _lf, True)
    # ⚑ THE CASE THAT KILLS `line.split('--')[0]`.  Every Agda flag OPENS with the
    # comment marker, so a naive comment-strip returns an empty flag list and the
    # census silently measures against nothing.
    check("...and does NOT eat the flag as a comment (`flags: --guardedness`)",
          "--guardedness" in _lf.get("substrate.agda-lib", []), True)
    _cf = cmdline_flags()
    check("cmdline_flags reads AGDA_FLAGS from the GENERATOR, not Flat.mk",
          "--safe" in _cf and "--without-K" in _cf, True)
    _gl = global_flags()
    check("global_flags unions both authorities",
          all(f in _gl for f in ("--safe", "--without-K", "--guardedness")), True)
    # ⚑ THE ORIGIN IS PART OF THE ANSWER: a library flag reaches an ad-hoc
    # `agda -i .`, a command-line flag does not.  A census that returned a bare set
    # could not say which invocations carry which.
    check("...and keeps each flag's ORIGIN",
          "flags:" in _gl.get("--guardedness", "")
          and "AGDA_FLAGS" in _gl.get("--safe", ""), True)
    _fc = flag_census("Substrate.WitnessTower")
    _fn = _fc.pop("_scanned")
    _fg = _fc.pop("_global")
    check("flag_census scans the whole subtree",
          _fn == len(modules_under("Substrate.WitnessTower")), True)
    check("flag_census carries the reference set it measured against", _fg, _gl)
    check("...and every reported module names a MISSING global flag",
          all(r["missing"] and all(f in _gl for f in r["missing"])
              for r in _fc.values()), True)
    check("...and never reports a flag the module DOES name",
          all(f not in r["options"] for r in _fc.values()
              for f in r["missing"]), True)
    # ⚑ NARROWER IS THE FINDING `--trust` CANNOT MAKE.  This module carries
    # `--safe --without-K --guardedness` — `--trust` flags it as WIDENED; the
    # reflection census must NOT flag it, because it reflects the global set fully.
    check("a module that names every global flag is NOT a finding",
          "Substrate.WitnessTower.Wedge.OrientationRigCatPermSignChirality"
          not in _fc, True)
    check("...while a plain --safe --without-K module IS (it omits --guardedness)",
          _fc.get("Substrate.WitnessTower.Core", {}).get("missing"),
          ["--guardedness"])
    check("the CLI exposes --flags", "--flags" in _src, True)

    # ⚑ AGGREGATION IS A MODE, NOT A SCRIPT.  The raw edge dump for the tower is
    # 164 KB / 1619 edges; "which packages consume this" and "what does it depend
    # on" are the actual questions, and collapsing 164 KB by eye is the
    # judgement-in-the-turn shape the standing rule forbids.
    _cpkg, _ctgt = consumer_profile("Substrate.WitnessTower")
    check("consumer_profile aggregates external importers by package",
          len(_cpkg) > 0 and all(isinstance(v, int) for _k, v in _cpkg), True)
    check("consumer_profile EXCLUDES internal edges",
          all(not k.startswith("Substrate.WitnessTower") for k, _v in _cpkg), True)
    check("consumer_profile counts are descending",
          [v for _k, v in _cpkg] == sorted([v for _k, v in _cpkg], reverse=True),
          True)
    check("consumer_profile by_target names tower-side modules",
          all(t.startswith("Substrate.WitnessTower") for t, _v in _ctgt), True)
    check("consumer_profile --depth truncates the package key",
          all(len(k.split(".")) <= 2
              for k, _v in consumer_profile("Substrate.WitnessTower", 2)[0]), True)

    _dpkg, _dmod = dependency_profile("Substrate.WitnessTower")
    check("dependency_profile finds the tower's outbound clusters",
          len(_dpkg) > 0, True)
    check("dependency_profile EXCLUDES self-subtree imports",
          all(not m.startswith("Substrate.WitnessTower") for m, _v in _dmod), True)
    check("dependency_profile's top dependency outranks its tail",
          _dmod[0][1] >= _dmod[-1][1], True)
    check("the CLI exposes the aggregation modes",
          "--consumers" in _src and "--depends" in _src, True)

    check("the CLI exposes the edge modes",
          all(f in _src for f in ("--imports", "--importers",
                                  "--closure", "--cluster", "--under")), True)

    # ⚑ --between: the DIRECTION mode.  Pinned on an edge the corpus actually has
    # and on the ASYMMETRY, because the whole point of the mode is that the two
    # orders are different questions.  `Algebra.Nat.CyclicSuc` importing nothing
    # from the tower is the layering `CyclicSuc`'s own header asserts, so a
    # regression that made edges_between symmetric would fail here.
    _t2f, _, _ = edges_between("Substrate.WitnessTower", "Substrate.Algebra.F2")
    _f2t, _, _ = edges_between("Substrate.Algebra.F2", "Substrate.WitnessTower")
    check("--between finds tower→F2 edges", len(_t2f) > 0, True)
    check("--between is NOT symmetric (the inversion is measurable)",
          len(_t2f) != len(_f2t), True)
    check("--between edges all start in the source subtree",
          all(s.startswith("Substrate.WitnessTower") for s, _d in _t2f), True)
    check("--between edges all land in the destination subtree",
          all(d.startswith("Substrate.Algebra.F2") for _s, d in _t2f), True)
    check("the CLI exposes --between", "--between" in _src, True)

    # ⚑ --unused-imports: pinned on the WITNESS the F₂ survey hand-read, so the
    # mode is guarded by the case that motivated it.  `PackedBridge/F2ToFin2` has
    # a two-line body (`f2→fin2 𝟘 = fzero; f2→fin2 𝟙 = fsuc fzero`) behind 25 F₂
    # imports; all but the one providing F₂/𝟘/𝟙 are unused.  A regression that
    # re-derived the token scan instead of delegating would reproduce the `_,_`
    # bug and under-report here.
    _f2f = ("agda/Substrate/WitnessTower/Wedge/PackedBridge/F2ToFin2.agda")
    if _o.path.isfile(_f2f):
        _rows, _bar, _unread = unused_imports([_f2f])
        check("--unused-imports finds the F2ToFin2 block",
              bool(_rows) and len(_rows[0][1]) > 10, True)
        check("--unused-imports keeps the import that provides F₂",
              all(m != "Substrate.Algebra.F2.F2" for _l, m in (_rows[0][1] if _rows else [])),
              True)
        check("--unused-imports reports barrels/unreadable separately (not as clean)",
              isinstance(_bar, list) and isinstance(_unread, list), True)
    check("the CLI exposes --unused-imports", "--unused-imports" in _src, True)

    # ⚑ --dangling: the DISSOLVED-PARENT census. Pinned on invariants rather than a
    # live count, because paydown moves the count and a test anchored on it would
    # go stale the first time it succeeds (measured four times this session).
    _dang, _unj = dangling_imports()
    check("--dangling targets are all absent from the index",
          all(t not in import_index() for t, _ms in _dang), True)
    check("--dangling judges only Substrate targets",
          all(t.startswith("Substrate.") for t, _ms in _dang), True)
    check("--dangling reports non-Substrate targets as UNJUDGED, not dangling",
          all(not t.startswith("Substrate.") for t, _c in _unj), True)
    check("--dangling importers all EXIST (only the target is missing)",
          all(m in import_index() for _t, ms in _dang for m in ms), True)
    check("the CLI exposes --dangling", "--dangling" in _src, True)

    # ⚑ --qualified: the form the OTHER TWO censuses are structurally blind to.
    # Both read `open import`; `import M as Q` is a different statement, and
    # `rewire_to_leaves` reported `0 importer(s)` on 11 genuinely broken consumers
    # — a true statement about what it rewrites, read as nothing-to-do.
    _q = qualified_aliases()
    check("--qualified finds only Substrate targets",
          all(m.startswith("Substrate.") for _p, _n, m, _a, _e in _q), True)
    check("--qualified splits dead targets from live ones",
          all(isinstance(e, bool) for _p, _n, _m, _a, e in _q), True)
    check("--qualified rows carry a line number",
          all(isinstance(n, int) and n > 0 for _p, n, _m, _a, _e in _q), True)
    # the regex must not swallow a plain `open import` — the two forms are
    # different statements and conflating them would double-count the ban census.
    check("--qualified ignores plain `open import`",
          _QUALIFIED.match("open import Substrate.Algebra.F2.F2") is None, True)
    check("--qualified matches the aliased form",
          bool(_QUALIFIED.match("import Substrate.Algebra.F2 as F2")), True)
    check("the CLI exposes --qualified", "--qualified" in _src, True)

    # ⚑⚑ THE TRANSFORM, ON A FIXTURE — the arms whose absence let a corrupting
    # `qualified_repair` ship behind a green 174/174. Every case above tests the
    # CENSUS; none touched the writer. It rewrote `module Substrate.Algebra.F2.…`
    # into `module Substrate.Algebra.…` and repointed a sibling import, across ten
    # files, and the suite never dipped. Fixture-based so the cases cannot go stale
    # when the live tree is paid down (which has invalidated anchors four times).
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        _f = _o.path.join(_td, "Fx.agda")
        open(_f, "w").write(
            "module Substrate.Algebra.F2.Poly.Fx where\n"
            "import Substrate.Algebra.F2 as F2\n"
            "open import Substrate.Algebra.F2.CommRing using (R)\n"
            "-- prose naming F2.𝟘 must survive verbatim\n"
            "v : F2.F₂\n"
            "v = F2.𝟘\n"
            "module Over (m : F2.F₂) where\n")
        qualified_repair("Substrate.Algebra.F2", apply=True, paths=[_f])
        _got = open(_f).read().split("\n")
        check("⚑ transform leaves the MODULE line alone",
              _got[0], "module Substrate.Algebra.F2.Poly.Fx where")
        check("⚑ transform leaves a SIBLING import alone",
              any(l == "open import Substrate.Algebra.F2.CommRing using (R)"
                  for l in _got), True)
        check("⚑ transform leaves COMMENT prose verbatim",
              any("prose naming F2.𝟘 must survive" in l for l in _got), True)
        check("transform strips the qualifier at a USE site",
              any(l == "v = 𝟘" for l in _got), True)
        check("transform strips it in a SIGNATURE too",
              any(l == "v : F₂" for l in _got), True)
        check("transform replaces the aliased import with the real home",
              any(l == "open import Substrate.Algebra.F2.F2" for l in _got), True)
        # ⚑ a NESTED module's TELESCOPE is a use site — skipping every `module `
        # line left one behind, and only the compiler caught it (:52).
        check("⚑ transform strips it in a NESTED module telescope",
              any(l == "module Over (m : F₂) where" for l in _got), True)
    # ⚑⚑ REPEATED ALIASES ON ONE CLAUSE-BODY LINE — the shape that shipped broken.
    # `AES/KeySchedule.agda:50` reads `rc1 = F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ …`; after the
    # transform every `F2.𝟘` was stripped and every `F2.𝟙` SURVIVED, leaving the
    # file uncompilable and INVISIBLE to `--qualified` (which reads import
    # statements, and the import was already correctly replaced). The suite was
    # green throughout — 191/191 — because no arm put two DIFFERENT aliased names
    # on one line. That is the missing-arm class a third time in this tool.
    with _tf.TemporaryDirectory() as _td3:
        _h = _o.path.join(_td3, "Hx.agda")
        # ⚑⚑ ENCODING IS EXPLICIT HERE, AND THAT IS THE WHOLE DEFECT. This fixture
        # used bare `open(path, "w")`, which takes the LOCALE default — and the
        # corpus is full of non-ASCII names (`𝟙`, `𝟘`, `∷`). Under a non-UTF-8
        # locale the write mangles them, so the transform under test received input
        # that did not contain what the test thought it wrote. FOUR cause
        # hypotheses were spent on `qualified_repair`'s logic; the function is
        # CORRECT, as `--alias-trace … --run` shows on an identical file written
        # from the shell. The defect was in the TEST's I/O, not the code under test.
        #
        # ⚑ `qualified_repair` itself reads and writes with bare `open()` too, which
        # is the same latent bug in the tool — it happens to work because this
        # session's locale is UTF-8, and would corrupt every Agda file under one
        # that is not. Fixed there as well; see the function.
        open(_h, "w", encoding="utf-8").write(
            "module Substrate.Algebra.F2.Poly.Hx where\n"
            "import Substrate.Algebra.F2 as F2\n"
            "rc : Set\n"
            "rc = F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ []\n")
        qualified_repair("Substrate.Algebra.F2", apply=True, paths=[_h])
        _h2 = open(_h, encoding="utf-8").read()
        # ⚑⚑ THIS ARM WAS KEPT INVERTED FOR ONE ROUND, asserting the DEFECT was
        # present, because two attempts at a cause were both wrong and shipping a
        # third guess over a file-corrupting transform is how the
        # verification-that-cannot-fail class recurs. ⓉQUALFIX-CAUSE found it: the
        # `<alias>.name` regex was written THREE TIMES in one function — once to
        # scan, twice to rewrite — and a capture fix reached only the rewrite
        # copies, so the two halves disagreed about where a name ends. Both now
        # route through `_alias_pattern`.
        #
        # ⚑ NEITHER FAILED GUESS WAS THE CAUSE, and both were plausible: a greedy
        # capture swallowing `∷`, then a `" : "` line filter. The real defect was
        # not in either path's LOGIC but in there being two of them — the
        # `agda_files()`-was-four-bodies shape, inside a single function.
        # ⚑⚑⚑ THE ASSERTION WAS THE DEFECT, NOT THE TRANSFORM. This read
        # `"F2." not in _h2` — but a CORRECT result necessarily contains `F2.`,
        # inside the module path `Substrate.Algebra.F2.F2` and the header
        # `Substrate.Algebra.F2.Poly.Hx`. So the arm could never pass, and every
        # cause hypothesis it provoked was a hunt for a bug that did not exist.
        #
        # ⚑ FIVE HYPOTHESES DIED HERE, ALL FROM READING CODE: greedy capture; a
        # `" : "` line filter; read/write pattern drift; unresolved-name guard;
        # locale encoding. The third was a real defect and worth the fix, but it
        # was not THIS. What settled it was printing the post-repair bytes — one
        # `repr` — after `--alias-trace … --run` had already shown the same fixture
        # transforming correctly outside the suite. THE DISCRIMINATOR WAS THAT ONE
        # PASSED AND ONE FAILED ON IDENTICAL INPUT, which points at the observer,
        # and I spent four rounds pointing at the observed instead.
        #
        # ⚑ AND `AES/KeySchedule.agda` WAS A SEPARATE, REAL BREAK — half-stripped
        # by an EARLIER version of the transform (before the pattern was unified),
        # hand-repaired, compiling. Its existence made a phantom defect here look
        # corroborated: two facts, one true, read as one story.
        _qual_refs = _alias_refs("F2", _h2)
        check("⚑ EVERY aliased name on a line is stripped, not just some",
              _qual_refs, [])
        check("repeated-alias line keeps its structure",
              any(l == "rc = 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟙 ∷ []" for l in _h2.split("\n")), True)
        check("the aliased import is replaced by the real home",
              any(l == "open import Substrate.Algebra.F2.F2"
                  for l in _h2.split("\n")), True)
    # ⚑ THE ZERO-USE CASE: a dead alias must have its import DELETED, not skipped.
    # Three FUSepQ files kept a dangling import while the run reported "applied to
    # 4" — fixing 1. A count of files TOUCHED is not a count of files REPAIRED.
    with _tf.TemporaryDirectory() as _td2:
        _g = _o.path.join(_td2, "Gx.agda")
        open(_g, "w").write(
            "module Substrate.Algebra.F2.Poly.Gx where\n"
            "import Substrate.Algebra.F2 as F2\n"
            "x : Set\n"
            "x = Set\n")
        qualified_repair("Substrate.Algebra.F2", apply=True, paths=[_g])
        _g2 = open(_g).read().split("\n")
        check("⚑ a DEAD alias has its import deleted",
              not any("import Substrate.Algebra.F2 as F2" in l for l in _g2), True)
        check("deleting a dead alias leaves the rest intact",
              _g2[0], "module Substrate.Algebra.F2.Poly.Gx where")

    # ⚑ --orphans: dropped-alias debris. Pinned on the SHAPE, not on a live count —
    # the two `ℕ≤` instances that motivated it were repaired before it existed, so
    # a tree-anchored case would test nothing. The discriminations below are what a
    # first cut got wrong: it scanned whole BODIES and returned 220 sites of which
    # NONE were the class (syntax `→`/`∀`, level vars `ℓ`, pattern binders `b₁`).
    _orph = orphan_names()
    _orph_names = {t for t, _s in _orph}
    check("⚑ --orphans does not report Agda SYNTAX as an orphan",
          _orph_names.isdisjoint({"→", "∀", "λ", "Set", "→"}), True)
    check("⚑ --orphans does not report LEVEL variables as orphans",
          "ℓ" not in _orph_names, True)
    check("--orphans reports every site with a line number",
          all(isinstance(n, int) and n > 0 for _t, ss in _orph for _p, n in ss),
          True)
    check("--orphans only judges non-ASCII tokens (the stated floor)",
          all(_ALIASY.search(t) for t in _orph_names), True)

    # ⚑ --flat-variable / --dup-variables: two readers for ONE splitter defect, and
    # neither existed until a dangling repair walked into it. The split copied a
    # `variable` preamble into every leaf of a cluster AND flattened it onto one
    # line; the flattening was a [ParseError] (loud), the copying was latent until
    # two leaves met in one scope (quiet). `def_index` carries no generalizable
    # variables, so `agda_defs S₁` reported NO DEFINER for a name declared in five
    # modules — every other census here was blind to the whole class.
    check("--flat-variable finds no unparseable blocks (the class is paid down)",
          flat_variable_blocks(), [])
    _dups = variable_declarations("Substrate.Category.UniversalProperty")
    check("--dup-variables reports only names in >1 module",
          all(len(ms) > 1 for _n, ms in _dups), True)
    check("--dup-variables no longer reports the repaired UPArrow2 cohort",
          not any(n in ("S₁", "W₁", "T₃") and len(ms) > 1 for n, ms in _dups
                  if any("ArrowOfArrow" in m for m in ms)
                  and any("Compose" in m for m in ms)), True)
    check("the CLI exposes --flat-variable and --dup-variables",
          "--flat-variable" in _src and "--dup-variables" in _src, True)

    # ⚑ --double-route: the cohort neither `--reexports` nor the compiler-per-file
    # can see. Pinned on the INVARIANT (every row imports both sides), not a live
    # count — paydown moves the count, and four live-tree anchors went stale today.
    _dr = double_route_names("Substrate.Algebra.Polynomial.Graded.FromCommRing",
                             "Substrate.Algebra.F2")
    _ii = import_index()
    check("--double-route rows import the GENERIC",
          all("Substrate.Algebra.Polynomial.Graded.FromCommRing" in _ii.get(m, [])
              for m, _ls in _dr), True)
    check("--double-route rows import at least one LEAF under the prefix",
          all(ls and all(_in_subtree(l, "Substrate.Algebra.F2") for l in ls)
              for _m, ls in _dr), True)
    check("--double-route reports nothing for a generic nothing pairs with",
          double_route_names("Substrate.Foundation.Eq.Cong2",
                             "Substrate.NoSuchSubtree"), [])
    check("the CLI exposes --double-route", "--double-route" in _src, True)
    check("--unused-imports delegates rather than re-deriving the scan",
          "should_keep" in _src or "prune_imports" in _src, True)

    # ⚑ --stranded-residue: THE THREE-VALUED VERDICT IS THE THING UNDER TEST.
    # A two-valued reading (re-homed vs damage) would fold `unused` into damage and
    # report work that does not exist, so the cases pin that all three CAN be
    # returned and that the live red leaf lands on `live-damage` specifically.
    _sr = dict(stranded_residue())
    _surreal = next((v for k, v in _sr.items() if "/Surreal/" in k), [])
    _sv = {n: v for n, v, _w in _surreal}
    check("--stranded-residue finds the Surreal telescope binders",
          sorted(_sv), ["≤ⁿ-refl", "≤ⁿ-trans"])
    check("...and calls BOTH live damage (a leaf uses them; nothing binds)",
          sorted(set(_sv.values())), ["live-damage"])
    # ⚑ THE DAMAGE ROW MUST NAME THE CONSUMER. A verdict with no witness is the
    # absence-claim this repo censuses elsewhere; the operator rules on the leaf.
    check("...naming the leaf that consumes them",
          all(any("SurrealQuotient" in w for w in _w)
              for _n, _v, _w in _surreal), True)

    # ⚑ RE-HOMED IS SIBLING-SCOPED, AND THE FIRST CUT GOT THIS WRONG. Asking
    # `def_index()` tree-wide reported `Word` re-homed on the strength of
    # `Coxeter.Word` — a DIFFERENT `Word`. Every witness must be a sibling leaf
    # under the residue's own directory, or the verdict is a coincidence.
    _idem = next((v for k, v in _sr.items() if "/IdemInequality/" in k), [])
    check("--stranded-residue reports IdemInequality's binders re-homed",
          sorted({v for _n, v, _w in _idem}), ["re-homed"])
    check("...witnessed ONLY by sibling leaves, never a tree-wide namesake",
          all(w.startswith("Substrate.Groups.Coxeter.Core.IdemInequality.")
              for _n, _v, ws in _idem for w in ws), True)

    # ⚑ A NON-TELESCOPE RESIDUE IS `no-binders`, NOT SILENCE. "not this question"
    # and "nothing to do" must not render alike — the same distinction
    # `--unused-imports` draws between a barrel and a clean file.
    _f2 = next((v for k, v in _sr.items() if "/F2/" in k), [])
    check("a bare fixity residue reports no-binders rather than vanishing",
          [v for _n, v, _w in _f2], ["no-binders"])

    check("the CLI exposes --stranded-residue", "--stranded-residue" in _src, True)
    # ⚑ AND IT IS A CENSUS. `write_residue` says the re-home-or-delete call must be
    # a DECISION; a mode that grew an --apply would be making it as a side effect.
    # ⚑⚑ ASK THE SIGNATURE, NOT THE SOURCE TEXT. The first cut tested `"…apply" not
    # in _src` — and FAILED, because `_src` is the whole module and the assertion's
    # OWN string was the match. A source-substring test over a file that contains
    # the test is self-defeating; the signature is the fact.
    import inspect as _i2
    check("--stranded-residue is a census: no `apply` parameter exists",
          "apply" in _i2.signature(stranded_residue).parameters, False)

    ok = sum(1 for _n, g, _got, _w in cases if g)
    for n, g, got, w in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {w!r}")
    print(f"agda_defs selftest: {ok}/{len(cases)}")
    return ok == len(cases)


if __name__ == "__main__":
    import sys as _sys
    if "--selftest" in _sys.argv:
        _sys.exit(0 if _selftest() else 1)

    # ⚑ THE AUTHORITY HAD NO WAY TO BE ASKED (audit finding 3, §48).  This module
    # is THE name→home index for **19 importing tools**, and `__main__` dispatched
    # only `--selftest` — so every tool could resolve a name and a HUMAN could not.
    # The measured consequence: "where does `divmod-unique` live?" got answered by
    # a `python3 -c` over `def_index` or by grep, and `resolve_notinscope.py:13`
    # names that defect verbatim.  `def_index` and `provides` already return
    # exactly these answers; only the entry point was missing.
    _args = [a for a in _sys.argv[1:] if not a.startswith("-")]
    if "--grep" in _sys.argv:
        # which NAMES look like this?  (the pattern question — see grep_names)
        for pat in _args:
            hits = grep_names(pat)
            for n, mods in hits:
                for h in mods:
                    print(f"{n}\t{h}")
            print(f"{pat}: {len(hits)} name(s) matching in agda/Substrate")
        _sys.exit(0)
    # ⚑ THE EDGE MODES.  See `import_index` for why these exist: six private
    # copies of the import regex, zero ways to ASK the corpus about an edge.
    if "--imports" in _sys.argv:
        _ii = import_index()
        for mod in _args:
            imps = _ii.get(mod)
            if imps is None:
                print(f"{mod}\n      (no such module in agda/Substrate)")
                continue
            print(mod)
            for i in imps:
                print(f"      -> {i}")
            print(f"{mod}: {len(imps)} import(s)")
        _sys.exit(0)
    if "--at" in _sys.argv:
        _i = _sys.argv.index("--at")
        _rev = _sys.argv[_i + 1] if _i + 1 < len(_sys.argv) else "HEAD"
        _mods = [a for a in _args if a != _rev]
        for _m in _mods:
            # ⚑⚑ THE THREE ARMS REACH THE CLI SEPARATELY (⟡vfs-chokepoints).  Before
            # the `vfs` promotion, `at_revision` returned `None` for a bad sha AND for
            # a genuinely-new module, so BOTH printed `DID NOT EXIST` — a typo'd
            # revision reported as a fact about history.  BROKEN is now caught and
            # REFUSED by name; ABSENT keeps its original line verbatim.
            try:
                _txt, _rel = at_revision(_m, _rev)
            except (ValueError, RuntimeError) as _e:
                # ⚑ NAMES THE ARM AND ITS SUCCESSOR.  The read did NOT happen — this
                # is emphatically not "the module is new in the working tree".
                print(f"── {_m} @ {_rev}: BROKEN — the read did not happen: {_e}\n"
                      f"   (this is NOT an absence; check the revision spelling)",
                      file=_sys.stderr)
                _sys.exit(2)
            if _txt is None:
                # ⚑ ABSENT ≠ EMPTY.  A module that did not exist at `rev` is a fact
                # about history, and a restore that silently treats it as "" would
                # invert exactly the thing being asked.
                print(f"── {_rel} @ {_rev}: DID NOT EXIST")
                continue
            if "--diff" in _sys.argv:
                import difflib
                try:
                    _now = open(_rel, encoding="utf-8", errors="replace").read()
                except OSError:
                    _now = ""
                _d = list(difflib.unified_diff(
                    _txt.split("\n"), _now.split("\n"),
                    fromfile=f"{_rel} @{_rev}", tofile=f"{_rel} (working tree)",
                    lineterm=""))
                print("\n".join(_d) if _d else f"── {_rel}: identical to {_rev}")
            else:
                print(f"── {_rel} @ {_rev}")
                print(_txt, end="")
        _sys.exit(0)
    if "--telescope" in _sys.argv:
        rows = telescope_contract(_args[0] if _args else None)
        bad = 0
        for mod, params, cons in rows:
            arities = {n for _c, _l, n, _a in cons}
            mism = [c for c in cons if c[2] != len(params)]
            mark = "  ⚑ ARITY MISMATCH" if mism else ""
            print(f"{mod}.Over   declares {len(params)} explicit param(s){mark}")
            print(f"   {' '.join(params)}")
            print(f"   {len(cons)} consumer(s), applying {sorted(arities)} argument(s)")
            for c, ln, n, _a in mism[:8]:
                print(f"      ✗ {c}:{ln} applies {n}")
            bad += len(mism)
        # ⚑⚑ ARITY IS THE WEAKER CHECK, AND THIS IS THE ONE THAT FINDS THE DEFECT.
        # Sibling shards of one split share a contract: they declare the SAME arity and
        # chain by passing their own parameters positionally into each other's `Over`.
        # A rename that walks into a telescope leaves the arity intact and changes only
        # WHICH NAME occupies a slot — so it typechecks at the application (every
        # argument is still `A`-typed) and fails far away, in whichever body then uses
        # the name at the wrong domain.
        #
        # MEASURED 2026-08-17 across `Graded.Laws.*`: 14 shards, 14 params each, 87
        # consumer applications, ZERO arity mismatches — and FIVE different spellings
        # of the same contract, because a tree-wide `rename_at_source` rewrote carrier
        # parameters (`+-assoc` → `+ℕ-assoc`) in 11 of the 14.  An arity-only report
        # calls that green.  The divergence report is what makes it a finding.
        # ⚑⚑ GROUP BY CONTRACT, NOT BY ARITY — arity is a PROXY and it reports
        # unrelated modules as divergent.  MEASURED 2026-08-17: the arity-1 bucket
        # paired `Graded.Base.Over (𝟘)` with `FromCommRing.Over (CR)` and
        # `PolyDivWedge.Over (CR)` — three different contracts that happen to take one
        # argument — and dutifully reported `Base` as deviating from a "majority" it
        # shares nothing with.  Two providers are under ONE contract when some consumer
        # applies them with the SAME argument list: that is what a shard chain does
        # (`open A0.Over _+_ _*_ 𝟘 𝟙 …` beside `open A1.Over _+_ _*_ 𝟘 𝟙 …`), and it is
        # the relation that makes a slot comparison meaningful.
        #
        # ⚑ THE EDGE IS THE CONSUMER'S, NOT THE PROVIDERS'.  Nothing in a provider
        # declares its family; the fact that two are interchangeable lives in the call
        # sites.  So the grouping is derived from `rows`' consumer side — union-find
        # over "co-applied with identical args by the same file".
        parent = {m: m for m, _p, _c in rows}

        def _find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def _union(a, b):
            ra, rb = _find(a), _find(b)
            if ra != rb:
                parent[rb] = ra

        by_site = {}
        for mod, _params, cons in rows:
            for c, _ln, _n, args in cons:
                by_site.setdefault((c, " ".join(args)), []).append(mod)
        for mods in by_site.values():
            for m in mods[1:]:
                _union(mods[0], m)
        groups = {}
        for mod, params, _cons in rows:
            groups.setdefault((_find(mod), len(params)), []).append((mod, params))
        div = 0
        for (_root, n), members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
            if len(members) < 2:
                continue
            per_slot = list(zip(*[p for _m, p in members]))
            odd = [(i, sorted(set(s))) for i, s in enumerate(per_slot) if len(set(s)) > 1]
            if not odd:
                continue
            div += len(odd)
            print(f"\n⚑ NAME DIVERGENCE among {len(members)} provider(s) of arity {n}:")
            print("   ⚑ THE MAJORITY IS NOT AUTOMATICALLY THE CONTRACT — a sweep that"
                  " hit most\n     siblings makes the DAMAGE the majority. Read the"
                  " slot's TYPE, or git, to\n     decide which spelling is right;"
                  " this reports the split, not the verdict.")
            for i, spellings in odd:
                # the majority is REPORTED as a datum, never as the target — see above
                tally = {}
                for _m, p in members:
                    tally[p[i]] = tally.get(p[i], 0) + 1
                major = max(tally, key=lambda k: tally[k])
                print(f"   slot {i}: {len(spellings)} spellings — majority `{major}`"
                      f" ({tally[major]}/{len(members)})")
                for _m, p in members:
                    if p[i] != major:
                        print(f"      ✗ {_m} binds `{p[i]}`")
        _n = sum(len(c) for _m, _p, c in rows)
        print(f"\ntelescope: {len(rows)} provider(s), {_n} consumer application(s)"
              + (f"; {bad} ARITY MISMATCH(es)" if bad else "; every consumer matches")
              + (f"; {div} DIVERGENT slot(s)" if div else ""))
        # ⚑ A TELESCOPE IS A CONTRACT WITH N CALLERS, so a mismatch is a GATE
        # condition, not a report: editing a provider's telescope breaks callers
        # that were correct before, and the error surfaces in the consumer.
        _sys.exit(1 if (bad or div) else 0)
    if "--stale-sections" in _sys.argv:
        # ⚑⚑ THE RENAME IS AN ARGUMENT, NOT A DEFAULT.  `stale_sections` was always
        # general over (op, renamed, home) and only this CLI arm froze it to the F₂
        # rename — the hardcoded-vocabulary defect the struct-tools skill names, and
        # I shipped it.  MEASURED 2026-08-18: the ℕ rename (`_+_` → `_ℕ+_`, home
        # `Foundation.Nat.Plus`) is the SAME class, and I walked eleven of its sites
        # one compile at a time in `S5/S5Carrier.agda` before noticing the mode I had
        # just built already answered it.
        #
        # `--rename op=renamed@Home` names the transform; the F₂ default stands
        # because it is the population this was measured on.
        _op, _new, _home = "+", "+F", "Substrate.Algebra.F2.PlusF"
        for _a in _sys.argv:
            if _a.startswith("--rename="):
                _spec = _a.split("=", 1)[1]
                _lhs, _, _home = _spec.partition("@")
                _op, _, _new = _lhs.partition(":")
                if not (_op and _new and _home):
                    print("usage: --rename=<op>:<renamed>@<Home.Module>\n"
                          "   e.g. --rename=+:ℕ+@Substrate.Foundation.Nat.Plus",
                          file=_sys.stderr)
                    _sys.exit(2)
        rows = stale_sections(_args[0] if _args else None,
                              op=_op, renamed=_new, home=_home)
        _verdict = {}
        try:
            import split_census as _sc
            for _rel, _v, _c in _sc.census_from_build(AG):
                _verdict[_rel[:-5].replace("/", ".") if _rel.endswith(".agda")
                         else _rel] = (_v, _c)
        except Exception as _e:
            print(f"   ⚠ build census unreadable ({_e}) — verdicts UNKNOWN")
        # ⚑ THE HEADER NAMES THE RENAME IT RAN, not a frozen example.  It read
        # "`+_` / `_+` … is `+F`" on an ℕ+ run — a report describing a transform
        # other than the one performed, which is how a reader mis-files a result.
        print(f"-- a SECTION left on a renamed operator (`{_op}_` / `_{_op}` where "
              f"the file's operator is `{_new}`, home {_home.split('.')[-1]}) --")
        _amb = _clean = 0
        for mod, ln, spelling, text in rows:
            v, _c = _verdict.get(mod, ("unmeasured", ""))
            if spelling == "AMBIGUOUS":
                _amb += 1
            if v == "clean":
                _clean += 1
            print(f"  {spelling:<10} {v:<11} {mod}:{ln}\n                          "
                  f"{text}")
        print(f"\n{len(rows)} section(s); {_amb} AMBIGUOUS, "
              f"{_clean} on a module that COMPILES")
        if _clean:
            # ⚑ A `clean` ROW IS A FALSE POSITIVE, NOT A BACKLOG ITEM.  If the
            # module builds, the section resolves — the scan is matching a
            # spelling that means something here, and saying so is the honest
            # report.  This is the self-falsifying join `--late-imports` was
            # rebuilt around after asserting a header false for 13 of 18 rows.
            print("   ⚑ a row on a COMPILING module is a false positive — the "
                  "section resolves there.")
        if _amb:
            print("   ⚑ AMBIGUOUS: the file imports another provider of the OLD "
                  "spelling, so\n     only the typechecker can say which is "
                  "meant.  Left alone by design.")
        print("   ⚑ the fix is to FINISH THE RENAME at the site — nothing is "
              "displaced here, so\n     `fix_noparse` correctly refuses this "
              "class (it repairs a DISPLACED operator).")
        # ⚑⚑ THE COMPILING-MODULE REFUSAL IS ENFORCED HERE, not merely printed.
        # A row on a module the build accepts is a FALSE POSITIVE by construction
        # — the section resolves there — so it must never be rewritten.  The
        # report above already names them; this is what makes the report a GATE.
        _safe = [r for r in rows if _verdict.get(r[0], ("unmeasured", ""))[0]
                 != "clean"]
        # ⚑ THE TRANSFORM TAKES THE SAME PARAMETERS AS THE SCAN.  Passing only
        # `_safe` would scan for one rename and repair with another's spelling —
        # the two-halves-disagree shape that `fix_noparse`'s `culprit` bug was.
        _n = repair_sections(_safe, op=_op, renamed=_new,
                             apply="--apply" in _sys.argv)
        print(f"\n{_n} site(s) "
              f"{'rewritten' if '--apply' in _sys.argv else 'repairable'}"
              + ("" if "--apply" in _sys.argv else "  (dry run — pass --apply)"))
        if len(rows) - len(_safe):
            print(f"   ⚑ {len(rows) - len(_safe)} row(s) REFUSED: on a module "
                  f"the build calls clean.")
        if _amb:
            print(f"   ⚑ {_amb} row(s) REFUSED: AMBIGUOUS.")
        if "--apply" in _sys.argv and _n:
            # ⚑ NO LOOP.  One pass, then re-verify — a repaired line can carry a
            # second error, and guessing the next one is how the line-local
            # heuristic in `fix_noparse` went wrong.
            print("   ⚑ one pass only — re-verify the touched modules; a repaired "
                  "line can carry a second error.")
        _sys.exit(0)
    if "--lp-apply" in _sys.argv:
        # ⚑ THE CENSUS ONLY.  ~28 sites were repaired by hand before this existed
        # and the shape never varied, which is what makes it a transform — but the
        # WRITE is deliberately not here yet: each repair also renames use sites,
        # and a rename that misses one leaves a file that compiles against the
        # WRONG instance in a two-index module.  Report first; the transform is
        # ⓉLP-APPLY-WRITE and wants the two-index case pinned by a selftest.
        _rows = lp_apply(_args[0] if _args else None)
        _q = [r for r in _rows if r[2]]
        _u = [r for r in _rows if not r[2]]
        _nobase = []
        for _p, _i, _qf, _bq, _nm in _q:
            print(f"   {_p}\tindex {_i}\tvia {_qf}\t{', '.join(_nm)}")
            if _bq:
                print(f"        + import …Coxeter.ListPresentation")
                print(f"            {_bq}.Gen {_qf}.Canonical-ex {_qf}.c-ε "
                      f"{_bq}.insert {_qf}.insert-canonical-ex as <Z>LP")
            else:
                _nobase.append((_p, _i))
                print(f"        ⚑ no `Cyclic.Base {_i}` binding in this file — the "
                      f"repair must ADD one; `Gen`/`insert` come from there")
        if _u:
            print("   ── UNQUALIFIED (bare open) — reported, never auto-rewritten:")
            for _p, _i, _qf, _bq, _nm in _u:
                print(f"      {_p}\tindex {_i}")
        print(f"lp-apply: {len(_q)} qualified site(s), {len(_u)} unqualified"
              + (f", {len(_nobase)} needing a Base binding" if _nobase else "")
              + (f"; {_args}" if _args else ""))
        _sys.exit(0)
    if "--telescope-imports" in _sys.argv:
        # ⚑ THE SUCCESSOR OF `--repair-telescopes`, and a DIFFERENT question: a
        # telescope whose types nothing imports above the header.  Restoring a
        # parameter is what makes its type load-bearing there, so this state is
        # unreachable from the census that produced it.
        _apply = "--apply" in _sys.argv
        if not _apply and "--dry-run" not in _sys.argv:
            print("⚑ state --apply or --dry-run: a mutating mode must not GUESS.")
            _sys.exit(2)
        _rows = telescope_imports(_args[0] if _args else None, apply=_apply)
        _n_need = 0
        for _p, _need, _amb in _rows:
            if _need:
                _n_need += 1
                print(f"   {'imported' if _apply else 'would import'}\t{_p}")
                for _m2 in _need:
                    print(f"        + open import {_m2}")
            for _a in _amb:
                print(f"   ⚑ refused\t{_p}\t`{_a}` has SEVERAL homes — import by hand")
        print(f"telescope-imports: {_n_need} module(s)"
              + ("" if _apply else "  (dry run)")
              + (f"; {_args}" if _args else ""))
        _sys.exit(0)
    if "--repair-telescopes" in _sys.argv:
        # ⚑ THE REPAIR HALF OF `--applied-args`, which could only ever REPORT.
        # Its own footer says "recover the parent's telescope with `--at <rev>`" —
        # a HAND edit, and the census names 33 sites across 17 modules, identical.
        _apply = "--apply" in _sys.argv
        if not _apply and "--dry-run" not in _sys.argv:
            print("⚑ state --apply or --dry-run: a mutating mode must not GUESS.")
            _sys.exit(2)
        plans, _ref = repair_telescopes(_args[0] if _args else None, apply=_apply)
        for _p, _d, _imports in plans:
            print(f"   {'restored' if _apply else 'would restore'} {_d}\t{_p}")
            for _m2 in _imports:
                print(f"        + open import {_m2}   (above the header)")
        # ⚑ REFUSALS ARE REPORTED, NOT SWALLOWED.  A repair that finds nothing and
        # a repair that declined 17 times must not render alike.
        for _m, _a, _why in _ref:
            print(f"   ⚑ refused  {_m}\t({_a})\t{_why}")
        print(f"repair-telescopes: {len(plans)} module(s)"
              + (f", {len(_ref)} refused" if _ref else "")
              + ("" if _apply else "  (dry run)")
              + (f"; {_args}" if _args else ""))
        if _apply and plans:
            print("   ⚑ the telescope is restored; a shard may STILL need its own "
                  "imports — the dissolved parent re-exported them.")
        _sys.exit(0)
    if "--stranded-residue" in _sys.argv:
        # ⚑ A CENSUS, NEVER A WRITER.  `split_lemmas.write_residue` says the
        # re-home-or-delete call must be "a decision, not a side effect", so this
        # mode makes it DECIDABLE and stops.  No --apply exists, deliberately.
        _files = stranded_residue(_args[0] if _args else None)
        print("-- a split's RESIDUE: re-homed / live-damage / unused --")
        _tot = {"re-homed": 0, "live-damage": 0, "unused": 0, "no-binders": 0}
        for _rp, _rows in _files:
            print(f"  {os.path.relpath(_rp, os.path.dirname(AG))}")
            for _nm, _v, _where in _rows:
                _tot[_v] = _tot.get(_v, 0) + 1
                if _v == "no-binders":
                    print("      no-binders   (not a telescope — a fixity or "
                          "pragma line; binds nothing to re-home)")
                    continue
                print(f"      {_v:<12} {_nm}")
                for _w in _where:
                    print(f"          {'bound in' if _v == 're-homed' else 'used by'}"
                          f" {_w}")
        print(f"stranded-residue: {len(_files)} file(s); "
              + ", ".join(f"{_k}={_v}" for _k, _v in _tot.items() if _v))
        if _tot.get("live-damage"):
            print("   ⚑ live-damage: a leaf USES a name the split dropped and "
                  "nothing binds — invisible to --applied-args, which reads only "
                  "APPLIED import arguments.")
        print("   ⚑ this mode does NOT re-home or delete: the writer's own "
              "instruction is that the call is a DECISION, not a side effect.")
        _sys.exit(0)
    if "--applied-args" in _sys.argv:
        rows = applied_imports(_args[0] if _args else None)
        # ⚑ THE SAME VERDICT JOIN AS `--late-imports`, AND FOR THE SAME REASON.
        # This mode makes a POSITIONAL claim (nothing binds this argument), and a
        # positional claim about source needs a semantic oracle.  Reporting rows
        # without the build's verdict is how that mode's first cut asserted a
        # header false for 13 of 18 rows.
        _verdict = {}
        try:
            import split_census as _sc
            for _rel, _v, _c in _sc.census_from_build(AG):
                _verdict[_rel[:-5].replace("/", ".") if _rel.endswith(".agda")
                         else _rel] = (_v, _c)
        except Exception as _e:
            print(f"   ⚠ build census unreadable ({_e}) — verdicts UNKNOWN, "
                  f"rows below are POSITIONAL CANDIDATES ONLY")
        print("-- `open import M x` where nothing binds `x` --")
        _clean = _unmeasured = 0
        for mod, ln, target, arg, _b in rows:
            v, _c = _verdict.get(mod, ("unmeasured", ""))
            if v == "clean":
                _clean += 1
            elif v == "unmeasured":
                _unmeasured += 1
            print(f"  {v:<11} {mod}:{ln}\n"
                  f"              open import {target} {arg}   ← `{arg}` unbound")
        # ⚑⚑ `unmeasured` IS NOT A VERDICT AND MUST NOT PRINT AS ONE.  A module
        # `make -k` never ATTEMPTED (it was blocked behind a failure) has no row
        # in the build census, and rendering that as `?` invites reading absence
        # as a weak `clean`.  It is the same distinction the census itself draws
        # between `stale` and `failing`: unmeasured, not passing.  A `clean` row
        # here IS noise worth seeing — it means the argument resolves through
        # something this scan does not model.
        print(f"{len(rows)} row(s): {_clean} on a module that COMPILES (likely "
              f"false positive),\n   {_unmeasured} on a module the build never "
              f"attempted (unmeasured, NOT passing), "
              f"{len(rows) - _clean - _unmeasured} on a measured failure")
        if rows:
            # ⚑ THE REMEDY IS A JUDGEMENT, NOT A REWRITE, so this mode reports and
            # never repairs.  The two measured instances wanted OPPOSITE fixes:
            # `Fin/Iterate` needed the applied import DELETED (its body never used
            # the target), the eight `Bridge` shards needed the parent's telescope
            # RESTORED.  A tool that picked one would have been wrong half the time.
            print("   ⚑ recover the parent's telescope with `--at <rev> <Mod>` — the "
                  "argument\n     is usually a parameter a decomposition dropped, "
                  "not a name to import.")
        _sys.exit(0)
    if "--late-imports" in _sys.argv:
        # ⚑ n of m, and the m is FILES SCANNED — the point of this census is a
        # SHRINKING population, which a bare list cannot express.
        rows = late_imports()
        if _args:
            rows = [r for r in rows
                    if any(r[0] == a or r[0].startswith(a + ".") for a in _args)]
        # ⚑⚑ EVERY ROW CARRIES THE BUILD'S VERDICT, BECAUSE THE POSITIONAL FACT DOES
        # NOT IMPLY THE COMPILE FACT AND I ASSERTED THAT IT DID.  The first cut of
        # this mode printed *"each of these supplies NOTHING to the use above it"* as
        # a header over 18 rows.  MEASURED 2026-08-17 by compiling all 15 modules:
        # **5 were clean, 8 failed on a DIFFERENT file, 2 on their own content** — so
        # the claim was false for at least 13 of 18, and the one instance it was
        # generalised from (`Algebra/Bijection.agda`, where hoisting six imports fixed
        # the build) was not representative.
        #
        # ⚑ SO THE VERDICT IS THE DELIVERABLE AND THE POSITION IS THE CANDIDATE.
        # Joining to `census_from_build` — a READ of the build's own per-module logs,
        # not a second build — makes a `clean` row visible as noise instead of
        # presented as a finding, which is what makes this mode self-falsifying rather
        # than self-confirming.  A row whose verdict is `dependency` is blocked
        # upstream and this import is not its problem.
        _verdict = {}
        try:
            import split_census as _sc
            for _rel, _v, _cited in _sc.census_from_build(AG):
                _verdict[_rel[:-5].replace("/", ".") if _rel.endswith(".agda")
                         else _rel] = (_v, _cited)
        except Exception as _e:                      # census absent is not a verdict
            print(f"   ⚠ build census unreadable ({_e}) — verdicts UNKNOWN, "
                  f"rows below are POSITIONAL CANDIDATES ONLY")
        for mod, ln, target, name, use in rows:
            _v, _cited = _verdict.get(mod, ("?", ""))
            print(f"[{_v:<10}] {mod}:{ln}\t-> {target}\tprovides {name}, "
                  f"first used at :{use}")
            if _v == "dependency" and _cited:
                print(f"             blocked upstream by {_cited}")
        _scanned = len(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True))
        _own = [r for r in rows if _verdict.get(r[0], ("?",))[0] == "own"]
        _cln = [r for r in rows if _verdict.get(r[0], ("?",))[0] == "clean"]
        print(f"late-imports: {len(rows)} import(s) below a use site in "
              f"{len({r[0] for r in rows})} of {_scanned} module(s)")
        if rows:
            print(f"   ⚑ {len(_own)} on a module failing on its OWN content — the "
                  f"only rows where this import can be the cause")
            print(f"   ⚑ {len(_cln)} on a module that COMPILES — position alone does "
                  f"not starve a use site, so these are noise, not findings")
            print("   ⚑ `agda_imports.py order` moves imports DOWN and cannot see "
                  "this class — a file in BOTH censuses has a real cycle")
        _sys.exit(0)
    if "--clause-audit" in _sys.argv:
        rows = clause_audit()
        if _args:
            rows = [r for r in rows
                    if any(r[0] == a or r[0].startswith(a + ".") for a in _args)]
        _want = ([v for v in ("NONEXPORT", "UNUSED", "UNKNOWN")
                  if "--" + v.lower() in _sys.argv]
                 or ["NONEXPORT", "UNUSED"])
        # ⚑ NONEXPORT FIRST AND ALWAYS SEPARATELY.  It is a LATENT BUILD FAILURE
        # (the name binds nothing; agda only warns, and the error lands at the
        # use site), where UNUSED is merely debt.  A single sorted list would
        # bury four build-breakers under hundreds of dead clause entries.
        for v in _want:
            hits = [r for r in rows if r[4] == v]
            if v == "NONEXPORT":
                print(f"── NONEXPORT — the target does not export this name.  Agda "
                      f"warns and binds NOTHING, so the")
                print(f"   failure surfaces at the USE site, elsewhere.  A latent "
                      f"build break, not debt.")
            elif v == "UNUSED":
                print(f"── UNUSED — exported, but this file never mentions it.  "
                      f"Dead clause entry; makes a")
                print(f"   clause look load-bearing when it is not.")
            else:
                print(f"── UNKNOWN — target outside the definition index.  A fact "
                      f"about the METHOD, never")
                print(f"   evidence of a missing export.")
            for m, ln, t, nm, _v in hits:
                print(f"   {m}:{ln}\t{t}\t{nm}")
            print(f"   {len(hits)} {v}")
            print()
        _scanned = len(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True))
        print(f"clause-audit: {len(rows)} clause name(s) in "
              f"{len({r[0] for r in rows})} of {_scanned} module(s)"
              + (f"; {_args}" if _args else ""))
        _sys.exit(1 if any(r[4] == "NONEXPORT" for r in rows) else 0)
    if "--reexports" in _sys.argv:
        # ⚑ n of m ALWAYS, and the m is FILES SCANNED — a bare list cannot
        # distinguish "no re-exports" from "no sources read", and this mode's
        # whole point is to make a shrinking population legible as paydown.
        rows = reexport_index()
        if _args:
            rows = [r for r in rows
                    if any(r[0] == a or r[0].startswith(a + ".")
                           or r[2] == a or r[2].startswith(a + ".") for a in _args)]
        _scanned = len(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True))
        if "--triage" in _sys.argv:
            # ⚑ TRIAGE RANKS BY WHAT PAYDOWN ACTUALLY COSTS, which is (kind ×
            # blast radius), not site count.  Both factors were already in the
            # tool — `reexport_index` knew the kind and threw it away, and
            # `importers_of` holds the radius — so "which of these 77 do I do
            # next" fell out of the toolkit and became a judgement in the turn.
            #
            # An `import … public` is retirable in place: bind the name at its
            # real home in each consumer, delete the `public`.  Cost scales with
            # EXTERNAL importers — the modules that reach a name through this
            # one and would unbind.  Zero external importers means the retirement
            # cannot break anything, which is the whole front of the queue.
            #
            # An `apply` is NOT that job and must not be ranked with it: the
            # applied instance's names have no other route in, so retiring it
            # rewrites use sites.  Listed separately, never merged into a total.
            _imp = [r for r in rows if r[4] == "import"]
            _app = [r for r in rows if r[4] == "apply"]
            _ext = {}
            for mod, ln, target, tail, _k in _imp:
                hits = importers_of(mod)
                _ext[(mod, ln)] = len([1 for s, _t in hits
                                       if not (s == mod or s.startswith(mod + "."))])
            print("── import … public — RETIRABLE IN PLACE, "
                  "ranked by external importers (cheapest first)")
            for mod, ln, target, tail, _k in sorted(
                    _imp, key=lambda r: (_ext[(r[0], r[1])], r[0])):
                print(f"{_ext[(mod, ln)]:4d}  {mod}:{ln}\t-> {target}\t{tail}")
            print()
            print("── open <applied module> … public — NOT the same job: the "
                  "instance's names have no other route in,")
            print("   so retiring rewrites every use site.  Separate queue, "
                  "never summed with the above.")
            for mod, ln, target, tail, _k in _app:
                print(f"      {mod}:{ln}\t-> {target}\t{tail}")
            _free = [k for k, v in _ext.items() if v == 0]
            print()
            print(f"triage: {len(_imp)} import-form ({len(_free)} with ZERO "
                  f"external importers — free to retire now), "
                  f"{len(_app)} application-form; {_scanned} module(s) scanned"
                  + (f"; {_args}" if _args else ""))
            _sys.exit(0)
        for mod, ln, target, tail, kind in rows:
            print(f"{mod}:{ln}\t-> {target}\t{tail}")
        # ⚑ ONLY THE IMPORT FORM HAS A MODULE PATH AS ITS TARGET.  An
        # application names a LOCAL module (`P0.Over`, `WithLemmas`), so testing
        # it against `import_index` reported 41 healthy rows as dangling — see
        # `reexport_index`'s note on the discarded kind.
        _dangling = [r for r in rows if r[4] == "import" and r[2] not in import_index()]
        print(f"re-exports: {len(rows)} site(s) in "
              f"{len({r[0] for r in rows})} of {_scanned} module(s)"
              + (f"; {_args}" if _args else ""))
        if _dangling:
            # a re-export whose TARGET has no module is already broken — this is
            # the `file-not-found` reservoir, named rather than predicted.
            print(f"   ⚑ {len(_dangling)} target(s) name no module in the tree:")
            for mod, ln, target, _t, _k in _dangling[:10]:
                print(f"      {mod}:{ln} -> {target}")
        _sys.exit(0)
    if "--importers" in _sys.argv:
        for pref in _args:
            hits = importers_of(pref)
            ext = [(s, t) for s, t in hits if not (
                s == pref or s.startswith(pref + "."))]
            for s, t in hits:
                mark = "  " if (s, t) in ext else "* "   # * = internal to subtree
                print(f"{mark}{s}\t-> {t}")
            print(f"{pref}: {len(hits)} edge(s) in, "
                  f"{len({s for s, _ in ext})} EXTERNAL importer(s), "
                  f"{len({s for s, _ in hits}) - len({s for s, _ in ext})} internal")
        _sys.exit(0)
    if "--closure" in _sys.argv:
        pref = None
        if "--prefix" in _sys.argv:
            i = _sys.argv.index("--prefix")
            pref = _sys.argv[i + 1]
            _args = [a for a in _args if a != pref]
        for mod in _args:
            cl = closure_of(mod, pref)
            for m in cl:
                print(m)
            print(f"{mod}: {len(cl)} module(s) in transitive closure"
                  + (f" under {pref}" if pref else ""))
        _sys.exit(0)
    if "--cycles" in _sys.argv:
        # ⚑ THE GRAPH, CYCLE-DETECTED — not a reachability probe per candidate. See
        # `cycles_with.__doc__` for why the three existing `_would_cycle` copies cannot
        # answer this: they sample the graph one edge at a time and cannot see a cycle
        # formed by a BATCH of edits, which is exactly what a tree-wide sweep produces.
        _cy = cycles_with()
        for _c in _cy:
            print("  cycle (%d): %s" % (len(_c), " → ".join(_c)))
        print(f"{len(_cy)} import cycle(s) over {len(import_index())} module(s)")
        _sys.exit(1 if _cy else 0)
    if "--cycle-cuts" in _sys.argv:
        _tot = 0
        _rs = cycle_cuts()
        _new = 0
        for _comp, _cuts, _how, _ne, _fresh in _rs:
            print("  SCC (%d module(s), %d internal edge(s)) — %d cut(s) [%s]"
                  % (len(_comp), _ne, len(_cuts), _how))
            for _a, _b in _cuts:
                # ⚑ THE PROVENANCE TAG IS THE ACTIONABILITY, NOT DECORATION. `NEW`
                # means the working tree added this edge — safe to cut. `pre-existing`
                # means the cycle is genuine design debt and cutting it DELETES CODE.
                _isn = (_a, _b) in _fresh
                _new += _isn
                print("      %s  ⟶  %s   [%s]"
                      % (_a, _b, "NEW since HEAD" if _isn else "⚑ pre-existing"))
            _tot += len(_cuts)
        print(f"{len(_rs)} SCC(s); {_tot} back-edge(s) to remove "
              f"({_new} NEW since HEAD, {_tot - _new} pre-existing)")
        _sys.exit(1 if _rs else 0)
    if "--cluster" in _sys.argv:
        for pref in _args:
            i, inb, out = cluster_edges(pref)
            n = len(modules_under(pref))
            ext = len({s for s, _t in importers_of(pref)
                       if not (s == pref or s.startswith(pref + "."))})
            print(f"{pref}: {n} module(s)")
            print(f"  internal edges : {i}")
            print(f"  inbound  edges : {inb}   (from {ext} external importer(s))")
            print(f"  outbound edges : {out}")
        _sys.exit(0)
    if "--trust" in _sys.argv:
        for pref in (_args or [None]):
            cen = trust_census(pref)
            n = cen.pop("_scanned")
            for mod, rec in sorted(cen.items()):
                bits = []
                if rec["postulates"]:
                    bits.append("postulate " + ",".join(rec["postulates"]))
                if rec["holes"]:
                    bits.append(f"{rec['holes']} hole(s)")
                for pn, pa in rec["pragmas"]:
                    bits.append(f"{{-# {pn} {pa} #-}}".strip())
                if "--safe" not in rec["options"]:
                    bits.append("NOT --safe (" + " ".join(rec["options"]) + ")")
                elif rec["extra_options"]:
                    bits.append("--safe, but WIDENED options: "
                                + " ".join(rec["extra_options"]))
                print(f"{mod}\n      " + "\n      ".join(bits))
            print(f"{pref or 'agda/Substrate'}: {n} module(s) scanned, "
                  f"{len(cen)} with a finding "
                  f"(postulate / non-OPTIONS pragma / hole / not --safe)")
        _sys.exit(0)
    if "--flags" in _sys.argv:
        # ⒢′ — the flag-reflection census.  Reports `n of m` because a bare list
        # cannot distinguish "no module fails to reflect" from "no file read".
        for pref in (_args or [None]):
            cen = flag_census(pref)
            n = cen.pop("_scanned")
            gl = cen.pop("_global")
            print("GLOBAL flag set (read from its authorities):")
            for f, origin in sorted(gl.items()):
                print(f"      {f:<28} <- {origin}")
            _fmk = os.path.join(_ROOT, "agda", "Flat.mk")
            if os.path.exists(_fmk):
                _m = re.search(r"^AGDA_FLAGS\s*\?=\s*(.*)$",
                               open(_fmk, errors="replace").read(), re.M)
                _gen = cmdline_flags()
                if _m and _m.group(1).split() != _gen:
                    print(f"      ⚑ DRIFT: Flat.mk says {_m.group(1).split()}, "
                          f"generator says {_gen} — regenerate")
            # ⚑ GROUPED, HEAD-PLUS-`… and N more`, AND BY DIRECTORY — the shape
            # `sppf_decode.undecodable_report` argued for and measured: a flat list
            # of ~1800 module paths is a wall, "these N sit under these subtrees,
            # all missing the same flag" is a repair plan.  The count is NEVER
            # truncated; only the listing is, and it says so.
            by_missing = collections.defaultdict(list)
            for mod, rec in sorted(cen.items()):
                by_missing[" ".join(rec["missing"])].append(mod)
            nopragma = sorted(m for m, r in cen.items() if not r["pragma"])
            for k, mods in sorted(by_missing.items(), key=lambda kv: -len(kv[1])):
                more = ("" if len(mods) <= 12
                        else ", … and %d more" % (len(mods) - 12))
                print(f"\n  MISSING {k or '(nothing)'} — {len(mods)} module(s)")
                print("      " + ", ".join(mods[:12]) + more)
                dirs = collections.Counter(m.rsplit(".", 1)[0] for m in mods)
                print("      by package (%d): %s" % (len(dirs), ", ".join(
                    "%s=%d" % kv for kv in dirs.most_common(8))))
            if nopragma:
                print(f"\n  ⚑ {len(nopragma)} module(s) carry NO "
                      "{-# OPTIONS #-} pragma at all: "
                      + ", ".join(nopragma[:12])
                      + ("" if len(nopragma) <= 12
                         else ", … and %d more" % (len(nopragma) - 12)))
            print(f"\n{pref or 'agda/Substrate'}: {len(cen)} of {n} module(s) "
                  f"do NOT reflect the full global flag set "
                  f"({len(gl)} global flag(s))")
            if not cen:
                print("      every scanned module names every global flag "
                      "(a fact about THIS scan, scoped to the prefix given)")
        _sys.exit(0)
    if "--consumers" in _sys.argv or "--depends" in _sys.argv:
        _depth = 3
        if "--depth" in _sys.argv:
            _depth = int(_sys.argv[_sys.argv.index("--depth") + 1])
            _args = [a for a in _args if a != str(_depth)]
        _cons = "--consumers" in _sys.argv
        for pref in _args:
            pkg, mod = (consumer_profile(pref, _depth) if _cons
                        else dependency_profile(pref, _depth))
            head = "CONSUMED BY" if _cons else "DEPENDS ON"
            print(f"=== {pref}: {head} — by package (depth {_depth}) ===")
            for k, v in pkg:
                print(f"{v:5d}  {k}")
            print(f"=== {pref}: {head} — by module ===")
            for k, v in mod:
                print(f"{v:5d}  {k}")
            print(f"{pref}: {len(pkg)} package(s), {len(mod)} module(s)")
        _sys.exit(0)
    if "--under" in _sys.argv:
        for pref in _args:
            ms = modules_under(pref)
            for m in ms:
                print(m)
            print(f"{pref}: {len(ms)} module(s)")
        _sys.exit(0)
    if "--dup-variables" in _sys.argv:
        # generalizable variables declared in MORE THAN ONE module — invisible to
        # `def_index` (which does not carry them) and therefore to every other
        # census here. Latent until two declaring modules meet in one scope, then
        # [AmbiguousName]/[ClashingDefinition] one compile at a time.
        _pfx = next((a for a in _args if a.startswith("Substrate")), None)
        _rows = variable_declarations(_pfx)
        for _n, _mods in _rows[:40]:
            print(f"== {_n}   ({len(_mods)} declaring module(s))")
            for _m in _mods[:8]:
                print(f"     {_m}")
            if len(_mods) > 8:
                print(f"     … and {len(_mods)-8} more")
        if len(_rows) > 40:
            print(f"\n… and {len(_rows)-40} more duplicated name(s)")
        print(f"\n{len(_rows)} name(s) declared in >1 module; "
              f"{sum(len(m) for _n, m in _rows)} declaration(s) total")
        _sys.exit(0)
    if "--flat-variable" in _sys.argv:
        # a `variable` block the horizontal split flattened onto one line —
        # unparseable by construction, and every instance fails identically.
        _pfx = next((a for a in _args if a.startswith("Substrate")), None)
        _rows = flat_variable_blocks(_pfx)
        for _p, _n, _txt in _rows:
            print(f"{_p}:{_n}")
            print(f"     {_txt[:110]}")
        if "--repair" in _sys.argv:
            _do = "--apply" in _sys.argv
            _plan = repair_flat_variables(_pfx, apply=False)
            for _p, _n, _gs in _plan:
                print(f"\n{_p}:{_n} ->")
                for _g in _gs:
                    print(f"     {_g}")
            if _do and _plan:
                import edit_snapshot
                edit_snapshot.guard("repair_flat_variables",
                                    [r[0] for r in _plan])
                repair_flat_variables(_pfx, apply=True)
                print(f"\napplied to {len(_plan)} file(s)")
            else:
                print(f"\n{len(_plan)} file(s) planned — pass --apply to execute")
            _sys.exit(0)
        print(f"\n{len(_rows)} flattened `variable` block(s) — each is a "
              f"[ParseError] at the second colon, not a scope problem")
        _sys.exit(0)
    if "--orphans" in _sys.argv:
        # tokens a body USES that nothing defines — dropped-alias debris from the
        # ban sweep.  ⚑ The count is a FLOOR: only non-ASCII tokens are judged,
        # because a rename-to-alias exists to give a name a distinct typographic
        # spelling and every measured instance (`ℕ≤`, `+F`, `∘V`) has one.  A
        # pure-ASCII dropped alias is invisible here and is NOT reported clean.
        _pfx = None
        for _a in _args:
            if _a.startswith("Substrate"):
                _pfx = _a
        _rows = orphan_names(_pfx)
        print("⚑⚑ THIS MODE DOES NOT WORK AND ITS ROWS ARE NOT ACTIONABLE.")
        print("   Measured tree-wide: 115 names / 416 sites / ZERO true findings.")
        print("   Qualified names (`S₃.Carrier`), module-parameter binders (`W₁`)")
        print("   and local binders (`b₁`) are all indistinguishable from a dropped")
        print("   alias without resolving scope — i.e. without being the compiler.")
        print("   The working instrument for this class is `split_pipeline --why`,")
        print("   whose [NotInScope] names the token. Retained as a negative result")
        print("   so the tightening loop is not re-derived; see orphan_names.__doc__.\n")
        for _t, _sites in _rows:
            print(f"== {_t}   ({len(_sites)} site(s), NO DEFINER ANYWHERE)")
            for _p, _n in _sites[:12]:
                print(f"     {_p}:{_n}")
            if len(_sites) > 12:
                print(f"     … and {len(_sites)-12} more")
        print(f"\n{len(_rows)} orphan name(s), "
              f"{sum(len(s) for _t, s in _rows)} site(s) — a FLOOR "
              f"(non-ASCII tokens only; a pure-ASCII dropped alias is UNEXAMINED)")
        _sys.exit(0)
    if "--alias-trace" in _sys.argv:
        # ⚑ INSTRUMENT THE PLAN, not the regex. Four cause hypotheses for
        # ⓉQUALFIX-CAUSE came from READING `qualified_repair` and all four were
        # wrong; `--alias-probe` then eliminated the entire regex class in one
        # command. What no probe reached is the CONTROL FLOW — which file the loop
        # sees, what `used` holds, whether the write guard fires. This prints that.
        _i = _sys.argv.index("--alias-trace")
        _tgt = _sys.argv[_i + 1] if len(_sys.argv) > _i + 2 else None
        _f = _sys.argv[_i + 2] if len(_sys.argv) > _i + 2 else None
        if not _tgt or not _f:
            print("--alias-trace <target> <file.agda>", file=_sys.stderr)
            _sys.exit(2)
        _src = open(_f).read()
        _lines = _src.split("\n")
        _rx = re.compile(r"^\s*import\s+" + re.escape(_tgt) + r"\s+as\s+(\S+)\s*$")
        _alias = _impline = None
        for _n, _l in enumerate(_lines):
            _m = _rx.match(_l)
            if _m:
                _alias, _impline = _m.group(1), _n
                break
        print(f"import line : {_impline}  alias={_alias!r}")
        if _alias is None:
            print("⚑ NO IMPORT MATCHED — the loop `continue`s and writes nothing.")
            _sys.exit(0)
        _masked = agda_lex.mask_comments("\n".join(_lines))
        _used = sorted(set(_alias_refs(_alias, _masked)))
        print(f"used        : {_used}")
        _idx = def_index()
        for _nm in _used:
            _own = sorted(_idx.get(_nm, ()))
            _loc = [o for o in _own if _in_subtree(o, _tgt)]
            _verdict = ("resolved->" + _loc[0]) if len(_loc) == 1 else (
                "resolved->" + _own[0] if not _loc and len(_own) == 1
                else f"UNRESOLVED ({len(_loc) or len(_own)} candidates)")
            print(f"  {_nm:<12} {_verdict}")
        _unres = [n for n in _used
                  if len([o for o in sorted(_idx.get(n, ())) if _in_subtree(o, _tgt)]) != 1
                  and not (not [o for o in sorted(_idx.get(n, ())) if _in_subtree(o, _tgt)]
                           and len(sorted(_idx.get(n, ()))) == 1)]
        print(f"write guard : used={bool(_used)} unresolved={_unres} "
              f"-> {'WRITES' if _used and not _unres else 'SKIPS'}")
        # ⚑ AND THEN RUN THE REAL FUNCTION ON THIS PATH. Everything above
        # re-derives the plan; only this exercises `qualified_repair` itself, which
        # is where four failed hypotheses said the defect must be. Re-deriving a
        # tool's logic to diagnose it is how you confirm your model instead of the
        # code — the trap this whole thread has been walking into.
        if "--run" in _sys.argv:
            _before = open(_f).read()
            qualified_repair(_tgt, apply=True, paths=[_f])
            _after = open(_f).read()
            print("\n--- REAL qualified_repair on this path ---")
            for _bl, _al2 in zip(_before.split("\n"), _after.split("\n")):
                if _bl != _al2:
                    print(f"  -{_bl}\n  +{_al2}")
            if _before == _after:
                print("  (no change written)")
        _sys.exit(0)
    if "--alias-probe" in _sys.argv:
        # ⚑ THE DIAGNOSTIC ⓉQUALFIX-CAUSE NEEDED AND DID NOT HAVE. Three cause
        # hypotheses were tried by READING the code and all three were wrong. This
        # prints what the shared pattern actually captures on a line, which is the
        # one question none of the guesses answered.
        _i = _sys.argv.index("--alias-probe")
        _al = _sys.argv[_i + 1] if len(_sys.argv) > _i + 2 else "F2"
        _ln = _sys.argv[_i + 2] if len(_sys.argv) > _i + 2 else ""
        print(f"alias   : {_al}")
        print(f"pattern : {_alias_pattern(_al)}")
        print(f"line    : {_ln!r}")
        print(f"captures: {_alias_refs(_al, _ln)}")
        print(f"rewrite : {re.sub(_alias_pattern(_al), r'\1', _ln)!r}")
        _sys.exit(0)
    if "--double-route" in _sys.argv:
        # modules reaching one name by TWO routes — a generic re-export AND a leaf.
        # ⚑ Neither route is malformed, so `--reexports` cannot see it and each file
        # compiles alone; the collision exists only in the combination. Found by
        # compiling three times before this mode existed.
        _i = _sys.argv.index("--double-route")
        _gen = _sys.argv[_i + 1] if len(_sys.argv) > _i + 2 else None
        _leaf = _sys.argv[_i + 2] if len(_sys.argv) > _i + 2 else None
        if not _gen or not _leaf:
            print("--double-route <generic-module> <leaf-prefix>", file=_sys.stderr)
            _sys.exit(2)
        _rows = double_route_names(_gen, _leaf)
        for _m, _ls in _rows:
            print(f"== {_m}")
            for _l in _ls:
                print(f"     also opens  {_l}")
        print(f"\n{len(_rows)} module(s) import BOTH {_gen} and a leaf under "
              f"{_leaf} — each is a potential [AmbiguousName] on any name the "
              f"generic re-exports.  ⚑ A row is a CANDIDATE, not a defect: the "
              f"collision fires only if the module USES a doubly-provided name.")
        _sys.exit(0)
    if "--qualified-repair" in _sys.argv:
        # strip `import <target> as Q` and its `Q.name` use sites TOGETHER, each
        # name resolved at ITS OWN home.  ⚑ PLAN unless --apply: a mutating tool
        # must not guess, and this one edits bodies rather than just imports.
        _i = _sys.argv.index("--qualified-repair")
        _tgt = _sys.argv[_i + 1] if len(_sys.argv) > _i + 1 else None
        if not _tgt or _tgt.startswith("-"):
            print("--qualified-repair needs a target module", file=_sys.stderr)
            _sys.exit(2)
        _do = "--apply" in _sys.argv
        if _do:
            import edit_snapshot
        _plan = qualified_repair(_tgt, apply=False)
        _blocked = [r for r in _plan if r[2]]
        for _p, _hm, _un in _plan:
            print(f"== {_p}")
            for _nm, _h in _hm:
                print(f"     {_nm:<20} -> {_h}")
            for _nm, _owners in _un:
                print(f"   ⚠ {_nm:<20} -> {len(_owners)} home(s) — REFUSED: "
                      f"{_owners if _owners else 'no home in the index'}")
        if _blocked:
            print(f"\n⚑ {len(_blocked)} file(s) REFUSED — a name with no home or "
                  f"several. A wrong import compiles until it does not; resolve "
                  f"the spelling at source, then re-run.")
        if _do:
            _ok = [r for r in _plan if not r[2]]
            if _ok:
                edit_snapshot.guard(f"qualified_repair {_tgt}", [r[0] for r in _ok])
                qualified_repair(_tgt, apply=True)
            print(f"\napplied to {len(_ok)} file(s); {len(_blocked)} refused")
        else:
            print(f"\n{len(_plan)} file(s) planned, {len(_blocked)} refused "
                  f"— pass --apply to execute")
        _sys.exit(0)
    if "--collide" in _sys.argv:
        # ⚑ Ⓠ9 — the repo is ONE NAMESPACE, so a shared spelling is a misnaming
        # regardless of how many consumers currently co-import the definers.
        _cn = _sys.argv[_sys.argv.index("--collide") + 1]
        _c = collide(_cn)
        _tot = len(_c["field"]) + len(_c["toplevel"])
        print(f"=== {_cn}: {_tot} provider(s) ===")
        print(f"\n-- RECORD FIELD ({len(_c['field'])}) — legitimately generic: the "
              f"structure's own operation, reached through its record.")
        for m in _c["field"]:
            print(f"   {m}")
        print(f"\n-- TOP-LEVEL ({len(_c['toplevel'])}) — a concrete carrier that "
              f"BORROWED the spelling. Rename-at-source applies to these.")
        for m in _c["toplevel"]:
            print(f"   {m}")
        print(f"\n⚑ {len(_c['toplevel'])} rename candidate(s). A collision is a "
              f"misnaming in a single namespace; the number of consumers that trip "
              f"over it today is a fact about the IMPORT GRAPH, not the names.")
        _sys.exit(0)
    if "--qualified" in _sys.argv:
        # `import M as Q` on a Substrate module — banned by the import ban, and the
        # form BOTH other censuses are structurally blind to (they read `open
        # import`).  Split by whether the TARGET still exists, because
        # banned-but-working and banned-AND-dangling are different urgencies.
        # ⚑ THE PATH ARGUMENT WAS ACCEPTED AND IGNORED. `qualified_aliases` takes
        # `paths=None`, and this call passed nothing — so `--qualified <dir>`
        # silently reported the WHOLE TREE. Measured twice today: asked about a
        # 22-file leaf directory it answered 859, and asked about a 272-file
        # cluster it answered 857, both the tree-wide figure. A scoped question
        # answered at tree scope is a census reporting the METHOD as the SUBSTRATE
        # — and it reads as a plausible number, so nothing flags it.
        # The dispatch branch is the half that gets forgotten; third instance today.
        # ⚑ AND A DIRECTORY MUST BE EXPANDED, NOT PASSED THROUGH. `qualified_aliases`
        # iterates `paths` as FILE paths and `open(<dir>)` raises, swallowed by its
        # bare `except: continue` — so my first fix turned "reports the whole tree"
        # into "reports ZERO", which is worse: a false zero gets banked while a
        # wrong-looking large number gets questioned. Caught only because 0 for
        # `agda/Substrate/Algebra` contradicted a qualified import I had read with
        # my own eyes minutes earlier.
        _qargs = [a for a in _sys.argv[1:] if not a.startswith("--")]
        _qpaths = None
        if _qargs:
            _qpaths = []
            for _a in _qargs:
                _qpaths.extend(agda_lex.agda_files(_a) if os.path.isdir(_a)
                               else [_a])
        _rows = qualified_aliases(_qpaths)
        _broken = [r for r in _rows if not r[4]]
        _live = [r for r in _rows if r[4]]
        # ⚑ --summary FOR THE THIRD TIME IN THIS TOOL, and the third time the
        # per-row form was written first and measured too large (106 KB here).
        # The live population is ban DEBT — a per-target count is what sizes a
        # paydown; the per-row listing is only wanted for the target being repaired.
        if "--summary" in _sys.argv:
            _bt = collections.Counter(m for _p, _n, m, _a, _e in _broken)
            _lt = collections.Counter(m for _p, _n, m, _a, _e in _live)
            print("=== BUILD-BREAKING: qualified alias, target gone ===")
            for _m, _c in _bt.most_common():
                print(f"{_c:5d}  {_m}")
            print("\n=== BAN DEBT: qualified alias, target live (top 20 targets) ===")
            for _m, _c in _lt.most_common(20):
                print(f"{_c:5d}  {_m}")
            if len(_lt) > 20:
                print(f"       … and {len(_lt)-20} more target(s)")
            print(f"\n{len(_rows)} qualified import(s): {len(_broken)} breaking over "
                  f"{len(_bt)} dead target(s), {len(_live)} debt over {len(_lt)} live "
                  f"target(s).  ⚑ Each has `<alias>.name` USE SITES that must change "
                  f"with the import.")
            _sys.exit(0)
        if _broken:
            print("=== QUALIFIED alias on a target that NO LONGER EXISTS "
                  "(build-breaking) ===")
            for _p, _n, _mod, _al, _ in _broken:
                print(f"   {_p}:{_n}  import {_mod} as {_al}")
        if _live:
            print("\n=== QUALIFIED alias on a LIVE target (ban debt, still builds) ===")
            for _p, _n, _mod, _al, _ in _live:
                print(f"   {_p}:{_n}  import {_mod} as {_al}")
        print(f"\n{len(_rows)} qualified Substrate import(s): "
              f"{len(_broken)} on a MISSING target, {len(_live)} on a live one. "
              f"⚑ Each also has `<alias>.name` USE SITES that must change with it "
              f"— the import alone is not the repair.")
        _sys.exit(0)
    if "--dangling" in _sys.argv:
        # every `open import M` whose M has no source file — the dissolved-parent
        # census.  A decomposition that deletes the parent and does not rewire its
        # consumers leaves exactly this, and agda surfaces it ONE BUILD FAILURE AT
        # A TIME.  Four were found by hand in one session before this mode existed.
        # ⚑ SUMMARY IS THE DEFAULT HERE, unlike --unused-imports, and the first run
        # is why: `Foundation.Empty` alone has 272 importers, so the per-importer
        # form is 32 KB before it says anything.  The question a dissolved-parent
        # census answers is WHICH PARENTS and HOW BIG, and the importer list is
        # only wanted for the one being repaired — hence `--target <Mod>`.
        _rows, _unjudged = dangling_imports()
        _only = None
        if "--target" in _sys.argv:
            _i = _sys.argv.index("--target")
            _only = _sys.argv[_i + 1] if len(_sys.argv) > _i + 1 else None
        if _only:
            _rows = [(t, ms) for t, ms in _rows if t == _only]
            if not _rows:
                print(f"--dangling --target {_only}: not a dangling target "
                      f"(it may exist, or nothing may import it)")
                _sys.exit(0)
            for _t, _ms in _rows:
                print(f"== {_t}   ({len(_ms)} importer(s), NO SOURCE FILE)")
                for _m in _ms:
                    print(f"     {_m}")
        else:
            print("=== dangling targets — an `open import` with no source file ===")
            for _t, _ms in _rows:
                print(f"{len(_ms):5d}  {_t}")
            print("\n(--target <Mod> lists the importers of one target)")
        # ⚑ UNJUDGED IS PRINTED, NEVER FOLDED IN.  A non-Substrate target (stdlib,
        # Agda.Primitive) resolves from the library path and has no file here
        # either; calling that dangling would report a fact about THIS corpus as a
        # fact about the module.  "I cannot see it" is not "it is not there".
        if _unjudged and "--verbose" in _sys.argv:
            print(f"\n{len(_unjudged)} non-Substrate target(s) UNJUDGED "
                  f"(resolved from the library path, not this corpus):")
            for _t, _c in _unjudged[:20]:
                print(f"   {_c:4d}  {_t}")
        print(f"\n{len(_rows)} dangling target(s), "
              f"{sum(len(m) for _t, m in _rows)} broken import(s); "
              f"{len(_unjudged)} non-Substrate target(s) unjudged "
              f"(--verbose to list)")
        _sys.exit(0)
    if "--unused-imports" in _sys.argv:
        # imports a module names but does not reference — the CENSUS half of
        # `prune_imports`, which is a WRITER and a pipeline stage.
        #
        # ⚑ WHY THIS IS A READ MODE ON A DIFFERENT TOOL RATHER THAN A PRUNE FLAG.
        # `prune_imports` refuses to run standalone ("a PIPELINE STAGE, not a
        # standalone tool") because repairing with it strands the next stage.
        # But the QUESTION it answers is one every consumer wants and none could
        # ask: two independent surveys of the F₂ arc this session both named this
        # exact missing mode, and both had to estimate from two hand-read
        # witnesses instead.
        #
        # ⚑ THE COUNT IS A FLOOR, NOT A TOTAL.  The underlying predicate is
        # KEEP-biased by design (a false drop breaks the build), so the census
        # inherits that bias and under-reports.  Silence about an import means
        # "no evidence", never "used".
        # ⚑ A MODULE PREFIX IS NOT A PATH, and treating it as one silently widened
        # the first tree-scale run to the WHOLE CORPUS (607 KB of output for a
        # question asked about one subtree).  `agda_lex.agda_files` takes a
        # DIRECTORY; a dotted prefix has to be resolved through the index first.
        _paths = []
        for a in _args:
            if a.endswith(".agda"):
                _paths.append(a)
            elif _o.path.isdir(a):
                _paths.extend(agda_lex.agda_files(a))
            else:
                # ⚑ `module_path` is path→MODULE; the inverse is `module_file`.
                # Calling the forward map on a dotted name returned something
                # unusable for every module, which the refusal below caught.
                _mods = modules_under(a)
                _hit = 0
                for _m in _mods:
                    _fp = agda_lex.module_file(_m, AG)
                    if _fp and _o.path.isfile(_fp):
                        _paths.append(_fp)
                        _hit += 1
                # ⚑⚑ A PREFIX THAT RESOLVES TO NOTHING MUST REFUSE, NEVER WIDEN.
                # The first cut fell back to the whole corpus when resolution
                # produced no paths — so `--unused-imports <one subtree>` silently
                # censused all 3487 modules and printed a total that LOOKED like an
                # answer to the narrow question.  Two runs at different prefixes
                # returned byte-identical output; only that coincidence exposed it.
                # A scoping bug that widens is strictly worse than one that errors:
                # the wrong number is indistinguishable from the right one.
                if not _hit:
                    print(f"--unused-imports: '{a}' resolved to {len(_mods)} module(s) "
                          f"but 0 readable file(s).", file=_sys.stderr)
                    print("  a prefix that resolves to nothing is REFUSED, not widened "
                          "to the corpus — pass a directory or a .agda path.",
                          file=_sys.stderr)
                    _sys.exit(2)
        if not _args:
            _paths = agda_lex.agda_files(AG)
        _rows, _barrels, _unreadable = unused_imports(_paths)
        # ⚑ --summary EXISTS BECAUSE THE DETAIL FORM DOES NOT SCALE, and the
        # scale is the question: "how much of this arrow is preamble" is a
        # per-TARGET aggregate, not a per-line listing.  Emitting 607 KB and
        # leaving the reader to total it by eye is the output-manipulation the
        # standing rule forbids — the aggregation belongs in the tool.
        _summary = "--summary" in _sys.argv
        _tot = 0
        if _summary:
            _by_target = collections.Counter()
            for _p, _ds in _rows:
                for _ln, _m in _ds:
                    _by_target[_m] += 1
                    _tot += 1
            print("=== unused imports BY TARGET (which module is named and not used) ===")
            for _m, _c in _by_target.most_common(40):
                print(f"{_c:5d}  {_m}")
            if len(_by_target) > 40:
                print(f"       … and {len(_by_target)-40} more target(s)")
            print("\n=== the heaviest SOURCES (modules carrying the most dead imports) ===")
            for _p, _ds in _rows[:20]:
                print(f"{len(_ds):5d}  {_p}")
            if len(_rows) > 20:
                print(f"       … and {len(_rows)-20} more source module(s)")
        else:
            for _p, _ds in _rows:
                print(f"== {_p}  ({len(_ds)} unused)")
                for _ln, _m in _ds:
                    print(f"   {_ln:5d}  {_m}")
                _tot += len(_ds)
        # ⚑ BOTH NON-RESULTS ARE REPORTED.  A barrel is REFUSED (liveness-by-use
        # cannot judge a module with no body) and an unparseable file is NOT
        # EXAMINED; collapsing either into the clean majority would make this
        # instrument report its own blind spots as good news.
        if _barrels:
            print(f"\n{len(_barrels)} pure aggregation barrel(s) REFUSED "
                  f"(no body ⇒ liveness-by-use cannot judge):")
            for _p in _barrels[:20]:
                print(f"   · {_p}")
            if len(_barrels) > 20:
                print(f"   … and {len(_barrels)-20} more")
        if _unreadable:
            print(f"\n{len(_unreadable)} file(s) NOT EXAMINED (parse failure) — "
                  f"these are unknown, NOT clean:")
            for _p in _unreadable[:20]:
                print(f"   · {_p}")
            if len(_unreadable) > 20:
                print(f"   … and {len(_unreadable)-20} more")
        print(f"\n{_tot} unused import(s) in {len(_rows)} of {len(_paths)} module(s) "
              f"— a FLOOR (the predicate is keep-biased); "
              f"{len(_barrels)} barrel(s) refused, {len(_unreadable)} unexamined")
        _sys.exit(0)
    if "--between" in _sys.argv:
        # every import edge FROM one subtree INTO another — the DIRECTION question.
        #
        # ⚑ THE ABSENCE OF THIS MODE READ AS AN ANSWER.  `--consumers`/`--depends`
        # aggregate by package, so "the tower leans on Algebra.F2" came back as a
        # single number (167) with no way to see WHICH tower modules or through
        # WHICH F2 modules — the only form in which a re-derivation can be planned.
        # Asked without the mode, the question fell through to `--importers`, which
        # answered a DIFFERENT question (every importer tree-wide, 35.9 KB) and
        # answered it convincingly.  Same shape as the `--calls emit` census that
        # missed `_emit_one`: a fact about the METHOD reported as a fact about the
        # SUBSTRATE.
        #
        # ⚑ TWO PREFIXES, AND THE ORDER IS THE QUESTION.  `A B` and `B A` are
        # different measurements; running both is how an inversion is MEASURED
        # rather than asserted.  Refuses on anything but exactly two prefixes,
        # because a one-prefix call would silently become a `--depends`.
        if len(_args) != 2:
            print("--between needs exactly two prefixes: <src> <dst>", file=_sys.stderr)
            print("  (order matters: `A B` counts A→B, `B A` counts B→A)", file=_sys.stderr)
            _sys.exit(2)
        _src, _dst = _args
        _edges, _by_dst, _by_src = edges_between(_src, _dst)
        print(f"=== {_src} → {_dst}: edges INTO the destination, by target ===")
        for k, v in _by_dst:
            print(f"{v:5d}  {k}")
        print(f"=== {_src} → {_dst}: edges OUT, by source module ===")
        for k, v in _by_src:
            print(f"{v:5d}  {k}")
        print(f"{_src} → {_dst}: {len(_edges)} edge(s), "
              f"{len(_by_src)} source module(s), {len(_by_dst)} target module(s)")
        _sys.exit(0)
    if "--provides" in _sys.argv:
        # which names does this MODULE define?  (the inverse question)
        #
        # ⚑⚑ A FILE PATH USED TO RETURN A CONFIDENT `0 name(s)`, AND THAT IS THE WORST
        # SHAPE A WRONG ANSWER CAN TAKE.  `provides()` is a set-membership test over
        # dotted MODULE names, so a path matched nothing and reported empty — no error,
        # no warning, indistinguishable from a module that genuinely defines nothing:
        #
        #     --provides agda/Substrate/Foundation/Fin/Literals.agda   ->   0 name(s)
        #     --provides Substrate.Foundation.Fin.Literals             ->  33 name(s)
        #
        # Same tool, same 2 KB file, opposite answers.  MEASURED 2026-08-18 by a peer
        # session, which ran it four times, read four clean zeroes as "these modules are
        # empty", and used that to RETRACT a correct hole-census reading — `--holes` had
        # said 33 and was right.  A broken measurement was used to correct a working one.
        #
        # ⚑ AND THE ZERO IS WHY THIS OUTRANKS THE OTHER INDEX BUGS.  Counting `private`
        # and `variable` as names INFLATES a count, which reads as noise; this ZEROES it,
        # and a zero is what a census ACTS on — a definer-count of 0 is what makes a
        # rename look unambiguous to a write path.
        #
        # ⚑ RESOLVED THROUGH `agda_lex.module_path`, NOT A LOCAL SPLIT.  It already owns
        # path -> dotted name (`module_file` is its inverse), it is pure, and a second
        # spelling here is the shared-name-not-shared-authority shape this repo censuses.
        _unknown = []
        for mod in _args:
            want = mod
            if mod.endswith(agda_lex.SUFFIX) or os.sep in mod or "/" in mod:
                # ⚑ `agda_root_from` RETURNS None RATHER THAN GUESSING, and the fallback
                # keeps that honest: an unlocatable root leaves the operand untouched, so
                # it falls through to the refusal below instead of being silently
                # re-spelled against a root that may not be this tree's.
                _root = agda_lex.agda_root_from(os.path.abspath(mod))
                if _root:
                    want = agda_lex.module_path(mod, _root)
            names = sorted(provides(want))
            # ⚑ AN OPERAND THAT NAMES NOTHING IS A REFUSAL, NEVER AN EMPTY LISTING.
            # "found nothing" and "could not look here" must not render alike — that
            # conflation IS this bug, and repeating it one line down would be the fix
            # re-introducing the defect it repairs.
            if not names and want not in def_index_modules():
                _unknown.append((mod, want))
                continue
            for n in names:
                print(n)
            print(f"{want}: {len(names)} name(s)")
        if _unknown:
            for mod, want in _unknown:
                extra = "" if mod == want else f" (read as `{want}`)"
                print(f"⚑ NOT A MODULE IN THE INDEX: {mod}{extra}", file=_sys.stderr)
            print(f"⚑ {len(_unknown)} operand(s) named no module — a fact about the "
                  f"QUERY, not about the tree.\n"
                  f"  Pass a dotted module name (Substrate.Foo.Bar) or a path under "
                  f"the agda root.", file=_sys.stderr)
            _sys.exit(2)
        _sys.exit(0)
    if "--prose" in _sys.argv:
        # ⚑ THE MODE SIX RESEARCH AGENTS ASKED FOR, EACH INDEPENDENTLY. Every one
        # reported the same gap in the same words: `--grep` matches definition
        # NAMES, so anything stated in a comment is unreachable, and they fell
        # back to raw grep (flagging it) or missed the fact entirely.
        #
        # ⚑ AND THE SHARPEST WITNESS IS THIS REPO'S OWN HISTORY. `Axes/Opposite.agda`'s
        # header preserves the user's earlier *"the answer to that is in the witness
        # tower"* — the SAME question a later agent was dispatched to answer, with the
        # answer already written down, invisible to every search mode it had. The
        # prose in this tree is not decoration: it is where the measured findings,
        # the retracted claims and the ⚑ incident notes live.
        #
        # ⚑ IT READS EXACTLY WHAT `def_index` THROWS AWAY. That walk skips any line
        # whose strip starts with `--` (line 29) — necessarily, since it indexes
        # definitions. This mode is that discarded half, so the two together cover
        # the file rather than leaving a band nothing reads.
        #
        # Reports MODULE + line + the matching comment line, because a hit without
        # its module cannot be followed up, and a count without witnesses is the
        # shape this toolkit exists to refuse.
        _i = _sys.argv.index("--prose")
        _pat = _sys.argv[_i + 1] if len(_sys.argv) > _i + 1 else None
        if not _pat:
            print("--prose needs a regex: agda_defs.py --prose <regex> [<Prefix>]")
            _sys.exit(2)
        _pfx = None
        for _a in _sys.argv[_i + 2:]:
            if not _a.startswith("-"):
                _pfx = _a
                break
        try:
            _rx = re.compile(_pat, re.IGNORECASE)
        except re.error as _e:
            print(f"--prose: bad regex {_pat!r}: {_e}")
            _sys.exit(2)
        _hits = 0
        _files = 0
        for _p in sorted(glob.glob(f"{AG}/Substrate/**/*.agda", recursive=True)):
            _mod = module_path(_p, AG)
            if _pfx and not _mod.startswith(_pfx):
                continue
            _files += 1
            _shown = False
            for _n, _l in enumerate(open(_p, errors="replace"), 1):
                _s2 = _l.strip()
                # comment lines only — `--` line comments and `{- -}` block bodies.
                # A trailing comment on a code line counts too: `foo = bar  -- why`
                # is where half this tree's reasoning lives.
                _c = None
                if _s2.startswith("--"):
                    _c = _s2
                elif "--" in _l and not _s2.startswith("{-#"):
                    _c = _l[_l.index("--"):].strip()
                elif _s2.startswith("{-") or _s2.startswith("-}") or _s2.startswith("|"):
                    _c = _s2
                if _c is None or not _rx.search(_c):
                    continue
                if not _shown:
                    print(f"== {_mod}")
                    _shown = True
                print(f"  {_n:5d}  {_c[:150]}")
                _hits += 1
        print(f"\n{_hits} comment line(s) in {_files} module(s) scanned"
              + (f" under {_pfx}" if _pfx else ""))
        # ⚑ ZERO IS A FACT ABOUT THE PATTERN, NOT THE TREE — say so rather than
        # letting an empty result read as an absence claim.
        if _hits == 0:
            print("no match: a fact about this REGEX over comment text, "
                  "not about the substrate")
        _sys.exit(0)

    if _args:
        _idx = def_index()
        for name in _args:
            # ⚑ AN OPERATOR HAS SEVERAL SPELLINGS and a QUALIFIED reference keys on
            # its last segment — the same rule `resolve_notinscope.homes_of`
            # applies.  Asking the authority must not require knowing which
            # spelling it stored.
            leaf = name.split(".")[-1]
            homes = (_idx.get(leaf) or _idx.get("_" + leaf + "_")
                     or _idx.get(leaf + "_") or _idx.get("_" + leaf) or [])
            print(name)
            if not homes:
                # absence here is a fact about THIS INDEX (agda/Substrate only),
                # not about the tree: `Level`, `[]`, `_⊔_` are Agda.Primitive/stdlib.
                print("      (no definer in agda/Substrate — "
                      "may be Agda.Primitive/stdlib)")
            for h in homes:
                print(f"      -> open import {h}")
        _sys.exit(0)
    print(__doc__ or "")
    print("usage: agda_defs.py <name> ...        # where does this name live?\n"
          "       agda_defs.py --provides <Mod>  # what does this module define?\n"
          "       agda_defs.py --grep <regex>    # what NAMES look like this?\n"
          "       agda_defs.py --prose <regex> [<Pfx>]\n"
          "                                      # what does the COMMENT TEXT say?\n"
          "                                      # (the half --grep cannot see)\n"
          "       agda_defs.py --imports <Mod>   # what does this module import?\n"
          "       agda_defs.py --importers <Pfx> # what imports this subtree? (consumed-by)\n"
          "       agda_defs.py --at <rev> <Mod>… [--diff]\n"
          "                                      # the module AS IT WAS at a revision —\n"
          "                                      # a pure READ.  `git checkout -- path`\n"
          "                                      # is a WRITE and destroys the working\n"
          "                                      # copy; this leaves it untouched so you\n"
          "                                      # can splice ONE line.  --diff compares\n"
          "       agda_defs.py --telescope [<Pfx>]\n"
          "                                      # a `module Over` telescope read as the\n"
          "                                      # CONTRACT its consumers apply: arity,\n"
          "                                      # and which NAME sits in each slot.  A\n"
          "                                      # rename that walks into a telescope\n"
          "                                      # keeps the arity and typechecks\n"
          "       agda_defs.py --stale-sections [<Pfx>] [--apply]\n"
          "                                      # ⚑ `--apply` WRITES: it finishes the\n"
          "                                      # rename at each reported site, one pass,\n"
          "                                      # per-LINE (never a file-wide sub).  It\n"
          "                                      # REFUSES an AMBIGUOUS row and any row on\n"
          "                                      # a module the build calls clean\n"
          "                                      # a SECTION (`a +_`, `_+ b`) left on\n"
          "                                      # an operator a rename MOVED.  A rename\n"
          "                                      # converts every APPLIED occurrence and\n"
          "                                      # misses sections, because a section\n"
          "                                      # spells the operator with only the\n"
          "                                      # underscores its open slots need.\n"
          "                                      # DIFFERENT from `fix_noparse`'s class:\n"
          "                                      # nothing is DISPLACED here, the spelling\n"
          "                                      # is stale — which is why that tool\n"
          "                                      # correctly refuses these\n"
          "       agda_defs.py --applied-args [<Pfx>]\n"
          "                                      # `open import M x` where NOTHING binds\n"
          "                                      # `x` — the telescope a decomposition\n"
          "                                      # dropped while keeping the applied\n"
          "                                      # import that consumes it.  Found twice\n"
          "                                      # only via a sweep REFUSAL; the census\n"
          "                                      # ranks such a root at cone size ~1\n"
          "                                      # while it gates a whole class\n"
          "       agda_defs.py --stranded-residue [<Pfx>]\n"
          "                                      # a split's `RESIDUE.md` READ BACK:\n"
          "                                      # for each binder the pre-split parent's\n"
          "                                      # telescope held, is it re-homed, live\n"
          "                                      # damage, or unused?  THREE-valued: a\n"
          "                                      # name bound nowhere AND used nowhere is\n"
          "                                      # neither, and folding it into damage\n"
          "                                      # reports work that does not exist.\n"
          "                                      # The third member of the chain\n"
          "                                      # --applied-args → --repair-telescopes →\n"
          "                                      # --telescope-imports, and the one those\n"
          "                                      # cannot see: they key on an APPLIED\n"
          "                                      # import argument, while a dropped PROOF\n"
          "                                      # WITNESS applies nothing to any import.\n"
          "                                      # A CENSUS — it never re-homes or deletes,\n"
          "                                      # because `write_residue` says the call\n"
          "                                      # must be a DECISION, not a side effect\n"
          "       agda_defs.py --late-imports [<Pfx>…]\n"
          "                                      # an import BELOW a use of what it\n"
          "                                      # provides — agda binds from the\n"
          "                                      # statement onward, so it supplies\n"
          "                                      # nothing above.  `agda_imports order`\n"
          "                                      # moves imports DOWN and cannot see it\n"
          "       agda_defs.py --reexports [<Pfx>…] [--triage]\n"
          "                                      # surviving `public` re-exports — the\n"
          "                                      # ban's uncensused half, and the\n"
          "                                      # reservoir refilling file-not-found.\n"
          "                                      # --triage RANKS by what paydown COSTS\n"
          "                                      # (kind × blast radius), both of which\n"
          "                                      # the tool already held and discarded.\n"
          "                                      # An `import … public` retires in place\n"
          "                                      # — bind at the real home — and costs\n"
          "                                      # its EXTERNAL importer count; ZERO\n"
          "                                      # means nothing can break, which is the\n"
          "                                      # front of the queue.  An `open <applied\n"
          "                                      # module> … public` is a DIFFERENT job\n"
          "                                      # (the instance's names have no other\n"
          "                                      # route in, so retiring rewrites every\n"
          "                                      # use site) — separate queue, never\n"
          "                                      # summed with the first\n"
          "       agda_defs.py --closure <Mod> [--prefix <Pfx>]\n"
          "                                      # transitive import closure\n"
          "       agda_defs.py --cluster <Pfx>   # leaf/hub/spine edge measurement\n"
          "       agda_defs.py --cycles          # import CYCLES over the WHOLE graph, and\n"
          "                                      # deliberately not scopable: a cycle is a\n"
          "                                      # property of the edge set, so a subtree\n"
          "                                      # census could only hide one that leaves\n"
          "                                      # and re-enters.  Exits 1 when any exists —\n"
          "                                      # the three `_would_cycle` copies sample the\n"
          "                                      # graph ONE EDGE AT A TIME and cannot see a\n"
          "                                      # cycle formed by a BATCH of edits, which is\n"
          "                                      # exactly what a tree-wide sweep produces\n"
          "       agda_defs.py --cycle-cuts      # per SCC, the MINIMAL edge set whose removal\n"
          "                                      # breaks the cycle — THE SIZE OF AN SCC IS NOT\n"
          "                                      # THE SIZE OF THE PROBLEM.  One wrong-direction\n"
          "                                      # edge absorbs a whole DAG into a component:\n"
          "                                      # measured 34- and 38-module SCCs that cut at\n"
          "                                      # 2 and 1 edge.  Each cut is tagged NEW-since-\n"
          "                                      # HEAD or pre-existing, because a minimum\n"
          "                                      # feedback arc set has no canonical member and\n"
          "                                      # the search alone will name working code.\n"
          "                                      # Exact by search where affordable, labelled\n"
          "                                      # `greedy` where not — never a heuristic\n"
          "                                      # passed off as a minimum\n"
          "       agda_defs.py --under <Pfx>     # every module in the subtree\n"
          "       agda_defs.py --dangling [--target <Mod>] [--verbose]\n"
          "                                      # every `open import M` whose M has NO\n"
          "                                      # SOURCE FILE — the dissolved-parent\n"
          "                                      # census.  A split that deletes the\n"
          "                                      # parent and leaves consumers unrewired\n"
          "                                      # surfaces ONE BUILD FAILURE AT A TIME;\n"
          "                                      # four were found that way by hand before\n"
          "                                      # this existed.  Non-Substrate targets are\n"
          "                                      # UNJUDGED, never dangling: they resolve\n"
          "                                      # from the library path, and 'I cannot see\n"
          "                                      # it' is not 'it is not there'\n"
          "       agda_defs.py --qualified [--summary]\n"
          "                                      # `import M as Q` on a Substrate module —\n"
          "                                      # BANNED, and the form --dangling and\n"
          "                                      # --unused-imports are both BLIND to (they\n"
          "                                      # read `open import`).  rewire_to_leaves\n"
          "                                      # reported `0 importer(s)` on 11 genuinely\n"
          "                                      # broken consumers: true about what it\n"
          "                                      # rewrites, read as nothing-to-do.  Split\n"
          "                                      # by whether the TARGET still exists —\n"
          "                                      # build-breaking and ban-debt are different\n"
          "                                      # urgencies and must not be summed\n"
          "       agda_defs.py --unused-imports [<Pfx>|<file.agda> …] [--summary]\n"
          "                                      # --summary aggregates BY TARGET and by\n"
          "                                      # heaviest source; the per-line form does\n"
          "                                      # not scale (a tree run is 607 KB) and\n"
          "                                      # totalling it by eye is the manipulation\n"
          "                                      # the standing rule forbids\n"
          "                                      # imports a module NAMES but does not\n"
          "                                      # REFERENCE.  Delegates to\n"
          "                                      # prune_imports.should_keep (the\n"
          "                                      # authority, whose docstring logs two\n"
          "                                      # REVERTED sharpenings) — this is the\n"
          "                                      # census half of a tool that is a WRITER\n"
          "                                      # and refuses to run standalone.  The\n"
          "                                      # count is a FLOOR: the predicate is\n"
          "                                      # keep-biased, so silence about an import\n"
          "                                      # means no-evidence, never used.  Barrels\n"
          "                                      # (no body) and parse failures are\n"
          "                                      # reported SEPARATELY, never folded into\n"
          "                                      # the clean majority\n"
          "       agda_defs.py --between <Src> <Dst>\n"
          "                                      # every import edge FROM one subtree\n"
          "                                      # INTO another, by target and by\n"
          "                                      # source — the DIRECTION question.\n"
          "                                      # --consumers/--depends aggregate to a\n"
          "                                      # package COUNT, which says the tower\n"
          "                                      # leans on Algebra.F2 (167) but not\n"
          "                                      # WHICH modules through WHICH — the\n"
          "                                      # only form a re-derivation can be\n"
          "                                      # planned in.  ORDER IS THE QUESTION:\n"
          "                                      # `A B` and `B A` are different\n"
          "                                      # measurements, and running both is how\n"
          "                                      # an INVERSION is measured, not asserted\n"
          "       agda_defs.py --consumers <Pfx> # consumed-by, AGGREGATED by package\n"
          "       agda_defs.py --depends <Pfx>   # depends-on, AGGREGATED by package\n"
          "       agda_defs.py --trust [<Pfx>]   # postulates / pragmas / holes / not --safe\n"
          "       agda_defs.py --flags [<Pfx>]   # which local {-# OPTIONS #-} fail to\n"
          "                                      # REFLECT the global flag set (.agda-lib\n"
          "                                      # flags: + AGDA_FLAGS), and which flag")
    _sys.exit(2)
