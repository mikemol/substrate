------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.TensorProductView
--
-- Demonstrates that `bilinear-form-of M` (from generic SymBilinForm)
-- factors through TensorProduct via the universal property:
--
--   bilinear-form-of M : Vector n → Vector n → F₂      (bilinear)
--   bilinear-form-of-via-tensor M : TensorProduct n n → F₂   (linear)
--
--   bilinear-form-of M v w ≡ bilinear-form-of-via-tensor M (pair v w)
--
-- This is THE universal-property-of-tensor-product instantiated at
-- the substrate's metric pairings. Bilinear maps Vector n × Vector n
-- → F₂ correspond uniquely to linear maps TensorProduct n n → F₂;
-- the specific bilinear map bilinear-form-of M corresponds to the
-- specific linear bilinear-form-of-via-tensor M.
--
-- Slice 3 of 3 in the TensorProduct-structural trio. Concrete
-- demonstration of the bilinear↔linear bijection at the substrate's
-- most-pervasive bilinear operation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.TensorProductView where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (lookup; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Vector.Universal using (sum-F₂; sum-F₂-cong)
open import Substrate.Algebra.F2.SymBilinForm.BilinForm using (BilinForm)
open import Substrate.Algebra.F2.SymBilinForm.BilinearFormOf using (bilinear-form-of)
open import Substrate.Algebra.F2.SymBilinForm.Bilinearity using (sum-F₂-scalar)
open import Substrate.Category.TensorProduct using (TensorProduct; pair)

------------------------------------------------------------------------
-- N-1: bilinear-form-of-via-tensor — linear evaluation of a tensor
-- against a bilinear form.
--
-- For M : BilinForm n and T : TensorProduct n n, evaluate the
-- tensor T against M:
--
--   bilinear-form-of-via-tensor M T = Σᵢ Σⱼ T(i,j) · M(i,j)
--
-- This IS a linear map TensorProduct n n → F₂ (the linear
-- corresponding to bilinear-form-of M via the ⊗-Hom adjunction).
------------------------------------------------------------------------

bilinear-form-of-via-tensor :
  ∀ {n} → BilinForm n → TensorProduct n n → F₂
bilinear-form-of-via-tensor {n} M T =
  sum-F₂ {n} (λ i →
    sum-F₂ {n} (λ j →
      lookup (lookup T i) j · M i j))

------------------------------------------------------------------------
-- N-2: Helper — the factor shuffle.
--
-- v · (M · w) ≡ v · w · M  (= (v · w) · M, after ·-assoc + ·-comm)
-- We need: lookup v i · lookup w j · M i j ≡ lookup v i · (M i j · lookup w j)
--
-- Direct chain: x · y · z ≡ x · (y · z) [·-assoc] ≡ x · (z · y) [·-comm on y, z]
------------------------------------------------------------------------

shuffle-three-F₂ : (x y z : F₂) → x · y · z ≡ x · (z · y)
shuffle-three-F₂ x y z =
  trans (·-assoc x y z)
        (cong (x ·_) (·-comm y z))

------------------------------------------------------------------------
-- N-3: bilinear-form-of-via-tensor agrees with bilinear-form-of.
--
-- The agreement at T = pair v w:
--
--   bilinear-form-of-via-tensor M (pair v w)
--   = sum-F₂ (λ i → sum-F₂ (λ j → lookup (lookup (pair v w) i) j · M i j))
--
-- (lookup (pair v w) i = lookup v i *ₛ w; lookup (... *ₛ w) j = lookup v i · lookup w j)
--
--   = sum-F₂ (λ i → sum-F₂ (λ j → lookup v i · lookup w j · M i j))
--   = sum-F₂ (λ i → sum-F₂ (λ j → lookup v i · (M i j · lookup w j)))
--                                                      [shuffle-three-F₂]
--   = sum-F₂ (λ i → lookup v i · sum-F₂ (λ j → M i j · lookup w j))
--                                                      [sum-F₂-scalar (reversed)]
--   = bilinear-form-of M v w   [by definition]
------------------------------------------------------------------------

-- Helper at module level (n must vary for recursive call to typecheck):
-- lookup (lookup (pair v w) i) j ≡ lookup v i · lookup w j.
lookup-of-pair :
  ∀ {n m} (v : Vector n) (w : Vector m) (i : Fin n) (j : Fin m) →
  lookup (lookup (pair v w) i) j ≡ lookup v i · lookup w j
lookup-of-pair (a ∷ v') w zero    j = lookup-*ₛ a w j
lookup-of-pair (a ∷ v') w (suc i) j = lookup-of-pair v' w i j

bilinear-form-of-via-tensor-agrees :
  ∀ {n} (M : BilinForm n) (v w : Vector n) →
  bilinear-form-of M v w ≡ bilinear-form-of-via-tensor M (pair v w)
bilinear-form-of-via-tensor-agrees {n} M v w =
  sym (
    trans
      -- lookup (lookup (pair v w) i) j = lookup v i · lookup w j
      -- ⇒ lookup ... · M i j = lookup v i · lookup w j · M i j
      (sum-F₂-cong {n} (λ i →
        sum-F₂-cong {n} (λ j →
          cong (_· M i j) (lookup-of-pair v w i j))))
    (trans
      -- shuffle: lookup v i · lookup w j · M i j ≡ lookup v i · (M i j · lookup w j)
      (sum-F₂-cong {n} (λ i →
        sum-F₂-cong {n} (λ j →
          shuffle-three-F₂ (lookup v i) (lookup w j) (M i j))))
      -- Pull lookup v i out of the inner sum-F₂.
      (sum-F₂-cong {n} (λ i →
        sum-F₂-scalar (lookup v i) (λ j → M i j · lookup w j)))))

------------------------------------------------------------------------
-- N-4: Capstone — bilinear ↔ linear bijection concretely demonstrated.
--
-- After this slice:
--
--   * bilinear-form-of-via-tensor M : TensorProduct n n → F₂
--     — the LINEAR map corresponding to bilinear-form-of M under
--     the ⊗-Hom adjunction's universal property.
--
--   * bilinear-form-of-via-tensor-agrees — the agreement:
--     bilinear-form-of M v w ≡ bilinear-form-of-via-tensor M (pair v w).
--
-- This is the substrate's first concrete instance of the
-- bilinear ↔ linear bijection. Per the categorical principle:
--
--   Bilinear (V × W, U) ≅ Linear (V ⊗ W, U)
--
-- bilinear-form-of M (V × V → F₂) corresponds uniquely to
-- bilinear-form-of-via-tensor M (V ⊗ V → F₂). The "agrees"
-- equation IS the unit-of-adjunction direction.
--
-- Per [[feedback-categorical-name-first]]: substrate's bilinear-form-of
-- IS the natural "linear function out of the tensor product"
-- evaluated at the universal pair. The categorical reading makes
-- explicit what was implicit in the bilinearity proofs of
-- Substrate.Algebra.F2.SymBilinForm.Bilinearity.
--
-- Substrate-wide implication: any bilinear operation on F₂-vector
-- spaces FACTORS through TensorProduct via pair + a specific linear
-- map. The Adjunction primitive (#4) handles single-argument linear;
-- TensorProduct (#7) handles two-argument bilinear; both together
-- name the universal free-construction infrastructure that the
-- substrate's algebra rests on.
--
-- Deferred follow-ons:
--
--   * **Bilinearity of bilinear-form-of-via-tensor as Linear**:
--     prove bilinear-form-of-via-tensor M respects the +T addition
--     on TensorProduct. Would package it as a Linear record.
--
--   * **General bilinear-form ↔ tensor-Hom uniqueness**: any other
--     linear g : TensorProduct n n → F₂ with
--     g (pair v w) ≡ bilinear-form-of M v w MUST equal
--     bilinear-form-of-via-tensor M. The universal-property uniqueness.
--
--   * **Concrete instances at metric-id**: combine with the existing
--     dim-3 and dim-4 HodgeRecast work — metric-id-via-tensor is the
--     standard inner-product-as-tensor-trace.
--
--   * **Generalisation to Λ²V and Sym²V evaluations**: the specific
--     linear maps out of antisymmetric/symmetric subspaces.
------------------------------------------------------------------------
