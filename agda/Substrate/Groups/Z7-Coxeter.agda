------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter
--
-- ℤ/7ℤ as Coxeter ⟨a | a⁷ = ε⟩. Thin instance of Coxeter.Cyclic 6.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter where
open import Substrate.Groups.Coxeter.Cyclic.NthPower 6 using (nth-power-identity)
open import Substrate.Groups.Coxeter.Cyclic.Core 6 using (_·_; _≈_; ε)
open import Substrate.Groups.Coxeter.Cyclic.Base 6 using (Gen; gen-≟)

open import Substrate.Foundation.Negation.Dec

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic.Existential 6 using () renaming (Canonical-ex to Canonical-at)
-- ⚑ `InvCanonical.InvInv` DISSOLVED (771283c8) into six leaves (Ⓐ¹²);
-- `inv-inv-canonical-ex` is `InvInvCanonicalEx`'s.
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx 6

open import Substrate.Groups.Coxeter.SameCanonical.SameCanonicalViaGen
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.GenDec

same-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/7-specific theorem: every element to the seventh equals ε.
-- Specialization of the generic nth-power-identity from Coxeter.Cyclic
-- at n = 6 (apply-power-suc w 6 = ((((((w·w)·w)·w)·w)·w)·w) by definition).
------------------------------------------------------------------------

seventh-power-identity : (w : Word Gen) → ((((((w · w) · w) · w) · w) · w) · w) ≈ ε
seventh-power-identity = nth-power-identity
