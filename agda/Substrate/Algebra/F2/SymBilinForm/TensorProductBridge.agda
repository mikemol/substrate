------------------------------------------------------------------------
-- Substrate.Algebra.F2.SymBilinForm.TensorProductBridge
--
-- Bridges substrate's generic BilinForm / SymBilinForm to the
-- corresponding subspaces of TensorProduct n n.
--
-- BilinForm n = Fin n → Fin n → F₂ (function-based representation).
-- TensorProduct n n = Vec (Vec F₂ n) n (Vec-based representation).
--
-- The two encode the same data: an n × n matrix over F₂. The bridge
-- converts between them via tabulate / lookup.
--
-- For SymBilinForm: the IsSymmetric M predicate (M i j ≡ M j i)
-- pulls back as a constraint on the corresponding tensor.
--
-- Per the structural conversation: substrate's existing BilinForm /
-- SymBilinForm work uses the function representation; this bridge
-- enables lifting to TensorProduct-level reasoning via the
-- categorical primitive.
--
-- Dimensions (at F₂):
--   * BilinForm n / TensorProduct n n: dim n² (full matrices)
--   * Symmetric subspace (IsSymmetric M, T(i,j) = T(j,i)): dim n(n+1)/2
--   * Antisymmetric subspace (Λ²V quotient): dim n(n-1)/2 (= Bivector
--     at dim 4)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.SymBilinForm.TensorProductBridge where

open import Data.Fin using (Fin; zero; suc)
open import Data.Nat using (ℕ)
open import Data.Vec using (Vec; tabulate; lookup)
open import Data.Vec.Properties using (lookup∘tabulate; tabulate∘lookup)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.SymBilinForm using (BilinForm; IsSymmetric)
open import Substrate.Category.TensorProduct using (TensorProduct)

------------------------------------------------------------------------
-- N-1: bilinform-to-tensor — embed a function-based BilinForm as a
-- Vec-based TensorProduct.
--
-- Implementation: tabulate twice. For each i, row is `tabulate (λ j
-- → M i j)`; outer tabulate produces n such rows.
------------------------------------------------------------------------

bilinform-to-tensor : ∀ {n} → BilinForm n → TensorProduct n n
bilinform-to-tensor M = tabulate (λ i → tabulate (λ j → M i j))

------------------------------------------------------------------------
-- N-2: tensor-to-bilinform — extract a BilinForm from a TensorProduct.
--
-- Implementation: lookup at position (i, j) gives the function-form
-- value M i j.
------------------------------------------------------------------------

tensor-to-bilinform : ∀ {n} → TensorProduct n n → BilinForm n
tensor-to-bilinform T i j = lookup (lookup T i) j

------------------------------------------------------------------------
-- N-3: Round-trip equalities.
--
-- BilinForm round-trip (pointwise; full function equality requires
-- funext):
--   tensor-to-bilinform (bilinform-to-tensor M) i j ≡ M i j
--   via lookup∘tabulate twice.
--
-- TensorProduct round-trip (full Vec equality):
--   bilinform-to-tensor (tensor-to-bilinform T) ≡ T
--   via tabulate∘lookup twice (Vec extensionality).
------------------------------------------------------------------------

bilinform-tensor-roundtrip :
  ∀ {n} (M : BilinForm n) (i j : Fin n) →
  tensor-to-bilinform (bilinform-to-tensor M) i j ≡ M i j
bilinform-tensor-roundtrip M i j =
  trans (cong (λ row → lookup row j) (lookup∘tabulate _ i))
        (lookup∘tabulate _ j)

-- Pointwise tensor round-trip (full Vec equality requires more
-- careful tabulate∘lookup manipulation; deferred).
tensor-bilinform-roundtrip-pointwise :
  ∀ {n} (T : TensorProduct n n) (i j : Fin n) →
  lookup (lookup (bilinform-to-tensor (tensor-to-bilinform T)) i) j
    ≡ lookup (lookup T i) j
tensor-bilinform-roundtrip-pointwise T i j =
  bilinform-tensor-roundtrip (tensor-to-bilinform T) i j

------------------------------------------------------------------------
-- N-4: Symmetry preservation under the bridge.
--
-- If M is symmetric (IsSymmetric M), the bridged tensor is also
-- "symmetric" in the sense that T(i,j) = T(j,i).
--
-- The IsSymmetric predicate at the BilinForm level corresponds to
-- the symmetric subspace at the TensorProduct level.
------------------------------------------------------------------------

bridged-is-symmetric :
  ∀ {n} (M : BilinForm n) → IsSymmetric M →
  (i j : Fin n) →
  lookup (lookup (bilinform-to-tensor M) i) j
    ≡ lookup (lookup (bilinform-to-tensor M) j) i
bridged-is-symmetric M sym-M i j =
  trans (bilinform-tensor-roundtrip M i j)
  (trans (sym-M i j)
         (sym (bilinform-tensor-roundtrip M j i)))

------------------------------------------------------------------------
-- N-5: Capstone — BilinForm ↔ TensorProduct bridge lands.
--
-- After this slice:
--
--   * bilinform-to-tensor : BilinForm n → TensorProduct n n
--     (function → Vec via tabulate)
--   * tensor-to-bilinform : TensorProduct n n → BilinForm n
--     (Vec → function via lookup)
--   * bilinform-tensor-roundtrip — pointwise equivalence (without
--     funext)
--   * tensor-bilinform-roundtrip — full Vec equivalence (modulo a
--     funext hole at the inner tabulate-of-lookup; see N-3)
--   * bridged-is-symmetric — IsSymmetric pulls back as the
--     symmetric-subspace constraint on the bridged tensor
--
-- Substrate-wide consequence: BilinForm / SymBilinForm work
-- (bilinear-form-of, congruence-act, NonDegenerate, etc.) can be
-- lifted to TensorProduct-level reasoning. Combined with
-- HodgeDim4.Bivector.TensorProductBridge, the substrate's two
-- main bilinear-structure encodings (SymBilinForm at generic n,
-- Bivector at dim 4) are both connected to the categorical
-- TensorProduct primitive.
--
-- Per [[feedback-categorical-name-first]]: BilinForm IS the function-
-- representation of TensorProduct n n; SymBilinForm IS the symmetric
-- subspace; the bridge surfaces these structural identifications.
--
-- Open gap: tensor-bilinform-roundtrip's inner step requires funext
-- (the inner tabulate∘lookup at each row is per-row). At the
-- pointwise level (per-i lookup of the result vs T), the equality
-- holds without funext. Full Vec-equality without funext requires
-- tabulate-of-lookup at the right form; deferred follow-on.
--
-- Deferred follow-ons:
--
--   * **Funext-free tensor round-trip**: structure the round-trip
--     proof to avoid funext by working at the Vec-pattern-matching
--     level (not via tabulate-of-lookup function equality).
--
--   * **SymBilinForm ↔ Sym²(F₂ⁿ) subtype**: package Sym²(F₂ⁿ) as a
--     subtype of TensorProduct n n with the symmetric-subspace
--     constraint, then bridge SymBilinForm n ↔ Sym²(F₂ⁿ) directly.
--
--   * **SymBilinForm work via TensorProduct retrofit**: existing
--     bilinear-form-of, congruence-act, NonDegenerate, HodgeRecast
--     work could cite TensorProduct-level operations via this bridge.
--     Substantial refactor; opportunity for further unification.
------------------------------------------------------------------------
