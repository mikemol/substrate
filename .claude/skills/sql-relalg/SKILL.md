---
name: sql-relalg
description: >-
  Fire this BEFORE answering any question about this repo's SQL, its postgres store, its query
  builders, the sql-lift arc (⟡graded-relational-carrier / ⟡qinfra / ⟡L*-⟡H* ladders), or
  relational algebra in the Agda tree (the allegory, Rel, maps, the modular law) — and the
  instant you catch yourself about to say a relational capability is "missing", "not modelled",
  "residue", "irreducible", or "would need a new table". It routes to the `sql-oracle` agent,
  which holds the map and re-derives it from the owning tools. It exists because this surface is
  LARGE (a multi-GB, 100M+-row store, a compiled builder layer, a graded lift arc, a tabular
  allegory — the counts live in the generated census, never here),
  spread across ~15 modules that do not name each other, and MOVING — a research sweep read the
  compiled-query cache as STALE and minutes later the same command read FRESH. Anyone answering
  from memory answers about a tree that has already changed.
---

# The SQL / relational-algebra oracle

**Route the question; do not answer it from this file.** Dispatch the `sql-oracle` agent
(`Agent` tool, `subagent_type: "sql-oracle"`). It starts fresh, reads the generated census
below, and runs the owning tools against the tree as it is *now*. This file carries only what a
reader must not get wrong on the way there.

## When this fires

- **Any question about the store** — relations, tiers, rows, growth, locks, lifecycle, indexes,
  what a query costs, why a plan is slow.
- **Any question about the query layer** — what a builder compiles to, whether two builders
  return the same set, which relations a builder reads, whether the cache is fresh.
- **The sql-lift arc** — is this python op liftable, what does the grade mean, what is the
  residue, where did ⟡L5 / ⟡L4 / ⟡resolve-view-columns get to.
  ⚑ **⟡L4 is the source/column-identity refinement, and this file used to call it
  "⟡lift-source-identity"** — a second spelling for one thread, while `sql_lift.py`'s own header
  tags it ⟡L4. That is the `census-keyed-on-one-spelling` shape applied to a thread NAME: ask
  for the wrong spelling and the thread reads as absent. Use the file's tag.
- **Relational algebra in Agda** — the allegory, Rel, maps, converse, meet, the modular law,
  power objects, and anything asking whether Codd's operators exist here.
- **On your own tells:** "there's no table for that", "that would need a schema change", "this
  can't be expressed relationally", "it's just a python loop", "no view covers this."

## The four facts to not get wrong

**1. `CARRIER-UNMODELLED` is not `RESIDUE`, and the arc's own report says so in capitals.**
Residue is a claim about the COMPUTATION — a Merkle fold or a log-sum-exp has no SQL aggregate,
so it stays python. Carrier-unmodelled is a claim about what has been MODELLED: the walk is
already a closure and lifts the moment its carrier has a relational form, **which need not be
durable** (a `VALUES` list, a CTE, an unnest, a temp table all serve). Calling an unmodelled
carrier "residue" converts work into a wall. The census below carries both counts separately
for exactly this reason.

**2. Liftability is PROVED, not estimated.** A python op is a licensed lift exactly when its
Rel-lowering is grade-0 coherent with an SQL construct — **same interned id**, never a
similarity score. The GRADE is the boundary: bounded grade flattens to a relational normal
form (liftable); unbounded grade (a recursive walk) does not. Do not report a percentage;
there isn't one.

**3. A read against the wrong tenant returns plausible rows nobody can distinguish.**
`schema.py` takes `--sandbox` or `--live` and *warns when given neither*. State one. Setting
`SUBSTRATE_EXPLICIT_TENANT=1` makes the omission a refusal. (Memory:
`wrong-tenant-read-is-silent`.)

**4. Three words are overloaded here, and each has bitten someone.**
- **"Wedge"** is three unrelated things: the division/reconstruction algebra `a = recon q b r`
  (~60 Agda modules); the **set-relational** wedge (∩ + two residues + a subset verdict) which
  is the Codd-flavoured one and lives in python (`reuse_check.py`); and the exterior-algebra
  wedge product. "Wedge projection" has exactly one witness and means *projections out of the
  Wedge record* — not relational projection.
