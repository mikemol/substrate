------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
--
-- Bridges substrate's existing Bivector at dim 4 (Vec F₂ 6) to the
-- antisymmetric subspace of TensorProduct 4 4 (from
-- Substrate.Category.TensorProduct).
--
-- At F₂ (char 2):
--   * Antisymmetric subspace of TensorProduct 4 4: T with
--     T(i,j) = T(j,i) AND T(i,i) = 0. Dimension 6 = C(4,2).
--   * Bivector = Vec F₂ 6 with the 6 basis 2-blades e_i ∧ e_j
--     indexed by lex-order (i, j) for 0 ≤ i < j ≤ 3.
--
-- Both have dim 6 and represent Λ²(F₂⁴). The bridge is the standard
-- isomorphism: each Bivector coefficient k (= eᵢ ∧ eⱼ) maps to the
-- (i, j) and (j, i) positions in the tensor; diagonal is zero.
--
-- After this slice: substrate's existing Bivector / HodgeStar /
-- SelfDual / ReservedBridge work can be lifted to TensorProduct-level
-- reasoning via this bridge. The Hodge ★ at dim 4 (= the index-
-- reversal involution on Bivector) becomes the "swap-tensor-axes"
-- operation at TensorProduct 4 4 (= transpose at the antisymmetric
-- subspace).
--
-- Per [[feedback-categorical-name-first]]: Bivector at dim 4 IS the
-- substrate's representation of Λ²(F₂⁴); this slice surfaces the
-- categorical handle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₀; ₁; ₂; ₃)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Category.TensorProduct using (TensorProduct)

------------------------------------------------------------------------
-- N-1: bivector-to-tensor — embed a Bivector as an antisymmetric
-- TensorProduct.
--
-- For Bivector = (a, b, c, d, e, f) with the lex-order encoding:
--   a = coeff of e₀ ∧ e₁  → tensor positions (0,1) and (1,0)
--   b = coeff of e₀ ∧ e₂  → (0,2) and (2,0)
--   c = coeff of e₀ ∧ e₃  → (0,3) and (3,0)
--   d = coeff of e₁ ∧ e₂  → (1,2) and (2,1)
--   e = coeff of e₁ ∧ e₃  → (1,3) and (3,1)
--   f = coeff of e₂ ∧ e₃  → (2,3) and (3,2)
--   Diagonal (i,i) = 0.
--
-- The resulting tensor is automatically in the antisymmetric subspace
-- at F₂: T(i,j) = T(j,i) for all i, j (since char 2 conflates ± and
-- the construction is symmetric) and T(i,i) = 0.
------------------------------------------------------------------------

bivector-to-tensor : Bivector → TensorProduct 4 4
bivector-to-tensor (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) =
  (𝟘 ∷ a ∷ b ∷ c ∷ []) ∷
  (a ∷ 𝟘 ∷ d ∷ e ∷ []) ∷
  (b ∷ d ∷ 𝟘 ∷ f ∷ []) ∷
  (c ∷ e ∷ f ∷ 𝟘 ∷ []) ∷
  []

------------------------------------------------------------------------
-- N-2: tensor-to-bivector — extract the upper-triangular entries.
--
-- Reads positions (0,1), (0,2), (0,3), (1,2), (1,3), (2,3) from a
-- TensorProduct 4 4, packaging them as a Bivector. Discards
-- diagonal and lower-triangular (which are redundant for
-- antisymmetric tensors at F₂).
------------------------------------------------------------------------

tensor-to-bivector : TensorProduct 4 4 → Bivector
tensor-to-bivector T =
  lookup (lookup T zero) (suc zero) ∷            -- (0, 1) = a
  lookup (lookup T zero) ₂ ∷      -- (0, 2) = b
  lookup (lookup T zero) ₃ ∷ -- (0, 3) = c
  lookup (lookup T (suc zero)) ₂ ∷ -- (1, 2) = d
  lookup (lookup T (suc zero)) ₃ ∷ -- (1, 3) = e
  lookup (lookup T ₂) ₃ ∷ -- (2, 3) = f
  []

------------------------------------------------------------------------
-- N-3: Round-trip: tensor-to-bivector ∘ bivector-to-tensor ≡ id.
--
-- Verifies that the bridge is a section: starting from any Bivector,
-- embedding as a tensor and re-extracting yields the original
-- Bivector.
--
-- Proof: refl after pattern matching on the Bivector.
------------------------------------------------------------------------

bivector-tensor-roundtrip :
  (v : Bivector) → tensor-to-bivector (bivector-to-tensor v) ≡ v
bivector-tensor-roundtrip (a ∷ b ∷ c ∷ d ∷ e ∷ f ∷ []) = refl

------------------------------------------------------------------------
-- N-4: Capstone — Bivector ↔ antisymmetric-TensorProduct bridge lands.
--
-- After this slice:
--
--   * bivector-to-tensor : Bivector → TensorProduct 4 4
--     Embeds a Bivector as an antisymmetric (= "symmetric T(i,j) =
--     T(j,i) with T(i,i) = 0" at F₂) tensor.
--
--   * tensor-to-bivector : TensorProduct 4 4 → Bivector
--     Extracts upper-triangular entries.
--
--   * bivector-tensor-roundtrip : refl-witness that the bridge is a
--     section (tensor-to-bivector ∘ bivector-to-tensor ≡ id).
--
-- The reverse round-trip (bivector-to-tensor ∘ tensor-to-bivector ≡ id)
-- would require T to be in the antisymmetric subspace — currently
-- not enforced by the TensorProduct 4 4 type, so the reverse holds
-- only on antisymmetric inputs. A subtype `AntisymmetricTensor n`
-- packaging the constraint would let us state both directions.
--
-- Substrate-wide consequence: HodgeDim4 work (Bivector, HodgeStar,
-- SelfDual, ReservedBridge) can be lifted to TensorProduct-level
-- reasoning via this bridge. The Hodge ★ at dim 4 — currently
-- defined as the index-reversal involution on Bivector (via
-- complement map in HodgeDim4.Bivector) — corresponds to a specific
-- transformation on the antisymmetric subspace of TensorProduct 4 4.
--
-- Per [[feedback-categorical-name-first]]: Bivector IS the substrate's
-- representation of Λ²(F₂⁴); the bridge connects it to the
-- TensorProduct-level reading where Λ²V = antisymmetric quotient of
-- V ⊗ V.
--
-- Deferred follow-ons:
--
--   * **AntisymmetricTensor n subtype**: package the antisymmetric
--     constraint as a Σ-type with the symmetry + diagonal-zero
--     witnesses. Enables stating both round-trip directions.
--
--   * **HodgeStar at TensorProduct level**: re-express the Hodge ★
--     involution as a transformation on antisymmetric subspaces of
--     TensorProduct 4 4 (= "swap (0,1)↔(2,3), (0,2)↔(1,3),
--     (0,3)↔(1,2)" — the complementary-position involution).
--
--   * **Generic Bivector at any n**: lift this dim-4 bridge to
--     arbitrary n via Bivector-n = Vec F₂ C(n, 2) ↔ antisymmetric
--     subspace of TensorProduct n n.
--
--   * **HodgeDim4 retrofit via this bridge**: existing
--     Bivector/HodgeStar/SelfDual/ReservedBridge work could cite
--     TensorProduct-level operations via the bridge. Substantial
--     refactor; opportunity for further unification.
------------------------------------------------------------------------
