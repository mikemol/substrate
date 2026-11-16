#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""THE information-lifecycle model — the relational image of `Substrate.Realizability.Charter`.

⚑ VOCABULARY *AND* STRUCTURE, BECAUSE THE TARGET IS CODESYNTH (user, 2026-08-06: *"Some day
I'll get this to codesynth from agda. But that'll be easier if things are already shaped
right."*). Consistently NAMING things after the Agda would be cheap and would leave a
generator inventing the translation. So this module is a faithful image: same constructors,
same cumulativity, same peel, same located rejection — a generator emitting it from
`Charter.agda` should have nothing to decide.

THE AGDA IT MIRRORS (`agda/Substrate/Realizability/Charter.agda:97-128`):

    data Chain : Set where
      ε   : Chain
      _▷_ : Chain → (D → Bool) → Chain

    ⟦ ε ⟧?     d = true
    ⟦ c ▷ f ⟧? d = ⟦ c ⟧? d ∧ f d

    data Wit : Chain → D → Set where          -- the CUMULATIVE realiser
      wε  : Wit ε d
      w▷  : Wit c d → f d ≡ true → Wit (c ▷ f) d

    drop : Wit (c ▷ f) d → Wit c d            -- Lemma 4.1: ordering is FORCED

    data Rejected : Chain → D → Set where      -- rejection LOCATED at a link
      here  : f d ≡ false  → Rejected (c ▷ f) d
      there : Rejected c d → Rejected (c ▷ f) d

⚑ THE THREE PROPERTIES THAT MAKE THIS THE RIGHT MODEL, and each fixes something the
watermark alone could not express:

  1. **CUMULATIVE.** `Wit (c ▷ f)` CONTAINS `Wit c`. A datum that reached stage N provably
     satisfies every earlier stage, so "what holds this row" is answerable by peeling
     rather than by re-deriving each constraint. The scalar floor could only say "below N".

  2. **LOCATED REJECTION.** `Rejected` names WHICH link failed (`here`) versus "something
     earlier did" (`there`). A boolean `reclaimable?` collapses exactly that distinction —
     which is why the 38-minute anti-join could report a count and never a reason.

  3. **STAGES ARE PREFIXES OF ONE CHAIN**, not four independent predicates. `chain-con ⊂
     chain-rea ⊂ chain-obs ⊂ charter`. So adding a stage is `_▷_`, and the entailments
     between stages are all the SAME function (`drop`) rather than N² hand-written
     implications.

⚑ AND THE LIFECYCLE'S OWN STAGES ARE NOT THE CHARTER'S FOUR. The charter audits a
DISTINCTION (constructible/reachable/observable/coverable). This audits a DATUM's passage
through the ingest, so the links differ — but the ALGEBRA is identical, which is the whole
point of mirroring the structure rather than copying the names.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


# ── Chain: ε and _▷_ ────────────────────────────────────────────────────────────────
class Chain(tuple):
    """A cons-list of named predicates. `Chain()` is ε; `.then(name, f)` is `_▷_`.

    ⚑ A TUPLE SUBCLASS SO IT IS IMMUTABLE AND ITS PREFIXES ARE SHARED. `chain[:n]` IS the
    n-th prefix — which is what makes the named stages prefixes of ONE chain rather than
    four separate declarations, exactly as `chain-con ⊂ chain-rea ⊂ chain-obs ⊂ charter`.
    """

    __slots__ = ()

    def then(self, name, predicate, because=""):
        """`c ▷ f` — extend the chain by one named link."""
        return Chain(self + ((name, predicate, because),))

    def names(self):
        return [n for n, _, _ in self]

    def holds(self, d):
        """`⟦ c ⟧? d` — the cumulative test: every link must pass."""
        return all(f(d) for _, f, _ in self)

    def witness(self, d):
        """`Wit c d` — the cumulative realiser, or None.

        ⚑ RETURNS THE WHOLE PREFIX IT SATISFIES, NOT A BOOLEAN. That is `Wit`'s
        cumulativity made concrete: the witness for stage N carries the witnesses for
        every stage below, so `drop` is a slice rather than a recomputation.
        """
        for _n, f, _w in self:
            if not f(d):
                return None
        return self

    def rejected(self, d):
        """`Rejected c d` — WHICH link failed, as (index, name, why), or None if accepted.

        ⚑ THE FIRST FAILING LINK IS THE ANSWER, matching `reject`'s recursion: `here` when
        this link fails, `there` when an earlier one did. Reporting "some constraint holds
        this" without naming it is the collapse this exists to prevent.
        """
        for i, (name, f, because) in enumerate(self):
            if not f(d):
                return (i, name, because)
        return None

    def reached(self, d):
        """The longest PREFIX this datum satisfies — its stage, as a chain.

        `len(reached(d))` is the stage index; `reached(d) == self` means fully accepted.
        """
        for i, (_n, f, _w) in enumerate(self):
            if not f(d):
                return Chain(self[:i])
        return self


def drop(wit):
    """`drop : Wit (c ▷ f) d → Wit c d` — Lemma 4.1, one peel.

    ⚑ EVERY STAGE ENTAILMENT IS THIS ONE FUNCTION. The Agda's `forces-cov⇒obs`,
    `forces-obs⇒rea`, `forces-rea⇒con` are all literally `drop`, and `forces-cov⇒con` is
    `drop ∘ drop ∘ drop`. Mirroring that means a new stage adds no implications.
    """
    if wit is None or len(wit) == 0:
        raise ValueError("drop: cannot peel ε — there is no earlier stage")
    return Chain(wit[:-1])


# ── the ingest lifecycle, as a chain ────────────────────────────────────────────────
#
# ⚑ EACH LINK IS A CONSTRAINT THAT HOLDS A DATUM AT A STAGE, and the ORDER is the
# entailment. A datum that is `reflected` is necessarily `observed`, which is necessarily
# `sourced` — by cumulativity, not by three checks. (The sentence named `consumed` and
# `settled` when it was written; both links are deleted, and it re-derives rather than being
# rewritten, which is the property "stages are prefixes of ONE chain" buys.)
#
# ⚑ `sourced` IS THE STAGE THE STORE DID NOT MODEL, and its absence is why the only
# expressible constraint for `scope_fix` was "keep everything forever". `write_events`
# derives source-liveness every run (glob the disk, diff `core_fp.mtime`) and DISCARDS it
# into local variables, so nothing could ask "is this row's source still real?".


def _sourced(d):
    """The datum's core still exists at the revision that produced it."""
    return bool(d.get("source_live"))


def _observed(d):
    """It has an ADDRESS in the append-only log — `(core_id, local_id)`.

    ⚑⚑ RE-ANCHORED 2026-08-12 FROM `d.get("seq")`, AND THE LINK IS KEPT WHILE THE COLUMN GOES.
    The predicate was *"it has a position in the append-only log (`obs.seq` assigned)"*. `seq`
    was deleted with the queue tier, but `observed` is not the queue's stage — it is the
    boundary INGEST spans, and `sppf_db.converge` keys its step roster by boundary index. The
    `consumed` deletion already moved retire 4 → 3; dropping this link would move promote and
    retire again and silently un-key a step, which is the failure `converge`'s own case exists
    to catch.

    ⚑ AND THE COORDINATE THAT SURVIVES IS THE RIGHT ONE, WHICH IS WHY THIS IS A RE-ANCHORING
    RATHER THAN A PATCH. This arc measured repeatedly that *"`seq` is log-wide while `local_id`
    is per-core and dense"* — the density that licenses the `ekey[]` fibre encoding, and the
    reason a positional cut slices ACROSS cores and leaves a prefix of one fibre. `obs` is keyed
    `(core_id, local_id)`; that pair is an observation's identity, and `seq` was a second
    numbering laid over it for a consumer that no longer exists. The stage always meant *is this
    row IN the log*, and only the log-wide counter is gone.
    """
    return d.get("local_id") is not None


# ── `_settled` — THE LINK, DELETED 2026-08-12. FOUR LINKS BECAME THREE. ───────────────────
#
#     Its inserting transaction has committed — `age(xmin) > 0`, wraparound-safe.
#         return bool(d.get("settled"))
#
# ⚑ ITS OWN ⚑ BLOCK IS KEPT BECAUSE THE REASONING IN IT IS STILL TRUE AND STILL NOT A STAGE:
# *"NOT `seq <= max(seq)`. A sequence gives monotonic ASSIGNMENT, never monotonic COMMIT, so a
# position may exist while its row is still invisible to other readers."* Correct — and it is
# an argument about a WATERMARK over a set, not about a row. `schema_decl` said the same:
# *"the HWM is the point below which no write transaction is still in flight"*. That
# boundary-over-a-set is the only form that carried information, and it went with `hwm()`.
#
# ⚑⚑ THE STAGE ITSELF IS NOT REAL, WHICH IS WHY THIS IS A DELETION AND NOT A RE-ANCHORING.
# Under MVCC, **if a reader can see the row, it is committed** — that is what visibility MEANS.
# If a reader cannot see it, the store's reconstruct-from-lower-order rule already covers the
# case (user, 2026-08-12: *"That should be a given from the moment an agdai is first written in
# as event records; remember we reconstruct higher-order views from lower-order views if the
# lower-order-view hasn't been persistently upgraded yet."*). So no reader ever has to ask.
#
# ⚑ AND THE PREDICATE IS OBSERVER-RELATIVE, WHICH IS THE OTHER HALF (user, 2026-08-12: *"It's
# not a meaningful metric; it's a scalar that gets mistaken for a field."*). `age(xmin)` is
# `current_xid − xmin`: not a fact about the row, a fact about the row FROM THE ASKING
# TRANSACTION'S SNAPSHOT. Two readers get two answers for one row. The only thing it can
# distinguish is a reader's own uncommitted inserts — the reader knowing about its own writes,
# which is not information about the substrate. There was no production writer of the `settled`
# key at all: `pycodemod --literal settled` found the predicate, the chain link, and the census
# arm, and nothing that ever SET it.
#
# ⚑⚑ DO NOT RE-ANCHOR IT ONTO A NEW PREDICATE — a `projected` stage was proposed and is WRONG.
# The model for that proposal was `_observed`, which WAS correctly re-anchored (from `d["seq"]`
# to `d["local_id"]`) when `seq` was deleted. The two cases look alike and are not: `_observed`
# was re-anchored because the STAGE was real and only its COORDINATE had gone. Here the stage
# itself is not real, so there is nothing to give a new coordinate to.
#
# ⚑ AND THE ONE EDIT IS THE CHAIN'S PREMISE PAYING OFF, FOR THE SECOND TIME. *"STAGES ARE
# PREFIXES OF ONE CHAIN … adding a stage is `_▷_`, and the entailments between stages are all
# the SAME function (`drop`)"* — so removing one is deleting one `.then(...)` and every
# entailment re-derives. What does NOT re-derive is anything that TYPED a boundary INDEX. When
# `consumed` went, `sppf_db.converge`'s integer-keyed roster moved retire 4 → 3 and the failure
# mode was SILENT. That roster is keyed by boundary NAME as of this same day, and this deletion
# is the first chain edit it has to survive: `settled` disappearing makes promote's declared
# boundary unresolvable, which now REFUSES instead of shortening the order.


# ── `_consumed` — THE LINK, DELETED 2026-08-12. FIVE LINKS BECAME FOUR. ────────────────────
#
#     Every registered CURSOR consumer has advanced past it.
#         floor = d.get("floor")
#         return floor is not None and d.get("seq") is not None and d["seq"] < floor
#
# ⚑ ITS OWN ⚑ BLOCK ALREADY NAMED THE READER THE STAGE COULD NOT MODEL: *"CURSORS ONLY. A
# source-driven reader (`scope_fix`) never advances — its liveness is a JOIN against the
# source, which is the `sourced` link, not this one. Counting it here would pin this stage
# forever and make consumption unreachable."* Every reader in the store turned out to be the
# kind this link had to exclude, and a stage whose population is empty is not a stage.
#
# ⚑⚑ AND THE CHAIN IS WHY THE DELETION IS ONE EDIT RATHER THAN N². The module's own premise —
# *"STAGES ARE PREFIXES OF ONE CHAIN, not four independent predicates … adding a stage is
# `_▷_`, and the entailments between stages are all the SAME function (`drop`)"* — cuts both
# ways: REMOVING a stage is deleting one `.then(...)`, and every entailment re-derives. What
# does NOT re-derive is anything that TYPED a boundary index: `sppf_db.converge` keys its step
# roster by index and its retire step moved 4 → 3. See the case there; the failure was silent.
#
# ⚑ THE DISTINCTION IT CARRIED SURVIVES IN THE LINK ABOVE IT AND THE ONE BELOW. `settled` is
# still "the inserting transaction has committed" and `reflected` is still "the durable form
# RECONSTRUCTS this record"; what is gone is the middle claim that some READER had passed a
# POSITION, which is the promise-about-the-future that reconstruct-on-demand replaced.


def _reflected(d):
    """The durable form RECONSTRUCTS this record — so the staged copy is redundant.

    ⚑ A CURSOR ADVANCING IS NOT A DURABLE ARTIFACT, AND CONFLATING THEM IS THE BUG THIS
    STAGE EXISTS TO PREVENT. `consumed` says every reader moved past a position; it says
    nothing about whether anything was BUILT. Draining on `consumed` alone would delete
    records whose replacement may not exist.
    #
    ⚑ THE LICENSE IS A ROUND-TRIP, NOT A BELIEF (user, 2026-08-07: *"between the reverse
    index and the SPPF, the event tier should be reconstructible; it's a reflection"*).
    Rebuild the core's rows from (SPPF, reverse index), compare to what is stored, and
    treat equality as the permission. `Substrate.Lifecycle.Drainable` proves the safety
    consequence: a reflection makes `project` injective, so the durable form DETERMINES the
    staged one and no two records can share an image.
    #
    ⚑ AND THE REVERSE INDEX IS NOT A SECOND STRUCTURE — IT IS THE EVENT TIER QUOTIENTED BY
    THE SPPF (user). The SPPF *is* the equivalence (same content ⇒ same node); the reverse
    index is the FIBRE, recording which occurrence fell into which class. So the three are
    one decomposition, not three artifacts:
    #
        event tier  =  recon( SPPF , reverse index )
           the whole      the base      the residue
    #
    That is `a = recon q b r` at the tier level — the same wedge as everywhere else in this
    repo — and it is WHY reconstruction works: a quotient together with its fibres is the
    original BY CONSTRUCTION, not by luck. It also explains `scope_fix` exactly: its
    complaint is that the projection collapses two applications of one module, i.e. the
    quotient losing information, and the reverse index is precisely what was lost. Not a
    patch for a defect — the other half of the decomposition.
    #
    ⚑ AND THE RESIDUE IS NOT OBLIGED TO INHERIT THE EVENT TIER'S REPRESENTATION (user).
    Its shape is fixed by the QUOTIENT, not by whatever the decoder happened to emit. `obs`
    stores `(core_id, local_id, ekey)` per observation because that is what the walk
    produced; after quotienting, the residue only has to answer "which occurrences fell
    into this class" — and the SPPF already supplies the class. So the residue is a FIBRE,
    and a fibre over a DENSE `local_id` is a SEQUENCE, not a set of triples: per core, an
    `ekey[]` whose index IS the `local_id`.
    #
    That is where the ~100× goes. The event tier pays full row width — `core_id` repeated
    on every one of ~55K rows per core, `local_id` stored rather than implied — to express
    something the quotient makes positional. The measurement said "compress the storage";
    the quotient says the residue was never that shape to begin with.
    #
    ⚑ AND THIS IS WHY THE EVENT TIER IS A BUFFER, NOT A STORE. Left undrained it grows
    without bound — measured: ~55K obs rows per core under the generic walk, ~100× the
    prior walk, projecting to ~177M rows and 40+ GB for the corpus. That number is a
    consequence of never draining, not of the walk recovering too much.
    #
    A core that fails to reconstruct does NOT drain: it is retained and the failure is
    reported. Nothing is deleted on the strength of an argument.

    ⚑⚑ AND UNTIL 2026-08-11 THIS FUNCTION WAS A DICT LOOKUP OF A KEY NOTHING SET. Forty lines
    deriving the obligation from `Substrate.Lifecycle.{Reflection,Drainable}` — correctly,
    naming the round-trip, the injectivity consequence and the wedge — terminating in
    `bool(d.get("reflected"))`, with `pycodemod --calls _reflected` reporting **1 def, 0
    calls**. The stage was DECLARED in `LIFECYCLE` and computed nowhere, so `--lifecycle`
    reported every observation `unconsumed` and the terminal link never fired.

    ⚑ THE DERIVATION WAS NEVER THE GAP — THE WIRING WAS. That is worth separating, because
    "the Python is a parallel implementation of the Agda model" was my reading an hour ago and
    it is wrong: this docstring cites `Drainable` by name and states `event = recon(SPPF,
    reverse index)` correctly. It is a DERIVED VIEW that was written from the specification
    and then left unconnected — a different defect from divergence, and one a
    do-they-agree test could never find, since an uncalled predicate agrees with everything.

    ⚑ WHAT DISCHARGES IT NOW: `reconstruct.reflects_obs`, which since Ⓒ1 checks BOTH halves
    the Agda demands — the round-trip (`reconstruct(project(s)) ≡ s`, per core) AND
    `drainable`'s injectivity hypothesis (`_ekey_ambiguity`: no `node_id`+`ch` addresses two
    ekeys). The second is the one that was missing, and it is exactly what `Drainable`'s
    comment warns about: *"'The data is elsewhere' is not enough — the durable form must
    DETERMINE the staged one."*
    """
    # ⚑ A PRECOMPUTED VERDICT IS HONOURED, AND ITS ABSENCE IS NOT A PASS. Callers that have
    # already run the per-core check pass it in; callers that have not get False, because an
    # unchecked record is UNMEASURED and this stage licenses deletion. Absent-read-as-pass has
    # cost this arc three separate fixes today; it does not get a fourth here.
    return bool(d.get("reflected"))


#: The lifecycle chain. Named prefixes below are slices of THIS — one declaration.
LIFECYCLE = (
    Chain()
    .then("sourced", _sourced, "the core still exists on disk at the revision that produced this")
    .then("observed", _observed, "a position was assigned in the append-only log")
    # ⚑ `.then("settled", _settled, "the inserting transaction has committed
    # (age(xmin) > 0)")` STOOD HERE — DELETED 2026-08-12. See the residue block above
    # `_reflected`: committedness is a property of the READ (if you can see the row it
    # is committed), and the predicate was observer-relative. Deleting the link, not
    # re-anchoring it.
    .then(
        "reflected",
        _reflected,
        "the SPPF + reverse index RECONSTRUCT this record — the staged copy "
        "is redundant and may be drained",
    )
)

# the named stages, as PREFIXES — mirroring chain-con ⊂ chain-rea ⊂ chain-obs ⊂ charter
chain_sourced = Chain(LIFECYCLE[:1])
chain_observed = Chain(LIFECYCLE[:2])
# `chain_consumed = Chain(LIFECYCLE[:4])` — DELETED 2026-08-12 with the link it named.
# `chain_settled = Chain(LIFECYCLE[:3])` — DELETED 2026-08-12, likewise. The prefixes are
# SLICES, so the roster shrinks by one line and nothing else changes; that is the whole content
# of "named stages are prefixes of ONE chain". Neither had a reader outside this module
# (`pycodemod --binding chain_settled`: 1 binding, 0 uses).
chain_reflected = LIFECYCLE


def reclaimable(d):
    """A datum may be released exactly when it is fully accepted by the chain.

    ⚑ AND THE TWO RELEASES ARE ONE PREDICATE READ FROM OPPOSITE ENDS. A source deletion
    fails `sourced` (the FIRST link) and releases from the top; a cursor advance satisfies
    `consumed` (the LAST) and releases from the bottom. They looked like two unrelated
    mechanisms — a core-prune and a positional sweep — only because no chain related them.
    """
    return LIFECYCLE.holds(d)


def explain(d):
    """Why this datum is held — the located rejection, in words.

    ⚑ THIS IS THE ANSWER THE SCALAR FLOOR COULD NOT GIVE. "0 reclaimable" is a count;
    "held at `sourced` because the core still exists on disk" is a reason.
    """
    r = LIFECYCLE.rejected(d)
    if r is None:
        return "reclaimable — accepted by every stage"
    i, name, because = r
    return "held at stage %d (%s): %s" % (i, name, because)


def _selftest():
    cases = []

    def check(label, got, want):
        cases.append((label, got == want, got, want))

    # ⚑ `"seq": 10` BECAME `"local_id": 10` (2026-08-12) WHEN `_observed` WAS RE-ANCHORED off
    # the deleted log-wide position onto the fibre coordinate `obs` is actually keyed by. The
    # datum is the same datum; only the coordinate naming its address in the log changed.
    # ⚑ `"settled": True` LEFT THE FIXTURE 2026-08-12 WITH ITS LINK. Leaving it would be a key
    # no predicate reads — the exact shape `_reflected` was in when it sat at 1 def / 0 calls
    # reading a key nothing set, reproduced in the fixture instead of in the model.
    live = {"source_live": True, "local_id": 10, "reflected": True}
    check("a fully-accepted datum is reclaimable", reclaimable(live), True)
    check("...and reached the whole chain", LIFECYCLE.reached(live), LIFECYCLE)
    check("...with no rejection", LIFECYCLE.rejected(live), None)

    # ⚑ CUMULATIVITY: a witness at stage N carries every stage below it.
    w = LIFECYCLE.witness(live)
    check("the witness IS the chain it satisfies", w, LIFECYCLE)
    check("drop peels exactly one link", drop(w).names(), ["sourced", "observed"])
    check("drop∘drop reaches the first stage", drop(drop(w)).names(), ["sourced"])
    # every named stage is a PREFIX, not a separate declaration
    # ⚑ `chain_consumed` WAS THE FOURTH ENTRY HERE AND WENT WITH ITS LINK (2026-08-12), and
    # `chain_settled` was the third and went the same day. The case is UNCHANGED IN KIND both
    # times, which is the property being asserted: the named stages are slices, so removing one
    # removes a line rather than rewriting a relationship.
    check(
        "named stages are prefixes of one chain",
        (chain_sourced.names(), chain_observed.names(), chain_reflected.names()),
        (["sourced"], ["sourced", "observed"], ["sourced", "observed", "reflected"]),
    )

    # ⚑ BEING IN THE LOG IS NOT BEING REFLECTED, AND THAT DISTINCTION IS THE WHOLE TERMINAL
    # STAGE. A row can exist without anything durable being built; draining on existence alone
    # would delete records whose replacement may not exist. This datum is observed and has NO
    # reverse-index record — it must be held, at the last link.
    #
    # ⚑ THE CASE HAS NOW BEEN RE-BASED TWICE, AND THE CLAIM IS THE SAME EACH TIME. It said
    # "CONSUMED IS NOT REFLECTED" and cited a CURSOR advancing; then "SETTLED IS NOT REFLECTED"
    # and cited a commit. Both framings retired with their links. What it is really asserting —
    # *"neither a cursor advancing nor a transaction committing is a durable artifact"* — is
    # always made against the strongest thing BELOW `reflected`, which is `observed` now. The
    # case tracks the chain instead of naming a fixed neighbour.
    observed_not_reflected = dict(live, reflected=False)
    check("an observed-but-unreflected datum is HELD", reclaimable(observed_not_reflected), False)
    check(
        "...rejected at `reflected`, not earlier",
        LIFECYCLE.rejected(observed_not_reflected)[1],
        "reflected",
    )
    check(
        "...having reached everything below it",
        LIFECYCLE.reached(observed_not_reflected).names(),
        ["sourced", "observed"],
    )

    # ⚑ LOCATED REJECTION — the property a boolean collapses. A dead source and an
    # unconsumed position are BOTH "not reclaimable" and are different facts.
    dead = dict(live, source_live=False)
    check("a dead source is rejected at link 0", LIFECYCLE.rejected(dead)[1], "sourced")
    check("...and reached NO stage", LIFECYCLE.reached(dead).names(), [])

    # ⚑ THIS PAIR USED TO BE `dead` VS `unconsumed` (`floor=0`). The unreflected datum is the
    # honest replacement: it is the one that is rejected at the LAST link while the dead source
    # is rejected at the FIRST, which is the located-rejection property the pair exists to
    # drive. Nothing about the property changed — only which datum can still exhibit it.
    unreflected = dict(live, reflected=False)
    check(
        "an unreflected datum is rejected at the LAST link",
        LIFECYCLE.rejected(unreflected)[1],
        "reflected",
    )
    # ⚑ SPELT FROM THE CHAIN, NOT COUNTED. This read "...but still reached three stages" over a
    # hardcoded three-name list; both halves were a second copy of `LIFECYCLE` and both went
    # stale the moment a link left. What the case is ABOUT is that it reached EVERYTHING BELOW
    # the link that rejected it, which is `drop` of the whole chain.
    check(
        "...but still reached every stage below it",
        LIFECYCLE.reached(unreflected).names(),
        drop(LIFECYCLE).names(),
    )
    # both are "not reclaimable" — and the point is that they are DISTINGUISHABLE
    check("both are unreclaimable", (reclaimable(dead), reclaimable(unreflected)), (False, False))
    check(
        "...yet rejected at DIFFERENT links",
        LIFECYCLE.rejected(dead)[0] != LIFECYCLE.rejected(unreflected)[0],
        True,
    )

    # ⚑⚑ `observed` HAD NO CASE THAT COULD FAIL IT, MEASURED BY MUTATION 2026-08-12: replacing
    # `_observed`'s body with `return True` left the suite at **41/41**. Every fixture datum
    # carried the address key, so the link was asserted by every case and DISCRIMINATED by none
    # — the shape `_reflected` was in when it sat at 1 def / 0 calls reading a key nothing set.
    # Found while re-anchoring the predicate off the deleted `obs.seq`; the re-anchoring is what
    # made someone look, which is the argument for mutating a guard rather than reading it.
    unaddressed = dict(live)
    del unaddressed["local_id"]
    check(
        "a datum with no address in the log is rejected at `observed`",
        LIFECYCLE.rejected(unaddressed)[1],
        "observed",
    )
    check("...having reached only `sourced`", LIFECYCLE.reached(unaddressed).names(), ["sourced"])

    # ── THE `unsettled` CASE — DELETED 2026-08-12 WITH ITS LINK. ─────────────────────
    #
    #     unsettled = dict(live, settled=False)
    #     check("an assigned-but-uncommitted position is rejected at `settled`",
    #           LIFECYCLE.rejected(unsettled)[1], "settled")
    #     check("...having still reached `observed`",
    #           LIFECYCLE.reached(unsettled).names(), ["sourced", "observed"])
    #
    # ⚑ ITS ARGUMENT IS QUOTED BECAUSE IT IS THE ONE THAT DISSOLVES: *"A position exists
    # (observed) while the row is still invisible — collapsing the two would let a consumer
    # advance past an uncommitted row and never see it."* Under MVCC that consumer CANNOT see
    # the uncommitted row, so it cannot advance past it; the hazard needs a reader that sees a
    # row it should not, which is the state the engine makes unreachable. The case constructed
    # its own discriminating datum by SETTING `settled=False` — a key no production writer ever
    # set — so it was driving a state the store cannot produce.

    # ⚑ `check("no floor ⇒ not consumed", _consumed(dict(live, floor=None)), False)` STOOD
    # HERE (2026-08-12). It drove the NULL rule — an absent floor must not read as satisfied —
    # and that rule is preserved where it can still fire: `schema_queue`'s residue block for
    # `lwm` states it as the general form (*"absent-read-as-permission is the one failure mode
    # that cannot be undone"*), and `_reflected` below still enforces it (an unchecked record
    # gets False, never a pass). The case goes because its subject does; the rule does not.

    # ⚑ ε HAS NOTHING TO PEEL, and saying so beats returning ε silently — a `drop` that
    # bottoms out quietly would make an over-peel indistinguishable from the base stage.
    try:
        drop(Chain())
        check("drop on ε REFUSES", "returned", "ValueError")
    except ValueError:
        check("drop on ε REFUSES", "ValueError", "ValueError")

    check("ε accepts everything", Chain().holds({}), True)

    # ⚑ THE CASES MUST FAIL AGAINST A BROKEN CHAIN, NOT MERELY PASS AGAINST THIS ONE.
    # 20/20 on a first run is a reason for suspicion, not satisfaction — so this drives a
    # DELIBERATELY COLLAPSED chain and asserts the structure notices. Without it, every case
    # above would pass on a model that cannot tell two adjacent stages apart.
    #
    # ⚑ THE MERGE UNDER TEST WAS `observed`+`settled` AND IS NOW `sourced`+`observed`
    # (2026-08-12). `settled` left the chain, so the old merge is not a mutation of anything —
    # it names a link that does not exist. The harness had to be RE-BASED onto a pair the chain
    # still has, which is the honest form: a mutation test is only a test while the thing it
    # breaks is present. The discriminating datum re-bases with it — `unaddressed` (a live
    # source with no address in the log) is now what separates the two chains, where `unsettled`
    # used to be.
    _collapsed = (
        Chain()
        .then("sourced+observed", lambda d: _sourced(d) and _observed(d), "")
        # ⚑ THE PADDING LINK WAS `_consumed`, THEN `_reflected`. The mutation under
        # test is the merge above it, so what this must be is *a real predicate that
        # is not one of the two being merged*, which `_reflected` is.
        .then("reflected", _reflected, "")
    )
    # ⚑ DERIVED, NOT TYPED. This read `len(LIFECYCLE) - 1` and broke when the chain gained
    # `reflected` — a case that hardcodes the chain's length is a second copy of it. What
    # the case is ABOUT is that the collapsed chain merged two links into one.
    check("the collapsed chain has FEWER stages", len(LIFECYCLE) - len(_collapsed) > 0, True)
    # the discriminating datum: the source is live but nothing was written to the log
    check(
        "the correct chain places it at `sourced`",
        LIFECYCLE.reached(unaddressed).names()[-1],
        "sourced",
    )
    check(
        "...while the collapsed chain loses that distinction",
        _collapsed.reached(unaddressed).names(),
        [],
    )
    # and the located rejection differs, which is the fact a boolean would have hidden
    check(
        "...rejecting at a DIFFERENT link than the correct chain",
        _collapsed.rejected(unaddressed)[1] != LIFECYCLE.rejected(unaddressed)[1],
        True,
    )
    check("explain names the holding stage", "sourced" in explain(dead), True)
    check("...and says why", "still exists on disk" in explain(dead), True)

    # ── boundaries: every stage pair, derived from the chain ────────────────────────
    # ⚑ THERE IS ONE BOUNDARY PER LINK, INCLUDING `ε → sourced`. That first one is the
    # FILESYSTEM edge — where `_core_ver` reads `st_mtime_ns` — and I had been treating
    # the filesystem as outside the model. Asserting the count catches a future edit that
    # starts boundaries at 1 and silently drops the ingest's draw side.
    check("one boundary per link", len(boundaries()), len(LIFECYCLE))
    check("boundary 0 is the filesystem edge", boundaries()[0][:2], (0, "ε"))
    check("...feeding the first stage", boundaries()[0][2], "sourced")
    check("the last boundary feeds the terminal stage", boundaries()[-1][2], "reflected")

    # ⚑ A BOUNDARY IS AN INDEX, NOT A STRING. Deriving both sides from the chain is what
    # stops a `"sourced→observed"` label drifting from the chain it names — the
    # derived-view defect this repo keeps paying for.
    # ⚑ SPELT AS "THE LAST BOUNDARY", NOT AS `boundary(2)` WITH A THREE-NAME LIST. Both halves
    # were a hardcoded copy of the chain and both went stale when `settled` left; the property
    # is that a boundary's sides are the chain's own prefixes, which is stated by DERIVING them.
    _up, _down = boundary(len(LIFECYCLE) - 1)
    check(
        "a boundary's sides are chain PREFIXES",
        (_up.names(), _down.names()),
        (drop(LIFECYCLE).names(), LIFECYCLE.names()),
    )
    check("...differing by exactly one link", len(_down) - len(_up), 1)
    # the downstream side of boundary i is the upstream side of boundary i+1 — the chain
    check("boundaries compose", boundary(1)[1].names(), boundary(2)[0].names())

    try:
        boundary(len(LIFECYCLE))
        check("an out-of-range boundary REFUSES", "returned", "IndexError")
    except IndexError:
        check("an out-of-range boundary REFUSES", "IndexError", "IndexError")

    # ── boundary_index: the NAME → position resolver, and its refusal ────────────────
    # ⚑⚑ THIS IS THE FUNCTION THAT LETS A CONSUMER STOP TYPING INTEGERS. `sppf_db.converge`
    # keyed its step roster by boundary INDEX; when `consumed` left the chain the retire key
    # renumbered 4 → 3 and `if i in steps` dropped the step with no error. Keying by the
    # boundary's NAME makes that class unreachable — but only if an unresolvable name RAISES,
    # so the two cases below are one guard: it resolves, and it refuses.
    check(
        "every link name resolves to the boundary that feeds it",
        [boundary_index(n) for n in LIFECYCLE.names()],
        list(range(len(LIFECYCLE))),
    )
    check(
        "...and the resolved index is the one `boundaries()` publishes",
        [boundary_index(d) for _i, _u, d in boundaries()],
        [i for i, _u, _d in boundaries()],
    )
    # ⚑ THE REFUSAL MUST NAME THE CHAIN, or the reader learns only that something is wrong.
    # A bare `KeyError('nosuchstage')` cannot distinguish "I typed it wrong" from "the link
    # was deleted under me", and the second is the case this exists for.
    try:
        boundary_index("nosuchstage")
        check("an unresolvable boundary name REFUSES", "returned", "KeyError")
    except KeyError as _e:
        check("an unresolvable boundary name REFUSES", "KeyError", "KeyError")
        check("...naming the offending name", "nosuchstage" in str(_e), True)
        check(
            "...and the chain's ACTUAL link names",
            all(n in str(_e) for n in LIFECYCLE.names()),
            True,
        )
    # ⚑ AND IT MUST NOT RESOLVE A STAGE THE CHAIN NO LONGER DECLARES — the mutation this
    # whole mechanism exists to make loud. Driven with a name that was a real link in this
    # module's history (`consumed`, deleted 2026-08-12), because a plausible-but-retired name
    # is the input a stale roster actually carries.
    try:
        boundary_index("consumed")
        check("a RETIRED link name does not resolve", "returned", "KeyError")
    except KeyError:
        check("a RETIRED link name does not resolve", "KeyError", "KeyError")

    # ── service_order: the actor roster, keyed by boundary NAME ─────────────────────
    # ⚑ THE ROSTER IT REPLACED WAS `{3: retire, 2: promote, 1: ingest}` FILTERED BY `if i in
    # steps` — so a chain edit renumbered a key out of existence and the step was dropped in
    # SILENCE. These cases assert the two halves that make that unreachable: the order comes
    # from `drain_order()`, and an unresolvable name REFUSES instead of vanishing.
    _r = [
        (LIFECYCLE.names()[-1], "reclaim", "drain"),
        (LIFECYCLE.names()[-1], "feed", "fill"),
        (LIFECYCLE.names()[1], "feed", "admit"),
    ]
    check(
        "a roster is serviced downstream-first",
        [e[2] for e in service_order(_r)],
        ["drain", "fill", "admit"],
    )
    check(
        "...and the WRITING order does not decide it",
        [e[2] for e in service_order(list(reversed(_r)))],
        ["drain", "fill", "admit"],
    )
    # ⚑ THE TIE-BREAK IS THE HALF `drain_order` CANNOT STATE: two actors at ONE boundary. A
    # sort keyed on the boundary alone would leave their order to the input's, which is the
    # declaration-order dependence the whole module avoids.
    check(
        "...reclaim before feed WITHIN one boundary",
        [e[2] for e in service_order([_r[1], _r[0]])],
        ["drain", "fill"],
    )
    # ⚑ AND THE REFUSALS. `consumed` is driven deliberately: a plausible-but-RETIRED name is
    # what a stale roster actually carries, and it is the exact input that failed silently.
    try:
        service_order([("consumed", "reclaim", "retire")])
        check("a roster naming a retired boundary REFUSES", "returned", "KeyError")
    except KeyError as _re:
        check("a roster naming a retired boundary REFUSES", "KeyError", "KeyError")
        check(
            "...naming the actor and the boundary it asked for",
            ("'retire'" in str(_re)) and ("'consumed'" in str(_re)),
            True,
        )
        check(
            "...and the chain's ACTUAL links, so the reader sees what it drifted from",
            all(n in str(_re) for n in LIFECYCLE.names()),
            True,
        )
    try:
        service_order([(LIFECYCLE.names()[-1], "nosuchside", "retire")])
        check("an unknown roster SIDE REFUSES", "returned", "KeyError")
    except KeyError:
        check("an unknown roster SIDE REFUSES", "KeyError", "KeyError")

    # ── drain PRECEDENCE: downstream empties before upstream refills ────────────────
    # ⚑ THIS IS WHAT BOUNDS THE DISK PEAK, and the chain alone does not imply it. Servicing
    # upstream first fills B before C is emptied, so every tier holds its maximum at once and
    # the footprint is the SUM of tiers rather than the MAX of one.
    check("drains are ordered downstream-first", drain_order()[0], len(LIFECYCLE) - 1)
    check("...ending at the filesystem edge", drain_order()[-1], 0)
    check(
        "...covering every boundary exactly once",
        sorted(drain_order()),
        list(range(len(LIFECYCLE))),
    )
    # ⚑ THE PREDICATE MUST BE ASYMMETRIC — a symmetric one would permit either order and
    # silently allow the schedule this rule exists to forbid.
    #
    # ⚑⚑ THESE THREE READ `drains_before(3, 1)`, `(1, 3)` AND `(2, 2)`, AND THE FIRST TWO
    # RAISED `IndexError: boundaries are 0..2` THE MOMENT `settled` LEFT THE CHAIN (measured,
    # 2026-08-12). That is the good outcome and it is worth recording rather than quietly
    # fixing: a typed boundary index is a second copy of the chain, and here it failed LOUDLY
    # only because `drains_before` range-checks. `sppf_db.converge`'s roster used the same
    # integers with no range check and would have dropped a step in silence. Same defect,
    # two different blast radii — which is the argument for naming boundaries everywhere.
    _terminal = boundary_index(LIFECYCLE.names()[-1])
    _ingest_b = boundary_index(LIFECYCLE.names()[1])
    check(
        "a downstream boundary precedes an upstream one", drains_before(_terminal, _ingest_b), True
    )
    check("...and NOT the reverse", drains_before(_ingest_b, _terminal), False)
    check("...a boundary does not precede itself", drains_before(_terminal, _terminal), False)
    # the concrete instance: the terminal boundary (which retire and promote share) must run
    # before `sourced→observed`, which is exactly "B drains to C before A drains to B"
    check(
        "the terminal drain precedes the ingest's own boundary",
        drains_before(_terminal, _ingest_b) and not drains_before(_ingest_b, _terminal),
        True,
    )

    failed = [c for c in cases if not c[1]]
    for label, _, got, want in failed:
        print("  FAIL %s: got %r want %r" % (label, got, want))
    print("selftest: %d/%d" % (len(cases) - len(failed), len(cases)))
    return 0 if not failed else 1


# ── ⚑⚑ A CURSOR SHOULD BE DERIVED, NOT STORED (user, 2026-08-11) ────────────────────
#
# > *"a cursor, as a stateful object, should probably not be reified; it should be
# > derivable. Because its advancement depends on satisfaction of a criteria, its frontier
# > can be derived from the boundary where that criteria ceases (or begins) to be
# > satisfied."*
#
# ⚑ THIS DISSOLVES A WHOLE CLASS OF DEFECT RATHER THAN PATCHING ITS INSTANCES, and every
# instance this session was the same shape: a REIFIED cursor is a CACHED answer to "how far
# has this consumer got", and each failure was that cache disagreeing with reality —
#
#   * the selftest deleted the registry and restored from a snapshot that an exception lost
#     (three separate live-store damages, "fix it with a `finally`" recorded and not done);
#   * a live cursor position (6,274,182) was copied into the SANDBOX registry by a selftest
#     run, and stopped a rehearsal dead at `refused move to 1255689`;
#   * `full=True` dropped the event tier and left both cursors at 1,255,689 over a tier whose
#     `seq` restarts at 1 — a promise outliving the data it describes.
#
# NONE of those are possible against a derived frontier. There is no snapshot to lose, no
# position to copy, and nothing to outlive the tier: drop the rows and the frontier moves
# because the criterion's answer moved.
#
# ⚑ AND THE CRITERION IS ALREADY WRITTEN DOWN PER CONSUMER — that is what makes this a
# simplification rather than a rewrite:
#
#   sppf:projection   consumed ⟺ this observation's node exists in the projection.
#                     Frontier = max(seq) over `obs ⋈ obs_node`. `obs_node` was built in Q17
#                     for the reflection check and already carries exactly this.
#   scope_fix:resolver  a PIN — its criterion is source-liveness, not a position, which is
#                     precisely why it never advances. A derived frontier states that as
#                     "the criterion is not positional" instead of as a magic 0 that the
#                     registry cannot distinguish from a stalled cursor.
#
# ⚑ WHAT THE `consumer` TABLE WOULD KEEP: the REGISTRY (who exists, of what kind) — a
# declaration, not a measurement. `lwm` and `updated` are the derived half and are the half
# that has gone wrong. Keeping identity in a table and computing position from the data is
# the same split as `SPPF × fibre`: store what cannot be recomputed, derive what can.
#
# ⚑ THE COST, STATED HONESTLY: a derived frontier is a JOIN per query where a stored one is
# a column read, so `lwm()` stops being O(1). That is a real trade and it is the reason to
# measure before switching — but it is a PERFORMANCE question, and the current design is
# paying a CORRECTNESS price for the speed. `advance()` and its forward-only guard also
# become unnecessary rather than merely fixed: a frontier that is computed cannot move
# backward, because there is no move.
#
# ⚑⚑ AND THE TRANSACTIONAL ARGUMENT IS STRONGER THAN EITHER (user, 2026-08-11: *"This will
# also mesh MUCH better with transactional models."*). I framed this as correctness-vs-speed
# and that undersold it: a STORED cursor is a SECOND WRITE that must be made atomic with the
# work it describes, and a DERIVED one is read from the same snapshot as the data, so the
# atomicity question does not arise.
#
# ⚑ THE WINDOW IS LIVE, NOT THEORETICAL. `sppf_db.build` runs `project_sppf(con)` — which
# commits its rows — and then `_advance_projection(con)`, which commits the cursor. TWO
# transactions. A crash between them leaves the projection durable and the cursor behind it,
# so the next run re-projects work already done; the reverse ordering (which someone will
# eventually "fix" it to) leaves the cursor AHEAD of the projection and licenses reclaiming
# rows nothing consumed. The comment at `_advance_projection` argues carefully for one of
# those orderings — which is the tell that the pair is a distributed-commit problem being
# solved by call order.
#
# A derived frontier has no second write to order. `max(seq) over obs ⋈ obs_node` inside the
# projection's own transaction is exactly as far as the projection has got, atomically, by
# construction — and a reader at REPEATABLE READ sees a frontier consistent with the rows it
# is reading, which a separately-committed column cannot guarantee.
#
# ⚑ IT ALSO RETIRES A CONCURRENCY HAZARD NOBODY HAS HIT YET: two projections running at once
# race on `UPDATE consumer SET lwm`, and last-write-wins can move the frontier BACKWARD past
# work the other committed. `advance()`'s forward-only check is a partial guard against a
# race that a computed frontier cannot have.
#
# NOT BUILT. Recorded here, in the actor model that owns the concept, rather than in a plan
# file — the next reader of `advance()` should find this before writing another guard for a
# cache that should not exist.


# ── actors and boundaries (the general form; ⚑ NOT YET WIRED TO THE STORE) ──────────
#
# ⚑ EVERY STAGE BOUNDARY HAS BOTH WATERMARKS, AND I BUILT ONLY ONE PAIR (user,
# 2026-08-06: *"every stage has a hwm and lwm relating it to the progress from the
# previous stage / to the next stage"*). `schema.hwm()` and `schema.lwm()` are NOT a
# pair bracketing one thing — they sit at DIFFERENT boundaries:
#
#     sourced ──┬── observed ──┬── settled ──┬── consumed
#               │              │             │
#               │              │             └─ lwm() = min consumer cursor
#               │              └─ hwm() = highest SETTLED seq
#               └─ (unmeasured: highest revision drawn from disk)
#
# Naming them as a pair hid that a boundary sits BETWEEN them — exactly the boundary a
# concurrent ingest moves.
#
# ⚑ AN ACTOR SPANS A BOUNDARY, AND ITS TWO WATERMARKS FACE OPPOSITE DIRECTIONS.
#   * HWM on the DRAW side — how far upstream has made data available. A bound the actor
#     OBEYS; reading past it reads data that may not be settled.
#   * LWM on the FEED side — how far it has released downstream. A promise the actor
#     PUBLISHES; everything below is done and safe to reclaim.
# One is imposed, the other asserted, and they chain: A's published LWM bounds B's HWM.
#
# ⚑ AN ACTOR IS ANYTHING THAT KNOWS AN INDEX (user's criterion, and it is DECIDABLE
# rather than a judgement): any stateful process, anything with side effects. The only
# non-actor is a stateless function with no knowledge of input or output index — a pure
# map, whose apparent stage is really its caller's. So the actor population is
# CENSUSABLE from the code, not declared in a table.
#
# ⚑ AND A BOUNDARY IS "ANY POINT WHERE WE'VE CHOSEN TO HAVE SIDE EFFECTS" — the same
# criterion. Boundaries are therefore observable too; naming them `"sourced→observed"`
# as strings would be a second spelling of what the code already states, drifting from
# the chain. A boundary is an INDEX into `LIFECYCLE`.
#
# ⚑ THIS RETYPES `scope_fix`, WHICH WAS NEITHER A PIN NOR A CURSOR. It is an actor whose
# DRAW side is `sourced` and whose FEED side is ABSENT — it reads observations bounded by
# source-liveness and releases nothing. An actor with no feed side has nothing to
# advance, which is precisely why "pin at zero forever" was the only thing the
# consumer-shaped registry could express for it. Terminal actor, not a special case.
#
# ⚑ AND THE FILESYSTEM ALREADY HAS ITS WATERMARK — `sppf_db._core_ver` is
# `os.stat(path).st_mtime_ns`, whose own docstring says "an advanced mtime IS 'rebuilt
# since we last decoded' — exactly the freshness question". `st_mtime_ns` is an exact
# integer, so it is a usable POSITION. The ingest's draw-side HWM is `max(mtime)` on
# disk and its feed-side LWM is what it committed as observations. I had been treating
# the filesystem as outside the model when it was already participating.
#
# ⚑ STORED-VS-DERIVED FOR A DRAW HWM *COMMUTES* (user) — same value either way, so it is
# a per-actor materialization choice, never a schema fork. I was about to bake a
# nullable-means-two-things column over a distinction with one meaning.


def boundary(i):
    """The i-th stage boundary: (upstream stage, downstream stage) as chain prefixes.

    Boundary i sits between link i-1 and link i, so boundary 0 is (ε, sourced) — the
    filesystem edge, where the ingest draws.
    """
    if not 0 <= i < len(LIFECYCLE):
        raise IndexError(
            "boundary %d: LIFECYCLE has %d links, so boundaries are 0..%d"
            % (i, len(LIFECYCLE), len(LIFECYCLE) - 1)
        )
    return Chain(LIFECYCLE[:i]), Chain(LIFECYCLE[: i + 1])


def boundaries():
    """Every boundary, as (index, upstream-name-or-'ε', downstream-name)."""
    out = []
    for i in range(len(LIFECYCLE)):
        up, down = boundary(i)
        out.append((i, up.names()[-1] if up else "ε", down.names()[-1]))
    return out


def boundary_index(name):
    """The index of the boundary that FEEDS stage `name` — a boundary's IDENTITY, not its
    position.

    ⚑⚑ A BOUNDARY'S NAME IS THE STAGE IT FEEDS, AND THAT IS WHAT A CONSUMER MUST KEY ON.
    `boundaries()` already returns indices, and an index is a POSITION: it renumbers the
    moment a link is added or removed. `sppf_db.converge` keyed its step roster by those
    integers and filtered with `if i in steps`, so when `consumed` left the chain on
    2026-08-12 the retire step's key 4 stopped existing and the step was SILENTLY DROPPED —
    a converge loop that would ingest and promote forever and never drain. Nothing raised.
    A name does not renumber; only a RENAME or a DELETION moves it, and both of those are
    the events that should be loud.

    ⚑ SO THE ONLY CORRECT FAILURE IS A REFUSAL. Returning None (or -1, or falling back to a
    position) reconstructs the silent-skip defect one layer down: the caller then has to
    remember to check, which is exactly the check nobody wrote. This raises, and the message
    carries the chain's actual link names so the reader can see what the roster drifted from.

    ⚑ AND IT IS THE SAME SCALAR-VS-FIELD LENS THE REST OF THIS ARC RAN ON. `obs.seq` was a
    log-wide POSITION standing in for the identity `(core_id, local_id)`; `consumer.lwm` was a
    POSITION standing in for "does anyone still need this". `3` was a position standing in for
    "the boundary retire spans". Positions renumber; identities do not.
    """
    names = LIFECYCLE.names()
    if name not in names:
        raise KeyError(
            "no lifecycle boundary feeds %r. LIFECYCLE declares the links %r, so the "
            "boundaries it has are %r. A boundary is named by the stage it FEEDS; a name "
            "that does not resolve is REFUSED rather than skipped, because a roster that "
            "silently loses an entry stops servicing that boundary with nothing raising."
            % (name, names, [(i, u, d) for i, u, d in boundaries()])
        )
    return names.index(name)


def drain_order():
    """The order boundaries must be SERVICED — downstream first, as indices.

    ⚑ THE CHAIN ORDERS A DATUM'S PASSAGE; THIS ORDERS THE DRAINS AGAINST EACH OTHER, and
    nothing expressed the second until now (user, 2026-08-07: *"Given tiers A > B > C … with
    the drain direction going A to B to C, then elements in B must be drained to C before
    elements in A are drained to B."*). `boundaries()` says each actor draws on an hwm and
    feeds an lwm — a LOCAL contract. It does not say which boundary runs first, so a
    scheduler reading only that model may legitimately service them in any order.

    ⚑ AND THE ORDER IS WHAT BOUNDS THE PEAK. Servicing upstream first fills B before C has
    been emptied, so every tier holds its maximum simultaneously — the ingest's footprint
    becomes the SUM of the tiers rather than the max of one. That is the difference between
    "the tier is 6 GB at 5% of the corpus" and a full ingest that must materialise ~100 GB
    before anything drains. Draining downstream-first means a tier is emptied into its
    successor before its predecessor refills it, so the resident set stays near ONE tier's
    worth however long the ingest runs.

    ⚑ SO 'DRAIN AS IT FILLS' IS THIS RULE, NOT A CONCURRENCY WISH. It is not "run the drain
    in parallel and hope"; it is a strict precedence — B→C completes before A→B is permitted
    — which makes the peak a property of the SCHEDULE rather than of the corpus size.

    Returned as boundary INDICES (descending), never as stage-name strings: the names are
    derived from `LIFECYCLE`, and a second spelling of them here would drift the moment a
    stage is added — the derived-view defect this module already avoids in `boundary`.
    """
    return list(range(len(LIFECYCLE) - 1, -1, -1))


#: The two sides an actor can occupy at ONE boundary, in service order.
#
# ⚑ A BOUNDARY CAN CARRY TWO ACTORS, AND THEY ARE NOT INTERCHANGEABLE. The FEED moves data
# across (`sppf_db`'s promote: `obs` → `_node`/`obs_node`); the RECLAIM releases the upstream
# tier once the feed has covered it (its retire: delete the reflected `obs`/`edge`/`event`
# rows). Emptying before refilling is `drain_order`'s own rule applied WITHIN a boundary
# instead of between two — which is why `reclaim` sorts ahead of `feed` and not the reverse.
#
# ⚑ AND THE TIE IS REAL, NOT HYPOTHETICAL. While the chain carried `settled`, promote and
# retire happened to land on different boundary indices and their order fell out of the
# numbering. That was an accident of a spare link: promote is what makes a record `reflected`,
# and retire is what the `reflected` stage LICENSES. Once `settled` went they name the SAME
# boundary, and the order between them has to be DECLARED rather than inherited from how the
# tuples were typed — the same defect `drain_order` exists to prevent one level up.
SIDES = ("reclaim", "feed")


def service_order(roster):
    """Sort an ACTOR ROSTER into service order — and REFUSE a boundary the chain lacks.

    An entry is `(boundary-name, side, actor-name, …)`; anything after the third field is
    carried through untouched (`sppf_db.converge` puts its work predicate and action there).
    The order is `drain_order()` over the boundary each actor NAMES, with `SIDES` breaking a
    tie inside one boundary.

    ⚑⚑ KEYED BY NAME, NOT BY BOUNDARY INDEX, AND THE DIFFERENCE IS A SILENT FAILURE. The
    consumer this was built for kept `{3: retire, 2: promote, 1: ingest}` and selected with
    `order = [i for i in drain_order() if i in steps]`. Shorten the chain by one link and
    `drain_order()` yields `[2,1,0]`: key 3 resolves to nothing, `if i in steps` DROPS it, and
    the loop ingests and promotes forever without ever draining — the precise failure the whole
    store exists to prevent, with no exception and no empty result. It had already mis-fired
    once: when `consumed` left the chain (2026-08-12) retire's index moved 4 → 3 and nothing
    but a hand-written case noticed.

    ⚑ SO AN UNRESOLVABLE NAME RAISES. Skipping is what made the defect silent; refusing is the
    whole content of the change. The message names the roster entry AND the chain's actual
    links, because "something is wrong" cannot distinguish a typo from a link deleted under you.

    ⚑ AND IT IS THIS ARC'S OWN LENS ONE LAYER DOWN: a POSITION standing in for an IDENTITY.
    `obs.seq` was a log-wide counter standing in for `(core_id, local_id)`; `consumer.lwm` was
    a position standing in for "does anyone still need this"; `3` stood in for "the boundary
    retire spans". Positions renumber; identities do not.
    """
    rank = {b: k for k, b in enumerate(drain_order())}
    keyed = []
    for entry in roster:
        bname, side, actor = entry[0], entry[1], entry[2]
        try:
            i = boundary_index(bname)
        except KeyError:
            raise KeyError(
                "actor %r spans the boundary named %r, which the lifecycle chain does NOT "
                "declare. Its links are %r and its boundaries are %r. A roster is keyed by "
                "boundary NAME precisely so this is a refusal: an unresolvable entry used to "
                "be filtered out, leaving a loop that never serviced that boundary and raised "
                "nothing." % (actor, bname, LIFECYCLE.names(), boundaries())
            ) from None
        if side not in SIDES:
            raise KeyError(
                "actor %r declares side %r; the sides are %r (reclaim empties a "
                "tier, feed refills the next one)" % (actor, side, list(SIDES))
            )
        keyed.append(((rank[i], SIDES.index(side)), entry))
    return [e for _k, e in sorted(keyed, key=lambda p: p[0])]


def drains_before(i, j):
    """Must boundary `i` be serviced before boundary `j`? — the precedence, as a predicate.

    ⚑ A PREDICATE, NOT A COMMENT, so a scheduler can be CHECKED against it rather than
    reviewed for it. `i` runs first exactly when it is further DOWNSTREAM (higher index):
    the successor must be emptied before the predecessor refills it.
    """
    if not (0 <= i < len(LIFECYCLE) and 0 <= j < len(LIFECYCLE)):
        raise IndexError("boundaries are 0..%d" % (len(LIFECYCLE) - 1))
    return i > j


# ⚑ ⟡mode-standardize — the `Mode(...)` shape via `climode.from_pairs`. All three are pure
# READS, so `writes=()` (the default) is a CLAIM `check_mode_contracts` holds this file to,
# not an omission: a mode that grows a write and does not declare it becomes a gate failure.
_MODES = (
    ("--selftest", "the guarded cases"),
    ("--stages", "the lifecycle chain: each link, in order, with why it holds a datum"),
    ("--boundaries", "each stage boundary — where an actor draws (hwm) and feeds (lwm)"),
)

import os.path as _osp  # noqa: E402

sys.path.insert(
    0, _osp.join(_osp.dirname(_osp.dirname(_osp.dirname(_osp.abspath(__file__)))), "scripts")
)
from climode import from_pairs  # noqa: E402

#: The declared roster, `{flag: Mode}`.
MODES = from_pairs(_MODES)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    if "--boundaries" in sys.argv:
        print("stage boundaries — an ACTOR spans one, drawing (hwm) and feeding (lwm)\n")
        print("  ix  name        span")
        for i, up, down in boundaries():
            print("  %2d  %-10s  %-10s → %-10s" % (i, down, up, down))
        print("\n  ⚑ a boundary's NAME is the stage it FEEDS, and that is what a consumer")
        print("    keys on (`boundary_index(name)`). The `ix` column is a POSITION: it")
        print("    renumbers whenever a link is added or removed, and a roster keyed by it")
        print("    loses an entry SILENTLY — measured, `sppf_db.converge`, 2026-08-12.")
        print("\n  service order (downstream FIRST — this is what bounds the peak):")
        _names = {i: (u, d) for i, u, d in boundaries()}
        for i in drain_order():
            _u, _d = _names[i]
            print("    %2d  %-10s  %-10s → %-10s" % (i, _d, _u, _d))
        print("\n  ⚑ a tier must be emptied into its successor BEFORE its predecessor")
        print("    refills it. Servicing upstream first makes the resident set the SUM of")
        print("    the tiers instead of the MAX of one — the difference between an ingest")
        print("    that stays near one tier's footprint and one that must materialise the")
        print("    whole corpus before anything drains.")
        print("\n  hwm on the DRAW side  — a bound the actor OBEYS (imposed upstream)")
        print("  lwm on the FEED side  — a promise the actor PUBLISHES (asserted)")
        print("\n  an actor with NO feed side is terminal: it releases nothing, so it")
        print("  can never advance.")
        print('\n  ⚑ THAT RULE HAS NO REGISTERED INSTANCE TODAY. It read "— which is what')
        print('    `scope_fix` is", and `scope_fix` was an actor only by virtue of the')
        print("    consumer registry it was registered in; that registry was deleted")
        print("    2026-08-12 with the queue tier. The rule is kept because it types a real")
        print("    shape — a reader whose liveness is a JOIN against the source rather than")
        print("    a position — but its example is named as GONE rather than left standing.")
        print("    A report explaining a mechanism its own numbers no longer have is the")
        print("    stale-claim class this arc pays for most.")
        raise SystemExit(0)

    if "--stages" in sys.argv:
        print("LIFECYCLE — a Chain, mirroring Substrate.Realizability.Charter\n")
        for i, (name, _f, because) in enumerate(LIFECYCLE):
            print("  %d  %-10s %s" % (i, name, because))
        print(
            "\nentailment: every stage implies all below it (drop), so a datum at "
            "stage N\nprovably satisfies stages 0..N-1 — cumulativity, not N checks."
        )
        raise SystemExit(0)
    print(__doc__.strip().splitlines()[0])
    print("\nmodes:")
    for flag, why in _MODES:
        print("  %-14s %s" % (flag, why))
