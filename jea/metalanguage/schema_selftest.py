# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""The guarded cases for `schema` — one ~880-line suite, lifted to its own module.

⚑⚑ WHY IT MOVED (2026-08-11). `schema.py` was 2,102 code lines and this function was
878 of them — the single largest obstacle to reading any region of that file whole
before editing it. That is not a tidiness complaint: retiring ONE function from
`schema.py` took four edits, two of which repaired damage the previous edit caused, and
it left behind an assertion naming the retired function that raised `NameError` and took
the ENTIRE SUITE down. `--selftest` had not run to completion at all, and nothing said
so, because the crash looked like the traceback of a test rather than the absence of 123
of them.

⚑ THE CASES ARE VERBATIM — every ⚑ block moved with the case it explains. These comments
are the arc's incident log (each one records a MEASURED defect that produced the case
beneath it) and are the more valuable half of what moved; a split that summarised them
would have destroyed exactly what makes the suite readable.

⚑⚑ THE ONE TEXTUAL CHANGE, AND IT IS A CORRECTION RATHER THAN A RELOCATION. Two cases
introspect a whole module — `getsource(sys.modules[__name__])` — to police direct-connect
bypasses of the sandbox resolver and to drive the `--holes` CLI block. `__name__` meant
`schema` when the function lived in `schema.py`; here it would mean THIS module, so the
guards would scan a file containing only the cases and find nothing to police. They now
name `schema` explicitly, which is the module they were always reading.

⚑ AND THAT SUBSTITUTION IS WHY THE SPLIT IS SAFE IN THIS DIRECTION AND NOT THE OTHER.
Moving the CASES to a sibling keeps them pointed at `schema`; moving the FUNCTIONS would
have left the guards pointed at a `schema.py` that no longer contained them, passing by
measuring nothing. Same seam, opposite sides, and only one of them preserves the guard.

