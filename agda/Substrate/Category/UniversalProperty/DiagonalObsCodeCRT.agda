------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalObsCodeCRT
--
-- ⟡odecode-crt-roundtrip — discharges ⟡diagonal-obs-code-crt-roundtrip
-- (DiagonalObsCode.agda's ONE scoped gap): the CRT pair-code round-trips
-- under coprime bounds.
--
-- DiagonalObsCode exposes `codePair w = combine w : ℕ × ℕ → ℕ` (the encode)
-- but scopes decode/rt to the caller, because the FULL round-trip needs the
-- slice components bounded below the moduli. Here that round-trip is PROVEN:
-- decoding a CRT-combined code by componentwise `mod-suc` recovers the pair
-- EXACTLY when a₁ < suc m and a₂ < suc n. The proof is `combine-mod-m/n`
-- (the CRT-Witness's own modular-recovery laws) composed with `mod-suc-id`
-- (mod fixes elements below the modulus) — no new machinery, the reuse point
-- DiagonalObsCode named.
--
-- This is the one genuine proof of the ⟡ta-upterm-O-decode arc: the triple
-- (S,T,W) → ℕ → (S,T,W) recovery that a concrete object's CRT-carrier needs
-- (⟡odecode-decode6, e.g. crt-UP / QuotientProduct).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.DiagonalObsCodeCRT where

open import Substrate.Foundation.Nat using (ℕ; suc; _<_)
open import Substrate.Foundation.Eq using (_≡_; trans; cong₂)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-id)
open import Substrate.Algebra.Quotient.CRT
  using (CRT-Witness; combine; combine-mod-m; combine-mod-n)

------------------------------------------------------------------------
-- 1. The decode: recover a pair from a CRT code by componentwise mod-suc.
------------------------------------------------------------------------

decodePair : (m n : ℕ) → ℕ → ℕ × ℕ
decodePair m n k = (k mod-suc m , k mod-suc n)

------------------------------------------------------------------------
-- 2. THE ROUND-TRIP: decode ∘ combine = id, under a₁ < suc m and a₂ < suc n.
--    combine-mod-m/n reduce the code's residues to (a₁ mod-suc m, a₂ mod-suc n);
--    mod-suc-id then fixes each below its modulus. cong₂ _,_ glues the pair.
------------------------------------------------------------------------

crt-roundtrip :
  {m n : ℕ} (w : CRT-Witness m n) (a₁ a₂ : ℕ) →
  a₁ < suc m → a₂ < suc n →
  decodePair m n (combine w (a₁ , a₂)) ≡ (a₁ , a₂)
crt-roundtrip {m} {n} w a₁ a₂ b₁ b₂ =
  cong₂ _,_
    (trans (combine-mod-m w a₁ a₂) (mod-suc-id a₁ m b₁))
    (trans (combine-mod-n w a₁ a₂) (mod-suc-id a₂ n b₂))
