------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfacesetstarinvolution
--
-- Defines: coemit-faceset-star-involution
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfacesetstarinvolution where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Axes.Axis
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.WitnessTower.FaceSet
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flip
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- (2) coemit-faceset-star: reuse FaceSet's ★ (the totality-dual) and its involution. Face n = Vector (suc n) over
--     F₂; coemit's boundary faces are List ℕ — DIFFERENT CARRIERS. What transfers is the CONSTRUCTION:
--     ★ S = universe +ⱽ S ("what S is missing to be everything, computed, not negated"), ★★ = id from the
--     additive group laws. Coemit's step-level analogue is exactly f2-flip (𝟙 +F _): the totality-dual on ONE bit,
--     with the SAME engine (x ⊕ x = 𝟘). So coemit's chirality flip IS FaceSet's ★ at n = 0 (the one-bit face).
------------------------------------------------------------------------

coemit-faceset-star-involution : {n : ℕ} (S : Face n) → ★ (★ S) ≡ S     -- the canonical ★★ = id, REUSED
coemit-faceset-star-involution = ★-involution
