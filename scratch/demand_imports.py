#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""⟡demand-imports — extrude a module's MINIMAL import block from the point-to-point demand.

catalog.db's `_node.op_path_id` records, per definition, the ELABORATED qname of everything it
references. Elaboration has already skipped conduit transport, so those qnames name DEFINERS with
their own spellings (`Canonical-ex`, `inv-left-canonical-ex`) — the answer an error-driven
resolver has to reconstruct one name at a time, and gets wrong whenever two modules export the
same name. Contracting that relation over a unit gives the minimal, direct point-to-point set.

Two things the raw qname does not settle, which this resolves:
  * COPIES — `Z3-Coxeter._.Gen` is a module-application copy, not a definer; `_alias_binding`
    reads the conduit's own statement to get the definer AND the application index.
  * LOCAL MODULES — `ListPresentation.WithLemmas.normalize-distrib` lives inside a local module;
    the importable owner is the file module that re-exports it.
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "jea", "metalanguage"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog_db
import schema as _schema                      # THE row/param contract: rows/ph, either driver
import query_builders as QB                   # THE read layer: compiled builders, no SQLAlchemy
import scope_fix as SF
import os as _o, sys as _s
_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from agda_imports import importable as _importable  # THE self-import predicate (never re-derive)

AGDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "agda")


def demand(unit_name, con):
    """Distinct elaborated Substrate refs of one definition.

    ⚑⚑ THIS IS THE SITE THAT BROKE THE WHOLE AGDA WRITE PATH, AND IT BROKE BY TYPING A
    PLACEHOLDER (⓺, 2026-08-11). It read `WHERE u.name = ?` and `con.execute(...)`, against
    a psycopg connection: `ProgrammingError: the query has 0 placeholders but 1 parameters
    were passed`. `demand_imports` is what `scope_fix` calls to extrude a module's minimal
    import block, so one hardcoded `?` took the ban-decompose loop — and with it the Agda
    tree — offline.

    ⚑ `ph()`'s OWN DOCSTRING PREDICTED THIS EXACT FAILURE AND THIS SITE NEVER CALLED IT:
    *"the fix is that a caller never types a placeholder, so there is no per-site chance to
    type the wrong one."* Removing `ph()`'s backend dispatch (⓺) fixes the sites that ROUTE
    through it; it cannot reach a site that spells `?` inline. Those are found by asking
    which SQL literals carry the retired paramstyle, not by fixing the helper.

    ⚑ AND `con.execute(...)` IS THE SECOND HALF, travelling with the first as it always
    does: sqlite3 puts `execute` on the CONNECTION, psycopg only on a CURSOR. `schema.rows`
    owns both — it yields name-keyed rows on either driver — so routing through it fixes
    the paramstyle and the cursor in one change rather than moving the failure one line.

    ⚑⚑ AND IT WENT DOWN THE SAME WAY A SECOND TIME (⟡view-purge, 2026-08-12), which is what
    finally moved it into the builder layer. The statement read `FROM unit u` — the compat
    VIEW — so dropping that view would have taken `scope_fix`'s import extrusion, and with it
    the Agda ban-decompose loop, offline at RUNTIME. Two outages, two different tokens
    (`?`, then a relation name), one cause: **a site that spells its own SQL is outside every
    layer that owns a spelling**, so each fix to the layer leaves it behind. `q_demand_refs`
    composes the `unit` FRAGMENT, so paramstyle, cursor and relation are all the layer's
    problem now and none of them is typed here.

    ⚑ THE CENSUS THAT FOUND IT IS WORTH NAMING: `query_defs --touching unit` reports this
    site NOWHERE — it models DECLARED builders and this was a hand-written string. It took
    `pycodemod --relname unit`, which reads SQL by GRAMMAR POSITION, to see it.
    """
    return [r["ref"] for r in QB.run(con, "demand_refs", name=unit_name)
            if r["ref"].startswith("Substrate")]


def file_module(qname):
    """Longest prefix of `qname` that is a real .agda file module, plus the remaining path."""
    parts = qname.split(".")
    for i in range(len(parts) - 1, 0, -1):
        cand = ".".join(parts[:i])
        if os.path.exists(os.path.join(AGDA, cand.replace(".", "/") + ".agda")):
            return cand, parts[i:]
    return None, parts


