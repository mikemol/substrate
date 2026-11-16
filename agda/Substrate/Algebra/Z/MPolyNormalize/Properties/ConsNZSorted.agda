------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.ConsNZSorted
--
-- Defines: consNZ-sorted
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.ConsNZSorted where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Z.DecInt
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.ZeroInt
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
open import Substrate.Algebra.Z.MPolyNormalize.Properties.NzBTt



------------------------------------------------------------------------
-- normalize produces a sorted list.
------------------------------------------------------------------------

consNZ-sorted : (m : Mono) (k : ℤ) (q : MPoly) →
                isSortedB q ≡ tt → minB m q ≡ tt → isSortedB (consNZ m k q) ≡ tt
consNZ-sorted m k []             sq mq with k ≟ℤ 0ℤ
... | yes _  = refl
... | no k≢0 = nzB-tt k≢0
consNZ-sorted m k (term n d ∷ q') sq mq with k ≟ℤ 0ℤ
... | yes _  = sq
... | no k≢0 = and-tt (nzB-tt k≢0) (and-tt mq sq)
