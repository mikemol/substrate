------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitisv4morph
--
-- Defines: coemit-digit-is-v4-morph
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitdigitisv4morph where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
import Substrate.Algebra.R.Trace.V4FullCocycle as V4
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipflipsparity
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Digittov4
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipfixesbit1
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- the two homomorphism laws: digit-to-v4 intertwines (pflip, xor2) with (v4-flip-morph, v4-flip-obj).
coemit-digit-is-v4-morph : (n : ℕ) → digit-to-v4 (pflip n) ≡ v4-flip-morph (digit-to-v4 n)
coemit-digit-is-v4-morph n = cong₂ V4.v4 (pflip-flips-parity n) (pflip-fixes-bit1 n)
