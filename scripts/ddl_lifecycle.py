#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""ddl_lifecycle.py — ⒧ THE LIFECYCLE OF A DDL-MANAGED OBJECT.

    The declaration says how to BUILD the store.  Nothing says how to take it
    apart, so the only teardown that exists asks postgres to work the order out
    with `CASCADE`.  This derives the order instead, and audits it against the
    one thing about it that is a JUDGEMENT.

⚑⚑ THE INVERSE WAS NEVER TAKEN, AND THAT IS THE WHOLE GAP.  `schema_rows.apply()`
creates in `MD.sorted_tables` order and returns a COUNT; `schema_decl.ddl()` appends
indexes and then the shadow view *"LAST: they select from the tables above"*.  Both
statements are about creation.  The only teardown in the tree is `store.sandbox_reset`,
and it does three things that make it not a lifecycle:

  1. it reads the LIVE CATALOGUE (`information_schema`), not the declaration — so it
     can only drop what happens to be there, and cannot say what SHOULD be;
  2. it drops with `CASCADE`, which is postgres computing the order — so no order is
     ever derived, and nothing can be wrong because nothing was claimed;
  3. it drops EVERY relation in the tenant, which is the `reset=True` hazard reachable
     from 23 call sites (`pycodemod --calls sandbox_connect`).

⚑⚑ AND THE GOVERNING SPLIT, WHICH THIS FILE IS ORGANISED BY: **generation makes
agreement guaranteed, which makes agreement uninformative.**  So the two halves are
kept apart on purpose and the tell is *did a human have to write a REASON?*

  * MECHANICAL → GENERATED.  One relation, one object; one object, one Salt state.
    Every `require:` edge is DERIVED (`Index.table`, the compiled view body,
    `Table.foreign_key_constraints`).  A disagreement here would be transcription
    error, and generating eliminates the class.  ⚑ **NO `require:` EDGE IS EVER
    HAND-AUTHORED** — a second declaration of the object graph beside `schema_decl`
    is the `_TIER_VIEWS` second-roster shape this repo retired.
  * JUDGEMENT → AUDITED.  `schema_decl.TIER_BELOW` carries a `why` PER PAIR, so it is
    judgement; `SHADOWS`' owning-tier value argues itself at length, so it is too.
    A disagreement here is a FINDING and both sides are printed.

⚑⚑ THE HEADLINE MEASUREMENT, AND IT IS WHY THE NAIVE TEARDOWN FAILS: **`MD` DECLARES
ZERO FOREIGN KEYS.**  `schema_decl` never imports `ForeignKey`.  So `MD.sorted_tables`
— the thing named as the create-order authority — does no dependency work at all and
degenerates to alphabetical.  The one real DDL dependency in this schema is the VIEW
`core_decoded_shadow`, which `MD` does not contain: it lives in `SHADOWS`, is compiled
separately, and is appended by `ddl()` after the loop.  **A reversal of
`MD.sorted_tables` therefore cannot know the view exists**, and `--demo` shows postgres
refusing it (`DependentObjectsStillExist`, 2BP01) where the derived order succeeds.

⚑ CREATE AND TEARDOWN ARE NOT THE SAME GRAPH REVERSED, AND ASSUMING THEY WERE IS THE
EASY ERROR HERE.  Creation is constrained by EXISTENCE only (a view needs its bases to
exist).  Teardown is constrained by existence AND by LIFETIME — `TIER_BELOW`'s `(a, b)`
means *b outlives a*, so `a`'s objects must go first, and no create order ever had to
respect that.  `ddl()`'s emitted order is checked against the existence graph alone
(A0b); the teardown is derived from both (A2), and their CONTRADICTION is a refusal.

⚑ WHAT THIS FILE IS NOT.  It is a CALLER, not a rung — `pycodemod --control` is
expected to be non-zero here, exactly as `tier_readset.py` states for itself.  It adds
NO `*_sql()` accessor under `jea/metalanguage/`, deliberately: `tier_readset` discovers
its population that way, so a DDL emitter spelled like a rung would enter a gate that
judges retire predicates and has nothing to say about `CREATE TABLE`.

⚑ IT LIVES IN `scripts/` FOR `tier_readset`'s MEASURED REASON: opening a view's body
needs `scratch/_pycodemod_sql`, and `check_scratch_independence` (Λ8) forbids `jea/`
from making a live reference to `scratch/`.  `scripts/ → scratch/` is the established
direction.

⚑ THE GRAPH NEEDS NO DATABASE.  Every input is a declaration or a statement compiled
through `store.dialect()` (which opens nothing).  Only `--demo` connects, and it
connects to a PRIVATE SCHEMA via `sandbox_fixture` — never the shared sandbox
namespace, never `reset=True`.

Usage: ddl_lifecycle.py [--census] [--order] [--check] [--emit DIR] [--salt]
                        [--demo] [--selftest]
