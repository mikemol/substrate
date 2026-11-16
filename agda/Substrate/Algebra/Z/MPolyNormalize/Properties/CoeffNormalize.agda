------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffNormalize
--
-- Defines: coeff-normalize
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffNormalize where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Foundation.List
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.ZeroInt
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Properties.Add
open import Substrate.Algebra.Z.JacobianResidue
open import Substrate.Algebra.Quotient.ApproxcanonicalEq
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.CanonicalEqApprox
open import Substrate.Algebra.Quotient.IdemCanonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Algebra.Z.MPolyNormalize
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffCons
open import Substrate.Algebra.Z.MPolyNormalize.Properties.CoeffInsertT



coeff-normalize : (j : Mono) (p : MPoly) → coeff j (normalize p) ≡ coeff j p
coeff-normalize j []             = refl
coeff-normalize j (term m k ∷ p) =
  trans (coeff-insertT j m k (normalize p))
  (trans (coeff-cons j m k (normalize p))
  (trans step (sym (coeff-cons j m k p))))
  where
    step : Bcase (eqM j m) (k +ℤ coeff j (normalize p)) (coeff j (normalize p))
         ≡ Bcase (eqM j m) (k +ℤ coeff j p)            (coeff j p)
    step with eqM j m
    ... | tt = cong (k +ℤ_) (coeff-normalize j p)
    ... | ff = coeff-normalize j p
