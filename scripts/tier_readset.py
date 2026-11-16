#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""tier_readset.py — ⒣ THE TIER READ-SET GATE.

    For each tier, its RETIRE predicate's read set must contain nothing at or below
    the tier it writes.

⚑⚑ WHY THIS IS A GATE AND NOT A REPORT. Deadlock-freedom in the ladder is a THEOREM,
not a discipline: *"every retire reads strictly UP and writes DOWN, so the tier order
is well-founded and the acquisition order is globally consistent — not because anyone
maintains that discipline, but because what the predicate is permitted to READ entails
it"* ([[deadlock-breakdown-before-any-fix]]). The theorem has exactly one hypothesis,
and a same-tier-or-below read in a retire predicate is the one thing that discharges
it wrongly. That hypothesis has now been found violated BY HAND twice:

  * **F10** — `terms`/`path_seg`/`path_text` declared in the EVENT tier while
    `_node`/`_unit`/`ref` hold ids into them, so `_rebuilt_obs` joined `terms` ×3 and
    read the tier it writes. Filed as a data-loss hazard; it is also a
    deadlock-freedom hazard.
  * **❶ (2026-08-13)** — `roots_sql` found a document root by joining `dec_ref`
    (disposable) to `core_decoded` (**the tier being retired**). Both inputs vanish in
    the drain. Caught by an agent reading the code, not by any gate.

MVCC masks both today (snapshot reads do not block), which is exactly why the property
needs a gate: the guarantee is supposed to rest on the STRUCTURE, not on postgres being
forgiving. **A property whose only enforcement is that someone notices is not enforced.**

⚑⚑ THE TIER ORDER IS HELD TWICE, ON PURPOSE, AND THE VERDICT IS THE DIFFERENTIAL. This
file first shipped (⒣, 2026-08-13) DERIVING the order from the retire statements, because
the order was declared NOWHERE: `schema_decl._TIERS` is the MEMBERSHIP authority and its
own note refused to be the order while claiming to be it, and the chain it pointed at
(`lifecycle.LIFECYCLE`) orders the stages of a DATUM, not the tiers of a store. Each
retire declares its own constraint — `tier(write) < tier(read)` — so the union of those
edges IS an order, derived; a **self-loop** is a same-tier read and a **cycle** is an
at-or-below read.

⚑⚑ THAT WAS SOUND AND IT WAS ALSO THE CEILING: **A DERIVED ORDER CANNOT BE WRONG, SO IT
CANNOT DETECT A WRONG ONE.** The derivation is self-consistent by construction — it
catches CYCLES and it cannot catch MIS-TIERING, and a retire reading a genuinely lower
tier that no retire relates in either direction closes no cycle and PASSES. Fixed by
DECLARING the order (`schema_decl.TIER_BELOW`, 2026-08-13, ⒦) and asserting that the two
readings agree: agreement is the common mode, and any disagreement is residue naming a
real defect. **BOTH SURVIVE.** Deleting the derivation and trusting the declaration would
swap one self-consistent reading for another and lose the differential entirely.

⚑ THE DECLARATION IS PAIRS, NOT A ROSTER — the bad move this file refused in ⒣ was *"add
a `TIER_ORDER` roster"*, the second-roster shape `_TIER_VIEWS` was deleted for, and it
still is: `TIER_BELOW` enumerates `(lower, higher, why)` PAIRS, so it duplicates no name
list and asserts no total order where the truth is partial. A tier related by no pair is
unordered, and `blind()` counts the unordered pairs into the printed verdict.

⚑ THE FIVE RULES. `R1` (same tier) is the property as stated and is technically a special
case of `R3` (cycle) — kept apart because it is the one the memory names and it deserves
its own sentence in the refusal. `R2` (the read is a relation some retire DELETES) is the
half of ❶ that `R1`/`R3` do NOT catch: a shadow reading `dec_ref` names a tier that is
neither the writer's own nor below it in the retire graph, yet *"both inputs vanish in the
drain"* all the same. `R4` is the DECLARED order contradicting the derivation, and `R5` is
a retire relating a pair the declaration does not.

⚑⚑ AND R4 IS TWO THINGS THAT TURNED OUT TO BE ONE PREDICATE, WHICH IS THE ⒦ FINDING.
*"the retire reads a tier the DECLARATION puts below it"* (the hole-closer) and *"DECLARED
and DERIVED disagree"* (the differential) are both `(read_tier, write_tier) ∈ declared` —
not two rules that happen to coincide. The declared order closes the derivation's blind
spot precisely BY being the thing it can disagree with.

⚑ WHAT THIS FILE IS NOT. It is a CALLER, not a rung — `pycodemod --control` is expected
to be non-zero here, exactly as it is for `query_defs.py` and `scripts/sppf_drain.py`.
It adds no rung and no statement; `jea/metalanguage/dec_drain.py` stays at `--control` 0.

⚑ IT LIVES IN `scripts/` AND NOT IN `jea/metalanguage/` BY A MEASURED CONSTRAINT, not by
taste: `check_scratch_independence` (Λ8) forbids a promoted project (`jea/`, `el-atlas/`)
from making a LIVE reference to `scratch/`, and the SQL read/write split this gate is
built on is `scratch/_pycodemod_sql.sql_rw` — the tool that owns SQL-inside-Python.
`scripts/ → scratch/` is the established direction (`run_selftests` states it).

⚑ IT NEEDS NO DATABASE, AND THAT IS A PROPERTY WORTH KEEPING. Every input is a
declaration or a compiled statement: `_TIERS`, `SHADOWS` compiled through
`store.dialect()` (which builds a dialect object and opens nothing), and the rung
modules' own `*_sql()` accessors. A gate over the ladder that had to touch the store
could not run while the ladder was building — which is precisely when it matters.

Usage: tier_readset.py [--census] [--order] [--check] [--selftest]
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scratch"))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))

