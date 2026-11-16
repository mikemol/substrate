------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeObj
--
-- Defines: freeObj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatUP.Properties.FreeObj where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Probability.MarkovCategory



------------------------------------------------------------------------
-- THE CONSTRUCTION on objects — freeObj: the grade-fold of the target's own
-- units and additive product. This is the object family determined by the
-- generator's image (the ⊗-unit at grade 1), n-fold ⊕-composed.
------------------------------------------------------------------------

freeObj : {Obj : ℕ → Set} {Hom : {i j : ℕ} → Obj i → Obj j → Set}
          (T : GradedRigCat Obj Hom) → (n : ℕ) → Obj n
freeObj T zero    = u (⊕obj T)
freeObj T (suc n) = _∧_ (⊕obj T) (u (⊗obj T)) (freeObj T n)
