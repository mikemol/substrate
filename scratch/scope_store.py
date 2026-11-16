#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_store.py — the CATALOG / SPPF STORE layer of `scope_fix`, split out verbatim.

⚑ WHY THIS FILE EXISTS. `scope_fix.py` was 2,142 code lines, over the 1,200-line cap
(`pycodemod.py --size`). The rule (user, 2026-08-11): *"if a file is so big you have to
patch-edit it, then it needs to be decomposed into smaller files."* `scope_fix` REWRITES
AGDA SOURCE, so a decomposition defect here is corrupted source, not a broken query.

THE THREE-LAYER SPLIT, AND WHAT EACH LAYER IS AN AUTHORITY ON:

  scope_store   (this file)  — what the INTERNED CORES say. catalog.db and the SPPF `ref`
                               index: which qnames exist, what each unit REFERENCED after
                               elaboration, at which application index. Pre-strip truth.
  scope_source  — what the CURRENT AGDA TEXT says: exports, imports, applications, renames,
                               telescopes. Post-strip truth. Owns THE WRITE PATH.
  scope_fix     — the error-driven `fix_*` handlers, the resolvers that RANK candidates
                               across the two oracles, and the CLI.

⚑ THE TWO ORACLES ANSWER DIFFERENT QUESTIONS AND THE SPLIT MAKES THAT UNCONFUSABLE. This
file is a PRE-STRIP oracle: `_module_defines` reports what a module defined BEFORE the
`public` re-exports were removed, so it is a false positive for any name whose only route
was a `public` that is now gone. `scope_source._module_exports` is the post-strip
counterpart, and the ⟡pd-export-oracle note records that reading the first where the second
was meant is what made the resolver "write an import that binds nothing". Two files, two
names, no ambiguity about which oracle a call site is consulting.

⚑ THIS LAYER CALLS DOWNWARD ONLY. `split_qname` needs `_is_file_module` and `_event_refs`
needs `_module_params` — both source questions, both taken from `scope_source`, which imports
nothing from here. `scope_fix` imports both and re-exports every name, so the public surface
(`scope_fix.X`, `from scope_fix import X`) is unchanged.

⚑ THE ⚑ COMMENTS MOVED VERBATIM — this is a pure relocation, verified by
`pycodemod --roundtrip`. No signature, body, or comment was altered.
"""
import base64
import os
import re
import sys

import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_lex import module_path   # THE path<->module authority; never re-derive

# ⚑⚑⚑ THE STORE AUTHORITY IS IMPORTED AT MODULE SCOPE, AND THAT IS A CENSUS FACT, NOT A STYLE
# CHOICE (⟡tenant-mandatory / `gate-F23`). `_connect_catalog` used to do its own
# `sys.path.insert` for `jea/metalanguage` and then `import store` INSIDE THE FUNCTION — not
# because the import was deliberately lazy, but because the module-scope insert above reaches
# only `scratch/`. A path-setup ordering artifact, read by two subsequent readers as intent.
#
# ⚑⚑ WHAT IT COST: `run_selftests --tenants` measures store reach by MODULE-LEVEL import
# closure, and a deferred import is a different edge — correctly excluded, since importing
# this module does not execute it. So this suite genuinely opened a store while every
# import-shaped probe read "reaches no store", and after it declared a tenant the census
# labelled it `STRAY — declares a tenant, reaches no store`, which was FALSE. That is
# `sql-F23`'s shape (a store-reacher no import probe can see) reproduced on a second file.
#
# ⚑ THE FIX IS THE PATH, NOT THE IMPORT. Both directories go on the path here, once, so the
# import can say what it means at the top of the file where a reader — and a census — will
# find it. Cost is one module import at startup for a tool whose every mode reaches the store
# anyway; the previous arrangement bought nothing and hid a row.
_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)),
                               "..", "jea", "metalanguage"))
import store as _store

from scope_source import (_is_file_module, _module_params, _alias_binding,
                          _rename_index, rename_records)


def _b64(s):
    """catalog.db's content-address: a REVERSIBLE base64 of the string, not a hash."""
    return base64.b64encode(s.encode()).decode()


_CAT = None
_REFS = None        # unit_id -> set(referenced qname)   |   module -> set(referenced qname)


def catalog_index():
    """leaf-name → [full qname] from the INTERNED cores (catalog.db), not a grep proxy.

    The elaborated qname carries the structure grep cannot see: a trailing `Type._∣_.divides`
    says `divides` is a CONSTRUCTOR of `_∣_` in module `…Divides.Type`; `Wedge.Wedge.remainder`
    says `remainder` is a record FIELD (which cannot be imported by name — it needs an `open`).
    """
    global _CAT
    if _CAT is None:
        import collections
        _CAT = collections.defaultdict(list)
        try:
            sys.path.insert(0, os.path.join(os.getcwd(), "..", "jea", "metalanguage"))
            import catalog_db as C
            import query_builders as QB
            # ⚑ STREAM, DO NOT MATERIALIZE. `QB.run` returns `con.execute(...)` — a
            # cursor — and this loop is a pure FOLD: every row is consumed once and
            # only appended to `_CAT`. `.fetchall()` therefore built a full list of
            # every unit name in the catalog solely to iterate it and drop it.
            for r in QB.run(C.connect(), "unit_names"):
                qn = r[-1]
                if qn and "." in qn:
                    _CAT[qn.rsplit(".", 1)[-1]].append(qn)
        except Exception as e:                      # no catalog → fall back to grep
            print(f"    (catalog unavailable: {e})")
    return _CAT


