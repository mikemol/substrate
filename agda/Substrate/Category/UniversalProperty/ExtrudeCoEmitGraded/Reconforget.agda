------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Reconforget
--
-- Defines: recon-forget
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Reconforget where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.Wedge.Graded
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.Wedge
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitgraded
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Forgetgrade
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- coemit-graded-flat-allegory: the graded↔flat bridge (SKIGradedFlatAllegory: flat recon = μΦ ungraded, graded
-- = the arity-grade, bridged by the Φ-chain). For coemit: the graded prefix (Vec, built by recon) FORGETS to
-- the flat prefix (List, from take) — gforget realized. The digit each grade contributes IS the head (the μ-exact
-- point); accumulating them is the graded chain; forgetting the grade is the flat shadow. The allegory = this forget.
------------------------------------------------------------------------

-- grade-raising by a digit, then forgetting, = consing the digit onto the forgotten base (recon commutes with forget):
recon-forget : {n : ℕ} (v : Vec ℕ n) (d : ℕ) → forget-grade (recon coemit-graded n v d) ≡ (d ∷ forget-grade v)
recon-forget v d = refl    -- recon = _∷_, forget = the List image — commutes definitionally (the allegory square)
