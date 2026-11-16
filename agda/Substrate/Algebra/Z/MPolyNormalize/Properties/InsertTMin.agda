------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.InsertTMin
--
-- Defines: insertT-min
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.InsertTMin where

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
open import Substrate.Algebra.Z.MPolyNormalize.Properties.SortedMin
open import Substrate.Algebra.Z.MPolyNormalize.Properties.MinBTrans
open import Substrate.Algebra.Z.MPolyNormalize.Properties.ConsNZMin



insertT-min : (n m : Mono) (k : ℤ) (q : MPoly) →
              ltMᵇ n m ≡ tt → isSortedB q ≡ tt → minB n q ≡ tt →
              minB n (insertT m k q) ≡ tt
insertT-min n m k []             n<m sq n<q = consNZ-min n m k [] n<m refl
insertT-min n m k (term o e ∷ q') n<m sq n<q with triM m o
... | ltM _   = consNZ-min n m k (term o e ∷ q') n<m n<q
... | eqM≡ refl = consNZ-min n m (k +ℤ e) q' n<q (minB-trans n m q' n<q (sorted-min m e q' sq))
... | gtM _   = n<q