def ref_index():
    """SHAPE DATA (user: "see the shape database for guidance"): every unit's REFERENCED qnames.

    Codomain alone cannot disambiguate `+-assoc` — every candidate is an `_≡_`. What separates
    ℕ's from F₂'s is the CARRIER each one MENTIONS. `deserialize_oppath` is that reference set,
    read off the interned cores; ranking a candidate by how much its reference set overlaps the
    CONSUMER's is what stops the resolver writing `Algebra.F2.+-assoc` into a ℕ context
    (which is what produced every `[UnequalTerms]` — a resolver bug, NOT a load-bearing re-export).
    """
    global _REFS
    if _REFS is None:
        import collections
        _REFS = collections.defaultdict(set)
        try:
            sys.path.insert(0, os.path.join(os.getcwd(), "..", "jea", "metalanguage"))
            import catalog_db as C
            import query_builders as QB
            # ⚑ TWO MATERIALIZED RESULT SETS WHERE ONE IS A LOOKUP FOR THE OTHER.
            # Both were `.fetchall()`: the first list existed only to become `names`
            # (so it was a fold), and the second only to be consumed row-by-row.
            # Streaming both holds one row at a time instead of two whole tables.
            #
            # ⚑ `names` IS STILL RESIDENT, AND THAT IS A JOIN NOT YET HANDED TO THE
            # ENGINE. It is a unit_id → qname map used to resolve the second query's
            # rows — i.e. `deserialize_oppath JOIN unit_names USING (unit_id)`, which
            # SQLite would stream in one pass. Recorded rather than done here: this
            # sitting is the mechanical fetchall sweep, and inventing a joined query
            # is a change to what is asked, not to how the answer is held.
            names = {}
            for r in QB.run(C.connect(), "unit_names"):
                names[r[0]] = r[-1]
            for r in QB.run(C.connect(), "deserialize_oppath"):
                qn = names.get(r[0])
                if qn:
                    _REFS[qn].add(r[-1])
        except Exception as e:
            print(f"    (ref-index unavailable: {e})")
    return _REFS


def consumer_refs(path):
    """The carriers the CONSUMER works over: union of its own units' reference sets (from HEAD,
    i.e. from when the file still compiled — exactly the context we must preserve)."""
    idx = ref_index()
    mod = module_path(path, "") + "."
    out = set()
    for qn, rs in idx.items():
        if qn.startswith(mod):
            out |= rs
    return out


def split_qname(qn):
    """Longest prefix that is a real FILE module → (module, [extra components])."""
    parts = qn.split(".")
    for i in range(len(parts) - 1, 0, -1):
        mod = ".".join(parts[:i])
        if _is_file_module(mod):
            return mod, parts[i:]
    return None, []


def owner_by_catalog(name, near=None):
    """Resolve via the interned catalog. Returns (module, import-spelling) or (None, None).

    A record FIELD is refused (it is not an importable name); a data CONSTRUCTOR is fine.
    """
    single_letter = len(name) == 1 and name.islower()   # `a` is usually a pattern variable …
    idx = catalog_index()
    cands = idx.get(name) or idx.get(f"_{name}_") or []
    if not cands:
        return None, None

    ctx = consumer_refs(near) if near else set()
    idxr = ref_index()
    # modules the consumer ALREADY imports — the strongest signal, and the one that stops
    # shape-overlap displacing an obvious canonical home (`cong₂` Foundation.Eq → FUSepQ,
    # `⊤` Brick.Unit → V4-as-PFG were exactly that overcorrection).
    here = set()
    try:
        here = set(re.findall(r"^open import ([\w.-]+)", open(near).read(), re.M)) if near else set()
    except OSError:
        pass

    # names the consumer ALREADY imports (from its using-lists) — a CONSTRUCTOR whose parent
    # data type is already imported is almost certainly the intended one. Same cohesion
    # principle as ⟡paydown-alias-cohesion, one level over: `e`/`α`/`β`/`γ` are constructors of
    # `V₄`, and Bundle already imports `V₄` — without this the ranking picked `Bezout._.α`,
    # a name inside an ANONYMOUS module (parent `_`), which is not a sane import path.
    herenames = set()
    try:
        if near:
            for u in re.findall(r"using \(([^)]*)\)", open(near).read()):
                herenames |= {x.strip() for x in re.split(r"[;\s]+", u) if x.strip()}
    except OSError:
        pass

    def score(qn):
        mod, _ = split_qname(qn)
        parts = qn.split(".")
        parent = parts[-2] if len(parts) >= 2 else ""
        kin = 0 if parent in herenames else 1        # parent type already imported → prefer
        anon = 1 if parent == "_" else 0             # anonymous-module member → deprefer
        a, b = (mod or "").replace(".", "/").split("/"), (near or "").split("/")
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        overlap = len(idxr.get(qn, set()) & ctx) if ctx else 0
        return (kin, anon,                   # constructor-of-an-imported-type wins outright
                0 if mod in here else 1,     # then an already-imported module
                -overlap, -i, len(qn))       # then shape-overlap, then path proximity

    ranked = sorted(cands, key=score)
    # … but NOT when it is a CONSTRUCTOR of a type the consumer already imports: `e` is a
    # single lowercase letter AND a constructor of `V₄`. The blanket refusal made `e`
    # unresolvable, so the fallback bound it to an unrelated module and closed an import cycle.
    if single_letter and score(ranked[0])[0] != 0:
        return None, None
    for qn in ranked:
        mod, extra = split_qname(qn)
        if not mod:
            continue
        leaf = qn.rsplit(".", 1)[-1]
        if not extra[:-1]:                          # top-level name in `mod`
            return mod, leaf
        parent = extra[-2]
        try:
            src = open(mod.replace(".", "/") + ".agda").read()
        except OSError:
            continue
        if re.search(rf"^\s*record\s+{re.escape(parent)}\b", src, re.M):
            continue                                # a FIELD — needs `open Rec`, not an import
        return mod, leaf                            # a data CONSTRUCTOR — importable
    return None, None


