------------------------------------------------------------------------
-- Substrate.Groups.V4.FourProduct.Private
--
-- Defines: Private
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.FourProduct; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.FourProduct.Private where

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


------------------------------------------------------------------------
-- Bijection injectivity + inequality lift.
------------------------------------------------------------------------

-- to-c is injective: distinct V₄ ctors map to distinct canonical Words.
