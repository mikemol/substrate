------------------------------------------------------------------------
-- Substrate.Geometry.HodgeDim3.Orthogonality
--
-- N-4 of M-11.dim3. The orthogonality lemma: every vector in the
-- V₄-plane is orthogonal (under the standard F₂-bilinear form) to
-- every vector in the chirality-axis.
--
-- This is the structural content of "chirality is the Hodge dual of
-- V₄" at n=3: the codim-2 subspace (chirality-axis) and the 2-dim
-- subspace (V₄-plane) annihilate each other under the dot product.
--
-- Provides both a predicate-form orthogonality (using the bit
-- constraints directly) and a kernel-form (using KernelCode
-- membership, via the bridges from N-1 / N-2).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Geometry.HodgeDim3.Orthogonality where

open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong; cong-trans)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.DotProduct
open import Substrate.Algebra.F2.Code
open import Substrate.Geometry.HodgeDim3.V4Plane
  using (V4-Plane; V4-Plane-Pred; kernel→pred)
open import Substrate.Geometry.HodgeDim3.ChiralityAxis
  using (ChiralityAxis; ChiralityAxis-Pred)
  renaming (kernel→pred to chir-kernel→pred)

------------------------------------------------------------------------
-- Orthogonality at the predicate level.
--
-- Given v with lookup v 2 ≡ 𝟘 and w with lookup w 0 ≡ 𝟘 ∧ lookup w 1 ≡ 𝟘,
-- the F₂-valued dot product v ·F w equals 𝟘.
--
-- Proof: expand v ·F w = a·x + (b·y + (c·z + 𝟘)); rewrite using the
-- three bit constraints; F₂ axioms collapse each summand to 𝟘.
------------------------------------------------------------------------

v4-chir-orthogonal-pred :
  (v w : Vector 3) →
  V4-Plane-Pred v →
  ChiralityAxis-Pred w →
  v ·F w ≡ 𝟘
v4-chir-orthogonal-pred (a ∷ b ∷ c ∷ []) (x ∷ y ∷ z ∷ []) v∈ (w∈0 , w∈1) =
  -- Goal: a · x + (b · y + (c · z + 𝟘)) ≡ 𝟘
  cong-trans (λ k → a · k + (b · y + (c · z + 𝟘))) w∈0
  (cong-trans (_+ (b · y + (c · z + 𝟘))) (·-absorbʳ a)
  (trans (+-identityˡ _)
  (cong-trans (λ k → b · k + (c · z + 𝟘)) w∈1
  (cong-trans (_+ (c · z + 𝟘)) (·-absorbʳ b)
  (trans (+-identityˡ _)
  (cong-trans (λ k → k · z + 𝟘) v∈
  (cong-trans (_+ 𝟘) (·-absorbˡ z)
         (+-identityˡ 𝟘))))))))

------------------------------------------------------------------------
-- Orthogonality at the KernelCode level (via bridges).
------------------------------------------------------------------------

v4-chir-orthogonal :
  (v w : Vector 3) →
  In-Kernel V4-Plane v →
  In-Kernel ChiralityAxis w →
  v ·F w ≡ 𝟘
v4-chir-orthogonal v w v∈ w∈ =
  v4-chir-orthogonal-pred v w (kernel→pred v v∈) (chir-kernel→pred w w∈)