- **"Join"** — most `join*` names in the Agda index are `joint-gen` (Sylow subgroups) or
  `JointEntropy` (information theory). Not Codd material.
- **A registered query has two spellings that never meet** — `def q_<name>` and
  `QB.run(con, "<name>")`. `pycodemod --calls q_<name>` therefore reports a live builder as a
  DEAD CAPABILITY; `--sqlname` is the mode that joins them. (Memory:
  `census-keyed-on-one-spelling`.)


**5. ⟡assert-dont-establish — A PER-ITEM OPERATION ASSERTS ITS SCHEMA; IT NEVER CREATES IT.**
`CREATE … IF NOT EXISTS` is not free and is not idempotent-under-concurrency: **it takes the
relation lock BEFORE it can discover the object already exists.** One process reads that as a
no-op; N processes read it as a queue, and then as a deadlock.

Measured twice, in two call sites, with the second one written after the first was diagnosed:

- `ingest_core` opened with `apply(only="event")` — 13 backends lock-waiting, 11 queued on the
  identical `CREATE UNIQUE INDEX IF NOT EXISTS ix_terms_text`.
- `pack_core_sql` opened with `apply(only="obsnode")` — under `make -j 8 promote`, five workers
  on `Lock: relation` and pairs deadlocking outright on `ix_obsnode_pk`.

⚑ **THE COMMENT DEFENDING IT IS THE TELL, AND IT IS TRUE OF ONE PROCESS:** *"apply is a no-op
when present and the correct DDL when absent. There is no state to check."* Correct serially,
false at any concurrency the build actually runs at. When you read that sentence above a
per-item function, it is the defect, not the justification.

**The lift.** Establishing a tier is a BUILD-TIME act performed ONCE. A per-item operation
takes the opposite stance:

    _schema.require_indexes(con, "<tier>", label="<caller>")   # asserts; raises naming the fix

`declared_indexes` is the roster (derived from `INDEXES`, never typed), `schema.py
--check-indexes` is the human spelling, `require_indexes` the programmatic one. The rule, from
the operator: **"a reader asserts what it requires and FAILS if it is missing; no reader
creates"** — and *"per-core operations should bail if the required indexes are not already
present."*

⚑ **WHY THIS RECURS RATHER THAN STAYING FIXED:** nothing in a function's signature says whether
it runs once or per-item, so "establish on entry" reads as defensive good practice at every
site. `pycodemod --guarded apply scripts/sppf_db.py` finds 10 of 13 sites at function top —
the reflex, repeated. The census cannot rank them because the per-item/build-time distinction
is not written down anywhere the tool can read.

⚑ **AND THE FIRST DIAGNOSIS DID NOT GENERALISE, WHICH IS THE ACTUAL LESSON.** `declared_indexes`
recorded the `ingest_core` incident, named the rule, and shipped only a CLI *report* — so the
rule existed as prose with no programmatic caller, and the next per-core writer reintroduced it
verbatim. A diagnosis with no enforceable form is a diagnosis that will be made again.


**6. ⟡count-is-a-query-fact — WHEN A COUNT DOES NOT MOVE, ASK THE INDEX WHAT THE NAMES *ARE*.**
A count is a fact about the QUERY. Read as a fact about the SUBSTRATE it produces a confident
wrong answer, and the count-shaped version is harder to catch than an empty list because **a
number feels like a measurement** — an empty result at least LOOKS like an absence.

Five instances in one session, three of them mine:

- `15 names / 15 names` before and after a fix → read as *"nothing to find"*. The names had
  been RENAMED (`Gen` → `Gen-SKI`) and RE-HOMED; one `--provides` call showed it.
- `--dangling` reporting **34** and `--importers` reporting **58** for one module → both true,
  answering *breakage* and *population*. Neither is wrong; quoting one without saying which
  question it answers is.
- `11 clean / 21 untouched` inferred as a PARTITION from two counts without checking
  membership. The sets OVERLAPPED, and `--apply` would have rewired files still naming the
  missing symbols.
- `--index-size` reporting `obs_node` at 1,333,966 rows → 1,071 B/row, which reads as
  pathological bloat. `--headroom` read **38,984,199** rows → 107 B/row. The first figure was
  stale planner statistics; a healthy relation was nearly reported as corrupt.
