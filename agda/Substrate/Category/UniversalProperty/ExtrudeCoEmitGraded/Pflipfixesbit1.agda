------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipfixesbit1
--
-- Defines: pflip-fixes-bit1
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipfixesbit1 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipmorph
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.V4flipobj
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bit1
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- THE ACTION HOMOMORPHISM: pflip acts as v4-flip-morph (rowSwap); xor2 acts as v4-flip-obj (recip).
-- pflip flips bit0 and FIXES bit1 ; xor2 flips bit1 and FIXES bit0 — D-independent-involutions-flip-different-bits,
-- now LITERAL (each proven by the same 2-/4-periodic recursion the maps themselves use).
pflip-fixes-bit1 : (n : ℕ) → bit1 (pflip n) ≡ bit1 n
pflip-fixes-bit1 zero                       = refl
pflip-fixes-bit1 (suc zero)                 = refl
pflip-fixes-bit1 (suc (suc zero))           = refl
pflip-fixes-bit1 (suc (suc (suc zero)))     = refl
pflip-fixes-bit1 (suc (suc (suc (suc n))))  = pflip-fixes-bit1 n
