------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Chirality.Structural
--
-- N-4 of the M-12 DBE plan. The bijection
--   Chirality ↔ F₂
-- bundled as a `Bijection` (universal-property record).
--
-- Chirality is the bare 2-ctor `even / odd` enumeration in
-- V4Signature.agda; it represents the Z/2 parity of the underlying
-- S₃ permutation (even = A₄ coset, odd = S₄ \ A₄ coset).
--
-- F₂ is the structural 2-element field from M-1 (Substrate.Algebra.F2).
-- All round-trips close by `refl`.
--
-- Structural identification (per
-- [[feedback_ordering_is_chirality_choice]] — yes, this IS the
-- chirality choice the feedback names):
--   even ↔ 𝟘   (identity / trivial coset)
--   odd  ↔ 𝟙   (sign-flip / nontrivial coset)
--
-- This matches the standard "sign character" convention (sign(σ) = 0
-- for even, 1 for odd in F₂, equivalently +1/-1 in {±1}).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Chirality.Structural where

open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Foundations.Bijection
open import Substrate.Algebra.F2
open import Substrate.Cocycles.V4Signature using (Chirality; even; odd)

------------------------------------------------------------------------
-- Forward: Chirality → F₂.
------------------------------------------------------------------------

Chirality→F₂ : Chirality → F₂
Chirality→F₂ even = 𝟘
Chirality→F₂ odd  = 𝟙

------------------------------------------------------------------------
-- Backward: F₂ → Chirality.
------------------------------------------------------------------------

F₂→Chirality : F₂ → Chirality
F₂→Chirality 𝟘 = even
F₂→Chirality 𝟙 = odd

------------------------------------------------------------------------
-- Round-trips.
------------------------------------------------------------------------

to-from-Chirality : (x : F₂) → Chirality→F₂ (F₂→Chirality x) ≡ x
to-from-Chirality 𝟘 = refl
to-from-Chirality 𝟙 = refl

from-to-Chirality : (c : Chirality) → F₂→Chirality (Chirality→F₂ c) ≡ c
from-to-Chirality even = refl
from-to-Chirality odd  = refl

------------------------------------------------------------------------
-- The Bijection bundle.
------------------------------------------------------------------------

Chirality↔F₂ : Bijection Chirality F₂
Chirality↔F₂ = record
  { to      = Chirality→F₂
  ; from    = F₂→Chirality
  ; to-from = to-from-Chirality
  ; from-to = from-to-Chirality
  }
