------------------------------------------------------------------------
-- Substrate.Groups.Z-x-FreeCyclic-Recovery
--
-- The "phase-projection recovers Zₙ" structural identity: embedding a
-- Zₙ word into the 2-D structure (Zₙ × ℕ) and then projecting back
-- yields the original word. Equivalently: phase-project is a
-- LEFT-inverse to a canonical embedding.
--
-- Demonstrated at both Z₃ and Z₄ in this combined module — the
-- pattern is mechanical and applies uniformly to any Zₙ-x-FreeCyclic
-- instance.
--
-- Categorical reading: the cover map (phase-project) is split — there
-- is a section (embed). The 2-D structure SPLITS over the base Zₙ via
-- the trivial embedding `w ↦ (w, ε)`. The cycle component starts at
-- "depth zero" (= ε in FreeCyclic).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery where

open import Data.Product using (_,_)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.Z3-x-FreeCyclic as Z₃×F
import Substrate.Groups.Z4-x-FreeCyclic as Z₄×F
import Substrate.Groups.Z3-x-FreeCyclic-PhaseProjection as Z₃-Proj
import Substrate.Groups.Z4-x-FreeCyclic-PhaseProjection as Z₄-Proj
open import Substrate.Groups.Coxeter.Word using (Word)

------------------------------------------------------------------------
-- N-1: Z₃ embedding into Z₃ × ℕ at cycle-depth zero.
------------------------------------------------------------------------

embed-Z₃ : Word Z₃.Gen → Z₃×F.Word
embed-Z₃ w = (w , F.ε)

------------------------------------------------------------------------
-- N-2: Z₃ phase-recovery — phase-project ∘ embed-Z₃ ≡ id.
------------------------------------------------------------------------

Z₃-phase-recovery :
  (w : Word Z₃.Gen) → Z₃-Proj.phase-project (embed-Z₃ w) ≡ w
Z₃-phase-recovery w = refl

------------------------------------------------------------------------
-- N-3: embed-Z₃ preserves the identity ε.
------------------------------------------------------------------------

embed-Z₃-ε : embed-Z₃ Z₃.ε ≡ Z₃×F.ε
embed-Z₃-ε = refl

------------------------------------------------------------------------
-- N-4: embed-Z₃ preserves _·_ (= homomorphism property on monoid
-- composition modulo normalize equivalence at the cycle component).
--
-- In Z₃×F: (w₁ , ε) · (w₂ , ε)
--          = (normalize (w₁ ++ w₂), normalize (ε ++ ε))
--          = (w₁ ·_Z₃ w₂, ε).
-- And embed-Z₃ (w₁ ·_Z₃ w₂) = (w₁ ·_Z₃ w₂, ε).
-- Both sides match by refl on the cycle component too (F.ε = []).
------------------------------------------------------------------------

embed-Z₃-· :
  (w₁ w₂ : Word Z₃.Gen) →
  embed-Z₃ (w₁ Z₃.· w₂) ≡ (embed-Z₃ w₁ Z₃×F.· embed-Z₃ w₂)
embed-Z₃-· w₁ w₂ = refl

------------------------------------------------------------------------
-- N-5: Same for Z₄.
------------------------------------------------------------------------

embed-Z₄ : Word Z₄.Gen → Z₄×F.Word
embed-Z₄ w = (w , F.ε)

Z₄-phase-recovery :
  (w : Word Z₄.Gen) → Z₄-Proj.phase-project (embed-Z₄ w) ≡ w
Z₄-phase-recovery w = refl

embed-Z₄-ε : embed-Z₄ Z₄.ε ≡ Z₄×F.ε
embed-Z₄-ε = refl

embed-Z₄-· :
  (w₁ w₂ : Word Z₄.Gen) →
  embed-Z₄ (w₁ Z₄.· w₂) ≡ (embed-Z₄ w₁ Z₄×F.· embed-Z₄ w₂)
embed-Z₄-· w₁ w₂ = refl

------------------------------------------------------------------------
-- N-6: Capstone — phase-recovery at Z₃ and Z₄.
--
-- After this slice:
--
--   * embed-Zₙ : Word Zₙ.Gen → Zₙ × F.Word, the zero-cycle section.
--   * Zₙ-phase-recovery : phase-project ∘ embed-Zₙ ≡ id.
--   * embed-Zₙ-ε / embed-Zₙ-· : embed is a Coxeter Core homomorphism.
--
-- Together with the phase-projection (slices 4, 6), this witnesses
-- that the cover-map Z_n × F → Z_n SPLITS via the trivial embedding.
-- The 2-D structure is then a SEMIDIRECT product of Z_n and F
-- (in this case, since F is just ℕ and acts trivially on Z_n, it's
-- actually a DIRECT product — the trivial splitting).
--
-- Per [[project-graded-bicategorical-arc]]: the splitting `id =
-- phase-project ∘ embed` makes the cycle axis a "fibre" over each
-- Z_n element. The graded structure (degree = cycle depth) naturally
-- decomposes any 2-D word as (Z_n part, cycle depth).
------------------------------------------------------------------------
