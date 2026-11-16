------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.ToC
--
-- Defines: to-c
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.ToC where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bijection.V4



------------------------------------------------------------------------
-- Bijection V₄ ↔ Coxeter canonical Words.
------------------------------------------------------------------------

to-c : V₄ → Word C.Gen-V4
to-c e = []
to-c α = C.A ∷ []
to-c β = C.B ∷ []
to-c γ = C.A ∷ C.B ∷ []
