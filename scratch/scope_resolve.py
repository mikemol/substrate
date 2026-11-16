#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_resolve.py — the CANDIDATE-RESOLUTION layer of `scope_fix`, split out verbatim.

⚑ WHY THIS FILE EXISTS. `scope_fix.py` was 2,142 code lines, over the 1,200-line cap
(`pycodemod.py --size`); the rule (user, 2026-08-11) is that a file too big to read whole
before editing must be decomposed, because a patch-edit that cannot see its region whole
repairs its own damage. `scope_fix` REWRITES AGDA SOURCE, so that failure mode is corrupted
source.

WHAT IS HERE: every function that answers **"which module owns this name?"** — and nothing
that acts on the answer. Each consults the two oracles and RANKS what they return:

  owner_from_suggestion   Agda's own `did you mean 'X'?` — the compiler names the owner, so
                          this beats any ranking we can compute and is consulted first.
  owner_from_shape        the CONSUMER's own pre-strip reference set, CLASSIFIED
                          (top/ctor/field/applied) — recovers the ORIGINAL binding rather
                          than guessing a plausible one.
  shape_candidates        that classification, which is the structure the elaborated qnames
                          carry and a flat `Module.name` discards.
  owner_of_ctor           the constructor case, where the parent TYPE sits between module
                          and leaf.
  owner_by_search         the tree grep — LAST resort, and the only oracle that can see a
                          `pattern` synonym (it appears in no interned core).
  _resolve_owner          an owner that is admissible, SUPPLIABLE, and still EXPORTS the
                          name TODAY — i.e. every candidate re-verified against post-strip
                          source before it is returned.

⚑ THE LAYER IS DEFINED BY WHAT IT DOES NOT DO, AND THAT IS WHAT MADE IT SEPARABLE. Nothing
here writes, and nothing here is driven by an error message. The `fix_*` handlers in
`scope_fix` own both of those; this file is pure ranking over `scope_store` (pre-strip) and
`scope_source` (post-strip). So it calls strictly downward and closes no import cycle.

⚑ THE RANKING ORDER IS ITSELF A RECORDED DEFECT LOG — see the ⚑ blocks below. Consulting
the ranked catalog before the shape data is what "made the resolver guess", and it is why
`_resolve_owner` re-checks every candidate against current source instead of trusting the
pre-strip oracle that produced it.

