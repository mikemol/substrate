------------------------------------------------------------------------
-- Substrate.Groups.V4.Bijection
--
-- The V₄ carrier and bijection to V4-Coxeter canonical Words.
-- Split from the former monolithic Substrate.Groups.V4 module.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Bijection where

open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.Coxeter.Word using ([]; _∷_; Word)

------------------------------------------------------------------------
-- The carrier.
------------------------------------------------------------------------

data V₄ : Set where
  e α β γ : V₄

------------------------------------------------------------------------
-- Bijection V₄ ↔ Coxeter canonical Words.
------------------------------------------------------------------------

to-c : V₄ → Word C.Gen
to-c e = []
to-c α = C.A ∷ []
to-c β = C.B ∷ []
to-c γ = C.A ∷ C.B ∷ []

to-c-canonical : (x : V₄) → C.Canonical-V4 (to-c x)
to-c-canonical e = C.c-ε
to-c-canonical α = C.c-A
to-c-canonical β = C.c-B
to-c-canonical γ = C.c-AB

from-c-canonical : {w : Word C.Gen} → C.Canonical-V4 w → V₄
from-c-canonical C.c-ε  = e
from-c-canonical C.c-A  = α
from-c-canonical C.c-B  = β
from-c-canonical C.c-AB = γ

from-c : Word C.Gen → V₄
from-c w = from-c-canonical (C.normalize-canonical w)

------------------------------------------------------------------------
-- Round-trips.
------------------------------------------------------------------------

from-to : (x : V₄) → from-c (to-c x) ≡ x
from-to e = refl
from-to α = refl
from-to β = refl
from-to γ = refl

to-from-canonical :
  {w : Word C.Gen} (c : C.Canonical-V4 w) → to-c (from-c-canonical c) ≡ w
to-from-canonical C.c-ε  = refl
to-from-canonical C.c-A  = refl
to-from-canonical C.c-B  = refl
to-from-canonical C.c-AB = refl

------------------------------------------------------------------------
-- Bijection-respecting equality transport on canonical Words.
-- Used as a bridge through the bijection round-trips (referenced by
-- the axiom proofs in V4.Axioms, kept private to this module).
------------------------------------------------------------------------

private
  cong-from-c-canonical :
    {w₁ w₂ : Word C.Gen}
    (c₁ : C.Canonical-V4 w₁) (c₂ : C.Canonical-V4 w₂) →
    w₁ ≡ w₂ → from-c-canonical c₁ ≡ from-c-canonical c₂
  cong-from-c-canonical C.c-ε  C.c-ε  refl = refl
  cong-from-c-canonical C.c-A  C.c-A  refl = refl
  cong-from-c-canonical C.c-B  C.c-B  refl = refl
  cong-from-c-canonical C.c-AB C.c-AB refl = refl