def _module_defines(mod, leaf):
    """Does `mod` DEFINE `leaf`? Asked of catalog.db (the owner oracle), never of grep —
    grep gave the wrong owner three times; the elaborated qnames carry what grep cannot see."""
    return any(q.rsplit(".", 1)[0] == mod for q in catalog_index().get(leaf, ()))


_DEMAND = {}
# {mod: {leaf: [(owner, canonical, args), …]}} — EVERY distinct demand candidate for a leaf,
# application index included. More than one entry means the file genuinely uses two applications
# (or two definers) of a name; picking one silently is the miscompile this records to prevent.
_DEMAND_CANDS = {}


def _connect_catalog(tenant):
    """The store this resolver reads, in the tenant the CALLER STATES.

    ⚑⚑⚑ THE TENANT IS STATED, NOT READ FROM THE ENVIRONMENT (⟡tenant-mandatory, 2026-08-24).
    This function used to branch on `SUBSTRATE_SANDBOX=1` → `store.sandbox_connect()` else
    `catalog_db.connect()`, and defended the env var as *"a parameter here would put rehearsal
    plumbing in the production signature — this is a leaf."*

    ⚑⚑ THAT DEFENCE WAS REFUSED, AND THE REASON GENERALISES. Operator: *"this is EXACTLY why
    we have --dry vs --apply, --live vs --sandbox, and why those are REQUIRED parameters for
    any command that needs either."* Stating the tenant IS the production signature. Nobody
    argues that threading MUTATION INTENT through a leaf is rehearsal plumbing — a tool that
    mutates says so, and a tool that picks a store says which one. *Verification-only,
    therefore exempt* is exemption-for-the-uncovered-case, the loophole that swallows the rule.

    ⚑ AND THE BRANCH HAD ALREADY STOPPED MEANING WHAT IT SAID. The `catalog_db` arm reads as
    "the sqlite catalog", but `catalog_db.connect` is a RE-EXPORT of `store.connect`, and
    `store.connect` is `psycopg.connect` unconditionally — its own docstring records dropping
    the sqlite arm (*"there is no longer a file that can be absent"*). So both branches
    reached the SAME postgres store and this was a sandbox/live selector wearing sqlite's old
    clothes. This file was ported in the same arc: the fallback below still carries the note
    about fixing sqlite's `?` paramstyle and `con.execute` for psycopg. The env var is what
    the port left behind.

    `require=` is `store.tenant`'s own named-tenant interface — the caller states the tenant
    IN CODE where it is not the operator's to pick, which is what a resolver reading a fixed
    tenant is.
    """
    if tenant == "sandbox":
        return _store.sandbox_connect(reset=False)
    return _store.connect(label="scope_store")


