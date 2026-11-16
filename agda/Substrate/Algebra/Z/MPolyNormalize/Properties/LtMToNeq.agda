------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.LtMToNeq
--
-- Defines: <M→≢
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.LtMToNeq where

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



-- irreflexivity by PROJECTING the differing coordinate (m, n stay
-- independent ⇒ no `a = a` self-equation ⇒ --without-K-safe).
<M→≢ : {m n : Mono} → m <M n → ¬ (m ≡ n)
<M→≢ (<x a<d) eq = <→≢ a<d (cong fst₃ eq)
<M→≢ (<y b<e) eq = <→≢ b<e (cong snd₃ eq)
<M→≢ (<z c<f) eq = <→≢ c<f (cong thd₃ eq)
