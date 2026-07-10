------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.Adjunction
--
-- THE ADJUNCTION IS THE WEDGE. Algebra.Wedge.Graded.Adjunction's Free ⊣ Forgetful
-- instantiated at the generative witness tower: C = Perm, R = Fin ∘ suc,
-- G = tower-graded (WitnessTower.Wedge.Graded).
--
--   FORGETFUL  geval = recon : (base perm at grade n) + (orientation r) ↦ the
--     grade-(n+1) perm (= insert-at r σ). It evaluates a decomposition.
--   FREE       package a perm with its decomposition against a base (the graded
--     wedge = the term Σ r. a ≡ recon b r).
--
-- The residue r : R n = Fin (suc n) is the ORIENTATION — the Lehmer digit, the
-- permutohedron edge, the Coxeter-word step. It is the adjunction's COUNIT-DEFECT:
-- `a ≡ recon b r` says the order-INsensitive base b reconstructs a only WITH r.
-- Forgetting r gives the nerve (order-insensitive, where the simplicial identities
-- hold, WitnessTower.Wedge.Simplicial §1); the wedge hands r back. So the "wedge of
-- distinction" between the base and the built perm IS the counit-defect, by
-- construction — the relative orientation of the two towers.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.Adjunction where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.Algebra.Wedge.Graded using (gforget)
open import Substrate.Algebra.Wedge.Graded.Adjunction using (geval; gTerm; gtriangle; geval-eq)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded; tower-step)

------------------------------------------------------------------------
-- 1. The orientation = the residue = R n. The datum the forgetful side drops.
------------------------------------------------------------------------

Orientation : ℕ → Set
Orientation n = Fin (suc n)

------------------------------------------------------------------------
-- 2. FORGETFUL (geval = recon): reconstruct the grade-(n+1) perm from a base and
--    an orientation. At the tower this IS insert-at.
------------------------------------------------------------------------

forget-eval : (n : ℕ) → Perm n → Orientation n → Perm (suc n)
forget-eval = geval tower-graded

forget-eval-is-insert-at : (n : ℕ) (σ : Perm n) (r : Orientation n) →
                           forget-eval n σ r ≡ insert-at r σ
forget-eval-is-insert-at n σ r = refl

------------------------------------------------------------------------
-- 3. FREE (the hom-set): a decomposition of a grade-(n+1) perm against a base —
--    an orientation r with a ≡ recon b r. This is the graded wedge (the unit).
------------------------------------------------------------------------

term : (n : ℕ) → Perm (suc n) → Perm n → Set
term = gTerm tower-graded

------------------------------------------------------------------------
-- 4. THE COUNIT-DEFECT IS THE ORIENTATION. Reconstructing the base with the
--    recorded orientation recovers the perm (geval-eq); the defect you must supply
--    is exactly r. So the wedge of distinction = the orientation, by construction.
------------------------------------------------------------------------

counit-defect-is-orientation : (n : ℕ) (σ : Perm n) (r : Orientation n) →
                               geval tower-graded n σ r ≡ insert-at r σ
counit-defect-is-orientation n σ r = geval-eq (tower-step n σ r)

-- the triangle law at the tower: forget-then-rebuild recovers the perm.
tower-triangle : (n : ℕ) (σ : Perm n) (r : Orientation n) →
                 gforget (tower-step n σ r) ≡ insert-at r σ
tower-triangle n σ r = gtriangle (tower-step n σ r)

-- and the orientation extracted from a decomposition IS its residue — the
-- relative orientation of that grade step.
orientation-of : (n : ℕ) {a : Perm (suc n)} {b : Perm n} →
                 term n a b → Orientation n
orientation-of n (r , _) = r
