------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace.LogSumExp
--
-- Ⓝ.lse — THE PAYOFF of the Ω3-L-primes arc: the el-atlas L-space OR-operator
-- IS log-sum-exp.
--
-- The codec ties additive L to multiplicative ℚ: `exp-⊕` says the L-space ⊕
-- mirrors G-space ·ℚ. The el-atlas G_OR is +ℚ (parallel conductance,
-- GValueAsQ). Its L-space mirror — `L_OR` — is therefore the operation whose
-- exp is the +ℚ of the exps: L_OR a b = logL (expL a +ℚ expL b), the LOG of the
-- SUM of the EXPs. That is log-sum-exp.
--
-- This needs the codec's INVERSE `logL` (its surjectivity onto ℚ₊) — realized
-- constructively for G-values by the prime factorisation
-- (GValueLSpace.PrimeFactor.q-factored-roundtrip, the Ω3-L-primes iso). Here it
-- enters as the honest structural hypothesis (scoped, per the discipline); the
-- whole factorisation arc is what discharges it for the concrete G-value codec.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace.LogSumExp where

open import Substrate.Algebra.Q using (ℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl)
open import Substrate.Logic.Evidence.GValueLSpace using (ExpLogCodec; ExpLogCodecℚ)

module _ {L : Set} (C : ExpLogCodecℚ L)
         (logL    : ℚ → L)
         (exp-log : (x : ℚ) → ExpLogCodec.expL C (logL x) ≈ℚ x) where
  open ExpLogCodec C

  -- L_OR : the L-space mirror of G_OR = +ℚ (parallel), as ⊕ mirrors ·ℚ.
  -- By definition the LOG of the SUM of the EXPs — log-sum-exp.
  L_OR : L → L → L
  L_OR a b = logL (expL a +ℚ expL b)

  -- THE PAYOFF: L_OR IS log-sum-exp — its exp-image is exactly the +ℚ (G_OR /
  -- parallel conductance) of the exp-images.
  L_OR-is-logsumexp : (a b : L) → expL (L_OR a b) ≈ℚ (expL a +ℚ expL b)
  L_OR-is-logsumexp a b = exp-log (expL a +ℚ expL b)

------------------------------------------------------------------------
-- Non-vacuity: the IDENTITY codec (L = G = ℚ, exp = id, ⊕ = ·ℚ). It is its own
-- inverse (logL = id), and there L_OR DEGENERATES to +ℚ itself = G_OR — since
-- exp = id makes "log of the sum of the exps" the bare sum. The construction
-- inhabits and computes.
------------------------------------------------------------------------

id-codec : ExpLogCodecℚ ℚ
id-codec = record
  { _⊕_ = _*ℚ_ ; 𝟘 = 1ℚ ; expL = λ x → x
  ; exp-⊕ = λ a b → ≈ℚ-refl (a *ℚ b) ; exp-𝟘 = ≈ℚ-refl 1ℚ }

-- At the identity codec, L_OR a b ≈ a +ℚ b (G_OR). A concrete firing.
id-L_OR-is-+ℚ : (a b : ℚ) →
  ExpLogCodec.expL id-codec
    (L_OR id-codec (λ x → x) (λ x → ≈ℚ-refl x) a b) ≈ℚ (a +ℚ b)
id-L_OR-is-+ℚ a b = L_OR-is-logsumexp id-codec (λ x → x) (λ x → ≈ℚ-refl x) a b
