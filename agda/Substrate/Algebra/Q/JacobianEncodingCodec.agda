{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingCodec — ⟡jac-encoding-bridge, ROUTE C1.
--
-- THE THIRD CODEC OFF THE ONE CANONICAL OBJECT. C2 (JacobianEncodingNormalize)
-- landed `normalize R.fᵢ ≡ normalize Cᴹfᵢ`; R4 re-codec'd it into ℕ×ℕ rails.
-- Route C1 re-codecs it through the LOG/ANTILOG codec — the ExpLogCodec that
-- DISSOLVES "SPPF/semiring has no negation": negation is not fielded, it is
-- TRANSPORTED — log to the multiplicative side, involute about 𝟙, antilog back.
--
--     expℤ z = 2^z : ℤ → ℚ          (the codec; `ZPow 2ℚ ½`, from ⟡jac-neg-route-B)
--     expℤ (-k)  =  (expℤ k)⁻¹      (a NEGATIVE coeff maps to a reciprocal —
--                                    NO additive inverse in the carrier)
--
-- `codecify` maps every ℤ coefficient through `expℤ`, so f₃'s `-3`, `-1` become
-- `2⁻³`, `2⁻¹` — the semiring gauge, negation dissolved into the codec. Because
-- C2's `bridgeᵢ` gives ℤ-equality, `cong codecify` lands the codec identification.
--
--     codecify (normalize R.fᵢ) ≡ codecify (normalize Cᴹfᵢ)   (cong codecify bridgeᵢ)
--
-- The equality is propositional `≡` on `List (Mono × ℚ)` — NO `≈ℚ` composition
-- (the wall). The codec is non-trivial at base 2 (`codec-discriminates`), so the
-- negation-transport is non-vacuous.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingCodec where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Z using (+_; -suc_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Logic.Evidence.GValueLSpace.Primes using (module ZPow)
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
open import Substrate.Algebra.Z.JacobianResidue as R
  using (MPoly; Mono; Term; term; mapL)
open import Substrate.Algebra.Q.JacobianEncodingNormalize
  using (Cᴹf₁; Cᴹf₂; Cᴹf₃; bridge₁; bridge₂; bridge₃)

------------------------------------------------------------------------
-- The log/antilog codec: expℤ z = 2^z into ℚ-multiplicative (⟡jac-neg-route-B).
------------------------------------------------------------------------

2ℚ half : ℚ
2ℚ   = mkℚ (+ 2) 0      -- 2/1
half = mkℚ (+ 1) 1      -- 1/2

base-inverse : (2ℚ *ℚ half) ≈ℚ 1ℚ
base-inverse = refl

open ZPow 2ℚ half base-inverse using (expℤ)

-- negation is TRANSPORTED, not fielded: expℤ (-k) is the reciprocal of expℤ k.
neg-transport : (expℤ (-suc 1) *ℚ expℤ (+ 2)) ≈ℚ 1ℚ     -- ¼ · 4 ≈ℚ 1ℚ
neg-transport = refl

-- the codec is NON-TRIVIAL at base 2 (else every image is 1ℚ and it transports nothing).
codec-discriminates : expℤ (+ 1) ≈ℚ expℤ (-suc 0) → ⊥    -- 2 ≢ ½
codec-discriminates ()

------------------------------------------------------------------------
-- The codec φ + ROUTE C1: C2's identification re-codec'd through log/antilog.
------------------------------------------------------------------------

codecify : MPoly → List (Mono × ℚ)
codecify = mapL (λ { (term m k) → (m , expℤ k) })

codecBridge₁ : codecify (normalize R.f₁) ≡ codecify (normalize Cᴹf₁)
codecBridge₁ = cong codecify bridge₁

codecBridge₂ : codecify (normalize R.f₂) ≡ codecify (normalize Cᴹf₂)
codecBridge₂ = cong codecify bridge₂

codecBridge₃ : codecify (normalize R.f₃) ≡ codecify (normalize Cᴹf₃)
codecBridge₃ = cong codecify bridge₃
