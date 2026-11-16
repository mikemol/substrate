------------------------------------------------------------------------
-- Substrate.Groups.V4.FourProduct.NeqTo
--
-- Defines: ≢→≉
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.FourProduct; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.FourProduct.NeqTo where

open import Substrate.Groups.V4.Operations
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
open import Substrate.Groups.V4.FourProduct.ToCInjective


≢→≉ : {x y : V₄} → x ≢ y → to-c x C.≉ to-c y
≢→≉ {x} {y} ineq normalize-eq =
  ineq (to-c-injective x y
          (sym-trans (C.canonical-is-fixed-V4 (to-c-canonical x))
                     (trans normalize-eq
                            (C.canonical-is-fixed-V4 (to-c-canonical y)))))

-- Bridge: to-c (a ·₄ b) ≡ to-c a C.· to-c b.