RUNG_DIR = os.path.join(ROOT, "jea", "metalanguage")

#: Where a statement's relations come from, and the ONE reader for them.
# ⚑ NOT A SECOND LEXER. `sql_rw` is `--relname`'s grammar-position walker with the
# read/write split; `sql_kind` is its depth-aware statement head. Both were added to
# the tool that owns the artifact rather than inlined here, which is why this file
# holds no SQL parsing of its own.
from _pycodemod_sql import sql_kind, sql_rw  # noqa: E402


# ── (1) THE POPULATION — DISCOVERED FROM THE RUNG LAYER, never listed ────────────────
#
# ⚑⚑ THE ACCESSOR CONVENTION IS THE RUNG'S DECLARED INTERFACE, so it is what the
# discovery reads. Every statement in `dec_drain` / `dec_tree` is reached by a
# `*_sql()` returning `(sql, params)`; the raw module-level templates cannot be read
# directly (they carry `%s` and `%%s` placeholders in relation position, so
# `sql_sites`'s parse probe rejects them — MEASURED: `--relname core_decoded
# dec_drain.py` returns 1 site out of five statements that name it). The COMPOSED
# statement is the thing the engine runs and the only thing a read-set can be taken of.
#
# ⚑ A ROSTER OF MODULES WOULD BE THE DEFECT THIS REPO KEEPS PAYING FOR — `DIRS` in
# `run_selftests`, `_TIER_VIEWS`, `LEGACY_BASELINE`. A rung module is discovered: it is
# a `.py` under the metalanguage dir defining at least one top-level `*_sql` whose
# parameters ALL have defaults (i.e. it composes with no caller state).
def accessors(path):
    """[name] — top-level `*_sql` defs in `path` callable with no arguments."""
    import ast

    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    except (OSError, SyntaxError):
        return []
    out = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.endswith("_sql") or node.name.startswith("_"):
            continue
        a = node.args
        required = len(a.posonlyargs) + len(a.args) - len(a.defaults)
        if required == 0 and not a.kwonlyargs:
            out.append(node.name)
    return sorted(out)


def rung_modules():
    """[(module_name, path, [accessor])] — every metalanguage module that emits SQL."""
    out = []
    for fn in sorted(os.listdir(RUNG_DIR)):
        if not fn.endswith(".py"):
            continue
        p = os.path.join(RUNG_DIR, fn)
        got = accessors(p)
        if got:
            out.append((fn[:-3], p, got))
    return out


def statements():
    """[(module, accessor, kind, sql)] and [(module, accessor, why)] — composed, unread.

    ⚑ AN IMPORT OR COMPOSE FAILURE IS RETURNED, NEVER SWALLOWED. A module this gate
    cannot compose is a HOLE in its coverage, and a hole reported as an empty result is
    the *fact-about-the-method-read-as-a-fact-about-the-substrate* error the standing
    rule names. The caller prints them; `check` counts them.
    """
    got, holes = [], []
    for mod, _path, names in rung_modules():
        try:
            m = __import__(mod)
        except Exception as e:  # noqa: BLE001
            holes.append((mod, "*", "import failed: %s: %s" % (type(e).__name__, e)))
            continue
        for nm in names:
            try:
                sql = getattr(m, nm)()[0]
            except Exception as e:  # noqa: BLE001
                holes.append((mod, nm, "compose failed: %s: %s" % (type(e).__name__, e)))
                continue
            if not isinstance(sql, str):
                holes.append((mod, nm, "accessor did not return (sql, params)"))
                continue
            got.append((mod, nm, sql_kind(sql), sql))
    return got, holes


# ── (2) THE TIER MAP, AND THE VIEW EXPANSION THAT IS THE WHOLE OF ❶ ──────────────────
#
# ⚑⚑ WITHOUT VIEW EXPANSION THIS GATE WOULD HAVE PASSED ❶'s DEFECT. The live retire
# reads exactly one relation — `core_decoded_shadow` — and a shadow is not in any tier,
# so an unexpanded reader sees a read set of one unknown name and nothing to compare.
# The violation lives in the shadow's BODY: had it been defined the way `roots_sql`
# derived a root (join `dec_ref` to `core_decoded`), the expansion would carry
# `core_decoded` — the relation the DELETE writes — into the read set. The view is
# where the defect hides, so the view is what must be opened.
def tier_of_relation():
    """`{relation: tier}` — inverted from `schema_decl._TIERS`, the MEMBERSHIP authority."""
    import schema_decl as D

    return {r: t for t, rels in D._TIERS.items() for r in rels}


def shadow_bases():
    """`{view: {base relation}}` — each declared shadow's body, read for its relations.

    ⚑ THE BODY IS COMPILED, NOT RE-DERIVED. `schema_decl.view_ddl` is the one emitter
    of a shadow's SQL and is what the store actually gets; taking the relations off a
    second rendering would let the gate and the deployment disagree about what the
    predicate reads — which is the drift `--check` gates elsewhere in this repo.
    """
    import schema_decl as D

    out = {}
    for name in D.SHADOWS:
        ddl = D.view_ddl("postgres", want={name})[0]
        # `CREATE OR REPLACE VIEW <n> AS <body>` — the view's own name is its write
        # target, not something it reads.
        w, r = sql_rw(ddl)
        out[name] = set(r) - {name}
    return out


def expand(rels, views, seen=None):
    """`(base relations, unresolved)` — every read, with declared views opened.

    Recursive, because a shadow over a shadow is the shape the model predicts (*"the
    `sourced` shadow is the FIRST of a CHAIN of shadows, one per reconstructible
    tier"*), and `seen` is what keeps a mutually-referential declaration from looping
    rather than a depth cap that would silently truncate the read set.
    """
    seen = set() if seen is None else seen
    base, unres = set(), set()
    for r in rels:
        if r in views:
            if r in seen:
                continue
            seen.add(r)
            b, u = expand(views[r], views, seen)
            base |= b
            unres |= u
        else:
            base.add(r)
    return base, unres


