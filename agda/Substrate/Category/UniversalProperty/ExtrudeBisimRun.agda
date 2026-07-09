{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeBisimRun — ⟡extrude-bisim-run: the COINDUCTIVE extruder run,
-- cashing out the 277 reground (the 6th D-no-classical-spook). The run does NOT use total Tm⟦533ef80d⟧ decidable
-- equality (the Turing/total-space spook); it operates BISIMILARLY: at each step it takes the cheapest
-- decidable observation (head-shape, 277) and BLEEDS THE RESIDUE (the next state via step, 276a) forward —
-- a coinductive stream. Then:
--   loop  = the residues COINCIDE up to bisimilarity (_≈_)   — a lasso, NOT a total decision
--   stop  = the residue is still being bled (a bounded prefix observed, tail deferred)
--   halt  = a fixed point of step (a normal form) — the tightest lasso (the trace is its own tail)
--
-- This is the Bisim._~_ pattern (head~ : a within-step ≡ observation + tail~ : the residue, coinductively
-- deferred) at the extruder's reduction stream. No total DecEq — the search IS the reduction strategy.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: RedTrace (the coinductive
-- reduction stream), run-trace (unfold a Tm⟦533ef80d⟧ via step, observing head-shape), _≈_ (bisimilarity — obs≈ +
-- more≈), ≈-refl, loop-from-fixed (step t ≡ t ⟹ run-trace t ≈ more (run-trace t) — the fixed-point lasso),
-- and take-obs (the bounded prefix = the stop observation). The framing ('loop = bisimulation, stop = residue
-- bled, no total DecEq') is (prose: 277 + Bisim._~_; the general k-cycle lasso + the wiring to
-- Wedge.Coalgebra.run's Unfold stay scoped, coinductive).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeBisimRun where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; subst; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeMinimalRun using (step)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape; head-shape)

------------------------------------------------------------------------
-- ① THE COINDUCTIVE REDUCTION STREAM: at each step, the within-step OBSERVATION (obs = head-shape) and the
--    RESIDUE (more = the reduction of the next state). Never the whole term at once — head decided, tail bled.
------------------------------------------------------------------------
record RedTrace : Set where
  coinductive
  field
    obs  : HeadShape       -- the within-step decidable observation (277 — the cheapest bijective piece)
    more : RedTrace        -- the residue: the reduction of the next state (bled forward)
open RedTrace public

-- unfold a term into its reduction stream: observe head-shape, bleed step (guarded corecursion):
run-trace : Tm⟦533ef80d⟧ → RedTrace
obs  (run-trace t) = head-shape t
more (run-trace t) = run-trace (step t)

------------------------------------------------------------------------
-- ② BISIMILARITY (the Bisim._~_ pattern): the observations match (obs≈, the per-step decidable piece) and
--    the residues coincide (more≈, coinductively deferred). This is the coinductive "equality" — no total
--    decision, an observation + a deferred residue.
------------------------------------------------------------------------
record _≈_ (s t : RedTrace) : Set where
  coinductive
  field
    obs≈  : obs s ≡ obs t        -- the within-step observations agree (decidable, cheap)
    more≈ : more s ≈ more t      -- the residues coincide (deferred to the next step)
open _≈_ public

≈-refl : (s : RedTrace) → s ≈ s
obs≈  (≈-refl s) = refl
more≈ (≈-refl s) = ≈-refl (more s)

------------------------------------------------------------------------
-- ③ THE LOOP as a BISIMULATION LASSO: a fixed point of step (a normal form / a self-reducing term) makes the
--    trace BISIMILAR TO ITS OWN TAIL — the residue coincides with the trace itself. This is the run's `loop`
--    (a residue recurred), witnessed by bisimilarity, NOT by a total equality decision.
------------------------------------------------------------------------
loop-from-fixed : (t : Tm⟦533ef80d⟧) → step t ≡ t → run-trace t ≈ more (run-trace t)
loop-from-fixed t p = subst (λ s → run-trace t ≈ run-trace s) (sym p) (≈-refl (run-trace t))
-- more (run-trace t) = run-trace (step t) (definitional); step t ≡ t transports ≈-refl to the lasso.

------------------------------------------------------------------------
-- ④ THE STOP as a BOUNDED PREFIX: observe only k steps (a finite list of observations), the tail DEFERRED —
--    the run's `stop` (fuel exhausted, residue still bled, no lasso found yet). A bounded, honest observation.
------------------------------------------------------------------------
take-obs : ℕ → RedTrace → List HeadShape
take-obs zero    s = []
take-obs (suc k) s = obs s ∷ take-obs k (more s)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder's run is COINDUCTIVE/BISIMILAR: per-step decidable observation
-- + residue bled forward; loop = bisimulation, stop = bounded prefix; NO total Tm⟦533ef80d⟧ DecEq — the Turing spook
-- dissolved, 6th time): the 277 reground said the cycle-test is bisimilarity (Bisim._~_), not total DecEq.
-- This wires it into an actual run: RedTrace (①) is the coinductive reduction stream — obs = head-shape (the
-- within-step decidable observation, 277) + more = run-trace ∘ step (the residue, 276a, bled forward). _≈_
-- (②) is bisimilarity (obs≈ the cheap observation + more≈ the deferred residue — the Bisim.head~/tail~
-- pattern). loop-from-fixed (③) witnesses the `loop` as a BISIMULATION LASSO (a fixed point of step ⟹ the
-- trace is bisimilar to its own tail — the residue coincides), and take-obs (④) the `stop` as a BOUNDED
-- PREFIX (k observations, tail deferred). At no point is total Tm⟦533ef80d⟧-DecEq needed — each step decides only the
-- cheap head (head-shape) and bleeds the subterm residue; the outcomes (loop/stop/halt) emerge from
-- bisimilarity and finite observation, the search AS the reduction strategy. Positive, coinductive, confluent
-- — no spook. Chain: 264 (run halt/loop/stop) → 277 (cycle-test = per-step obs + residue) → 278 (the
-- coinductive run: loop = bisimulation, stop = bounded prefix).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = RedTrace + run-trace (the coinductive run), _≈_ + ≈-refl
-- (bisimilarity), loop-from-fixed (the fixed-point lasso), take-obs (the bounded-prefix stop). SCOPED
-- (reused-in-spirit, coinductive — NOT a total decision): the GENERAL k-cycle lasso (iterate k step t ≡ t,
-- k>1 ⟹ run-trace t ≈ the k-shifted tail — ⟡extrude-bisim-lasso-k); the explicit map to
-- Wedge.Coalgebra.run's Unfold (halt/loop/stop) as bisimilarity outcomes (⟡extrude-bisim-unfold). What's
-- grounded: the extruder's run is coinductive/bisimilar — per-step decidable observation + residue bled
-- forward, loop = bisimulation, stop = bounded prefix — the weaker-than-total form, no Turing spook.
------------------------------------------------------------------------
