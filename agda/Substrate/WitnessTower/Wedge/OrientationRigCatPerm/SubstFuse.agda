------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFuse
--
-- Defines: subst-fuse
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFuse where

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



-- transport fusion (P explicit — the carrier is not inferable from `P x`).
subst-fuse : {A : Set} (P : A → Set) {x y z : A}
             (p : x ≡ y) (q : y ≡ z) (w : P x) →
             subst P q (subst P p w) ≡ subst P (trans p q) w
subst-fuse P refl q w = refl