# ── (3) THE RULES ────────────────────────────────────────────────────────────────────
RULES = {
    "R1": "a RETIRE predicate reads a relation in the tier it writes (same tier)",
    "R2": "a RETIRE predicate reads a relation that a RETIRE deletes — "
    "both inputs vanish in the drain",
    "R3": "the retire graph has a CYCLE, so a read is at or BELOW the tier written",
    "R4": "the DECLARED order (`schema_decl.TIER_BELOW`) puts the read BELOW the write — "
    "and the retire graph, read alone, entails the opposite: DECLARED and DERIVED "
    "DISAGREE, and the disagreement is a downward read",
    "R5": "a retire relates two tiers that `schema_decl.TIER_BELOW` relates in NEITHER "
    "direction — the statements entail an order the declaration does not carry",
}


def _cycles(edges):
    """[[tier, …]] — every elementary cycle in `{tier: {tier}}`, as a stable list."""
    out, path, onpath = [], [], set()

    def walk(u):
        path.append(u)
        onpath.add(u)
        for v in sorted(edges.get(u, ())):
            if v in onpath:
                out.append(path[path.index(v) :] + [v])
            elif v not in seen:
                walk(v)
        path.pop()
        onpath.discard(u)

    seen = set()
    for n in sorted(edges):
        if n not in seen:
            walk(n)
            seen |= onpath | {n}
            seen.add(n)
        seen.add(n)
    return out


def declared_below(pairs=None, known=None):
    """`({(lower, higher)}, {(lower, higher): why})` — the DECLARED order, closed.

    ⚑⚑ THIS IS THE HALF THE GATE DID NOT HAVE, AND WITHOUT IT THE GATE HAD A CEILING IT
    COULD NOT SEE PAST. Everything above derives the order from the retire statements, which
    is sound and is exactly the problem: *a derived order cannot be WRONG, so it cannot
    detect a wrong one.* The derivation is self-consistent by construction — it catches
    CYCLES and cannot catch MIS-TIERING, and a retire reading a genuinely lower tier that no
    retire relates in either direction closes no cycle and PASSES.

    `schema_decl.TIER_BELOW` is the second, independent reading: a human declaration with a
    WITNESS per pair. The gate now holds two facts arrived at by different routes, and the
    judgement is the DIFFERENTIAL between them — agreement is the common mode, disagreement
    is residue naming a defect (R4/R5). ⚑ THE DERIVATION IS NOT REPLACED. Trusting the
    declaration alone would swap one self-consistent reading for another and lose the
    differential entirely; both survive, and R3 still fires on a cycle the declaration
    happens not to mention.

    ⚑ IT RAISES RATHER THAN REPORTING on a malformed declaration — an unknown tier name or a
    declared cycle. That is `schema_decl._tier`'s own stance (*"REFUSE an unknown tier rather
    than defaulting"*, because a typo'd tier silently applied the wrong one and reported
    success). A broken declaration is not a ladder defect the gate should rank alongside a
    downward read; it is the gate's own input being unreadable.

    `pairs`/`known` are parameters for the reason the population is: a case must be able to
    drive a WRONG declaration and see the refusal.
    """
    import schema_decl as D

    pairs = D.TIER_BELOW if pairs is None else pairs
    known = set(D._TIERS) if known is None else set(known)
    why, dedges = {}, {}
    for lo, hi, w in pairs:
        for t in (lo, hi):
            if t not in known:
                raise ValueError(
                    "TIER_BELOW relates %r, which is not a declared tier; known: %s"
                    % (t, sorted(known))
                )
        why[(lo, hi)] = w
        dedges.setdefault(lo, set()).add(hi)
    cyc = _cycles(dedges)
    if cyc:
        raise ValueError(
            "TIER_BELOW is not an order — it declares a cycle: "
            + "; ".join(" < ".join(c) for c in cyc)
        )
    # ⚑ CLOSED TRANSITIVELY BECAUSE THE DECLARATION LISTS GENERATING PAIRS, NOT THE ORDER.
    # `a < b` and `b < c` must refuse a retire of `c` reading `a` even though nobody wrote
    # that pair down — otherwise the declaration would have to be quadratic to be useful,
    # and a quadratic declaration is one nobody keeps correct.
    rel = set(why)
    grew = True
    while grew:
        grew = False
        for a, b in sorted(rel):
            for c, d in sorted(rel):
                if b == c and (a, d) not in rel:
                    rel.add((a, d))
                    grew = True
    return rel, why