- `--calls <name>` returning `1 def, 0 calls  ⚑ DEAD CAPABILITY` for a live function reached
  through an aliased module. **This repo deletes on `--dead`.**

⚑ **THE OPERATIONAL FORM, and it is one extra call:** when a count is the basis of a
conclusion — especially a count that DID NOT CHANGE — ask the index for the MEMBERS before
concluding anything about the substrate. `--provides`, `--rows`, `--sample`, `--at HEAD`. Each
of the five above was one call from the right answer.

⚑ **AND STATE WHICH QUESTION A COUNT ANSWERS.** `--dangling` counts imports whose target has no
source file; `--importers` counts every edge under a prefix. Reporting "34" without "of what"
is what let two sessions carry different numbers for the same module for an hour.

⚑ **A COUNT THAT MATCHES IS THE WORST CASE.** `Tm: 6 names vs 6 names` — with DIFFERENT SETS.
An audit by count passes on exactly the row that most needs to fail, which is why that row goes
FIRST in any evidence table, not the dramatic 40-vs-34 one.

## Absence claims need a witness

This surface is where "no tool covers that" is most often a fact about the METHOD. Two live
examples, both currently true of the tree:

- **Residuals / the division allegory are DELETED, not merely absent** — `Allegory.agda:128-137`
  records `Rel-DivisionAllegory` removed as dead Set₁ surface, with residuals filed as an
  unbuilt "Step 6". Several `Stencil*` headers still cite `Allegory.Division.residual-duality`,
  a **stale prose pointer to a term that no longer exists**.
- **Codd's named operators do not exist as such in Agda** — a `--prose` sweep over 3477 modules
  returns 0. The Codd-shaped content is the allegory ops plus the python `--relalg` census.

Report presence with witnesses; say "no entry for that spelling", never "no such capability".

## The census — GENERATED, do not edit

`python3 jea/metalanguage/sql_lift.py --sync-census` rewrites everything between the markers;
`--check-census` is the pre-commit drift gate. Every figure is derived from the tool that owns
it — the lift map from `sql_lift.build`, the builders from `query_defs`, the relations and
tiers from `schema_decl`. **A generated block nobody regenerates is worse than no block: it
reads as authoritative precisely because it looks derived.**

⚑ **THE CENSUS MEASURES ITSELF, so editing this repo's own tooling can move it.** The lift map
interns every `.py` in the corpus — including `sql_census.py` and the gate that reads it — so
adding a `sorted(...)` to a tool shifts the pipeline and carrier-node counts. A `--check-census`
failure right after a tooling edit is the instrument working, not a spurious alarm: re-sync.

--- BEGIN sql-census ---
⚑ **GENERATED — DO NOT EDIT BY HAND.** `python3 jea/metalanguage/sql_lift.py --sync-census`
rewrites everything between the markers; a hand edit is overwritten on the next
sync, and `--check-census` is a pre-commit gate that refuses drift. Every figure is
DERIVED from the tool that owns it — the lift map from `sql_lift.build`, the builder
count from `query_defs`, the relations and tiers from `schema_decl`. No number below
is typed by a human, which is why none of them can rot into a false claim.

