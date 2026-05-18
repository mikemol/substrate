------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.BCInstance
--
-- A concrete `BCSquare` instance demonstrating substrate's
-- BeckChevalley primitive #5 in action — applied to the Bivector ↔
-- TensorProduct round-trip bridge.
--
-- The square: the round-trip
-- `tensor-to-bivector ∘ bivector-to-tensor ≡ id` packages as a
-- BCSquare whose cell is `bivector-tensor-roundtrip`.
--
-- Slice 3 of 3 in the BC-load-bearing trio. Completes the
-- "factorization through TensorProduct" instances for polynomial
-- multiplication, bilinear-form evaluation, and the antisymmetric
-- (Hodge dim-4) bridge.
--
-- Per [[feedback-categorical-name-first]]: the Hodge dim-4 Bivector
-- IS the antisymmetric quotient of TensorProduct 4 4; the bridge
-- round-trip IS a BC commuting square (= the "TensorProduct sees
-- Bivector" axis is a section).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.BCInstance where

open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
  using (bivector-to-tensor; tensor-to-bivector; bivector-tensor-roundtrip)
open import Substrate.Category.TensorProduct using (TensorProduct)
open import Substrate.Category.BeckChevalley using (BCSquare; bc-trivial)

------------------------------------------------------------------------
-- N-1: bivector-roundtrip-BCSquare — BCSquare for the Bivector ↔
-- TensorProduct section.
--
-- The square has:
--   A = Bivector                    (input)
--   B = TensorProduct 4 4           (lifted via bivector-to-tensor)
--   C = Bivector                    (identity)
--   D = Bivector                    (output)
--
-- Paths:
--   A → B → D : v → bivector-to-tensor v → tensor-to-bivector (... )
--   A → C → D : v → v → v   (identity)
--
-- Cell: tensor-to-bivector (bivector-to-tensor v) ≡ v
-- (via bivector-tensor-roundtrip).
--
-- This is a "section" BCSquare: the round-trip composition equals
-- the identity. The cell is refl-on-pattern-match (proof structure)
-- but conceptually NON-trivial: it states the round-trip closes.
------------------------------------------------------------------------

private
  embed : Bivector → TensorProduct 4 4
  embed = bivector-to-tensor

  id-Bivector : Bivector → Bivector
  id-Bivector = λ x → x

  extract : TensorProduct 4 4 → Bivector
  extract = tensor-to-bivector

bivector-roundtrip-BCSquare :
  BCSquare {A = Bivector}
           {B = TensorProduct 4 4}
           {C = Bivector}
           {D = Bivector}
           embed
           id-Bivector
           extract
           id-Bivector
bivector-roundtrip-BCSquare =
  bc-trivial embed id-Bivector extract id-Bivector
    bivector-tensor-roundtrip

------------------------------------------------------------------------
-- N-2: Capstone — BC primitive #5's third concrete substrate instance.
--
-- After this slice:
--
--   * bivector-roundtrip-BCSquare — a BCSquare instance witnessing
--     that extract ∘ embed ≡ id on Bivector at dim 4. The cell is
--     bivector-tensor-roundtrip.
--
-- Together with poly-mult-BCSquare (Slice 1) and
-- bilinform-eval-BCSquare (Slice 2), the substrate now has THREE
-- concrete BCSquare instances:
--
--   #1 polynomial multiplication via TensorProduct
--      (cell: *P-via-tensor-eq)
--   #2 bilinear-form evaluation via TensorProduct
--      (cell: bilinear-form-of-via-tensor-agrees)
--   #3 Bivector ↔ TensorProduct round-trip
--      (cell: bivector-tensor-roundtrip)
--
-- The three together make BeckChevalley primitive #5 LOAD-BEARING
-- across the substrate's three main bilinear/algebraic operations.
-- Each instance demonstrates a distinct flavor of BC structure:
--
--   * #1, #2 are "factorization-via-pair" squares (the ⊗-Hom
--     adjunction unit at specific bilinear maps).
--   * #3 is a "section-of-an-isomorphism" square (round-trip closure
--     of a bridge).
--
-- Per [[project-3plus1-parity-universal]]: each BCSquare's cell IS
-- the structural content that distinguishes the two paths. At a
-- substantive (non-refl) cell, the BC condition records the
-- categorical "quotient curvature" that the substrate's bridges
-- and factorizations witness.
--
-- Per [[project-tetrative-metacircularity]]: BCSquare provides a
-- uniform packaging for the substrate's structural-bridge work;
-- each meta-level's bridges land naturally as BCSquares whose cells
-- carry that level's specific structural content.
--
-- Deferred follow-ons:
--
--   * **BC composition**: prove that BCSquares compose along shared
--     edges (vertical / horizontal pasting). The categorical
--     calculus of BC 2-cells.
--
--   * **BC condition vs BC failure**: name explicitly when a
--     BCSquare's cell is iso (BC condition holds) vs structurally
--     non-trivial (BC failure 2-cell carries content).
--
--   * **Retrofit existing bridges**: re-express the dim-3 ↔ dim-4
--     SymBilinForm bridge, the ReservedBridge, the V₄-orbit /
--     chirality split, etc., as BCSquares with their respective
--     cells.
------------------------------------------------------------------------
