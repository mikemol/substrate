------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize.Properties.LtMTrans
--
-- Defines: <M-trans
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.MPolyNormalize.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.MPolyNormalize.Properties.LtMTrans where

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
open import Substrate.Algebra.Z.MPolyNormalize.Properties.LtTrans



<M-trans : {m n o : Mono} → m <M n → n <M o → m <M o
<M-trans (<x a<d) (<x d<h) = <x (<-trans a<d d<h)
<M-trans (<x a<d) (<y _)   = <x a<d
<M-trans (<x a<d) (<z _)   = <x a<d
<M-trans (<y _)   (<x a<h) = <x a<h
<M-trans (<y b<e) (<y e<i) = <y (<-trans b<e e<i)
<M-trans (<y b<e) (<z _)   = <y b<e
<M-trans (<z _)   (<x a<h) = <x a<h
<M-trans (<z _)   (<y b<i) = <y b<i
<M-trans (<z c<g) (<z g<j) = <z (<-trans c<g g<j)