def analyse(stmts, tiers, views, declared):
    """`(violations, edges, unknown)` — the whole judgement, over an INJECTED population.

    ⚑⚑ THE POPULATION IS A PARAMETER SO A CASE CAN DRIVE IT. A gate whose input is
    always the live tree can only ever be observed PASSING, and *"a gate never observed
    to refuse has not been shown to be a gate"*. `_selftest` hands it ❶'s actual
    `roots_sql` shape and F10's same-tier join and asserts the refusal, naming the
    offending relation and its tier.

    ⚑ `declared` IS `declared_below()`'s pair, AND IT IS REQUIRED RATHER THAN DEFAULTED to
    the live declaration — for the same reason. A gate whose declaration is always the live
    one can only ever be observed AGREEING with it, and the whole point of holding two
    independent readings is to be able to drive them apart and see the refusal.
    """
    dec_rel, dec_why = declared
    retire_targets = set()
    for _m, _a, kind, sql in stmts:
        if kind == "delete":
            retire_targets |= sql_rw(sql)[0]

    violations, edges, unknown = [], {}, set()
    for mod, acc, kind, sql in stmts:
        if kind != "delete":
            continue
        writes, reads = sql_rw(sql)
        base, _unres = expand(reads, views)
        for w in sorted(writes):
            wt = tiers.get(w)
            if wt is None:
                unknown.add(w)
                continue
            for r in sorted(base):
                rt = tiers.get(r)
                if rt is None:
                    unknown.add(r)
                    continue
                if rt == wt:
                    violations.append(
                        (
                            "R1",
                            mod,
                            acc,
                            w,
                            wt,
                            r,
                            rt,
                            "the DELETE writes tier %r and the predicate reads %r, "
                            "which is in that same tier" % (wt, r),
                        )
                    )
                    continue
                if r in retire_targets:
                    violations.append(
                        (
                            "R2",
                            mod,
                            acc,
                            w,
                            wt,
                            r,
                            rt,
                            "the predicate reads %r (tier %r), which a retire DELETEs — "
                            "the licence is drained with the thing it licenses" % (r, rt),
                        )
                    )
                # ⚑⚑ R4 AND R5 ARE THE DIFFERENTIAL, AND R4 IS ALSO THE HOLE-CLOSER —
                # THESE TURNED OUT TO BE THE SAME PREDICATE, WHICH IS THE FINDING. A
                # "derived edge" IS a retire writing `wt` and reading `rt`; so *"the
                # declaration contradicts the derivation"* and *"the retire reads a
                # DECLARED-lower tier"* are not two rules that happen to agree — they are
                # one condition, `(rt, wt) in dec_rel`, spelled twice. The declared order
                # closes the derivation's blind spot by BEING the thing it disagrees with.
                if (rt, wt) in dec_rel:
                    violations.append(
                        (
                            "R4",
                            mod,
                            acc,
                            w,
                            wt,
                            r,
                            rt,
                            "DECLARED: %r < %r — %s. DERIVED: this retire writes %r and reads "
                            "%r, which entails %r < %r. The two disagree, and the direction of "
                            "the disagreement is a DOWNWARD read."
                            % (
                                rt,
                                wt,
                                dec_why.get((rt, wt), "entailed transitively by TIER_BELOW"),
                                wt,
                                rt,
                                wt,
                                rt,
                            ),
                        )
                    )
                elif (wt, rt) not in dec_rel:
                    violations.append(
                        (
                            "R5",
                            mod,
                            acc,
                            w,
                            wt,
                            r,
                            rt,
                            "DERIVED: this retire entails %r < %r. DECLARED: nothing — "
                            "`schema_decl.TIER_BELOW` relates %r and %r in neither direction, "
                            "so the at-or-below rule cannot fire on this pair. Declare it with "
                            "its witness." % (wt, rt, wt, rt),
                        )
                    )
                edges.setdefault(wt, set()).add(rt)

    for cyc in _cycles(edges):
        violations.append(
            (
                "R3",
                "-",
                "-",
                "-",
                cyc[0],
                "-",
                cyc[-1],
                "the retire graph closes a cycle: " + " → ".join(cyc),
            )
        )
    return violations, edges, unknown


def order(edges):
    """The DERIVED tier order, lowest first — a topological sort of the retire graph.

    ⚑ A PARTIAL ORDER, REPORTED AS ONE. Tiers with no retire edge between them are
    genuinely unordered by this construction and are printed in the layer they fall in;
    presenting a total order would invent precedence the declarations do not carry.
    Returns `None` when the graph is cyclic — there is no order to report, and that is
    the R3 violation rather than something to linearise past.
    """
    nodes = set(edges) | {v for vs in edges.values() for v in vs}
    indeg = {n: 0 for n in nodes}
    for u in edges:
        for v in edges[u]:
            indeg[v] += 1
    layers, left = [], dict(indeg)
    while left:
        cur = sorted(n for n, d in left.items() if d == 0)
        if not cur:
            return None
        layers.append(cur)
        for n in cur:
            for v in edges.get(n, ()):
                if v in left:
                    left[v] -= 1
            del left[n]
    return layers


def check(stmts=None, declared=None):
    """`(violations, edges, unknown, holes, declared)` — the judgement over the live tree."""
    holes = []
    if stmts is None:
        stmts, holes = statements()
    if declared is None:
        declared = declared_below()
    v, e, u = analyse(stmts, tier_of_relation(), shadow_bases(), declared)
    return v, e, u, holes, declared


# ── (4) WHAT THIS GATE CANNOT SEE — printed with every verdict, never inferred ───────
#
# ⚑⚑ A GREEN RESULT MUST NOT BE READ AS COVERAGE. Each line below is a spelling through
# which a retire predicate could reach a relation this reader misses; none is
# hypothetical — every one is a shape that exists somewhere in this corpus's history.
BLIND = (
    "a table name built at RUNTIME (an f-string, a `%s` in RELATION position, a name "
    "passed as a parameter) — `sql_rw` is a positional lexer over a literal, so a "
    "computed relation names nothing it can find",
    "a statement reached by a spelling other than a no-argument `*_sql()` accessor on a "
    'module under jea/metalanguage — a raw `con.execute("DELETE …")` in a caller is '
    "outside this population by construction",
    "a POSTGRES VIEW that is not a declared `schema_decl.SHADOWS` entry: the expansion "
    "opens declared shadows only, so a view created by a migration reads as an unknown "
    "relation (reported under `unknown`, never silently as a tier)",
    "`DELETE … USING t` / `MERGE`: `USING` terminates the relation list, so `t` is "
    "invisible. Nothing in this corpus uses either; a future one would be missed",
    "a relation genuinely NAMED like a SQL keyword (`set`, `values`) — `_REL_END` is a "
    "frozen roster and this is its stated cost",
    "anything a rung module could not be IMPORTED or COMPOSED for — counted as a hole "
    "and named, because an unimported module contributes an empty read set that looks "
    "exactly like a clean one",
)


