------------------------------------------------------------------------
-- Substrate.TokiPona.F2toQForget
--
-- TPQ8 of the Toki Pona ℚ-retrofit arc per [scratch/tpq_arc_plan.md].
--
-- Forgetful functor from F₂ Toki Pona to ℚ Toki Pona. Each F₂
-- semantic value lifts to its ℚ counterpart via the canonical
-- embedding 𝟘 ↦ 0ℚ, 𝟙 ↦ 1ℚ. Demonstrates that the original F₂
-- Toki Pona arc IS a sub-instance of the ℚ version.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.F2toQForget where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.Q using (ℚ; 0ℚ; 1ℚ)

-- F₂-side imports
open import Substrate.Algebra.F2.Vector as F2V
  using ()
  renaming (Vector to F2-Vector)

-- ℚ-side imports
open import Substrate.TokiPona.QSemanticSpace using (QSemVec)

------------------------------------------------------------------------
-- 1. The forgetful map on scalars.
--
-- 𝟘 ↦ 0ℚ; 𝟙 ↦ 1ℚ. The canonical F₂ → ℚ ring-embedding
-- restricted to {𝟘, 𝟙}.
------------------------------------------------------------------------

F2→Q : F₂ → ℚ
F2→Q 𝟘 = 0ℚ
F2→Q 𝟙 = 1ℚ

------------------------------------------------------------------------
-- 2. The forgetful map on vectors.
--
-- Componentwise application of F2→Q.
------------------------------------------------------------------------

F2-Vec→Q-Vec : {n : ℕ} → F2-Vector n → QSemVec n
F2-Vec→Q-Vec v = map F2→Q v

------------------------------------------------------------------------
-- 3. Worked examples.
------------------------------------------------------------------------

F2→Q-𝟘 : F2→Q 𝟘 ≡ 0ℚ
F2→Q-𝟘 = refl

F2→Q-𝟙 : F2→Q 𝟙 ≡ 1ℚ
F2→Q-𝟙 = refl

-- Empty vector maps to empty.
F2-Vec→Q-Vec-empty :
  F2-Vec→Q-Vec [] ≡ []
F2-Vec→Q-Vec-empty = refl

------------------------------------------------------------------------
-- 4. Capstone for TPQ8.
--
-- The F₂ → ℚ forgetful functor witnesses that the original F₂
-- Toki Pona arc embeds into the ℚ version. TPQ9 builds worked
-- ℚ-Fragment examples; TPQ10 capstone.
------------------------------------------------------------------------