```
── THE GRADED RELATIONAL CARRIER (⟡graded-relational-carrier / the sql-lift arc)
   1146 python Rel-pipelines · 52 SQL builder pipelines · ONE interned carrier (2539 nodes)
   Rel heads: Scan Filter Distinct GroupBy Agg OrderBy Limit Join
   A python op is a LICENSED LIFT exactly when its Rel-lowering is grade-0 coherent
   with an SQL construct — PROVED BY SAME-INTERNED-ID, never by similarity.

   licensed lifts .......... 120
   recursion-pole walks .... 55
     → recursion→parallel .. 2   (lifts to WITH RECURSIVE)
     → residue ............. 7   (no relational form — the honest greatest-fp)
     → carrier-unmodelled .. 46   ⚑ WORK, NOT A WALL
     → refuted ............. 0   (a residue verdict a probe overturned)
   STEER: [Filter → Distinct] first (score +0.0732 over 18 site(s))

   ⚑ CARRIER-UNMODELLED IS NOT RESIDUE. Residue is a claim about the COMPUTATION (a
     Merkle fold has no SQL aggregate). Carrier-unmodelled is a claim about what has
     been MODELLED: the walk is already a closure and lifts the moment its carrier has
     a relational form — which need not be durable (a VALUES list, a CTE, an unnest).

── THE QUERY LAYER (⟡qinfra)
   94 compiled builder(s)  ·  dialect: postgresql
   query_defs.py is the COMPILER; query_builders.py is the cached SQLAlchemy-free
   RUNTIME. `--check` gates the two against each other and pre-commit runs it.

── THE DECLARED STORE
   28 relation(s) · 10 tier(s) · 1 declared view/shadow(s)
   tiers: argperm event obsnode ref sourced sppf tree treestage valstage vocab
   ⚑ DECLARED, not live. Whether the running tenant matches is `schema.py --relations`'
     question — and it takes --sandbox or --live, because a read against the wrong
     tenant returns PLAUSIBLE ROWS nobody can distinguish.

── WHO OWNS WHICH QUESTION
   jea/metalanguage/schema.py                 the live store — census, spread, lifecycle, locks, plan
   jea/metalanguage/schema_decl.py            THE schema declaration — tables, tiers, shadows
   jea/metalanguage/store.py                  THE tenant authority — dsn, dialect, sandbox vs live
   jea/metalanguage/query_defs.py             the query COMPILER — sql, equiv, explain, scans, check
   jea/metalanguage/query_builders.py         the cached SQLAlchemy-free RUNTIME
   jea/metalanguage/query_registry.py         index priority by orbit BREADTH × direction × selectivity
   jea/metalanguage/sql_lift.py               ⟡graded-relational-carrier — which python ops LIFT
   jea/metalanguage/numpy_builders.py         the ⟡H3 numpy↔SQL hexagon (byte-exact arms)
   scratch/pycodemod.py                       --sql/--sqlname/--relname/--relalg over the python corpus
   agda/Substrate/Category/Allegory.agda      Rel as a TABULAR allegory (the modular law)
```
--- END sql-census ---

## Growing this

A missing mode is WORK, not a finding. Named gaps, each a build rather than a wall:

⚑⚑ **⟡index-coverage-wrong-store — FIXED 2026-08-20, and it had INVERTED the report.**
`_live_indexed` opened `catalog/catalog.db` with `sqlite3` (334 MB, two weeks stale) while
`_selectivity` read live postgres — **two stores in one report**. The postgres relations do not
exist in catalog.db at all, so every `PRAGMA` returned nothing, the `OperationalError` handler
swallowed it, and `_roles` defaulted them to `candidate`. MEASURED against `schema.py --ddl
--live`: `_node` has `PRIMARY KEY (node_id)`, `unit_node` has `ix_un_unit`/`ix_un_node`,
`node_child` has `ix_nc_node` — and **all three were the report's HIGHEST-BREADTH candidates
(12, 12, 10)**. Not a stale annotation: a false positive in the direction that GENERATES WORK,
proposing an index for a column that already has one. Candidates **32 → 26** once coverage read
`schema_decl.MD`/`INDEXES` (the declaration, as structure — no regex over rendered DDL). 29/29.

⚑ **AND A SELFTEST WITNESS MOVED, WHICH IS THE GATE WORKING.** The ⟡probe-join-keys cases
asserted on `node_child.node_id` — a candidate *only because* coverage was wrong. It is now
`indexed` and correctly carries no cardinality, so the property (a base-table join key gets
PROBED, not excused) re-pins to `obs_node.local_id`. Keeping the old witness would have
asserted the false positive.