def _event_refs(con, mod):
    """[(ref-qname, application-args)] from the EVENT TIER — positions intact.

    ⚑ ⟡resolver-event-tier. The SPPF PROJECTION (`_node`/`node_child`) cannot answer this: node
    identity is depth-1 `sym ‖ child-SYMS`, and `Cyclic.Base.insert` has the SAME sym applied at 1
    and at 2 — so in `node_child` BOTH `Lit 1` and `Lit 2` hang off EVERY argument position of BOTH
    calls (16,842 of 350,827 slots are packed this way). A resolver reading the projection is
    unsound BY CONSTRUCTION for any file that applies one parameterized module twice.

    `obs`/`edge` is the append-only truth with `UNIQUE(core_id, plid, ord)` — exactly one child per
    position. Walking it recovers each reference's OWN arguments, so the two carriers stay apart:
    `Cyclic.Base.insert ['Lit 1']` and `Cyclic.Base.insert ['Lit 2']` are separate facts.

    ⚑ READS THE `ref` INDEX, NOT `obs`/`edge` — AND THAT IS WHAT LIFTS THE RECLAMATION PIN.
    This walked the event tier row by row, which made `scope_fix` a persistent reader of the
    whole log: it is registered as a `pin`, holds `lwm` at 0 forever, and so the event tier
    can never drain by position. `ref` is a DERIVED index carrying the same positional fact
    — `(core_id, plid)` is each reference's OWN location, so two applications of one
    parameterized module stay apart, which `_node`'s content key cannot do — and being
    derived, it survives the drain that `obs` does not.

    ⚑ THE INDEX IS 195× SMALLER AND STILL SOUND: 380 reference rows against 74,223
    observations on a measured core. It is not a summary — it carries exactly the two facts
    this function needs (which qname, at which position, with which argument literals) and
    nothing it does not.

    ⚑ AND IT MUST `DISTINCT`, BECAUSE THE INDEX FANS OUT. `Apply` is not the only elim shape,
    so the builder's unconstrained walk emits a row per path — duplicates keyed identically
    on `(plid, arg_ord)`. Without the dedupe a two-argument reference reads as having five.
    """
    if not mod.startswith("Substrate."):
        return []
    # ⚑⚑ A LOOKUP, NOT A DERIVATION (ⓝ P4) — and this is a READ path, so it must NOT mint.
    # `core_id` used to be `_b64(relpath)`, so a module name could be turned into a core_id
    # with no store access at all. Under surrogates the map lives in `core_fp`, and a module
    # the store has never ingested has NO id — which is the honest answer here. Calling
    # `core_id_for` would MINT one and insert a `core_fp` row for a module with no rows,
    # manufacturing a core out of a resolver query.
    #
    # ⚑ AND AN UNKNOWN MODULE RETURNS `[]`, WHICH IS WHAT IT ALREADY MEANT. The caller reads
    # "no references found"; a module absent from the store genuinely has none indexed. This
    # is the one place where returning empty is a fact rather than a method artifact.
    #
    # ⚑ THE IMPORT IS HOISTED HERE BECAUSE THE LOOKUP NEEDS IT — it sat below, next to the
    # `rows()` call, which was fine while this line derived the id arithmetically and needed
    # no store at all. Turning a derivation into a lookup moves the store dependency EARLIER
    # in the function, and a local import below its first use is a `NameError`, not a style
    # question.
    import sys as _sys, os as _os
    _sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                      "..", "jea", "metalanguage"))
    import schema as _schema
    _relpath = mod[len("Substrate."):].replace(".", "/") + ".agdai"
    # ⚑⚑ `core_fp.path` IS GONE AND THIS WAS THE LAST READER OF IT (2026-08-11). The column
    # was added and removed again in the same arc (ⓟ): `_insert_decoded` writes
    # `cid = tid(relpath)`, so the path is ALREADY interned in `terms` under exactly this id,
    # and the column was a second copy of that fact. `core_path` was corrected to read
    # `terms`; this site was not, and it failed only once the SANDBOX was re-ingested from the
    # current declaration — `UndefinedColumn: column "path" does not exist`, in a suite that
    # had been reporting VACUOUS for an unrelated reason and so was hiding it.
    #
    # ⚑ THE JOIN IS THE NON-MINTING INVERSE OF `core_path`, AND BOTH HALVES ARE LOAD-BEARING.
    # `terms` alone answers "is this string interned", which is TRUE for any path the store
    # has ever seen in any role; joining `core_fp` narrows it to "this core is INGESTED",
    # which is what the note above demands. `core_id_for` is the wrong reuse here — it MINTS
    # on a miss, and this is a READ path, so it would manufacture a core out of a resolver
    # query for every un-ingested module.
    core = _schema.scalar(
        con,
        "SELECT f.core_id FROM core_fp f JOIN terms t ON t.term_id = f.core_id "
        " WHERE t.text = %s" % _schema.ph(), (_relpath,))
    if core is None:
        return []
    # ⚑ `nargs` STAYS HERE, DELIBERATELY. `_module_params(owner)` is a SOURCE lookup, not a
    # store fact, so the index carries argument POSITIONS and this decides how many to take.
    # Baking the slice into `ref` would freeze a judgement that changes when a module's
    # telescope changes — the index would silently rot against the tree.
    # ⚑ THROUGH THE SCHEMA AUTHORITY, NOT `con.execute` WITH A `?`. The replaced code wrote
    # sqlite's paramstyle inline, which psycopg rejects outright — so this reader could not
    # have run against the live store at all. `schema.rows`/`ph()` is the one contract that
    # spells the placeholder per backend.
    per_ref = {}
    for r in _schema.rows(
            con,
            "SELECT r.plid, p.text AS qname, r.arg_ord, t.text AS lit "
            "  FROM ref r "
            "  JOIN path_text p ON p.path_id = r.qname_pid "
            "  LEFT JOIN terms t ON t.term_id = r.arg_lit_id "
            " WHERE r.core_id = %s "
            " GROUP BY r.plid, p.text, r.arg_ord, t.text "     # the fan-out dedupe
            " ORDER BY r.plid, r.arg_ord" % _schema.ph(), (core,)):
        slot = per_ref.setdefault(r["plid"], [r["qname"], []])
        if r["arg_ord"] is not None:
            slot[1].append(r["lit"])
    out = []
    for _plid, (qname, lits) in per_ref.items():
        owner = _owner_of_ref(qname)
        nargs = len(_module_params(owner)) if owner else 0
        args = ""
        if nargs:
            take = lits[:nargs]
            # a non-literal parameter (a record, a family) is REAL but not writeable as an
            # application here — the same refusal the event walk made, on the same grounds.
            args = " ".join(take) if len(take) == nargs and all(take) else ""
        out.append((qname, args))
    return out


