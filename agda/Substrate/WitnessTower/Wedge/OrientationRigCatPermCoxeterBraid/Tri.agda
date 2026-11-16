------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Tri
--
-- Defines: tri
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Tri where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Private


tri : {N : ℕ} (A B : Perm N) (fA fB : Fin N → Fin N) →
      ((x : Fin N) → apply A x ≡ fA x) → ((x : Fin N) → apply B x ≡ fB x) →
      (x : Fin N) → apply (compose A (compose B A)) x ≡ fA (fB (fA x))
tri A B fA fB rA rB x =
  trans (apply-compose A (compose B A) x)
    (trans (cong (apply A) (apply-compose B A x))
      (trans (rA (apply B (apply A x)))
        (cong fA (trans (rB (apply A x)) (cong fB (rA x))))))
