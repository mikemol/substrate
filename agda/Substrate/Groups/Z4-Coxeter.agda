------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter
--
-- ℤ/4ℤ as Coxeter ⟨a | a⁴ = ε⟩. Thin instance of Coxeter.Cyclic 3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter where
open import Substrate.Groups.Coxeter.Cyclic.NthPower 3 using (nth-power-identity)
open import Substrate.Groups.Coxeter.Cyclic.Core 3 using (_·_; _≈_; ε)
open import Substrate.Groups.Coxeter.Cyclic.Base 3 using (Gen; gen-≟)

open import Substrate.Foundation.Negation.Dec

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic.Existential 3 using () renaming (Canonical-ex to Canonical-at)
-- ⚑ `InvCanonical.InvInv` DISSOLVED (771283c8) into six leaves (Ⓐ¹²);
-- `inv-inv-canonical-ex` is `InvInvCanonicalEx`'s.
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx 3

open import Substrate.Groups.Coxeter.SameCanonical.SameCanonicalViaGen
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.GenDec

same-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/4-specific theorem: every element to the fourth equals ε.
-- Specialization of the generic nth-power-identity from Coxeter.Cyclic
-- at n = 3 (apply-power-suc w 3 = ((w · w) · w) · w by definition).
------------------------------------------------------------------------

fourth-power-identity : (w : Word Gen) → (((w · w) · w) · w) ≈ ε
fourth-power-identity = nth-power-identity