def _owner_of_ref(ref):
    """The longest prefix of a dotted ref that is an actual module file."""
    parts = ref.split(".")
    for i in range(len(parts) - 1, 0, -1):
        cand = ".".join(parts[:i])
        if os.path.exists(cand.replace(".", "/") + ".agda"):
            return cand
    return None


_FREE_CTORS = {"Def", "Con", "Proj", "PCon", "PDef", "PProj", "Prim", "PrimSort"}


def _demand_of(mod, tenant="live"):
    """{leaf: (owner, canonical-leaf)} — this module's ELABORATED reference set.

    ⚑ `tenant` IS THREADED, NOT READ FROM THE ENVIRONMENT (⟡tenant-mandatory). It defaults to
    `"live"` here and NOWHERE ELSE: this is a memoised read helper whose callers are the
    resolver's own internals, and a required parameter on an internal read would push the
    statement one layer further from the CLI that should own it rather than to it. The
    DEFAULT IS THE CORPUS because that is what this resolver reads in production — a default
    of `sandbox` would make a mistake silently answer from rehearsal data, which is the
    wrong-tenant failure `sql-F2` calls silent by construction.

    Read from catalog.db: what each definition actually referenced AFTER elaboration — conduit
    transport already skipped, definer's own spelling. Keyed by BOTH the canonical leaf and (below)
    any conduit spelling that renames to it, so a use site still written against the conduit
    resolves — and then gets rewritten to canonical.

    ⚑ The ARGUMENTS come from the EVENT tier (`_event_refs`), never the projection: the projection
    discards position and so cannot tell `Cyclic.Base 1` from `Cyclic.Base 2` inside one file. The
    projection query survives only as a fallback for cores the event walk cannot reach.
    """
    if mod in _DEMAND:
        return _DEMAND[mod]
    out = {}
    cands = {}
    _DEMAND_CANDS[mod] = cands
    try:
        con = _connect_catalog(tenant)
        import schema as _schema           # the placeholder/row authority, per backend
        refs = _event_refs(con, mod)
        if not refs:
            # ⚑ THE FALLBACK COULD NOT RUN ON POSTGRES AT ALL, and it is the safety net for
            # every core `ref` does not cover — so it matters most exactly when the primary
            # path is empty. Two defects in one statement, both found by `pycodemod
            # --portable` rather than by reading: sqlite's `?` paramstyle (psycopg rejects it
            # outright) and `con.execute` (psycopg puts `execute` on a CURSOR, not the
            # connection). Routed through the schema authority, which spells both per backend.
            #
            # ⚑ AND THE BARE `except Exception` BELOW IS WHY NOBODY NOTICED. A postgres
            # failure here was swallowed into "no demand for this module" — a wrong answer
            # that looks like a legitimate empty result. The handler now says which it means.
            # ⚑⚑ AND A THIRD DEFECT WAS IN THE SAME STATEMENT AND OUTLIVED BOTH: it read
            # `FROM unit u`, the compat VIEW, which ⟡view-purge drops (2026-08-12). Same
            # lesson as the paramstyle and the cursor, one level up — a site that spells its
            # own SQL is outside every layer that owns a spelling, so it collects one defect
            # per layer. `q_module_refs` composes the `unit` FRAGMENT and takes the prefix as
            # a bound parameter, so the `|| '.%%'` concatenation (a doubled-percent literal
            # inside a `%`-formatted string, itself a hazard) is gone with it.
            import query_builders as QB       # the read layer: compiled builders
            refs = [(r["ref"], "") for r in QB.run(con, "module_refs", likep=mod + ".%")]
    except Exception as _e:
        # ⚑ REPORTED, NOT SWALLOWED. "the store is unreachable" and "this module genuinely
        # demands nothing" are different facts with different repairs, and collapsing them
        # is the absent-read-as-empty defect this repo keeps paying for. The demand map is
        # still cached empty (the caller cannot proceed either way), but it SAYS so.
        print(f"  ⚠ demand_for({mod}): store read failed — {type(_e).__name__}: {_e}")
        _DEMAND[mod] = out
        return out
    for ref, ev_args in refs:
        if not ref.startswith("Substrate"):
            continue
        parts = ref.split(".")
        leaf = parts[-1]
        if leaf == "constructor" and len(parts) >= 2:
            leaf = parts[-2]
        owner = _owner_of_ref(ref)
        if owner:
            # `Mod._.leaf` — the `_` segment is an ANONYMOUS MODULE APPLICATION, i.e. a COPY, not
            # the definer (`Z3-Coxeter._.Gen` is Base's `Gen` seen through `Cyclic 2`). Such a copy
            # is OPAQUE in the store for a Datatype/Record/Constructor (418 units decode to
            # `Defn(Sort)` — no target, no argument), so the conduit's own statement is the only
            # remaining source. That fallback is the honest boundary, not the default path.
            inpath = parts[len(owner.split(".")):-1]
            cand = None
            if inpath and inpath[0] == "_":
                o, sname, a = _alias_binding(owner, leaf)
                if o:
                    cand = (o, sname, a, owner)
            if cand is None:
                # ⚑ the DIRECT-DEFINER case: the event tier already carried this reference's OWN
                # arguments, positionally. No chase, no text, no guess — `Cyclic.Base 1` and
                # `Cyclic.Base 2` arrive as two separate facts from one file.
                cand = (owner, leaf, ev_args, owner)
            # ⚑ THE CARRIER IS ALREADY IN THE CANONICAL REF PATH — DO NOT DISCARD IT.
            # `Z2-Coxeter._.Gen` and `Z3-Coxeter._.Gen` are DISTINCT elaborated qnames: the `_`
            # marks a copy through an application, and the CONDUIT PREFIX names which carrier it
            # is. Keying by the bare leaf `Gen` collapses the two and the file silently binds one
            # carrier's name at the other's index. Keep the conduit; a qualified use site then
            # matches its alias TARGET against it — derived from the SPPF, not scanned from text.
            # a conduit that passes its OWN parameter through (`Existential n` → `Base n`) fixes no
            # index: that is an UNKNOWN, not a carrier. Record it as such so it cannot masquerade
            # as a concrete application and cannot manufacture a false ambiguity.
            if cand[2] and cand[2] in _module_params(cand[3]):
                cand = (cand[0], cand[1], "", cand[3])
            cands.setdefault(leaf, [])
            if cand not in cands[leaf]:
                cands[leaf].append(cand)
            out.setdefault(leaf, cand[:2])
    # an index-less candidate is subsumed by a concrete one for the same owner: keeping both would
    # report a two-carrier ambiguity where the store actually named one carrier and one unknown.
    for leaf, cs in cands.items():
        concrete = {o for o, _c, a, _p in cs if a}
        if concrete:
            cs[:] = [c for c in cs if c[2] or c[0] not in concrete]
    # a use site may still be written against a CONDUIT spelling; map it onto the canonical one
    for tgt in _rename_index():
        if tgt in out:
            continue
        # ⚑ ⟡rename-index-arbitrary-carrier — RANKED/REFUSING, not the raw list. The
        # `break` below takes the FIRST record whose source is already demanded, so
        # among several carriers ORDER decided which spelling this target maps onto.
        # `rename_records` returns EMPTY when the records differ only by application
        # argument, and empty is exactly the right answer HERE: with no mapping, `out`
        # gains no entry for the conduit spelling, so the candidate list is never
        # narrowed to one carrier and the no-merge guard keeps the qualification —
        # which is precisely the collapse the ⚑ at :518 below calls "the fourth
        # instance of the same defect". Refusing is what PREVENTS it, not a new gap.
        for _sub, src, _a in rename_records(tgt):
            if src in out:
                out[tgt] = out[src]
                # ⚑ CARRY THE WHOLE CANDIDATE LIST ACROSS THE RENAME, not just the first. The
                # conduit spelling `Canonical` renames to `Canonical-ex`, which may be demanded at
                # TWO carriers; copying one candidate collapses them again and the no-merge guard
                # then sees a single carrier and de-qualifies. Fourth instance of the same defect.
                cands.setdefault(tgt, list(cands.get(src, [])))
                break
    _DEMAND[mod] = out
    return out


