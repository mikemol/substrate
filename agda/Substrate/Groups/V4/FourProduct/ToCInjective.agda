------------------------------------------------------------------------
-- Substrate.Groups.V4.FourProduct.ToCInjective
--
-- Defines: to-c-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.FourProduct; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.FourProduct.ToCInjective where

open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.ToCCanonical
open import Substrate.Groups.V4.Bijection.ToFromCanonical
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.V4.Bundle
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Groups.V4.FourProduct.Private


to-c-injective : (x y : V₄) → to-c x ≡ to-c y → x ≡ y
to-c-injective e e _  = refl
to-c-injective α α _  = refl
to-c-injective β β _  = refl
to-c-injective γ γ _  = refl
to-c-injective e α ()
to-c-injective e β ()
to-c-injective e γ ()
to-c-injective α e ()
to-c-injective α β ()
to-c-injective α γ ()
to-c-injective β e ()
to-c-injective β α ()
to-c-injective β γ ()
to-c-injective γ e ()
to-c-injective γ α ()
to-c-injective γ β ()

-- Lift V₄ inequality to canonical-Word inequality via to-c.