def blind(tiers, declared):
    """The blind spots AS PRINTED — the six static ones, plus the declaration's residue.

    ⚑⚑ THE SEVENTH WAS THE SHARPEST AND WAS NOT IN THE LIST. `BLIND` above held six, and
    the gate's own plan and the memory both called the weakness it omitted *"the sharpest
    one"*: **a retire reading a genuinely-lower tier that no retire relates in either
    direction closes no cycle and passes.** It was written in a plan file and in a memory —
    i.e. in exactly the two places a future reader of a GREEN verdict does not look. A gate
    that prints its blind spots so that green is never read as coverage was not printing its
    largest one, which is the same defect one level up.

    ⚑ IT IS COMPUTED AND NOT A STRING because after `TIER_BELOW` the hole is no longer a
    yes/no — it is exactly the set of tier pairs the declaration leaves unordered, and that
    is a NUMBER that moves when someone declares a pair. A prose hole cannot be paid down
    visibly; a counted one can.
    """
    names = sorted(set(tiers.values()))
    total = len(names) * (len(names) - 1) // 2
    rel = {frozenset(p) for p in declared[0] if p[0] != p[1]}
    return BLIND + (
        "a retire reading a genuinely LOWER tier that `schema_decl.TIER_BELOW` does not "
        "relate: %d of %d tier pairs are declared, so R4 cannot fire on the other %d. This "
        "is the one the DERIVED order can never see — a derived order cannot be wrong, so "
        "it cannot detect a wrong one — and it shrinks only by declaring a witnessed pair."
        % (len(rel), total, total - len(rel)),
    )


def _print(violations, edges, unknown, holes, declared, quiet=False):
    for mod, acc, why in holes:
        print("  HOLE      %s.%s — %s" % (mod, acc, why))
    if unknown:
        print(
            "  UNKNOWN   %d relation(s) in no declared tier and no declared shadow: %s"
            % (len(unknown), ", ".join(sorted(unknown)))
        )
    for rule, mod, acc, w, wt, r, rt, why in violations:
        print("  %s VIOLATION  %s.%s" % (rule, mod, acc))
        print("      writes  %s  (tier %s)" % (w, wt))
        print("      reads   %s  (tier %s)" % (r, rt))
        print("      %s" % why)
        print("      rule: %s" % RULES[rule])
    lay = order(edges)
    if not quiet:
        rel, dwhy = declared
        # ⚑ BOTH READINGS ARE PRINTED, SIDE BY SIDE, AND NEITHER IS PRESENTED AS THE
        # ANSWER. The verdict is the DIFFERENTIAL between them; a reader who sees only one
        # is back at a self-consistent check.
        print(
            "  tier order (DECLARED, schema_decl.TIER_BELOW — %d relation(s), closed): " % len(rel)
            + ",  ".join("%s < %s" % p for p in sorted(rel))
        )
        if lay is None:
            print("  tier order: NONE — the retire graph is cyclic (see R3 above)")
        else:
            print(
                "  tier order (DERIVED from the retire graph, lowest first): "
                + "  <  ".join("{" + ", ".join(l) + "}" for l in lay)
            )
        direct = {(u, v) for u in edges for v in edges[u]}
        # ⚑ A DECLARED RELATION NO RETIRE WITNESSES IS REPORTED AND IS NOT A FAILURE. The
        # declaration is ALLOWED to be stronger than the retire graph — that is the whole
        # reason it exists: R4 fires on a pair the derivation could never relate. Refusing
        # here would forbid declaring anything before a retire needs it, i.e. would forbid
        # closing the hole in advance.
        unwit = sorted(p for p in dwhy if p not in direct)
        print(
            "  DECLARED vs DERIVED: %d derived edge(s), %d entailed by the declaration; "
            "%d declared relation(s) no retire witnesses%s"
            % (
                len(direct),
                sum(1 for p in direct if p in rel),
                len(unwit),
                (" — " + ", ".join("%s < %s" % p for p in unwit)) if unwit else "",
            )
        )
        print("  ⚑ WHAT THIS GATE CANNOT SEE — a green result is not coverage:")
        for b in blind(tier_of_relation(), declared):
            print("      · " + b)


# ── (5) THE CASES — the gate SHOWN REFUSING before it is shown passing ───────────────
def _fixtures():
    """The two violations that were found BY HAND, as statement populations.

    ⚑⚑ ❶'s SHAPE IS REPRODUCED, NOT INVENTED. `roots_sql` derived a document root by
    joining `dec_ref` (treestage, disposable) to `core_decoded` (the tier being
    retired); the honest reintroduction is a shadow whose body does the same, because
    that is where the predicate lives now. The retire statement itself is unchanged —
    which is the point: the statement looks identical and the defect is one level down.
    """
    live = (
        "DELETE FROM core_decoded c WHERE EXISTS ("
        "SELECT 1 FROM core_decoded_shadow s WHERE s.core_id = c.core_id "
        "AND s.dec IS NOT DISTINCT FROM c.dec)"
    )
    ref = (
        "DELETE FROM dec_ref f WHERE EXISTS (SELECT 1 FROM dec_root d WHERE d.core_id = f.core_id)"
    )
    return live, ref


def _raises(f):
    """The `ValueError` message `f` raises, or `None` — a refusal is a RESULT, not an escape.

    ⚑ A REFUSAL THAT IS NEVER ASSERTED ON IS A REFUSAL NOBODY HAS SEEN. `declared_below`
    raises on a malformed declaration; a case that merely called it and let the exception
    escape would report a suite ERROR, not a checked expectation, so the message text would
    never be compared and could rot into something unactionable.
    """
    try:
        f()
    except ValueError as e:
        return str(e)
    return None


