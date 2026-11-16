------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.InsertTSorted
--
-- Defines: insertT-sorted
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.InsertTSorted where

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
open import Substrate.Algebra.Z.MPolyNormalize.Properties.LtMToltMB
open import Substrate.Algebra.Z.MPolyNormalize.Properties.SortedNz
open import Substrate.Algebra.Z.MPolyNormalize.Properties.SortedTail
open import Substrate.Algebra.Z.MPolyNormalize.Properties.SortedMin
open import Substrate.Algebra.Z.MPolyNormalize.Properties.ConsNZSorted
open import Substrate.Algebra.Z.MPolyNormalize.Properties.InsertTMin
open import Substrate.Algebra.Z.MPolyNormalize.Properties.ConsSorted



insertT-sorted : (m : Mono) (k : ℤ) (q : MPoly) →
                 isSortedB q ≡ tt → isSortedB (insertT m k q) ≡ tt
insertT-sorted m k []             sq = consNZ-sorted m k [] sq refl
insertT-sorted m k (term n d ∷ p) sq with triM m n
... | ltM m<n = consNZ-sorted m k (term n d ∷ p) sq (<M→ltMᵇ m<n)
... | eqM≡ refl = consNZ-sorted n (k +ℤ d) p (sorted-tail n d p sq) (sorted-min n d p sq)
... | gtM n<m = cons-sorted n d (insertT m k p)
                  (sorted-nz n d p sq)
                  (insertT-min n m k p (<M→ltMᵇ n<m) (sorted-tail n d p sq) (sorted-min n d p sq))
                  (insertT-sorted m k p (sorted-tail n d p sq))
