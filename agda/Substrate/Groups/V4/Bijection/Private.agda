------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection.Private
--
-- Defines: cong-from-c-canonical
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.V4.Bijection; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection.Private where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Bijection.FromCCanonical
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- Bijection-respecting equality transport on canonical Words.
-- Used as a bridge through the bijection round-trips (referenced by
-- the axiom proofs in V4.Axioms, kept private to this module).
------------------------------------------------------------------------

cong-from-c-canonical :
  {w₁ w₂ : Word C.Gen-V4}
  (c₁ : C.Canonical-V4 w₁) (c₂ : C.Canonical-V4 w₂) →
  w₁ ≡ w₂ → from-c-canonical c₁ ≡ from-c-canonical c₂
cong-from-c-canonical C.c-ε  C.c-ε  refl = refl
cong-from-c-canonical C.c-A  C.c-A  refl = refl
cong-from-c-canonical C.c-B  C.c-B  refl = refl
cong-from-c-canonical C.c-AB C.c-AB refl = refl
