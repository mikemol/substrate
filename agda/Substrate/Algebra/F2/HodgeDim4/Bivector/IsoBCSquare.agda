------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.IsoBCSquare
--
-- The Bivector ↔ TensorProduct 4 4 bridge as a pair of BCSquares
-- (section + retraction), witnessing the bridge is an iso on the
-- antisymmetric subspace.
--
-- After the BCSquare combinators in Substrate.Category.BeckChevalley
-- (section-BCSquare and retraction-BCSquare added in slice 9), this
-- module instantiates BOTH directions of the Bivector ↔ AntisymTensor
-- iso:
--
--   * section: tensor-to-bivector ∘ bivector-to-tensor ≡ id on Bivector
--     — always holds (refl after pattern-matching on Bivector).
--   * retraction-on-tensor: bivector-to-tensor ∘ tensor-to-bivector ≡ id
--     on the underlying tensor of any AntisymmetricTensor 4 input
--     — holds via tensor-bivector-roundtrip (slice 7).
--
-- This is the substrate's first iso instance of a categorical bridge:
-- both round-trips close, packaging the bridge as a full
-- isomorphism on the antisymmetric subspace.
--
-- Note on the subtype-level iso: a full iso AT THE AntisymmetricTensor
-- record level would require record equality, which without K
-- (--without-K) means the witnesses must be equal — and Π-type
-- witness equality requires function extensionality. We work at the
-- UNDERLYING tensor field instead; the iso on the subtype is implicit
-- (record equality is determined by tensor-field equality on
-- inhabitants of the antisymmetric subspace).
--
-- Per [[project-3plus1-parity-universal]]: the 6-dim Bivector IS the
-- 6-dim antisymmetric subspace of TensorProduct 4 4. The iso
-- witnesses identify them at the substrate level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.IsoBCSquare where

open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
  using (bivector-to-tensor; tensor-to-bivector; bivector-tensor-roundtrip)
open import Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip
  using (tensor-bivector-roundtrip)
open import Substrate.Category.TensorProduct using (TensorProduct)
open import Substrate.Category.TensorProduct.AntisymmetricTensor
  using (AntisymmetricTensor; tensor)
open import Substrate.Category.BeckChevalley
  using (BCSquare; bc-trivial; section-BCSquare)

------------------------------------------------------------------------
-- N-1: section-BCSquare for the bridge — bivector-to-tensor is a
-- section (always-true direction).
--
-- A = Bivector, B = TensorProduct 4 4, C = D = Bivector.
-- Square:
--   bivector-to-tensor : A → B
--   id                  : A → C
--   tensor-to-bivector  : B → D
--   id                  : C → D
-- Cell: tensor-to-bivector (bivector-to-tensor v) ≡ v
--       (bivector-tensor-roundtrip).
------------------------------------------------------------------------

bivector-iso-section-BCSquare :
  BCSquare {A = Bivector} {B = TensorProduct 4 4}
           {C = Bivector} {D = Bivector}
           bivector-to-tensor
           (λ x → x)
           tensor-to-bivector
           (λ x → x)
bivector-iso-section-BCSquare =
  section-BCSquare bivector-to-tensor tensor-to-bivector
                   bivector-tensor-roundtrip

------------------------------------------------------------------------
-- N-2: retraction-BCSquare for the bridge — at the underlying-tensor
-- level, the round-trip closes for antisymmetric inputs.
--
-- A = AntisymmetricTensor 4 (= the subtype packaging an antisymmetric
-- input), B = D = TensorProduct 4 4, C = AntisymmetricTensor 4.
-- Square:
--   tensor : A → B            (project the underlying tensor)
--   id     : A → C
--   bivector-to-tensor ∘ tensor-to-bivector : B → D  (round-trip)
--   tensor : C → D            (project the underlying tensor)
-- Cell: bivector-to-tensor (tensor-to-bivector (tensor T)) ≡ tensor T
--       (tensor-bivector-roundtrip).
--
-- Note: this is NOT a retraction-BCSquare combinator instance
-- because the retraction-BCSquare combinator wants A and B as the
-- "outer" types directly. Here we use bc-trivial with the projection
-- `tensor` doing the structural work.
------------------------------------------------------------------------

bivector-iso-retraction-on-tensor-BCSquare :
  BCSquare {A = AntisymmetricTensor 4} {B = TensorProduct 4 4}
           {C = AntisymmetricTensor 4} {D = TensorProduct 4 4}
           tensor
           (λ x → x)
           (λ T → bivector-to-tensor (tensor-to-bivector T))
           tensor
bivector-iso-retraction-on-tensor-BCSquare =
  bc-trivial tensor (λ x → x)
             (λ T → bivector-to-tensor (tensor-to-bivector T))
             tensor
             tensor-bivector-roundtrip

------------------------------------------------------------------------
-- N-3: Capstone — substrate's first iso-as-BC-pair instance.
--
-- After this slice:
--
--   * bivector-iso-section-BCSquare — section direction.
--   * bivector-iso-retraction-on-tensor-BCSquare — retraction
--     direction (at the underlying-tensor level, on antisymmetric inputs).
--
-- Together they witness that the Bivector ↔ TensorProduct 4 4 bridge
-- is an ISOMORPHISM on the antisymmetric subspace. The categorical
-- reading: Λ²(F₂⁴) ≅ Bivector at dim 4, with the bridge as the
-- explicit isomorphism.
--
-- Closes the BC-asymmetry deferred follow-on from BCInstances.
--
-- Per [[project-3plus1-parity-universal]]: 6-dim Bivector IS 6-dim
-- antisymmetric subspace. The iso-as-BC-pair makes the identification
-- substantive at the categorical level.
--
-- Per [[feedback-categorical-name-first]]: "iso" is the categorical
-- name; packaging it as a section + retraction pair of BCSquares
-- aligns with the Beck-Chevalley universal property reading rather
-- than inventing a substrate-local "Bivector ≅ AntisymTensor"
-- record.
--
-- Deferred follow-ons:
--
--   * **BCIso record**: a Σ-type packaging section + retraction
--     BCSquares as a single iso witness. Would let downstream code
--     pattern-match on the iso pair.
--
--   * **Subtype-level iso**: full record-level equality
--     `antisymmetric-from-bivector (tensor-to-bivector (tensor T)) ≡ T`
--     requires K or function extensionality on the witnesses.
--     Deferred per the substrate's --without-K discipline.
--
--   * **Generic Λ²V ↔ Bivector-n iso**: lift this dim-4 iso to
--     arbitrary n via Bivector-n = Vec F₂ C(n, 2) ↔ AntisymTensor n.
------------------------------------------------------------------------
