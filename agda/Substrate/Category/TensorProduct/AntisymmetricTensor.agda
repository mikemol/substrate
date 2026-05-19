------------------------------------------------------------------------
-- Substrate.Category.TensorProduct.AntisymmetricTensor
--
-- The antisymmetric subspace of TensorProduct n n packaged as a
-- Σ-type subtype: TensorProduct + symmetry constraint + diagonal-zero
-- constraint.
--
-- At F₂ (char 2), antisymmetric tensors satisfy:
--   * T(i, j) ≡ T(j, i)   (symmetric — characteristic 2 collapses ±)
--   * T(i, i) ≡ 𝟘         (diagonal zero)
--
-- These two conditions identify the same subspace that
-- `antisymmetrize` (in Antisymmetric.agda) projects onto. Wrapping
-- them as a subtype enables stating round-trip equalities that
-- require the target tensor to BE antisymmetric (e.g., Bivector ↔
-- AntisymmetricTensor 4 reverse round-trip closes only on
-- antisymmetric inputs).
--
-- Per [[feedback-categorical-name-first]]: this is the F₂ analog of
-- Λ²V's element-level characterisation. The "antisymmetric subspace"
-- is a categorical object; this subtype names it at the Set level.
--
-- Per [[feedback-multi-reading-ambient-discipline]]: at F₂ the
-- "symmetric vs antisymmetric" distinction collapses at the subspace
-- level (T = Tᵀ ⇔ T + Tᵀ = 0). Both readings (symmetric Λ²; cyclic
-- difference) project to the same subspace. The subtype here is the
-- ambient predicate; downstream Bivector-bridge work attaches a
-- specific reading.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct.AntisymmetricTensor where

open import Data.Fin using (Fin)
open import Data.Nat using (ℕ)
open import Data.Vec using (lookup)
open import Relation.Binary.PropositionalEquality using (_≡_)

open import Substrate.Algebra.F2
open import Substrate.Category.TensorProduct using (TensorProduct)

------------------------------------------------------------------------
-- N-1: AntisymmetricTensor — the subtype.
--
-- A TensorProduct n n paired with witnesses that it lies in the
-- antisymmetric subspace.
--
-- Field naming uses the categorical reading: tensor for the
-- underlying data, symmetric and diag-zero for the two constraints
-- that pick out the antisymmetric subspace at F₂.
------------------------------------------------------------------------

record AntisymmetricTensor (n : ℕ) : Set where
  field
    tensor    : TensorProduct n n
    symmetric : (i j : Fin n) →
                lookup (lookup tensor i) j ≡ lookup (lookup tensor j) i
    diag-zero : (i : Fin n) →
                lookup (lookup tensor i) i ≡ 𝟘

open AntisymmetricTensor public

------------------------------------------------------------------------
-- N-2: Capstone — AntisymmetricTensor subtype lands.
--
-- After this slice:
--
--   * AntisymmetricTensor n : Set — the antisymmetric subspace of
--     TensorProduct n n at F₂, packaged as a Σ-type with explicit
--     symmetric + diag-zero witnesses.
--
-- Substrate-wide consequence: any operation that requires the input
-- tensor to BE antisymmetric (e.g., the reverse direction of the
-- Bivector ↔ TensorProduct 4 4 bridge — recovering the original
-- tensor from its 6 upper-triangular entries) can now be stated.
--
-- Per [[project-3plus1-parity-universal]]: the antisymmetric subspace
-- at n=4 has dim 6 = C(4,2) = 3+3 (where 3 = "live" pairs and 3 =
-- "complement" pairs — the Hodge ★ involution swaps them). The "+1"
-- chirality structure manifests at the subspace's internal Hodge
-- structure, not in the subspace's dimensionality count.
--
-- Deferred follow-ons:
--
--   * **Bivector ↔ AntisymmetricTensor 4 isomorphism**: package the
--     existing bivector-to-tensor / tensor-to-bivector pair as an
--     isomorphism on the subtype level. Closes the reverse-direction
--     gap from the Bivector.TensorProductBridge module.
--
--   * **antisymmetrize : TensorProduct n n → AntisymmetricTensor n**:
--     existing `antisymmetrize` operation packaged as producing a
--     subtype-witnessed output (the projection's image IS in the
--     subspace by construction).
--
--   * **AntisymmetricTensor + algebraic operations**: addition and
--     scalar multiplication restrict to the subspace; structural
--     lemmas would package these as the subspace's induced algebra.
------------------------------------------------------------------------
