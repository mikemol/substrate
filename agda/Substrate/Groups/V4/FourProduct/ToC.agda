------------------------------------------------------------------------
-- Substrate.Groups.V4.FourProduct.ToC
--
-- Defines: to-c-·
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.FourProduct; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.FourProduct.ToC where

open import Substrate.Groups.V4.Operations
open import Substrate.Groups.V4.Bijection.ToC
open import Substrate.Groups.V4.Bijection.ToCCanonical
open import Substrate.Groups.V4.Bijection.ToFromCanonical
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bundle
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Neq
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Groups.V4.FourProduct.Private


to-c-· : (a b : V₄) → to-c (a ·₄ b) ≡ to-c a C.· to-c b
to-c-· a b =
  trans (to-from-canonical
          (C.normalize-canonical (to-c a C.· to-c b)))
        (C.normalize-idem (to-c a ++ to-c b))
