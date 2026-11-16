------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.LtMBToLtM
--
-- Defines: ltMᵇ→<M
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.LtMBToLtM where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
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



ltMᵇ→<M : (m n : Mono) → ltMᵇ m n ≡ tt → m <M n
ltMᵇ→<M (mono a b c) (mono d e f) h with triℕ a d | triℕ b e | triℕ c f
... | ltN a<d  | _        | _       = <x a<d
... | gtN _    | _        | _       = ⊥-elim (ff≢tt h)
... | eqN refl | ltN b<e  | _       = <y b<e
... | eqN refl | gtN _    | _       = ⊥-elim (ff≢tt h)
... | eqN refl | eqN refl | ltN c<f = <z c<f
... | eqN refl | eqN refl | gtN _   = ⊥-elim (ff≢tt h)
... | eqN refl | eqN refl | eqN _   = ⊥-elim (ff≢tt h)
