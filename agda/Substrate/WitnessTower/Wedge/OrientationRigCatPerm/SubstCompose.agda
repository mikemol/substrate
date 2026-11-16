------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstCompose
--
-- Defines: subst-compose
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstCompose where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



-- transport distributes over composition.
subst-compose : {n n' : ℕ} (q : n ≡ n') (α β : Perm n) →
                subst Perm q (compose α β) ≡ compose (subst Perm q α) (subst Perm q β)
subst-compose refl α β = refl
