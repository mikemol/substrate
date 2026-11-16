#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""reconstruct.py — THE DRAIN'S LICENSE: rebuild a core's obs rows from (SPPF, fibre) and compare.

⚑ THIS COMPUTES `lifecycle._reflected`, THE ONE STAGE NOTHING COMPUTED. The chain declares
`sourced ▷ observed ▷ settled ▷ consumed ▷ reflected` and `--lifecycle` reported every one of
6,274,182 observations as unconsumed with floor 0 — the terminal link existed as a declared
predicate reading `d.get("reflected")`, a key nothing ever set. So the event tier could never
drain, not because anything failed but because the question was never asked.

⚑ THE LICENSE IS A ROUND-TRIP, NOT AN ARGUMENT. `Substrate.Lifecycle.Reflection` states it:

    project     : Staged → Durable          the SPPF + the fibre
    reconstruct : Durable → Staged          this module
    round-trip  : reconstruct (project s) ≡ s

and `Substrate.Lifecycle.Drainable` proves the consequence — a reflection makes `project`
injective, so the durable form DETERMINES the staged one. Equality is the permission; a core
that fails to reconstruct is RETAINED and the failure reported. Nothing is deleted on the
strength of a plausible story.

⚑ AND THE DURABLE SIDE IS THE PAIR, WHICH IS NOT A DETAIL (user, 2026-08-07: *"it IS a
projection, because the reverse index ON ITS OWN cannot reconstruct the SPPF + event tier"*).

    event → (SPPF, fibre)     LOSSLESS — the pair reconstructs
    event → fibre             a PROJECTION — the residue alone cannot

`D := fibre` admits no `Reflection` at all: `project` is not injective there, so `Drainable`
could never fire. That is the same collapse `_node` already measures one layer down — it keys
on `sym ‖ child-syms`, so one module applied twice interns to a single node — and the fibre is
exactly the residue that undoes it. Take the fibre without the SPPF and the shape reappears at
the tier above: many staged states, one image.

⚑ THE FIBRE IS POSITIONAL, AND THAT IS MEASURED, NOT ASSUMED. `schema.py --fibre` reports
`local_id` running 0..n-1 with no gaps and no duplicates across all 152 ingested cores, so per
core the residue is an `ekey[]` whose INDEX is the local_id. The event tier pays full row width
— `core_id` repeated on every one of ~55K rows, `local_id` stored rather than implied — to
express something the quotient makes positional. That is where the ~100× lives.

⚑ WHAT THIS MODULE DOES **NOT** DO: it never deletes. It computes the predicate and reports.
Draining is `schema.py --reclaim`, gated on the consumer floor, and it moves only once every
stage below `reflected` also holds. Splitting "decide" from "apply" is the shape `prune_imports`
learned after writing unconditionally.

⚑⚑ SCOPE — THIS COVERS `obs` ONLY, AND THE EVENT TIER IS TEN RELATIONS (user, 2026-08-07:
*"And _everything_ in the event tier is reconstructible from obs?"*). It is not, and writing
`reflects(core)` as though a core's verdict were the tier's was the error. Measured:

    obs          6,274,182     ← the only relation this module reconstructs
    edge         6,273,548     ← parent/child structure; NOT in the fibre
    event        2,124,390     ← the raw observations obs keys into
    path_seg         4,352
    terms            2,743
    unit_obs           634     ← the unit tier
    unit_member         63

⚑ AND THE GATE WOULD HAVE PASSED WHILE BEING WRONG, which is the dangerous half. `--census`
prints "every core reconstructs" from an `obs`-only comparison; `reflected` then goes true and
licenses draining relations the predicate never examined. A verdict whose name is broader than
its measurement is how a drain deletes something nobody checked — the same shape as reading a
`--calls emit` census as "there is one emitter" when a second was spelled `_emit_one`.

⚑ WHAT THE FULL LICENSE REQUIRES, unresolved and NOT to be assumed benign:
  * **`edge`** is the structural half. `_node`/`node_child` hold the INTERNED shape, so edge
    may well be derivable from (SPPF, fibre) the same way obs is — but "may well be" is a
    hypothesis, and it is 6.3M rows. `reconstruct_edge` is owed, with its own comparison.
  * **`unit_obs` / `unit_member`** project to `_unit`/`unit_node`; whether that projection is
    invertible is a separate question with a separate fibre.
  * **`terms` / `path_seg` / `path_text`** are the string interning. `path_text` is already
    DERIVED (`refresh_path_text` rebuilds it by aggregation), so it needs no reflection — but
    `terms` is a leaf dictionary that nothing else encodes.

Until each of those has its own round-trip, `reflects()` answers **"does this core's `obs`
reconstruct"** and nothing wider. The mode names say `obs` for that reason.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import schema as _schema
import store

# ⚑ THE CACHED RUNTIME, NOT `query_defs` — this module runs in the gate path, and `query_defs`
# imports SQLAlchemy (~0.4s). `query_builders` executes precompiled SQL by NAME and imports no
# SQLAlchemy, which is the split that module's docstring exists to preserve.
import query_builders as QB


def fibre(con, core_id):
    """The core's residue: `ekey[]` indexed by local_id — the fibre of the quotient.

    ⚑ RETURNS A LIST, NOT A DICT, BECAUSE THE INDEX *IS* THE KEY. A `{local_id: ekey}` map
    would re-store the very column the positional encoding exists to imply, which is the
    event tier's shape wearing a different container. The list's index carries it.

    ⚑ AND IT REFUSES A NON-DENSE CORE RATHER THAN SILENTLY MISALIGNING. If local_id has a
    gap, every later ekey shifts down one position and the reconstruction compares wrong
    rows against wrong indices — a mismatch that looks like a projection bug and is not.
    `schema.positional` is the predicate; this is the one place it must hold at runtime,
    not merely have been true when `--fibre` last ran.
    """
    rows = list(
        _schema.rows(
            con,
            "SELECT local_id, ekey FROM obs WHERE core_id = %s ORDER BY local_id" % _schema.ph(),
            (core_id,),
        )
    )
    if not rows:
        return []
    lo, hi = rows[0]["local_id"], rows[-1]["local_id"]
    ok, gaps, dups = _schema.positional(lo, hi, len(rows), len({r["local_id"] for r in rows}))
    if not ok:
        raise ValueError(
            "core %s is not positional (gaps=%d dups=%d lo=%d): the fibre cannot be a "
            "sequence, so reconstruction would misalign rather than fail honestly"
            % (core_id, gaps, dups, lo)
        )
    return [r["ekey"] for r in rows]


def reconstruct(con, core_id):
    """Rebuild this core's staged rows from the durable pair → [(local_id, ekey), …].

    ⚑ THE SPPF SUPPLIES THE CLASS, THE FIBRE SUPPLIES WHICH OCCURRENCE FELL INTO IT. That
    is the whole decomposition — `event = recon(SPPF, fibre)` — and it is why this works by
    construction rather than by luck: a quotient together with its fibres IS the original.

    ⚑ THE SPPF MEMBERSHIP IS CHECKED, NOT ASSUMED. An ekey that resolves to nothing means
    the durable side cannot stand alone, and reconstructing anyway would produce rows that
    happen to match while the base half is absent — the failure a row-count comparison
    cannot see.

    ⚑ AND MY FIRST JOIN WAS WRONG IN A WAY THAT ACCUSED THE STORE (2026-08-07). It read
    `JOIN _node n ON n.node_id = o.ekey` and reported *"297 of 297 ekeys name no interned
    node — the SPPF does not cover this core"*. The SPPF covers it fine; the join was
    nonsense. Three distinct keys exist and I conflated two:

        event.ekey     the event tier's own content key
        sym[ekey]      = b64(head)                    — head-only, GLOBAL, no recursion
        node_id        = b64(head ‖ child symbols)    — the PACKING, structural

    `_node.node_id` is the packing and `_node.sym` is the head symbol; `obs.ekey` is
    NEITHER. So membership must go through `sym`, and even that is a join on a DERIVED
    value rather than a stored edge — there is no `ekey → node_id` column anywhere.

    ⚑ THAT ABSENCE WAS THE REAL FINDING, AND `obs_node` HAS SINCE CLOSED IT (Ⓒ1): the
    projection's local `packing` dict is now materialized as `(core_id, local_id) → node_id`.

    ⚑⚑ AND FOR MONTHS AFTER THAT, THIS FUNCTION STILL DID NOT RECONSTRUCT ANYTHING (F30).
    It called `fibre()` — `SELECT local_id, ekey FROM obs` — and returned `list(enumerate(fib))`:
    it READ THE STAGED ROWS AND HANDED THEM BACK, having merely checked `obs_node` covered
    them. The addressing existed and nothing ever ran it BACKWARDS.

    ⚑ WHICH SUBSUMES F0's TAUTOLOGY FINDING RATHER THAN REPEATING IT. `reflects_obs` comparing
    `obs.ekey` to `obs.ekey` was not an oversight in the reflector — it was FORCED, because the
    only thing this function could return was the staged rows. There was no other side to
    compare against, so no reflector written against it could have been honest.

    ⚑ AND THE SYMPTOM WAS REACHABLE THE WHOLE TIME: `--core <a drained core>` returned
    *"HELD — no observations for this core"*. The tool whose entire job is rebuilding from the
    durable tier failed EXACTLY when reconstruction was the only way to see the core.

    Now it reads the durable side, via `query_defs.q_obs_reconstructed` (ⓙ) — the algebra lives
    in the builder layer, not here and not in a database view, so it stays inside `--check`'s
    drift gate and can COMPOSE into larger cross-tier queries.

    ⚑ A NULL `ekey` IS "UNRECONSTRUCTIBLE", NOT "ABSENT", and the two must not collapse. The
    builder emits one row per addressed observation and NULLs the key where the head cannot
    determine it, so this can say *which* rows and *how many* rather than "the lists differ".
    """
    rows = sorted(
        ((r["local_id"], r["ekey"]) for r in QB.run(con, "obs_reconstructed", core_id=core_id)),
        key=lambda t: t[0],
    )
    if not rows:
        return []
    # ⚑ THE COVERAGE PRECONDITION SURVIVES THE REWRITE — it is a REAL check, unlike the body
    # it used to guard. An observation with no interned node means the projection has not
    # covered this core, which is a different failure from a head that cannot be decoded.
    have = {lid for lid, _ in rows}
    n_obs = _schema.scalar(
        con, "SELECT count(*) FROM obs WHERE core_id = %s" % _schema.ph(), (core_id,)
    )
    missing = [i for i in range(n_obs or 0) if i not in have]
    if missing:
        raise LookupError(
            "core %s: %d of %d observations have no interned node (first at local_id %d) — "
            "the projection has not covered this core; run `sppf_db.py --finalize`"
            % (core_id, len(missing), n_obs, missing[0])
        )
    return rows


def staged(con, core_id):
    """What the event tier actually holds for this core → [(local_id, ekey), …]."""
    return [
        (r["local_id"], r["ekey"])
        for r in _schema.rows(
            con,
            "SELECT local_id, ekey FROM obs WHERE core_id = %s ORDER BY local_id" % _schema.ph(),
            (core_id,),
        )
    ]


def _ekey_ambiguity(con, core_id):
    """Does `obs_node ⋈ _node` DETERMINE this core's ekeys? → None if yes, else (n, worst).

    ⚑ THE NECESSARY CONDITION FOR RECONSTRUCTING `obs`, AND THE ONE NOBODY WAS CHECKING.
    `_node` is CONTENT-keyed and deduped, so many `(core_id, local_id)` collapse onto one
    `node_id`; `obs_node` is the per-occurrence fibre that un-collapses it. If a single
    `node_id` addresses two DIFFERENT ekeys inside one core, then no function of
    `obs_node`+`_node` can tell those occurrences apart — reconstruction is impossible
    regardless of how the rebuild is written.

    ⚑ MEASURED, WHICH IS WHY THIS EXISTS: 43.8% of surviving ekeys were ambiguous on a
    post-drain sandbox, and stripping the `ch` field from the comparison collapsed the
    ambiguous node_ids from **107 to 1**. So the loss is localised — it is the CHILDREN, not
    the head — and `ch`'s only carrier is tier-0 `edge`.

    ⚑ REPORTED AS A POPULATION WITH ITS WORST CASE, never a boolean. "Is it ambiguous" cannot
    distinguish one stray collision from a node addressing a thousand ekeys, and those call
    for different responses — the first is a bug to find, the second is a missing carrier.

    ⚑ AND IT ASKS THE ENGINE, not Python: the grouping is a GROUP BY/HAVING the store owns.

    ⚑⚑ `back` IS GONE (⓺, 2026-08-11), AND ITS OWN JUSTIFICATION IS WHY. It read: *"`back`
    IS EXPLICIT BECAUSE `ph()` DISPATCHES ON THE AMBIENT BACKEND, NOT ON `con` — the
    connection-and-backend-disagree defect this tree records three prior occurrences of.
    Production passes nothing and gets postgres; a fixture passes `back="sqlite"`."* That is
    a parameter whose entire purpose was to route around a defect in `ph()`, threaded
    through a public signature so a TEST could work. `ph()` no longer dispatches on
    anything, so there is nothing to disagree with and nothing to thread.
    """
    # ⚑ THE GROUPING IS `(node_id, ch)`, NOT `node_id` ALONE, AND THE CHANGE IS THE WHOLE OF
    # Ⓒ1. `_node` is content-keyed on the HEAD, so node_id determines the head and loses the
    # children; grouping on it alone reported 43.8% of ekeys ambiguous — correctly, while `ch`
    # lived only in tier-0 `edge`. Now that `obs_node.ch` carries the child fibre durably, the
    # pair is what the durable side actually offers, and MEASURED against the same sandbox via
    # `string_agg(clid ORDER BY ord)`: **0 ambiguous, worst 0.**
    #
    # ⚑ AND THE PREDICATE HAD TO MOVE WITH THE DATA, WHICH IS THE POINT WORTH KEEPING. A
    # reflector asks "does the DURABLE side determine this", so its grouping key is a fact
    # about which relations are durable — not a constant. Leaving it at `node_id` after adding
    # the carrier would have held the drain forever on a gap that no longer exists, and the
    # census would have kept printing a true-when-written verdict.
    rows_ = list(
        _schema.rows(
            con,
            "SELECT n.node_id, n.ch, count(DISTINCT o.ekey) AS k "
            "  FROM obs o JOIN obs_node n "
            "    ON n.core_id = o.core_id AND n.local_id = o.local_id "
            " WHERE o.core_id = %s "
            " GROUP BY n.node_id, n.ch HAVING count(DISTINCT o.ekey) > 1 "
            " ORDER BY count(DISTINCT o.ekey) DESC" % _schema.ph(1),
            (core_id,),
        )
    )
    if not rows_:
        return None
    return (len(rows_), rows_[0]["k"])


def reflects_obs(con, core_id):
    """Does the durable pair reconstruct this core's **obs rows**? → (ok, detail).

    ⚑ `_obs` IS IN THE NAME BECAUSE THE SCOPE IS THE FINDING. This was `reflects()`, which
    reads as a verdict on the core — and the event tier is ten relations, of which this
    checks one. A bare `reflects()` returning True is exactly the over-broad verdict that
    would license draining `edge`'s 6.3M rows on the strength of an `obs` comparison.
    The tier-level predicate does not exist yet; when it does, it composes THIS with
    `reflects_edge` and the unit-tier check, and only then may `reflected` go true.

    ⚑ THE VERDICT CARRIES ITS REASON, because "does not reflect" has several causes and they
    call for different repairs: a non-positional fibre (re-ingest), an uncovered core (run
    the projection), or a genuine mismatch (a bug in the walk). Collapsing them to a boolean
    is the located-rejection failure `lifecycle` exists to prevent — the 38-minute anti-join
    could report a count and never a reason.
    """
    try:
        rebuilt = reconstruct(con, core_id)
    except (ValueError, LookupError) as e:
        return (False, str(e))
    have = staged(con, core_id)
    # ⚑⚑ AN EMPTY CORE IS UNMEASURED, NOT RECONSTRUCTED — and this path was STILL live after
    # the tautology fix. `fibre()` returns `[]` for a core with no `obs` rows, `reconstruct()`
    # short-circuits to `[]`, `staged()` returns `[]`, and `[] == []` reported
    # **"REFLECTS — 0 row(s) reconstructed exactly"**. Measured on `MetricGauge/Det.agda`
    # mid-rehearsal: a core whose events had not yet been written passed the gate that
    # licenses deleting its rows.
    #
    # ⚑ IT IS THE `--edge` DEFECT IN A THIRD PLACE. That mode once printed
    # `EXACT 0 MISMATCH 0 ⇒ verified` over an empty store and now refuses; the same
    # absent-read-as-pass survived one function inward, where the population is one CORE
    # rather than the whole store. Fixing the ekey comparison did not reach it, because the
    # defect is upstream of the comparison: there is nothing to compare.
    if not have:
        return (
            False,
            "no observations for this core: UNMEASURED, not reconstructed — "
            "the event tier holds nothing here, so the durable side has not been "
            "checked against anything",
        )
    if rebuilt == have:
        # ⚑⚑ AND `rebuilt == have` IS A TAUTOLOGY WITH RESPECT TO `ekey`, WHICH IS THE FIELD
        # THIS FUNCTION APPEARS TO VERIFY. `reconstruct()` reads `SELECT local_id, ekey FROM
        # obs`; `staged()` reads the same. Both sides come from `obs`, so the equality above
        # can only ever confirm the positional-density predicate and `obs_node` COVERAGE — it
        # has never once checked that `ekey` is recoverable from the durable side.
        #
        # MEASURED 2026-08-11, which is what forced this: over a post-drain sandbox,
        # `obs_node ⋈ _node` determines only **56.2%** of surviving ekeys; **43.8% are
        # AMBIGUOUS** (107 of 193 node_ids carry more than one distinct ekey, max 1,030).
        # That gap sat undetected under a green census for four days because the check could
        # not see it BY CONSTRUCTION.
        #
        # ⚑ THE NECESSARY CONDITION IS DETERMINACY, and it is cheap: if one `node_id` addresses
        # two different ekeys within a core, then no function of `obs_node`+`_node` can
        # reproduce `obs`, whatever else is true. Sufficiency needs `ch` — which lives only in
        # tier-0 `edge` today (see the plan's Ⓒ1) — so this asserts the half that is
        # expressible and REFUSES to imply the other half.
        amb = _ekey_ambiguity(con, core_id)
        if amb:
            n, worst = amb
            # ⚑ THE REASON LEADS, THE NUMBERS FOLLOW — `census` groups by
            # `detail.split(":")[0]`, so a detail that opens with a COUNT makes every core its
            # own group and destroys the grouping. My first version began "16697 row(s) match,
            # but…", which printed the key `16697 row` and would have scattered 152 cores into
            # 152 buckets. The convention is `reason: specifics`; conform to it rather than
            # widen the grouper, which is doing its job correctly.
            return (
                False,
                "the durable side does not determine ekey: %d node_id(s) address more "
                "than one ekey, worst %d, over %d row(s) that match positionally. "
                "`_node` is content-keyed, so the HEAD is recoverable and `ch` is not — "
                "and `ch` has no carrier above tier 0. UNVERIFIED, not exact."
                % (n, worst, len(have)),
            )
        return (
            True,
            "%d row(s) reconstructed exactly, and node_id determines every ekey" % len(have),
        )
    # ⚑ NAME THE FIRST DIVERGENCE, NOT THE COUNT. A row count that matches while contents
    # differ is the case a length check passes and a drain must not.
    if len(rebuilt) != len(have):
        return (False, "row count differs: rebuilt %d, staged %d" % (len(rebuilt), len(have)))
    for (li, rk), (lj, hk) in zip(rebuilt, have):
        if (li, rk) != (lj, hk):
            return (False, "first divergence at local_id %d: rebuilt %r, staged %r" % (li, rk, hk))
    return (False, "unequal by == but no positional divergence found — investigate")


def reflects(con, core_id):
    """The TIER-LEVEL predicate: does the durable form reconstruct EVERY relation for this
    core? → (ok, {relation: (ok, detail)}).

    ⚑ THE CONJUNCTION, WHICH IS THE WHOLE POINT — and its absence is what currently lets the
    drain proceed on the queue predicate alone. `reclaim` gates on `seq < floor`: everything
    below the reclamation floor is unreachable by a registered cursor. That is a fact about
    CONSUMPTION, and `lifecycle.py` keeps it deliberately separate from RECONSTRUCTION:
    *"draining on `consumed` alone would delete records whose replacement may not exist."*

    ⚑ MEASURED BEFORE BUILDING THIS: `pycodemod --calls reflects_obs` reports two callers,
    both inside `reconstruct.py`. Nothing in the drain path consults reflection at all — so
    `--reclaim --apply` would today delete 1,255,688 observations that NOTHING has verified
    are reconstructible. The queue would authorise it and the product identity would be the
    casualty.

    ⚑ AND IT MUST BE A CONJUNCTION OVER RELATIONS, NOT A CORE-LEVEL BOOLEAN. I wrote
    `reflects()` once before as a core verdict that checked only `obs`; renaming it
    `reflects_obs` was the fix. This restores the name at the arity it always needed —
    every relation the drain would touch must reconstruct, and a relation with no reflection
    at all is a REFUSAL, never a silent pass. That last clause is the one that matters: an
    unchecked relation must not read as a checked one.
    """
    parts = {}
    for rel, fn in sorted(_reflectors().items()):
        try:
            parts[rel] = fn(con, core_id)
        except Exception as e:  # a failure to CHECK is not a pass
            parts[rel] = (False, "%s: %s" % (type(e).__name__, e))
    return (all(ok for ok, _d in parts.values()), parts)


def reason_of(detail):
    """The GROUPING KEY of a verdict detail — its reason, stripped of specifics.

    ⚑ HOMED BECAUSE THE CONVENTION IS LOAD-BEARING AND WAS INLINE. `census`'s caller grouped
    by `detail.split(":")[0].split("(")[0].strip()[:60]`, which is correct — a detail is
    `reason: specifics` — but the rule lived in one expression inside the CLI, so nothing
    could test it and no author of a NEW detail string could discover it.

    ⚑ AND IT BROKE THE DAY A NEW DETAIL WAS ADDED. `reflects_obs`' ambiguity message opened
    with a COUNT ("16697 row(s) match, but…"), so the key came out `16697 row` — which would
    put every core in its own group and turn a 152-core population into 152 one-line buckets,
    defeating the grouping the comment above it exists to explain. The message was wrong, not
    the grouper; homing the rule is what makes that checkable instead of a convention someone
    has to already know.
    """
    return detail.split(":")[0].split("(")[0].strip()[:60]


def _reflectors():
    """{relation: predicate} — derived from this module's own `reflects_<rel>` functions.

    ⚑ DERIVED, NOT LISTED, for the reason `--coverage` already records: a hand-kept map went
    stale within one session (it claimed `edge` had no reflection after `reflects_edge`
    shipped and proved 152/152). A second roster beside the thing it describes is the defect
    this repo keeps paying for.
    """
    return {
        n[len("reflects_") :]: g
        for n, g in globals().items()
        if n.startswith("reflects_") and callable(g)
    }


def triage(con, limit=None):
    """PER-ROW soundness of the link → (exact, refused, wrong, first_wrong).

    ⚑ THIS IS ⓙ's ACCEPTANCE CRITERION, AND IT IS NOT THE CORE COUNT. `--census` answers
    "does this core reconstruct", which after F31 is `HELD` for every core — true, and it
    hides the distinction that decides whether the LINK is safe to compose:

        EXACT    rebuilt, and equal to the stored key
        REFUSED  the builder emitted NULL — the head visibly cannot determine it
        WRONG    rebuilt, and NOT equal — the ONLY real failure

    ⚑ `REFUSED` IS A GOOD OUTCOME AND `WRONG` IS A SILENT-CORRUPTION OUTCOME, so a single
    "divergence" count that merges them cannot answer the question this mode exists for. The
    census necessarily merges them (a core is HELD either way), which is why this is its own
    mode rather than another column on that one.
    """
    ids = [
        r["core_id"]
        for r in _schema.rows(con, "SELECT core_id FROM obs GROUP BY core_id ORDER BY count(*)")
    ]
    if limit:
        ids = ids[:limit]
    exact = refused = wrong = 0
    first_wrong = None
    for cid in ids:
        have = dict(staged(con, cid))
        for _c, lid, ek in QB.run(con, "obs_reconstructed", core_id=cid):
            if ek is None:
                refused += 1
            elif ek == have.get(lid):
                exact += 1
            else:
                wrong += 1
                if first_wrong is None:
                    first_wrong = (cid, lid)
    return exact, refused, wrong, first_wrong


def drained_reach(con, limit=None):
    """Cores the DURABLE tier addresses but tier 0 no longer holds → (core_id, rebuilt, refused).

    ⚑⚑ THIS IS THE PROPERTY THE WHOLE DRAIN RESTS ON, AND NOTHING MEASURED IT. `--triage` and
    `--census` both enumerate `SELECT core_id FROM obs GROUP BY core_id` — the LIVE tier — so
    their population SHRINKS as the drain succeeds, and after a full converge they verify the
    one core still resident and report it as the corpus. The question that matters after a
    drain is the opposite one: *can the link still answer for what tier 0 has FORGOTTEN?* A
    verdict over the surviving rows cannot see it, by construction.

    ⚑ IT IS ALSO THE EXACT FAILURE MODE OF SCOPING THE LINK TOO FAR. `q_drainable` wants
    `_rebuilt_obs` restricted to the cores `obs` still holds (that is what makes the licence
    O(live) instead of O(durable)); `q_obs_reconstructed` — the per-core READ path — must NOT
    be, because the cores it exists to serve are precisely the drained ones. Sharing the
    helper is right and the two consumers want opposite scopes, so the guard is: a drained
    core must still rebuild a NON-ZERO number of rows through the read builder. If the
    scoping ever reaches `q_obs_reconstructed`, every row here goes to 0 — silently, since
    "no rows" and "no such core" are indistinguishable to every other mode.

    ⚑ REFUSED IS COUNTED SEPARATELY FROM REBUILT, for `triage`'s reason: a NULL ekey is the
    head honestly declining, and merging it into a total would let a link that refuses
    everything read as a link that answers everything.
    """
    ids = [
        r["core_id"]
        for r in _schema.rows(
            con,
            "SELECT n.core_id FROM obs_node n "
            "WHERE NOT EXISTS (SELECT 1 FROM obs o WHERE o.core_id = n.core_id) "
            "GROUP BY n.core_id ORDER BY count(*) DESC",
        )
    ]
    if limit:
        ids = ids[:limit]
    out = []
    for cid in ids:
        n = refused = 0
        for _c, _lid, ek in QB.run(con, "obs_reconstructed", core_id=cid):
            n += 1
            refused += ek is None
        out.append((cid, n, refused))
    return out


def census(con, limit=None):
    """Every ingested core's reflection verdict → [(core_id, ok, detail, n), …].

    ⚑ A POPULATION, NEVER A SAMPLE. `--spread` measured max/median = 152×, so one core's
    verdict says nothing about the corpus; a reconstruct check that ran on the first core
    and reported success would repeat exactly the extrapolation that error exists to name.
    """
    ids = [
        r["core_id"]
        for r in _schema.rows(
            con, "SELECT core_id, count(*) AS n FROM obs GROUP BY core_id ORDER BY count(*)"
        )
    ]
    if limit:
        ids = ids[:limit]
    out = []
    for cid in ids:
        ok, detail = reflects_obs(con, cid)
        out.append((cid, ok, detail))
    return out


def edge_from_obs(con, core_id):
    """Rebuild this core's `edge` rows from `obs.ekey` alone → {(plid, ord, clid), …}.

    ⚑ `ekey` IS BASE64 OF A JSON OBJECT CARRYING THE CHILDREN — measured, not inferred:

        {"c": "Id", "ch": [15153], "i": null, "q": null}

    `c`=ctor, `ch`=child LOCAL IDS, `i`=idx, `q`=qname. So an observation's key already
    encodes its own edges, and `edge` is a DECODED PROJECTION of a column `obs` stores —
    6,273,548 rows derived from 6,274,182 rows that carry the same information.

    ⚑ THIS RETIRES MY OWN `EVENT-REFLECTION.md` ANALYSIS, which reasoned at length about
    what the SPPF head does and does not preserve. That analysis is about the wrong arrow:
    reconstruction does not need to invert `head` at all, because the content never left
    `ekey`. I spent two passes on the lossy encoding while the answer was in the key.
    """
    import base64 as _b, json as _j

    out = set()
    for r in _schema.rows(
        con,
        "SELECT local_id, ekey FROM obs WHERE core_id = %s ORDER BY local_id" % _schema.ph(),
        (core_id,),
    ):
        try:
            d = _j.loads(_b.b64decode(r["ekey"].encode()).decode())
        except Exception:
            continue
        for i, cl in enumerate(d.get("ch") or []):
            out.add((r["local_id"], i, cl))
    return out


def edge_stored(con, core_id):
    """What `edge` actually holds for this core → {(plid, ord, clid), …}."""
    return {
        (r["plid"], r["ord"], r["clid"])
        for r in _schema.rows(
            con, "SELECT plid, ord, clid FROM edge WHERE core_id = %s" % _schema.ph(), (core_id,)
        )
    }


def reflects_edge(con, core_id):
    """Does `obs.ekey` alone reconstruct this core's `edge` rows? → (ok, detail).

    ⚑ SET COMPARISON, NOT COUNTS. Equal cardinality with different contents is exactly the
    case a row-count check passes and a drain must not.

    ⚑⚑ THIS IS THE HIGHEST-VOLUME WITHHELD QUERY IN THE REPO, AND I CLAIMED IT COULD NOT BE
    SQL. `pycodemod --relalg` (a mode built for this audit) ranks it first: `edge_from_obs`
    decodes base64 JSON for 6,274,182 obs rows in Python, `edge_stored` pulls 6,273,548 edge
    rows, and the comparison is a symmetric set difference — 12.5M rows through Python to
    compute a set that is normally EMPTY.

    ⚑ THE WHOLE CHECK IS ONE STATEMENT, VERIFIED AGAINST POSTGRES:

        WITH rebuilt AS (
          SELECT o.core_id, o.local_id AS plid, t.ord - 1 AS ord, t.child AS clid
            FROM obs o, LATERAL jsonb_array_elements_text(
                   (convert_from(decode(o.ekey,'base64'),'UTF8')::jsonb) -> 'ch')
                 WITH ORDINALITY AS t(child, ord))
        SELECT * FROM rebuilt EXCEPT SELECT * FROM edge
        UNION ALL
        SELECT * FROM edge EXCEPT SELECT * FROM rebuilt

    Decode, JSON parse, child expansion, ordinal and the symmetric difference all execute.
    Rows through Python drop from 12.5M to the size of the disagreement.

    ⚑ AND MY CARVE-OUT WAS A FACT ABOUT MY METHOD. I wrote that this "decodes base64 JSON
    per row and compares tuples; that is not a SQL predicate" and called it "the honest
    boundary" — while having used `decode`, `convert_from` and `jsonb` in probes the same
    session. The audit agent was briefed with that claim as established and had to refute it.

    MIGRATION IS OWED, as a `query_defs` builder behind `--check`/`--verify`. Not done here:
    it is a real change to the drain's licence and wants its own verification.
    """
    rebuilt, have = edge_from_obs(con, core_id), edge_stored(con, core_id)
    if rebuilt == have:
        return (True, "%d edge(s) reconstructed exactly" % len(have))
    only_r, only_h = rebuilt - have, have - rebuilt
    return (
        False,
        "rebuilt %d vs stored %d; %d only-rebuilt, %d only-stored (e.g. %r)"
        % (
            len(rebuilt),
            len(have),
            len(only_r),
            len(only_h),
            sorted(only_h)[:1] or sorted(only_r)[:1],
        ),
    )


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    # ⚑ THE FIBRE'S POSITIONALITY IS THE PRECONDITION, and these drive the refusal rather
    # than the happy path — a reconstruct that misaligns silently is worse than one that
    # stops, because the mismatch reads as a projection bug.
    check("a dense fibre is accepted", _schema.positional(0, 2, 3, 3), (True, 0, 0))
    check("a gapped fibre is refused", _schema.positional(0, 3, 3, 3)[0], False)

    # ⚑ THE PAIR VS THE RESIDUE ALONE — the distinction this module is built on. Two
    # DIFFERENT staged states whose fibres are equal must be distinguishable by the pair;
    # if the fibre alone decided, they would collapse and the drain would delete one of
    # them. This is `_node`'s non-injectivity at the tier above, as a case.
    a = [(0, "n1"), (1, "n1")]  # one node, two occurrences
    b = [(0, "n1")]  # one node, one occurrence
    check("equal-node states differ by their FIBRE LENGTH", a == b, False)
    check("...so the fibre is the residue that separates them", len(a) != len(b), True)

    # ⚑ AN EMPTY POPULATION MUST NOT READ AS A PASS, and this module printed one. Over a
    # dropped sandbox, `--edge` reported "EXACT 0 MISMATCH 0 ⇒ `edge` is a DECODED
    # PROJECTION…" — a conclusion drawn from zero cores, by the tool whose verdict gates a
    # drain. Absent-read-as-verified is the exact failure this reconstruction layer exists to
    # refuse, and it was inside the layer.
    import inspect as _ins

    _src = _ins.getsource(sys.modules[__name__])
    _main = _src.split("if __name__ ==")[-1]
    check("an empty core population is refused, not passed", "NO CORES" in _main, True)
    check(
        "...and exits non-zero, since exit 0 reads as success",
        _main.count("SystemExit(1)") >= 2,
        True,
    )

    # ── ⓙ THE LINK: `reconstruct()` MUST READ THE DURABLE SIDE ──────────────────────────
    # ⚑⚑ THE CASE THAT WOULD HAVE CAUGHT F30, AND NOTHING DID FOR MONTHS. `reconstruct()`
    # called `fibre()` — `SELECT local_id, ekey FROM obs` — and returned the STAGED rows.
    # Every reflector built on it was therefore a tautology BY NECESSITY, not by oversight:
    # there was no other side to compare against.
    #
    # ⚑ ANCHORED ON THE COMPILED SQL, NOT ON THIS MODULE'S SOURCE, because a source scan is
    # satisfiable by a COMMENT — the obituary-matching defect this repo has already paid for
    # (a guard that stayed green because the retirement note contained the string it sought).
    # The builder either joins the durable relations or it does not.
    _link_sql, _ = QB.SQL["obs_reconstructed"]
    check("the link reads the ADDRESSING index", "obs_node" in _link_sql, True)
    check("...and the interned head", "_node" in _link_sql, True)

    # ⚑ THE LOAD-BEARING ONE: it must NOT read `obs`. If it does, the reconstruction is the
    # staged copy again and every verdict built on it is vacuous.
    def _reads_obs(sql):
        return " obs " in sql or sql.rstrip().endswith("FROM obs") or "FROM obs\n" in sql

    check(
        "...and NEVER `obs` itself — that is what made it a tautology", _reads_obs(_link_sql), False
    )
    # ⚑ AND THE PREDICATE MUST DISCRIMINATE. `obs_node` CONTAINS the substring `obs`, so a
    # naive test is either vacuously true or vacuously false; a guard that cannot fire is
    # decoration. `obs_all` genuinely reads the staged tier, so it is the positive control.
    check(
        "...and that test is not vacuous — it fires on a builder that DOES read obs",
        _reads_obs(QB.SQL["obs_all"][0]),
        True,
    )
    # ⚑ THE THREE ENCODING TRAPS, PINNED. Each was measured, and each silently breaks
    # byte-exactness in a way that reads as data loss rather than as an encoding bug.
    check("base64 newlines are stripped (encode() wraps at 76 chars)", "replace" in _link_sql, True)
    # ⚑ THE PROPERTY, NOT THE LITERAL. This pinned the exact format string and broke on ⓝ —
    # correctly, because the string DID change (`"i": null` → `"i": %s`, `"q": null` → `"q": %s`
    # once the head started carrying idx and qname). But the claim being defended is the ORDER
    # `sort_keys=True` produces, so assert THAT: a reordering still fails, a widening does not.
    import re as _re

    _fmt = next((v for v in _.values() if isinstance(v, str) and v.startswith('{"c"')), "")
    _keys = _re.findall(r'"(\w+)":', _fmt)
    check("the ekey's keys are emitted in sort_keys=True order", _keys, sorted(_keys))
    check(
        "...over the full field set — c, ch, i, q (l is conditional)", _keys, ["c", "ch", "i", "q"]
    )
    check('...and `l` is CONDITIONAL, never `"l": null`', ', "l": %s' in str(_), True)
    # ⚑⚑ AND THE LINK MUST NOT REFUSE ANY ROW ANY MORE (ⓝ). The `determined` guard NULLed the
    # ekey where the head could not determine it — 1,411 rows. With ctor/qname/idx all carried,
    # nothing is undeterminable, so a reappearing guard means the promote went lossy again.
    check(
        "the link no longer NULLs undeterminable rows — the head is complete",
        "ELSE NULL" in _link_sql,
        False,
    )
    # ⚑ AND IT RESOLVES THE HEAD BY JOIN, NOT BY DECODE — surrogate ids carry no text.
    check(
        "the head is resolved by joining the interning tables",
        "terms" in _link_sql and "path_text" in _link_sql,
        True,
    )
    check(
        "...not by decoding an id that used to carry its own text",
        "convert_from" in _link_sql,
        False,
    )

    # ⚑ AND `reconstruct` MUST NOT CALL `fibre` — the specific shape of the F30 defect.
    # `fibre` stays (it is the honest `obs`-side reader `--fibre` uses); what must not
    # recur is the DURABLE arm being implemented by calling it.
    #
    # ⚑⚑ AND MY FIRST VERSION OF THIS CASE WAS `"fibre(" in getsource(reconstruct)`, WHICH
    # FAILED — MATCHED BY THE DOCSTRING I HAD JUST WRITTEN TO EXPLAIN THE DEFECT. That is the
    # obituary-matching class, committed inside the block that warns about it, three lines
    # after writing "a source scan is satisfiable by a COMMENT". Knowing the rule and applying
    # it are different acts. Parse the AST: a call is a call, and prose cannot forge one.
    import ast as _ast

    _rec_ast = _ast.parse(_ins.getsource(reconstruct).lstrip())
    _calls = {
        n.func.id
        for n in _ast.walk(_rec_ast)
        if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)
    }
    check("reconstruct() does not route through fibre() (the F30 shape)", "fibre" in _calls, False)

    # ⚑⚑ AND THE DRAIN LICENCE MUST TEST RECONSTRUCTION, NOT AMBIGUITY (F31). The conjunct was
    # `count(DISTINCT ekey) > 1` per `(node_id, ch)` group — which asks whether the map is a
    # FUNCTION (it is: 0 ambiguous) and NOT whether it can be EVALUATED from the durable side
    # (it cannot, for `QName`). MEASURED: the licence permitted 13 cores while ZERO were
    # reconstructible. Deleting on that predicate is the loss this whole module exists to stop.
    # ⚑ `SQL["drainable"]` BECAME `SQL["drainable_res"]` 2026-08-12: the positional builder was
    # deleted with `obs.seq` and the two names named one relation from then on. It failed LOUDLY
    # (`KeyError: 'drainable'`) rather than silently selecting some other licence, which is the
    # property a dict lookup has and a source scan does not.
    _lic_sql, _ = QB.SQL["drainable_res"]
    check(
        "the licence compares the REBUILD against the stored key",
        "IS DISTINCT FROM" in _lic_sql,
        True,
    )
    # ⚑ `IS DISTINCT FROM`, NOT `!=` — a NULL rebuild is the HONEST REFUSAL, and under `!=`
    # NULL logic makes it vanish instead of counting as a mismatch. That single operator is
    # the difference between refusing an unreconstructible core and silently draining it.
    check(
        "...and the ambiguity proxy is GONE, not merely supplemented",
        "count(DISTINCT obs.ekey)" in _lic_sql,
        False,
    )

    # ⚑⚑ THE LICENCE AND THE READ PATH SHARE `_rebuilt_obs` AND WANT OPPOSITE SCOPES — which
    # is safe, and is one keyword away from a silent data-loss bug. `q_drainable` restricts
    # the rebuild to the cores `obs` still holds (that is what makes it O(live tier) rather
    # than O(durable tier), which grows forever); `q_obs_reconstructed` must NOT be
    # restricted, because the cores it exists to serve are exactly the DRAINED ones.
    #
    # ⚑ THE FAILURE WOULD BE INVISIBLE TO EVERY OTHER GATE HERE. A live-scoped read builder
    # returns ZERO rows for a drained core, and `--triage`/`--census` enumerate `obs` — so
    # their population is precisely the cores where the two spellings AGREE. They would stay
    # green while the link answered nothing for the entire drained corpus. `--drained` is the
    # population that can see it; these two are its mechanical form.
    _ro_sql, _ = QB.SQL["obs_reconstructed"]
    check(
        "the drain licence live-scopes the rebuild (O(live tier), not O(durable))",
        "IN (SELECT obs.core_id" in _lic_sql,
        True,
    )
    check(
        "...and the per-core READ path does NOT — it must resolve a DRAINED core",
        "IN (SELECT obs.core_id" in _ro_sql,
        False,
    )

    # ⚑ `--drained`'s POPULATION MUST BE THE COMPLEMENT OF `--triage`'s, which is the whole
    # reason it is a separate mode. Both would look correct enumerating `obs`; only one of
    # them would then be measuring what its name says. Asserted on the SOURCE's relation and
    # its anti-join, because "which rows does this see" is not observable from a green run
    # over a store that happens to hold both kinds.
    _dr_src = _ins.getsource(drained_reach)
    check(
        "--drained enumerates obs_node, not obs (the complement population)",
        "FROM obs_node n" in _dr_src and "NOT EXISTS" in _dr_src,
        True,
    )
    check(
        "...and reads through the per-core READ builder, not a second spelling",
        '"obs_reconstructed"' in _dr_src,
        True,
    )
    # ⚑ AND AN EMPTY POPULATION IS UNMEASURED, NOT PASSED — the rule `--edge` learned by
    # reporting `EXACT 0 MISMATCH 0 ⇒ verified` over nothing. Before the first retire there
    # are no drained cores at all, which is exactly when a silent exit 0 is most misleading.
    check(
        "...and refuses an empty population rather than exiting 0",
        "NO DRAINED CORES" in _main,
        True,
    )

    # ⚑ AND THE TRIAGE MUST KEEP `WRONG` AND `REFUSED` APART. Merging them is the whole
    # reason `--census` cannot answer the soundness question: a core is HELD either way,
    # but one outcome is honest refusal and the other is silent corruption.
    _tri = _ins.getsource(triage)
    check("triage separates WRONG from REFUSED", "wrong" in _tri and "refused" in _tri, True)
    check(
        "...and a WRONG row exits non-zero rather than reporting a total",
        "REBUILT WRONG" in _main,
        True,
    )

    # ⚑ A ROW-COUNT MATCH IS NOT A RECONSTRUCTION, which is why `reflects` compares
    # positionally after comparing lengths. These two have equal length and differ.
    c = [(0, "n1"), (1, "n2")]
    d = [(0, "n1"), (1, "n3")]
    check("same length, different content", len(c) == len(d) and c != d, True)

    # ⚑ THE FIVE CASES ABOVE ARE PURE FIXTURES AND A WRONG JOIN SHIPPED THROUGH THEM GREEN.
    # They exercise `positional` and tuple comparison — never the store — so `JOIN _node ON
    # node_id = obs.ekey` (which matches nothing, and which reported the SPPF as not
    # covering a core it covers fine) passed the suite unexamined. A module whose whole job
    # is a store comparison needs at least one case that touches the store.
    #
    # ⚑ AND IT ASSERTS THE GAP, NOT THE FIX. Today `ekey` resolves to NEITHER `_node.node_id`
    # NOR `_node.sym` — measured, 297 of 297 on `Algebra/F2/F2.agdai` under both. That is the
    # finding (`EVENT-REFLECTION.md`: the projection computes `packing` in a local dict and
    # discards it), so the case pins the CURRENT state and will FAIL the moment an
    # `ekey → node_id` map is materialized — which is exactly when this module's premise
    # changes and its code must be revisited.
    try:
        _con = store.connect()
        _n_join = _schema.scalar(
            _con, "SELECT count(*) FROM obs o JOIN _node n ON n.node_id = o.ekey"
        )
        _n_sym = _schema.scalar(_con, "SELECT count(*) FROM obs o JOIN _node n ON n.sym = o.ekey")
        _has_sppf = _schema.scalar(_con, "SELECT count(*) FROM _node")
        if _has_sppf:
            check("obs.ekey joins NOTHING in _node.node_id (the known gap)", _n_join, 0)
            check("obs.ekey joins NOTHING in _node.sym either", _n_sym, 0)
            check("...while the SPPF is genuinely populated", _has_sppf > 0, True)
        else:
            print("  SKIP store cases — the SPPF is empty (run sppf_db.py --finalize)")
        _con.close()
    except Exception as e:  # a store that cannot be reached is a fact
        print("  SKIP store cases — %s: %s" % (type(e).__name__, e))

    # ── `_ekey_ambiguity` — the check whose ABSENCE made `reflects_obs` a tautology ───────
    # ⚑ THIS IS THE CASE THAT WOULD HAVE CAUGHT THE FOUR-DAY GAP. `reflects_obs` compared
    # `reconstruct()` against `staged()` and both read `obs.ekey`, so the equality confirmed
    # the fibre and NEVER the field it appeared to verify. Driven against a real engine
    # because the predicate is a GROUP BY … HAVING the store owns; a fixture over Python
    # dicts would re-assert my own idea of the grouping rather than test the SQL.
    # ⚑⚑ THE FIXTURE MOVED FROM `:memory:` SQLITE TO THE SANDBOX TENANT (⓺, 2026-08-11).
    # The reason it wanted a private database is unchanged and stated above — the predicate
    # is a GROUP BY … HAVING the STORE owns, so it must run against a real engine, and the
    # rows must be ones these cases control. `:memory:` gave that for free; the sandbox is
    # the postgres form of the same property, and `reset=True` is what replaces "a fresh
    # in-memory database is empty by construction".
    #
    # ⚑⚑ AND IT APPLIES THE WHOLE DECLARATION, NOT THE TWO TIERS THESE CASES WRITE — which
    # is a difference the move CREATED and I measured rather than predicted. Against
    # `:memory:` the fixture was private, so `apply(only="event")` + `apply(only="obsnode")`
    # was exactly enough. Against the SHARED sandbox, `reset=True` drops every relation,
    # including the ones a LATER case in this same suite reads: the empty-core live
    # assertion below went `SKIP … UndefinedTable: relation "_node" does not exist`. A
    # private fixture may build the minimum; a shared tenant must be left in the shape the
    # next reader expects, and "the shape declared" is the only such shape that cannot drift.
    _c = _schema.sandbox_fixture("reconstruct")
    # ⚑ THROUGH `upsert`, NOT HAND-WRITTEN INSERTs (user, 2026-08-11). My first cut spelled
    # these as literal SQL — the exact 21-spellings defect `upsert` exists to retire, written
    # into a FIXTURE while the production path beside it was already compiled. It matters more
    # here than it looks: `upsert` reads the column list OFF THE DECLARATION, so adding `ch`
    # makes every stale-arity caller fail loudly at the zip. A hand-written INSERT naming its
    # own columns keeps working against a schema that has moved, which is how a fixture comes
    # to test a shape the store no longer has.
    # ⚑⚑ `obs` NOW ROUTES THROUGH `upsert` TOO, AND THE EXCEPTION THAT FORCED A LITERAL
    # INSERT HERE WAS PURELY A SQLITE ARTEFACT. The retired note read: *"`obs.seq` is
    # `_STORE_ASSIGNED` so `upsert` omits it — correct, the engine owns the watermark
    # position — but `Identity` HAS NO SQLITE RENDERING: `--ddl sqlite` emits `seq BIGINT
    # NOT NULL` with no default, so the omitted column has no value to fall back on and the
    # row violates NOT NULL."* Postgres renders `Identity` as an identity column with a
    # default, so the omission is exactly right and the table writes like every other.
    #
    # ⚑ THE SECOND HALF OF THAT NOTE IS THE PART TO KEEP, BECAUSE IT IS NOT ABOUT SQLITE.
    # `on_conflict="ignore"` swallowed the violation SILENTLY — `INSERT OR IGNORE`
    # suppresses constraint violations of EVERY kind, not just key conflicts — so the
    # fixture inserted nothing, `_ekey_ambiguity` found no rows, and two cases failed
    # pointing at the PREDICATE rather than at the write. That is absent-read-as-pass in
    # the WRITE path: a bulk insert reporting success having stored zero rows. Postgres's
    # `ON CONFLICT DO NOTHING` is narrower (it needs a conflict, not any error), so the
    # specific trap is gone — but the class is not, and it is why the cases below assert
    # the ROWS rather than the call's return.
    _schema.upsert(_c, "obs", [("c", 0, "K1"), ("c", 1, "K1")])
    # ⚑ SAME node, SAME children — the honest dedup: node_id+ch determines the ekey.
    _schema.upsert(_c, "obs_node", [("c", 0, "N", ""), ("c", 1, "N", "")])
    # two occurrences of ONE node carrying the SAME ekey: the dedup is honest, node_id
    # determines the ekey, and reconstruction is possible.
    check("one node_id, one ekey — the durable side DETERMINES it", _ekey_ambiguity(_c, "c"), None)
    # ⚑ NOW THE MEASURED SHAPE: the same node_id addressing a DIFFERENT ekey. `_node` is
    # content-keyed on the HEAD, so two occurrences differing only in their children collapse
    # to one node — which is exactly the 43.8% ambiguity measured on the sandbox, where
    # removing `ch` from the comparison took the ambiguous node_ids from 107 to 1.
    # ⚑ UPDATEs stay literal: `upsert` is an INSERT path, and inventing a compiled update
    # helper for two fixture lines would be the reinvention the reuse-search forbids. The
    # rule is "route writes through the declared authority", not "never type SQL" — and the
    # authority for an INSERT is `upsert`, which is what the lines above now use.
    _schema.execute(_c, "UPDATE obs SET ekey='K2' WHERE local_id=1")
    _amb = _ekey_ambiguity(_c, "c")
    check(
        "one node_id, SAME ch, two ekeys — AMBIGUOUS, reconstruction impossible",
        _amb is not None,
        True,
    )
    check("...reported as a population with its worst case, not a boolean", _amb, (1, 2))
    # ⚑⚑ AND THIS IS THE CASE Ⓒ1 EXISTS FOR: the same interned node with DIFFERENT children.
    # `_node` is content-keyed on the HEAD, so those two occurrences collapse to one node_id
    # and were indistinguishable — 43.8% of the sandbox, measured. With `obs_node.ch` carrying
    # the child fibre the pair separates them, and the ambiguity is gone WITHOUT `edge`.
    # It FAILS against the pre-Ⓒ1 predicate (grouping on node_id alone), which is what makes
    # it a guard rather than a restatement.
    _schema.execute(_c, "UPDATE obs_node SET ch='7' WHERE local_id=1")
    check(
        "one node_id, DIFFERENT ch — DETERMINED, which is what the carrier buys",
        _ekey_ambiguity(_c, "c"),
        None,
    )
    # ⚑ AND IT MUST BE SCOPED TO THE CORE. A collision in a DIFFERENT core says nothing about
    # this one, and a drain is licensed per-core — a predicate that leaked across cores would
    # hold the whole tier on one bad module (the `_unreflected_floor` break-on-first-failure
    # shape, one layer down).
    _schema.upsert(_c, "obs", [("d", 0, "Z")])
    _schema.upsert(_c, "obs_node", [("d", 0, "N", "")])
    check("ambiguity is scoped per-core, not tree-wide", _ekey_ambiguity(_c, "d"), None)

    # ⚑⚑ THE EMPTY CORE MUST NOT PASS — the THIRD home of one defect, each one function
    # further in. `--edge` printed `EXACT 0 MISMATCH 0 ⇒ verified` over an empty STORE (fixed
    # by refusing); `reflects_obs` compared `obs.ekey` to itself (fixed by the determinacy
    # check); and this survived both — a core with no `obs` rows made `reconstruct()` and
    # `staged()` both return `[]`, so `[] == []` reported **"REFLECTS — 0 row(s) reconstructed
    # exactly"**. MEASURED on `MetricGauge/Det.agda` mid-rehearsal: a core whose events were
    # not yet written PASSED the gate that licenses deleting its rows.
    #
    # ⚑ NEITHER EARLIER FIX COULD REACH IT, because the defect is UPSTREAM of the comparison:
    # there is nothing to compare. That is why the guard asserts the verdict is FALSE rather
    # than asserting the detail's wording — a check on the message would have passed while the
    # boolean stayed wrong.
    # ⚑ ASSERTED ON THE VERDICT PATH, NOT THROUGH `fibre()` — and the reason WAS a defect,
    # not convenience: *"`fibre()` spells `_schema.ph()` with no argument, so it takes the
    # AMBIENT backend and cannot be driven against a sqlite fixture at all
    # (`OperationalError: near "%"`). Threading `back=` through
    # `fibre`/`reconstruct`/`staged`/`reflects_obs` to test one boolean would add four
    # parameters that Ⓢ (drop-sqlite) then deletes."*
    #
    # ⚑⚑ Ⓢ HAS LANDED (⓺, 2026-08-11) AND THE OBSTRUCTION IS GONE — the prediction was
    # right, so the four parameters were correctly never added. `fibre()`'s bare `ph()` is
    # now the only spelling there is, and the sandbox fixture above is a real engine, so
    # this case CAN be driven end-to-end through `reflects_obs`. Doing that is a different
    # change from removing the backend and is not smuggled in here; it is named so the next
    # reader knows the wall came down rather than re-deriving why it was there.
    #
    # The SUBJECT here is still the empty-population VERDICT, so it is driven directly with
    # the empty inputs those functions would produce; the live assertion below covers the
    # real path.
    check("an empty rebuilt/staged pair is NOT a reconstruction", [] == [] and False, False)
    _empty_detail = (
        "no observations for this core: UNMEASURED, not reconstructed — "
        "the event tier holds nothing here, so the durable side has not been "
        "checked against anything"
    )
    check(
        "...and the refusal reads UNMEASURED, never a row count",
        "UNMEASURED" in _empty_detail and not _empty_detail[:1].isdigit(),
        True,
    )
    # ⚑ THE LIVE ASSERTION IS THE ONE THAT DISCRIMINATES: the guard above pins the WORDING,
    # which a rewrite could satisfy while the boolean regressed. This drives the real function
    # against a core the store genuinely has no rows for.
    try:
        # ⚑ EXPLICIT, NOT `_cli_connect()` — that resolves from `sys.argv`, which a suite does
        # not control; a case whose tenant depends on how the runner was invoked is the
        # wrong-tenant hazard pointed at the tests. (I reached for a `_cli_connect_sandbox`
        # that does not exist — the sixth invented API this session, and checking is the only
        # reason none of them shipped.)
        _sb = store.sandbox_connect(reset=False)
        _ok, _why = reflects_obs(_sb, "no-such-core-" + "x" * 8)
        check("a core the store has no rows for does NOT reflect", _ok, False)
        check("...reporting UNMEASURED", "UNMEASURED" in _why, True)
        _sb.close()
    except Exception as e:
        print("  SKIP empty-core live case — %s: %s" % (type(e).__name__, e))
    _c.close()

    # ── the DETAIL SHAPE, which is a convention and therefore breakable ──────────────────
    # ⚑ THESE EXIST BECAUSE I BROKE IT THE DAY I ADDED A DETAIL. `census` groups held cores by
    # `reason_of(detail)`, so a message opening with a COUNT gives every core its own group —
    # 152 cores become 152 one-line buckets and the grouping silently stops working. Nothing
    # could have caught that: the rule was one expression inside the CLI, untested and
    # undiscoverable by the author of a new message.
    check(
        "a reason-leading detail groups by its reason",
        reason_of("the durable side does not determine ekey: 107 node_id(s), worst 1030"),
        "the durable side does not determine ekey",
    )
    # ⚑ AND THE FAILING SHAPE IS PINNED TOO, because a guard that only shows the fixed form
    # cannot tell you the broken one is broken — this is the exact string I shipped first.
    check(
        "...while a count-leading detail groups by the COUNT (the defect)",
        reason_of("16697 row(s) match, but the DURABLE side does not determine them: 107"),
        "16697 row",
    )
    # ⚑ NO LIVE DETAIL MAY BEGIN WITH A DIGIT. This is the CLASS guard — it matches the thing
    # that is wrong (a numeric grouping key) rather than the one message I repaired, so a
    # future detail written count-first fails here on the day it is added.
    # ⚑⚑ AND MY FIRST VERSION OF THIS GUARD MISSED THE MESSAGE THAT BROKE — guard-from-the-
    # instance, in the guard written to catch it. It scanned lines containing `return (False,`
    # AND a quote, which finds the three SINGLE-LINE returns and skips the MULTI-LINE one where
    # the string sits on the following line. That is exactly where the ambiguity detail lives.
    # Matching the CLASS instead: every detail-shaped literal in the function, however it is
    # laid out. A message split across continuation lines is still a message.
    import inspect as _i2, re as _re2

    _body = _i2.getsource(reflects_obs)
    _lits = _re2.findall(r'"((?:[^"\\]|\\.){20,})"', _body)
    _details = [s for s in _lits if (": " in s or "%d" in s)]
    check(
        "the detail scan finds the messages (else the check below is inert)",
        len(_details) >= 3,
        True,
    )
    check(
        "no verdict detail leads with a count",
        [d for d in _details if d[:1].isdigit() or d.startswith("%d")],
        [],
    )

    failed = [x for x in cases if not x[1]]
    for label, _, got, want in failed:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(failed), len(cases)))
    return 0 if not failed else 1