def audit_demand(paths, verbose=True):
    """⟡silent-miscompile-audit — compare a file's ACTUAL bindings against the SPPF's demand.

    The compiler cannot find this class. A file that binds `Gen` at `Cyclic.Base 1` where the
    elaborated demand says `Z3-Coxeter._.Gen` (= `Base 2`) is SELF-CONSISTENTLY WRONG: it
    typechecks, and only a downstream consumer fails — with an error naming neither the file nor
    the binding. The store is the only oracle that sees it, because the demand records what the
    definition ACTUALLY referenced when the tree last compiled.

    Reports, per file: leaf, the owner+args the demand implies, and the owner+args the source
    currently binds. A mismatch is a silent miscompile in waiting.
    """
    findings = []
    for path in paths:
        if not path.endswith(".agda") or not os.path.exists(path):
            continue
        mod = module_path(path, "")
        _demand_of(mod)
        src = open(path).read()
        for leaf, cands in sorted(_DEMAND_CANDS.get(mod, {}).items()):
            for owner, canon, args, conduit in cands:
                if not args or conduit == owner:
                    continue                      # no application to get wrong
                if args in _module_params(conduit):
                    continue                      # the conduit passes its OWN parameter through:
                                                  # `Existential n` fixes no index to contradict
                # what does the file actually apply this owner at, for this name?
                got = [a.strip() for m, a in
                       re.findall(r"^(?:open\s+)?import\s+(" + re.escape(owner)
                                  + r")(?![\w.-])([^\n]*?)(?:\s+as\s+[^\s;]+)?\s*$", src, re.M)]
                got = [g.split("using")[0].split("renaming")[0].strip() for g in got]
                got = [g for g in got if g]
                if got and args not in got:
                    findings.append((path, leaf, conduit, owner, args, got))
    if verbose:
        if not findings:
            print("demand-audit: no binding contradicts the SPPF")
        for path, leaf, conduit, owner, want, got in findings:
            print(f"  ⚠ {path}: `{leaf}` demand says {owner.rsplit('.', 1)[-1]} {want} "
                  f"(via {conduit.rsplit('.', 1)[-1]}) but source binds it at {got}")
    return findings


