------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.NormalizeFixed
--
-- Defines: normalize-fixed
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.NormalizeFixed where

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
open import Substrate.Algebra.Z.MPolyNormalize.Properties.SortedNz
open import Substrate.Algebra.Z.MPolyNormalize.Properties.SortedTail
open import Substrate.Algebra.Z.MPolyNormalize.Properties.SortedMin
open import Substrate.Algebra.Z.MPolyNormalize.Properties.InsertTPrepend



normalize-fixed : (q : MPoly) → isSortedB q ≡ tt → normalize q ≡ q
normalize-fixed []             _  = refl
normalize-fixed (term m k ∷ q') sq =
  trans (cong (insertT m k) (normalize-fixed q' (sorted-tail m k q' sq)))
        (insertT-prepend m k q' (sorted-nz m k q' sq) (sorted-min m k q' sq))
