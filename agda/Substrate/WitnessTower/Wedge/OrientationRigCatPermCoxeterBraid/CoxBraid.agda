------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.CoxBraid
--
-- Defines: cox-braid
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.CoxBraid where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.TpBraid
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Tri



------------------------------------------------------------------------
-- 4. THE DELIVERABLES: the braid + commute relations at the Perm level.
------------------------------------------------------------------------

-- ◆ip-cox-braid — sᵢ sᵢ₊₁ sᵢ ≡ sᵢ₊₁ sᵢ sᵢ₊₁ (i : Fin n, at grade suc (suc n)).
cox-braid : {n : ℕ} (i : Fin n) →
  compose (sadj (suc n) (inj1 i)) (compose (sadj (suc n) (suc i)) (sadj (suc n) (inj1 i)))
  ≡ compose (sadj (suc n) (suc i)) (compose (sadj (suc n) (inj1 i)) (sadj (suc n) (suc i)))
cox-braid {n} i = apply-injective (λ x →
  trans (tri (sadj (suc n) (inj1 i)) (sadj (suc n) (suc i)) (tp (inj1 i)) (tp (suc i))
             (sadj-realizes (suc n) (inj1 i)) (sadj-realizes (suc n) (suc i)) x)
    (trans (tp-braid i x)
      (sym (tri (sadj (suc n) (suc i)) (sadj (suc n) (inj1 i)) (tp (suc i)) (tp (inj1 i))
                (sadj-realizes (suc n) (suc i)) (sadj-realizes (suc n) (inj1 i)) x))))
