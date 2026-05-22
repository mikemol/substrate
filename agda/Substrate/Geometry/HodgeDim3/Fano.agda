------------------------------------------------------------------------
-- Substrate.Geometry.HodgeDim3.Fano
--
-- M-11.fano slice: parametric chirality construction at any Fano point,
-- plus the Hamming-syndrome-as-Fano-phase identification.
--
-- Generalises M-11.dim3 (which fixed the chirality axis at ⟨e₃⟩ =
-- Fano point p₄) to all 7 Fano points. Each Fano point p induces:
--
--   * A chirality projection `Linear 3 → 1` = "dot product with point-coords p"
--   * A V₄-plane `KernelCode 3 1` = the F₂³-vectors orthogonal to point-coords p
--   * A chirality-axis predicate = the 1-dim subspace ⟨point-coords p⟩
--
-- The 7 Fano points = 7 distinct chirality choices = PG(2, F₂) = the
-- "phase space" of chirality-as-Hodge-dual readings at n=3. Per memory
-- `project_3plus1_parity_universal` and the chirality-rotation
-- conjecture: this is the smallest non-trivial instance of the phase
-- structure.
--
-- **Key identification**: the Hamming parity-check map
-- `H : Vector 7 → Vector 3` from M-7 is *literally* the
-- "vector ↦ Fano chirality phase" map. For each basis vector e_i ∈ F₂⁷,
-- `apply H (basis i) ≡ point-coords i` = the i-th Fano point's
-- coordinates. The syndrome of a single-bit error at position i IS
-- the i-th Fano point.
--
-- Uses the new `apply-linear-from-images-basis` foundational primitive
-- (M-11.fano N-1) per the universal-property discipline.
--
-- Deferred:
--   * Full orthogonality proof parametric in p (analogous to M-11.dim3's
--     proof for p=p₄; structurally clear via dot-product bilinearity).
--   * GL(3, F₂) transitivity on Fano points (M-11.fano.gl3 follow-on).
--   * KernelCode form for chirality-axis at general p (would require
--     basis choice for v's orthogonal complement per point).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.HodgeDim3.Fano where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Vec using ([]; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.DotProduct
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images;
         apply-linear-from-images-lookup;
         apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Code
open import Substrate.Codes.Hamming.H-7-4-3
  using (H-cols; Hamming-7-4-3)
open import Substrate.Geometry.Fano
  using (Point; point-coords;
         p₁; p₂; p₃; p₄; p₅; p₆; p₇)

------------------------------------------------------------------------
-- Parametric chirality-projection basis-images.
--
-- For any Fano point p, the chirality-projection sends basis vector e_i
-- to (lookup (point-coords p) i) ∷ []. This is the "i-th component of
-- point-coords p" packaged as a Vector 1.
------------------------------------------------------------------------

chirality-projection-images : Point → Fin 3 → Vector 1
chirality-projection-images p i = lookup (point-coords p) i ∷ []

------------------------------------------------------------------------
-- The chirality-projection Linear at any Fano point.
------------------------------------------------------------------------

chirality-projection : Point → Linear 3 1
chirality-projection p = linear-from-images (chirality-projection-images p)

------------------------------------------------------------------------
-- The V₄-plane at any Fano point: kernel of the chirality-projection.
--
-- u ∈ V₄-Plane-At p iff `apply (chirality-projection p) u ≡ 𝟎ⱽ`
-- iff u is orthogonal to point-coords p under the standard form
-- iff u ·F point-coords p ≡ 𝟘.
------------------------------------------------------------------------

V4Plane-At : Point → KernelCode 3 1
V4Plane-At p = record { parity-check = chirality-projection p }

------------------------------------------------------------------------
-- The chirality-axis predicate at any Fano point.
--
-- u ∈ ChiralityAxis-At p iff u is a scalar multiple of point-coords p
-- (i.e., u = 𝟎ⱽ or u = point-coords p, since F₂ has just two scalars).
------------------------------------------------------------------------

ChiralityAxis-At-Pred : Point → Vector 3 → Set
ChiralityAxis-At-Pred p u = Σ F₂ (λ c → u ≡ c *ₛ point-coords p)

------------------------------------------------------------------------
-- The key apply-reduction: applying the chirality-projection at p to a
-- vector u gives the dot product u ·F point-coords p.
--
-- Uses `apply-linear-from-images-lookup` (universal-property discipline).
-- The inner `lookup (chirality-projection-images p i) fz` reduces by
-- refl to `lookup (point-coords p) i`, so the sum matches the dot-
-- product definition directly.
------------------------------------------------------------------------

apply-chirality-projection-as-dot :
  (p : Point) (u : Vector 3) →
  lookup (apply (chirality-projection p) u) zero ≡ u ·F (point-coords p)
apply-chirality-projection-as-dot p u =
  apply-linear-from-images-lookup (chirality-projection-images p) u zero

------------------------------------------------------------------------
-- THE SYNDROME IDENTIFICATION.
--
-- The Hamming parity-check H : Linear 7 → 3 from M-7 is built as
-- `linear-from-images H-cols`. By `apply-linear-from-images-basis`:
--
--    apply (parity-check Hamming-7-4-3) (basis i) ≡ H-cols i
--
-- And by M-9's definition, `point-coords = H-cols`. So the syndrome
-- of the i-th basis vector IS the i-th Fano point's coordinates.
--
-- This is the literal "vector ↦ Fano chirality phase" map: each
-- single-bit error pattern at position i in F₂⁷ maps under H to a
-- specific Fano point in F₂³. The Hamming code's purpose (correct
-- single-bit errors via syndrome lookup) IS the chirality-phase
-- assignment in the smallest non-trivial instance.
------------------------------------------------------------------------