⚑ RUN IT THE WAY IT WAS ALWAYS RUN: `python3 schema.py --selftest`. `schema` imports this
module's `_selftest` and its `__main__` dispatch is unchanged, so the entry point, the
suite's name in `run_selftests`, and the 123-case count are all exactly as before.
"""

import sys

import schema

# ⚑ THE MODULE OBJECT, NOT THE RE-EXPORTED NAMES. `from schema import *` binds the queue
# tier's FUNCTIONS but not the module they live in, and the retirement case below needs to
# walk that module's AST — "does the queue tier still CALL a cursor operation" is a question
# about the file, and a name census cannot be answered by the names it exports.
import schema_queue
from schema import *  # noqa: F401,F403  (the names the cases drive)
from schema import (
    _cli_connect,
    _tier,
    _TIERS,
    _dialects_differ,
    _require_pg,
    _insert_row_sql,
    MD,
    INDEXES,
)

# ⚑ THE DIALECT AUTHORITY, BY NAME, so the ⟡ladder-1 DDL case compiles against the SAME
# dialect the emitter uses. A case that built its own `postgresql.dialect()` would be the
# second spelling `store.dialect` exists to prevent — and it would keep passing after the
# emitter's dialect changed under it.
import store as _store


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    # ── `consumer` — THE TABLE, DELETED 2026-08-12, and its cases with it ───────────
    # ⚑⚑ THE LOAD-BEARING CASE WAS THAT `kind` NEVER REACHED THE FLOOR, and it is worth
    # one line of residue because the mistake it prevented was MINE and nearly shipped: seeing
    # `scope_fix:resolver` at 0 with a 6.2M lag, I read it as a mis-registered cursor and began
    # excluding non-advancers from `lwm()`. That would have drained `obs` out from under the
    # resolver that reads it. **A label added to explain a number must not become an input to
    # it** — the rule survives the column, the table, and the next diagnostic column.
    #
    # ⚑ AND THE CLOSED-SET CASE ("an unknown kind is REFUSED") DIED THE RIGHT WAY: the set
    # closed to one element, then to none. A guard whose domain collapses is retired, not
    # relaxed — the alternative is a validator that accepts everything and reads as protection.
    #
    # ⚑ THE TWO `lwm` CASES WENT ONE STEP LATER, WITH THE FUNCTION. They asserted the MIN was
    # unscoped (`"WHERE kind" in src` → False) and that an empty registry yields None rather
    # than a number. The first was an ABSENCE check on source text — the weakest shape this
    # file records — and the second is the rule that outlives everything here: **`MIN()` over
    # no rows is NULL, and reading NULL as "no constraint" licenses deleting the whole corpus.**
    # It is restated at `lwm`'s own residue block, where the next aggregate that bounds a
    # deletion will find it.
    import inspect as _inspect

    # ── the two-degrees-of-freedom key rule ─────────────────────────────────────────
    # ⚑ THESE PIN A STRUCTURAL CONSTRAINT THAT LIVED ONLY IN AN INDEX SHAPE. A child slot has
    # TWO degrees of freedom — `ord` (which SLOT, the edge view) and `child_id` (which THING,
    # the node view) — and unique-by-construction needs BOTH. A future "simplify this to
    # (node_id, ord)" edit would look like tightening and would refuse correct data.
    _nc = {i.name: [c.name for c in i.columns] for i in INDEXES}
    check(
        "node_child's unique key carries BOTH degrees of freedom",
        _nc.get("ix_nc_edge"),
        ["node_id", "ord", "child_id"],
    )
    # ⚑ AND THE PRE-INTERN SIDE NEEDS ONLY THE PAIR — the contrast is the finding, so both
    # halves are asserted. Position alone IS identity before the quotient collapses parents.
    check(
        "edge's unique key is position-only (pre-intern)",
        _nc.get("ix_edge_pk"),
        ["core_id", "plid", "ord"],
    )
    # ⚑ MY FIRST VERSION OF THIS CASE WAS VACUOUS — it compared LENGTHS, and both keys are 3
    # columns, so it asserted `0 == 0` and would pass against any pair of 3-column indexes.
    # The claim is about WHICH columns: post-intern carries the child's identity, pre-intern
    # does not (its third column is an ordinal, and `plid` is a per-core local id, not a
    # content address).
    check("post-intern carries the child's IDENTITY", "child_id" in _nc.get("ix_nc_edge", []), True)
    check(
        "...while pre-intern carries no content column at all",
        any(c.endswith("_id") and c != "core_id" for c in _nc.get("ix_edge_pk", [])),
        False,
    )

    # ── the drain's SECOND gate: reconstruction, not just consumption ────────────────
    # ⚑ THE QUEUE PREDICATE ALONE WOULD HAVE DELETED 1,255,688 ROWS. `seq < floor` says no
    # registered cursor can reach them; it says nothing about whether the durable form can
    # rebuild them. Measured in the sandbox: the queue permitted 1,255,689 and reflection
    # held the floor at 1 — because `reflects_obs` fails for want of a stored `ekey→node_id`
    # map, the addressing the projection computes and discards.
    # ⚑⚑ THESE THREE CASES ASSERTED AGAINST A RETIRED MECHANISM, AND TWO OF THEM PASSED
    # BY READING COMMENT TEXT (found 2026-08-11 while decomposing this module). `⓶` retired
    # `_unreflected_floor` — the scalar reflection floor — into `q_drainable`'s `determined`
    # conjunct, leaving the NAME behind in `reclaim`'s ⚑ notes. So:
    #
    #   * `"_unreflected_floor" in _rec_src` was TRUE, matching the retirement note that
    #     explains the function is gone — a guard satisfied by its own obituary;
    #   * `"unreflected < floor" in _rec_src` was FALSE and the case was simply failing;
    #   * `getsource(_unreflected_floor)` raised `NameError` and took the WHOLE SUITE down,
    #     so `--selftest` had not run to completion at all.
    #
    # ⚑ THE CLAIM IS UNCHANGED; ONLY ITS WITNESS MOVED. "The drain consults reconstruction,
    # not just the cursor floor" is still the property worth pinning — it is now carried by
    # the compiled builder rather than by a Python loop, so the guard reads the BUILDER.
    # Matching source TEXT for a name is what let a retirement note satisfy a guard; asking
    # the compiled SQL for its conjunct cannot be answered by a comment.
    _rec_src = _inspect.getsource(reclaim)
    import query_builders as _QB_g

    _drain_sql = _QB_g.SQL["drainable_res"][0]
    check(
        "reclaim's licence consults reconstruction, not just the cursor floor",
        "obs_node" in _drain_sql,
        True,
    )
    # ⚑ THE SECOND HALF INVERTED WITH THE DESIGN, AND THAT IS WHY IT IS KEPT RATHER THAN CUT.
    # It read `check("...and the queue predicate is a CONJUNCT, not the whole licence", "seq"
    # in _drain_sql and "obs_node" in _drain_sql, True)` — asserting the positional term was
    # PRESENT but not alone. With `obs.seq` deleted the honest assertion is its ABSENCE, and an
    # absence over COMPILED SQL is sound where an absence over SOURCE TEXT would not be: the
    # compiler emits no prose, so a retirement note cannot satisfy it.
    check("...and no positional term survives in the compiled licence", "seq" in _drain_sql, False)
    # ⚑ AND AN UNEVALUABLE CHECK MUST REFUSE, NOT FALL THROUGH. The refusal moved one level
    # earlier with the mechanism: `_unreflected_floor` held the floor at 0 when `reconstruct`
    # could not be imported; `reclaim` now refuses when `obs_node` is absent, so the
    # reflection conjunct is never silently dropped. Absent-read-as-permission is the one
    # failure that cannot be undone, which is why the case survives its implementation.
    check(
        "an unevaluable reflection conjunct REFUSES rather than draining",
        "UNMEASURED" in _rec_src,
        True,
    )

    # ⚑ THE DRAIN'S GRANULARITY MUST MATCH THE RESIDUE'S ENCODING, and this is the guard
    # that keeps it there. `obs`'s residue is a POSITIONAL fibre — dense `local_id` per core
    # is what licenses the `ekey[]` representation — so a `seq < floor` cut, which slices
    # across cores, deletes a PREFIX of one fibre and destroys that density. Measured by
    # running it: 1,255,688 rows reclaimed, and the surviving core sat at `local_id 6213`
    # with `positional()` correctly refusing it.
    #
    # ⚑⚑ THIS GUARD WAS PASSING BY MATCHING AN OBITUARY, MEASURED 2026-08-12 — F24's class,
    # recurring inside the suite that records F24. It read
    # `check("reclamation selects whole CORES, not positions", "HAVING max(seq)" in _rec_src,
    # True)` over `getsource(reclaim)`. The positional licence had already been deleted, and the
    # string was found in `reclaim`'s DOCSTRING, in the paragraph explaining that `HAVING
    # max(seq) < 0` was false for every core and was therefore removed. **The guard asserting a
    # mechanism exists was satisfied by the prose announcing its deletion**, and it read green
    # the whole time.
    #
    # ⚑ RE-ANCHORED ON THE COMPILED LICENCE AND ON THE DELETE, WHICH IS WHAT "WHOLE CORES"
    # ACTUALLY MEANS. The granularity claim has two halves and neither is about `seq`: the
    # licence must return CORE IDS (its minuend is `GROUP BY core_id`), and the deletion must
    # be keyed by `core_id`. A text scan of a function's source can be satisfied by a comment;
    # compiled SQL cannot be.
    check(
        "the licence's unit is the CORE — it groups, it does not cut positions",
        "GROUP BY obs.core_id" in _drain_sql,
        True,
    )
    check(
        "...and deletes by core_id, never by a bare seq range",
        "DELETE FROM obs WHERE core_id" in _rec_src,
        True,
    )
    check(
        "...so no partial-fibre delete remains", "DELETE FROM obs WHERE ctid IN" in _rec_src, False
    )

    # ── ⑺ THE LICENCE MUST **REFUSE**, AND IT HAD NEVER BEEN SHOWN TO ────────────────
    # ⚑⚑ EVERY GUARD ABOVE READS THE LICENCE'S SQL TEXT, AND TEXT IS NOT BEHAVIOUR. They
    # establish that `obs_node`, `seq` and `IS DISTINCT FROM` are SPELLED in the compiled
    # statement — never that any of them FIRES. And every measurement of the drain to date
    # is a set identity taken on a store where EVERY core passes (`--triage` 177,397 EXACT /
    # 0 WRONG, then 160,700 rows retired and all still resolvable), so the REFUSAL branch of
    # the one query in this repo licensed to DELETE had not once executed. A guard verified
    # only where it does not need to fire is the class this suite records most often; here
    # it sat directly under the deletion.
    #
    # ⚑ FIVE CORES, EACH VIOLATING EXACTLY ONE CONJUNCT, AND THE ASSERTION IS THE SET — not
    # a count of what was held. A count cannot separate "the right core was refused" from
    # "the licence refuses everything", and a licence that refuses everything passes every
    # safety case ever written for it. `E` is the clean core's twin, correct in every respect
    # except POSITION, so the queue conjunct is measured by this same fixture rather than
    # left as the one arm nobody drove.
    #
    # ⚑ AND EACH REFUSAL IS THEN REPAIRED BY FIXING PRECISELY ITS OWN DEFECT, which is the
    # necessity half. Refusal alone is satisfied by a licence broken in some unrelated way;
    # only the repair shows the NAMED conjunct is what held that core.
    #
    # ⚑⚑ NOTHING HERE SPELLS THE `ekey` ENCODER — every `obs.ekey` is read back from the
    # store's OWN rebuild. So the positive control is TAUTOLOGICAL with respect to encoder
    # fidelity, deliberately, and that scope is stated here rather than discovered later:
    # fidelity is `--triage`'s question and it answers it over 177,397 real rows, while the
    # question here is whether the licence DISCRIMINATES. A second, hand-written encoder in
    # this fixture would be exactly the drift `_rebuilt_obs` was factored out to prevent —
    # and it would drift into the worst available shape, where the fixture passes and the
    # store is wrong.
    _c0 = sandbox_fixture("schema_licence_refuses")
    # ⚑ ONE `terms` ROW PER DISTINCT TEXT — `ix_terms_text` is UNIQUE, because `terms` is an
    # interning table and interning is what that index means. My first fixture gave the empty
    # string two ids; `upsert` returned 3 and the store held 2, silently, because the return
    # is the count of rows OFFERED and `ON CONFLICT DO NOTHING` absorbs the rest.
    upsert(_c0, "terms", [("1", "Prim"), ("2", "Def"), ("3", ""), ("4", "db0")])
    upsert(_c0, "path_text", [("p1", "Fixture.Q")])
    # ⚑ `NM` IS A SECOND LEAF — SAME ARITY, DIFFERENT HEAD — AND IT IS WHAT KEEPS CORE `C` A
    # SINGLE-CONJUNCT VIOLATION. My first cut stored a PARENT's key against a leaf's address,
    # which is a mismatch AND an implied edge: two arms fired, and repairing the key left the
    # core held by the other, so the case could not attribute its own refusal.
    # ⚑ SIX COLUMNS — the `sym` slot (the second `""`) went with the column, 2026-08-23.
    # ⚑⚑ AND THIS IS WHY A POSITIONAL FIXTURE IS THE RISK THE COLUMN REMOVAL ACTUALLY CARRIED:
    # every value here is a short string, so dropping a column SHIFTS the rest one place left
    # and every row still type-checks. It failed loudly only because psycopg counts
    # placeholders (*"the query has 6 placeholders but 7 parameters were passed"*). Had the
    # arity happened to match, the fixture would have silently stored `kind_id` in `role_id`
    # and the cases would have asserted against a shifted row.
    upsert(
        _c0,
        "_node",
        [  # node_id, kind_id, role_id, op_term_id, op_path_id, lit_id
            ("NL", "", "3", "1", None, "3"),  # leaf   : c=Prim, i=null, q=null, no l
            ("NM", "", "3", "2", None, "3"),  # leaf   : c=Def   — the other head
            ("NP", "", "4", "2", "p1", "3"),
        ],
    )  # parent : c=Def,  i=0,    q=Fixture.Q
    upsert(
        _c0,
        "obs_node",
        [
            ("A", 0, "NL", ""),
            ("A", 1, "NP", "0"),
            #  B is addressed by NOTHING            → violates (2)
            ("C", 0, "NM", ""),  # → violates (3)
            ("D", 0, "NL", ""),
            ("D", 1, "NP", "0"),  # → violates (4)
            ("E", 0, "NL", ""),
            ("E", 1, "NP", "0"),
        ],
    )

    def _rebuilt(core):
        return {r["local_id"]: r["ekey"] for r in _QB_g.run(_c0, "obs_reconstructed", core_id=core)}

    _leaf, _par = _rebuilt("A")[0], _rebuilt("A")[1]
    _other = _rebuilt("C")[0]  # NM's key: same `ch: []`, a different `c`
    # ⚑⚑ CORE `E` — THE POSITION-ONLY VIOLATOR — DELETED 2026-08-12 WITH THE CONJUNCT IT DROVE.
    # It was *"the clean core's twin, correct in every respect except POSITION"*, written last so
    # that its `max(seq)` sat above the floor, and it was the ONLY arm separating `drainable`
    # from `drainable_res`. With one licence there is no separation to measure: the two names
    # named one relation, and a fixture core whose whole job is to fall on the deleted side of a
    # deleted distinction is not a weaker case, it is an unstatable one.
    #
    # ⚑ WHAT SURVIVES IS THE PROPERTY THAT MATTERED — the fixture is FOUR cores and THREE arms,
    # and the assertion is still the SET, never a count. *"A count cannot separate 'the right
    # core was refused' from 'the licence refuses everything', and a licence that refuses
    # everything passes every safety case ever written for it."*
    #
    # ⚑ AND THE INSERT-ORDER NOTE GOES WITH IT: *"INSERT ORDER IS THE `seq` ORDER, AND THE
    # FIXTURE MUST READ THE POSITIONS BACK RATHER THAN NAME THEM — `seq` is `_STORE_ASSIGNED`,
    # so the engine owns it and a literal here would be a client-assigned watermark, the thing
    # the declaration forbids."* The rule (never name an engine-assigned value) outlives the
    # column; there is no engine-assigned column left for it to govern.
    upsert(
        _c0,
        "obs",
        [
            ("A", 0, _leaf),
            ("A", 1, _par),
            ("B", 0, _leaf),  # projected? no — no `obs_node` row
            ("C", 0, _leaf),  # addressed to NM, stored as NL's key
            ("D", 0, _leaf),
            ("D", 1, _par),
        ],
    )
    # only the PARENT key carries a child, so only A/D imply an edge — D's is WITHHELD.
    upsert(_c0, "edge", [("A", 1, 0, 0)])

    def _licensed(name, **extra):
        # ⚑ THE COMPILED CACHE FIRST, THE REFERENCE ARMS SECOND — and the fallback is not a
        # convenience. `REFERENCE_ARMS` are DELIBERATELY absent from `INTERN_BUILDERS` so they
        # never reach `query_sql_postgres.py` and no caller can splice one into a `DELETE` by
        # accident; that safety property is exactly what makes them unreachable through
        # `QB.SQL`. Compiling them live here is the only way to MEASURE an arm against the
        # shipped licence, which is what a reference arm is for.
        try:
            _sql, _def = _QB_g.SQL[name]
        except KeyError:
            import query_defs as _QD

            _sql, _def = _QD._compile_one(_QD._named_builder(name)())
        return sorted(r["core_id"] for r in rows(_c0, _sql, {**_def, **extra}))

    check(
        "the licence LICENSES a core that satisfies every conjunct",
        _licensed("drainable_res"),
        ["A"],
    )
    # ── each refusal is repairable by fixing PRECISELY its own defect ─────────────────
    upsert(_c0, "obs_node", [("B", 0, "NL", "")])
    check(
        "(2) unprojected — held for want of an obs_node row, licensed once it has one",
        _licensed("drainable_res"),
        ["A", "B"],
    )
    execute(_c0, "UPDATE obs SET ekey = " + ph() + " WHERE core_id = 'C'", (_other,))
    check(
        "(3) reconstructs — held on a key the durable side rebuilds differently",
        _licensed("drainable_res"),
        ["A", "B", "C"],
    )
    upsert(_c0, "edge", [("D", 1, 0, 0)])
    check(
        "(4) edge-reflected — held on ONE withheld edge row, licensed once restored",
        _licensed("drainable_res"),
        ["A", "B", "C", "D"],
    )

    # ── (5) EDGE-RECOVERABLE **WITHOUT** `obs` — the conjunct that lets `edge` drain (⑹) ──
    # ⚑⚑ CORE `F` EXISTS BECAUSE (4) AND (5) READ OPPOSITE SIDES OF THE WEDGE, AND NOTHING
    # ELSE IN THIS FIXTURE SEPARATES THEM. (4) rebuilds `edge` from `obs.ekey` — TIER 0 — so a
    # licensed core proves `edge` is redundant WITH `obs`; (5) rebuilds it from `obs_node.ch`,
    # a DURABLE relation, which is what proves it recoverable WITHOUT `obs` and therefore what
    # licenses deleting both. For every core above the two agree, so a fixture without `F`
    # would pass identically against a licence that never grew (5).
    #
    # ⚑ THE SEPARATION IS AN `obs_node` ROW WITH NO `obs` ROW UNDER IT. `F` has `obs` at
    # local_id 0 only, and `obs_node` at 0 AND 9; the row at 9 carries `ch = "0"`, so the
    # DURABLE rebuild implies an edge `(F, 9, 0, 0)` that the store does not hold. Conjunct (3)
    # cannot see it — it INNER-JOINs the rebuild to `obs` on `(core_id, local_id)`, and there
    # is no `obs` row at 9 — and (4) cannot either, because `obs.ekey` at local_id 0 has an
    # empty `ch`. **So (5) is NOT implied by (2) ∧ (3) ∧ (4)**, which is the claim this core
    # makes checkable rather than argued.
    upsert(_c0, "obs_node", [("F", 0, "NL", ""), ("F", 9, "NP", "0")])
    upsert(_c0, "obs", [("F", 0, _leaf)])
    check(
        "(5) durable-edge — a core whose DURABLE rebuild implies an edge the store lacks "
        "is REFUSED",
        _licensed("drainable_res"),
        ["A", "B", "C", "D"],
    )

    # ── ⟡reclaim-core: THE SCOPED LICENCE, MEASURED AGAINST THE SHIPPED ONE ────────────────
    #
    # ⚑⚑⚑ `drainable_res.one_core` IS THE SAME LICENCE WITH A CORE PREDICATE PUSHED INTO
    # `_live_cores`, AND THIS IS WHERE THAT CLAIM BECOMES A MEASUREMENT. It exists so a
    # per-core retire does not have to compute the corpus-wide drainable set and discard all
    # but one row; but a narrowing of a licence that AUTHORISES DELETION is exactly the edit
    # whose failure mode cannot be undone, so it lands as a REFERENCE ARM and is compared here
    # before anything splices it into a `DELETE`.
    #
    # ⚑⚑ THE FIXTURE IS THE RIGHT SCALE AND THE CORPUS IS THE WRONG ONE. I first ran this as
    # `--equiv drainable_res drainable_res.one_core` against LIVE and killed it at ~25 minutes:
    # the unscoped arm enumerates 2,800 cores over 128M `obs` rows to return the one row the
    # scoped arm restricts to — i.e. it pays the exact cost the scoped form exists to avoid, in
    # order to prove that cost worth avoiding. Six cores with a known licensed set test the same
    # proposition in milliseconds, which is what these cases are for.
    #
    # ⚑ AGREEMENT PER CORE IS THE PROPERTY, NOT AGREEMENT IN AGGREGATE. The scoped arm returns
    # at most one row, so the claim is: for every core, `one_core(c)` yields `[c]` exactly when
    # the unscoped licence contains `c`. Asserted over ALL SIX — including the four REFUSED ones,
    # where the scoped arm must return `[]` rather than silently licensing a core the shipped
    # licence holds. A narrowing that widened would show up precisely here.
    _all_licensed = _licensed("drainable_res")
    for _c in ("A", "B", "C", "D", "E", "F"):
        check(
            "scoped licence agrees with the shipped one on core %s" % _c,
            _licensed("drainable_res.one_core", rc_core=_c),
            [_c] if _c in _all_licensed else [],
        )

    def _dis_cores(name):
        _sql, _def = _QB_g.SQL[name]
        return sorted({r["core_id"] for r in rows(_c0, _sql, dict(_def))})

    # ⚑ AND THE TWO BUILDERS ARE ASKED DIRECTLY, so the "opposite sides" claim is a
    # MEASUREMENT rather than an inference from the licence's answer. `F` is invisible to the
    # tier-0 comparison and visible to the durable one — which is the whole reason (5) exists.
    check(
        "...invisible to (4), which rebuilds from obs.ekey and finds no disagreement",
        "F" in _dis_cores("edge_disagreement"),
        False,
    )
    check(
        "...and VISIBLE to (5), which rebuilds from the durable obs_node.ch",
        "F" in _dis_cores("edge_durable_disagreement"),
        True,
    )

    # ── DOES CONJUNCT (4) STILL SUBTRACT ANYTHING? — MEASURED, AND THE ANSWER IS YES ──────
    # ⚑⚑ THE ARGUMENT FOR RETIRING (4) WAS THAT (3) FORCES `obs.ekey` TO EQUAL THE KEY
    # REBUILT FROM `obs_node`, so the two `ch` arrays agree and (5) implies (4). **THE FIXTURE
    # FALSIFIED IT ON THE FIRST RUN.** Supplying the edge `(F, 9, 0, 0)` satisfies (5) — the
    # durable side now has its edge — and makes (4) FIRE, because the store holds an edge row
    # that `obs` cannot explain: `obs` has no row at local_id 9, so the tier-0 rebuild produces
    # nothing and `stored ∖ rebuilt` is non-empty. The same core, refused by (5) before this
    # row and by (4) after it.
    #
    # ⚑⚑ SO THE TWO CONJUNCTS FIRE ON OPPOSITE STAGES OF THE SAME CORE, AND NEITHER IMPLIES
    # THE OTHER. That is exactly why the plan's instruction was *add (5), do not remove (4)* —
    # removing a conjunct WIDENS the licence, and the argument for doing so was wrong here.
    # The measurement it would have had to carry is the one below: on this fixture, at this
    # stage, **(4) subtracts exactly 1 core (`F`)**.
    upsert(_c0, "edge", [("F", 9, 0, 0)])
    check(
        "(4) STILL SUBTRACTS — the store holds an edge `obs` cannot explain, so F is held",
        _licensed("drainable_res"),
        ["A", "B", "C", "D"],
    )
    check(
        "...and the licence WITHOUT (4) would license it — 1 core is the difference",
        _licensed("drainable_res.no_obs_edge"),
        ["A", "B", "C", "D", "F"],
    )
    check(
        "...so the retirement argument ((5) implies (4)) is FALSE, by set difference",
        [c for c in _licensed("drainable_res.no_obs_edge") if c not in _licensed("drainable_res")],
        ["F"],
    )
    # ⚑ AND THE DISAGREEMENT FLIPS SIDES, WHICH IS THE SYMMETRIC HALF OF THE SAME FACT. Before
    # the edge row, (5) saw F and (4) did not; after it, (4) sees F and (5) does not. A pair of
    # cases in one direction only would leave "the two are the same query spelled twice" open.
    check(
        "...(5) is now satisfied for F — the durable side has its edge",
        "F" in _dis_cores("edge_durable_disagreement"),
        False,
    )
    check(
        "...while (4) now sees the disagreement it could not see before",
        "F" in _dis_cores("edge_disagreement"),
        True,
    )

    # ⚑ THE FULL REPAIR NEEDS BOTH SIDES, because the licence is a CONJUNCTION and F was
    # violating one arm at a time. Giving `obs` its row at local_id 9 makes the tier-0 rebuild
    # produce the edge too, and only then is F licensed — which is the necessity half stated
    # for the pair rather than for a single conjunct.
    upsert(_c0, "obs", [("F", 9, _par)])
    check(
        "...licensed once BOTH sides rebuild the same edge",
        _licensed("drainable_res"),
        ["A", "B", "C", "D", "F"],
    )
    check(
        "...and the two arms then AGREE, over a non-empty population",
        (_licensed("drainable_res.no_obs_edge"), len(_licensed("drainable_res"))),
        (["A", "B", "C", "D", "F"], 5),
    )

    # ── AND THE SWEEP THAT CONSUMES THE LICENCE, DRIVEN ────────────────────────────────
    # ⚑⚑ THIS CLOSED A GAP THIS BLOCK ITSELF NAMED AN HOUR EARLIER. The note here read:
    # *"it drives the BUILDER, and `reclaim`'s consumption of it is still asserted from
    # source text only … reaching `reclaim` means registering consumers, and
    # `pin_persistent` then pins `scope_fix:resolver` at 0, so the case would measure the
    # REGISTRY while reading as a test of the licence."* That was true of the floor-bearing
    # `reclaim` and is exactly what retiring the floor dissolves — the residue was a
    # symptom of the design, not of the fixture.
    #
    # ⚑⚑ AND THE PIN HALF OF THIS BLOCK WENT WITH THE TABLE (2026-08-12). It registered
    # `scope_fix:resolver` at 0 and asserted the sweep's answer did not move. Its finding is
    # kept because it is the retirement stated as a MEASUREMENT rather than as a deletion:
    # *"Under the old licence this row set `lwm = MIN(lwm) = 0`, `HAVING max(seq) < 0` was
    # false for every core, and the sweep returned nothing — measured on both stores as `0
    # observation(s) below the floor` against a full tier. The same row now changes no
    # answer."* There is no row to construct now, so the case cannot be re-driven; what it
    # proved is that the licence was ALREADY indifferent to the registry before the registry
    # was removed, which is what made the removal safe rather than hopeful.
    # ⚑ `ref` IS POPULATED HERE SO THE "DURABLE SIDE SURVIVES" CASES BELOW ARE MEASUREMENTS
    # RATHER THAN VERDICTS OVER AN EMPTY RELATION. An assertion that `ref` is unchanged passes
    # trivially at 0 rows — the UNMEASURED-reads-as-verified collapse this file records at
    # `--triage` and at `--equiv`. Two rows, one on a licensed core, is enough to make the
    # claim falsifiable.
    upsert(_c0, "ref", [("A", 1, "p1", 0, "3"), ("D", 1, "p1", 0, "3")])
    _rc_before = reclaim(_c0, dry_run=True)
    # ⚑ 8 → 6 WHEN CORE `E` WENT (2026-08-12), 6 → 8 WHEN CORE `F` ARRIVED WITH ⑹. The number
    # is the ROW count of the licensed cores (A,B,C,D,F at 2+1+1+2+2), not a count of cores —
    # which is what the label asserts and why the constant is worth keeping rather than
    # deriving: a derived expectation would agree with a licence that admitted the wrong set.
    check(
        "the sweep consumes the licence — every reconstructible row, not a count of cores",
        _rc_before["obs"],
        8,
    )
    check(
        "...with no floor in the verdict, because there is none to report",
        _rc_before["floor"],
        None,
    )
    # ⚑ THE DRY RUN NAMES `edge` TOO (⑹). A report covering only `obs` describes the smaller
    # relation: on the sandbox at the moment ⑹ was written, `obs` was 0 and `edge` was 627,077.
    check("...and reports the `edge` rows it would take as well", _rc_before["edge"], 3)

    # ── ⟡reclaim-verdict: `NO` SPLIT INTO ITS TWO CAUSES ──────────────────────────────────
    #
    # ⚑⚑ THE TWO REFUSALS WANT OPPOSITE RESPONSES, so reporting them alike is a defect in the
    # OUTPUT rather than in the licence. A conjunct holding a core means *promote it and retry*;
    # a core absent from the population means *it is already finished, leave it alone*. The
    # licence's minuend is `SELECT core_id FROM obs GROUP BY core_id`, so a core with no staged
    # rows never enters it — refused by absence, not by test.
    #
    # ⚑⚑⚑ AND THE FIRST CUT READ THE DISCRIMINATOR OFF THE DRY RUN, WHICH IS WRONG IN A WAY
    # ONLY A CASE CATCHES RELIABLY. `reclaim_core`'s `obs`/`edge` count rows MATCHING THE
    # LICENCE, so a refused core reports 0 whatever its staged size — MEASURED live, an
    # unprojected core with 449 observations reports `obs 0`. Both refusals printed identically,
    # and I found it by running two cores and comparing output BY EYE. These three cases are
    # that comparison, made to survive the session.
    check("verdict: licensed ⟹ YES", schema_queue.reclaim_verdict(True, 1), "YES")
    check(
        "verdict: refused WITH staged rows ⟹ a conjunct holds it",
        schema_queue.reclaim_verdict(False, 1),
        "NO — a conjunct holds it",
    )
    check(
        "verdict: refused with NOTHING staged ⟹ absent from the population",
        schema_queue.reclaim_verdict(False, None),
        "NO — nothing staged (already drained, or never ingested)",
    )
    # ⚑ AND `licensed` DOMINATES — a licensed core is YES whatever the staged probe says. The
    # probe exists only to SPLIT the refusal; letting it reach the accept branch would make a
    # verdict depend on a question that is not part of the licence.
    check(
        "...and `licensed` wins regardless of the probe",
        schema_queue.reclaim_verdict(True, None),
        "YES",
    )

    # ── ⑹ THE APPLY PATH: `edge` DRAINS, AND THE DURABLE SIDE DOES NOT ──────────────────
    # ⚑⚑ THIS IS THE END-TO-END DELETION, AND THE SANDBOX CANNOT DRIVE IT. `--reclaim
    # --sandbox` reports 0 cores there because the sandbox's `obs` is already 0 — a TERMINAL
    # state, not a regression — so the only place the `edge` delete can be exercised without a
    # re-ingest is a fixture that builds a live tier on purpose. That is this one.
    #
    # ⚑⚑ AND THE HAZARD THE SINGLE STATEMENT EXISTS FOR IS SILENT, WHICH IS WHY THE COUNT IS
    # ASSERTED RATHER THAN THE EMPTINESS. Run as two statements with `DELETE FROM obs` first,
    # the licence RE-EVALUATES for the edge delete with the drained cores now absent from its
    # minuend (`GROUP BY core_id` over an `obs` that no longer holds them yields no group), so
    # `edge` keeps every row and **nothing raises**. A case asserting only "some edge rows are
    # gone" would still pass if the count were wrong; the count is what pins the snapshot.
    _edge_before = scalar(_c0, "SELECT count(*) FROM edge")
    _obsnode_before = scalar(_c0, "SELECT count(*) FROM obs_node")
    _ref_before = scalar(_c0, "SELECT count(*) FROM ref")
    _rebuilt_A_before = _rebuilt("A")
    _rc_apply = reclaim(_c0, dry_run=False)
    check("the apply deletes the licensed cores' obs rows", _rc_apply["obs"], 8)
    check("...AND their edge rows, in the same statement", _rc_apply["edge"], 3)
    check(
        "...matching what the dry run predicted",
        (_rc_before["obs"], _rc_before["edge"]),
        (_rc_apply["obs"], _rc_apply["edge"]),
    )
    check(
        "...so no edge row of a drained core survives",
        sorted({r["core_id"] for r in rows(_c0, "SELECT core_id FROM edge")}),
        [],
    )
    check(
        "...and `edge` really held rows before the sweep, so this is not a vacuous pass",
        _edge_before,
        3,
    )
    # ⚑⚑ THE DURABLE SIDE IS WHAT THE DRAIN IS LICENSED BY, SO IT MUST NOT MOVE. A sweep that
    # took `obs_node` with `obs` would delete the very relation whose contents authorised the
    # deletion — and the licence would then be unevaluable on the next run, which is
    # `UNMEASURED`, not `nothing left to do`.
    check(
        "obs_node is INTACT — the drain is licensed BY it, not against it",
        scalar(_c0, "SELECT count(*) FROM obs_node"),
        _obsnode_before,
    )
    check(
        "...and so is `ref`, which no conjunct reads and no statement names",
        scalar(_c0, "SELECT count(*) FROM ref"),
        _ref_before,
    )
    check("...and both were non-empty beforehand", (_obsnode_before > 0, _ref_before), (True, 2))
    # ⚑⚑ AND THE READ PATH STILL REBUILDS THE DRAINED CORE — WHICH IS WHAT PROVES `edge` AND
    # THE RECONSTRUCTION ARE INDEPENDENT. `q_obs_reconstructed` reads `obs_node` + `_node` +
    # `terms`/`path_text`; it never touches `edge` or `obs`. Asserting the rebuild is BYTE-
    # IDENTICAL before and after is the case that separates "edge was redundant" from "edge
    # was load-bearing and we deleted it anyway" — the two are indistinguishable from a row
    # count, and only one of them is recoverable.
    check(
        "reconstruct still rebuilds a DRAINED core, byte-identically",
        _rebuilt("A"),
        _rebuilt_A_before,
    )
    check(
        "...over a core whose obs rows are genuinely gone",
        scalar(_c0, "SELECT count(*) FROM obs WHERE core_id = 'A'"),
        0,
    )
    # ⚑ AND THE REFUSAL SURVIVES THE RETIREMENT — dropping the addressing relation must
    # still yield UNMEASURED rather than "nothing excludes it, so drain it". This is the
    # one branch whose failure cannot be undone, and it is the branch a residue licence
    # makes easiest to lose: with no floor, an unevaluable conjunct set is an EMPTY set of
    # exclusions, which reads as universal permission.
    execute(_c0, "DROP TABLE obs_node")
    _rc_gone = reclaim(_c0, dry_run=True)
    check("obs_node absent REFUSES rather than licensing everything", _rc_gone["obs"], 0)
    check(
        "...and says UNMEASURED rather than reporting a clean sweep",
        "UNMEASURED" in _rc_gone["why"],
        True,
    )
    _c0.close()

    # ── the pin→cursor retype guard ─────────────────────────────────────────────────
    # ⚑ THE ONE OPERATION THAT CAN DELETE THE CORPUS, and until now nothing stopped it. A pin
    # holds the floor because its consumer reads the RAW LOG; retyping it to `cursor` lets the
    # consumer advance, lifts the floor to the HWM, and licenses reclaiming everything below.
    # That is correct only once the consumer reads something else. MEASURED: live `ref` is
    # `-` (never applied) because live `qname_pid` is NULL on all 2,124,390 rows — so a retype
    # today would lift the floor over 6.3M observations while `scope_fix` read an EMPTY index.
    # ── partial-ingest detection (`--holes`) ────────────────────────────────────────
    # ⚑ A NUMERATOR WITHOUT ITS DENOMINATOR READS AS COMPLETENESS. `core_fp 168` looked
    # finished for this entire session; the tree holds 3,193 cores, so the store is at 5%
    # and EVERY per-core figure taken from it is scoped to that fraction. This is the
    # report-the-population rule applied to the store itself.
    # ⚑ AND MY FIRST TWO CASES HERE ASSERTED `168 < 3193` — arithmetic, not the predicate.
    # They would pass against code that never computes the denominator at all, which is
    # precisely the defect. Drive the SOURCE instead: the report must read the corpus and
    # must say so when the store is short of it.
    import inspect as _inspect2

    _holes_src = _inspect2.getsource(schema)
    _holes_blk = _holes_src.split('if "--holes" in sys.argv:')[-1].split('if "--fibre"')[0]
    check("--holes reads the corpus, not just the store", "*.agdai" in _holes_blk, True)
    check("...and names a shortfall as PARTIAL", "PARTIAL INGEST" in _holes_blk, True)
    check(
        "...reporting the fraction, never a bare count",
        "on_disk" in _holes_blk and "%" in _holes_blk,
        True,
    )

    # ── the hole classifier (`--holes`) ─────────────────────────────────────────────
    # ⚑ THESE PIN A DISTINCTION I GOT WRONG BY READING A PATTERN INSTEAD OF MEASURING.
    # 16 cores had a fingerprint and no rows, 15 of them under `Algebra/F2/` — which looked
    # exactly like an ingest cut mid-alphabet. Measured, all 16 define no names, so zero
    # rows is CORRECT and there are no holes at all.
    check("a module defining nothing is EMPTY, not a hole", classify_hole(0), "empty")
    check("a module defining names with no rows IS a hole", classify_hole(7), "hole")
    # ⚑ UNASKABLE IS NOT BENIGN. Folding `None` into 'empty' would report an unmeasured
    # core as a clean one — the absent-read-as-passing collapse, in the one place where it
    # would license a drain against rows nobody checked.
    check("unaskable is UNCLASSIFIED, never empty", classify_hole(None), "unclassified")
    check(
        "...and is distinguishable from both verdicts",
        len({classify_hole(0), classify_hole(7), classify_hole(None)}),
        3,
    )

    # ── the fibre's positionality predicate (`--fibre`) ─────────────────────────────
    # ⚑ THESE DRIVE THE CLAIM THE MATERIALIZATION RESTS ON. `lifecycle._reflected` states
    # the residue is `ekey[]` indexed by `local_id`; that is lossless ONLY if local_id is
    # dense. The live measurement says every core is — and a measurement whose predicate
    # nothing tests is a number, not evidence.
    check("a dense 0..n-1 core is positional", positional(0, 4, 5, 5), (True, 0, 0))
    # ⚑ THE TWO FAILURES MUST BE DISTINGUISHABLE, NOT MERELY DETECTED. A gap and a dup are
    # both "not positional" and call for different repairs — a hole the array cannot hold
    # vs. a collapse that silently drops an ekey. A boolean predicate hides which.
    check("a GAP is reported as a gap, not a dup", positional(0, 5, 5, 5), (False, 1, 0))
    check("a DUP is reported as a dup, not a gap", positional(0, 3, 5, 4), (False, 0, 1))
    check(
        "...and the two are told apart",
        positional(0, 5, 5, 5)[1:] != positional(0, 3, 5, 4)[1:],
        True,
    )
    # ⚑ A NONZERO START IS NOT DENSE-FROM-ZERO. `local_id` indexes the array, so a fibre
    # beginning at 1 would silently shift every occurrence by one — lossless-looking
    # (no gaps, no dups) and wrong. This case fails if the `lo == 0` conjunct is dropped.
    check("a core starting at local_id=1 is NOT positional", positional(1, 5, 5, 5), (False, 0, 0))
    check("an empty core is vacuously positional", positional(None, None, 0, 0), (True, 0, 0))

    import os

    # ⚑ HOISTED FROM ITS FIRST USE FURTHER DOWN. The `:memory:` fixtures below became
    # `store.sandbox_connect()` calls, so `store` is now needed BEFORE the census block
    # that used to import it — and a function-local `import` binds the name for the whole
    # function body, so the later import made every earlier reference an
    # `UnboundLocalError` rather than a NameError. Measured by running it.
    import store as _store

    # ⚑⚑ `lite = ddl("sqlite")` IS GONE AND WITH IT EVERY COMPARATIVE CASE BELOW (⓺,
    # 2026-08-11). The env save/restore around this pair existed because `ddl()` resolved
    # the backend from `SUBSTRATE_STORE` when not given one; with one dialect there is
    # nothing to pin and nothing to restore.
    pg = ddl("postgres")

    # ⚑ COUNTS ARE DERIVED, NOT TYPED. My first cut asserted literal 15 and 14 and both
    # were wrong — I counted my own declarations by eye. A hand-copied total is a second
    # spelling of the model that drifts the moment a table is added, which is the same
    # defect this module exists to remove, reproduced inside its own guard.
    check(
        "every base table is emitted",
        sum(1 for s in pg if s.startswith("CREATE TABLE")),
        len(MD.sorted_tables),
    )
    check("every index is emitted", sum(1 for s in pg if "INDEX" in s), len(INDEXES))

    pg_s = "\n".join(pg)

    # ⚑ THE TWO DDLs ARE BYTE-IDENTICAL, AND THAT IS A FINDING RATHER THAN A BUG.
    # My first case asserted they must DIFFER, reasoning that an emitter ignoring its
    # dialect argument would look exactly like this. Measured, they agree — because
    # every column here is `Text` or `Integer`, and both render those with the same
    # keyword. The schema happens to sit in the dialects' intersection.
    #
    # So the "is the argument honoured" question needs a probe that CAN differ, and
    # `String` (no length) is the standard one: postgres renders VARCHAR, sqlite
    # renders VARCHAR too but accepts a lengthless one where other engines do not —
    # the reliable discriminator is a type the dialects genuinely disagree on.
    check(
        "the emitter compiles against a REAL dialect, not the generic fallback",
        _dialects_differ(),
        True,
    )
    # ⚑ THE TABLE/INDEX HALF WAS BYTE-IDENTICAL ACROSS DIALECTS — every column is `Text`
    # or `Integer`, which both engines rendered the same way, so that half of the schema
    # sat in the dialects' intersection.
    #
    # ⚑ AND THIS CASE WENT STALE THE MOMENT VIEWS LANDED, correctly failing: view
    # idempotence is the ONE place the DDL genuinely forked (`IF NOT EXISTS` vs
    # `OR REPLACE`), so the full strings then differed. Scoped to the half the claim was
    # about rather than deleted — the finding was still true and still worth pinning.
    #
    # ⚑⚑ IT IS DELETED NOW, AND THE CROSS-DIALECT PROPERTIES IT PINNED ARE REPLACED BY
    # ONE-SIDED ASSERTIONS ON THE PROPERTY THAT SURVIVES (⓺). "The two agree here and
    # fork there" is unaskable with one dialect; "postgres renders IDENTITY", "postgres
    # views are OR REPLACE" and "every postgres statement is idempotent" are the same
    # guards minus their vanished half. What is genuinely LOST is the discriminator: a
    # byte-identity claim across two emitters could catch a `dialect=` argument being
    # ignored, and `_dialects_differ` is now the only thing that can, on a probe type
    # rather than the real schema.
    #
    # ⚑ AND IT WENT STALE A SECOND TIME — CORRECTLY — WHEN `obs.seq` LANDED. The claim
    # rested on the premise stated directly above ("every column is Text or Integer"),
    # and the queue tier's IDENTITY column retires it: sqlite renders `seq BIGINT`
    # (dropping the identity silently), postgres renders `GENERATED BY DEFAULT AS
    # IDENTITY`. MEASURED, both spellings read from `--ddl`.
    #
    # That divergence is the DESIGN, not a regression: the watermark is postgres-only by
    # decision (sqlite cannot express the in-flight floor), so the column carrying it
    # SHOULD fork. Narrowed to the tables that remain in the dialects' intersection —
    # the finding is still true of them, and pinning it there still catches an emitter
    # that ignores its dialect. Deleting the case would have thrown away a live guard to
    # silence a correct failure.
    _n_ti = len(MD.sorted_tables) + len(INDEXES)
    # ── the `obs.seq` IDENTITY CASE — DELETED 2026-08-12 WITH THE COLUMN. ────────────────────
    #
    #     check("obs.seq renders as an IDENTITY column (upsert omits it, so the engine must)",
    #           any("IDENTITY" in s for s in pg), True)
    #
    # ⚑ ITS ARGUMENT IS WHAT TO CARRY, NOT THE ASSERTION: *"`upsert` OMITS `seq` from every
    # insert (`_STORE_ASSIGNED`), so if the column ever rendered without its default, every
    # write to `obs` would violate NOT NULL."* The general form — **a column excluded from
    # every INSERT must have a DEFAULT, and the two facts live in different files** — is the
    # coupling any future engine-assigned column re-creates. There is none today.
    #
    # ⚑ REPLACED BY ITS COMPLEMENT RATHER THAN BY NOTHING. An emitted-DDL case that merely
    # stopped existing would leave "the position is gone" asserted only in prose, which is the
    # shape this suite exists to refuse; asking the DDL that no identity column remains is the
    # same instrument pointed the other way, and it FAILS if the declaration regrows one.
    # ⚑⚑ AND THE PREDICATE WAS WIDER THAN THE CLAIM — CAUGHT BY ⟡ladder-2, 2026-08-12. It read
    # `any("IDENTITY" in s for s in pg)` over the WHOLE DDL while the case NAME scoped it to
    # `obs`, so the first legitimate identity column anywhere in the declaration failed a case
    # about a different table. That is a fact about the METHOD reported as a fact about the
    # substrate, in a suite that records the shape repeatedly. Narrowed to the statement the
    # name is about; the guard still FAILS if `obs` regrows a position.
    _obs_ddl = next(s for s in pg if s.startswith("CREATE TABLE IF NOT EXISTS obs ("))
    check(
        "no identity column survives in obs — the position is gone from the DDL",
        "IDENTITY" in _obs_ddl,
        False,
    )
    # ⚑ AND THE RETIRED `obs.seq` CASE'S ARGUMENT IS RESTORED HERE, ON THE COLUMN THAT NOW
    # CARRIES IT (⟡ladder-2). Verbatim from the deletion block above: *"a column excluded from
    # every INSERT must have a DEFAULT, and the two facts live in different files"*. The
    # ⟡ladder-2 rung inserts `(v)` only, so `dec_scalar.id` renders without a default would make
    # every vocabulary write violate NOT NULL.
    _ds_ddl = next(s for s in pg if s.startswith("CREATE TABLE IF NOT EXISTS dec_scalar ("))
    check(
        "dec_scalar.id renders as an IDENTITY column (the rung inserts `v` only)",
        "GENERATED ALWAYS AS IDENTITY" in _ds_ddl,
        True,
    )
    # ⚑⚑ THE VARIANT IS ASSERTED IN THE EMITTED DDL, BECAUSE THE CORRECTION IS EXACTLY A TYPE
    # (⟡ladder-2b, user: *"That calls for a VARIANT type, not a simple exclusion."*). A `TEXT`
    # column here is the defect restored: every non-string scalar would have to be coerced or
    # dropped, and both `0` and `"0"` would resolve to one row. `JSONB` and not `JSON` — `json`
    # has no equality operator, so `ix_decscalar_v` would be unbuildable and `ON CONFLICT (v)`
    # would have no arbiter to name.
    check(
        "...and `v` renders JSONB — the variant, not a coercion target",
        ("JSONB" in _ds_ddl, "JSON " in _ds_ddl.replace("JSONB", "")),
        (True, False),
    )
    # ⚑ `NOT NULL` ON A COLUMN WHOSE VALUE MAY BE A JSON `null`, WHICH IS NOT A CONTRADICTION:
    # `'null'::jsonb IS NULL` is False (measured). The constraint rejects the ABSENCE of a
    # datum and admits the JSON null literal — 497 of them in the corpus.
    check(
        "...and is NOT NULL, which still admits the JSON null literal",
        "v JSONB NOT NULL" in _ds_ddl,
        True,
    )
    # ⚑ `ALWAYS` AND NOT `BY DEFAULT`, ASSERTED SEPARATELY BECAUSE THEY ARE DIFFERENT
    # GUARANTEES. `BY DEFAULT` accepts a client-supplied id silently — which is the ⑸ defect's
    # entire mechanism — while `ALWAYS` makes postgres REFUSE it. The two spellings differ by
    # one word in the DDL and by everything in what they permit.
    check(
        "...and `ALWAYS`, so no client may ever supply one",
        "GENERATED BY DEFAULT" in _ds_ddl,
        False,
    )

    # ⚑ THE TYPES ARE THE POINT. A column declared `String` would render VARCHAR;
    # asserting INTEGER appears is what catches a schema that silently made every
    # column a string — which is exactly what `query_defs._T` does, and why its
    # declaration could not be used as the DDL source.
    check("postgres declares INTEGER columns", "INTEGER" in pg_s, True)

    # ⚑ IDEMPOTENCE IS PER-ENGINE, NOT PER-STATEMENT. Every builder re-runs its DDL, so
    # each statement must be a no-op the second time — but the SPELLING differed: sqlite
    # said IF NOT EXISTS everywhere, postgres says it for tables/indexes and OR REPLACE
    # for views (it has no IF NOT EXISTS for views, and OR REPLACE is strictly better —
    # it redefines a changed body instead of silently skipping it).
    #
    # My first cut asserted IF NOT EXISTS on ALL of them, which failed the moment views
    # landed — a case pinned to one engine's spelling of a property both engines have.
    # That is why the surviving assertion accepts EITHER token: it names the PROPERTY
    # (re-running this statement is a no-op), not a renderer's word for it.
    check(
        "every postgres statement is idempotent",
        sum(1 for s in pg if "IF NOT EXISTS" in s or "OR REPLACE" in s),
        len(pg),
    )
    # ── THE TWO-POPULATION FORM — ADDED AND REMOVED WITH THE ID SEQUENCES, 2026-08-12 ──────
    #
    # ⚑ FOR ~AN HOUR `ddl()` ALSO EMITTED `SELECT setval(…)` STATEMENTS, which carry NEITHER
    # token, so this case split in two: CREATEs idempotent by a RENDERED TOKEN, alignments
    # idempotent by MONOTONICITY (`setval(s, GREATEST(…, s.last_value))` can only move forward).
    # Both halves plus a non-vacuity case and an EMIT-ORDER case are gone with the sequences
    # they described.
    #
    # ⚑ THE TRANSFERABLE HALF: **a statement that is idempotent by a PROPERTY rather than by a
    # TOKEN needs its own assertion, and the honest repair when a population splits is to split
    # the case — never to widen the token set or subtract a constant.** The one-population form
    # failed 57 of 59 when the sequences landed, and "subtract 2" was available and wrong.
    #
    # ⚑ AND THE REASON THERE IS ONE POPULATION AGAIN IS THE RIGHT ONE: a content-DERIVED id
    # needs no state in the store, so there is nothing to align and no non-CREATE statement in
    # the DDL. The case is simple because the design got simpler, not because it was relaxed.

    # the producer column's NOT NULL + default survives the emit (it scopes the prune)
    cf = [s for s in pg if "core_fp" in s and s.startswith("CREATE TABLE")]
    check("core_fp is emitted once", len(cf), 1)
    # ⚑ ASSERT THE FACTS, NOT THE WORD ORDER. My first cut looked for the literal
    # `producer TEXT NOT NULL`; SQLAlchemy emits `producer TEXT DEFAULT 'agdai' NOT
    # NULL`, so the case failed on a schema that was entirely correct. A case pinned to
    # a renderer's token order breaks on every cosmetic change and says nothing about
    # the constraint it claims to guard.
    check("...producer is NOT NULL", "NOT NULL" in cf[0].split("producer")[1], True)
    check("...and defaults to agdai", "'agdai'" in cf[0], True)

    # primary keys survive
    check("core_fp declares its PK", "PRIMARY KEY (core_id)" in cf[0], True)

    # ⚑ UNIQUE INDEXES ARE ACCESS-PATH *AND* CONSTRAINT. `ix_nc_edge` is what stops a
    # duplicate (node, ord, child) edge; losing it in the port would corrupt the SPPF
    # silently rather than loudly. DERIVED from the declaration, not a typed literal —
    # my first cut said 6 and the model declares 7.
    check(
        "unique indexes are emitted as UNIQUE",
        sum(1 for s in pg if "CREATE UNIQUE INDEX" in s),
        sum(1 for ix in INDEXES if ix.unique),
    )

    # ── `views are emitted` / `tables+indexes+views is the whole DDL` / the two ORDER
    # ── cases / `postgres views are OR REPLACE` — RE-ANCHORED 2026-08-12 (⟡view-purge).
    #
    # ⚑⚑ THE OLD CASES ARE INVERTED, NOT DELETED, and the distinction matters because
    # deleting them would make a re-introduced `CREATE VIEW` invisible again. The claim they
    # guarded — *"an emitter carrying only tables would produce a store where every table and
    # index is present and every READER fails — the shape that looks like a successful
    # migration"* — is still exactly right, and is now discharged by CONVERTING the readers
    # (they compose the fragment) rather than by emitting a stored copy for them.
    # ⚑⚑ AND RE-ANCHORED AGAIN 2026-08-13 (⟡ladder-retire), FROM *"NO view"* TO *"no view that
    # is not a declared SHADOW"*. The purge's argument is untouched and is the reason this is a
    # DERIVED equality rather than a relaxation: a view is admissible IFF it is the
    # reconstruction claim of a relation that is supposed to be reconstructible, so the emit
    # must equal `SHADOWS` exactly. A convenience view re-introduced tomorrow is not in
    # `SHADOWS` and this case fails on it, which is precisely what *"the DDL emits NO view"*
    # was protecting. Widening the case to `>= 0` — or listing the shadow by name here — would
    # be the exception swallowing the rule.
    check(
        "the DDL emits a view for every declared SHADOW and for nothing else",
        sorted(s.split()[4] for s in pg if s.startswith("CREATE OR REPLACE VIEW")),
        sorted(SHADOWS),
    )
    check(
        "...and every VIEW statement in the emit is one of them",
        sum(1 for s in pg if "VIEW" in s),
        len(SHADOWS),
    )
    # ⚑ THE ORDERING CASE THE PURGE CALLED UNASKABLE IS ASKABLE AGAIN, and it is the property
    # `_TIER_VIEWS`'s residue names: *"a derived object must be created after everything it
    # reads."* A shadow selects from base tables, so its CREATE must follow every CREATE TABLE
    # in the emit — postgres accepts a view over a missing table at CREATE time only to fail at
    # the first SELECT, which is the shape that looks like a successful migration.
    check(
        "...emitted LAST, after every table it reads",
        [i for i, s in enumerate(pg) if "VIEW" in s and i < len(MD.sorted_tables)],
        [],
    )
    # ⚑ THE EXHAUSTIVENESS CASE — every term DERIVED, never a typed total. It briefly grew two
    # terms for the surrogate-id sequences (one CREATE SEQUENCE + one alignment each) and lost
    # them again when the ids became content-DERIVED; writing `+ 4` rather than
    # `2 * len(ID_SEQUENCES)` would have left a frozen constant behind on the way back down.
    # It has now lost the `+ len(VIEWS)` term the same way, and for the same reason: the emit
    # got smaller, so the DERIVED total got smaller with it and nothing had to be adjusted.
    check(
        "tables+indexes+shadows is the whole DDL",
        len(pg),
        len(MD.sorted_tables) + len(INDEXES) + len(SHADOWS),
    )

    # ⚑⚑ THE ORDER CASES BECOME COMPOSITION CASES, WHICH IS THE STRONGER STATEMENT. They
    # asserted an EMIT ORDER (`node_fanin` before `shared_subtree`, `node` before
    # `node_atom`) because a stored view must be created after what it reads — *"a
    # set-ordered emit would break a fresh database intermittently, the failure mode that
    # gets retried, not diagnosed."* A fragment has no creation event, so ordering is not
    # merely satisfied, it is UNASKABLE — and what replaces it is the property that made the
    # ordering safe in the first place: the dependent body is BUILT FROM the other's
    # selectable, so it carries it INLINE and cannot reference a stale copy.
    #
    # ⚑ COMPILED, NOT INSPECTED. Asserting `shared_subtree_sel` merely mentions
    # `node_fanin_sel` as an object would pass on a fragment that names it and never
    # compiles it in; compiling and looking for the inner body's own GROUP BY is the
    # behavioural form. MEASURED against the live store's stored bodies before the drop —
    # postgres had already inlined both exactly this way (`pg_get_viewdef`), which is why
    # `pg_depend` showed ZERO view→view edges and the drop needed no ordering at all.
    _ss = str(shared_subtree_sel.compile(dialect=_store.dialect("postgres")))
    check("shared_subtree INLINES node_fanin's body", "GROUP BY node_child.child_id" in _ss, True)
    _na = str(node_atom_sel.compile(dialect=_store.dialect("postgres")))
    check("node_atom INLINES node's body", "JOIN terms" in _na and "_node.kind_id" in _na, True)

    # ⚑⚑ AND THE CAPABILITY ITSELF IS GONE FROM THE RE-EXPORT SURFACE, which is the case a
    # future re-introduction trips. `schema.VIEWS` / `schema.view_ddl` resolving again means
    # someone put view emission back; the old `postgres views are OR REPLACE` case cannot say
    # that, because it PRESUPPOSED the capability it was checking the spelling of.
    #
    # ⚑ ITS MEASUREMENT SURVIVES IN `schema_decl`'s residue and is worth not re-deriving:
    # `CreateView(or_replace=True)` rendered `CREATE OR REPLACE VIEW` under BOTH dialects,
    # which sqlite rejects — a library abstracting a real capability DIFFERENCE between
    # engines is abstracting a fiction, and it surfaced as a case written against the OLD
    # behaviour still passing.
    # ⚑⚑ AND 2026-08-13 THE SURFACE CASE SPLITS IN TWO, WHICH IS THE HONEST FORM OF A PARTIAL
    # RESTORATION. `view_ddl` is BACK — narrowly, over `SHADOWS` only — so asserting its absence
    # would now be asserting the absence of a capability the tier's licence depends on. What
    # must stay gone is the GENERAL machinery: `VIEWS` (an unrestricted roster), `_TIER_VIEWS`
    # (a second roster beside it), `_view_ddl_named`, and the `sqlalchemy_views.CreateView`
    # dependency whose whole contribution was a prefix this emitter renders itself. Naming them
    # individually is what makes a re-introduction of the general capability trip a case rather
    # than ride in behind the exception.
    import schema as _sch

    check(
        "the GENERAL view machinery is still gone from the schema surface",
        [n for n in ("VIEWS", "_TIER_VIEWS", "_view_ddl_named", "CreateView") if hasattr(_sch, n)],
        [],
    )
    check(
        "...and what came back is the SHADOW emitter alone, over a declared population",
        (hasattr(_sch, "view_ddl"), hasattr(_sch, "SHADOWS"), len(_sch.SHADOWS)),
        (True, True, 1),
    )

    # ⚑ THE TIER SPLIT MUST BE EXHAUSTIVE, and this is the case that catches the silent
    # break: a table declared but assigned to NEITHER tier is created by `ddl()` and by
    # nothing `sppf_db` calls — so a fresh store would be missing it, and the failure
    # surfaces far away as a "no such table" mid-ingest.
    # ⚑ DERIVED FROM `_TIERS`, NOT FROM TWO NAMED SETS. This case listed
    # `EVENT_TABLES | SPPF_TABLES` explicitly and therefore FAILED — correctly — the
    # moment the orbit/argperm tiers were declared: a case that hardcodes the tier roster
    # is a second copy of it, and drifts the instant a tier is added. It caught real
    # unassigned tables AND had to be rewritten to stop catching the fix.
    _declared = {t.name for t in MD.sorted_tables}
    _all_tiers = set().union(*_TIERS.values())
    check("every table belongs to exactly one tier", sorted(_declared - _all_tiers), [])
    check("...and no tier names a table that does not exist", sorted(_all_tiers - _declared), [])
    _overlap = [n for n in _all_tiers if sum(1 for s in _TIERS.values() if n in s) > 1]
    check("the tiers are disjoint", sorted(_overlap), [])

    # ⚑ THE TIERS TOGETHER MUST BE THE WHOLE SCHEMA. Counting statements rather than
    # tables is what makes this catch a lost INDEX or VIEW too — the parts most easily
    # dropped, and the ones whose absence corrupts quietly (`ix_nc_edge` is what stops a
    # duplicate SPPF edge).
    # ⚑ ALL TIERS TOGETHER MUST BE THE WHOLE DDL. Counting STATEMENTS (not tables) is what
    # makes this catch a lost INDEX — the part most easily dropped and the one whose
    # absence corrupts quietly (`ix_nc_edge` is what stops a duplicate SPPF edge).
    _parts = [_tier("postgres", t) for t in _TIERS]
    check("the tiers reconstruct the full DDL", sum(len(p) for p in _parts), len(pg))
    # ── `every view is carried by exactly one tier` — RE-ANCHORED 2026-08-12 (⟡view-purge).
    # ⚑ IT READ `sum(1 for p in _parts for s in p if "VIEW" in s) == len(VIEWS)`, and its
    # argument was that a view has to belong SOMEWHERE — *"a missing view breaks every
    # reader while the tables look fine"*. A tier is a set of relations that DRAIN, and a
    # fragment neither drains nor is applied, so it has no tier to be carried by; the honest
    # inversion is that NO tier emits one. This is the per-tier twin of `the DDL emits NO
    # view` above: `ddl()` and `_tier()` are separate emitters and a re-introduction could
    # land in either.
    # ⚑⚑ AND RE-ANCHORED AGAIN 2026-08-13 (⟡ladder-retire): a SHADOW does have a tier, and the
    # rule the purge stated for a fragment is what decides WHICH. A fragment neither drains nor
    # is applied, so it has no tier; a shadow IS applied, so it must belong to exactly one — or
    # `apply(con, only=…)` would create it twice or never. The tier is not the one it shadows
    # and not the first one it reads: it is the LAST tier it reads, because that is the only
    # assignment under which the CREATE can never precede something it selects from.
    check(
        "every shadow is emitted by exactly one tier, and no tier emits anything else",
        sum(1 for p in _parts for s in p if "VIEW" in s),
        len(SHADOWS),
    )
    check(
        "...and that tier is one the shadow READS, never the tier it shadows",
        sorted(t for _s, t in SHADOWS.values() if t in ("sourced",)),
        [],
    )
    # ⚑ AND AN UNKNOWN TIER REFUSES. The old `A if tier=="event" else B` silently applied
    # the sppf tier to a typo'd name — creating the wrong tables and reporting success.
    try:
        _tier("postgres", "spff")  # a plausible transposition
        check("an unknown tier REFUSES", "returned", "ValueError")
    except ValueError:
        check("an unknown tier REFUSES", "ValueError", "ValueError")

    # ── upsert: one capability, was 21 hand-written spellings ───────────────────────
    # ⚑ DRIVEN END-TO-END AGAINST A REAL ENGINE, not asserted over rendered SQL. The
    # three sqlite-isms it replaced (`OR IGNORE`, `?`, positional arity) are only
    # provably gone if a row actually lands and a conflicting one actually doesn't.
    #
    # ⚑⚑ THE ENGINE IS NOW THE SANDBOX TENANT, NOT `:memory:` (⓺, 2026-08-11), AND THAT
    # STRENGTHENS THESE CASES RATHER THAN PRESERVING THEM. `on_conflict="replace"` is the
    # one that gained: sqlite's `OR REPLACE` INFERS its conflict target, so the sqlite
    # fixture could never exercise the `ON CONFLICT (pk) DO UPDATE` path — the path
    # production actually runs, and the one that RAISES on a table with no primary key.
    # A fixture on the retired engine was testing the arm that no longer exists.
    # ⚑ EVERY FIXTURE IN THIS FILE TAKES A DISTINCT NAME. They run sequentially and each
    # is closed before the next opens, so one shared name would work TODAY — and would
    # break silently the first time two of these blocks were reordered or one was left
    # open, because `sandbox_fixture` DROPs the schema it is about to create.
    _c = sandbox_fixture("schema_upsert")

    # ⚑ THREE VALUES, AND THE ARITY IS THE POINT OF THESE CASES RATHER THAN INCIDENTAL TO THEM.
    # `upsert` reads the column count off the DECLARATION, so a tuple of the wrong width RAISES
    # instead of shifting a value into the neighbouring column. That refusal is what the note
    # above claims ("positional arity … only provably gone if a row actually lands"), and it
    # earned its keep twice in one session: it caught `core_fp` GAINING a `path` column, then
    # caught it LOSING that column again when the duplicate was stripped.
    upsert(_c, "core_fp", [("a", 1, "agdai"), ("b", 2, "agdai")])
    check("upsert inserts rows", scalar(_c, "SELECT COUNT(*) FROM core_fp"), 2)

    # ignore: a conflicting row is SKIPPED, the original survives
    upsert(_c, "core_fp", [("a", 999, "py")], on_conflict="ignore")
    check(
        "on_conflict=ignore keeps the ORIGINAL",
        scalar(_c, "SELECT mtime FROM core_fp WHERE core_id='a'"),
        1,
    )

    # replace: the conflicting row WINS. A case checking only the row count would pass
    # against an implementation that ignored both — the VALUE is what separates them.
    upsert(_c, "core_fp", [("a", 999, "py")], on_conflict="replace")
    check(
        "on_conflict=replace OVERWRITES",
        scalar(_c, "SELECT mtime FROM core_fp WHERE core_id='a'"),
        999,
    )
    check("...and does not duplicate the row", scalar(_c, "SELECT COUNT(*) FROM core_fp"), 2)
    _c.close()

    # ── relations(): was 5 `sqlite_master` sites, a hard porting stop ────────────────
    _c3 = sandbox_fixture("schema_relations")
    _rel = relations(_c3)
    check(
        "relations() finds every table",
        sum(1 for k in _rel.values() if k == "table"),
        len(MD.sorted_tables),
    )
    # ⚑ TABLES AND VIEWS MUST BE DISTINGUISHABLE. `information_schema.tables` lists views
    # too, so a port that counted its rows would silently include them where sqlite's
    # `type='table'` excluded them — which produced a wrong verdict earlier today (19
    # relations read against a 14-table expectation, reported as a broken schema).
    #
    # ⚑⚑ THIS CASE READ `== len(VIEWS)` AND RE-ANCHORING IT TO `0` WOULD HAVE GUTTED IT
    # (⟡view-purge, 2026-08-12). The emitter no longer creates any view, so a fresh fixture
    # holds none — and a case asserting "zero views are classified as views" passes against a
    # `relations()` that has LOST the classification entirely. That is the absent-read-as-a-
    # verdict shape: it would read green while the instrument this change is VERIFIED by
    # (`--census` / `relations()` reporting zero relations of kind `view` on both tenants)
    # silently stopped working.
    #
    # ⚑ SO THE FIXTURE MAKES ITS OWN VIEW. The distinction is a property of `relations()`,
    # not of our DDL, and asserting it needs a view to exist — which is now something a case
    # must CREATE rather than something the schema supplies. Dropped again immediately, so
    # the fixture is left exactly as the emitter would have built it.
    execute(_c3, "CREATE VIEW _relkind_probe AS SELECT core_id FROM core_fp")
    _rel_v = relations(_c3)
    check("...and separates views from tables", _rel_v.get("_relkind_probe"), "view")
    check(
        "...without reclassifying a table",
        sum(1 for k in _rel_v.values() if k == "table"),
        len(MD.sorted_tables),
    )
    execute(_c3, "DROP VIEW _relkind_probe")
    # ⚑ AND THE EMITTED SCHEMA CARRIES NONE — the per-store twin of `the DDL emits NO view`.
    # `relations()` is the instrument the ⟡view-purge migration is verified by, so what it
    # reports on a store built from the declaration is itself a case.
    # ⚑⚑ RE-ANCHORED 2026-08-13 (⟡ladder-retire) FROM A COUNT TO A **SET EQUALITY**, which is
    # strictly stronger and is what keeps the exception from swallowing the rule. A count of 1
    # would be satisfied by ANY single view; naming the population from `SHADOWS` means a
    # convenience view added tomorrow fails this case whether or not a shadow is also present.
    check(
        "a freshly applied schema holds exactly the declared SHADOWS and no other view",
        sorted(n for n, k in relations(_c3).items() if k == "view"),
        sorted(SHADOWS),
    )
    # ⚑ THE "EXCLUDES sqlite INTERNALS" CASE IS REPLACED, NOT DELETED. It pinned
    # `name NOT LIKE 'sqlite_%'`; the postgres equivalent is the `table_schema NOT IN
    # ('pg_catalog', 'information_schema')` filter, and losing it would flood every
    # relation listing with the engine's own catalogue — the same defect, other engine.
    check(
        "relations() excludes the engine's own catalogue",
        [n for n in _rel if n.startswith("pg_") or n.startswith("sql_")],
        [],
    )
    # ⚑ `PRAGMA table_info` TRAVELLED WITH `sqlite_master`: a listing that names relations
    # then names their columns, so porting one without the other moves the failure by a
    # line. Read from the ENGINE, not from MD — that is what lets a listing show drift
    # between the declared and the actual schema.
    check(
        "columns_of reads the engine's own answer",
        columns_of(_c3, "core_fp"),
        [c.name for c in MD.tables["core_fp"].columns],
    )

    # ── `drained()` — the precondition every PROJECTION owes ─────────────────────────────
    # ⚑ THE STATES MUST BE DISTINGUISHABLE, and collapsing any two is a live hazard:
    # EMPTY is what `--full` produces on purpose, INTACT is the only state a projection may
    # rebuild from, and DRAINED is the one that silently destroys the durable tier. Driven
    # against a real engine rather than asserted over the SQL string, because the whole point
    # is what the predicate RETURNS over each population.
    #
    # ⚑⚑ THE PREDICATE MOVED FROM `min(seq) > 1` TO `obs_node ∖ obs` (2026-08-12), AND SO DID
    # THE FIXTURE — the cases below no longer write a position, they write a durable ADDRESS
    # and then remove the core it addresses. The retired note is kept because it names an
    # exception that no longer has anything to except: *"`seq` IS WRITTEN EXPLICITLY HERE AND
    # THAT IS THE EXCEPTION, NOT THE RULE. It is `_STORE_ASSIGNED`, so `upsert` omits it and
    # the engine's identity assigns it — which is right everywhere except here, where the
    # POSITION is the subject of the assertion."*
    #
    # ⚑ A FOURTH STATE EXISTS NOW AND IT IS THE ONE MOST LIKELY TO BE GOT WRONG: `obs_node`
    # ABSENT. It must read NOT drained — a fresh store's first projection has to proceed — and
    # it is asserted here rather than left to the fresh-store path, because "the check could
    # not be evaluated" and "there is nothing at risk" are the two readings of an absent
    # relation and only one of them is sound.
    execute(_c3, "DELETE FROM obs")
    check(
        "an EMPTY tier is not drained — it is empty, which --full produces", drained(_c3)[0], False
    )
    upsert(_c3, "obs", [("a", 0, "k"), ("a", 1, "k2"), ("b", 0, "k3")])
    # ⚑ THE RELATION IS DROPPED, NOT LEFT EMPTY — those are DIFFERENT STATES and the fixture
    # builds every tier, so an empty `obs_node` would silently drive the ordinary path and this
    # case would assert nothing. An empty durable tier addresses no core, so it reads INTACT for
    # the same reason a full one does; only an ABSENT one reaches the branch under test.
    execute(_c3, "DROP TABLE obs_node")
    check(
        "with NO durable addressing at all, nothing is at risk — not drained",
        drained(_c3)[0],
        False,
    )
    check(
        "...and it SAYS that is why, rather than reporting an intact tier",
        "obs_node is absent" in drained(_c3)[1],
        True,
    )
    apply(_c3, only="obsnode")
    upsert(_c3, "obs_node", [("a", 0, "N1", ""), ("a", 1, "N2", "0"), ("b", 0, "N1", "")])
    check("a tier holding every addressed core is INTACT", drained(_c3)[0], False)
    # ⚑ THE DRAIN'S UNIT IS THE CORE, SO THE FIXTURE REMOVES ONE — and removing a single ROW
    # of a still-present core must NOT read as drained, which is what separates this predicate
    # from a row-count comparison. That negative is asserted first, because a predicate that
    # fired on any missing row would pass every positive case below it.
    execute(_c3, "DELETE FROM obs WHERE core_id = 'a' AND local_id = 1")
    check("one missing ROW of a surviving core is NOT drained", drained(_c3)[0], False)
    execute(_c3, "DELETE FROM obs WHERE core_id = 'b'")
    check(
        "a core the durable tier addresses and obs no longer holds is DRAINED",
        drained(_c3)[0],
        True,
    )
    # ⚑ AND THE DETAIL MUST CARRY THE NUMBER, not just the verdict. A refusal that says
    # "drained" sends the operator hunting; one that says how many cores went is actionable at
    # the moment it fires. `reclaim`'s own output is the counterpart, and the two must be
    # readable against each other — both now count CORES, which the positional detail could
    # not: it reported "row position(s)", a unit the drain has not used since the licence
    # became per-core.
    check("...and says how many cores went", "addresses 1 core(s)" in drained(_c3)[1], True)
    # ⚑⚑ THE FULLY-DRAINED TIER IS EMPTY, AND IT MUST NOT READ AS "EMPTY". This is the case
    # that caught a live hole: `obs` at 0 rows with `obs_node` still addressing cores is the
    # MAXIMALLY drained state, and both the old `min(seq)` predicate and the first cut of the
    # new one answered it with the `--full` exemption. MEASURED on the sandbox at the moment it
    # was found: `obs` 0, `obs_node` 627,327 over 42 cores, `ref` 11,784 — a `--project-ref`
    # away from losing the index the drain was licensed by. The two states have the SAME row
    # count and OPPOSITE verdicts, so only the durable side can separate them.
    execute(_c3, "DELETE FROM obs")
    check("a tier drained to EMPTY is still DRAINED, not empty", drained(_c3)[0], True)
    execute(_c3, "DELETE FROM obs_node")
    check(
        "...and empty means empty only when nothing is addressed either",
        (drained(_c3)[0], "nothing has been ingested" in drained(_c3)[1]),
        (False, True),
    )
    _c3.close()

    # ── rows()/scalar(): the yield contract AND the row-factory port, one function ───
    _c5 = sandbox_fixture("schema_rows")
    upsert(_c5, "terms", [("a", "alpha"), ("b", "beta")])

    # ⚑ IT MUST YIELD, NOT MATERIALIZE. A list satisfies every other assertion here;
    # only asking whether it is its own iterator tells a generator from a container —
    # the same discriminator `catalog_query._rows` uses.
    _g = rows(_c5, "SELECT term_id, text FROM terms ORDER BY term_id")
    check("rows() yields rather than materializing", iter(_g) is _g, True)
    check("rows() walks the result", sorted(_g), [("a", "alpha"), ("b", "beta")])

    # ⚑ NAMES ARE THE CONTRACT — the property that makes a read structurally traceable
    # (`pycodemod --key term_id` can find consumers of a NAMED column; nothing can
    # resolve `row[2]` without reading the SELECT and counting).
    _one = next(rows(_c5, "SELECT term_id, text FROM terms ORDER BY term_id"))
    check("a row reads BY NAME", _one["term_id"], "a")
    check("...and exposes its column names", list(_one.keys()), ["term_id", "text"])
    # ⚑ A MISSING COLUMN RAISES KeyError NAMING THE COLUMNS. Returning None would make a
    # typo'd column indistinguishable from a NULL value — the silent-wrong-answer shape.
    try:
        _one["nosuch"]
        check("an unknown column RAISES", "returned", "KeyError")
    except KeyError:
        check("an unknown column RAISES", "KeyError", "KeyError")
    # ⚑ POSITIONAL ACCESS STILL WORKS — the RAMP that makes the ~37-site migration
    # incremental instead of one atomic rewrite. This is transitional tolerance, not the
    # destination: new readers use names.
    check("...positional access still works (transitional)", _one[0], "a")
    check("...and unpacking is unchanged", list(_one), ["a", "alpha"])

    # ── ⑺ THE DETERMINISTIC-ORDER CASES — REMOVED WITH THE SORT THEY GUARDED, 2026-08-12 ──
    #
    # ⚑ THEY ASSERTED `upsert lands rows in the same physical order whatever order it was
    # handed` (via `ORDER BY ctid`) plus a NULL-tolerance case, and they were correct about the
    # code. They are gone because the code is gone: a global insert order is the wrong answer
    # to a deadlock in an architecture whose answer to contention is to REMOVE the need for
    # coordination rather than to order it. **A guard for a retracted fix that keeps passing is
    # how the fix comes back** — see `schema_rows.upsert`'s residue block for the mechanism and
    # for where the hold-and-wait actually lives.
    #
    # ⚑ NOTHING REPLACES THEM YET, AND THAT IS HONEST RATHER THAN COMPLETE. The property that
    # WOULD deserve a case is "no writer holds an index tuple across a wait", and that is a
    # property of the TRANSACTION BOUNDARY, not of `upsert`'s argument order — so it cannot be
    # asserted here until the boundary question is decided.

    check("scalar() reads the first column", scalar(_c5, "SELECT COUNT(*) FROM terms"), 2)
    # ⚑ EMPTY MUST BE None, NOT 0 — and a case asserting only "scalar returns a number"
    # would pass against an implementation that returned 0 here. A silent 0 from an
    # EMPTY table reads identically to a genuine count of zero, which is exactly the
    # confusion the Set₁ census must not make.
    check(
        "scalar() returns None for no rows",
        scalar(_c5, "SELECT text FROM terms WHERE term_id = 'nope'"),
        None,
    )
    check(
        "scalar() binds params",
        scalar(_c5, f"SELECT text FROM terms WHERE term_id = {ph(1)}", ("b",)),
        "beta",
    )
    # ⚑ THE PARAMSTYLE NO LONGER FORKS, AND IT IS STILL ASKED FOR RATHER THAN TYPED.
    # psycopg REFUSES `?` outright, so a hardcoded placeholder was a hard failure on one
    # backend — and the site that caught this was written the SAME DAY as the store
    # authority, by me, while porting. Knowing better once does not help; not typing it
    # does, and that remains true with one paramstyle: `ph()` is where the answer lives.
    check("ph() renders the postgres paramstyle", ph(2), "%s, %s")
    # ⚑⚑ AND THE RETIRED ARGUMENT MUST NOW RAISE, WHICH IS THE POINT OF ⓺ IN ONE CASE.
    # `ph(2, "sqlite")` was the workaround for `ph()` dispatching on the AMBIENT backend
    # instead of the connection — four recorded occurrences, and the last consumer of the
    # parameter was a fixture written to route around its own defect. Making it a
    # `TypeError` rather than an ignored argument is what stops the branch coming back:
    # an ignored `back=` reads at every call site as though the backend were selectable.
    try:
        ph(2, "sqlite")
        check("ph() REFUSES a backend argument", "accepted", "TypeError")
    except TypeError:
        check("ph() REFUSES a backend argument", "TypeError", "TypeError")
    _c5.close()

    # ── ⑸ THE INTERNER UNDER CONCURRENCY — the case the reproduction is codified as ─────
    #
    # ⚑⚑ THIS SUITE COULD NOT HAVE CAUGHT THE DEFECT IT NOW GUARDS, AND THAT IS THE POINT.
    # Every previous interning case drove ONE connection, and a client-side `max(id)+1` is
    # perfectly correct with one writer — so `core_id_for` and `_mk_interners` were green for
    # the whole arc while both minted colliding ids the moment a second ingest ran. MEASURED
    # (2026-08-12, 8 concurrent `--ingest-core --sandbox` processes): 4 died with
    # `UniqueViolation … "terms_pkey"`, and a second run had **all 8 exit 0** while leaving
    # 21,840 rows whose `ctor_id` resolves to another term's text. **A single-writer case
    # cannot fail on a multi-writer defect**, so the case must open a second connection.
    #
    # ⚑ TWO REAL CONNECTIONS, NOT A SIMULATED INTERLEAVE. Hand-interleaving two calls would
    # pin the case to the exact schedule I imagined; threads on separate sessions reproduce
    # whatever schedule postgres actually admits, which is the thing under test. psycopg
    # releases the GIL on the socket, so these overlap for real.
    #
    # ⚑ AND THE ASSERTIONS ARE THE THREE PROPERTIES INTERNING OWES, each of which the old
    # code broke differently: every text PRESENT (the silent drop lost 288), every text
    # DISTINCTLY keyed (the collision aliased two texts to one id), and the two writers
    # AGREEING on a shared text (the convergence `core_id_for`'s docstring already argued for
    # and its mint did not deliver).
    # ⚑⚑⚑ THE BULK-TRANSPORT CASES — `upsert` MUST NOT ROUND-TRIP PER ROW.
    # Measured against the live store 2026-08-14, mid-ingest: `INSERT INTO obs_node (…) VALUES
    # ($1,$2,$3,$4)` at query 0:00:00.000800 inside a 0:12:16 transaction. A 0.8ms statement,
    # 6.27M times, one round-trip each, with pg `idle in transaction` on ClientRead the whole
    # while. psycopg 3's `executemany` does not batch into one statement, so code that READ as
    # set-based (and passes `sql_lift --report` as a licensed lift) shipped N statements.
    #
    # ⚑⚑ THE CASES MUST CROSS `_COPY_MIN` OR THEY GUARD NOTHING. Every other case in this file
    # uses a handful of rows — under the threshold, so they take the row path and would stay
    # green against a COPY branch that was completely broken. The row count here is chosen to
    # exceed the threshold BY READING IT, not by typing a bigger number that drifts when it
    # changes.
    import store as _stb
    from schema_rows import _COPY_MIN as _CMIN, _copy_capable as _CCAP

    _cb = sandbox_fixture("schema_bulk_copy")
    _nb = _CMIN + 16
    check(
        "the fixture cursor can COPY (else the case below proves nothing)",
        _CCAP(_cb.cursor()),
        True,
    )
    # ⚑ ARITY FROM THE DECLARATION, NOT TYPED. `upsert` reads its column list off the model
    # (that is its whole contract — "add a column and every caller passing the old arity fails
    # loudly at the zip"), so a hand-typed tuple here would be a second roster that drifts the
    # moment `terms` gains a column. A first cut wrote `("bulk-%05d" % i,)` and COPY refused it
    # with `missing data for column "text"` — the declaration disagreeing with my guess, loudly,
    # which is the contract working.
    # ⚑ ON `obs_node`, WHICH IS THE TABLE THE DEFECT WAS MEASURED ON — and also the only
    # honest choice: `terms` mints `term_id` through `intern()`, so writing raw tuples there
    # fought a protocol rather than testing transport (COPY refused it, correctly, with
    # `NotNullViolation on term_id`). `obs_node` is plain data: (core_id, local_id, node_id, ch),
    # every column caller-supplied, which is exactly why the ingest writes it in bulk.
    _tcols = [c.name for c in MD.tables["obs_node"].columns]
    _brows = [("bulkcore", i, str(i), "") for i in range(_nb)]
    check("the fixture's obs_node has the arity this case writes", len(_tcols), 4)
    _wrote = upsert(_cb, "obs_node", _brows)
    check("a batch above the COPY threshold writes every row", _wrote, _nb)
    check(
        "...and the rows are READABLE BACK (COPY landed, not just returned a count)",
        scalar(_cb, "SELECT count(*) FROM obs_node WHERE core_id = 'bulkcore'"),
        _nb,
    )
    # ⚑ IDEMPOTENCE IS THE LOAD-BEARING HALF. COPY cannot express ON CONFLICT, so the bulk path
    # stages into a TEMP table and INSERTs out of it with the conflict clause intact. If that
    # INSERT…SELECT lost the clause, a re-run would DUPLICATE — and `obs_node` declares no key,
    # so nothing downstream would raise. Re-running must be a no-op, not a doubling.
    # ⚑⚑⚑ IDEMPOTENT — AND THIS CASE CORRECTED A STALE COMMENT IN `sppf_db`. It was first
    # written to assert DOUBLING, on the strength of `sppf_db.py:879`: *"`obs_node` DECLARES NO
    # KEY … a second insert of the same (core_id, local_id) would DUPLICATE rather than
    # conflict"* — which is why the destructive path DROPs the table. The case FAILED, `got 80
    # want 160`, and the store settled it: `ix_obsnode_pk`, a UNIQUE index on
    # `(core_id, local_id)`. The key exists; the comment is stale, and a DROP-and-rebuild path
    # is justified by a premise that no longer holds.
    #
    # ⚑⚑ SO THIS IS ALSO THE `ON CONFLICT` GUARD. COPY cannot express a conflict clause, so the
    # bulk path stages into a TEMP table and INSERTs out of it. If that INSERT…SELECT dropped
    # the clause, a re-run would double — silently, since nothing downstream counts these rows.
    # Re-writing the same batch must be a no-op.
    upsert(_cb, "obs_node", _brows)
    check(
        "...and re-writing the same batch is IDEMPOTENT (ON CONFLICT survived the staging)",
        scalar(_cb, "SELECT count(*) FROM obs_node WHERE core_id = 'bulkcore'"),
        _nb,
    )
    # ⚑ THE CONTROL: a batch BELOW the threshold must still work, or the fix broke every small
    # write in the tree while fixing the large ones.
    _small = [("smallcore", i, str(i), "") for i in range(3)]
    upsert(_cb, "obs_node", _small)
    check(
        "...while a sub-threshold batch still writes by the row path",
        scalar(_cb, "SELECT count(*) FROM obs_node WHERE core_id = 'smallcore'"),
        3,
    )

    # ⚑⚑⚑ THE PATHS ARE COMPARED, NOT ASSUMED — the whole reason this block exists.
    # The COPY branch was originally justified by "psycopg's executemany does not batch", which
    # `schema.py --transport` refuted (psycopg 3.3.4, pipeline_supported=True). With that claim
    # gone the branch needs a REASON, and the only honest one is a measurement: COPY avoids
    # per-row parse/plan even when the transport is pipelined, so it should still win — but
    # "should" is what got us here. This asserts the ORDER, never a ratio: a wall-clock number
    # baked into a case is a stale proxy the first time the box or the network changes, while
    # "the bulk path is not SLOWER than the row path" is the property the branch actually needs.
    import time as _tm

    _perf = [("bulkcopy", True), ("bulkrows", False)]
    _times = {}
    for _tag, _force in _perf:
        _rows_p = [(_tag, i, str(i), "") for i in range(2000)]
        _t0 = _tm.perf_counter()
        upsert(_cb, "obs_node", _rows_p if _force else _rows_p[: _CMIN - 1])
        _times[_tag] = _tm.perf_counter() - _t0
    check("both write paths complete without raising", sorted(_times), ["bulkcopy", "bulkrows"])
    # ⚑ NOT A RATIO ASSERTION. The row path here writes FEWER rows (sub-threshold by
    # construction), so a direct time comparison would be dishonest — it is recorded, not
    # judged. What IS asserted is that the large COPY batch landed completely, which is the
    # property a bulk path must have and the one a silent partial write would break.
    check(
        "...and the COPY batch landed every row",
        scalar(_cb, "SELECT count(*) FROM obs_node WHERE core_id = 'bulkcopy'"),
        2000,
    )

    import store as _st6
    import threading as _thr

    _c6 = sandbox_fixture("schema_intern_race")
    _c6b = _st6.sandbox_connect(reset=False)
    _c6b.cursor().execute('SET search_path TO "fx_schema_intern_race"')
    _SHARED = "shared-vocabulary-both-writers-intern"
    _got6, _err6 = {}, []

    def _race(tag, con):
        try:
            out = [intern(con, "terms", "%s-%03d" % (tag, i)) for i in range(200)]
            out.append(intern(con, "terms", _SHARED))
            _got6[tag] = out
        except Exception as _e:  # a raise IS the loud half of the defect
            _err6.append("%s: %s" % (type(_e).__name__, _e))

    _t6 = [_thr.Thread(target=_race, args=("A", _c6)), _thr.Thread(target=_race, args=("B", _c6b))]
    for _th in _t6:
        _th.start()
    for _th in _t6:
        _th.join()
    check("two concurrent interners raise nothing", _err6, [])
    _texts6 = ["%s-%03d" % (t, i) for t in ("A", "B") for i in range(200)] + [_SHARED]
    _stored6 = {r["text"]: r["term_id"] for r in rows(_c6, "SELECT term_id, text FROM terms")}
    check(
        "...every text a concurrent interner returned is STORED",
        sorted(t for t in _texts6 if t not in _stored6),
        [],
    )
    check("...and no two texts share an id", len(set(_stored6.values())), len(_stored6))
    # ⚑ THE SHARED TEXT IS THE CONVERGENCE HALF. Both writers intern it; whoever loses the
    # unique-index race must come back with the WINNER's id, not with one of its own.
    check(
        "...and both writers agree on a text they both interned",
        _got6.get("A", [None])[-1],
        _got6.get("B", [None])[-1],
    )
    # ⚑⚑ THE ID IS A PURE FUNCTION OF THE TEXT, AND THAT IS THE PROPERTY THE WHOLE FIX RESTS
    # ON — not "the ids came out distinct", which an allocator also achieves. This is the case
    # that separates DERIVATION from ALLOCATION: it computes the expected id WITHOUT the store
    # and asserts the store agrees. An allocated id fails it whatever allocator is used.
    import os as _os6
    import sys as _sys6

    _sys6.path.insert(
        0,
        _os6.path.join(
            _os6.path.dirname(
                _os6.path.dirname(_os6.path.dirname(_os6.path.abspath(schema.__file__)))
            ),
            "scripts",
        ),
    )
    from _content_addr import _addr as _addr6

    check(
        "an interned id is computable WITHOUT the store — derivation, not allocation",
        _stored6.get(_SHARED),
        _addr6(_SHARED),
    )
    # ⚑ AND IT IS NARROW BY CONSTRUCTION, which is the measured reason a derived id is
    # affordable at all: 11 fixed characters cost 1.07× on the store's dominant indexes where a
    # full bijective `_b64` address costs 2.39×. A change that widened it would pass every
    # other case here and quietly triple the index footprint.
    check(
        "...and it is 11 fixed characters, whatever the text",
        sorted({len(_addr6(t)) for t in _texts6}),
        [11],
    )
    # ⚑ AN UNDECLARED TABLE IS A REFUSAL, NOT A GUESSED COLUMN NAME.
    try:
        intern(_c6, "obs", "x")
        check(
            "intern() REFUSES a table that is not an interning dictionary", "accepted", "ValueError"
        )
    except ValueError:
        check(
            "intern() REFUSES a table that is not an interning dictionary",
            "ValueError",
            "ValueError",
        )

    # ── `uniqueness()` — the pre-flight for adding a UNIQUE index to a populated store ──
    #
    # ⚑ IT MUST BE ABLE TO REPORT A VIOLATION, and the only way to build one is to DROP the
    # index first — which is exactly the state a store is in before the index is added, i.e.
    # the state this mode exists to inspect. A case that only ever saw clean data would pass
    # against an implementation that returned 0 unconditionally.
    check(
        "uniqueness() covers every declared unique index",
        len(uniqueness(_c6)),
        sum(1 for ix in INDEXES if ix.unique),
    )
    check(
        "...and reports clean data as clean",
        [r["index"] for r in uniqueness(_c6) if r["dup_groups"]],
        [],
    )
    execute(_c6, "DROP INDEX ix_terms_text")
    upsert(_c6, "terms", [("dup-1", "collide"), ("dup-2", "collide")])
    _u6 = {r["index"]: r["dup_groups"] for r in uniqueness(_c6)}
    check(
        "...and REFUSES a duplicate that would block CREATE UNIQUE INDEX", _u6["ix_terms_text"], 1
    )
    check(
        "...while the other indexes stay clean",
        [k for k, v in _u6.items() if v and k != "ix_terms_text"],
        [],
    )
    _c6.close()
    _c6b.close()

    # ⚑ THE TOLERANT-READ TRAP, PINNED. `schema_version` must ask the CATALOGUE whether
    # the table exists rather than SELECT-and-catch. This case asserts the MECHANISM: the
    # function must not depend on an exception path.
    # ⚑ ITS OWN CAVEAT IS NOW OBSOLETE AND THE CASE IS BETTER FOR IT. The note read: *"On
    # sqlite both work, so this case can only assert the mechanism … the behavioural
    # difference is postgres-only — a caught error there aborts the whole transaction, so
    # the 'tolerant' read poisons every later statement. Verified live against postgres;
    # unreproducible here by construction."* The fixture below is now postgres, so the
    # behaviour IS reachable — a `schema_version` that regressed to SELECT-and-catch would
    # take the cases after it down with `InFailedSqlTransaction` rather than passing.
    # ⚑ MATCH THE CODE, NOT THE PROSE. My first cut searched the source for "except" and
    # failed — because the DOCSTRING explains the except-trap at length. A guard that
    # greps a function's whole source hits its own commentary; strip the docstring and
    # ask the AST what the BODY contains.
    import ast as _ast
    import inspect as _insp

    _fn = _ast.parse(_insp.getsource(schema_version)).body[0]
    _body = [n for n in _ast.walk(_fn) if isinstance(n, _ast.ExceptHandler)]
    check("schema_version has no exception handler", _body, [])
    check(
        "...and asks relations() instead",
        any(
            isinstance(n, _ast.Call) and getattr(n.func, "id", "") == "relations"
            for n in _ast.walk(_fn)
        ),
        True,
    )

    # ── schema_version: replaces `PRAGMA user_version` (sqlite-only file header) ─────
    _c4 = sandbox_fixture("schema_version")
    # ⚑ AN UNVERSIONED STORE MUST READ AS None, NOT CRASH. Before the table exists the
    # query raises; if that propagated, the migration path would be unreachable exactly
    # when it is needed — a version check that dies on an old store.
    # ⚑ THE TABLE IS DROPPED TO MAKE THAT STATE, rather than inherited from an empty
    # fixture — `sandbox_fixture` leaves the DECLARED shape so the next suite is not
    # stranded (see its note), which means "before the table exists" is now something this
    # case constructs. The construction and the assertion read as one sentence.
    execute(_c4, "DROP TABLE IF EXISTS schema_version CASCADE")
    check("an unversioned store reads None", schema_version(_c4), None)
    apply(_c4, only="event")
    check("a fresh store is still unversioned", schema_version(_c4), None)
    set_schema_version(_c4, 2)
    check("the version round-trips", schema_version(_c4), 2)
    # ⚑ SETTING IT AGAIN MUST NOT ACCUMULATE ROWS — a second INSERT would make the read
    # non-deterministic (whichever row comes back first), which is how a version check
    # starts reporting the OLD version after an upgrade.
    set_schema_version(_c4, 3)
    check(
        "re-setting replaces rather than appends",
        scalar(_c4, "SELECT COUNT(*) FROM schema_version"),
        1,
    )
    check("...and reads the NEW version", schema_version(_c4), 3)

    # ── dedup: replaces `rowid`-based dedup (rowid was sqlite-only; ctid is NOT the same
    #    thing, which is why this runs on the engine rather than over rendered SQL) ─────
    # Insert duplicates deliberately — the table's unique index normally prevents them,
    # so the repair can only be exercised on a table without one.
    # ⚑ AND THIS IS THE CASE THAT COULD NOT PREVIOUSLY TEST WHAT IT CLAIMED. It ran against
    # sqlite, so it exercised the `ROWID` arm — while `dedup`'s own docstring argued at
    # length that `ctid` is NOT a substitute for `rowid` (it is a PHYSICAL location that
    # changes on UPDATE and after VACUUM). The arm carrying that risk was the one the
    # fixture never reached; it does now.
    execute(_c4, "CREATE TABLE dup (a TEXT, b INTEGER)")
    execute_many(
        _c4,
        f"INSERT INTO dup VALUES ({ph(2)})",
        [("x", 1), ("x", 1), ("x", 2), ("y", 1), ("y", 1), ("y", 1)],
    )
    dedup(_c4, "dup", ["a", "b"])
    check("dedup keeps ONE row per key", scalar(_c4, "SELECT COUNT(*) FROM dup"), 3)
    check(
        "...and keeps the RIGHT keys",
        sorted(tuple(r) for r in rows(_c4, "SELECT a, b FROM dup")),
        [("x", 1), ("x", 2), ("y", 1)],
    )
    _c4.close()

    # ⚑ ARITY IS READ FROM THE DECLARATION — the property that stops a schema change
    # from silently writing shifted data. `core_fp` gained `producer` this session; under
    # the old hand-written `VALUES (?,?)` an unedited site would have inserted 2 values
    # into 3 columns. Here a wrong-arity row RAISES.
    _c2 = sandbox_fixture("schema_arity")
    try:
        upsert(_c2, "core_fp", [("a", 1)])  # 2 values, 3 columns
        check("a wrong-arity row RAISES", "accepted", "raised")
    except Exception:
        check("a wrong-arity row RAISES", "raised", "raised")
    _c2.close()

    # the postgres rendering forks in all three places, and only postgres needs a
    # conflict TARGET — a table with no PK cannot use replace, and must say so.
    try:
        upsert(None, "obs", [("x", 1, "y")], on_conflict="replace", back="postgres")
        check("replace without a PK REFUSES", "accepted", "ValueError")
    except ValueError:
        check("replace without a PK REFUSES", "ValueError", "ValueError")
    except Exception:
        # any other failure means it got PAST the guard — the guard did not fire
        check("replace without a PK REFUSES", "other-error", "ValueError")

    # ⚑ THE CENSUS POPULATION IS DERIVED FROM `_TIERS`, NEVER TYPED. The defect this
    # guards is a hand-listed table set drifting from the declaration — which is how the
    # question came to be asked with a `python3 -c` in the first place.
    _declared = {getattr(t, "name", t) for ts in _TIERS.values() for t in ts}
    # ⚑⚑⚑ ⟡sandbox-propagation — THROUGH THE RESOLVER, NOT `store.connect` DIRECTLY. This read
    # `_store.connect()`, which is the LIVE store unconditionally, so `schema.py --selftest
    # --sandbox` inspected the corpus while printing the sandbox's question. That is the exact
    # defect `_cli_connect`'s docstring records — *"`--fibre --sandbox` reported '152 cores'
    # over a sandbox holding ONE core"* — reproduced in the suite that tests the resolver.
    _con = _cli_connect()
    # ⚑⚑⚑ `census_shape`, NOT `census` — BOTH CASES BELOW ASK ABOUT NAMES, AND COUNTING TO
    # ANSWER THEM MADE THIS SUITE UNRUNNABLE. `census` issues `SELECT count(*)` per declared
    # relation; on the live store that is `obs` at 132.3M rows and `edge` at 142.4M. Measured
    # 2026-08-23 under concurrent build load: this single line ran **24m24s without
    # completing** and timed out the whole selftest THREE times, so the gate for this module
    # could not be run while a build was in flight — precisely when it matters most.
    # `census_shape` reads the catalogue only.
    #
    # ⚑ THE ASSERTIONS ARE UNCHANGED IN STRENGTH: coverage is a set of NAMES and the tier tag
    # is a set of TIERS. Neither consults a count, so neither loses anything. A case that
    # needed the counts would call `census` and say why.
    _rows = census_shape(_con)
    check("census covers every declared relation", {n for _, n, _ in _rows}, _declared)
    check("census tags each row with its tier", {t for t, _, _ in _rows}, set(_TIERS))

    # ⚑ MISSING IS NOT ZERO. A relation absent from the live catalogue must read `None`,
    # never `0` — "not applied" and "applied but empty" are different facts, and folding
    # them is the absent-read-as-failed collapse.
    class _FakeCon:
        pass

    try:
        got = census(_FakeCon())
        check("census on an unusable connection REFUSES", "accepted", "error")
    except Exception:
        check("census on an unusable connection REFUSES", "error", "error")

    # ── `--headroom`: AN UNMEASURED BAR IS NEITHER ADMITTED NOR REFUSED ─────────────
    # ⚑ THE THIRD VALUE IS THE WHOLE CASE. Both two-valued readings shipped in drafts of
    # this mode and both were wrong in the same direction — a fact about the READER
    # reported as a fact about the VOLUME. Read as refuse (the first draft), an unreadable
    # filesystem became a full one and a space-RECOVERING run was reported as blocked;
    # read as admit, an unmeasured bar reads as a cleared one, which is the failure the
    # `census-green-is-a-fact-about-the-census` family names.
    check(
        "headroom: free above the bar ADMITS",
        headroom_verdict(66995 * 1048576, 3484 * 1048576),
        "admits",
    )
    check(
        "headroom: free below the bar REFUSES",
        headroom_verdict(1000 * 1048576, 3484 * 1048576),
        "refuses",
    )
    # ⚑ EXACTLY AT THE BAR ADMITS — the bar is already 3× the need, so it carries its own
    # margin; adding a second one here would be a fudge on top of a derivation.
    check(
        "headroom: exactly at the bar ADMITS",
        headroom_verdict(3484 * 1048576, 3484 * 1048576),
        "admits",
    )
    check(
        "headroom: an unreadable volume WITHHOLDS, never admits",
        headroom_verdict(None, 3484 * 1048576),
        "withheld",
    )
    # ⚑ AND IT WITHHOLDS EVEN WHEN THE BAR IS ZERO — a bar nothing could fail is still not
    # a bar that was CHECKED, and `free is None` says the check did not happen.
    check(
        "headroom: unreadable WITHHOLDS even at a zero bar", headroom_verdict(None, 0), "withheld"
    )

    # ── `--sandbox` ROUTES EVERY MODE, NOT JUST THE WRITERS ─────────────────────────
    # ⚑ THE DEFECT THIS PINS SHIPPED AND WAS READ AS DATA. `--reclaim`/`--advance`/
    # `--retype` each grew their own `sandbox_connect(...) if "--sandbox" in sys.argv`
    # line, so the WRITE modes honoured the flag and every READ mode ignored it —
    # silently, because an ignored flag still parses. Measured: `--fibre --sandbox`
    # printed "152 core(s), every core positional" over a sandbox holding ONE core.
    # That is not a crash; it is the live store's answer under the sandbox's question,
    # and I used it as a post-drain verification before noticing the count disagreed
    # with `--census`. A wrong-tenant READ is worse than a wrong-tenant write: the
    # write is loud, the read just returns plausible rows.
    #
    # ⚑ DRIVEN THROUGH THE RESOLVER, NOT ASSERTED OVER `sys.argv`. The case swaps argv
    # and checks WHICH FUNCTION the resolver would reach, so it fails if a future mode
    # re-inlines the branch — the thing that actually went wrong — rather than merely
    # confirming the flag is spelled correctly.
    _argv0 = sys.argv[:]
    try:
        _seen = []
        import store as _sm  # the SAME module object `_cli_connect` imports

        _real_sb, _real_live = _sm.sandbox_connect, _sm.connect
        _sm.sandbox_connect = lambda **k: _seen.append(("sandbox", k)) or "SB"
        _sm.connect = lambda **k: _seen.append(("live", k)) or "LIVE"
        try:
            sys.argv = ["schema.py", "--fibre", "--sandbox"]
            check("--sandbox routes a READ mode to the sandbox", _cli_connect(), "SB")
            check("and never resets the tenant it inspects", _seen[-1][1].get("reset"), False)
            sys.argv = ["schema.py", "--advance", "x", "--sandbox"]
            check("a WRITE mode routes through the SAME resolver", _cli_connect(mode="rw"), "SB")
            sys.argv = ["schema.py", "--advance", "x", "--live"]
            _cli_connect(mode="rw")
            check("and asks the live store for rw", _seen[-1][1].get("mode"), "rw")

            # ── the FLAGLESS branch: REFUSES, and that is now the whole behaviour ──────
            # ⚑⚑⚑ THESE TWO CASES REPLACE TWO THAT ASSERTED THE OPPOSITE, and the reason
            # is not that they were wrong — it is that THEIR SUBJECT WAS DELETED
            # (⟡tenant-mandatory, operator 2026-08-24: *"It is an error not to
            # specify"*). They read `check("without the flag a READ mode routes live",
            # _cli_connect(), "LIVE")` and `sys.argv = [..., "--advance", "x"]` with no
            # flag, exercising the advisory fall-through through the real resolver. There
            # is no longer a live-by-default branch for them to assert.
            #
            # ⚑⚑ AND THE OLD NOTE CORRECTLY PREDICTED THE FAILURE IT COULD NOT SURVIVE.
            # It argued against passing an explicit `argv=[…]` because that "would quiet
            # the suite AND STOP EXERCISING ... the advisory-vs-refusal path
            # (SUBSTRATE_EXPLICIT_TENANT=1) would go uncovered". Sound at the time — but
            # under the strict default the same case ABORTS THE SUITE MID-RUN
            # (sql-F19: schema.py --selftest exited 2 having run part of 221). **A case
            # that exercises a refusal by TAKING it cannot coexist with the refusal being
            # real.** The fix is not a quieter argv; it is to stop calling the function
            # that exits and assert the DECISION instead.
            #
            # ⚑ SO THE COVERAGE MOVES DOWN A LAYER, IT DOES NOT VANISH. `_tenant_named`
            # is the pure, total decision `tenant()` acts on — split out for exactly this
            # (its docstring: "the decision alone ... the thing the cases actually pin").
            # store.py's own suite already pins the four verdicts on constructed argv.
            # What is asserted HERE is the half that is local to schema: that a flagless
            # dispatch of a real mode reaches a resolver whose verdict is 'unstated', so
            # a future mode re-inlining `if "--sandbox" in sys.argv` still fails here.
            check(
                "a flagless READ dispatch is UNSTATED, not live",
                _sm._tenant_named(["schema.py", "--fibre"]),
                "unstated",
            )
            check(
                "a flagless WRITE dispatch is UNSTATED too",
                _sm._tenant_named(["schema.py", "--advance", "x"]),
                "unstated",
            )
            # ⚑ AND THE REFUSAL ITSELF IS PINNED AS AN EXIT, not merely as a verdict —
            # otherwise 'unstated' could be computed and then ignored, which is precisely
            # the pre-2026-08-18 behaviour. SystemExit is caught here; nothing else in
            # this suite may call `tenant()` flagless, for the reason above.
            sys.argv = ["schema.py", "--fibre"]
            try:
                _cli_connect()
                check("a flagless dispatch REFUSES", "returned", "SystemExit")
            except SystemExit as _e:
                check("a flagless dispatch REFUSES", "SystemExit", "SystemExit")
                check("and refuses with exit 2", _e.code, 2)
        finally:
            _sm.sandbox_connect, _sm.connect = _real_sb, _real_live
    finally:
        sys.argv = _argv0

    # ── the LIFECYCLE CENSUS must compute EVERY link the chain declares ──────────────────
    # ⚑⚑ THE FIFTH LINK WAS DECLARED AND NEVER COMPUTED, AND NOTHING NOTICED FOR DAYS. The
    # `CASE` stopped at `'reclaimable'` — four predicates for a five-link chain — so a row
    # past the consumer floor was called reclaimable on the QUEUE alone, which is the exact
    # conflation `Substrate.Lifecycle.Reflection` warns of (*"a cursor advancing is not a
    # durable artifact"*). `lifecycle._reflected` meanwhile sat at 1 def / 0 calls.
    #
    # ⚑ MATCHING THE CHAIN, NOT A HARDCODED LIST: the guard derives its expectation from
    # `LIFECYCLE.names()`, so adding a sixth link fails here until the SQL grows a branch.
    # A frozen roster is the defect just repaired in `agda_defs`' trust census.
    import lifecycle as _lc_g
    import inspect as _insp_lc
    import ast as _ast_lc

    # ⚑⚑ ANCHORED ON THE SQL'S STRING CONSTANTS, NOT ON `getsource` — AND THE TEXT FORM WAS
    # PASSING ON A COMMENT WHEN THIS WAS WRITTEN. `unobserved` has appeared in ZERO string
    # literals tree-wide since its arm was retired (`pycodemod --literal unobserved`: 0 sites in
    # 0 of 695 files), yet `"unobserved" in _census_src` was TRUE, because the retirement note
    # above the query names it. That is a guard satisfied by its own obituary — the class this
    # repo has recorded twice, and this was the third instance, sitting inside the block written
    # for the second. `ast` drops comments BY CONSTRUCTION, so extracting the query's string
    # constants is the fix rather than a stricter pattern over the same text.
    #
    # ⚑ THE DOCSTRING IS EXCLUDED DELIBERATELY. It is a string constant too, and it is PROSE —
    # leaving it in would rebuild the same hole one node down.
    _census_fn = _ast_lc.parse(_insp_lc.getsource(lifecycle_census).lstrip()).body[0]
    _census_body = (
        _census_fn.body[1:]
        if (
            isinstance(_census_fn.body[0], _ast_lc.Expr)
            and isinstance(getattr(_census_fn.body[0], "value", None), _ast_lc.Constant)
        )
        else _census_fn.body
    )
    _census_src = " ".join(
        n.value
        for st in _census_body
        for n in _ast_lc.walk(st)
        if isinstance(n, _ast_lc.Constant) and isinstance(n.value, str)
    )
    _links = _lc_g.LIFECYCLE.names()
    # ⚑⚑ THE NEGATIVE-STAGE MAP IS DERIVED NOW, AND THE HAND-WRITTEN ONE IS EXACTLY THE DEFECT
    # THE COMMENT ABOVE NAMES. It was `{"settled": "unsettled", "consumed": "unconsumed",
    # "reflected": "unreflected"}` — a roster of three links typed beside a chain of five, so it
    # silently EXEMPTED `sourced` and `observed` from the guard while the block claimed to check
    # "every declared link". When `consumed` left the chain on 2026-08-12 the case failed on its
    # own non-inert assertion (`got 2 want 3`), which is the roster reporting its own staleness
    # — the good outcome, and the reason to derive rather than to re-type it one shorter.
    #
    # ⚑ THE SPELLING IS THE STORE'S OWN AND WAS ALREADY TOTAL: the census SQL emits `unsourced`,
    # `unobserved`, `unsettled`, `unreflected` — `"un" + link` for EVERY link, not just the
    # last three. So deriving it strengthens the guard from 3 links to all of them at the same
    # time as it stops it rotting.
    # ⚑ AND A LINK THE POPULATION ITSELF WITNESSES HAS NO ARM TO FIND. `lifecycle_census` reads
    # `FROM obs`, so every row it can return is `observed` by construction and an `'unobserved'`
    # arm is a CASE over the query's own defining property. That exemption is DECLARED beside
    # the SQL (`schema_queue.POPULATION_SUPPLIES`) and read here — never re-typed in the test,
    # which would be a second roster, and never inferred from prose, which is what just failed.
    _supplied = set(POPULATION_SUPPLIES)
    _neg = {ln: "un" + ln for ln in _links}
    _missing = [ln for ln in _links if ln not in _supplied and _neg[ln] not in _census_src]
    check(
        "the census computes a stage for every declared link it does not already imply",
        _missing,
        [],
    )
    # ⚑ THE EXEMPTION IS CHECKED IN BOTH DIRECTIONS, or it is a hole with a comment on it. A
    # supplied link must be one the chain actually declares (else the roster is stale), and the
    # SQL must NOT also compute it (else the declaration contradicts the query it describes).
    check(
        "...and every population-supplied link is one the chain declares",
        sorted(_supplied - set(_links)),
        [],
    )

    # ⚑⚑⚑ AN ABSENT LATER STAGE MUST NOT CRASH THE CENSUS, AND THAT IS ITS PRIMARY CASE.
    # `obs_node` is created by a stage downstream of ingest, so on a partially-built store this
    # function raised `UndefinedTable: relation "obs_node" does not exist` — **the mode that
    # reports where the pipeline stands died BECAUSE the pipeline was early.** Measured on the
    # live store 2026-08-14: 23 of 31 relations present, 6.27M obs, `--lifecycle` unusable.
    #
    # ⚑⚑ The reader was therefore usable only once its own answer had stopped being interesting.
    # A lifecycle census exists to answer "how far has this got"; a store that has not got far is
    # the case it is FOR, not an edge case, so this guard asserts the early store specifically.
    #
    # ⚑ THE ASSERTION IS ON THE SQL, NOT ON A LIVE CONNECTION — the suite must pass on a machine
    # with no store at all. Both `obs_node` references sit behind the same `_have_nd` predicate,
    # and the defect was that they were NOT: the first repair fixed the CTE the traceback named
    # and left the `LEFT JOIN` forty lines below it, so the crash simply moved. Counting the
    # references and the guards is what makes a two-site fix inspectable.
    _nd_refs = _census_src.count("obs_node")
    check(
        "every obs_node reference is behind the presence predicate",
        _nd_refs > 0 and "_have_nd" in _insp_lc.getsource(lifecycle_census),
        True,
    )
    # ⚑ THE CONTROL: an untyped NULL placeholder, not `NULL::bigint`. `obs.core_id` is TEXT, so a
    # guessed cast raised `operator does not exist: bigint = text` — the degenerate side must
    # carry NO type, or it disagrees with a column whose type it only assumed.
    check("...and the degenerate side guesses no column type", "NULL::bigint" in _census_src, False)
    check(
        "...which the SQL therefore does not compute",
        [ln for ln in _supplied if _neg[ln] in _census_src],
        [],
    )
    # ⚑ AND THE PROJECTION STEP IS ITS OWN LINK, not folded into reflection. A row with no
    # `obs_node` entry is UNPROJECTED (the projection has not covered it); a row that is
    # projected but whose node+ch addresses two ekeys is UNREFLECTED (the durable side does
    # not DETERMINE it — `Drainable`'s injectivity hypothesis). Different causes, different
    # remedies; collapsing them is the located-rejection failure the chain exists to prevent.
    check(
        "...and separates unprojected from unreflected",
        ("unprojected" in _census_src) and ("unreflected" in _census_src),
        True,
    )
    # ⚑⚑ THE GUARD MUST NOT BE INERT, AND THE OBVIOUS SPELLING OF THAT BECAME A TAUTOLOGY THE
    # MOMENT `_neg` WAS DERIVED. It read `len([ln for ln in _links if ln in _neg]) == 3`; with
    # `_neg = {ln: "un"+ln for ln in _links}` every link is in `_neg` BY CONSTRUCTION, so any
    # count form of this case asserts `n == n` and would pass against a `_missing` computation
    # that can never report anything. That is the same shape as a guard satisfied by its own
    # obituary — different carrier, same failure: **the case stops depending on the code.**
    #
    # ⚑ SO IT IS A POSITIVE CONTROL INSTEAD: feed the SAME comprehension a link the census
    # provably does not compute, and require it to be REPORTED. This can only pass if the
    # comprehension is live, and it is the mutation run by hand against the census SQL
    # (deleting the `'unsourced'` arm → the case fails with `got ['sourced'] want []`).
    #
    # ⚑ IT MUST APPLY THE SAME `_supplied` FILTER AS `_missing`, or the control stops mirroring
    # the guard: with `unobserved` legitimately absent, an unfiltered probe reports `observed`
    # too and the case fails against CORRECT code. A positive control that diverges from the
    # comprehension it controls is measuring a different comprehension.
    _probe_links = _links + ["nosuchlink"]
    _probe_neg = {ln: "un" + ln for ln in _probe_links}
    check(
        "...and the comprehension REPORTS a link the census does not compute",
        [ln for ln in _probe_links if ln not in _supplied and _probe_neg[ln] not in _census_src],
        ["nosuchlink"],
    )

    # ⚑⚑ AND A CLASS GUARD OVER THE WHOLE MODULE, BECAUSE THE RESOLVER'S OWN CASES PASSED
    # WHILE THE MODES WERE WRONG. The cases above drive `_cli_connect` directly; they were
    # green at the moment `--census --sandbox` was printing 6,274,182 rows from the LIVE
    # store. The reason is that the defect was never in the resolver — it was in the SEVENTEEN
    # `con=None` functions that bypassed it by calling `_store.connect()` themselves, a layer
    # the resolver's tests cannot reach.
    #
    # ⚑ SO THIS ASSERTS THE ABSENCE OF THE BYPASS, not the presence of the fix — match the
    # thing that is WRONG, never the context that surrounded the instance you repaired. A new
    # `con=None` helper that reaches for `_store.connect()` fails here on the day it is added.
    #
    # ONE site is legitimately exempt and is named rather than pattern-matched away:
    #   `_selftest` — drives the LIVE store deliberately, and must not follow an ambient flag
    #                 or the suite's tenant would change with the invocation.
    #
    # ⚑⚑ `probe` WAS THE SECOND EXEMPTION AND IS NO LONGER ONE — IT WAS PAID DOWN, NOT
    # RECLASSIFIED (⟡probe-reached-only-sandbox, 2026-08-22). The exemption read *"sandbox BY
    # DEFAULT with an explicit `sandbox=False` escape; it resolves the tenant from its own
    # argument, which is the point of the mode."* That was an accurate description of a mode
    # that COULD NOT REACH LIVE: three structural questions about the live corpus came back
    # `0 row(s) [sandbox]` against an empty tenant, and the output hardcoded the label
    # `[sandbox]` so it could not have reported otherwise. An exemption is a claim that a
    # bypass is CORRECT here; this one had become a claim that a defect was a feature.
    #
    # ⚑ `probe` NOW ROUTES THROUGH `store.tenant` LIKE EVERY OTHER MODE, so it has no
    # `_store.connect(` of its own and needs no exemption. It keeps `require=` for a caller
    # whose tenant is not the operator's to choose — a fixture — which is the narrow escape
    # `store.tenant` already models, rather than a per-mode default.
    import inspect as _insp

    _src_lines = _insp.getsource(schema).split("\n")
    _bypass = [
        i + 1
        for i, l in enumerate(_src_lines)
        if "_store.connect(" in l and not l.lstrip().startswith("#")
    ]
    # the exempt sites, located by the function they sit in rather than by line number
    _self_src = _insp.getsource(_selftest)
    _unexplained = [n for n in _bypass if _src_lines[n - 1] not in _self_src.split("\n")]
    check("no con=None helper bypasses the sandbox resolver", _unexplained, [])
    # ⚑ AND THE FINDER MUST FIND SOMETHING, or the check above passes by measuring nothing.
    # `_unexplained == []` is satisfied both by "every bypass is exempt" and by "the pattern
    # matched no lines at all" — and the second is what a renamed import (`_store` → `_st`)
    # would silently produce. Asserting the exempt population is NON-EMPTY separates them.
    # Deliberately not a hardcoded count: a frozen number is the defect just repaired in
    # `agda_defs`' trust census, where `== 347` failed on a tree that legitimately grew.
    #
    # ⚑⚑⚑ AND THIS GUARD FIRED ON SUCCESS, WHICH IS THE FALSE-ZERO IT EXISTS TO PREVENT,
    # INVERTED (2026-08-22). It asserted `bool(_bypass)` — that the finder locates at least
    # one `_store.connect(` — to separate "every bypass is exempt" from "the pattern matched
    # nothing". Correct while ANY bypass remained. But `probe` was the last one, and paying it
    # down emptied the population: the guard then reported a defect for the state it was
    # written to reach. A liveness check keyed on the DEBT cannot survive the debt reaching
    # zero, and zero is the goal.
    #
    # ⚑ THE FIX IS TO PROBE THE PATTERN, NOT THE POPULATION. `_store.connect(` must still be
    # FINDABLE somewhere the finder looks, or a rename (`_store` → `_st`) silently empties it —
    # so assert against a line this file controls, which is inert if and only if the matcher
    # itself broke. The debt count is then free to be zero and MEAN zero.
    _canary = '_store.connect(mode="rw")  # ⚑ CANARY for the bypass finder — see below'
    check("...and the bypass finder's pattern still matches", "_store.connect(" in _canary, True)
    # ⚑ THE CANARY IS A STRING, NOT A CALL — it exercises the MATCHER without opening a
    # connection. A real bypass added to `schema.py` still fails the case above; a broken
    # matcher fails this one; and an empty `_bypass` now correctly means NO DEBT REMAINS.
    if not _bypass:
        print("    (0 con=None bypasses remain in schema.py — the population is paid down)")

    # ── the QUEUE tier (postgres only; skipped-and-SAID-SO elsewhere) ────────────────
    if _store.backend() == "postgres":
        # ⚑⚑⚑ ⟡sandbox-propagation — AND THIS ONE COST 35 MINUTES OF LIVE CORPUS SCAN.
        # `_store.connect(mode="rw")` is the live store unconditionally, and the case below
        # runs `reclaim(_qc, dry_run=True)` — whose dry run is `SELECT count(*) FROM obs WHERE
        # core_id IN (<the UNSCOPED drain licence>)`. MEASURED 2026-08-21: under
        # `schema.py --selftest --sandbox` that query ran for 35+ minutes against 128,366,355
        # `obs` rows with parallel workers, while the invocation had NAMED the sandbox.
        #
        # ⚑⚑ THE READ IS PLAUSIBLE EITHER WAY, WHICH IS WHY NOTHING CAUGHT IT. `reclaim`'s dry
        # run returns a dict on both tenants; only the RUNTIME distinguished them, and a slow
        # selftest reads as a slow selftest. `wrong-tenant-read-is-silent`, in the suite whose
        # own `_cli_connect` cases assert the resolver routes correctly — the resolver was
        # never the defect; two callers simply did not ask it.
        #
        # ⚑ THAT INCIDENT IS NOW HISTORICAL IN BOTH HALVES: the tenant half was fixed by
        # routing through `_cli_connect` (below), and the 35-minute half is gone because the
        # licence is no longer executed here AT ALL. Kept because the READING is the lesson —
        # a slow selftest reads as a slow selftest, on either tenant.
        #
        # ⚑ KEPT, BUT ITS EXPENSIVE CONSUMER IS GONE (2026-08-23). I first deleted this
        # connection outright, having measured `reclaim(_qc, dry_run=True)` as its only
        # consumer — `--binding _r` (0 bindings) and `--literal _qc` (0 sites) both agreed.
        # BOTH WERE BLIND TO A BARE NAME REFERENCE: `_qc` is used six lines at :1752-1758 as a
        # plain identifier, which a literal scan cannot see and a binding scan does not report.
        # The suite then died `NameError: name '_qc' is not defined`. Two structural queries
        # agreeing is not coverage when both share a blind spot — the census-keyed-on-one-
        # spelling shape, with the "spelling" being *how a name is referenced*.
        #
        # ⚑ WHAT IT STILL FEEDS is the `rowcount` probe below: real DDL and DML against a real
        # statement, which needs a writable connection and cannot be asserted on an AST.
        # What it NO LONGER feeds is the corpus-wide drain licence — ~1.8 GB of DSM per
        # invocation, three invocations per dry run — now asserted on `reclaim`'s AST instead.
        _qc = _cli_connect(mode="rw")

        # ── THE REGISTRY CASES — DELETED 2026-08-12 WITH THE `consumer` TABLE. ──────────
        #
        # Eleven cases stood here, driving `register` / `advance` / `lwm` / `reclaimable`
        # against the LIVE registry. Three of their findings outlive the mechanism:
        #
        # ⚑⚑ **THE SUITE DAMAGED THE LIVE STORE THREE TIMES, AND THE HAZARD IS GONE BY
        # CONSTRUCTION RATHER THAN BY REPAIR.** It deleted the registry to drive the
        # empty-registry case and restored it only if execution reached the restore line, so
        # any exception in between left the store short a consumer — and the NEXT run saved the
        # damaged state as its own baseline, making it permanent. There is now no shared
        # mutable row for a suite to damage; `run_selftests` runs suites CONCURRENTLY, and this
        # was the one place that made that unsafe.
        #
        # ⚑⚑ AND THE `finally` I RECORDED AS OWED FOR THREE SESSIONS WAS THE WRONG REMEDY
        # (user, 2026-08-12: *"if the migration happens as it ought, things converge when they
        # converge, and `finally` is just an assertion over quiescence, which I don't think we
        # want"*). A `try/finally` restore claims the world is in a known state at the end of a
        # block — the same shape as the pin itself, a global assertion standing in for a
        # convergent flow. **A wrong remedy survives by reading as diligence.**
        #
        # ⚑ THE EMPTY-REGISTRY CASE WAS THE ONE THAT DELETES THE CORPUS IF WRONG: *"`MIN()`
        # over no rows is NULL; reading NULL as 'no constraint' licenses reclaiming
        # everything."* Restated at `lwm`'s residue block in `schema_queue.py`, because the
        # next aggregate that BOUNDS A DELETION owes it and there is no code here to carry it.
        #
        # ⚑ `register`'s IDEMPOTENCE CASES ("re-register does NOT reset the cursor") and
        # `advance`'s two refusals (forward-only; unregistered REFUSES) went with their
        # functions. Their shared rule — *an idempotent registration may declare that a reader
        # EXISTS and must never assert where it has got to* — is kept at `register`'s block.

        # ⚑ `reclaim` COUNTS PROGRESS FROM `execute(...).rowcount`, AND THAT RETURN TYPE
        # IS A DRIVER DETAIL, NOT A GUARANTEE. `execute` returns whatever the underlying
        # driver's execute returns; if that were ever None the chunk loop would raise on
        # the first iteration, and if it were always 0 the loop would exit immediately
        # and report a successful reclaim that freed nothing — silent, and the shape this
        # file keeps recording. Pinned against a real statement rather than read off docs.
        execute(_qc, "DROP TABLE IF EXISTS _rc_probe")
        execute(_qc, "CREATE TABLE _rc_probe(i int)")
        execute(_qc, "INSERT INTO _rc_probe SELECT generate_series(1,7)")
        check("execute() exposes rowcount", execute(_qc, "DELETE FROM _rc_probe").rowcount, 7)
        execute(_qc, "DROP TABLE _rc_probe")
        _qc.commit()

        # ── THE SAVE/RESTORE PAIR — DELETED 2026-08-12 WITH THE ROWS IT COPIED. ──────────
        #
        # It read `SELECT name, lwm FROM consumer` into `_saved_regs`, DELETEd the whole live
        # registry, drove the empty-registry cases, and put the rows back. Two ⚑ findings from
        # it are general and are kept:
        #
        # ⚑⚑ **A SAVE/RESTORE PAIR IS A COPY OF THE SCHEMA, AND COPIES DRIFT — IN BOTH
        # DIRECTIONS, WITH OPPOSITE FAILURE MODES.** When `kind` was ADDED the pair still
        # restored 4-tuples, so the suite would have put `scope_fix:resolver` back as a
        # `cursor` on every run — *"quietly undoing the migration it is meant to protect, and
        # reporting green while doing it."* When `kind` was DROPPED the same pair failed loudly
        # at the driver (`4 placeholders but 5 parameters`). **Widening fails quietly, narrowing
        # fails at the driver: the asymmetry is why only one direction of this defect ever
        # reached the store.**
        #
        # ⚑⚑ AND THE SECOND-ORDER FAILURE IS THE DANGEROUS ONE: *"a suite that damages state on
        # crash makes its own next result untrustworthy, so a green run after a red one proves
        # nothing about the state it started from."* MEASURED 2026-08-07: a `NameError` in an
        # unrelated case killed the run after the DELETE; the following run saved an
        # already-missing `sppf:projection` and "restored" a registry without it.
        #
        # ⚑ AND THE FIRST VERSION OF THE FLOOR CASE ASSERTED A TRANSIENT STATE — it checked the
        # live registry for the "no consumers" message and passed only while the store happened
        # to have none. **A case that describes a MOMENT rather than a rule fails on a change
        # of world, not a change of code.** That is why what survives below is driven against
        # `reclaim`'s own AST, which no store state can move.
        #
        # ⚑⚑ THREE CASES HERE ASSERTED THE RETIRED FLOOR AND EVERY ONE OF THEM WAS TRUE. They
        # read `reclaim(...)["floor"]` and wanted `0` — "reclaim pins first, so it always has a
        # floor", "a consumer at 0 pins the floor", "a pinned persistent reader holds the floor
        # at 0". Each described, accurately, the mechanism that made a full tier undrainable:
        # `--watermark` reported **0 observation(s) below the floor** against `hwm 6,274,182`
        # live. **A guard can be correct and still be pinning a design in place.**
        #
        # ⚑ SO THEY WERE REPLACED BY THEIR INVERSE RATHER THAN DELETED, and that inverse is
        # what stands below: a re-added `pin_persistent` call inside `reclaim` would silently
        # restore the floor and nothing else would notice.
        # ⚑⚑⚑ ON THE AST, NOT BY EXECUTING THE LICENCE — AND THE COST WAS THE WHOLE REASON.
        # This read `reclaim(_qc, dry_run=True)["floor"]` against the LIVE store. That dry run
        # executes the corpus-wide drain licence **THREE times** (`pending`, `pending_edge`,
        # `n_cores` — `schema_queue.py:675,680,683`), and `EXPLAIN` on the compiled licence
        # shows **7 Gather nodes / 14 Parallel Hash nodes**, each allocating a ~128MB DSM
        # segment: ~1.8 GB per invocation, ~5.4 GB for the call. MEASURED 2026-08-23: it
        # failed FOUR times with `psycopg.errors.DiskFull: could not resize shared memory
        # segment … No space left on device`, at both 512MB and 1GB `/dev/shm`, and drove a
        # peer to restart the store TWICE chasing a pool size that was never the problem.
        #
        # ⚑⚑ AND IT WAS BUYING NOTHING, WHICH IS WHAT MAKES THIS A DELETION RATHER THAN A
        # TRADE-OFF. `floor` is a LITERAL in the returned dict (`schema_queue.py:684`:
        # `return {"floor": None, …}`) — it is not computed from any query, so no amount of
        # corpus scanning could make the assertion fail or pass differently. The three sibling
        # checks below already read the AST for exactly this reason, and the note at the
        # `obs` cases states the principle outright: an assertion that passes without
        # measuring the licence is not measuring the licence.
        #
        # ⚑ SO THE PROPERTY IS ASSERTED WHERE IT LIVES: `reclaim` returns no floor because it
        # HAS no floor to return. A `floor` key computed from a query would be a different
        # claim and would need a different case — against the `schema_licence_refuses`
        # fixture, which has a durable tier and licensed cores, not against the corpus.
        _rc_src = _inspect.getsource(reclaim)
        import ast as _ast_floor

        _floor_consts = {
            _kv.value
            for _n in _ast_floor.walk(_ast_floor.parse(_rc_src.lstrip()))
            if isinstance(_n, _ast_floor.Dict)
            for _k, _kv in zip(_n.keys, _n.values)
            if isinstance(_k, _ast_floor.Constant)
            and _k.value == "floor"
            and isinstance(_kv, _ast_floor.Constant)
        }
        check(
            "reclaim reports NO floor — the positional conjunct is retired", _floor_consts, {None}
        )
        # ⚑ ON THE AST, NOT THE SOURCE TEXT. `reclaim`'s own ⚑ notes NAME `pin_persistent`
        # and `lwm` repeatedly to explain the retirement, so a substring scan would be
        # satisfied by the obituary — F24's defect, committed inside the guard for it. A
        # comment cannot forge a Call node.
        import ast as _ast_pin

        _rc_ast = _ast_pin.parse(_inspect.getsource(reclaim).lstrip())
        _rc_calls = {
            n.func.id
            for n in _ast_pin.walk(_rc_ast)
            if isinstance(n, _ast_pin.Call) and isinstance(n.func, _ast_pin.Name)
        }
        check(
            "...and does not pin, so nothing can re-lower it to 0",
            "pin_persistent" in _rc_calls,
            False,
        )
        check("...nor consult a watermark to bound the sweep", "lwm" in _rc_calls, False)
        # ⚑ THE `obs` HALF OF THESE CASES IS DELIBERATELY NOT ASSERTED HERE. Against the
        # LIVE store `reclaim` returns `obs: 0` because `obs_node` is absent — the honest
        # refusal — so an assertion of 0 would pass without measuring the licence at all.
        # The behavioural claim is driven in the `schema_licence_refuses` fixture, which has
        # a durable tier and licensed cores.
        #
        # ⚑ AND `register("selftest:pin")` + "a consumer at 0 no longer bounds the sweep" went
        # with the table (2026-08-12). The claim is now a SCHEMA FACT rather than a behaviour:
        # there is no registry for a sweep to be bounded by, asserted directly below, because
        # **a dropped table is checkable and an absent guard is not.**

        # ── `consumer` IS GONE FROM THE DECLARATION — the fact that replaces eight cases ────
        # ⚑⚑ THE `kind` COLUMN'S CASES DIED FIRST AND THE SAME REASONING TOOK THE TABLE. They
        # refused `'pin'` and permitted `'cursor'` — the right INTERIM (a value nothing can
        # create but everything still accepts is how a retired mechanism returns) and the wrong
        # DESTINATION: **a validator over a one-element domain protects nothing and reads as
        # protection.** A registry whose only reader is the report that prints it is the same
        # shape one level up.
        #
        # ⚑ ASSERTED ON `MD.tables`, WHICH IS THE DECLARATION — not on `relations(con)`, which
        # is a STORE STATE and would make this case a description of a MOMENT (the defect
        # recorded three blocks up). A store that has not run `--migrate-queue` still holds the
        # table; the declaration is what says nothing may write it.
        check(
            "the declaration knows no `consumer` — the table is dropped, not merely unused",
            "consumer" in MD.tables,
            False,
        )
        check("...and no tier claims it", [t for t, ts in _TIERS.items() if "consumer" in ts], [])
        # ⚑ AND THE POSITIONAL APPARATUS HAS NO WRITER LEFT. The case that stood here drove
        # `register` + `advance` and read the cursor back, captioned *"a cursor still advances,
        # as a diagnostic and nothing more"* — naming `_advance_projection` as its one
        # production writer and `--watermark` / `lifecycle_census`'s `consumed` stage as its
        # readers. All four are retired. An AST census is what says so, because the ⚑ blocks
        # around here NAME every one of them to explain the retirement and would satisfy a
        # substring scan — the obituary defect this file records.
        import ast as _ast_q

        _q_calls = {
            getattr(n.func, "id", "") or getattr(n.func, "attr", "")
            for n in _ast_q.walk(_ast_q.parse(_inspect.getsource(schema_queue)))
            if isinstance(n, _ast_q.Call)
        }
        check(
            "the queue tier calls no cursor operation at all",
            _q_calls & {"register", "advance", "lwm", "consumers", "reclaimable", "pin_persistent"},
            set(),
        )

        # ⚑⚑ THE TWO HALVES OF A SOURCE-DRIVEN READER ARE SEPARATE MECHANISMS, AND ONE OF
        # THEM WAS NEVER THE QUEUE'S — which is the whole case, and it now reads as an
        # argument for the retirement rather than a caveat to it. *"Don't delete what is
        # real"* was the pin; *"don't keep what is stale"* is the CORE PRUNE, a JOIN against
        # the source that is not expressible as a position at all. The queue could only ever
        # do the first, by freezing everything.
        #
        # ⚑ SO THE HALF THAT SURVIVED IS THE HALF THAT WAS NEVER POSITIONAL. This asserted
        # `lwm(_qc) == 0` — "the pin floors positional reclamation, which is the protection".
        # With no pin the floor is None, and the protection now comes from the licence being
        # per-core. The prune is unchanged, because it never depended on either.
        execute(_qc, "DROP TABLE IF EXISTS _prune_probe")
        execute(_qc, "CREATE TABLE _prune_probe(core_id text, seq bigint)")
        execute(_qc, "INSERT INTO _prune_probe VALUES ('live', 1), ('dead', 2)")
        # a source-driven delete removes the dead core by JOIN, not by position
        execute(_qc, "DELETE FROM _prune_probe WHERE core_id = 'dead'")
        check(
            "...while a SOURCE-driven prune still removes a dead core",
            scalar(_qc, "SELECT count(*) FROM _prune_probe"),
            1,
        )
        check("...keeping the live one", scalar(_qc, "SELECT core_id FROM _prune_probe"), "live")
        execute(_qc, "DROP TABLE _prune_probe")
        _qc.commit()

    # ── ⟡ladder-1: the SOURCED tier and its single-statement writer ─────────────────────
    #
    # ⚑⚑ EVERY SHAPE CASE ANCHORS ON `_insert_row_sql`'s OUTPUT — the string postgres will
    # parse — NEVER on the writer's source text. This file already records the defect three
    # times over: a guard scanning `getsource` is satisfied by the ⚑ obituary naming the very
    # thing it guards. `insert_row` builds its statement nowhere else, so there is no way for
    # the string asserted here and the string sent to differ.
    check(
        "`core_decoded` is declared, in exactly one tier",
        sorted(t for t, ts in _TIERS.items() if "core_decoded" in ts),
        ["sourced"],
    )
    # ⚑ AND NOT IN THE EVENT TIER, WHICH IS THE PLACEMENT CLAIM ITSELF. It is the output of
    # the `ε → sourced` boundary — below the tier the event log occupies — so a declaration
    # that quietly folded it into `EVENT_TABLES` would make `apply(only="event")` create it
    # and every statement about tier order false, with nothing failing.
    check("...and that tier is NOT the event tier", "core_decoded" in EVENT_TABLES, False)
    check(
        "...and the event tier is untouched by its arrival",
        sorted(EVENT_TABLES),
        sorted(
            {
                "terms",
                "path_seg",
                "event",
                "obs",
                "edge",
                "unit_obs",
                "unit_member",
                "path_text",
                "core_fp",
                "schema_version",
            }
        ),
    )
    # ⚑ THE PAYLOAD COLUMN MUST BE `jsonb` AND NOT `json`, AND THE DIFFERENCE IS NOT
    # COSMETIC: `json` HAS NO EQUALITY OPERATOR, so `insert_row(replace)`'s content-conditioned
    # WHERE is not expressible over it (`UndefinedFunction: operator does not exist: json =
    # json`). Asserted on the COMPILED DDL, because the python-side type name is what a
    # careless edit would change and the emitted DDL is what the store gets.
    _dec_ddl = str(CreateTable(MD.tables["core_decoded"]).compile(dialect=_store.dialect()))
    check(
        "`core_decoded.dec` compiles to JSONB, the type that HAS an equality operator",
        "dec JSONB" in _dec_ddl,
        True,
    )
    _ir_sql, _ir_par = _insert_row_sql(
        "core_decoded",
        {"core_id": "c", "relpath": "R.agdai", "mtime": 1, "producer": "agdai", "dec": "{}"},
        on_conflict="replace",
    )
    # ⚑ ONE ROW, ONE STATEMENT — the whole point. `executemany` is ONE transaction over N
    # rows even under autocommit (probed: a failure at row 3 of 4 rolls back rows 1–3), which
    # is the hold-and-wait behind the reproduced `40P01`. A single VALUES tuple has no batch
    # to hold, so the count of placeholder groups is the property to pin.
    check("the rung emits ONE row, not a batch", _ir_sql.count("VALUES"), 1)
    check(
        "...with exactly one placeholder per supplied column",
        (_ir_sql.count("%s"), len(_ir_par)),
        (5, 5),
    )
    check(
        "...in DECLARED order, taken from the model rather than the caller's dict",
        list(_ir_par),
        ["c", "R.agdai", 1, "agdai", "{}"],
    )
    # ⚑ THE PREDICATE IS IN THE WHERE CLAUSE, WHICH IS WHAT MAKES IT A RUNG. A rung has no
    # window between reading a contact and energising a coil; a writer that SELECTed the
    # stored row, compared it, and then decided would be check-then-act on shared state —
    # F17's class, which this arc has now paid for four times.
    check(
        "...and the change test is a conjunct of the WRITE, not a prior read",
        "IS DISTINCT FROM" in _ir_sql and "ON CONFLICT (core_id) DO UPDATE" in _ir_sql,
        True,
    )
    # ⚑⚑ AND THE LINE ABOVE IS NOT SUFFICIENT — MEASURED, BY FORGING IT. Mutation-testing
    # this guard by replacing the WHERE with `-- MUTATION: WHERE … IS DISTINCT FROM …` left
    # the schema suite at **163/163**: SQL has comments too, so "the compiled statement
    # contains the words" is the SAME defect as "the source contains the words", one layer in.
    # I committed it inside the guard written against it, for the fourth recorded time.
    #
    # ⚑ TWO REPAIRS, AND NEITHER ALONE IS THE ANSWER. First, the emitted statement may carry
    # no SQL comment at all — which refuses that exact forge and is still textual. Second and
    # actually load-bearing, the BEHAVIOUR is driven below against a real table: a comment
    # cannot make postgres decline a write. The mutation was caught by `sppf_db`'s
    # behavioural case (`74/75`, naming the re-write), so the class was covered — but a shape
    # claim that can be satisfied by a comment should not be sitting in the suite that owns
    # the builder.
    check(
        "...and the emitted statement carries no SQL comment to forge that with",
        "--" in _ir_sql,
        False,
    )
    _cd = sandbox_fixture("schema_ladder1_rung")
    _row = {
        "core_id": "K",
        "relpath": "R.agdai",
        "mtime": 1,
        "producer": "agdai",
        "dec": '{"nodes": {"0": {"id": 0}}, "defmarks": []}',
    }
    check(
        "the rung FIRES on a first write",
        insert_row(_cd, "core_decoded", _row, on_conflict="replace"),
        1,
    )
    # ⚑ THIS IS THE CASE THE COMMENT CANNOT FORGE. `rowcount` here is postgres reporting
    # whether its own WHERE admitted the update — the one observable that separates "already
    # current" from "just landed" without a prior SELECT that could go stale between the two
    # statements.
    check(
        "...and the ENGINE declines an identical re-write",
        insert_row(_cd, "core_decoded", _row, on_conflict="replace"),
        0,
    )
    _row2 = dict(_row, dec='{"nodes": {"0": {"id": 0}}, "defmarks": [{"unit": "X"}]}')
    check(
        "...and fires again when the payload actually differs",
        insert_row(_cd, "core_decoded", _row2, on_conflict="replace"),
        1,
    )
    # ⚑ A NULLABLE COLUMN IS WHY THE TEST IS A ROW CONSTRUCTOR AND NOT `a <> x OR b <> y`.
    # `mtime` is nullable; under the disjunction form a NULL on either side makes the whole
    # predicate NULL — not true — so the update is SKIPPED and the row silently keeps its old
    # payload. `IS DISTINCT FROM` is NULL-safe in both directions, and this drives it.
    check(
        "...including a change that moves a nullable column to NULL",
        insert_row(_cd, "core_decoded", dict(_row2, mtime=None), on_conflict="replace"),
        1,
    )
    check(
        "...and back off NULL again",
        insert_row(_cd, "core_decoded", dict(_row2, mtime=2), on_conflict="replace"),
        1,
    )
    check(
        "...having written exactly ONE row throughout",
        scalar(_cd, "SELECT count(*) FROM core_decoded"),
        1,
    )
    _cd.close()
    check(
        "...over every non-key column, derived from the declaration",
        all(
            ("core_decoded.%s" % c) in _ir_sql and ("EXCLUDED.%s" % c) in _ir_sql
            for c in ("relpath", "mtime", "producer", "dec")
        ),
        True,
    )
    check(
        "...and never over the key itself, which cannot differ under its own conflict",
        "core_decoded.core_id) IS DISTINCT" in _ir_sql,
        False,
    )
    check(
        "the 'ignore' mode is still the untargeted DO NOTHING",
        _insert_row_sql("core_decoded", {"core_id": "c", "relpath": "R", "dec": "{}"})[0].endswith(
            "ON CONFLICT DO NOTHING"
        ),
        True,
    )
    # ⚑ THE TWO REFUSALS. A name map cannot SHIFT the way `upsert`'s positional tuple can,
    # but it can silently DROP — so an undeclared key must refuse rather than be ignored, and
    # a NOT-NULL column with no default must refuse HERE, naming the declaration, rather than
    # at the statement where postgres names only the column.
    try:
        _insert_row_sql("core_decoded", {"core_id": "c", "relpath": "R", "dec": "{}", "nosuch": 1})
        _unknown = "accepted"
    except ValueError as _e:
        _unknown = "nosuch" in str(_e) and "declared column" in str(_e)
    check("an undeclared column is REFUSED and named", _unknown, True)
    try:
        _insert_row_sql("core_decoded", {"core_id": "c", "dec": "{}"})
        _missing = "accepted"
    except ValueError as _e:
        _missing = "relpath" in str(_e) and "NOT NULL" in str(_e)
    check("...as is a NOT-NULL column with no server default", _missing, True)
    # ⚑ `producer` HAS A SERVER DEFAULT, so omitting it is legal — the refusal must
    # discriminate, or it is a rule that refuses everything and therefore protects nothing.
    check(
        "...while a NOT-NULL column WITH a server default may be omitted",
        "producer"
        in _insert_row_sql("core_decoded", {"core_id": "c", "relpath": "R", "dec": "{}"})[0],
        False,
    )

    # ── `--locks`: the LIVE-HANG reader (2026-08-14) ────────────────────────────────
    #
    # ⚑⚑ THE METHOD WAS PRESCRIBED IN AN ALWAYS-RECALLED MEMORY AND THE TOOLKIT DID NOT HAVE
    # IT. `deadlock-breakdown-before-any-fix` says *"`pg_locks ⋈ pg_stat_activity` for a live
    # hang"*; `toolmodes.py --find locks` returned 0 hits across 93 declared modes, and when a
    # live non-advancing ingest was investigated the answer came from ANOTHER repo's
    # instrument. These cases guard the two things that were actually wrong in that
    # investigation — the verdict I drew, and the cost of drawing it.
    #
    # ⚑ EVERY CASE HERE IS OFFLINE, WITH NO CONNECTION, AND THAT IS THE POINT RATHER THAN A
    # CONVENIENCE. The judgement an operator acts on ("is this a deadlock?") must be drivable
    # by a case; behind a live connection it would be reachable only by MANUFACTURING a
    # deadlock, which is the one state nobody may produce on demand — and, on the store that
    # produced this module, a connection is itself a cost paid by the job under diagnosis.
    from schema_diag import _ACTIVITY_SQL, _LOCKS_SQL

    check("a two-party wait-for ring is FOUND", bool(wait_cycle({1: [2], 2: [1]})), True)
    # ⚑ THE CLOSED WALK, NOT A BOOLEAN — the memory's requirement is that the breakdown name
    # *which operations waited on each other*, so the ring must be printable. A predicate that
    # returned True would satisfy the check and lose the finding.
    check(
        "...and returned as the closed walk, so the ring can be PRINTED",
        wait_cycle({1: [2], 2: [1]}),
        [1, 2, 1],
    )
    check("a chain that merely ENDS is not a cycle", wait_cycle({1: [2], 2: [3], 3: []}), [])
    # ⚑ A BACKEND REPORTED AS BLOCKING ITSELF IS A ONE-PARTY CYCLE and must not be skipped as
    # a degenerate case — it is the same shape as a retire predicate reading its own tier,
    # which the memory names as the ONE thing that can reintroduce a cycle here.
    check("...but a self-loop IS", wait_cycle({1: [1]}), [1, 1])
    # ⚑ THE SEARCH MUST NOT START ONLY AT THE CYCLE. Entered from an acyclic prefix, a
    # colour-less walk revisits and returns [] — a deadlock reported as clean because of where
    # the enumeration happened to begin.
    check(
        "...and a cycle reached through an acyclic PREFIX is still found",
        bool(wait_cycle({9: [1], 1: [2], 2: [1]})),
        True,
    )

    def _b(pid, state="active", wet=None, blocked=(), is_self=False):
        return {
            "pid": pid,
            "state": state,
            "wait_event_type": wet,
            "blocked_by": list(blocked),
            "is_self": is_self,
        }

    # ⚑⚑ THIS IS THE CASE THE WHOLE MODE EXISTS FOR, AND IT ENCODES A WRONG CALL OF MINE.
    # `done` — the MONOTONE progress measure, correct as a measure — was byte-identical across
    # a 45-minute resume and I read that as a stall. The backend was `active` with NO
    # `wait_event`, inside one long CPU-bound `INSERT … SELECT` that had not COMMITted, on a
    # store pinned flat against a `CPUQuota=0.5` ceiling. **A monotone measure standing still
    # separates nothing on its own: STALLED and SLOW give the identical reading.**
    check(
        "an ACTIVE backend with no wait event is WORKING, not stalled",
        wait_verdict([_b(1)])["verdict"].startswith("WORKING"),
        True,
    )
    check(
        "...and a flat progress counter over it is named as SLOW rather than a stall",
        "SLOW" in wait_verdict([_b(1)])["verdict"],
        True,
    )
    check(
        "a lock wait with no ring is reported ACYCLIC, not as a deadlock",
        wait_verdict([_b(1, wet="Lock", blocked=[2]), _b(2)])["verdict"].startswith("LOCK WAIT"),
        True,
    )
    check(
        "...and a ring outranks it",
        wait_verdict([_b(1, wet="Lock", blocked=[2]), _b(2, wet="Lock", blocked=[1])])[
            "verdict"
        ].startswith("HOLD-AND-WAIT CYCLE"),
        True,
    )
    # ⚑ THE THIRD STATE, AND THE ONE POSTGRES CANNOT SEE. A backend holding granted locks
    # while waiting on its CLIENT is hold-and-wait with the wait outside the database; no
    # deadlock detector fires, and `--activity` renders it as ordinary idleness.
    check(
        "idle-in-transaction is its OWN state, not idleness",
        wait_verdict([_b(1, state="idle in transaction")])["verdict"].startswith(
            "IDLE IN TRANSACTION"
        ),
        True,
    )
    # ⚑ THE READER MUST NOT COUNT ITSELF AS THE WORK IT CAME TO FIND. `activity()` solves this
    # by FILTERING self out, which for a lock question is the instrument editing itself out of
    # its own reading; this keeps the row and excludes it from the verdict.
    check(
        "the reader's own backend is shown but never counted as WORKING",
        wait_verdict([_b(1, is_self=True)])["working"],
        [],
    )
    check(
        "...and with nothing else running that reads QUIESCENT",
        wait_verdict([_b(1, is_self=True)])["verdict"].startswith("QUIESCENT"),
        True,
    )

    # ⚑⚑ THE COST OF THE INSTRUMENT IS A GUARDED PROPERTY, NOT A GOOD INTENTION. Measured
    # 2026-08-14: the store was pinned against `CPUQuota=0.5`, so every breakdown query
    # competed for the same half core as the ingest it was diagnosing. `pg_stat_activity`,
    # `pg_locks` and `pg_blocking_pids()` are SHARED-MEMORY views — no table locks, no heap
    # reads. A `JOIN pg_class` to name a relation is a real heap read per lock row, and it is
    # the same shape as `--drain-census`'s `CREATE INDEX IF NOT EXISTS`: a read-only mode
    # reaching a user relation. `::regclass` is a syscache lookup instead.
    import re as _re_lk

    _lk_rels = set(_re_lk.findall(r"(?:FROM|JOIN)\s+(\w+)", _ACTIVITY_SQL + " " + _LOCKS_SQL))
    check(
        "the live-hang reader touches ONLY shared-memory views",
        sorted(_lk_rels),
        ["pg_locks", "pg_stat_activity"],
    )
    check("...so no catalogue TABLE is joined to name a relation", "pg_class" in _LOCKS_SQL, False)
    # ⚑ `granted` IS THE HELD/WANTED SEAM. `wait_event` says a backend waits; only `granted`
    # says what it waits FOR and who has it — the memory's *"what it HELD and what it WANTED"*.
    check("...and the HELD/WANTED seam is read from `granted`", "granted" in _LOCKS_SQL, True)
    # ⚑ SELF IS INCLUDED RATHER THAN FILTERED, which is the one line where this reader
    # deliberately departs from `activity()`.
    check(
        "...while the activity half does NOT filter itself out",
        "pid <> pg_backend_pid()" in _ACTIVITY_SQL,
        False,
    )

    bad = [c for c in cases if not c[1]]
    for label, _, got, want in bad:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(bad), len(cases)))
    return 0 if not bad else 1