"""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, os.path.join(ROOT, "scratch"))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))

# ⚑⚑ THE TOPOLOGY, THE CYCLE ENUMERATION AND THE DECLARATION'S CLOSURE ARE ⒣/⒦'s AND
# ARE IMPORTED, NOT REIMPLEMENTED.  `tier_readset.order` is already a generic layered
# topological sort over `{node: {succ}}` that returns `None` on a cycle; `_cycles`
# enumerates the elementary cycles; `declared_below` closes `TIER_BELOW` transitively
# and REFUSES a malformed declaration; `shadow_bases` compiles each shadow through
# `schema_decl.view_ddl` — the ONE emitter — and takes its relations with `sql_rw`.
# Four capabilities, none of them owed a second body.  (The reuse-search fired on the
# plan: `scratch/dagcone.py` was checked and is the CONE authority — reachability and
# exclusivity — not a layered order, so it is not the tool for this.)
import tier_readset as TR  # noqa: E402

#: The Salt binary this repo declares.  ⚑ `uv add salt` (2026-08-13) — a DECLARED
# dependency, not a `uv run --with` incantation, because *"a dependency named only in a
# docstring is a permission slip, not a declaration: it must be re-granted every time
# and nothing can check it"* (`pyproject.toml`'s own note).
SALT_CALL = os.path.join(ROOT, ".venv", "bin", "salt-call")


# ── (1) THE POPULATION — one DDL object per declared thing, never a roster ───────────
#
# ⚑ AN OBJECT IS `(kind, name)` AND THE KIND IS LOAD-BEARING: a table, an index and a
# view are dropped by three different statements and depend on each other in one
# direction only.  Collapsing them to bare names would make `DROP` a lookup nobody can
# check, which is how `sandbox_reset` ended up branching on `table_type` at the point of
# use instead of carrying the kind.
def objects():
    """`[(kind, name)]` — every object `schema_decl` declares, from the DECLARATION."""
    import schema_decl as D

    out = [("table", t.name) for t in D.MD.sorted_tables]
    out += [("index", ix.name) for ix in D.INDEXES]
    out += [("view", n) for n in sorted(D.SHADOWS)]
    return out


def _head(sql):
    """`(kind, name)` for one emitted `CREATE …` statement, or `None`.

    ⚑ THE EMITTED STATEMENT IS PARSED RATHER THAN TRUSTED, so A0a compares two
    independently-derived populations.  Reading the objects off `MD`/`INDEXES`/`SHADOWS`
    AND off `ddl()`'s output means a construct that stops being emitted (the ⟡view-purge
    shape — six views deleted from the emitter while their selectables stayed) shows up
    as a population disagreement instead of as silence.
    """
    tok = sql.replace("(", " ( ").split()
    if not tok or tok[0].upper() != "CREATE":
        return None
    i = 1
    for skip in (("OR", "REPLACE"), ("UNIQUE",), ("MATERIALIZED",)):
        if [t.upper() for t in tok[i : i + len(skip)]] == list(skip):
            i += len(skip)
    kind = tok[i].upper()
    i += 1
    if [t.upper() for t in tok[i : i + 3]] == ["IF", "NOT", "EXISTS"]:
        i += 3
    if kind not in ("TABLE", "INDEX", "VIEW") or i >= len(tok):
        return None
    return (kind.lower(), tok[i].strip('"'))


def emitted():
    """`[(kind, name)]` in the order `schema_decl.ddl()` sends them — the CREATE order.

    ⚑ THIS IS THE ORDER THAT EXISTS TODAY, and A0b asks whether it is a valid
    linearisation of the derived graph.  It is not assumed to be: `ddl()` walks
    `MD.sorted_tables`, then `INDEXES` in declaration order, then the views — an
    arrangement that is CORRECT and is correct by three separate conventions rather than
    by a computed order, which is exactly the thing that can silently stop being true.
    """
    import schema_decl as D

    got, unparsed = [], []
    for s in D.ddl("postgres"):
        h = _head(s)
        (got if h else unparsed).append(h if h else s.split("\n")[0][:70])
    return got, unparsed


# ── (2) THE EXISTENCE GRAPH — mechanical, and the ONLY source of `require:` edges ────
#
# ⚑⚑ AN EDGE `X → Y` MEANS **X IS TORN DOWN BEFORE Y**, in both edge kinds, so the two
# sources compose without a translation step.  Read the other way it says Y is CREATED
# before X.  One convention, stated once, because a direction convention spelled per
# call site is how `TIER_BELOW`'s own note came to contain prose in both senses.
def exist_edges():
    """`({obj: {obj}}, unknown)` — DDL EXISTENCE dependencies, derived from three facts.

    ⚑ THE THREE SOURCES, AND EACH IS A LOOKUP RATHER THAN A JUDGEMENT:

      * `index → its table`      — `Index.table.name`.  Postgres drops an index with its
                                   table, but the ORDER is still derived here so the
                                   teardown never relies on a cascade it did not ask for.
      * `view  → each base`      — `tier_readset.shadow_bases()`, which compiles the body
                                   through `schema_decl.view_ddl` (the one emitter) and
                                   reads its relations with `sql_rw`.  ⚑ Taking the bases
                                   off a second rendering would let this graph and the
                                   deployed view disagree about what depends on what.
      * `table → referenced table` — `Table.foreign_key_constraints`.

    ⚑⚑ AND THE THIRD SOURCE IS **EMPTY** — MEASURED, not assumed.  `schema_decl` imports
    no `ForeignKey` at all, so there is not one referential constraint in the model.
    That is reported by `--census` as a number rather than left as an absence, because
    it is precisely what makes `MD.sorted_tables` (a topological sort over FKs) do no
    work: with no FKs it is alphabetical, and alphabetical is not an order.
    """
    import schema_decl as D

    edges, unknown = {}, set()
    for ix in D.INDEXES:
        edges.setdefault(("index", ix.name), set()).add(("table", ix.table.name))
    for t in D.MD.sorted_tables:
        for fk in t.foreign_key_constraints:
            edges.setdefault(("table", t.name), set()).add(("table", fk.referred_table.name))
    bases = TR.shadow_bases()
    for view, rels in bases.items():
        for r in sorted(rels):
            if r in D.MD.tables:
                edges.setdefault(("view", view), set()).add(("table", r))
            elif r in D.SHADOWS:
                edges.setdefault(("view", view), set()).add(("view", r))
            else:
                unknown.add(r)
    return edges, unknown


# ── (3) THE TIER OF AN OBJECT, AND THE SHADOWED RELATION ─────────────────────────────
def tier_of_object(obj, tiers, owner):
    """The tier an object belongs to, or `None`.

    A table's tier is `_TIERS`' membership; an INDEX inherits its table's (an access
    path is not a lifecycle stage — `INDEXES` declares no tier and inventing one would
    be a second roster); a VIEW's is the OWNING tier `SHADOWS` names, which is the value
    that argues itself and is therefore audited rather than trusted.
    """
    kind, name = obj
    if kind == "table":
        return tiers.get(name)
    if kind == "index":
        return tiers.get(owner.get(name))
    return owner.get(name)


def shadowed():
    """`({view: relation}, ambiguous)` — which relation each shadow RECONSTRUCTS.

    ⚑⚑ DERIVED BY EXACT COLUMN MATCH, NOT BY THE `_shadow` NAME SUFFIX, and the choice is
    the difference between a check and a convention.  `SHADOWS`' own note states the
    property this reads: *"THE COLUMN LIST MIRRORS `core_decoded` EXACTLY — same names,
    same order.  A shadow whose columns differ from the relation it shadows cannot be
    `EXCEPT`ed against it, and `EXCEPT` is the whole observability claim."*  So the
    match is the DECLARED invariant, and a rename that broke it would be caught here;
    a name-suffix rule would keep agreeing while the claim silently stopped holding.

    ⚑ AMBIGUITY AND ABSENCE ARE BOTH REFUSALS, NEVER A GUESS.  Two relations with the
    same column list would make "which one does this shadow claim to rebuild" a coin
    flip, and a coin flip inside an audit is worse than no audit.
    """
    import schema_decl as D

    cols = {t.name: [c.name for c in t.columns] for t in D.MD.sorted_tables}
    out, bad = {}, []
    for v, (sel, _tier) in sorted(D.SHADOWS.items()):
        want = [c.name for c in sel.selected_columns]
        hit = sorted(n for n, cs in cols.items() if cs == want)
        if len(hit) == 1:
            out[v] = hit[0]
        else:
            bad.append((v, want, hit))
    return out, bad


# ── (4) THE LIFETIME GRAPH — the DECLARED order, expanded to objects ─────────────────
def life_edges(objs, tiers, owner, declared):
    """`{obj: {obj}}` — `TIER_BELOW` as object-level teardown edges.

    ⚑ `(a, b)` MEANS **b OUTLIVES a**, so every object of tier `a` is torn down before
    every object of tier `b`.  Expanded to the object level rather than checked at the
    tier level for a measured reason: the tiers a teardown SEQUENCE visits interleave —
    `tree`'s indexes have nothing depending on them and fall in the first layer beside
    `sourced`'s table — so a positional "tier a before tier b" test over a linearised
    sequence passes or fails by whatever the intra-layer tiebreak happens to be.  A
    check that can pass ALPHABETICALLY is not a check.  As edges it is exact: either the
    combined graph is acyclic, or the two sources contradict and `--check` says where.
    """
    rel, _why = declared
    by_tier = {}
    for o in objs:
        t = tier_of_object(o, tiers, owner)
        if t is not None:
            by_tier.setdefault(t, []).append(o)
    edges = {}
    for lo, hi in sorted(rel):
        for a in by_tier.get(lo, ()):
            for b in by_tier.get(hi, ()):
                edges.setdefault(a, set()).add(b)
    return edges


def merge(*graphs):
    """The union of `{node: {node}}` graphs."""
    out = {}
    for g in graphs:
        for k, vs in g.items():
            out.setdefault(k, set()).update(vs)
    return out


def sequence(objs, edges):
    """`[obj]` — one linearisation of `edges` over `objs`, or `None` if it is cyclic.

    ⚑ THE LAYERS COME FROM `tier_readset.order` AND THE FLATTENING IS THIS FILE'S ONLY
    ADDITION.  A layer is a set of objects with no remaining constraint between them, so
    ANY intra-layer order is correct; sorting makes the emitted statement list stable
    run to run, which is what lets `--emit`'s output be diffed.  ⚑ Objects that no edge
    mentions are absent from the layering entirely and are appended — a table with no
    index, in no view and in no declared tier pair is genuinely unconstrained, and
    dropping it from the sequence would be a teardown that does not tear it down.
    """
    lay = TR.order(edges)
    if lay is None:
        return None
    seen, out = set(), []
    for layer in lay:
        for o in sorted(layer):
            out.append(o)
            seen.add(o)
    out += sorted(o for o in objs if o not in seen)
    return out


def drop_statements(seq, schema):
    """`[sql]` — the teardown, as statements.  ⚑ NO `CASCADE`, and that is the point.

    `store.sandbox_reset` uses `CASCADE` on every drop, which is postgres computing the
    dependency order — so no order was ever derived, and nothing could be wrong because
    nothing was claimed.  Withholding it makes the derived order LOAD-BEARING: a wrong
    order raises `DependentObjectsStillExist` instead of quietly succeeding.

    ⚑ AND NO `IF EXISTS`, FOR THE SAME REASON ONE LEVEL DOWN.  A teardown derived from
    the declaration should find exactly what the declaration says is there; tolerating
    an absent object would make a half-built store and a fully-built one produce the
    same green result.

    ⚑⚑ `schema` IS REQUIRED, AND THAT IS THE TARGET HALF OF THE SAME ARGUMENT.  This
    emitted `DROP TABLE "dec_val"` — quoted identifier, NO schema — so the object it
    destroyed was whatever `search_path` resolved AT TEARDOWN.  `dec_val` exists in
    SIXTEEN schemas of `substrate_sandbox`; the demo hit the right one because
    `sandbox_fixture` had set `search_path` on that same connection, which is luck
    rather than mechanism — and `search_path` is exactly what a concurrent fixture
    mutates.  An increment whose whole thesis is DERIVED, CORRECTLY-ORDERED DESTRUCTION
    got the ORDER right and left the TARGET ambiguous, which is the more dangerous half:
    a wrong order raises, a wrong target succeeds.

    ⚑ REQUIRED RATHER THAN DEFAULTED, so the ambiguity is impossible by construction
    instead of merely discouraged — a default is a caller silently re-creating it.  And
    the value must come from where the object was CREATED (`schema_rows.fixture_schema`),
    never from `current_schema()`: that reads `search_path` too, one layer down and
    later, which would re-pose the same question while looking like an answer.
    """
    kw = {"table": "DROP TABLE", "index": "DROP INDEX", "view": "DROP VIEW"}
    return ['%s "%s"."%s"' % (kw[k], schema, n) for k, n in seq]


def naive_drop_statements(schema):
    """`[sql]` — `reversed(MD.sorted_tables)`, the only inverse the tree could have taken.

    ⚑⚑ THIS IS NOT A STRAW MAN.  It is the exact dual of `schema_rows.apply()`, whose
    create order IS `MD.sorted_tables` and whose docstring calls the ordering solved.
    It fails, and it fails for a structural reason rather than a fixable one: the VIEW
    is not in `MD` at all, so no function of `MD` can ever place it.

    ⚑ SCHEMA-QUALIFIED TOO, and NOT because the straw man deserves care.  It is executed
    against a real namespace by `demo()`, so leaving it unqualified would keep a live
    unqualified DROP in the file whose finding is that unqualified DROPs are the defect
    — and would make the naive run's failure partly a fact about `search_path` rather
    than purely about the order, which is the one thing the comparison must isolate.

    ⚑ AND THE SCHEMA CANNOT BE READ OFF `D.MD`: measured, `MetaData(…)` is constructed at
    NINE sites in this tree and NOT ONE passes `schema=`, so `t.schema` is `None`
    everywhere.  **The declaration does not know its own schema** — that is a finding,
    not something to paper over here.  The namespace is a property of the DEPLOYMENT
    (which fixture, which tenant), so it arrives as an argument from the caller that
    created it.
    """
    import schema_decl as D

    return ['DROP TABLE "%s"."%s"' % (schema, t.name) for t in reversed(D.MD.sorted_tables)]


# ── (5) THE AUDIT ────────────────────────────────────────────────────────────────────
RULES = {
    "A0a": "the DECLARED population and the population `schema_decl.ddl()` EMITS "
    "disagree — an object is declared and not emitted, or emitted and not "
    "declared",
    "A0b": "`schema_decl.ddl()` emits an object BEFORE something it depends on — its "
    "create order is not a linearisation of the existence graph",
    "A0c": "the derived teardown does not cover the declared population exactly once",
    "A1": "a SHADOW reads a base relation whose tier `schema_decl.TIER_BELOW` does NOT "
    "put above the tier of the relation the shadow reconstructs — so the "
    "reconstruction claim rests on something declared no longer-lived than the "
    "thing it licenses draining",
    "A2": "the EXISTENCE graph and the DECLARED lifetime order CONTRADICT: their union "
    "is cyclic, so no teardown order satisfies both",
    "A3": "salt's requisite-resolved order is not a linearisation of the generated "
    "graph — the generator and the DAG resolver disagree",
}


def audit(objs, ex, life, tiers, owner, shadows, bases, declared, emit=None):
    """`[(rule, subject, detail)]` — the whole judgement, over an INJECTED population.

    ⚑⚑ EVERY INPUT IS A PARAMETER SO A CASE CAN DRIVE IT, and this is `tier_readset`'s
    rule inherited verbatim: *"A gate whose input is always the live tree can only ever
    be observed PASSING, and a gate never observed to refuse has not been shown to be a
    gate."*  `declared` in particular is REQUIRED rather than defaulted to the live
    `TIER_BELOW`, so a case can perturb the declaration — drop a pair, invert a pair —
    and see the refusal name both sides, without mutating `schema_decl`.
    """
    dec_rel, dec_why = declared
    out = []

    if emit is not None:
        emitted_set, decl_set = set(emit), set(objs)
        for o in sorted(decl_set - emitted_set):
            out.append(("A0a", "%s %s" % o, "DECLARED by schema_decl and NOT emitted by ddl()"))
        for o in sorted(emitted_set - decl_set):
            out.append(
                ("A0a", "%s %s" % o, "EMITTED by ddl() and in no declaration this reader knows")
            )
        pos = {o: i for i, o in enumerate(emit)}
        for x, ys in sorted(ex.items()):
            for y in sorted(ys):
                if x in pos and y in pos and pos[y] > pos[x]:
                    out.append(
                        (
                            "A0b",
                            "%s %s" % x,
                            "ddl() emits it at position %d but emits %s %s — which "
                            "it DEPENDS ON — at position %d" % (pos[x], y[0], y[1], pos[y]),
                        )
                    )

    seq = sequence(objs, merge(ex, life))
    if seq is None:
        for c in TR._cycles(merge(ex, life)):
            out.append(
                (
                    "A2",
                    " → ".join("%s %s" % o for o in c),
                    "the EXISTENCE graph and the DECLARED lifetime order close a "
                    "cycle, so no teardown satisfies both. DECLARED: "
                    + "; ".join(
                        "%s < %s — %s" % (a, b, dec_why.get((a, b), "")) for a, b in sorted(dec_why)
                    ),
                )
            )
    else:
        if sorted(seq) != sorted(objs) or len(seq) != len(objs):
            out.append(
                (
                    "A0c",
                    "-",
                    "teardown covers %d object(s) for a declared "
                    "population of %d" % (len(seq), len(objs)),
                )
            )

    for view, rel_name in sorted(shadows.items()):
        st = tiers.get(rel_name)
        for b in sorted(bases.get(view, ())):
            bt = tiers.get(b)
            if bt is None or st is None or bt == st:
                continue
            if (st, bt) in dec_rel:
                continue
            back = (
                "DECLARED THE OTHER WAY: %r < %r — %s"
                % (bt, st, dec_why.get((bt, st), "entailed transitively"))
                if (bt, st) in dec_rel
                else "DECLARED: nothing — TIER_BELOW relates %r and %r in NEITHER "
                "direction" % (st, bt)
            )
            out.append(
                (
                    "A1",
                    "%s reads %s" % (view, b),
                    "DERIVED: the shadow of %r (tier %r) selects %r (tier %r), so %r must "
                    "outlive %r. %s." % (rel_name, st, b, bt, bt, st, back),
                )
            )
    return out


def salt_linearises(objs, edges, run_order):
    """`[(rule, subject, detail)]` — A3: salt's order against the generated graph."""
    pos = {o: i for i, o in enumerate(run_order)}
    out = []
    for x, ys in sorted(edges.items()):
        for y in sorted(ys):
            if x in pos and y in pos and pos[x] > pos[y]:
                out.append(
                    (
                        "A3",
                        "%s %s" % x,
                        "salt runs it at %d, after %s %s at %d, but the generated "
                        "graph puts it first" % (pos[x], y[0], y[1], pos[y]),
                    )
                )
    missing = sorted(set(objs) - set(pos))
    if missing:
        out.append(
            (
                "A3",
                "-",
                "salt ran %d state(s) for a population of %d; absent: %s"
                % (len(pos), len(objs), ", ".join("%s %s" % o for o in missing)),
            )
        )
    return out


