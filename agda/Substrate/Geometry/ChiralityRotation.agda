------------------------------------------------------------------------
-- Substrate.Geometry.ChiralityRotation
--
-- M-11 full machinery sub-slice 4 (capstone). Integration module that
-- ties together the chirality-rotation framework: chirality at any
-- Fano point (M-11.fano), Hodge ★ + self-dual subspace at grade 2
-- (M-11.dim4), GL(3, F₂) generators (Gl3.agda), generic projective
-- space (PG), and the cohomological transfer map (Transfer.agda).
--
-- The framework, in summary:
--
--   1. Chirality choice at scale n = a 1-dim subspace of F₂^(n+1)
--      = a point of PG(n, F₂).
--      At n=2 (Fano), there are 7 chirality choices.
--
--   2. Rotation between phases = action of GL(n+1, F₂) on PG(n, F₂).
--      At n=2, GL(3, F₂) of order 168 acts transitively on the 7
--      Fano points; generators σ (cyclic shift) and τ (shear) suffice.
--
--   3. Hodge ★ at grade 1 in F₂^(n+1) maps each chirality choice
--      to its codim-1 hyperplane (the V₄-plane in the n=2 case);
--      at grade 2 in F₂⁴ it's a non-trivial involution with an
--      8-element fixed subspace (= candidate for catalog's "8 reserved").
--
--   4. Codes (Hamming, Reed-Muller, ExtHamming) MEDIATE between scales.
--      The Hamming syndrome H : F₂⁷ → F₂³ is literally the
--      "vector ↦ chirality phase" map at n=2 (via the syndrome of
--      single-bit errors).
--
--   5. Cohomological transfer (lift to higher scale + apply automorphism
--      + project back) realizes phase-rotation through the code
--      structure. Generic Section + transfer-map machinery is in
--      Transfer.agda.
--
-- This capstone file is documentation-heavy. It provides one concrete
-- demonstration (σ ∈ GL(3, F₂) rotating chirality from p₁ to p₂) and
-- exposes the framework's structural layout.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.ChiralityRotation where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (apply-linear-from-images-basis)
open import Substrate.Geometry.Fano
  using (point-coords; p₁; p₂; p₃; p₄; p₅; p₆; p₇)
open import Substrate.Geometry.HodgeDim3.Gl3
  using (σ; σ-images; τ; τ-images)

------------------------------------------------------------------------
-- Concrete demonstration: σ rotates chirality from Fano point p₁ to p₂.
--
-- σ is the cyclic shift e₀ → e₁ → e₂ → e₀. Applied to point-coords p₁
-- (= e₀ via H-cols), σ produces point-coords p₂ (= e₁).
--
-- This is the simplest non-trivial chirality rotation: starting from
-- the "chirality at point 1" (= the 1-dim subspace ⟨e₀⟩), σ moves us
-- to "chirality at point 2" (= ⟨e₁⟩).
--
-- Proof: apply-linear-from-images-basis on σ at index zero gives
-- σ-images zero = (𝟘 ∷ 𝟙 ∷ 𝟘 ∷ []) = e₁ = point-coords p₂.
------------------------------------------------------------------------

σ-rotates-p₁-to-p₂ : apply σ (point-coords p₁) ≡ point-coords p₂
σ-rotates-p₁-to-p₂ = apply-linear-from-images-basis σ-images zero

------------------------------------------------------------------------
-- σ rotates p₂ to p₄ (= e₂).
------------------------------------------------------------------------

σ-rotates-p₂-to-p₄ : apply σ (point-coords p₂) ≡ point-coords p₄
σ-rotates-p₂-to-p₄ = apply-linear-from-images-basis σ-images (suc zero)

------------------------------------------------------------------------
-- σ rotates p₄ to p₁ (closing the 3-cycle).
------------------------------------------------------------------------

σ-rotates-p₄-to-p₁ : apply σ (point-coords p₄) ≡ point-coords p₁
σ-rotates-p₄-to-p₁ = apply-linear-from-images-basis σ-images (suc (suc zero))

------------------------------------------------------------------------
-- Framework summary (documentation).
--
-- The chirality-rotation framework's components, in implementation
-- order across this multi-slice arc:
--
-- Foundational F₂ tier:
--   * F₂ (M-1), Vector (M-2), Linear (M-3), Code (M-4), linear-from-images (M-5)
--   * F₂-Like universal property (M-1.5)
--   * Vector free-module + atomic decomposition (M-2.5)
--   * Linear extensionality (M-3.5)
--   * apply-linear-from-images-lookup, apply-linear-from-images-basis
--     (universal-property discipline foundationals)
--
-- Specific code instances:
--   * RM(1,3) (M-6), Hamming [7,4,3] (M-7), Ext-Hamming [8,4,4] (M-8 via parity-lift)
--
-- Geometry / Hodge:
--   * Fano plane (M-9): points = F₂³ \ {0}, lines via collinearity
--   * HodgeDim3 / V4Plane / ChiralityAxis (M-11.dim3): the n=3 instance
--   * HodgeDim3 / Fano: parametric chirality at any of 7 Fano points
--   * HodgeDim3 / Gl3: σ, τ generators of GL(3, F₂) action
--   * HodgeDim4 / Bivector + HodgeStar + SelfDual (M-11.dim4): Λ²(F₂⁴) machinery
--   * HodgeDim4 / ReservedBridge: SelfDual ↔ Vector 3 ↔ Reserved validation
--
-- Generic phase-space + transfer machinery:
--   * PG(n, F₂) (this slice, sub-slice 2): parametric projective space
--   * Transfer (this slice, sub-slice 3): cohomological transfer map
--   * ChiralityRotation (this file, sub-slice 4): capstone integration
--
-- Cocycle-side (substrate's original target — partial):
--   * M-12: Pairing / Chirality / OrbitKey bridges to F₂-linear forms
--   * M-10A (planned, not yet built): F₂-linear Codeword + IsReserved
--
-- Status of the chirality-rotation conjecture:
--   * Cardinality + F₂-vector-space structure of the "8 reserved =
--     signed singletons = self-dual bivectors" claim: VALIDATED
--     (M-11.dim4.reserved-bridge).
--   * GL(3, F₂) transitive action on Fano: DEMONSTRATED via σ + τ
--     generators (formal transitivity proof deferred).
--   * Cohomological transfer machinery: DEFINED (this file +
--     Transfer.agda); concrete F₂³ ↔ F₂⁵ section instances deferred.
--   * Connection to Reed-Muller and higher Hamming structure
--     (Λᵏ tower for k ≥ 3, full exterior algebra): deferred.
--
-- Memory cross-references:
--   * project_3plus1_parity_universal: the underlying recurring pattern.
--   * feedback_universal_property_discipline: the proof discipline that
--     scales the framework across dimensions.
------------------------------------------------------------------------