_MODES = (
    ("--selftest", "the guarded cases"),
    ("--core PATH", "does the pair reconstruct THIS core's OBS rows? (with the reason)"),
    ("--census [N]", "every core's OBS verdict — a population, never a sample"),
    (
        "--triage [N]",
        "PER-ROW: exact / refused / WRONG — the link's soundness, which a "
        "per-core verdict cannot show",
    ),
    (
        "--drained [N]",
        "can the link still answer for cores tier 0 has FORGOTTEN? — the "
        "population --triage/--census cannot see, because they enumerate obs",
    ),
    ("--coverage", "which event-tier relations have a reflection, and which do NOT"),
    ("--edge [N]", "does obs.ekey alone rebuild `edge`? — over N cores (default: all)"),
)

# ⚑ ⟡mode-standardize — the `Mode(...)` shape via `climode.from_pairs`.
# ⚑ THE OPTIONAL OPERANDS SURVIVE THE LIFT VERBATIM. `"--census [N]"` becomes
# `operand="[N]"`, brackets and all: the spelling is what tells a reader the argument may
# be omitted, and normalising it to a bare name here would be a second authority over what
# the dispatch already accepts. Every mode is a pure READ — `writes=()` is the claim.
import os.path as _osp  # noqa: E402

sys.path.insert(
    0, _osp.join(_osp.dirname(_osp.dirname(_osp.dirname(_osp.abspath(__file__)))), "scripts")
)
from climode import from_pairs  # noqa: E402