# ── (6) THE GENERATED SALT STATE TREE ────────────────────────────────────────────────
#
# ⚑⚑ SALT IS THE **SECOND READING**, NOT THE AUTHORITY, and that is what makes adding it
# worth 82 packages.  The applier uses THIS file's topological order; salt independently
# resolves the same `require:` DAG and reports its resolution as `__run_num__`.  A3 is
# the differential — `tier_readset`'s declared-vs-derived discipline applied one layer
# down.  Trusting either alone would swap one self-consistent reading for another.
#
# ⚑ MASTERLESS ONLY (`salt-call --local`), AND THE BOUNDARY IS OWNERSHIP RATHER THAN
# TASTE (user, 2026-08-13: *"handling system services as-a-service is
# cassian-observability's job"*).  Nothing here daemonises, listens, or writes outside
# the repo and a caller-supplied directory.  **NO MASTER IS REQUIRED**, so there is no
# ask to route: `state.apply … test=True` resolves requisites entirely in-process.
#
# ⚑ THE STATES NEVER TOUCH POSTGRES, DELIBERATELY, and this is what dissolved the
# container question.  `store.PG_HOST` is a UNIX socket (`~/.local/share/cassian/pg-run`)
# with no TCP surface; a containerised applier would need it bind-mounted with matching
# uids.  Salt here only EMITS AND ORDERS, so there is no socket to mount and the
# executor stays replaceable — which is the whole point of generating rather than
# hand-authoring.
def state_id(obj):
    """`'<kind>-<name>'` — the state's id.  ⚑ NOT `'<kind>:<name>'`: a colon inside an
    unquoted YAML key is a mapping separator, so the id would parse as a nested dict and
    the `require:` reference would silently name nothing."""
    return "%s-%s" % obj


