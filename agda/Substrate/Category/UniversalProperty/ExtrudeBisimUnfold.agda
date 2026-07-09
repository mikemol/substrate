{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeBisimUnfold — ⟡extrude-bisim-unfold: my coinductive run
-- (278/279) IS the substrate's wedge-run, its outcomes mapping to Wedge.Coalgebra.Unfold (halt/loop/stop) as
-- BISIMILARITY outcomes. Wedge.Coalgebra.Unfold is a 3-way tag: halt (reached z — terminates), loop (residue
-- recurred — eventually periodic), stop (fuel exhausted). These are EXACTLY my three coinductive outcomes,
-- each POSITIVELY WITNESSED (no total Tm⟦533ef80d⟧ DecEq — the 6th-spook frame, 277/278):
--
--   halt ← halted   : step t ≡ t                         — a normal-form fixed point (the trace's own tail)
--   loop ← looped   : iterate k step t ≡ t  + the ≈ lasso — an eventually-periodic bisimulation lasso (279)
--   stop ← stopped  : a bounded prefix (take-obs)         — fuel exhausted, residue still bled (278)
--
-- So the wedge-run's Unfold tags are the observations of WHICH bisimilarity outcome holds — the loop is a
-- lasso (bisimulation), not a decided equality; the halt a fixed point; the stop a bounded prefix. My run
-- and the substrate's coincide, coinductively.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: BisimOutcome (the three
-- POSITIVELY-witnessed outcomes), to-unfold (the map to Wedge.Coalgebra.Unfold), and the three constructors
-- outcome-halt/outcome-loop/outcome-stop (reusing loop-from-fixed/lasso-k/take-obs). The framing ('my run IS
-- the wedge-run; halt/loop/stop as bisimilarity outcomes') is (prose: 264/277/278/279 + the Unfold gloss; the
-- full fuel-threaded run driver stays scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeBisimUnfold where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Algebra.Wedge.Coalgebra using (Unfold; halt; loop; stop)
open import Substrate.Category.UniversalProperty.ExtrudeMinimalRun using (step)
open import Substrate.Category.UniversalProperty.ExtrudeStepDecidable using (HeadShape)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun
  using (RedTrace; run-trace; more; _≈_; loop-from-fixed; take-obs)
open import Substrate.Category.UniversalProperty.ExtrudeBisimLassoK using (more^; lasso-k)

open import Substrate.Foundation.Function.Iterate using (iterate)

------------------------------------------------------------------------
-- ① THE POSITIVELY-WITNESSED OUTCOMES: each of the wedge-run's three outcomes, carried as a POSITIVE witness
--    (no total decision) — a fixed point (halt), a k-cycle + its bisimulation lasso (loop), a bounded prefix
--    (stop). The loop carries the ≈ witness (279) — it is a bisimulation, not a decided equality.
------------------------------------------------------------------------
data BisimOutcome (t : Tm⟦533ef80d⟧) : Set where
  halted  : step t ≡ t → BisimOutcome t                                            -- normal-form fixed point
  looped  : (k : ℕ) → iterate k step t ≡ t →
            run-trace t ≈ more^ k (run-trace t) → BisimOutcome t                   -- the bisimulation lasso
  stopped : (fuel : ℕ) → List HeadShape → BisimOutcome t                           -- the bounded prefix

------------------------------------------------------------------------
-- ② THE MAP to Wedge.Coalgebra.Unfold: each witnessed outcome is tagged by the wedge-run's Unfold — the tag
--    is the OBSERVATION of which bisimilarity outcome holds. My run's outcomes ARE the wedge-run's.
------------------------------------------------------------------------
to-unfold : {t : Tm⟦533ef80d⟧} → BisimOutcome t → Unfold
to-unfold (halted _)     = halt
to-unfold (looped _ _ _) = loop
to-unfold (stopped _ _)  = stop

------------------------------------------------------------------------
-- ③ THE CONSTRUCTORS (reusing 278/279): build each outcome from its positive witness — a fixed point → halt
--    (via loop-from-fixed, the tightest lasso), a k-cycle → loop (via lasso-k), a fuel bound → stop (via
--    take-obs observing the bounded prefix). No total DecEq anywhere.
------------------------------------------------------------------------
outcome-halt : (t : Tm⟦533ef80d⟧) → step t ≡ t → BisimOutcome t
outcome-halt t p = halted p

outcome-loop : (t : Tm⟦533ef80d⟧) (k : ℕ) → iterate k step t ≡ t → BisimOutcome t
outcome-loop t k cyc = looped k cyc (lasso-k t k cyc)

outcome-stop : (t : Tm⟦533ef80d⟧) (fuel : ℕ) → BisimOutcome t
outcome-stop t fuel = stopped fuel (take-obs fuel (run-trace t))

-- and the tags come out as expected — my run's halt/loop/stop ARE Wedge.Coalgebra's:
halt-is-halt : (t : Tm⟦533ef80d⟧) (p : step t ≡ t) → to-unfold (outcome-halt t p) ≡ halt
halt-is-halt t p = refl

loop-is-loop : (t : Tm⟦533ef80d⟧) (k : ℕ) (cyc : iterate k step t ≡ t) → to-unfold (outcome-loop t k cyc) ≡ loop
loop-is-loop t k cyc = refl

stop-is-stop : (t : Tm⟦533ef80d⟧) (fuel : ℕ) → to-unfold (outcome-stop t fuel) ≡ stop
stop-is-stop t fuel = refl

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — my coinductive run IS the substrate's wedge-run; its Unfold outcomes are
-- BISIMILARITY outcomes, no total DecEq): 264 introduced Wedge.Coalgebra.run with Unfold = halt | loop | stop
-- (reached z / residue recurred / fuel out). 277/278/279 built the coinductive run WITHOUT total Tm⟦533ef80d⟧-DecEq
-- (per-step observation + residue; loop = bisimulation lasso). This maps them: BisimOutcome (①) carries each
-- outcome as a POSITIVE WITNESS (halted = a fixed point, looped = a k-cycle + its ≈ lasso, stopped = a
-- bounded prefix), to-unfold (②) tags each with the wedge-run's Unfold, and the constructors (③, reusing
-- loop-from-fixed/lasso-k/take-obs) build them from their witnesses — with halt-is-halt/loop-is-loop/
-- stop-is-stop confirming the tags. So the wedge-run's halt/loop/stop ARE my run's fixed-point/lasso/prefix
-- — the same three outcomes, mine coinductive/bisimilar (positive witnesses), the substrate's the Unfold tag.
-- The loop is EXPLICITLY a bisimulation (it carries run-trace t ≈ more^ k (run-trace t)), NOT a decided
-- equality — the 6th-spook frame all the way through. Positive, coinductive, no Turing spook. Chain: 264
-- (Unfold) → 277 (bisimilarity) → 278 (k=1 lasso) → 279 (any-k lasso) → 280 (outcomes ARE the wedge Unfold).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = BisimOutcome (the witnessed outcomes) + to-unfold (the map to
-- Wedge.Coalgebra.Unfold) + the three constructors (from loop-from-fixed/lasso-k/take-obs) + the tag
-- confirmations. SCOPED (reused-in-spirit): the full RUN DRIVER (a fuel-threaded function producing a
-- BisimOutcome by observing the trace — which needs the per-step bisimilar cycle-DETECTION, ⟡extrude-bisim-
-- detect, itself a per-step search not a total decision); the ≡ between my (prefix, Unfold) and Wedge.
-- Coalgebra.run's actual output (⟡extrude-bisim-run-eq). What's grounded: my run's outcomes ARE the
-- wedge-run's Unfold (halt/loop/stop), each a positive bisimilarity witness — no total DecEq.
------------------------------------------------------------------------