def resolve(ref, ctx_alias, idx=""):
    """ref → (owner, leaf, args).

    The demand relation says WHAT is needed and in whose spelling; the conduit's own binding
    statement says WHERE to bind it and at which application. Ask the conduit first: it maps a
    local-module or applied re-export (`ListPresentation.normalize`) onto the importable owner
    (`Cyclic.Existential n`), which the bare qname cannot.
    """
    mod, rest = file_module(ref)
    if not mod:
        return None
    leaf = rest[-1]
    if leaf == "constructor" and len(rest) >= 2:
        leaf = rest[-2]
    if ctx_alias:
        o, s, a = SF._alias_binding(ctx_alias, leaf)
        if o and (o == mod or not SF._module_exports(mod, leaf) or SF._module_params(mod)):
            return o, s, (a or (idx if SF._module_params(o) else ""))
    args = ""
    if SF._module_params(mod):
        o, s, a = (SF._alias_binding(ctx_alias, leaf) if ctx_alias else (None, None, ""))
        # the carrier index IS the witness's identity; the demand relation already fixed WHICH
        # module, so an owner in the parameterized family takes the context index, not a guess.
        args = (a if o == mod and a else idx)   # mod is parameterized (checked above)
    return mod, leaf, args


def renames(ctx_alias):
    """conduit target → canonical source, for rewriting a body onto canonical names."""
    out = {}
    if not ctx_alias:
        return out
    for text in (SF._module_text(ctx_alias)[0], SF._head_text(ctx_alias)):
        for _sub, stmt in SF._open_stmts(text or ""):
            for src_name, tgt in SF._rename_pairs(stmt):
                out.setdefault(tgt, src_name)
    return out


def block(unit_name, ctx_alias, con, idx=""):
    """The minimal import block: one line per (owner, application), names merged."""
    groups, unresolved = {}, []
    for ref in demand(unit_name, con):
        r = resolve(ref, ctx_alias, idx)
        if not r:
            unresolved.append(ref); continue
        owner, leaf, args = r
        if owner == unit_name.rsplit(".", 1)[0]:
            continue                                   # self-reference
        groups.setdefault((owner, args), set()).add(leaf)
    # ⚑ CANONICAL ONLY. catalog.db's elaborated qname IS the canonical name; re-issuing the
    # conduit's rename would bind its non-canonical spelling and inherit that conduit's rename
    # blast radius. The import block stays canonical and `renames()` rewrites the BODY onto it.
    lines, by_owner = [], {}
    for (owner, args), names in sorted(groups.items()):
        exported = sorted(n for n in names if SF._module_exports(owner, n))
        missing = sorted(n for n in names if n not in exported)
        for n in missing:
            # a LOCAL-module name (`ListPresentation.WithLemmas.normalize-distrib`) is not
            # importable at its own file module. It is importable at whichever module re-exports
            # it — and that module is already IN this block, because the same definition also
            # demanded siblings from it. Merge rather than guess.
            host = next(((o2, a2) for (o2, a2) in groups
                         if (o2, a2) != (owner, args) and SF._module_exports(o2, n)), None)
            if host:
                by_owner.setdefault(host, set()).add(n)
            else:
                unresolved.append(f"{owner}.{n} (no demanded owner exports it)")
        if exported:
            by_owner.setdefault((owner, args), set()).update(exported)
    for (owner, args), names in sorted(by_owner.items()):
        lines.append(f"open import {owner}{' ' + args if args else ''} "
                     f"using ({'; '.join(sorted(names))})")
    return lines, unresolved


if __name__ == "__main__":
    con = catalog_db.connect()
    unit = sys.argv[1]
    alias = sys.argv[2] if len(sys.argv) > 2 else None
    lines, un = block(unit, alias, con, sys.argv[3] if len(sys.argv) > 3 else "")
    print(f"── minimal import block for {unit}" + (f"  [ctx {alias}]" if alias else ""))
    for l in lines: print("  " + l)
    if un:
        print("── unresolved (needs a decision, not a guess):")
        for u in un: print("  ! " + u)
