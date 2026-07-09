{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeBisimLassoK — ⟡extrude-bisim-lasso-k: the GENERAL k-cycle
-- lasso for the coinductive run (278). 278's loop-from-fixed witnessed the k=1 case (a fixed point of step
-- ⟹ the trace ≈ its own tail). This generalizes to any period k: a term with a k-CYCLE (iterate k step t ≡ t,
-- e.g. a self-reducing non-normal term) makes the reduction trace k-PERIODIC — bisimilar to its k-shifted
-- tail (more^ k). This is the run's `loop` at full generality — a bisimulation lasso of any period, witnessed
-- coinductively, with NO total Tm⟦533ef80d⟧ decidable equality (the 6th-spook frame, 277/278).
--
--   more^ k               = shift the trace k steps (iterate the residue `more` k times)
--   more^-run             = more^ k ∘ run-trace ≡ run-trace ∘ iterate k step   (the shift IS k reductions)
--   lasso-k               = iterate k step t ≡ t  ⟹  run-trace t ≈ more^ k (run-trace t)   (the k-lasso)
--   lasso-from-order      = HasFixedOrder step k ⟹ every trace is a k-lasso   (the 275b order corollary)
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: more^ (the k-step shift),
-- more^-run (the shift equals k reductions), lasso-k (the k-cycle lasso), loop-from-fixed-is-lasso-1 (278's
-- lemma is the k=1 case), and lasso-from-order (the HasFixedOrder corollary). The framing ('the run's loop at
-- full generality; no total DecEq') is (prose: 277/278 + Function.Iterate; the map to Wedge.Coalgebra.run's
-- Unfold stays scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeBisimLassoK where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Function.Iterate using (iterate; HasFixedOrder)
open import Substrate.Algebra.R.Trace.SKIShedDuality using () renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeMinimalRun using (step)
open import Substrate.Category.UniversalProperty.ExtrudeBisimRun
  using (RedTrace; run-trace; more; _≈_; ≈-refl)

------------------------------------------------------------------------
-- ① THE k-STEP SHIFT: iterate the residue `more` k times — the trace after k reduction steps.
------------------------------------------------------------------------
more^ : ℕ → RedTrace → RedTrace
more^ zero    s = s
more^ (suc k) s = more (more^ k s)

------------------------------------------------------------------------
-- ② THE SHIFT IS k REDUCTIONS: shifting the trace k steps IS the trace of the k-fold reduct. (more∘run-trace
--    = run-trace∘step definitionally; iterate (suc k) step = step ∘ iterate k step; so cong more threads it.)
------------------------------------------------------------------------
more^-run : (k : ℕ) (t : Tm⟦533ef80d⟧) → more^ k (run-trace t) ≡ run-trace (iterate k step t)
more^-run zero    t = refl
more^-run (suc k) t = cong more (more^-run k t)

------------------------------------------------------------------------
-- ③ THE k-CYCLE LASSO: a term whose k-fold reduct is itself (iterate k step t ≡ t) has a k-PERIODIC trace —
--    bisimilar to its k-shifted tail. The run's `loop` at any period, witnessed by bisimilarity, no decision.
------------------------------------------------------------------------
lasso-k : (t : Tm⟦533ef80d⟧) (k : ℕ) → iterate k step t ≡ t → run-trace t ≈ more^ k (run-trace t)
lasso-k t k cyc =
  subst (λ s → run-trace t ≈ s) (sym shift≡t) (≈-refl (run-trace t))
  where
    shift≡t : more^ k (run-trace t) ≡ run-trace t
    shift≡t = trans (more^-run k t) (cong run-trace cyc)

------------------------------------------------------------------------
-- ④ 278's loop-from-fixed IS the k=1 case (iterate 1 step t = step t; more^ 1 = more): the fixed-point lasso
--    is the tightest cycle, recovered here.
------------------------------------------------------------------------
loop-from-fixed-is-lasso-1 : (t : Tm⟦533ef80d⟧) → step t ≡ t → run-trace t ≈ more^ 1 (run-trace t)
loop-from-fixed-is-lasso-1 t p = lasso-k t 1 p

------------------------------------------------------------------------
-- ⑤ THE ORDER COROLLARY: if step has finite order k on every term (HasFixedOrder, 275b/Function.Iterate),
--    then EVERY trace is a k-lasso — the globally k-periodic case.
------------------------------------------------------------------------
lasso-from-order : (k : ℕ) → HasFixedOrder step k → (t : Tm⟦533ef80d⟧) → run-trace t ≈ more^ k (run-trace t)
lasso-from-order k ord t = lasso-k t k (ord t)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the run's `loop` is a bisimulation lasso of ANY period, coinductive, no
-- total DecEq): 278 grounded the k=1 fixed-point lasso; this generalizes to any k. more^ (①) shifts the
-- trace k steps, more^-run (②) proves the shift IS k reductions (more^ k ∘ run-trace ≡ run-trace ∘ iterate k
-- step — by cong more, since more∘run-trace = run-trace∘step definitionally), and lasso-k (③) witnesses the
-- `loop`: a k-cycle (iterate k step t ≡ t) makes the trace bisimilar to its k-shifted tail (via subst
-- transporting ≈-refl along the cycle). 278's loop-from-fixed is the k=1 case (④), and HasFixedOrder gives
-- the global corollary (⑤, reusing 275b). At no point is total Tm⟦533ef80d⟧-DecEq used — the lasso is a bisimulation
-- (obs≈ + more≈, the per-step observation + deferred residue), the cycle a positive ≡-witness, the period any
-- k. So the extruder's run detects cycles of any length coinductively/bisimilarly — the search AS the
-- reduction strategy, positive, no Turing spook. Chain: 277 (bisimilarity) → 278 (k=1 lasso) → 279 (any-k
-- lasso).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = more^ (the k-shift), more^-run (shift = k reductions), lasso-k
-- (the any-period lasso), loop-from-fixed-is-lasso-1 (278 recovered), lasso-from-order (the HasFixedOrder
-- corollary). SCOPED (reused-in-spirit): the explicit map of {lasso-k found / take-obs prefix / normal-form
-- halt} to Wedge.Coalgebra.run's Unfold (loop/stop/halt) as bisimilarity outcomes (⟡extrude-bisim-unfold);
-- DETECTING the cycle (finding k such that iterate k step t ≡ t) is itself a per-step bisimilar search, not a
-- total decision (⟡extrude-bisim-detect). What's grounded: the run's loop is a bisimulation lasso of any
-- period k, coinductive, positive, no total DecEq.
------------------------------------------------------------------------