def sls(objs, edges, reverse=False):
    """The generated `.sls` — one state per object, `require:` edges DERIVED.

    `reverse=False` is the CREATE tree: an object requires what must exist first.
    `reverse=True` is the TEARDOWN tree: an object requires its DEPENDENTS to have gone.
    One generator, one graph, the edge direction as the only parameter — so the two
    trees cannot drift, which is what "teardown order as its inverse" has to mean if it
    is to mean anything checkable.

    ⚑ `test.succeed_without_changes` AND NOT A POSTGRES STATE MODULE.  The state tree's
    job is the ORDER; the DDL is executed by `apply()`/`drop_statements` over a
    connection this process owns.  A `postgres_*` state would need salt to hold the
    socket, the credentials and the search_path — three couplings for a capability the
    repo already has.
    """
    inv = {}
    for x, ys in edges.items():
        for y in ys:
            (inv.setdefault(y, set()).add(x) if reverse else inv.setdefault(x, set()).add(y))
    lines = []
    for o in objs:
        lines.append("%s:" % state_id(o))
        lines.append("  test.succeed_without_changes:")
        lines.append("    - name: %s %s" % o)
        req = sorted(inv.get(o, ()))
        if req:
            lines.append("    - require:")
            for r in req:
                lines.append("      - test: %s" % state_id(r))
        lines.append("")
    return "\n".join(lines)


def emit_tree(directory, objs, edges):
    """Write the masterless salt root: `minion`, `create/init.sls`, `teardown/init.sls`.

    ⚑⚑ THE `minion` FILE IS THE WHOLE OF THE "SYSTEM-LEVEL DAEMON CONFIG" WALL, MEASURED.
    `salt-call --local --config-dir=<dir>` ALONE still fails with
    `Permission denied: '/etc/salt'` and `No permissions to access /var/log/salt/minion`
    — because `--config-dir` says where to READ config, not where to WRITE state.  What
    moves the writes is `root_dir` + `cachedir` + `pki_dir` + `sock_dir` + `log_file`
    inside that config.  One file, no daemon, no root: which is why masterless stayed
    inside substrate's own boundary and no ask had to be routed.
    """
    os.makedirs(directory, exist_ok=True)
    run = os.path.join(directory, "run")
    for sub in ("create", "teardown"):
        os.makedirs(os.path.join(directory, sub), exist_ok=True)
    with open(os.path.join(directory, "minion"), "w", encoding="utf-8") as fh:
        fh.write(
            "id: substrate-ddl\nfile_client: local\n"
            "root_dir: %s\ncachedir: %s\npki_dir: %s\nsock_dir: %s\n"
            "log_file: %s\nfile_roots:\n  base:\n    - %s\n"
            "pillar_roots:\n  base: []\n"
            % (
                run,
                os.path.join(run, "cache"),
                os.path.join(run, "pki"),
                os.path.join(run, "sock"),
                os.path.join(run, "minion.log"),
                directory,
            )
        )
    with open(os.path.join(directory, "create", "init.sls"), "w", encoding="utf-8") as fh:
        fh.write(sls(objs, edges, reverse=False))
    with open(os.path.join(directory, "teardown", "init.sls"), "w", encoding="utf-8") as fh:
        fh.write(sls(objs, edges, reverse=True))
    return directory


