------------------------------------------------------------------------
-- Substrate.Groups.Z2-Coxeter
--
-- ℤ/2ℤ as Coxeter ⟨a | a² = ε⟩. Thin instance of Coxeter.Cyclic 1.
-- Useful theorem: `self-inverse` (every element is its own inverse).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z2-Coxeter where
open import Substrate.Groups.Coxeter.Cyclic.NthPower 1 using (nth-power-identity)
open import Substrate.Groups.Coxeter.Cyclic.Core 1 using (_·_; _≈_)
open import Substrate.Groups.Coxeter.Cyclic.Base 1 using (Gen; gen-≟)

open import Substrate.Foundation.Negation.Dec

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic.Existential 1 using () renaming (Canonical-ex to Canonical-at)
-- ⚑ `InvCanonical.InvInv` DISSOLVED (771283c8) into six leaves (Ⓐ¹²);
-- `inv-inv-canonical-ex` is `InvInvCanonicalEx`'s.
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx 1

open import Substrate.Groups.Coxeter.SameCanonical.SameCanonicalViaGen
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.GenDec

same-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/2-specific theorem: self-inverse. Specialization of the generic
-- nth-power-identity from Coxeter.Cyclic at n = 1
-- (apply-power-suc w 1 = w · w by definition).
------------------------------------------------------------------------

self-inverse : (w : Word Gen) → (w · w) ≈ []
self-inverse = nth-power-identity
