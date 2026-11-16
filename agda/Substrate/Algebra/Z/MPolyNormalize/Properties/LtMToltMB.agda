------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.LtMToltMB
--
-- Defines: <M→ltMᵇ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.LtMToltMB where

open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order
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
open import Substrate.Algebra.Z.MPolyNormalize.Properties.LtToNeq
open import Substrate.Algebra.Z.MPolyNormalize.Properties.LtTrans



<M→ltMᵇ : {m n : Mono} → m <M n → ltMᵇ m n ≡ tt
<M→ltMᵇ (<x {a}{b}{c}{d}{e}{f} a<d) with triℕ a d | triℕ b e | triℕ c f
... | ltN _   | _        | _       = refl
... | eqN a≡d | _        | _       = ⊥-elim (<→≢ a<d a≡d)
... | gtN d<a | _        | _       = ⊥-elim (<-irrefl a (<-trans a<d d<a))
<M→ltMᵇ (<y {a}{b}{c}{e}{f} b<e) with triℕ a a | triℕ b e | triℕ c f
... | ltN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | gtN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | eqN _   | ltN _    | _       = refl
... | eqN _   | eqN b≡e  | _       = ⊥-elim (<→≢ b<e b≡e)
... | eqN _   | gtN e<b  | _       = ⊥-elim (<-irrefl b (<-trans b<e e<b))
<M→ltMᵇ (<z {a}{b}{c}{f} c<f) with triℕ a a | triℕ b b | triℕ c f
... | ltN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | gtN a<a | _        | _       = ⊥-elim (<-irrefl a a<a)
... | eqN _   | ltN b<b  | _       = ⊥-elim (<-irrefl b b<b)
... | eqN _   | gtN b<b  | _       = ⊥-elim (<-irrefl b b<b)
... | eqN _   | eqN _    | ltN _   = refl
... | eqN _   | eqN _    | eqN c≡f = ⊥-elim (<→≢ c<f c≡f)
... | eqN _   | eqN _    | gtN f<c = ⊥-elim (<-irrefl c (<-trans c<f f<c))
