------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4ToPairing
--
-- V₄ → Pairing as a partial function: V₄'s α/β/γ each induce an
-- axis-pair partition; the identity element e has no axis-swap, so
-- the e-case is structurally absent. We expose the absence
-- first-class as `e-pair : ⊥ → Pairing` so the cross-type stem-match
-- has a target.
--
-- The detector's cross-type signal V₄→Pairing (3-of-4 fanout,
-- missing 'e-pair') is structurally true: Pairing = V₄/⟨e⟩ as a
-- set quotient.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4ToPairing where

open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Eq    using (_≡_; refl)
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
open import Substrate.Cocycles.V4Signature.Pairing.Type
  using (Pairing; α-pair; β-pair; γ-pair)

_≢_ : V₄ → V₄ → Set
v ≢ w = (v ≡ w) → ⊥

V₄→Pairing : (v : V₄) → v ≢ e → Pairing
V₄→Pairing e v≢e = ⊥-elim (v≢e refl)
V₄→Pairing α _   = α-pair
V₄→Pairing β _   = β-pair
V₄→Pairing γ _   = γ-pair

e-pair : ⊥ → Pairing
e-pair ()
