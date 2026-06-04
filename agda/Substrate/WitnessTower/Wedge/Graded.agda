------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.Graded
--
-- THE WITNESSTOWER AS A SINGLE GRADED WEDGE-CARRIER. WitnessTower.Wedge.Action
-- founded the rung step as a wedge but only as a PER-RUNG FAMILY (StepWedge n),
-- because the plain Algebra.Wedge.DivStr is un-indexed and could not link the
-- base Perm n to the remainder Fin (suc n) at the same grade n. With
-- Algebra.Wedge.Graded.GradedDivStr (carrier indexed by the grade) that link
-- is structural, and the whole tower is ONE graded wedge-carrier:
--
--   C n     = Perm n              the rung-n permutations
--   R n     = Fin (suc n)         the Lehmer digit / insertion slot
--   recon n = insert-at           the inductive witnessing action
--
-- The factoradic arity suc n (Wedge.Factoradic.tower-quotient) is now |R n| =
-- |Fin (suc n)|, read off the grade — the quotient IS the grade structure.
-- This is the graded form the obstruction note pointed to; the per-rung
-- StepWedge family is recovered as GradedWedge tower-graded n.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.Graded where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.Algebra.Wedge.Graded
  using (GradedDivStr; GradedWedge; recon; gforget; gcell)

------------------------------------------------------------------------
-- 1. The tower as a graded wedge-carrier: C = Perm, R n = Fin (suc n),
--    recon = the inductive insertion action.
------------------------------------------------------------------------

tower-graded : GradedDivStr
tower-graded = record
  { C     = Perm
  ; R     = λ n → Fin (suc n)
  ; recon = λ n σ p → insert-at p σ
  }

-- recon IS the inductive action, definitionally (the Action.agda identity,
-- now living inside the single graded structure).
recon-is-insert-at :
  (n : ℕ) (σ : Perm n) (p : Fin (suc n)) → recon tower-graded n σ p ≡ insert-at p σ
recon-is-insert-at n σ p = refl

------------------------------------------------------------------------
-- 2. The rung step as the graded wedge — the per-rung StepWedge family of
--    Action.agda recovered as ONE GradedWedge over tower-graded.
------------------------------------------------------------------------

tower-step : (n : ℕ) (σ : Perm n) (p : Fin (suc n)) →
             GradedWedge tower-graded n (insert-at p σ) σ
tower-step n σ p = record { rem = p ; wedge-eq = refl }

-- the cell read = the insertion slot (the Lehmer digit at grade n).
tower-cell : (n : ℕ) (σ : Perm n) (p : Fin (suc n)) →
             gcell (tower-step n σ p) ≡ p
tower-cell n σ p = refl

-- the forgetful read recovers the inserted perm.
tower-forget : (n : ℕ) (σ : Perm n) (p : Fin (suc n)) →
               gforget (tower-step n σ p) ≡ insert-at p σ
tower-forget n σ p = refl

------------------------------------------------------------------------
-- 3. The worked seam (rung 0→1): the empty perm inserted at its only slot.
------------------------------------------------------------------------

base-step : GradedWedge tower-graded 0 (insert-at zero []) []
base-step = tower-step 0 [] zero

base-step-forget : gforget base-step ≡ (zero ∷ [])
base-step-forget = refl