hamming-syndrome-basis :
  (i : Fin 7) →
  apply (parity-check Hamming-7-4-3) (basis i) ≡ point-coords i
hamming-syndrome-basis i = apply-linear-from-images-basis H-cols i

------------------------------------------------------------------------
-- Seven named instances of V₄-Plane-At, one per Fano point.
--
-- Documents that there are 7 distinct chirality choices at n=3, all
-- structurally accessible via the parametric construction. M-11.dim3's
-- V4-Plane is structurally equivalent to V4Plane-At p₄ (both have
-- chirality-bit-images / chirality-projection-images p₄ as their
-- basis-image function, since point-coords p₄ = col₄ = (𝟘, 𝟘, 𝟙)).
------------------------------------------------------------------------

v4plane-at-p₁ : KernelCode 3 1
v4plane-at-p₁ = V4Plane-At p₁

v4plane-at-p₂ : KernelCode 3 1
v4plane-at-p₂ = V4Plane-At p₂

v4plane-at-p₃ : KernelCode 3 1
v4plane-at-p₃ = V4Plane-At p₃

v4plane-at-p₄ : KernelCode 3 1
v4plane-at-p₄ = V4Plane-At p₄

v4plane-at-p₅ : KernelCode 3 1
v4plane-at-p₅ = V4Plane-At p₅

v4plane-at-p₆ : KernelCode 3 1
v4plane-at-p₆ = V4Plane-At p₆

v4plane-at-p₇ : KernelCode 3 1
v4plane-at-p₇ = V4Plane-At p₇

------------------------------------------------------------------------
-- Connection to M-11.dim3 (capstone documentation).
--
-- M-11.dim3 built the chirality-as-Hodge-dual structure at the specific
-- chirality choice ⟨e₃⟩ (= Fano point p₄). This file lifts that to all
-- 7 Fano points via parametric construction. The 7 instances are
-- gauge-equivalent under GL(3, F₂) action (transitivity proof deferred
-- to M-11.fano.gl3 follow-on); each gives an analogous Hodge-complement
-- structure.
--
-- The chirality-rotation conjecture (catalog § chirality-rotation):
-- the 7 Fano-point phases are the "phase space" at n=3; transitions
-- between phases via codes are mediated by GL(3, F₂) (order 168);
-- the Hamming syndrome `hamming-syndrome-basis` IS the canonical
-- "vector ↦ phase" map.
--
-- This is the smallest concrete grounding of the phase-space framework.
-- Medium step (M-11.dim4 / Λ²(F₂⁴)) and full machinery (transfer maps,
-- GL transitivity, exterior algebra) build on this base.
------------------------------------------------------------------------