def _selftest():
    cases = []

    def check_(label, got, want):
        cases.append((label, got == want, got, want))

    live, ref = _fixtures()
    tiers = {
        "core_decoded": "sourced",
        "dec_scalar": "vocab",
        "dec_node": "tree",
        "dec_root": "tree",
        "dec_ref": "treestage",
        "dec_stage": "treestage",
        "dec_val": "valstage",
        "terms": "event",
        "obs": "event",
        "_node": "sppf",
    }
    good = {"core_decoded_shadow": {"dec_root", "dec_node", "dec_scalar", "dec_val"}}
    # ⚑ THE FIXTURE DECLARATION MIRRORS THE LIVE ONE'S DEC-LADDER PAIRS, and is separate
    # from it for the reason the fixture tiers are: a case must be able to hold the
    # declaration fixed while the statements move, and the reverse.
    decl = declared_below(
        (
            ("sourced", "tree", "the shadow selects dec_root and dec_node"),
            ("sourced", "vocab", "the shadow selects dec_scalar"),
            ("sourced", "valstage", "the shadow selects dec_val"),
            ("treestage", "tree", "retire_ref_sql DELETEs dec_ref on the strength of dec_root"),
        ),
        known=set(tiers.values()),
    )

    # ── the gate PASSES the ladder as it stands ──────────────────────────────────
    v, e, u = analyse(
        [
            ("dec_drain", "retire_sql", "delete", live),
            ("dec_drain", "retire_ref_sql", "delete", ref),
        ],
        tiers,
        good,
        decl,
    )
    check_("the live ladder has no violation", v, [])
    check_("...and no unknown relation", u, set())
    # ⚑ THE LAYERS ARE BY INDEGREE, NOT BY DEPTH, and my first expectation here said
    # `vocab` sits between `sourced` and `tree`. It does not: nothing puts `vocab`
    # below `tree`, so both fall in the same layer the moment `sourced` is removed.
    # Kept as a case rather than corrected silently — the derived order is exactly as
    # strong as the retire edges, and reading extra precedence into it is the error the
    # whole "no declared order" argument at the top of this file exists to avoid.
    check_(
        "...and the derived order puts sourced BELOW tree",
        order(e),
        [["sourced", "treestage"], ["tree", "valstage", "vocab"]],
    )
    check_(
        "...and it claims NO precedence between vocab and tree",
        [i for i, l in enumerate(order(e)) if "vocab" in l]
        == [i for i, l in enumerate(order(e)) if "tree" in l],
        True,
    )

    # ── ❶ — the shadow derives its root the way `roots_sql` did ──────────────────
    # ⚑ THE RETIRE STATEMENT IS BYTE-IDENTICAL TO THE PASSING ONE. Only the shadow's
    # body changed, which is exactly how the defect shipped: the DELETE reads one
    # relation and looks clean at every layer above the view.
    bad1 = {"core_decoded_shadow": {"dec_ref", "core_decoded", "dec_node", "dec_scalar"}}
    v, _e, _u = analyse(
        [
            ("dec_drain", "retire_sql", "delete", live),
            ("dec_drain", "retire_ref_sql", "delete", ref),
        ],
        tiers,
        bad1,
        decl,
    )
    check_(
        "❶ REFUSED: the shadow reading core_decoded fires R1",
        [(r, rel, rt) for r, _m, _a, _w, _wt, rel, rt, _y in v if r == "R1"],
        [("R1", "core_decoded", "sourced")],
    )
    check_(
        "❶ REFUSED: the shadow reading dec_ref fires R2 — a retire DELETEs it",
        [(r, rel, rt) for r, _m, _a, _w, _wt, rel, rt, _y in v if r == "R2"],
        [("R2", "dec_ref", "treestage")],
    )
    check_(
        "❶: the refusal NAMES the offending relation and its tier",
        any(
            "core_decoded" in why and "sourced" in why for _r, _m, _a, _w, _wt, _rel, _rt, why in v
        ),
        True,
    )
    # ⚑ AND ❶ FIRES A THIRD RULE ONCE AN ORDER IS DECLARED: the defective shadow makes the
    # `sourced` retire read `treestage`, entailing `sourced < treestage` — which the
    # declaration relates in NEITHER direction. R5 is the derivation reporting that the
    # statements have outrun the declaration, which is exactly what a broken shadow does.
    check_(
        "❶ REFUSED a third way: the sourced→treestage edge is UNDECLARED (R5)",
        [(r, wt, rt) for r, _m, _a, _w, wt, _rel, rt, _y in v if r == "R5"],
        [("R5", "sourced", "treestage")],
    )

    # ── F10 — a retire predicate joining a relation in its OWN tier ──────────────
    f10 = (
        "DELETE FROM obs o WHERE EXISTS ("
        "SELECT 1 FROM _node n JOIN terms t ON t.term_id = n.head "
        "WHERE n.core_id = o.core_id)"
    )
    v, _e, _u = analyse([("x", "rebuilt_obs_sql", "delete", f10)], tiers, {}, decl)
    # ⚑ FILTERED TO R1 SINCE ⒦, AND THE UNFILTERED FORM WAS THE OLD CASE. The same
    # statement now also reads `_node` (sppf) from a retire of `event`, a pair the fixture
    # declaration does not relate — so R5 fires beside R1 and the total is no longer 1.
    check_(
        "F10 REFUSED: `terms` is in the EVENT tier the DELETE writes",
        [(r, rel) for r, _m, _a, _w, _wt, rel, _rt, _y in v if r == "R1"],
        [("R1", "terms")],
    )
    check_(
        "F10: and the event→sppf pair the declaration does not relate fires R5",
        [(r, wt, rt) for r, _m, _a, _w, wt, _rel, rt, _y in v if r == "R5"],
        [("R5", "event", "sppf")],
    )

    # ── R3 — an at-or-below read that is neither same-tier nor a retire target ───
    # ⚑ THIS IS THE CASE THE DERIVED ORDER EXISTS FOR. Neither R1 nor R2 fires: the
    # tiers differ and nothing DELETEs `dec_node`. What refuses it is that the other
    # retire already established `sourced < tree`, so `tree` reading `sourced` closes
    # the loop — the order is not declared, it is what the statements entail.
    down = (
        "DELETE FROM dec_node n WHERE EXISTS ("
        "SELECT 1 FROM core_decoded c WHERE c.core_id = n.core_id)"
    )
    v, _e, _u = analyse(
        [("dec_drain", "retire_sql", "delete", live), ("x", "retire_tree_sql", "delete", down)],
        tiers,
        good,
        decl,
    )
    check_(
        "R3 REFUSED: a retire reading a tier the graph puts BELOW it",
        [(r, y.split(": ")[-1]) for r, _m, _a, _w, _wt, _rel, _rt, y in v if r == "R3"],
        [("R3", "sourced → tree → sourced")],
    )
    check_(
        "...and there is then NO tier order to report",
        order(
            analyse(
                [
                    ("dec_drain", "retire_sql", "delete", live),
                    ("x", "retire_tree_sql", "delete", down),
                ],
                tiers,
                good,
                decl,
            )[1]
        ),
        None,
    )
    # ⚑⚑ AND THE SAME DEFECT IS CAUGHT INDEPENDENTLY BY THE DECLARED READING — this is the
    # differential's COMMON MODE, as a case. The derivation refuses it because the other
    # retire closed a cycle; the declaration refuses it because `sourced < tree` is written
    # down with a witness. Two routes, one verdict; that agreement is what makes a
    # DISAGREEMENT (R4 alone, or R3 alone) informative rather than noise.
    check_(
        "...and the DECLARED reading refuses the same statement independently (R4)",
        [(r, wt, rt) for r, _m, _a, _w, wt, _rel, rt, _y in v if r == "R4"],
        [("R4", "tree", "sourced")],
    )

    # ── ⒦ — THE DECLARED ORDER ITSELF, AND THE HOLE ONLY IT CAN CLOSE ────────────
    check_(
        "the declaration is closed TRANSITIVELY (it lists generating pairs)",
        declared_below((("a", "b", ""), ("b", "c", "")), known={"a", "b", "c"})[0],
        {("a", "b"), ("b", "c"), ("a", "c")},
    )
    check_(
        "a declaration naming an undeclared tier is REFUSED, never defaulted",
        _raises(lambda: declared_below((("a", "nosuch", ""),), known={"a"})),
        "TIER_BELOW relates 'nosuch', which is not a declared tier; known: ['a']",
    )
    check_(
        "a declaration that is not an ORDER (it declares a cycle) is REFUSED",
        _raises(lambda: declared_below((("a", "b", ""), ("b", "a", "")), known={"a", "b"})),
        "TIER_BELOW is not an order — it declares a cycle: a < b < a",
    )

    # ⚑⚑ THE HOLE THE DERIVED ORDER COULD NEVER SEE, AS A CASE. A retire of `sppf` reading
    # `ref`: the tiers differ (no R1), nothing DELETEs `ref` (no R2), and the retire graph
    # holds ONE edge and therefore no cycle (no R3) — the derivation has nothing to compare
    # and PASSES. What refuses it is that `TIER_BELOW` says `ref < sppf`, with a witness.
    # This is precisely the *"a retire reading a genuinely-lower tier that no retire relates
    # in either direction"* weakness ⒣ named as its sharpest and could not close.
    hole = "DELETE FROM _node n WHERE EXISTS (SELECT 1 FROM ref r WHERE r.node_id = n.id)"
    hdecl = declared_below(
        (("ref", "sppf", "ref is an INDEX over SPPF × fibre"),), known={"sppf", "ref"}
    )
    v, he, _u = analyse(
        [("x", "retire_sppf_sql", "delete", hole)], {"_node": "sppf", "ref": "ref"}, {}, hdecl
    )
    check_(
        "⒦ REFUSED: a retire reading a DECLARED-lower tier — R1/R2/R3 all miss it",
        [(r, w, rel) for r, _m, _a, w, _wt, rel, _rt, _y in v],
        [("R4", "_node", "ref")],
    )
    check_(
        "...and the DERIVED reading alone passes it: there is no cycle to close", _cycles(he), []
    )
    check_(
        "...and the refusal QUOTES the reason the pair was declared",
        any("INDEX over SPPF" in y for _r, _m, _a, _w, _wt, _rel, _rt, y in v),
        True,
    )

    # ── the reader's own bounds, as cases rather than as prose ───────────────────
    # ⚑ THE DELETE TARGET IS NOT A READ. Keyed on `FROM` alone every retire reads the
    # tier it writes, so the gate would refuse the whole ladder — a gate that always
    # fires is exactly as useless as one that never does.
    check_(
        "the DELETE target is a write, never a read",
        sql_rw(live),
        ({"core_decoded"}, {"core_decoded_shadow"}),
    )
    check_(
        "an unknown relation is REPORTED, never defaulted into a tier",
        analyse(
            [
                (
                    "x",
                    "y_sql",
                    "delete",
                    "DELETE FROM core_decoded WHERE EXISTS (SELECT 1 FROM mystery m)",
                )
            ],
            tiers,
            {},
            decl,
        )[2],
        {"mystery"},
    )
    # ⚑ A NON-DELETE STATEMENT IS OUT OF POPULATION AND MUST STAY OUT: promote reads
    # DOWN by design, so judging it by this rule would refuse every correct build.
    check_(
        "a promote is not judged by the retire rule",
        analyse(
            [
                (
                    "x",
                    "root_sql",
                    "insert",
                    "WITH r AS (SELECT 1 AS id) INSERT INTO dec_root (root) "
                    "SELECT r.id FROM r JOIN core_decoded c ON c.core_id = r.id",
                )
            ],
            tiers,
            {},
            decl,
        )[0],
        [],
    )
    check_(
        "a shadow chain is expanded transitively",
        expand({"a"}, {"a": {"b"}, "b": {"dec_node"}})[0],
        {"dec_node"},
    )
    check_(
        "a self-referential shadow terminates rather than looping",
        expand({"a"}, {"a": {"a", "dec_node"}})[0],
        {"dec_node"},
    )

    # ── the LIVE tree, last: the population is real and it is clean ──────────────
    stmts, holes = statements()
    check_(
        "the live population holds at least one retire statement",
        sum(1 for _m, _a, k, _s in stmts if k == "delete") >= 1,
        True,
    )
    lv, le, lu, _lh, ldecl = check(stmts)
    check_("the LIVE ladder passes the gate", [x[0] for x in lv], [])
    check_("...with every read relation resolving to a declared tier", lu, set())
    check_("...and every rung module composing (no unread holes)", holes, [])
    # ── the DIFFERENTIAL on the live tree: the two readings, compared ────────────
    derived = {(u_, v_) for u_ in le for v_ in le[u_]}
    check_(
        "...and every DERIVED edge is entailed by the DECLARED order",
        sorted(derived - ldecl[0]),
        [],
    )
    # ⚑ THE DECLARATION IS STRICTLY STRONGER, AND THAT IS REPORTED RATHER THAN REFUSED.
    # `sourced < event` and `ref < sppf` are declared from notes in `schema_decl` and no
    # retire witnesses either — which is the POINT: R4 can refuse a downward read on a pair
    # the retire graph will never relate. Requiring a witness would forbid closing the hole
    # in advance, i.e. would forbid the declaration from doing the only thing it is for.
    check_(
        "...and the DECLARATION is strictly stronger than the retire graph",
        sorted(set(ldecl[1]) - derived),
        [("ref", "sppf"), ("sourced", "event")],
    )
    # ⚑ THE DENOMINATOR IS A FUNCTION OF THE TIER COUNT, NOT A TUNED CONSTANT. It was
    # `6 of 55` until 2026-08-23, when the ORBIT tier was removed: 11 tiers → 10, and the
    # unordered pair count follows, 11·10/2 = 55 → 10·9/2 = 45. The numerator (`6` declared
    # pairs) is unchanged, because removing an empty tier declared no new order. Recorded so
    # the next reader sees a DERIVED figure moving with its input rather than a magic number
    # someone edited to make a case pass — the two are indistinguishable without this note.
    check_(
        "...and the blind-spot list is SEVEN, the seventh a COUNT that can be paid down",
        (
            len(blind(tier_of_relation(), ldecl)),
            "6 of 45 tier pairs are declared" in blind(tier_of_relation(), ldecl)[6],
        ),
        (7, True),
    )

    # ── ⒦ SHOWN REFUSING ON A WRONG DECLARATION — `_TIERS`' OWN INSERTION ORDER ───
    # ⚑⚑ THIS PERTURBATION IS NOT INVENTED. It is the reading `_TIERS`' old note invited
    # (*"the ordering of this dict is the only place the tier ORDER is written down"*), and
    # an agent took it on 2026-08-13 before the gate measured otherwise. Read as a chain it
    # puts `tree` BEFORE `treestage`, while `retire_ref_sql`/`retire_stage_sql` DELETE
    # `dec_ref`/`dec_stage` on the strength of `dec_root` — the reverse. So the wrong
    # declaration is REFUSED against the LIVE statements, naming the pair and the direction.
    import schema_decl as _D

    _ins = list(_D._TIERS)
    wrong = declared_below(
        tuple((_ins[i], _ins[i + 1], "`_TIERS` insertion order") for i in range(len(_ins) - 1))
    )
    wv, _we, _wu = analyse(stmts, tier_of_relation(), shadow_bases(), wrong)
    check_(
        "⒦ REFUSED: `_TIERS`' insertion order, declared, is CONTRADICTED by the ladder",
        sorted({(r, wt, rt) for r, _m, _a, _w, wt, _rel, rt, _y in wv}),
        [("R4", "treestage", "tree")],
    )
    check_("...and the DERIVED order is unchanged by a wrong declaration", order(_we), order(le))

    for label, ok, got, want in cases:
        if not ok:
            print("  FAIL %s\n    got  %r\n    want %r" % (label, got, want))
    import rungs

    rungs.emit_record(sum(1 for _l, ok, _g, _w in cases if ok), len(cases), key="tier_readset")
    print("tier_readset selftest: %d/%d" % (sum(1 for _l, ok, _g, _w in cases if ok), len(cases)))
    return all(ok for _l, ok, _g, _w in cases)


