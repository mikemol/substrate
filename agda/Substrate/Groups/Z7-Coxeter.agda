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

open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic.Existential 6 using () renaming (Canonical-ex to Canonical-at; insert-canonical-ex to insert-canonical; inv-canonical-ex to inv-canonical; canonical-cover-ex to canonical-cover-fin)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv 6 using () renaming (inv-inv-canonical-ex to inv-inv-canonical)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left 6 using () renaming (inv-left-canonical-ex to inv-left-canonical)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right 6 using () renaming (inv-right-canonical-ex to inv-right-canonical)

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/7-specific theorem: every element to the seventh equals ε.
-- Specialization of the generic nth-power-identity from Coxeter.Cyclic
-- at n = 6 (apply-power-suc w 6 = ((((((w·w)·w)·w)·w)·w)·w) by definition).
------------------------------------------------------------------------

seventh-power-identity : (w : Word Gen) → ((((((w · w) · w) · w) · w) · w) · w) ≈ ε
seventh-power-identity = nth-power-identity
