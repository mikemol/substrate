------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.CoxCommute
--
-- Defines: cox-commute
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.CoxCommute where

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
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Sep
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.TpCommute
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Duo
open import Substrate.Lifecycle.Fragment.Delim



-- ◆ip-cox-commute — sₐ s_b ≡ s_b sₐ for disjoint (Sep a b) positions.
cox-commute : {n : ℕ} {a b : Fin (suc n)} → Sep a b →
  compose (sadj (suc n) a) (sadj (suc n) b) ≡ compose (sadj (suc n) b) (sadj (suc n) a)
cox-commute {n} {a} {b} sep = apply-injective (λ x →
  trans (duo (sadj (suc n) a) (sadj (suc n) b) (tp a) (tp b)
             (sadj-realizes (suc n) a) (sadj-realizes (suc n) b) x)
    (trans (tp-commute sep x)
      (sym (duo (sadj (suc n) b) (sadj (suc n) a) (tp b) (tp a)
                (sadj-realizes (suc n) b) (sadj-realizes (suc n) a) x))))
