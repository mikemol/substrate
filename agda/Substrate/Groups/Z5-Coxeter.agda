------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter
--
-- ℤ/5ℤ as Coxeter ⟨a | a⁵ = ε⟩. Thin instance of Coxeter.Cyclic 4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter where
open import Substrate.Groups.Coxeter.Cyclic.NthPower 4 using (nth-power-identity)
open import Substrate.Groups.Coxeter.Cyclic.Core 4 using (_·_; _≈_; ε)
open import Substrate.Groups.Coxeter.Cyclic.Base 4 using (Gen; gen-≟)

open import Substrate.Foundation.Negation.Dec

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic.Existential 4 using () renaming (Canonical-ex to Canonical-at)
-- ⚑ A FOURTH DISSOLVED PARENT (Ⓐ¹²).  `InvCanonical.InvInv` was split by the
-- same commit (771283c8) into six leaves; the one name this file uses,
-- `inv-inv-canonical-ex`, lives in `InvInvCanonicalEx`.
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx 4

open import Substrate.Groups.Coxeter.SameCanonical.SameCanonicalViaGen
open import Substrate.Foundation.Eq
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.GenDec

same-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/5-specific theorem: every element to the fifth equals ε.
-- Specialization of the generic nth-power-identity from Coxeter.Cyclic
-- at n = 4 (apply-power-suc w 4 = (((w · w) · w) · w) · w by definition).
------------------------------------------------------------------------

fifth-power-identity : (w : Word Gen) → ((((w · w) · w) · w) · w) ≈ ε
fifth-power-identity = nth-power-identity
