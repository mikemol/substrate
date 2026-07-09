{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeMinimalCoalgebra — ⟡extrude-minimal-coalgebra: the extruder's
-- μ as ITERATION, wiring Foundation.Function.Iterate (the 274-study keystone — the generic nth-iterate,
-- relocated to the base as a pure combinator). 265 grounded the μ CORE as bounded least-cost search (halt =
-- the minimal witness); this expresses μ's UNFOLD as function iteration, giving the wedge-run's halt/loop
-- (264) at the pure-combinator level:
--
--   iterate k step        = k-fold self-application (the extruder's ω/SII machinery = the reduction stream)
--   fixed-preserved       = the HALT: once the μ reaches a fixed point, iterating STAYS there (μ stabilises)
--   cycle-repeats         = the LOOP: a finite-order point (HasFixedOrder) is a reduction CYCLE, repeating
--
-- So the extruder's self-application IS iterate (my Y-of f ⇒* f (Y-of f), 265, is its fixed point — order-∞),
-- and the wedge-coalgebra run's outcomes (264: halt at z / loop on recurrence) are iterate's fixed-point
-- stability / finite-order cycling. The μ is the fixed point of the iterated step — positive, it EXISTS.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: fixed-preserved (a fixed
-- point of the step is stable under iterate — the halt), cycle-repeats (HasFixedOrder ⇒ iterate (m·k) fixes
-- — the loop, = Iterate.HasFixedOrder-multiple), and μ-iterate-fixpoint (the extruder's Y-of fixed point at
-- ⇒*, referenced from 265). The framing ('iterate is the extruder's self-application; halt/loop via iterate')
-- is (prose: the 274 study + 264/265; the full SPPF run wiring stays scoped).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeMinimalCoalgebra where

open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Function.Iterate
  using (iterate; iterate-add; HasFixedOrder; HasFixedOrder-multiple)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (_∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of; Y-fix)

------------------------------------------------------------------------
-- ① THE HALT: the μ fixed point is STABLE under iteration. Once the step-function reaches a fixed point,
--    iterating any number of times stays there — bounded minimisation HALTS at the minimal witness (265).
------------------------------------------------------------------------
fixed-preserved : {A : Set} (f : A → A) (t : A) → f t ≡ t → (k : ℕ) → iterate k f t ≡ t
fixed-preserved f t ft≡t zero    = refl
fixed-preserved f t ft≡t (suc k) = trans (cong f (fixed-preserved f t ft≡t k)) ft≡t

------------------------------------------------------------------------
-- ② THE LOOP: a finite-order point is a reduction CYCLE — HasFixedOrder f k means iterate k f fixes every
--    point, and then any multiple m·k also fixes it (the lasso repeats). This is the wedge-run's `loop`.
------------------------------------------------------------------------
cycle-repeats : {A : Set} (f : A → A) (k m : ℕ) → HasFixedOrder f k →
                (x : A) → iterate (m * k) f x ≡ x
cycle-repeats f k m ord x = HasFixedOrder-multiple f k m ord x

------------------------------------------------------------------------
-- ③ THE EXTRUDER'S SELF-APPLICATION IS ITERATE — its fixed point is the μ (Y-of, 265). At the term level the
--    fixed point is at ⇒* (reduction), not ≡ (iterate's stable point is the ≡-face of the same fixed point).
------------------------------------------------------------------------
μ-iterate-fixpoint : (f : Tm⟦533ef80d⟧) → (Y-of f) ⇒* (f ∙ (Y-of f))
μ-iterate-fixpoint f = Y-fix f

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder's μ is ITERATION; its fixed point (halt) is stable, its cycle
-- (loop) repeats — the wedge-run outcomes at the pure-combinator level, no spook): the 274 study found
-- Foundation.Function.Iterate (the generic nth-iterate) is the extruder's self-application machinery — iterate
-- k step is k-fold application, my Y-of (265) its order-∞ fixed point. This wires it: fixed-preserved (①) is
-- the HALT (the μ fixed point is stable under iteration — bounded minimisation stops at the minimal witness),
-- cycle-repeats (②, = HasFixedOrder-multiple) is the LOOP (a finite-order point cycles), and μ-iterate-
-- fixpoint (③ = Y-fix) is the extruder's fixed point at ⇒*. So the wedge-coalgebra run's halt/loop (264) are
-- iterate's fixed-point-stability / finite-order-cycling — the μ unfold expressed by the reused pure
-- combinator, not hand-rolled. The μ is the fixed point of the iterated step; it EXISTS (Lawvere-positive).
-- No spook. Chain: 264 (run halt/loop) → 265 (μ core, Y-of) → 274 (Iterate reusable) → 275b (μ = iterate).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = fixed-preserved (halt — the fixed point stable under iterate),
-- cycle-repeats (loop — HasFixedOrder-multiple reused), μ-iterate-fixpoint (the Y-of fixed point at ⇒*).
-- SCOPED (reused-in-spirit): the full SPPF run wiring (the actual step : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ as one β-reduction + the
-- shared-forest cycle-closing over Tm⟦533ef80d⟧ — ⟡extrude-minimal-run); the ≡-level term fixed point (needs a Tm⟦533ef80d⟧
-- normal-form stepper). What's grounded: the extruder's μ IS iteration (the reused Function.Iterate), its
-- halt = fixed-point stability, its loop = finite-order cycling, its fixed point = Y-of.
------------------------------------------------------------------------
