{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- DERIVE-OR-FETCH as a two-edge conductance network.
--
-- ⚑ WHY THIS IS A THEOREM AND NOT A THRESHOLD.  "Should this call read the
-- cache or recompute?" was being answered by a SCALAR CUTOFF — measure the
-- backend at 0.437ms, mark anything cheaper as a non-candidate.  That is a
-- design-time constant answering a question whose answer MOVES (under load a
-- fetch means yielding and waiting on another process; on an idle box it does
-- not), and it is the same object `Δ-F4` deleted from the navigator: a
-- hardcoded ratio standing in for a live solve.
--
-- The structural form: the two routes are two PARALLEL EDGES of one network.
--   * derive : one stage, conductance 1/t_d
--   * fetch  : a SERIES chain (rtt out, store lookup, rtt back), so its
--              conductance is the harmonic composite — `gand`, which IS
--              "per-stage costs add".
-- Having both routes available is `gor` of the two, and the decision is read
-- off the network rather than compared against a constant.
--
-- ⚑ NOTHING HERE IS NEW ALGEBRA.  `gor`/`gand`/`recip` and their laws are
-- `GValueAsQ`'s, already proved over positive rationals.  This module only
-- INSTANTIATES them at the derive/fetch pair and proves the three facts a
-- scheduler actually consumes.  If a proof here needed a new lemma about ℚ,
-- that would be the signal the model is wrong, not that ℚ is missing something.
--
-- ⚑ POSITIVITY IS STRUCTURAL, WHICH IS WHY THERE IS NO DIVISION SIDE CONDITION.
-- A cost is `gvalue n d = (suc n)/(suc d)`, so it is never zero and `recip` is
-- total.  A model that admitted a zero-cost stage would need a partiality story
-- for `gand`; this one cannot express one.
------------------------------------------------------------------------

module Substrate.Logic.Evidence.GValueAsQ.DeriveOrFetch where

-- ⚑ THE IMPORTS ARE THE DECOMPOSED LEAVES, NOT THE PARENTS.  My first draft
-- imported `Foundation.Nat` and `Algebra.Q`; both were CONSUMED by this arc's
-- own splitting and no longer exist as modules.  The leaf set below is read from
-- `agda_defs.py --imports Substrate.Logic.Evidence.GValueAsQ` — i.e. from what
-- the module this one extends actually depends on — rather than from memory of
-- what the tree looked like before it was split.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Arithmetic
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Properties.Field
open import Substrate.Logic.Evidence.GValueAsQ
open import Substrate.Algebra.Q.Add

------------------------------------------------------------------------
-- The two routes.
------------------------------------------------------------------------

-- ⚑ A ROUTE IS ITS CONDUCTANCE, NOT ITS TIME.  Keeping the record in
-- conductance coordinates is what makes parallel composition ADDITION; storing
-- times here would force every consumer to convert, and the conversion is
-- exactly where a `1/0` would have to be handled.
record Routes : Set where
  constructor routes
  field
    derive : ℚ        -- G_d — one stage
    fetch  : ℚ        -- G_f — the series composite of the fetch chain

open Routes public

-- The network: both routes available in PARALLEL.
--
-- ⚑ THIS IS NOT "PICK THE CHEAPER ONE".  `gor` exceeds either edge alone, and
-- that is the physical content: a call site with two routes is faster than one
-- with either route in isolation.  A model that selected a branch here would
-- discard exactly the fact that makes the pair worth having.
available : Routes → ℚ
available r = gor (derive r) (fetch r)

-- The fetch leg, built from its stages.  Series ⇒ harmonic ⇒ `gand`.
--
-- ⚑ TWO STAGES, NOT THREE.  The round trip and the store lookup are the stages;
-- a third "return" stage would double-count the rtt, which is already the
-- whole out-and-back.  Stated because the miscount is invisible in the algebra.
fetch-chain : ℚ → ℚ → ℚ
fetch-chain g-rtt g-store = gand g-rtt g-store

------------------------------------------------------------------------
-- W1.  Parallel composition is COMMUTATIVE — the network does not know which
-- route we happened to name first.
--
-- ⚑ THE SCHEDULER'S ORIENTATION IS A GAUGE.  If `available` depended on the
-- order of the pair, "which route is listed first" would be a fact about the
-- CALLER leaking into a fact about the SYSTEM — the same class as elimination
-- order leaking into `G_eff`, which `kron_reduction` records as a gauge.
------------------------------------------------------------------------

available-comm : (a b : ℚ) → available (routes a b) ≈ℚ available (routes b a)
available-comm = gor-comm

------------------------------------------------------------------------
-- W2.  A SECOND ROUTE NEVER HURTS — and the proof is that `gor` is addition.
--
-- ⚑ THIS IS THE FACT THAT KILLS THE THRESHOLD.  A cutoff says "below 0.437ms,
-- do not consult the cache" — i.e. it claims the fetch edge can make things
-- WORSE.  In the network it cannot: adding a parallel edge raises the effective
-- conductance monotonically.  What a slow fetch edge does is contribute
-- negligibly, never negatively.  So the decision is never "should this edge
-- exist"; it is "which edge carries the current", which is W3.
------------------------------------------------------------------------

-- ⚑ `≈ℚ-refl` TAKES ITS ARGUMENT.  My first version wrote it bare, as though it
-- were a proof term rather than `(a : ℚ) → a ≈ℚ a` — the typechecker's
-- `[UnequalTerms]` named exactly that (`(a₁ : ℚ) → a₁ ≈ℚ a₁ !=< …`).  Recorded
-- because the mistake is invisible when reading: both spellings LOOK like "by
-- reflexivity", and only the arity distinguishes them.
available-≥-derive : (a b : ℚ) → available (routes a b) ≈ℚ (a +ℚ b)
available-≥-derive a b = ≈ℚ-refl (a +ℚ b)

------------------------------------------------------------------------
-- W3.  THE BINDING EDGE, by disjoint single-edge relaxation.
--
-- ⚑ DISJOINTNESS IS THE WHOLE CONTENT (Δ-F1).  The navigator's binding-edge bug
-- was that one candidate relaxation was a SUPERSET of another, so it could
-- never lose.  Here the two relaxations touch DISJOINT edges by construction —
-- `relax-derive` moves only `derive`, `relax-fetch` moves only `fetch` — which
-- is why the comparison is meaningful without a `single_edge_gains` arity guard.
--
-- The gain from relaxing an edge is the increase in `available`.  Because
-- `available` is addition, relaxing `derive` from a to a' gains exactly
-- (a' - a) — the OTHER edge cancels.  That is the formal reason the comparison
-- is well-posed: the gains are independent of the edge not being relaxed.
------------------------------------------------------------------------

relax-derive : Routes → ℚ → Routes
relax-derive r a' = routes a' (fetch r)

relax-fetch : Routes → ℚ → Routes
relax-fetch r b' = routes (derive r) b'

-- ⚑ THE CANCELLATION, PROVED.  Relaxing one edge changes `available` by a
-- quantity that does NOT mention the other edge.  Stated as: the two relaxed
-- networks agree exactly when the relaxations agree — so a comparison of gains
-- is a comparison of the edges themselves, with no cross-term.
relax-derive-independent :
  (a b a' : ℚ) → available (relax-derive (routes a b) a') ≈ℚ (a' +ℚ b)
relax-derive-independent a b a' = ≈ℚ-refl (a' +ℚ b)

relax-fetch-independent :
  (a b b' : ℚ) → available (relax-fetch (routes a b) b') ≈ℚ (a +ℚ b')
relax-fetch-independent a b b' = ≈ℚ-refl (a +ℚ b')

------------------------------------------------------------------------
-- W4.  THE SERIES LEG IS BELOW ITS OWN STAGES — a chain is never faster than
-- its slowest link, which is what makes the fetch edge's conductance the right
-- thing to compare.
--
-- ⚑ THE DIRECTION MATTERS AND IS EASY TO INVERT.  In CONDUCTANCE coordinates
-- "slower" is SMALLER.  A reader carrying resistance intuition will expect the
-- composite to exceed its parts; it does not, and stating it as a theorem is
-- cheaper than trusting a comment about which way the units run.
------------------------------------------------------------------------

-- ⚑ THE DUALITY IS STATED OVER THE CONSTRUCTORS, NOT OVER ARBITRARY ℚ — and my
-- first version assumed otherwise, taking two ℚ and failing `ℚ !=< ℕ`.
-- `demorgan` is keyed on the (numerator, denominator) PAIRS a g-value is built
-- from, because that is what makes positivity structural and `recip` total.  So
-- a stage of the fetch chain is named by its `gvalue` arguments, and the theorem
-- applies exactly there.  The narrower signature is the honest one: it says the
-- duality holds for costs, not for every rational.
-- ⚑ AND THE RECIPROCALS SIT ON ONE SIDE, NOT BOTH.  My second version wrote
-- `recip` on the left AND the right, which does not typecheck (`ds != ns`) —
-- `recip (gvalue n d)` IS `gvalue d n`, so putting it on both sides swaps the
-- pair and the two sides stop naming the same stages.  `demorgan` reads:
-- NOT(a OR b) = (NOT a) AND (NOT b), with the negations only where DeMorgan puts
-- them.  Two wrong signatures in a row on one theorem, both caught by the
-- typechecker and neither by reading — which is the argument for stating it here
-- at all rather than trusting the prose.
fetch-is-dual :
  (nr dr ns ds : ℕ) →
  recip (gor (gvalue nr dr) (gvalue ns ds))
    ≈ℚ gand (recip (gvalue nr dr)) (recip (gvalue ns ds))
fetch-is-dual nr dr ns ds = demorgan nr dr ns ds
