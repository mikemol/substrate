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

open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; _≢_)

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Groups.Coxeter.Cyclic.Existential 1 using () renaming (Canonical-ex to Canonical-at; insert-canonical-ex to insert-canonical; inv-canonical-ex to inv-canonical; canonical-cover-ex to canonical-cover-fin)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv 1 using () renaming (inv-inv-canonical-ex to inv-inv-canonical)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Left 1 using () renaming (inv-left-canonical-ex to inv-left-canonical)
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.Right 1 using () renaming (inv-right-canonical-ex to inv-right-canonical)

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical-at w₁ → Canonical-at w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/2-specific theorem: self-inverse. Specialization of the generic
-- nth-power-identity from Coxeter.Cyclic at n = 1
-- (apply-power-suc w 1 = w · w by definition).
------------------------------------------------------------------------

self-inverse : (w : Word Gen) → (w · w) ≈ []
self-inverse = nth-power-identity