def main():
    argv = set(sys.argv[1:])
    if "--selftest" in argv:
        return 0 if _selftest() else 1
    stmts, holes = statements()
    if "--census" in argv:
        for mod, acc, kind, sql in stmts:
            w, r = sql_rw(sql)
            print(
                "  %-10s %-18s %-7s writes=%s reads=%s"
                % (mod, acc, kind or "-", sorted(w) or "-", sorted(r) or "-")
            )
        for mod, acc, why in holes:
            print("  HOLE      %s.%s — %s" % (mod, acc, why))
        print(
            "%d statement(s) over %d rung module(s); %d hole(s)"
            % (len(stmts), len({m for m, _a, _k, _s in stmts}), len(holes))
        )
        return 0
    v, e, u, holes, decl = check(stmts)
    if "--order" in argv:
        _print([], e, set(), [], decl, quiet=False)
        return 0
    _print(v, e, u, holes, decl)
    # ⚑ A HOLE IS NOT A PASS. An unimported rung module contributes an empty read set,
    # which is indistinguishable from a clean one — so the gate refuses rather than
    # reporting green over a population it could not read.
    if v or holes:
        print(
            "tier-readset (⒣): FAILED — %d violation(s), %d unread rung(s)." % (len(v), len(holes))
        )
        print(
            "  The property: a retire predicate's read set must contain nothing at "
            "or below the tier it writes."
        )
        return 1
    print(
        "tier-readset (⒣/⒦): %d retire statement(s) over %d rung module(s) — no read at "
        "or below the tier written, by EITHER reading (declared and derived agree)."
        % (sum(1 for _m, _a, k, _s in stmts if k == "delete"), len({m for m, _a, _k, _s in stmts}))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
