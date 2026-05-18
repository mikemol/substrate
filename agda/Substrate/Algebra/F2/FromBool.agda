------------------------------------------------------------------------
-- Substrate.Algebra.F2.FromBool
--
-- N-1 of M-11.dim4.codeword-bridge. Direct Bool ↔ F₂ bijection.
--
-- Foundational primitive for bridging Bool-based ambient types
-- (e.g., Codeword.agda's Bool⁵ Codeword) to F₂-linear structural
-- forms. Minimal subset of M-10A N-1 (the full M-10A would package
-- this as an F₂-Like universal-property instance + derived
-- Foundations.Bijection bundle; here we just provide the direct
-- bijection for use by M-11.dim4.codeword-bridge).
--
-- Convention: false ↔ 𝟘, true ↔ 𝟙. Matches the existing convention
-- in M-12 N-4 (Chirality ↔ F₂ with even ↔ 𝟘, odd ↔ 𝟙) and the
-- canonical sign-character convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.FromBool where

open import Data.Bool using (Bool; true; false)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl)

open import Substrate.Algebra.F2

------------------------------------------------------------------------
-- Forward: Bool → F₂.
------------------------------------------------------------------------

bool→F₂ : Bool → F₂
bool→F₂ true  = 𝟙
bool→F₂ false = 𝟘

------------------------------------------------------------------------
-- Backward: F₂ → Bool.
------------------------------------------------------------------------

F₂→bool : F₂ → Bool
F₂→bool 𝟙 = true
F₂→bool 𝟘 = false

------------------------------------------------------------------------
-- Round-trips.
------------------------------------------------------------------------

bool→F₂→bool : (b : Bool) → F₂→bool (bool→F₂ b) ≡ b
bool→F₂→bool true  = refl
bool→F₂→bool false = refl

F₂→bool→F₂ : (x : F₂) → bool→F₂ (F₂→bool x) ≡ x
F₂→bool→F₂ 𝟙 = refl
F₂→bool→F₂ 𝟘 = refl