def _selftest():
    """⚑ THIS MODULE HAD NO SELFTEST, so `run_selftests` never saw it — and it REWRITES AGDA
    SOURCE. The reference reader was repointed from `obs`/`edge` to the `ref` index with no
    guard at all; the only verification was me running the same JOIN by hand in a probe,
    which tests my SQL rather than the function.

    ⚑ AND THIS IS THE CONSUMER THE RECLAMATION PIN EXISTS TO PROTECT. `scope_fix:resolver`
    holds `lwm` at 0 because it read the raw log; lifting that pin is safe exactly when this
    function returns the same references from `ref`. So "does `_event_refs` work" is not a
    tidiness question — it is the precondition for draining 6.3M observations.

    ⚑⚑ AND IT REPORTED `VACUOUS 0/0` FOR A REASON THAT WAS NOT `ref` BEING EMPTY (measured
    2026-08-11). The standing explanation — "`core_fp.path` is absent" — was half a diagnosis:
    that column EXISTS in the SANDBOX (`schema.py --probe`: core_id, path, mtime, producer) and
    is absent from the LIVE store (`schema.py --nullity core_fp`: core_id, mtime, producer,
    168 rows). This suite opens a SANDBOX connection and then handed `core_path` NO connection,
    so `core_path` fell through to `_cli_connect()` — the LIVE tenant — and raised
    `UndefinedColumn`, which the broad `except` below turned into a SKIP and a zero denominator.

    ⚑ A WRONG-TENANT READ IS SILENT BY CONSTRUCTION, which is exactly the recorded class: an
    argument-defaulted connection resolves to a DIFFERENT store than the one the caller is
    holding, and nothing in the call site says so. The fix is to pass the connection this
    function already has — one tenant per suite, named at the point of use.
    """
    _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
    import rungs
    check = rungs.Cases(key="scratch/scope_store.py")
    # ⚑ AN UNRUN CASE IS DECLARED, NOT INFERRED FROM A SMALL DENOMINATOR. `0/0` is
    # VACUOUS and stays so; what changes is that the three resolver cases now say
    # they were SKIPPED and why, instead of vanishing into an empty count.
    skipped, why = 0, []

    # ⚑ DRIVEN AGAINST THE SANDBOX, WHERE REHEARSAL DATA LIVES. The live store's `ref` is
    # empty (its qnames are still NULL pending the full re-ingest), so a live-store case
    # would assert nothing and pass — the shape this repo keeps paying for.
    #
    # ⚑⚑ STATED, NOT EXPORTED (⟡tenant-mandatory). This used to save `SUBSTRATE_SANDBOX`,
    # set it to "1", and restore it in a `finally`. Three problems that a parameter does not
    # have: the env var is PROCESS-GLOBAL, so it reached anything else this process touched;
    # the restore was a second thing that had to be right; and the tenant was invisible to
    # every census — `run_selftests --tenants` could see neither a flag nor a pragma here, so
    # this suite read as declaring nothing while genuinely opening a store (`gate-F23`).
    try:
        con = _connect_catalog("sandbox")
        import schema as _sc
        n_ref = _sc.scalar(con, "SELECT count(*) FROM ref")
        if not n_ref:
            skipped += 3
            why.append("sandbox `ref` is empty (run: sppf_db.py <FILTER> --full --sandbox)")
            print("  SKIP resolver cases — sandbox `ref` is empty "
                  "(run: sppf_db.py <FILTER> --full --sandbox)")
        else:
            # ⚑ THE SUBJECT IS DERIVED FROM THE STORE, NOT HARDCODED. This named
            # `…HodgeDim4.Bivector.AsExterior`, a module from the 30-core rehearsal that
            # happened to be loaded when the case was written. The next rehearsal ingested
            # a DIFFERENT filter (HodgeDim3, 14 cores), so `ref` was healthy — 2,618 rows
            # over 14 cores — and the case failed anyway, reporting the resolver broken
            # when the only thing wrong was the fixture's memory of which corpus was live.
            #
            # ⚑ AND THE SKIP COULD NOT CATCH IT: `ref` was non-empty, so the empty-store
            # guard correctly declined to fire. A fixture pinned to a value its own subject
            # legitimately changes reports a REGRESSION when the subject is fine — the
            # inverse of the empty-store pass this guard was added to prevent, and the same
            # defect from the other direction.
            # ⚑ THE SUBJECT IS THE *REFERENCING* CORE, NOT A REFERENCED QNAME. `_event_refs`
            # keys on `ref.core_id` (the module doing the referencing); my first derivation
            # took the most-cited `qname_pid`, which is the other end of the edge, and the
            # case kept failing on a resolver that was working. `ref` stores the core as the
            # b64 of its relative path, so invert exactly that to get the module name.
            _cid = _sc.scalar(con,
                "SELECT core_id FROM ref GROUP BY core_id "
                "ORDER BY count(*) DESC LIMIT 1")
            # `schema.core_path` is THE inverse of `_b64` and already exists — a second
            # decoder here would be the same-name-different-body class this repo has paid
            # for four times.
            # ⚑ `con` IS PASSED, AND ITS ABSENCE WAS THE WHOLE `VACUOUS 0/0`.
            # `core_path(core_id, con=None)` defaults to `_cli_connect()` — the LIVE
            # tenant — while this suite is deliberately holding the SANDBOX one. The
            # live `core_fp` predates the surrogate-id scheme and has no `path`
            # column, so the read raised and the whole suite skipped itself.
            mod = ("Substrate." +
                   _sc.core_path(_cid, con)[:-len(".agdai")].replace("/", ".")) if _cid else None
            refs = _event_refs(con, mod) if mod else []
            check("the resolver returns references from `ref`", bool(refs), True)
            # ⚑ EVERY REF MUST BE A SUBSTRATE QNAME — a malformed join would surface here as
            # empty strings or None, which `demand_for`'s `startswith` would silently skip.
            # [the sentence above is the ORIGINAL note, kept verbatim; the claim it makes is
            #  corrected immediately below rather than deleted, because the REASON the case
            #  exists — catching a malformed join — is still exactly right.]
            #
            # ⚑⚑ IT ASSERTED `startswith("Substrate.")` AND THAT IS A CLAIM ABOUT THE CORPUS,
            # NOT ABOUT THE JOIN — false for any core that touches an Agda builtin. MEASURED
            # on the sandbox the first time this suite ran with a populated `ref`: **7,951
            # `Substrate.*` rows and 154 `Agda.*` rows**, so the case failed on a resolver that
            # was working, exactly like the pinned-module defect recorded two comments up.
            #
            # ⚑ AND IT COULD NOT HAVE BEEN CAUGHT UNTIL NOW, WHICH IS THE FINDING. The suite
            # read `VACUOUS 0/0` for as long as the sandbox `ref` was empty — a green run in
            # which this line never executed. A case that has never run is not a passing case,
            # and the vacuity was reported (`state: vacuous`) rather than hidden, which is the
            # only reason the difference is legible now. `demand_for` filtering to `Substrate.`
            # downstream is a separate and correct act; the INDEX carries every reference.
            check("...each a well-formed dotted qname",
                  all(isinstance(q, str) and "." in q and not q.startswith(".")
                      for q, _a in refs),
                  True)
            # ⚑ AND THE FAN-OUT MUST BE DEDUPED. The index emits a row per elim path, so
            # without the GROUP BY a two-argument reference reads as having five.
            check("...with args deduped (no arg repeated within one reference)",
                  all(len(a.split()) == len(set(a.split())) or not a for _q, a in refs),
                  True)
        con.close()
    except Exception as e:                      # a store that cannot be reached is a FACT
        # ⚑ AND THE FACT IS NOW COUNTED. This printed a SKIP and left the suite at
        # `0/0` — vacuous, correctly, but with no reader able to tell WHY without
        # re-running by hand. The exception text rides in the record's `reason`.
        if not skipped:
            skipped += 3
        why.append("%s: %s" % (type(e).__name__, str(e).split("\n")[0]))
        print("  SKIP resolver cases — %s: %s" % (type(e).__name__, e))
    # ⚑ NO `finally` RESTORING AN ENV VAR ANY MORE — the tenant is an argument, so there is
    # no process-global state to put back and no second thing that has to be right. The
    # save/restore pair it replaced is the shape `deadlock-breakdown-before-any-fix` names:
    # the fix SUBTRACTS coordination rather than adding a careful version of it.

    return check.report(skipped=skipped, reason="; ".join(why) or None)


