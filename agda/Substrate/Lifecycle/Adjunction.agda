------------------------------------------------------------------------
-- Substrate.Lifecycle.Adjunction
--
-- Defines: Orientation, forget-eval, forget-eval-is-step, term,
--          counit-defect-is-orientation, lifecycle-triangle, orientation-of
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Adjunction where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Wedge.Graded using (gforget)
open import Substrate.Algebra.Wedge.Graded.Adjunction using (geval; gTerm; gtriangle; geval-eq)
open import Substrate.Lifecycle.Path
open import Substrate.Lifecycle.Graded
open import Substrate.Foundation.Eq


------------------------------------------------------------------------
-- FREE ⊣ FORGETFUL AT THE LIFECYCLE — `Algebra.Wedge.Graded.Adjunction`
-- instantiated at `lifecycle-graded`, mirroring `WitnessTower.Wedge.Adjunction`.
--
-- ⚑ THE ORIENTATION IS THE RESIDUE IS THE COUNIT-DEFECT. `a ≡ recon b r`
-- says the order-INsensitive base reconstructs `a` only WITH `r`. Forgetting
-- `r` gives the nerve (order-insensitive, everything commutes); the wedge
-- hands it back. For a lifecycle that datum is exactly WHICH ACTOR RELEASED
-- WHAT, WHEN — the ordering a scalar floor destroys.
--
-- ⚑ AND THIS IS WHY THE STORE'S FLOOR COULD REPORT A COUNT AND NEVER A
-- REASON. `min(feed)` over a registry is the FORGETFUL side: it evaluates
-- the decomposition and drops the orientation. The free side keeps it, so
-- "which constraint holds this row, and at which boundary" is answerable by
-- construction rather than by a `CASE` expression someone remembered to write.
------------------------------------------------------------------------

Orientation : ℕ → Set
Orientation n = Fin (suc n)

-- FORGETFUL (geval = recon): rebuild the grade-(n+1) path from a base and an
-- orientation. At the lifecycle this IS the cons.
forget-eval : (n : ℕ) → LifecyclePath n → Orientation n → LifecyclePath (suc n)
forget-eval = geval lifecycle-graded

forget-eval-is-step : (n : ℕ) (p : LifecyclePath n) (r : Orientation n) →
                      forget-eval n p r ≡ p ◂ r
forget-eval-is-step n p r = refl

-- FREE (the hom-set): a decomposition of a grade-(n+1) path against its base.
term : (n : ℕ) → LifecyclePath (suc n) → LifecyclePath n → Set
term = gTerm lifecycle-graded

-- THE COUNIT-DEFECT IS THE ORIENTATION.
counit-defect-is-orientation : (n : ℕ) (p : LifecyclePath n) (r : Orientation n) →
                               geval lifecycle-graded n p r ≡ p ◂ r
counit-defect-is-orientation n p r = geval-eq (lifecycle-step n p r)

-- the triangle law: forget-then-rebuild recovers the path.
lifecycle-triangle : (n : ℕ) (p : LifecyclePath n) (r : Orientation n) →
                     gforget (lifecycle-step n p r) ≡ p ◂ r
lifecycle-triangle n p r = gtriangle (lifecycle-step n p r)

-- the orientation extracted from a decomposition IS its residue.
orientation-of : (n : ℕ) {a : LifecyclePath (suc n)} {b : LifecyclePath n} →
                 term n a b → Orientation n
orientation-of n (r , _) = r