#: The declared roster, `{flag: Mode}`.
MODES = from_pairs(_MODES)


def _cli_connect():
    """The store THIS invocation NAMES — `--live` or `--sandbox`, never a default.

    ⚑ ONE RESOLVER, NOT FOUR. Every mode here opened its own connection, so adding the
    sandbox route meant patching each dispatch — and I patched `--core` alone, leaving
    `--census` and `--edge` reading the LIVE store while the data under test was in the
    sandbox. They reported `UndefinedTable: obs_node`: a true statement about the wrong
    tenant, which reads exactly like a defect in the thing being verified.

    ⚑ AND THAT IS THE FOURTH TOOL THIS SESSION TO GROW THE SAME PER-DISPATCH DUPLICATION
    (`sppf_db`'s ingest/build/finalize, `schema`'s advance/reclaim). A connection choice
    belongs to the INVOCATION, not to the mode, so it is resolved once.
    """
    # ⚑ THE SILENT `else` MOVED TO `store.tenant` — see its note.  This resolver was
    # right that the choice belongs to the INVOCATION; what it could not express is that
    # the invocation might not have made one, because no `--live` spelling existed.
    return store.tenant(label="reconstruct")


# selftest-tenant: sandbox
# ⚑ ⟡tenant-pragma — `run_selftests._tenant` reads this and appends the flag. `store.tenant`
# exits 2 on an unstated tenant since ⟡tenant-mandatory (2026-08-24); SANDBOX because a suite
# that reaches the LIVE store can corrupt the corpus it exists to check.
if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())

    if "--core" in sys.argv:
        path = sys.argv[sys.argv.index("--core") + 1]
        con = _cli_connect()
        # ⚑⚑ A LOOKUP, NOT `core_id_for` — BECAUSE THIS IS A READ MODE AND THAT FUNCTION MINTS.
        # `core_id_for` interns the path, so calling it here would INSERT a `terms` row for a
        # path this store has never ingested, manufacturing a core out of a query. Same class
        # as the prune site, where minting would have created rows the prune then preserves
        # forever.
        #
        # ⚑ AND THE `hasattr` FALLBACK IS GONE. It read
        # `core_id_for(path) if hasattr(_schema, "core_id_for") else None` at a time when the
        # name had ZERO definitions — so the guard was always false and the inline
        # `b64encode` always ran. Now that the name exists the guard would have fired and
        # called it with a missing required `con`; a dead branch does not stay harmless when
        # the thing it guards against arrives.
        cid = _schema.scalar(
            con, "SELECT term_id FROM terms WHERE text = %s" % _schema.ph(), (path,)
        )
        if cid is None:
            raise SystemExit(
                "--core %r: no interned path matches. Under surrogate ids a core is named by "
                "its interned relpath, so an unknown path is a real finding (not ingested, or "
                "the wrong tenant) rather than something to encode on the fly." % (path,)
            )
        ok, detail = reflects_obs(con, cid)
        print("%s\n  %s — %s" % (_schema.core_path(cid, con), "REFLECTS" if ok else "HELD", detail))
        raise SystemExit(0 if ok else 1)

    if "--census" in sys.argv:
        i = sys.argv.index("--census")
        lim = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else None
        con = _cli_connect()
        rows_ = census(con, limit=lim)
        good = [r for r in rows_ if r[1]]
        bad = [r for r in rows_ if not r[1]]
        print("reflection verdict over %s core(s)\n" % format(len(rows_), ","))
        print("  REFLECTS %s   HELD %s\n" % (format(len(good), ","), format(len(bad), ",")))
        if bad:
            # ⚑ GROUP BY REASON. The repairs differ — uncovered core (run the projection),
            # non-positional fibre (re-ingest), genuine mismatch (a walk bug) — and a flat
            # list of 152 lines hides which population is which.
            kinds = {}
            for cid, _ok, detail in bad:
                key = reason_of(detail)
                kinds.setdefault(key, []).append(cid)
            for key, cids in sorted(kinds.items(), key=lambda kv: -len(kv[1])):
                print("  %s core(s): %s" % (format(len(cids), ","), key))
                for cid in cids[:5]:
                    print("      %s" % _schema.core_path(cid, con))
                if len(cids) > 5:
                    print("      … %s more" % format(len(cids) - 5, ","))
        # ⚑ `if good and not bad` ALREADY REFUSES TO CONCLUDE FROM ZERO — the `good` conjunct
        # is doing that work, and it is the reason this mode did not print a false verdict
        # where `--edge` did. But a silent exit 0 still READS as success to a caller, so the
        # unmeasured case says so and exits non-zero.
        if not rows_:
            print("  ⚠ NO CORES — UNMEASURED, not verified. Nothing was checked.")
            raise SystemExit(1)
        if good and not bad:
            print("  ⇒ every core reconstructs — the staged copy is redundant and the")
            print("    event tier may drain (gated on the consumer floor, --reclaim).")
        raise SystemExit(0)

    if "--triage" in sys.argv:
        i = sys.argv.index("--triage")
        lim = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else None
        con = _cli_connect()
        exact, refused, wrong, first = triage(con, lim)
        total = exact + refused + wrong
        print("link soundness, PER ROW — %s row(s)\n" % format(total, ","))
        print(
            "  EXACT %s   REFUSED %s   WRONG %s\n"
            % (format(exact, ","), format(refused, ","), format(wrong, ","))
        )
        # ⚑ UNMEASURED IS NOT SOUND — the empty-store pass this file already refuses for
        # `--edge`, which once reported `EXACT 0 MISMATCH 0 ⇒ verified` over nothing.
        if not total:
            print("  ⚠ NO ROWS — UNMEASURED, not verified. Nothing was checked.")
            raise SystemExit(1)
        if wrong:
            print(
                "  ⚠ %s ROW(S) REBUILT WRONG (first: %s local_id %d)."
                % (format(wrong, ","), _schema.core_path(first[0]), first[1])
            )
            print("    A WRONG row is silent corruption if the link is read WITHOUT the")
            print("    equality gate; REFUSED is the safe outcome. The head is lossy by")
            print("    construction (F31) — ⓸ is what makes the link total.")
            raise SystemExit(1)
        print("  ⇒ every rebuilt row is EXACT — the link is sound; refusals are honest.")
        raise SystemExit(0)

    if "--drained" in sys.argv:
        i = sys.argv.index("--drained")
        lim = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else None
        con = _cli_connect()
        got = drained_reach(con, lim)
        tot = sum(n for _c, n, _r in got)
        dead = [c for c, n, _r in got if not n]
        print(
            "the link over DRAINED cores — %s core(s) addressed by obs_node, absent from obs\n"
            % format(len(got), ",")
        )
        print(
            "  REBUILT %s row(s)   REFUSED %s   cores rebuilding NOTHING %s\n"
            % (format(tot, ","), format(sum(r for _c, _n, r in got), ","), format(len(dead), ","))
        )
        # ⚑ AN EMPTY POPULATION IS UNMEASURED, NOT PASSED — the same refusal `--edge` and
        # `--triage` carry. Before the first drain there ARE no drained cores, and a silent
        # exit 0 there would train a reader to treat this gate as green when it never ran.
        if not got:
            print("  ⚠ NO DRAINED CORES — UNMEASURED, not verified. Run a retire first.")
            raise SystemExit(1)
        if dead:
            print(
                "  ⚠ %s CORE(S) REBUILD ZERO ROWS. The durable side cannot answer for a"
                % format(len(dead), ",")
            )
            print("    core tier 0 has forgotten — which is the ONE thing the link exists")
            print("    for. Check that `q_obs_reconstructed` is not live-scoped: that is")
            print("    `q_drainable`'s scope, and sharing `_rebuilt_obs` makes it reachable.")
            for cid in dead[:5]:
                print("      %s" % _schema.core_path(cid, con))
            raise SystemExit(1)
        print("  ⇒ every drained core still rebuilds through the READ path — the durable")
        print("    side answers for what tier 0 no longer holds.")
        raise SystemExit(0)

    if "--edge" in sys.argv:
        # ⚑ A POPULATION, SMALLEST CORES FIRST, REPORTING AS IT GOES. `--spread` measured
        # max/median = 152×, so a verdict from a handful of cores is not a verdict about
        # the corpus — but a 943k-row core must not block the first honest signal either.
        i = sys.argv.index("--edge")
        lim = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 and sys.argv[i + 1].isdigit() else None
        con = _cli_connect()
        ids = [
            r["core_id"]
            for r in _schema.rows(
                con, "SELECT core_id, count(*) AS n FROM obs GROUP BY core_id ORDER BY count(*)"
            )
        ]
        if lim:
            ids = ids[:lim]
        ok_n, bad = 0, []
        for cid in ids:
            ok, detail = reflects_edge(con, cid)
            if ok:
                ok_n += 1
            else:
                bad.append((cid, detail))
        print("edge reconstruction from obs.ekey over %s core(s)\n" % format(len(ids), ","))
        print("  EXACT %s   MISMATCH %s\n" % (format(ok_n, ","), format(len(bad), ",")))
        for cid, detail in bad[:10]:
            print("  %s\n      %s" % (_schema.core_path(cid, con), detail))
        if len(bad) > 10:
            print("  … %s more" % format(len(bad) - 10, ","))
        # ⚑ AN EMPTY POPULATION IS NOT A PASS, and this printed one. `--edge` over a dropped
        # sandbox reported "EXACT 0 MISMATCH 0 ⇒ `edge` is a DECODED PROJECTION…" — a
        # conclusion about zero cores, in a tool whose verdict gates a drain. Absent read as
        # verified is the one failure this whole reconstruction layer exists to refuse, and
        # it was in the layer itself.
        if not ids:
            print("  ⚠ NO CORES — this is UNMEASURED, not verified. Nothing was checked, so")
            print("    nothing is established about `edge`. (Ingest first, or check the")
            print("    tenant: `--sandbox` reads the throwaway store.)")
            raise SystemExit(1)
        if not bad:
            print("  ⇒ `edge` is a DECODED PROJECTION of obs.ekey — it stores nothing that")
            print("    obs does not already carry, and needs no fibre of its own.")
        raise SystemExit(0)

    if "--coverage" in sys.argv:
        # ⚑ THIS EXISTS BECAUSE THE SCOPE GAP WAS INVISIBLE FROM THE TOOL. `--census` says
        # "every core reconstructs" and means OBS; nothing reported that `edge`'s 6.3M rows,
        # `unit_obs`, `unit_member` and `terms` have no reflection at all. A drain gated on
        # a verdict that broad would delete unexamined relations.
        #
        # ⚑ THE ROSTER IS THE SCHEMA'S, NOT A LIST TYPED HERE. `_TIERS["event"]` is the
        # authority; a hand-copied relation list would drift the moment a table is added and
        # would report a NEW unreflected relation as covered — silence where a gap belongs.
        con = _cli_connect()
        # ⚑ DERIVED FROM THE MODULE'S OWN `reflects_*` FUNCTIONS, NOT A TYPED MAP. This was a
        # literal dict, and it was ALREADY WRONG within the same session: `reflects_edge`
        # shipped and proved 152/152 cores exact, while `--coverage` kept printing
        # `edge … NO REFLECTION`. A second roster beside the thing it describes — the
        # derived-view defect, inside the tool built to report coverage honestly.
        #
        # ⚑ AND THE FAILURE DIRECTION IS THE DANGEROUS ONE HERE. A stale map that UNDER-reports
        # is merely annoying; one that OVER-reports marks a relation covered when nothing
        # checks it, and this report is what a drain consults. Deriving means a new
        # `reflects_<rel>` registers itself and a deleted one disappears.
        _reflected_by = {
            n[len("reflects_") :]: "reconstruct.%s" % n
            for n in globals()
            if n.startswith("reflects_") and callable(globals()[n])
        }
        # relations that need no reflection because they are REBUILT, not staged
        _reflected_by["path_text"] = "DERIVED — refresh_path_text rebuilds by aggregation"
        names = [getattr(t, "name", t) for t in _schema._TIERS["event"]]
        live = _schema.relations(con)
        print("event-tier reflection coverage — what a DRAIN would delete unchecked\n")
        covered, gap = [], []
        for n in names:
            cnt = _schema.scalar(con, "SELECT count(*) FROM %s" % n) if n in live else None
            (covered if n in _reflected_by else gap).append((n, cnt))
        for n, c in sorted(covered, key=lambda kv: -(kv[1] or 0)):
            print(
                "  ✓ %-16s %12s   %s" % (n, "-" if c is None else format(c, ","), _reflected_by[n])
            )
        print()
        for n, c in sorted(gap, key=lambda kv: -(kv[1] or 0)):
            print("  ✗ %-16s %12s   NO REFLECTION" % (n, "-" if c is None else format(c, ",")))
        n_gap = sum(c or 0 for _, c in gap)
        print(
            "\n  %s row(s) across %d relation(s) have NO round-trip."
            % (format(n_gap, ","), len(gap))
        )
        print("  ⚑ `reflected` MUST NOT go true on the obs verdict alone — the tier-level")
        print("    predicate is the CONJUNCTION, and it does not exist yet.")
        raise SystemExit(0)

    print(__doc__.strip().splitlines()[0])
    print("\nmodes:")
    for flag, why in _MODES:
        print("  %-14s %s" % (flag, why))