⚑ MOVED VERBATIM — pure relocation, verified by `pycodemod --roundtrip`. `scope_fix`
re-exports every name, so the public surface is unchanged.
"""
import os
import re
import subprocess
import sys

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive

from scope_source import (
    _applied_owner, _conduit_owner, _is_file_module, _module_exports, _module_params,
    _nearest_reexporter, _owner_admissible, _parent_kind, _reexports_fields, _suppliable,
)
from scope_store import consumer_refs, owner_by_catalog, split_qname

# ⚑ THE SUGGESTION PARSER'S REGEX COMES WITH IT. `SUGG` is used by exactly one function
# (`owner_from_suggestion`) and by nothing else; leaving it behind would have made the moved
# function depend on a name in the module it left — the shape that turns a relocation into a
# breakage. `scope_fix` re-exports it.
SUGG = re.compile(r"'([^']+)'")


def owner_from_suggestion(name, sugg):
    """'Substrate.Algebra.F2.Vector.Vector' → module 'Substrate.Algebra.F2.Vector'.

    A suggestion may be `Module.Record.field` — the leaf is a record FIELD, which cannot be
    imported. Walk the prefix back to a real FILE module; if what we dropped was a record
    (i.e. more than the name itself), report no owner so the caller can flag it rather than
    emit an import of a non-existent module."""
    for q in SUGG.findall(sugg or ""):
        leaf = q.rsplit(".", 1)[-1]
        if leaf not in (name, f"_{name}_") or "." not in q:
            continue
        mod = q.rsplit(".", 1)[0]
        if _is_file_module(mod):
            return mod, leaf
        return None, None                       # field of a record: needs `open`, not `import`
    return None, None


def owner_by_search(name, near=None):
    """Fall back to the tree: find the module DECLARING `name` (op forms use _name_)."""
    # an operator `≡` is DECLARED as `_≡_`; try both spellings, decl-forms first.
    forms = [name] + ([f"_{name}_"] if not name.startswith("_") else [])
    pats = []
    for f in forms:
        e = re.escape(f)
        pats += [rf"^{e}\s*:", rf"^\s*(data|record)\s+{e}\b", rf"^\s*{e}\s*:"]
    hits, matched = [], name
    for f in forms:
        e = re.escape(f)
        # ⚑ T3 ⟡pd-pattern-synonyms: a `pattern ₂ = suc ₁` declaration is a real, importable
        # name that appears in NO interned core (synonyms elaborate away to `Fin.suc`/`.zero`),
        # so the shape DB and the catalog are both blind to it. The tree is the only oracle.
        # ⚑ a synonym may take ARGUMENTS (`pattern c-pos k = k , c-here _`); anchoring on `=`
        # immediately after the name missed every parameterized one — the same shape that hid
        # `data Word (Gen : Set) : Set` from the datatype matcher.
        for pat in [rf"^{e}\s*:", rf"^\s*(data|record)\s+{e}\b", rf"^\s+{e}\s*:",
                    rf"^\s*pattern\s+{e}([^\n=]*)="]:
            r = subprocess.run(["grep", "-rlE", pat, "Substrate", "--include=*.agda"],
                               capture_output=True, text=True)
            hits += [h for h in r.stdout.split() if h]
            if hits:
                matched = f
                break
        if hits:
            break
    if not hits:
        return None, name
    # prefer the home sharing the longest DIRECTORY prefix with the consumer (a bare
    # shortest-path pick sent MixColumns' `Vector` to Algebra.Q.Vector); tie-break shallow.
    def score(h):
        a, b = h.split("/"), (near or "").split("/")
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        return (-i, len(h))
    hits.sort(key=score)
    return module_path(hits[0], ""), matched


# ── ⟡paydown-shape-first ─────────────────────────────────────────────────────────────────────
# The strongest resolver is not a ranking at all: the SHAPE DB records, per unit, the elaborated
# qnames that unit REFERENCED when the tree still compiled. If this file used to reference
# `Substrate.Foundation.Unit.⊤`, then its missing `⊤` IS that one — no scoring required. This
# recovers the ORIGINAL binding instead of guessing a plausible one, which is what let a
# homonym from an exotic parameterized module (`V4-as-PFG.⊤`, `Geometry.Fano.Point`,
# `PredictorRing.Gen`, a `Σ Bool Bool` posing as `V₄`) beat the canonical home.
# ⚑⚑ T1 ⟡pd-shape-structured-qnames — THE fix behind 4 of the 6 residual files.
# The DB records ELABORATED qnames, which carry MORE structure than a flat `Module.name`:
#     top-level    Substrate.Foundation.Nat.Properties.Add.+-comm   extra ['+-comm']
#     constructor  Substrate.Groups.V4.Bijection.V₄.e               extra ['V₄','e']
#     record field Substrate.Groups.Symmetric.Permutation.apply     extra ['Permutation','apply']
#     applied mod  Substrate.Groups.S4._.Permutation                extra ['_','Permutation']
# The old filter accepted ONLY `len(extra)==1`, so EXACTLY the structured cases fell through to
# the ranked catalog — which then picked a same-named TOP-LEVEL homonym that is a DIFFERENT
# THING (`SFin.Permutation : ℕ → Set` for the record `Symmetric.Permutation`; the UNAPPLIED
# `ListPresentation.normalize` for the applied one, whose first explicit argument is then
# `(Gen : Set)` — the `Word (Base.Gen n) !=< Set` error). The structure the DB records is
# precisely what distinguishes the homonyms; discarding it is what made the resolver guess.
def shape_candidates(name, path):
    """Every pre-strip reference of the CONSUMER whose leaf is `name`, CLASSIFIED.

    Returns [(kind, module, leaf)] with kind ∈ {top, ctor, field, applied}.
    ⚑ A candidate whose module IS the consumer is dropped outright: that is the consumer's own
    same-named definition, and importing it is the whole `[CyclicModuleDependency]` class
    (`V4FullCocycle`'s local `e : V4Full` beat the wanted `V4.Bijection.V₄.e` purely because the
    ctor form was filtered out and the local one was not)."""
    if not path:
        return []
    self_mod = module_path(path, "") if path.endswith(".agda") else None
    out = []
    for qn in consumer_refs(path):
        leaf = qn.rsplit(".", 1)[-1]
        if leaf != name and leaf != f"_{name}_":
            continue
        mod, extra = split_qname(qn)
        if not mod or mod == self_mod:
            continue
        if len(extra) == 1:
            out.append(("top", mod, leaf))
        elif len(extra) == 2:
            parent = extra[0]
            out.append(("applied" if parent == "_" else _parent_kind(mod, parent), mod, leaf))
    return out


def _resolve_owner(leaf, path):
    """An owner that is admissible, SUPPLIABLE, and actually EXPORTS `leaf` today.

    Every candidate is verified against the current source before it is returned — the ranked
    catalog is a pre-strip oracle and will happily name a module that no longer exports the
    name (it named the 16-parameter `Coxeter.DirectProduct` for `Word`, which is how a whole
    alias got repointed onto a combinator)."""
    seen = []
    for cand in (owner_from_shape(leaf, path)[0], owner_by_catalog(leaf, path)[0]):
        if cand and cand not in seen:
            seen.append(cand)
            if _owner_admissible(cand, path) and _suppliable(cand, path) \
               and _module_exports(cand, leaf):
                return cand
    return _conduit_owner(leaf, path)                 # already export- and suppliability-checked


def owner_from_shape(name, path):
    """(module, spelling) recovered from the CONSUMER's own pre-strip reference set.

    `top` and `ctor` import directly. A `field` imports only when its module re-exports the
    record (`open Rec public`). An `applied` name is resolved THROUGH the applying module to
    the real owner, so the caller emits the APPLIED form — never a bare unapplied `using`."""
    cands = shape_candidates(name, path)
    if not cands:
        return None, None
    ctors = {(m, l) for k, m, l in cands if k == "ctor"}
    tops = {(m, l) for k, m, l in cands if k == "top"}
    if len(ctors) == 1 and not tops:                 # a constructor is always importable
        return ctors.pop()
    if len(tops) == 1:
        mod, leaf = tops.pop()
        # ⚑ A top-level name of a PARAMETERIZED module is NOT usable unapplied — that is the
        # `Word (Base.Gen n) !=< Set` class. Prefer a module that still re-exports the APPLIED
        # instance publicly; otherwise keep the definer and let add_import apply it.
        # ⚑ T15: a re-exporter is only useful if the CONSUMER can supply its parameters. The
        # unfiltered pick returned the 8-parameter `Coxeter.Core` for `Flat`, which no consumer
        # of `Cyclic.*` can apply — a refusal that read as "unresolvable" for four runs.
        if _module_params(mod):
            for cand in (_nearest_reexporter(mod, path), _conduit_owner(leaf, path)):
                if cand and _owner_admissible(cand, path) and _suppliable(cand, path):
                    return cand, leaf
        return mod, leaf
    if tops or ctors:
        return None, None                            # genuinely ambiguous — do not guess
    # `field`: importable iff the defining module re-exports the record publicly.
    for k, m, l in cands:
        if k == "field":
            for qn in consumer_refs(path):
                mod, extra = split_qname(qn)
                if mod == m and len(extra) == 2 and extra[1] == l and _reexports_fields(m, extra[0]):
                    return m, l
    applied = {(m, l) for k, m, l in cands if k == "applied"}
    if len(applied) == 1:
        via, leaf = applied.pop()
        owner, _args = _applied_owner(via, leaf)
        if owner:
            return owner, leaf
    return None, None


def owner_of_ctor(name, path):
    """Owner module of a CONSTRUCTOR `name`, from the consumer's pre-strip reference set."""
    cands = set()
    for qn in consumer_refs(path):
        parts = qn.split(".")
        if parts[-1] != name:
            continue
        mod, extra = split_qname(qn)
        if mod and len(extra) == 2:                  # module . TYPE . constructor
            cands.add((mod, parts[-1]))
    if len(cands) == 1:
        return cands.pop()
    o, sp = owner_from_shape(name, path)
    if o:
        return o, sp
    return owner_by_catalog(name, path)              # ranked catalog is the LAST resort
