------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.ToCCanonical
--
-- Defines: to-c-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.ToCCanonical where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Bijection.ToC



to-c-canonical : (x : V₄) → C.Canonical-V4 (to-c x)
to-c-canonical e = C.c-ε
to-c-canonical α = C.c-A
to-c-canonical β = C.c-B
to-c-canonical γ = C.c-AB
