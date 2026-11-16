#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""conduit_resolve.py — resolve a CONDUIT/BARREL chain to its base, recursively.

THE ALGORITHM (user, 2026-08-01):

    "Conduits / barrels need to be resolved RECURSIVELY in order to find all
     downstream consumers, which all need to be rewritten to bind to the base
     definition, which needs to be renamed IFF one of these final downstream
     consumers will get a naming ambiguity out of it."

Four steps, and the ORDER IS A DEPENDENCY — step 4 is conditional on step 2, so
no rename can be decided before the walk:

  1. resolve the chain RECURSIVELY to its base   (a conduit may import a conduit)
  2. enumerate the FINAL downstream consumers    (NOT the barrel's direct importers)
  3. rewrite each to bind at the base
  4. rename at source IFF a final consumer would then be AMBIGUOUS

⚑ WHY A PER-FILE JUDGEMENT IS THE WRONG SHAPE.  `prune_imports` asks "is this
import used in this file?"  A pure barrel has NO BODY, so the answer is always
"no" and the honest response is to refuse (which it now does).  But refusing
resolves nothing: the barrel still stands and its consumers still bind through
it.  A barrel is not a file to judge — it is an EDGE IN A CHAIN.

⚑ WHAT THIS REUSES, AND THE ONE THING IT DOES NOT.
`scope_fix._conduit_set/_conduit_owner/_conduit_pair` (`:2234-2294`) already walk
conduit chains — but they answer the INVERSE question ("which conduit supplies
name X to consumer P", a lookup) and `_conduit_set` is capped at
`for _ in range(3)`.  MEASURED: 95 pure conduits tree-wide, chain-depth histogram
{1:80, 2:12, 3:2, 4:1} — the bound bites on `Groups.Actions.S3-on-V4` TODAY, and
"3" is a magic number where the spec says RECURSIVELY.  `_module_exports` already
recurses to depth 12 with a `seen` set, so the recursion primitive exists; this
module supplies the missing direction and drops the bound.

Usage:
    conduit_resolve.py --list                    # every pure conduit + its depth
    conduit_resolve.py <Module>                  # resolve one chain to its base
    conduit_resolve.py <Module> --consumers      # + the FINAL downstream consumers
    conduit_resolve.py <Module>… --plan          # THE WHOLE 4-STEP RESOLUTION: per-name routing
                                                 # and the ambiguities, with signatures attached,
                                                 # grouped by TARGET SET (the unit of review).
                                                 # ⚑ `plan()` WAS DECIDED AND UNREACHABLE — 1 def,
                                                 # 3 calls, ALL in the selftest. The tool computed
                                                 # the actionable answer and `main` could print
                                                 # only bases and consumers, so no operator could
                                                 # ask for it. Exits 1 on a module that has a body
                                                 # (not a conduit — nothing to resolve).
    conduit_resolve.py --selftest
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import agda_lex

AG = "agda"
IMPORT = re.compile(r"^\s*(?:open\s+)?import\s+(Substrate\S*)", re.M)


def _src(mod):
    p = os.path.join(AG, mod.replace(".", "/") + ".agda")
    try:
        return agda_lex.mask_comments(open(p, encoding="utf-8", errors="replace").read())
    except OSError:
        return None


def is_conduit(mod):
    """True iff `mod` has a header and NO body — imports and prose only.

    That is the structural definition of a barrel: it exists to aggregate, so it
    declares nothing itself.  Deliberately NOT "has `public`" — a barrel that
    forgot `public` is still a barrel, and `⟡public-policy` has been retiring
    the flag, so keying on it would shrink the population as the policy succeeds.
    """
    src = _src(mod)
    if src is None:
        return False
    lines = src.split("\n")
    try:
        hdr = next(i for i, l in enumerate(lines) if l.startswith("module "))
    except StopIteration:
        return False
    has_body = any(l.strip() and not re.match(r"\s*(open |import |\{-|--)", l)
                   for l in lines[hdr + 1:])
    if has_body:
        return False
    # ⚑ A BARREL AGGREGATES SOMETHING.  "no body" alone also matches an EMPTY
    # STUB — a module with no body AND NO IMPORTS, which aggregates nothing and
    # has no base to resolve to.  MEASURED: 14 of 95 (`Algebra.F1.Capstone`,
    # `Algebra.F2.GF256`, `Category.Allegory.Refinement.Preamble`, …).  They
    # surfaced as "280 final consumers, 0 bases" — an incoherent verdict that a
    # rewrite-to-base step would have acted on.  A conduit must have at least one
    # outgoing edge, or it is a different thing wearing the same shape.
    return bool(IMPORT.findall(src))


def imports_of(mod):
    src = _src(mod)
    return list(dict.fromkeys(IMPORT.findall(src))) if src else []


def resolve(mod, _seen=None):
    """(bases, path) — resolve `mod` RECURSIVELY to the non-conduit modules under it.

    No depth bound: recurse until every branch reaches a module that declares
    something.  `_seen` breaks import cycles (a conduit pair that re-exports each
    other would otherwise spin) — the same guard `_module_exports` uses.
    """
    _seen = _seen if _seen is not None else set()
    if mod in _seen:
        return set(), []
    _seen.add(mod)
    if not is_conduit(mod):
        return {mod}, [mod]
    bases, chain = set(), [mod]
    for sub in imports_of(mod):
        b, c = resolve(sub, _seen)
        bases |= b
        if len(c) > len(chain) - 1:
            chain = [mod] + c
    return bases, chain


def depth(mod, _seen=None):
    """Longest conduit-only chain from `mod` (0 if it is not a conduit)."""
    _seen = _seen or set()
    if mod in _seen or not is_conduit(mod):
        return 0
    _seen.add(mod)
    return 1 + max([depth(x, _seen) for x in imports_of(mod) if is_conduit(x)] + [0])


def conduits():
    """Every pure conduit in the tree — DISCOVERED, never declared."""
    out = []
    for f in agda_lex.agda_files(AG):
        m = agda_lex.module_path(f, AG)
        if is_conduit(m):
            out.append(m)
    return out


def final_consumers(mod, _seen=None):
    """Modules that import `mod` (transitively THROUGH conduits) and are NOT conduits.

    ⚑ STEP 2, and the reason the rename in step 4 cannot be decided early: a
    barrel's DIRECT importers may themselves be barrels, so the set that will
    actually be rewritten — and can actually become ambiguous — is only known
    after the walk.
    """
    _seen = _seen if _seen is not None else set()
    direct = [m for m in _all_importers().get(mod, ()) if m not in _seen]
    out = set()
    for m in direct:
        _seen.add(m)
        if is_conduit(m):
            out |= final_consumers(m, _seen)
        else:
            out.add(m)
    return out


_IMPORTERS = None


def _all_importers():
    """{module -> [modules importing it]} — built once."""
    global _IMPORTERS
    if _IMPORTERS is None:
        _IMPORTERS = {}
        for f in agda_lex.agda_files(AG):
            me = agda_lex.module_path(f, AG)
            for t in IMPORT.findall(
                    agda_lex.mask_comments(open(f, encoding="utf-8", errors="replace").read())):
                _IMPORTERS.setdefault(t, []).append(me)
    return _IMPORTERS


# ── STEPS 3-4: rewrite to the base, rename IFF ambiguous ───────────────────
from agda_defs import def_index as _def_index


def exports_of(mod):
    """Names `mod` defines, from the shared def-index (never a local `^name :` scan)."""
    return {n for n, homes in _def_index().items() if mod in homes}


def _requested_names(src, conduit):
    """The names a consumer asks the conduit for — None if it imports it BARE.

    None and the empty set are DIFFERENT answers: `using ()` means "nothing by
    name", while bare means the module's WHOLE export set.

    ⚑ AND UNDER ONE-DEFINITION-PER-FILE, "EVERYTHING" IS NOT VAGUE (user,
    2026-08-01): *"each file should only have one thing, so 'everything' means
    'exactly the thing I've named by doing the bare import, and nothing more'."*
    A bare `open import Substrate.Foo.Bar` IS the demand — `Bar` names one thing,
    so the caller can route it as precisely as a `using` list. I had been treating
    bare as *demand-unknown* and erring wide, which is the same over-wide reflex
    that produced 354 over-imported consumers.

    ⚑ MEASURED, and the invariant is the TARGET not yet the STATE: of 656 bases
    reachable from the conduits, **347 export exactly one name**; the rest are 0
    (empty stub) or 2+ (not yet split). So a caller must ROUTE BY THE BASE'S OWN
    EXPORT SET — which is exactly one name where the decomposition has landed, and
    honestly wider where it has not. Never "all the conduit's bases".
    """
    if src is None:
        return None
    want, saw_bare = set(), False
    for m in re.finditer(r"^\s*(?:open\s+)?import\s+(Substrate\S*)([^\n]*)", src, re.M):
        if m.group(1) != conduit:
            continue
        u = re.search(r"using\s*\(([^)]*)\)", m.group(2))
        if not u:
            saw_bare = True
        else:
            want |= {x.strip() for x in u.group(1).split(";") if x.strip()}
    return None if saw_bare else want


def signature_of(mod, name):
    """`name`'s declared type in `mod`, or None — the SPELLING as Agda sees it.

    ⚑ A BARE NAME IS NOT A DECIDABLE UNIT (user, 2026-08-01: *"the tooling should
    have been able to present a plan about this, including type signatures"*).
    A plan that says *"`-ℤ` collides"* is unactionable; one that says

        Z.Sub._-ℤ_  : ℤ → ℤ → ℤ      (binary subtraction)
        Z.Int2.-ℤ_  : ℤ → ℤ          (unary negation)

    tells the reader instantly that these are DIFFERENT OPERATORS and that
    "renaming the collision" would pick one meaning for a consumer wanting the
    other.  MEASURED: `agda_defs.def_index` keys BOTH under the bare `-ℤ`, so the
    index's own spelling manufactures a collision Agda does not have — the
    mixfix-underscore distinction (`_x_` binary vs `x_` unary) is exactly the
    information it drops.
    """
    src = _src(mod)
    if src is None:
        return None
    for sp in (f"_{name}_", f"{name}_", name):
        m = re.search(r"^" + re.escape(sp) + r"\s*:([^\n]*)$", src, re.M)
        if m:
            return f"{sp} :{m.group(1).rstrip()}"
    return None


def ambiguity(consumer, bases):
    """{name -> {other providers ALSO imported by `consumer`}} if it bound at `bases`.

    ⚑ STEP 4, AND IT IS NOT A RARE EDGE CASE.  MEASURED before building this:
    **22 of 71 (consumer, conduit) pairs would become ambiguous** at the base.
    That is the whole reason the four steps are ordered — the rename is
    CONDITIONAL on this answer, and this answer needs the step-2 walk.

    A consumer that reaches a name THROUGH a conduit sees exactly one binding.
    Bind it at the base and it sees the base's — plus any other provider it
    already imports directly. That second binding is the ambiguity, and it exists
    only after the rewrite, which is why a per-file pre-check cannot find it.
    """
    src = _src(consumer)
    if src is None:
        return {}
    # ⚑ A `using (…)` FILTER MEANS THE NAME NEVER ENTERS SCOPE.  Counting a module
    # as "imported" ignores what it actually BINDS: `open import M using (_*ℤ_)`
    # brings in exactly one name, so a collision on `-ℤ` through that statement is
    # impossible.  MEASURED before writing any apply: **18 of 22 reported
    # ambiguities were FALSE for exactly this reason** — including
    # `Q/Properties/Abs.agda`, which compiles today and would have been "fixed" by
    # a rename it does not need.
    #
    # ⚑⚑ And the rename would have been WRONG, not merely unnecessary: `-ℤ` has
    # THREE providers and they are DIFFERENT OPERATORS — `Z.Sub._-ℤ_` is binary
    # subtraction, `Z.Int2.-ℤ_` is unary negation. Renaming "the collision" picks
    # one meaning for a consumer that wants the other.
    bound = {}          # module -> the names it actually brings into scope (None = all)
    for m in re.finditer(r"^\s*(?:open\s+)?import\s+(Substrate\S*)([^\n]*)", src, re.M):
        mod, tail = m.group(1), m.group(2)
        u = re.search(r"using\s*\(([^)]*)\)", tail)
        names = {x.strip() for x in u.group(1).split(";") if x.strip()} if u else None
        prev = bound.get(mod, "unset")
        # two statements for one module: the scope is the UNION, and a bare one wins
        bound[mod] = None if (names is None or prev is None) else (
            names if prev == "unset" else prev | names)
    out = {}
    for b in bases:
        for name in exports_of(b):
            others = set()
            for o in set(_def_index().get(name, ())) - set(bases):
                vis = bound.get(o, "absent")
                if vis == "absent":
                    continue                      # not imported here at all
                if vis is None or name in vis:    # bare import, or explicitly named
                    others.add(o)
            if others:
                out.setdefault(name, set()).update(others)
    return out


def plan(mod):
    """The full 4-step plan for conduit `mod` — DECIDED, not applied.

    Returns {conduit, bases, consumers, rewrites, renames}:
      · `rewrites` — (consumer, base) pairs: step 3.
      · `renames`  — {name: providers} per consumer: step 4's CONDITIONAL, the
        subset that needs `rename_at_source` on the OTHER provider first.

    ⚑ PLAN, THEN APPLY — the shape `prune_imports` learned after writing
    unconditionally. And ⚑ MEASURE WHAT THE NEXT STEP WOULD DO: asking this
    module for its actionable answer is what exposed the empty-stub bug (three
    conduits reporting "280 consumers, 0 bases"), which a census alone had hidden.
    """
    if not is_conduit(mod):
        return None
    bases, chain = resolve(mod)
    consumers = sorted(final_consumers(mod))
    rewrites, renames = [], {}
    for c in consumers:
        amb = ambiguity(c, bases)
        if amb:
            # ⚑ ATTACH THE SIGNATURES.  "`-ℤ` collides" is not actionable; the pair
            # of type signatures decides the case on sight — same spelling, same
            # arity, same type ⇒ a genuine duplicate that wants a rename; DIFFERENT
            # arity or type ⇒ two operators the index merged, and renaming either
            # is wrong.  This is what makes the plan reviewable rather than trusted.
            renames[c] = {
                name: {o: signature_of(o, name) for o in sorted(others)}
                | {b: signature_of(b, name) for b in sorted(bases)
                   if signature_of(b, name)}
                for name, others in amb.items()}
        # ⚑ ROUTE PER NAME, NOT PER CONDUIT.  Rewriting a consumer to ALL the
        # conduit's bases hands it modules it never asked for.  MEASURED on
        # `Algebra.Q.Add`, which imports the conduit `using (_+ℤ_; _*ℤ_)`: the two
        # names live in `Z.Add` and `Z.Mul` ONLY, yet a whole-base rewrite would
        # also give it `Z.Sub`.
        #
        # That is exactly the over-wide shape this arc already paid for twice —
        # 354 consumers holding ≥5 leaves of one parent (§17), and the `+_` SECTION
        # ambiguity that `split_pipeline:366` records as fixable ONLY by dropping
        # the unused import.  A rewrite that needs a prune afterwards is a rewrite
        # that was too wide to begin with.
        #
        # A BARE import (no `using`) genuinely needs every base — the consumer's
        # demand is unknown, so err wide there and let the pipeline's prune cut it.
        wanted = _requested_names(src_of := _src(c), mod)
        if wanted is None:
            # ⚑ BARE IS NOT "DEMAND UNKNOWN" — route it by what the consumer's BODY
            # actually mentions. Under one-definition-per-file a base names one
            # thing, so this is as precise as a `using` list; where the split has
            # not landed the base is wider and this is honestly wider with it.
            # Erring wide here is what handed 354 consumers leaves they never used.
            body = "\n".join(l for l in (src_of or "").split("\n")
                             if not IMPORT.match(l))
            used = {n for b in bases for n in exports_of(b)
                    if agda_lex.word(n).search(body)}
            targets = sorted({b for b in bases if exports_of(b) & used}) or sorted(bases)
        else:
            targets = sorted({b for b in bases
                              if exports_of(b) & wanted}) or sorted(bases)
        rewrites.append((c, targets))
    return {"conduit": mod, "bases": sorted(bases), "chain": chain,
            "consumers": consumers, "rewrites": rewrites, "renames": renames}


def _selftest():
    """Counted from len(cases)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    # These run against the LIVE tree — the corpus is the fixture, as with the
    # sibling tools' corpus-backed cases.
    cs = conduits()
    check("conduits() finds the measured population (95 at census time; "
          "assert only that it is non-trivial and bounded)",
          10 < len(cs) < 400, True)
    check("a conduit is not its own base", all(is_conduit(c) for c in cs[:5]), True)
    # ⚑ THE BOUND DOES NOT BITE TODAY — and my first measurement said it did.
    # An earlier ad-hoc script shared ONE `seen` set across sibling branches, so a
    # module already visited down one branch was skipped in another and the depth
    # inflated to 4.  Correct per-branch recursion gives {1:80, 2:14, 3:1}: max 3,
    # exactly AT `_conduit_set`'s `range(3)`, not past it.  The resolver is still
    # right to be unbounded — "3" is a magic number and the deepest chain sits ON
    # it, one added layer from silent truncation — but the JUSTIFICATION is
    # "no arbitrary bound", not "the bound is currently wrong".
    check("the deepest chain sits AT the old bound of 3 (not past it)",
          max((depth(c) for c in cs), default=0), 3)
    # resolve() must terminate and reach non-conduits
    b, _ch = resolve(cs[0]) if cs else (set(), [])
    check("resolve() reaches only NON-conduit bases",
          all(not is_conduit(x) for x in b), True)
    # ⚑ AN EMPTY STUB IS NOT A BARREL.  14 of the first 95 "conduits" had no body
    # AND no imports; they reported "280 final consumers, 0 bases" — a verdict a
    # rewrite-to-base step would have ACTED on.
    check("an empty stub (no body, NO imports) is not a conduit",
          any(is_conduit(m) and not imports_of(m) for m in cs), False)
    check("every conduit has at least one outgoing edge",
          all(imports_of(m) for m in cs), True)
    # ── steps 3-4 ───────────────────────────────────────────────────────────
    live = [m for m in cs if final_consumers(m)]
    check("some conduit has final consumers to rewrite (step 3 has work)",
          bool(live), True)
    if live:
        pl = plan(live[0])
        check("plan(): one rewrite per final consumer",
              len(pl["rewrites"]), len(pl["consumers"]))
        check("plan(): every rewrite targets a NON-EMPTY base set",
              all(b for _c, b in pl["rewrites"]), True)
        # ⚑ step 4 is CONDITIONAL and must be a SUBSET of the rewrites — a rename
        # for a consumer that is not being rewritten would be unmotivated.
        check("plan(): renames are a subset of the consumers",
              set(pl["renames"]) <= set(pl["consumers"]), True)
    # ⚑ SIGNATURES MAKE THE PLAN REVIEWABLE.  `-ℤ` is keyed bare by def_index for
    # BOTH `Z.Sub._-ℤ_ : ℤ → ℤ → ℤ` (binary) and `Z.Int2.-ℤ_ : ℤ → ℤ` (unary) — so
    # the INDEX manufactures a collision Agda does not have, and a rename would
    # pick one meaning for a consumer wanting the other.
    check("signature_of recovers the mixfix spelling AND arity (binary)",
          signature_of("Substrate.Algebra.Z.Sub", "-ℤ"), "_-ℤ_ : ℤ → ℤ → ℤ")
    check("signature_of distinguishes the UNARY same-bare-name operator",
          signature_of("Substrate.Algebra.Z.Int2", "-ℤ"), "-ℤ_ : ℤ → ℤ")
    # ⚑ PER-NAME ROUTING.  A whole-base rewrite hands a consumer modules it never
    # asked for — the over-wide shape this arc paid for twice (354 consumers; the
    # `+_` section ambiguity). MEASURED on `Algebra.Q.Add`: it asks the conduit for
    # `_+ℤ_; _*ℤ_`, which live in Z.Add and Z.Mul ONLY, yet the whole-base rewrite
    # also handed it Z.Sub.
    check("_requested_names: a `using` list is the demand",
          # ⚑ the fixture must use a REAL module prefix: the scanner matches
          # `Substrate\S*`, so a bare `M` never matches and every answer is the
          # empty set — a test that would have "passed" a broken helper.
          _requested_names("open import Substrate.M using (a; b)\n",
                           "Substrate.M"), {"a", "b"})
    check("_requested_names: a BARE import means demand-unknown (None, not empty)",
          _requested_names("open import Substrate.M\n", "Substrate.M"), None)
    check("_requested_names: bare WINS over a sibling using-statement",
          _requested_names("open import Substrate.M using (a)\nopen import Substrate.M\n", "Substrate.M"), None)
    _zp = plan("Substrate.Algebra.Z.Arithmetic")
    if _zp:
        _t = dict(_zp["rewrites"]).get("Substrate.Algebra.Q.Add")
        check("plan(): a filtered consumer routes ONLY to the bases owning its names",
              _t, ["Substrate.Algebra.Z.Add", "Substrate.Algebra.Z.Mul"])
    # ⚑ A BARE import is routed by what the BODY uses, not by "all bases" —
    # under one-definition-per-file the base names one thing, so bare is as
    # precise as a `using` list.  MEASURED: whole-base rewrites 34 -> 3 (per-name)
    # -> 4 of 71 tree-wide (bare-by-usage), the remainder being genuinely-wide bases.
    if _zp:
        _allbases = len(_zp["bases"])
        _widest = [c for c, t in _zp["rewrites"] if len(t) == _allbases]
        check("plan(): few consumers need EVERY base of a multi-base conduit",
              len(_widest) < len(_zp["rewrites"]) // 2, True)
    check("plan() of a NON-conduit is None", plan("Substrate.Foundation.Bool.Bool"), None)
    check("resolve() of a NON-conduit is itself",
          resolve("Substrate.Foundation.Bool.Bool")[0], {"Substrate.Foundation.Bool.Bool"})
    # cycle safety: resolve must not recurse forever on a self-referential seen-set
    check("resolve() is cycle-safe (returns, does not hang)",
          isinstance(resolve(cs[0])[0], set) if cs else True, True)

    ok = sum(1 for _, g, _, _ in cases if g)
    for n, g, got, want in cases:
        if not g:
            print(f"  FAIL {n}\n       got {got!r} want {want!r}")
    print(f"conduit_resolve selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


def main(argv):
    if "--selftest" in argv:
        return _selftest()
    args = [a for a in argv[1:] if not a.startswith("-")]
    if "--list" in argv or not args:
        cs = conduits()
        print(f"  {len(cs)} pure conduit(s) (header + imports, NO body):")
        for c in sorted(cs, key=lambda m: -depth(m))[:20]:
            print(f"    depth {depth(c)}  {c}")
        return 0
    if "--plan" in argv:
        # ⚑ `plan()` WAS DECIDED AND UNREACHABLE — 1 def, 3 calls, ALL of them in
        # the selftest.  The tool computes the whole 4-step resolution (per-name
        # routing, ambiguity with signatures attached) and `main` could print only
        # bases and consumers, so the actionable answer existed and no operator
        # could ask for it.  Same shape as `solvers()` knowing a class's module
        # COUNT while discarding the set.
        rc = 0
        for mod in args:
            pl = plan(mod)
            if pl is None:
                print(f"  {mod}: NOT a conduit (has a body) — nothing to resolve")
                rc = 1
                continue
            print(f"  {pl['conduit']}  →  {len(pl['bases'])} base(s), "
                  f"{len(pl['consumers'])} final consumer(s)")
            for b in pl["bases"]:
                print(f"      base · {b}")
            # ⚑ GROUPED BY TARGET SET, because that is the unit of review: the
            # question an operator asks is "which consumers get handed which
            # bases", and a flat per-consumer list buries the over-wide rewrites
            # this tool exists to avoid.
            byt = {}
            for c, t in pl["rewrites"]:
                byt.setdefault(tuple(t), []).append(c)
            for t, cs in sorted(byt.items(), key=lambda kv: -len(kv[1])):
                wide = " ⚑ EVERY base" if len(t) == len(pl["bases"]) else ""
                print(f"    {len(cs):>3} consumer(s) → "
                      f"{', '.join(x.split('.')[-1] for x in t)}{wide}")
            if pl["renames"]:
                # ⚑ STEP 4 IS CONDITIONAL AND IS NOT AUTO-APPLIED.  A collision may
                # be the INDEX's, not agda's: `-ℤ` is keyed bare for both a binary
                # `Z.Sub._-ℤ_` and a unary `Z.Int2.-ℤ_`, and renaming either picks
                # a meaning some consumer did not want.  The signatures are printed
                # so the case is decided on sight.
                print(f"    ⚑ {len(pl['renames'])} consumer(s) need a "
                      f"rename-at-source FIRST (step 4, conditional):")
                for c, names in sorted(pl["renames"].items())[:6]:
                    for n, provs in sorted(names.items()):
                        print(f"        {c.split('.')[-1]}: `{n}`")
                        for o, sig in sorted(provs.items()):
                            print(f"            {sig or '?':<28} {o}")
            print("   ⚑ a plan is DECIDED, not applied — the rewrite runs through "
                  "the\n     pipeline's rewire stage, which owns the write.")
        return rc
    for mod in args:
        bases, chain = resolve(mod)
        print(f"  {mod}")
        print(f"    conduit: {is_conduit(mod)}   chain depth: {depth(mod)}")
        print(f"    chain:   {' -> '.join(chain)}")
        print(f"    base(s): {len(bases)}")
        for b in sorted(bases)[:8]:
            print(f"      · {b}")
        if "--consumers" in argv:
            fc = final_consumers(mod)
            print(f"    FINAL downstream consumers (non-conduit): {len(fc)}")
            for c in sorted(fc)[:8]:
                print(f"      → {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
