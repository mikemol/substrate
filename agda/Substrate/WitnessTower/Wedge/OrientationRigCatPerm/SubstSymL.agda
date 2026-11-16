------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstSymL
--
-- Defines: subst-symˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstSymL where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



-- a transport followed by its inverse on the underlying set cancels.
subst-symˡ : {n n' : ℕ} (q : n ≡ n') (x : Fin n') →
             subst Fin q (subst Fin (sym q) x) ≡ x
subst-symˡ refl x = refl