def salt_order(directory, tree):
    """`([obj], None)` — salt's requisite-resolved order, or `(None, why)`.

    ⚑ AN ABSENT OR FAILING SALT IS A **HOLE**, NEVER A PASS.  A3 compares two readings;
    if the second one could not be taken there is no differential, and reporting that as
    green would be the *fact-about-the-method-read-as-a-fact-about-the-substrate* error.
    The reason is returned and printed.
    """
    exe = SALT_CALL if os.path.exists(SALT_CALL) else "salt-call"
    try:
        p = subprocess.run(
            [
                exe,
                "--local",
                "--config-dir=" + directory,
                "--out=json",
                "state.apply",
                tree,
                "test=True",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (OSError, subprocess.SubprocessError) as e:  # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, e)
    try:
        res = json.loads(p.stdout)["local"]
    except (ValueError, KeyError, TypeError):
        return None, "salt produced no readable JSON (rc=%d): %s" % (
            p.returncode,
            (p.stderr or p.stdout or "")[:200].replace("\n", " "),
        )
    if not isinstance(res, dict):
        return None, "salt reported %r" % (res,)
    got = []
    for _k, v in res.items():
        if not isinstance(v, dict) or "__run_num__" not in v:
            return None, "salt state result without __run_num__: %r" % (v,)
        kind, _, name = v["__id__"].partition("-")
        got.append((v["__run_num__"], (kind, name)))
    return [o for _n, o in sorted(got)], None


# ── (7) WHAT THIS AUDIT CANNOT SEE — printed with EVERY verdict ──────────────────────
#
# ⚑⚑ A GREEN RESULT MUST NOT BE READ AS COVERAGE.  ⒦'s lesson is the reason this block
# exists and the reason the SHARPEST entry is COMPUTED rather than prose: the hole that
# mattered was named in a plan file and in a memory — the two places a reader of a green
# verdict does not look — while the printed list held six lesser ones.
BLIND = (
    "an object created by anything other than `schema_decl.ddl()` — a migration, an "
    "`ALTER TABLE`, a hand-run statement.  ⚑ THIS IS NOT HYPOTHETICAL: `obs.seq`'s "
    "residue records a column *reached only by ALTER* whose CREATE had never been "
    "rendered, so the declaration and the live store disagreed indefinitely with "
    "nothing failing",
    "a dependency postgres knows about and the DECLARATION does not — a trigger, a "
    "sequence owned by a column, a rule, a generated column, a partition parent.  The "
    "graph is read off `MD`/`INDEXES`/`SHADOWS`, so anything the model does not carry "
    "is invisible to it however loudly `pg_depend` would say otherwise",
    "a view that is not a declared `schema_decl.SHADOWS` entry: its body is never "
    "compiled, so its bases contribute no edge and it is not torn down at all",
    "a relation named at RUNTIME inside a shadow body (an f-string, a `%s` in relation "
    "position) — `sql_rw` is a positional lexer over a literal, inherited from ⒣",
    "ROW-LEVEL lifetime.  This is the lifecycle of the OBJECT, not of the data in it: "
    "`TIER_BELOW` is asserted here as a DDL teardown order, while the drain it was "
    "written for retires ROWS.  A tier whose relation must outlive another's rows is "
    "the same declaration read at a different grain, and nothing here checks the grain",
    "the DEPENDENT layer — query fragments, `sql_lift` statements, every caller that "
    "names a relation.  ⚑ DELIBERATELY OUT OF SCOPE (increment 1 is the DDL objects "
    "only); the reader for it EXISTS (`_pycodemod_sql.sql_rw` / `sql_rel_roles`) and "
    "is unused here, which is a named gap and not a missing capability",
)


def blind(tiers, declared, ex, life):
    """`BLIND` plus the two holes that are COUNTS, so they can be paid down visibly."""
    names = sorted(set(tiers.values()))
    total = len(names) * (len(names) - 1) // 2
    rel = {frozenset(p) for p in declared[0] if p[0] != p[1]}
    import schema_decl as D

    nfk = sum(1 for x, ys in ex.items() for y in ys if x[0] == "table" and y[0] == "table")
    return BLIND + (
        "an object pair the DECLARATION leaves unordered: %d of %d tier pairs are "
        "declared, so A1/A2 cannot fire on the other %d.  A teardown between two "
        "unordered tiers is constrained by EXISTENCE alone, which says nothing about "
        "lifetime.  It shrinks only by declaring a witnessed pair in "
        "`schema_decl.TIER_BELOW`." % (len(rel), total, total - len(rel)),
        "a table→table dependency: **%d declared**.  `schema_decl` imports no "
        "`ForeignKey`, so `MD.sorted_tables` sorts %d tables by NOTHING but their names "
        "and every inter-table ordering claim in this graph comes from the view body "
        "alone.  Declaring the referential constraints the ingest already assumes would "
        "make this number the measure of the gap rather than its absence."
        % (nfk, len(D.MD.sorted_tables)),
    )


# ── (8) THE LIVE READING ─────────────────────────────────────────────────────────────
def read(declared=None):
    """Everything the live declaration says, as one bundle."""
    import schema_decl as D

    objs = objects()
    ex, unknown = exist_edges()
    tiers = TR.tier_of_relation()
    owner = {v: t for v, (_s, t) in D.SHADOWS.items()}
    for ix in D.INDEXES:
        owner[ix.name] = ix.table.name
    sh, bad = shadowed()
    if declared is None:
        declared = TR.declared_below()
    life = life_edges(objs, tiers, owner, declared)
    emit, unparsed = emitted()
    return dict(
        objs=objs,
        ex=ex,
        life=life,
        tiers=tiers,
        owner=owner,
        shadows=sh,
        bad_shadows=bad,
        bases=TR.shadow_bases(),
        declared=declared,
        emit=emit,
        unparsed=unparsed,
        unknown=unknown,
    )


def check(declared=None, with_salt=True, directory=None):
    """`(violations, holes, R)` — the judgement over the live declaration."""
    import tempfile

    R = read(declared)
    v = audit(
        R["objs"],
        R["ex"],
        R["life"],
        R["tiers"],
        R["owner"],
        R["shadows"],
        R["bases"],
        R["declared"],
        emit=R["emit"],
    )
    holes = []
    for view, want, hit in R["bad_shadows"]:
        holes.append(
            "shadow %s matches %d relation(s) by column list %s — the "
            "reconstruction target is not derivable, so A1 cannot judge it" % (view, len(hit), want)
        )
    for r in sorted(R["unknown"]):
        holes.append(
            "a shadow body names %r, which is neither a declared table nor a "
            "declared shadow — no edge was derived for it" % r
        )
    for u in R["unparsed"]:
        holes.append("ddl() emitted a statement this reader could not head-parse: %s" % u)
    if with_salt:
        d = directory or tempfile.mkdtemp(prefix="ddl-salt-")
        emit_tree(d, R["objs"], merge(R["ex"], R["life"]))
        run, why = salt_order(d, "teardown")
        if run is None:
            holes.append("salt did not produce an order, so A3 was NOT taken: %s" % why)
        else:
            v += salt_linearises(R["objs"], merge(R["ex"], R["life"]), run)
    else:
        holes.append("salt was not run (--no-salt), so A3 was NOT taken")
    return v, holes, R


def _print(violations, holes, R):
    for h in holes:
        print("  HOLE      %s" % h)
    for rule, subject, detail in violations:
        print("  %s VIOLATION  %s" % (rule, subject))
        print("      %s" % detail)
        print("      rule: %s" % RULES[rule])
    seq = sequence(R["objs"], merge(R["ex"], R["life"]))
    print(
        "  population: %d object(s) — %d table(s), %d index(es), %d view(s)"
        % (
            len(R["objs"]),
            sum(1 for k, _n in R["objs"] if k == "table"),
            sum(1 for k, _n in R["objs"] if k == "index"),
            sum(1 for k, _n in R["objs"] if k == "view"),
        )
    )
    print(
        "  edges: %d EXISTENCE (mechanical, generated), %d LIFETIME "
        "(from TIER_BELOW, %d declared pair(s) closed to %d)"
        % (
            sum(len(x) for x in R["ex"].values()),
            sum(len(x) for x in R["life"].values()),
            len(R["declared"][1]),
            len(R["declared"][0]),
        )
    )
    if seq is None:
        print("  teardown order: NONE — existence and lifetime CONTRADICT (see A2)")
    else:
        print("  teardown order (derived, first dropped first):")
        print("      " + "  →  ".join("%s %s" % o for o in seq))
    print("  ⚑ WHAT THIS AUDIT CANNOT SEE — a green result is not coverage:")
    for b in blind(R["tiers"], R["declared"], R["ex"], R["life"]):
        print("      · " + b)


# ── (9) THE TEARDOWN, DEMONSTRATED ───────────────────────────────────────────────────
def _run_drops(con, stmts):
    """`[(sql, None | error)]` — each statement attempted, the first failure recorded.

    ⚑ ONE STATEMENT AT A TIME AND THE CONNECTION IS AUTOCOMMIT, which is what makes the
    contrast readable: postgres aborts a whole transaction on any error, so a batched
    teardown would report the FIRST failure and then a cascade of
    `InFailedSqlTransaction` naming nothing.  `sandbox_connect` opens autocommit, so each
    DROP is its own transaction and the failure names the object that actually refused.
    """
    out = []
    for s in stmts:
        try:
            con.cursor().execute(s)
            out.append((s, None))
        except Exception as e:  # noqa: BLE001
            out.append((s, "%s: %s" % (type(e).__name__, str(e).strip().split("\n")[0])))
            break
    return out


def demo():
    """Build, tear down naively, tear down derived — in TWO private schemas.

    ⚑⚑ TWO FIXTURES AND NOT ONE, BECAUSE THE NAIVE RUN LEAVES THE SCHEMA HALF-DROPPED.
    Reusing it would make the derived run's success a fact about what the failure
    happened to leave behind rather than about the order.

    ⚑ PRIVATE SCHEMAS VIA `sandbox_fixture`, `reset=False` UNDERNEATH.  A corpus fixpoint
    writes the shared sandbox namespace; `sandbox_fixture`'s own note records that a
    per-fixture `reset=True` is what left later suites reading
    `UndefinedTable: relation "ref" does not exist`.

    ⚑⚑ AND THE PRIVACY WAS ONLY EVER `search_path`-DEEP.  These two fixtures are private
    namespaces, but the DROPs went out UNQUALIFIED, so what made them land in the right
    one was a session setting rather than the statement.  The schema now travels from
    `fixture_schema` — the same function `sandbox_fixture` uses to CREATE it, so the
    target named in the SQL and the namespace actually built cannot disagree.
    """
    import schema_rows

    R = read()
    seq = sequence(R["objs"], merge(R["ex"], R["life"]))
    out = {}
    ns_naive = schema_rows.fixture_schema("ddl_lifecycle_naive")
    ns_derived = schema_rows.fixture_schema("ddl_lifecycle_derived")
    con = schema_rows.sandbox_fixture("ddl_lifecycle_naive")
    out["built"] = sorted(schema_rows.relations(con))
    out["naive"] = _run_drops(con, naive_drop_statements(ns_naive))
    con2 = schema_rows.sandbox_fixture("ddl_lifecycle_derived")
    out["derived"] = _run_drops(con2, drop_statements(seq, ns_derived))
    out["left"] = sorted(schema_rows.relations(con2))
    out["seq"] = seq
    return out


def _print_demo(d):
    print("  BUILT (private schema, from the declaration): %d relation(s)" % len(d["built"]))
    nf = [(s, e) for s, e in d["naive"] if e]
    print("\n  ── NAIVE teardown — reversed(MD.sorted_tables), no CASCADE ──")
    print(
        "      %d statement(s) attempted, %d succeeded before the refusal"
        % (len(d["naive"]), len(d["naive"]) - len(nf))
    )
    for s, e in d["naive"]:
        print("      %-34s %s" % (s, e if e else "ok"))
    print("\n  ── DERIVED teardown — the existence ∪ lifetime order, no CASCADE ──")
    for s, e in d["derived"]:
        print("      %-34s %s" % (s, e if e else "ok"))
    df = [(s, e) for s, e in d["derived"] if e]
    print(
        "      %d statement(s), %d failure(s); %d relation(s) left in the schema"
        % (len(d["derived"]), len(df), len(d["left"]))
    )


# ── (10) THE CASES — the audit SHOWN REFUSING before it is shown passing ─────────────
def _perturb(pairs, drop=None, invert=None):
    """`TIER_BELOW` with one pair removed or one pair reversed — a DECLARATION fixture.

    ⚑ THE LIVE DECLARATION IS NEVER MUTATED.  `schema_decl.TIER_BELOW` is a module-level
    tuple; editing it in a case would leak into every later case in the same process and
    into any suite sharing the interpreter.  A perturbation is a VALUE passed in, which
    is the same reason `tier_readset.analyse` takes its population as a parameter.
    """
    out = []
    for lo, hi, why in pairs:
        if drop is not None and (lo, hi) == drop:
            continue
        if invert is not None and (lo, hi) == invert:
            out.append((hi, lo, "PERTURBED: " + why))
            continue
        out.append((lo, hi, why))
    return tuple(out)


def _selftest():
    import schema_decl as D

    # ⚑ IMPORTED FOR THE NAMESPACE AUTHORITY, NOT FOR A CONNECTION.  `fixture_schema`
    # is a pure function of the fixture name; reading it here does NOT reach the store,
    # which is what lets the schema-qualification cases run with postgres unreachable.
    import schema_rows as _SR
    import tempfile

    cases = []

    def check_(label, got, want):
        cases.append((label, got == want, got, want))

    R = read()
    objs, ex, tiers, owner = R["objs"], R["ex"], R["tiers"], R["owner"]
    bases, sh = R["bases"], R["shadows"]

    # ── the MECHANICAL half: the generated population and graph ──────────────────
    check_(
        "the declared population and ddl()'s emitted population agree",
        sorted(set(objs) ^ set(R["emit"])),
        [],
    )
    check_("every ddl() statement head-parses", R["unparsed"], [])
    check_(
        "the shadow's reconstruction target is derived by COLUMN MATCH, uniquely",
        sh,
        {"core_decoded_shadow": "core_decoded"},
    )
    check_(
        "...and it is NOT the `_shadow` name suffix doing the work",
        [c.name for c in D.SHADOWS["core_decoded_shadow"][0].selected_columns],
        [c.name for c in D.MD.tables["core_decoded"].columns],
    )
    check_(
        "every index edge points at its own table",
        sorted(
            {(x[1], y[1]) for x, ys in ex.items() for y in ys if x[0] == "index"}
            - {(ix.name, ix.table.name) for ix in D.INDEXES}
        ),
        [],
    )
    # ⚑⚑ THE FINDING, AS A CASE.  Not a note in a docstring: a number that fails loudly
    # the moment someone declares a ForeignKey, so the claim cannot go stale silently.
    check_(
        "MEASURED: the model declares ZERO table→table (ForeignKey) edges",
        sum(1 for x, ys in ex.items() for y in ys if x[0] == "table" and y[0] == "table"),
        0,
    )
    check_(
        "...so the ONLY inter-relation edges are the shadow's bases",
        sorted(y[1] for x, ys in ex.items() for y in ys if x[0] == "view"),
        ["dec_node", "dec_root", "dec_scalar", "dec_val"],
    )

    # ── the teardown itself ──────────────────────────────────────────────────────
    seq = sequence(objs, merge(ex, R["life"]))
    check_(
        "the derived teardown covers the declared population exactly once",
        (seq is not None and sorted(seq) == sorted(objs) and len(seq) == len(objs)),
        True,
    )
    pos = {o: i for i, o in enumerate(seq or [])}
    check_(
        "the VIEW is dropped before every relation its body selects",
        [
            b
            for b in sorted(bases["core_decoded_shadow"])
            if pos[("view", "core_decoded_shadow")] > pos[("table", b)]
        ],
        [],
    )
    check_(
        "every index is dropped before its table",
        [ix.name for ix in D.INDEXES if pos[("index", ix.name)] > pos[("table", ix.table.name)]],
        [],
    )
    # ⚑ THE LIFETIME CONSTRAINT IS LOAD-BEARING IN THE TEARDOWN AND ABSENT FROM THE
    # CREATE ORDER — the asymmetry this file's docstring names.  `sourced < tree` puts
    # `core_decoded` before `dec_node` on the way DOWN, while `ddl()` emits
    # `core_decoded` FIRST on the way up (alphabetically).  Both correct; different
    # graphs.
    check_(
        "the DECLARED lifetime order constrains the teardown: sourced before tree",
        pos[("table", "core_decoded")] < pos[("table", "dec_node")],
        True,
    )
    check_(
        "...and the CREATE order does NOT carry that constraint (it is existence-only)",
        R["emit"].index(("table", "core_decoded")) < R["emit"].index(("table", "dec_node")),
        True,
    )
    check_(
        "the naive teardown is EXACTLY reversed(MD.sorted_tables) and names no view",
        (
            len(naive_drop_statements("fx_case")),
            len(D.MD.sorted_tables),
            any("shadow" in s for s in naive_drop_statements("fx_case")),
        ),
        (len(D.MD.sorted_tables), len(D.MD.sorted_tables), False),
    )
    check_(
        "no DROP asks postgres to work out the order (no CASCADE)",
        [s for s in drop_statements(seq, "fx_case") if "CASCADE" in s],
        [],
    )

    # ── the TARGET, not only the ORDER ───────────────────────────────────────────
    # ⚑⚑ THIS INCREMENT'S WHOLE THESIS IS DERIVED, CORRECTLY-ORDERED DESTRUCTION, AND IT
    # GOT THE ORDER RIGHT WHILE LEAVING THE TARGET AMBIGUOUS.  Every statement here used
    # to read `DROP TABLE "dec_val"` — a quoted identifier and no schema, so the object
    # it destroys is whatever `search_path` resolves at teardown.  `dec_val` exists in
    # SIXTEEN schemas of `substrate_sandbox`; the demo hit the right one because
    # `sandbox_fixture` had set `search_path` on that same connection, i.e. BY LUCK AND
    # NOT BY MECHANISM — and `search_path` is precisely what a concurrent fixture
    # mutates.  A teardown derived to the statement and ambiguous at the target is not
    # a derived teardown.
    #
    # ⚑ THE SCHEMA IS A REQUIRED PARAMETER AND NOT A DEFAULT, so an unqualified emission
    # is impossible by construction rather than merely discouraged.  These cases FAIL
    # against the pre-change code twice over: `drop_statements(seq)` took one argument,
    # and its output carried no namespace at all.
    check_(
        "every DROP is SCHEMA-QUALIFIED — the target is named, not resolved",
        [s for s in drop_statements(seq, "fx_case") if '"fx_case".' not in s],
        [],
    )
    check_(
        "...the naive teardown too — the straw man must not be safer than the point",
        [s for s in naive_drop_statements("fx_case") if '"fx_case".' not in s],
        [],
    )
    check_(
        'the qualified form is exactly `DROP <kind> "schema"."name"`',
        drop_statements([("table", "dec_val")], "fx_case"),
        ['DROP TABLE "fx_case"."dec_val"'],
    )

    # ⚑ AND THE SCHEMA CANNOT BE OMITTED.  A defaulted parameter would let a caller
    # re-create the ambiguity silently; a TypeError is a caller that must say which
    # namespace it is destroying.
    def _unqualified():
        try:
            drop_statements(seq)
            return "accepted"
        except TypeError:
            return "refused"

    check_("REFUSED: emitting a teardown without naming its schema", _unqualified(), "refused")
    # ⚑⚑ AND THE QUALIFICATION COMES FROM WHERE THE OBJECT WAS CREATED, NOT FROM
    # `current_schema()`.  Papering it with `current_schema()` would re-create exactly
    # the same ambiguity one layer down — it reads `search_path` too, just later.  The
    # only code that KNOWS the namespace is the one that made it, so
    # `schema_rows.fixture_schema` is the single authority and `sandbox_fixture` itself
    # resolves through it; a second spelling of `"fx_" + sanitize(name)` would be a
    # target that agrees by coincidence.
    check_(
        "the namespace is derived from the fixture that CREATES it, not search_path",
        _SR.fixture_schema("ddl_lifecycle_derived"),
        "fx_ddl_lifecycle_derived",
    )

    # ── the LIVE audit passes ────────────────────────────────────────────────────
    live = audit(objs, ex, R["life"], tiers, owner, sh, bases, R["declared"], emit=R["emit"])
    check_("the LIVE declaration passes the audit", live, [])

    # ── SHOWN REFUSING (1): a DECLARED pair DROPPED ──────────────────────────────
    # ⚑ THE SHADOW'S BODY IS UNCHANGED.  Only the declaration moved, which is the point:
    # the generated half cannot disagree with itself, so every finding this tool can
    # produce comes from the half a human had to write a reason for.
    d_drop = TR.declared_below(_perturb(D.TIER_BELOW, drop=("sourced", "valstage")))
    v = audit(
        objs,
        ex,
        life_edges(objs, tiers, owner, d_drop),
        tiers,
        owner,
        sh,
        bases,
        d_drop,
        emit=R["emit"],
    )
    check_(
        "REFUSED: dropping `sourced < valstage` — the shadow still reads dec_val",
        [(r, s) for r, s, _d in v],
        [("A1", "core_decoded_shadow reads dec_val")],
    )
    check_(
        "...and the refusal prints BOTH sides, naming the absent declaration",
        [("DERIVED" in d and "NEITHER direction" in d) for _r, _s, d in v],
        [True],
    )

    # ── SHOWN REFUSING (2): a DECLARED pair INVERTED ─────────────────────────────
    d_inv = TR.declared_below(_perturb(D.TIER_BELOW, invert=("sourced", "tree")))
    v = audit(
        objs,
        ex,
        life_edges(objs, tiers, owner, d_inv),
        tiers,
        owner,
        sh,
        bases,
        d_inv,
        emit=R["emit"],
    )
    check_(
        "REFUSED: inverting `sourced < tree` — the shadow reads a DECLARED-LOWER tier",
        sorted({(r, s) for r, s, _d in v if r == "A1"}),
        [
            ("A1", "core_decoded_shadow reads dec_node"),
            ("A1", "core_decoded_shadow reads dec_root"),
        ],
    )
    check_(
        "...and the refusal QUOTES the declared pair's own `why`",
        any("DECLARED THE OTHER WAY" in d and "retire_sql" in d for _r, _s, d in v),
        True,
    )
    # ⚑⚑ A PREDICTION REFUTED BY THE MEASUREMENT, KEPT AS A CASE RATHER THAN CORRECTED
    # SILENTLY.  I expected this perturbation to fire A1 ALONE — the shadow reading a
    # declared-lower tier — and wrote the case that way.  It ALSO fires A2, and the
    # reason is a real property of the graph rather than a leak between the rules:
    # `sourced < valstage` (still declared) puts `core_decoded` before the shadow, the
    # EXISTENCE graph puts the shadow before `dec_node`, and the inverted `tree <
    # sourced` puts `dec_node` back before `core_decoded` — a three-hop cycle.  So a
    # single inverted pair is caught TWICE, by two independent readings, and the case
    # now asserts both.  ⚑ The two rules being able to agree is what makes a
    # DISAGREEMENT between them informative later.
    check_(
        "...and the SAME inversion is caught independently by A2 (a 3-hop cycle)",
        any(r == "A2" and s.count("→") == 3 for r, s, _d in v),
        True,
    )

    # ── SHOWN REFUSING (3): existence and lifetime CONTRADICT (A2) ───────────────
    # ⚑⚑ THIS IS THE PERTURBATION THAT COULD NOT BE FAKED BY A1.  `tree < valstage` says
    # the tree tier drains first; the EXISTENCE graph says the shadow (a `valstage`
    # object, by `SHADOWS`' own placement argument) must be dropped before `dec_node` (a
    # `tree` object).  Neither is a downward read — they are two orders that cannot both
    # hold, and the union is cyclic.  It is exactly the claim `SHADOWS`' docstring argues
    # at length (*"it is `valstage` and NOT `tree`, which looks wrong and is the only
    # correct answer"*), so this is that judgement being audited rather than trusted.
    d_a2 = TR.declared_below(D.TIER_BELOW + (("tree", "valstage", "PERTURBED"),))
    v = audit(
        objs,
        ex,
        life_edges(objs, tiers, owner, d_a2),
        tiers,
        owner,
        sh,
        bases,
        d_a2,
        emit=R["emit"],
    )
    check_(
        "REFUSED: `tree < valstage` contradicts the shadow's existence dependency",
        sorted({r for r, _s, _d in v}),
        ["A2"],
    )
    check_(
        "...and there is then NO teardown order to report",
        sequence(objs, merge(ex, life_edges(objs, tiers, owner, d_a2))),
        None,
    )
    check_(
        "...and the refusal names the cycle with both endpoints",
        all("view core_decoded_shadow" in s and "dec_" in s for r, s, _d in v if r == "A2"),
        True,
    )

    # ── SHOWN REFUSING (4): the MECHANICAL half, perturbed ───────────────────────
    # ⚑ A0b IS THE ONE RULE OVER THE GENERATED HALF, AND IT IS NOT VACUOUS: it judges
    # `ddl()`'s HAND-ARRANGED emit order (tables, then indexes, then views — three
    # conventions, not a computed order) against the derived graph.  Reversing the emit
    # is exactly the ⟡view-purge hazard, quoted: *"postgres accepts a view over a
    # missing table at CREATE time only to fail at first SELECT, which is the shape that
    # makes an out-of-order emit look like a successful migration."*
    v = audit(
        objs, ex, R["life"], tiers, owner, sh, bases, R["declared"], emit=list(reversed(R["emit"]))
    )
    check_(
        "REFUSED: ddl() emitting the view BEFORE its base tables",
        sorted({(r, s) for r, s, _d in v if r == "A0b"})[:1],
        [("A0b", "index ix_decnode_c1")],
    )
    check_(
        "...and A0b fires on every violated edge, not just the first",
        len([1 for r, _s, _d in v if r == "A0b"]),
        sum(len(y) for y in ex.values()),
    )
    v = audit(objs[:-1], ex, R["life"], tiers, owner, sh, bases, R["declared"], emit=R["emit"])
    check_(
        "REFUSED: an object ddl() emits and no declaration this reader knows",
        [(r, s) for r, s, _d in v if r == "A0a"],
        [("A0a", "view core_decoded_shadow")],
    )

    # ── SALT: the SECOND READING, and it is a real resolver ──────────────────────
    d = tempfile.mkdtemp(prefix="ddl-salt-selftest-")
    emit_tree(d, objs, merge(ex, R["life"]))
    body = open(os.path.join(d, "teardown", "init.sls"), encoding="utf-8").read()
    check_(
        "the generated tree declares one state per object",
        body.count("test.succeed_without_changes"),
        len(objs),
    )
    check_(
        "...and NO require: edge is hand-authored — the count IS the graph's",
        body.count("      - test: "),
        sum(len(v_) for v_ in merge(ex, R["life"]).values()),
    )
    check_(
        "the CREATE tree is the TEARDOWN tree with every edge reversed",
        sorted(
            l for l in sls(objs, ex, reverse=False).split("\n") if l.startswith("      - test: ")
        )
        == sorted(
            l for l in sls(objs, ex, reverse=True).split("\n") if l.startswith("      - test: ")
        ),
        False,
    )
    run, why = salt_order(d, "teardown")
    if run is None:
        cases.append(("salt produced an order (A3 taken)", False, why, "an order"))
    else:
        check_(
            "salt resolves the requisite DAG — its order linearises the graph",
            salt_linearises(objs, merge(ex, R["life"]), run),
            [],
        )
        check_(
            "...and salt REORDERS: its first state is not the first DECLARED state",
            run[0] == objs[0],
            False,
        )
        check_(
            "...and salt's order agrees with ours on the view going first",
            run.index(("view", "core_decoded_shadow"))
            < min(run.index(("table", b)) for b in bases["core_decoded_shadow"]),
            True,
        )

    # ── the TEARDOWN, DEMONSTRATED against a live private schema ─────────────────
    # ⚑⚑ THE CONTRAST IS THE DELIVERABLE AND IT IS A CASE, NOT A PRINTOUT.  A teardown
    # order asserted and never executed is the shape this repo has paid for repeatedly;
    # the naive order must be OBSERVED failing, or "the derived one is needed" is a
    # claim about reasoning rather than about postgres.
    dd = demo()
    check_(
        "the fixture builds every declared relation",
        len(dd["built"]),
        len([1 for k, _n in objs if k in ("table", "view")]),
    )
    nf = [(s, e) for s, e in dd["naive"] if e]
    check_(
        "the NAIVE teardown FAILS — reversed(MD.sorted_tables) cannot place the view",
        (len(nf), "DependentObjectsStillExist" in (nf[0][1] if nf else "")),
        (1, True),
    )
    # ⚑ THE CASE READ THE OBJECT NAME BY QUOTE POSITION (`split('"')[1]`) AND THE
    # QUALIFICATION MOVED IT — index 1 is now the SCHEMA.  Recorded rather than quietly
    # re-indexed: it is the same defect one level up, a statement read by position
    # instead of by structure, and it FAILED LOUDLY the moment the target stopped being
    # ambiguous.  Both halves are asserted now, so the next reader cannot mistake the
    # schema for the relation.
    _stmt = nf[0][0] if nf else ""
    check_(
        "...and it fails on a table the SHADOW selects from, IN THE FIXTURE SCHEMA",
        (
            _stmt.split('"')[1] == _SR.fixture_schema("ddl_lifecycle_naive"),
            _stmt.split('"')[3] in bases["core_decoded_shadow"],
        ),
        (True, True),
    )
    check_(
        "the DERIVED teardown succeeds — every statement, no CASCADE",
        [e for _s, e in dd["derived"] if e],
        [],
    )
    check_("...and leaves the schema empty", dd["left"], [])

    for label, ok, got, want in cases:
        if not ok:
            print("  FAIL %s\n    got  %r\n    want %r" % (label, got, want))
    import rungs

    rungs.emit_record(sum(1 for _l, ok, _g, _w in cases if ok), len(cases), key="ddl_lifecycle")
    print("ddl_lifecycle selftest: %d/%d" % (sum(1 for _l, ok, _g, _w in cases if ok), len(cases)))
    return all(ok for _l, ok, _g, _w in cases)


def main():
    argv = sys.argv[1:]
    flags = set(argv)
    if "--selftest" in flags:
        return 0 if _selftest() else 1
    if "--demo" in flags:
        _print_demo(demo())
        return 0
    if "--emit" in flags:
        d = argv[argv.index("--emit") + 1]
        R = read()
        emit_tree(d, R["objs"], merge(R["ex"], R["life"]))
        print(
            "generated %s: minion, create/init.sls, teardown/init.sls "
            "(%d state(s), %d require edge(s) — all DERIVED)"
            % (d, len(R["objs"]), sum(len(v) for v in merge(R["ex"], R["life"]).values()))
        )
        return 0
    v, holes, R = check(with_salt="--no-salt" not in flags)
    if "--census" in flags:
        for o in R["objs"]:
            print(
                "  %-6s %-22s tier=%-10s depends-on=%s"
                % (
                    o[0],
                    o[1],
                    tier_of_object(o, R["tiers"], R["owner"]) or "-",
                    ", ".join("%s %s" % y for y in sorted(R["ex"].get(o, ()))) or "-",
                )
            )
        print(
            "%d object(s); %d existence edge(s)"
            % (len(R["objs"]), sum(len(x) for x in R["ex"].values()))
        )
        return 0
    if "--order" in flags:
        seq = sequence(R["objs"], merge(R["ex"], R["life"]))
        print("  CREATE   (ddl(), as emitted): " + "  →  ".join("%s %s" % o for o in R["emit"]))
        print("  TEARDOWN (derived):           " + "  →  ".join("%s %s" % o for o in (seq or [])))
        return 0
    _print(v, holes, R)
    # ⚑ A HOLE IS NOT A PASS.  An unrun salt, an unresolvable shadow target and an
    # unparsed statement each contribute an EMPTY finding set, which is
    # indistinguishable from a clean one.
    if v or holes:
        print("ddl-lifecycle (⒧): FAILED — %d violation(s), %d hole(s)." % (len(v), len(holes)))
        return 1
    print(
        "ddl-lifecycle (⒧): %d object(s), %d edge(s) — the generated graph, the "
        "derived teardown and `schema_decl.TIER_BELOW` agree, and salt's independent "
        "resolution linearises the same graph."
        % (len(R["objs"]), sum(len(x) for x in merge(R["ex"], R["life"]).values()))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
