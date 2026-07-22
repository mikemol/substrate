{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingRails — ⟡jac-encoding-bridge, ROUTE R4.
--
-- THE ROSETTA-STONE THESIS, MACHINE-CHECKED: every landing route is the SAME
-- canonical object read through a different codec. C2 (JacobianEncodingNormalize)
-- landed the identification `normalize R.fᵢ ≡ normalize Cᴹfᵢ` — its `.agdai` IS
-- the materialised canonical core. Route R4 is that identification transported
-- into the SUBTRACTION-FREE semiring carrier by `cong` — no fresh proof.
--
-- The codec is the Grothendieck rail split `split : ℤ → ℕ × ℕ` ⟨pos, neg⟩
-- (`JacobianNegSemiring`, ⟡jac-neg-route-C — the ℕ×ℕ difference-pair =
-- `GradedProductOver _+_ 0 (λ _ → ℕ)`). `railify` splits every coefficient, so
-- f₃'s `-3 x²y` / `-x³z` appear as rails `(0,3)` / `(0,1)` — no ℤ negation in
-- the carrier. Because C2's `bridgeᵢ` gives ℤ-equality, `cong railify` lands the
-- rail identification.
--
--     railify (normalize R.fᵢ) ≡ railify (normalize Cᴹfᵢ)    (cong railify bridgeᵢ)
--
-- This IS "having landed C2, extract from its core to land any other": the
-- canonical bridge is the source; each route re-codecs it.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingRails where

open import Substrate.Foundation.Eq using (_≡_; cong)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Z.MPolyNormalize using (normalize)
open import Substrate.Algebra.Z.JacobianNegSemiring using (split)
open import Substrate.Algebra.Z.JacobianResidue as R
  using (MPoly; Mono; Term; term; mapL)
open import Substrate.Algebra.Q.JacobianEncodingNormalize
  using (Cᴹf₁; Cᴹf₂; Cᴹf₃; bridge₁; bridge₂; bridge₃)

------------------------------------------------------------------------
-- The rail codec: split every ℤ coefficient into ℕ × ℕ ⟨pos, neg⟩.
------------------------------------------------------------------------

railify : MPoly → List (Mono × (ℕ × ℕ))
railify = mapL (λ { (term m k) → (m , split k) })

------------------------------------------------------------------------
-- ROUTE R4: C2's canonical identification, re-codec'd into the rails.
------------------------------------------------------------------------

railBridge₁ : railify (normalize R.f₁) ≡ railify (normalize Cᴹf₁)
railBridge₁ = cong railify bridge₁

railBridge₂ : railify (normalize R.f₂) ≡ railify (normalize Cᴹf₂)
railBridge₂ = cong railify bridge₂

railBridge₃ : railify (normalize R.f₃) ≡ railify (normalize Cᴹf₃)
railBridge₃ = cong railify bridge₃