# ⚑ THE DISPATCH MOVES WITH THE FUNCTION, AND THE SPLIT PROVED WHY IT HAS TO.
# `run_selftests` discovers a suite by finding a module that DEFINES `_selftest`, then runs
# it with `--selftest` and reads the `selftest: N/M` line. Relocating `_selftest` here without
# its dispatch made `scope_store` a newly-discovered suite that printed nothing — reported as
# SILENT by the runner, MEASURED on the first full-suite run after the carve.
#
# That is precisely the defect this function's own neighbouring note records against
# `rewire_to_leaves` ("a `--selftest` flag wired to a function that did not exist"), arriving
# from the other direction: a function with no flag rather than a flag with no function. The
# lesson generalises past both — A SUITE IS THE PAIR, and moving one half across a file
# boundary breaks it exactly as surely as never writing the other half.
# selftest-tenant: sandbox
# ⚑ ⟡tenant-mandatory — `run_selftests._tenant` reads this and appends `--sandbox`. SANDBOX
# because the resolver cases are driven against rehearsal data by construction: the live
# store's `ref` is empty (qnames NULL pending the full re-ingest), so a live case would
# assert nothing and pass.
#
# ⚑⚑ AND THIS SUITE IS WHY THE PRAGMA COULD NOT BE WRITTEN UNTIL TODAY. `_connect_catalog`
# read `SUBSTRATE_SANDBOX` from the environment and `_selftest` exported it around the cases,
# so the tenant was chosen by a process-global neither `--tenants` lens could see — visible
# only as a call-site-lens DISAGREEMENT (`gate-F23`). The env var is gone; the tenant is an
# argument; and the declaration now describes what the code does rather than excusing it.
# ⚑ A `self` PRAGMA VALUE WAS BUILT FOR EXACTLY THIS SUITE AND BACKED OUT (`gate-F24`): a
# value meaning "I set my own" makes the bypass DECLARABLE, hence permanent, hence invisible
# to the census built to find it. The fix was to remove the bypass, not to name it.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    print(__doc__)
    sys.exit(0)
