------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bit1
--
-- Defines: bit1
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bit1 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge.Mul
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- PREFLIGHT (verbatim from V4FullCocycle):  e = v4 𝟘 𝟘 ;
--   rowSwap-gen = v4 𝟙 𝟘   -- "generator 1: det-flip / Chirality (⟡S3)"   ⇒ the MORPH bit (bit0)
--   recip-gen   = v4 𝟘 𝟙   -- "generator 2: recip / object side"          ⇒ the OBJ bit (bit1)
-- and Substrate.Axes has the bijection (axis-of-v-v-of-axis, v-of-axis-axis-of-v) but NO torsor lemma.
--
-- (2) coemit-bar₂-guise, CONFIRMED: bar = pflip = XOR-1 flips bit0 = morph = **rowSwap / det-flip / chirality**
--     (ChiralityBridge's ONE ℤ/2). bar₂ = xor2 = XOR-2 flips bit1 = obj = **recip / the object side** — exactly
--     StarV4's "the dagger's fraction-level shadow is `recip` (swap)". So ⟨bar, bar₂⟩ = ⟨rowSwap, recip⟩ = V₄.
-- (3) coemit-digit-is-v4: the digit's low two bits ARE V4Full's (morph, obj) coords, and pflip/xor2 ARE its
--     two generators' actions. Made literal below.
------------------------------------------------------------------------
-- bit1 of a digit (4-periodic), the OBJ coordinate. (bit0 = parity, already have.)
bit1 : ℕ → F₂
bit1 zero                          = 𝟘
bit1 (suc zero)                    = 𝟘
bit1 (suc (suc zero))              = 𝟙
bit1 (suc (suc (suc zero)))        = 𝟙
bit1 (suc (suc (suc (suc n))))     = bit1 n