⚑ **THE SPPF IS THREE THINGS, and the census does not distinguish them.** The `sppf` tier
proper is `_node`/`node_child`/`_unit`/`_unit_cod`/`unit_node` — the interned hypergraph,
*projected from* the `event` tier (`obs` 72.8M, `edge` 72.8M, `event` 19.0M), which is the
append-only source of truth. The `dec_*` family is a **separate, newer ladder** re-modelling the
decoded `.agdai` JSON as a relational CNF-2 tree — **all 0 rows live**, as are every `orbit_*`
and `graded_orbit_*`. A reader taking "11 tiers" as the shape of the store would conclude five
of them hold data. `catalog/catalog.db` is the OLD sppf.
⚑ `scripts/catalog_query.py` is a **live regression**: `_con()` correctly follows
`SUBSTRATE_STORE` to postgres (its docstring records avoiding a stale-store read) but 9 of 11
commands still name `structs`/`edges`/`in_degree`, which exist only in the SQLite file —
`summary` and `find` both raise. Its `_selftest` uses an in-memory sqlite fixture, so
`run_selftests` reads it GREEN while every command fails against the live store.

⚑ **⟡viewdef-vs-tenant — REFUTED AS FRAMED; the right frame is DEF/USE, not store-membership.**
I proposed reconciling "builder-layer view definitions against what the tenant holds." Operator:
*"This feels more SSA-shaped than anything"* — correct, and the measurement bears it out.
`modules_index` is `SELECT modules.* FROM modules`: a **USE** whose reaching **DEF** is
`view.modules`, a compiled projection. There is a definition; it is not a stored relation.

⚑⚑ **AND THE STORE QUESTION HAS NO ANSWER TO GIVE.** `_modules`/`_structs`/`_refs` exist in
**neither** postgres tenant (live 28 relations, sandbox 34) **nor** catalog.db (28) —
`--rows view.modules` raises `UndefinedTable`. Nothing lost them: per the operator, **that
family is re-derived from the SPPF rather than stored**. So there is no view to materialise and
no tenant to blame, and `SHADOWS` has exactly ONE member (`core_decoded_shadow`) because
⟡view-purge deleted `VIEWS` deliberately. The report now names the reaching def
(`structs.qname` → `qb.view.structs`) and says plainly that **a recomputed projection is not
indexable** — an index recommendation was never the right question for these. Two cases pin it
(21/21). New symbol: **⟡sppf-rederived**.

⚑ **⟡alias-scope-per-builder — CLOSED 2026-08-20.** An alias is scoped to the statement that
binds it, so resolution is per-builder. The scope was ALREADY in the corpus: `node_units` maps
a node id → the units referencing it and `Unit.name` is the builder — both built at intern time
for the breadth readout, so this is a JOIN on existing data, not a second traversal. Result:
`n.*` (Σbreadth 10) moved from *"ambiguous across builders"* to a definite answer — **an alias
over a DERIVED table in its own builders**, i.e. not indexable, the cost lives in the subquery.
That is a resolution, not a deferral.

⚑⚑ **AND THE FIRST CUT NEVER BOUND, WHILE LOOKING LIKE IT DID.** It keyed the per-builder map on
`query_defs.INTERN_BUILDERS`' bare names; `build_corpus` interns them as **`qb.<name>`** plus
nine local `q_*` (`query_registry.py:82-90`). Every lookup missed, `_scoped` returned None for
all 32 columns, the unscoped fallback answered — and the output was **byte-identical** to
before. A scoping layer that silently never binds is indistinguishable from one that works, so
three cases now assert a column RESOLVES that the corpus-wide view could only call ambiguous,
and that the map is keyed as the corpus names them (19/19).

⚑ **⟡resolve-alias-columns — PARTIALLY CLOSED 2026-08-20; the 21 were four populations.**
`query_registry` now resolves aliases from the COMPILED SQL (`FROM/JOIN <tbl> AS <alias>`), not
from name shape. What the 21 actually are: **11 unresolved prefixes** (`structs`, `modules`,
`meta`, `in_degree`, `node.*`, `s.*` — bound in no compiled builder, so a gap in the binding
map, NOT a verdict about the tree); **5 ambiguous** (`n.*` binds `_node` in one builder and
`terms` in another — resolving needs per-builder scope this column-keyed report does not
carry); **4 derived-table aliases** (`unit.*`, `shared_subtree.fanin` — a subquery, so no base
relation to index; the cost lives in the subquery); **1** reported ambiguous after a
verification catch.

