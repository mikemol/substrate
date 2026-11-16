------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.TpCommute
--
-- Defines: tp-commute
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.TpCommute where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Sep



-- the disjoint-commute identity on indices (5 clauses: 3 at sep0, 2 at sepS).
tp-commute : {m : ℕ} {a b : Fin m} → Sep a b → (x : Fin (suc m)) →
             tp a (tp b x) ≡ tp b (tp a x)
tp-commute (sep0 k) zero          = refl
tp-commute (sep0 k) (suc zero)    = refl
tp-commute (sep0 k) (suc (suc x)) = refl
tp-commute (sepS s) zero          = refl
tp-commute (sepS s) (suc x)       = cong suc (tp-commute s x)