⚑⚑ **AND THE FIRST CUT PRODUCED A FALSE RESOLUTION, which is worse than none.** It unioned
alias bindings across builders and reported `r.lid` → *"RESOLVED to terms.lid"* — but `terms`
is `(term_id, text)` and has no `lid`; it had matched `JOIN terms AS r` in one builder and
applied it to a predicate from another. A resolution now must name a column that EXISTS on the
target (`_cols_of`), or it reports ambiguity. Two selftest cases pin it (16/16). **An alias is
scoped to the statement that binds it**; a corpus-wide map answers "what has `r` ever meant"
when the question is "what does `r` mean here".

⚑ **⟡probe-join-keys — CLOSED 2026-08-20, and it corrects the shape of ⟡resolve-view-columns.**
`_selectivity` was fed only value filters (`op in fcols`), on the true-but-insufficient ground
that *"a join column's index utility is about direction, not cardinality."* Direction decides IF
an index could serve (`_roles` already runs it); cardinality decides WHETHER IT IS WORTH ADDING.
Six base-table join keys were reported unmeasured for a reason that was never about them.
Measured now: `node_child.node_id` 8489/19531 and `obs_node.local_id` 943927/956336 are highly
selective; `edge.clid`/`plid`/`obs.local_id` are ~64M rows and honestly report *"too big to
probe"* rather than an estimate. Three selftest cases pin it (14/14).

⚑ **AND THE `⟡resolve-view-columns` FIGURE WAS AN ARTIFACT.** The report rendered
`('  '+note) if note else '(view / absent-in-this-db …)'` — an `else` branch on an empty note,
narrating ONE cause for four. It read as "29 of 32 blocked on views." Derived properly the 32
split into: **21 SQL aliases** (⟡resolve-alias-columns — the real dominant bucket, Σbreadth 46),
**6 join keys** (now measured), 3 already-selective, 1 too-big, and **1** actual declared
view/shadow. ⟡resolve-view-columns owns `core_decoded_shadow.relpath` and nothing else.
`query_registry.py --candidates` groups by cause, because the causes have different repairs.

- **No mode ranks the 49 carrier-unmodelled by tractability.** They are the arc's declared WORK,
  and `report()` hardcodes `und[:12]` in corpus-glob order — no sort, no grouping, no full
  listing. Several cluster on ONE carrier (the `jea_pyalg.Intern` node/children structure), so
  modelling it as a `(node_id, child_idx, child_id)` relation would plausibly unlock a large
  fraction at once. The build: emit all 49, group by the carrier object the walk traverses
  (`_shallow_nodes(fn)` already computes it), rank by cluster size — the orbit-dedup fan-in
  logic already implemented for the lift side.
- **No mode attributes a census delta to a file set.** `--check-census` reports a diff, not a
  cause. Since the lift map interns `scripts/*.py`, editing this repo's tooling moves the
  census — so "did the arc move, or did I move it?" cannot currently be answered. Measured:
  three untracked scripts created this session appear as live pipeline sites.
- **No mode cross-checks a prose citation against a live term.** The `Stencil*` →
  `Allegory.Division.residual-duality` pointer is STILL LIVE at 5 comment lines across 3
  modules, citing a term deleted at `Allegory.agda:128-137`. This is the tightening-loop's
  reify-audit phase, mechanized.
- No mode aggregates the allegory's downstream dependency cone; and `scripts/sppf_*.py` sit
  outside the `toolmodes` census, so `--find wedge` cannot see `sppf_tree --tree-wedge`.

⚑ **`pack.sql` / `pack.python` is UNMEASURABLE, not deferred** — and the difference matters.
`query_defs.py --equiv pack.sql pack.python` returns *"BOTH EMPTY — UNMEASURED, not
equivalent"* and exits 1. The tool correctly refuses a vacuous pass. Promotion is blocked by
**measurability** (the parameterised licence has no bound value against the current store), not
by a deliberate choice to wait. Reporting it as "deferred" overstates how ready it is.

⚑ **`canon_syms`' blocker is CONFIRMED live, and it is a fact about the STORE, not a licence.**
`schema.py --census --live` shows the `orbit` and `argperm` tiers at **0 rows across all
relations**. So "unmigrated only because the orbit tier is empty" is true *today* — and remains,
in the code's own words, "a fact about the STORE'S STATE, not a licence to keep the python."
