------------------------------------------------------------------------
-- Substrate.Category.TensorProduct.BCInstances.BivectorRoundtripBCSquare
--
-- Defines: bivector-roundtrip-BCSquare
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.TensorProduct.BCInstances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct.BCInstances.BivectorRoundtripBCSquare where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.AbsorbL
open import Substrate.Algebra.F2.AbsorbR
open import Substrate.Algebra.F2.Assoc
open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.F2Cases
open import Substrate.Algebra.F2.Idempotent
open import Substrate.Algebra.F2.IdentityL
open import Substrate.Algebra.F2.IdentityR
open import Substrate.Algebra.F2.InvOfOne
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.Op2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.PlusInverseL
open import Substrate.Algebra.F2.PlusInverseR
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.F2.ZeroNeqOne
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
open import Substrate.Algebra.F2.Polynomial.TensorProductView
open import Substrate.Algebra.F2.SymBilinForm.BilinForm
open import Substrate.Algebra.F2.SymBilinForm.BilinearFormOf
open import Substrate.Algebra.F2.SymBilinForm.TensorProductView
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
open import Substrate.Category.TensorProduct
open import Substrate.Category.BeckChevalley
open import Substrate.Category.TensorProduct.BCInstances.PolyMultBCSquare
open import Substrate.Category.TensorProduct.BCInstances.BilinformEvalBCSquare



------------------------------------------------------------------------
-- N-3: bivector-roundtrip-BCSquare — section BCSquare for Bivector ↔
-- TensorProduct 4 4. The section combinator says: extract ∘ embed ≡ id.
------------------------------------------------------------------------

bivector-roundtrip-BCSquare :
  BCSquare {A = Bivector}
           {B = TensorProduct 4 4}
           {C = Bivector}
           {D = Bivector}
           bivector-to-tensor
           (λ x → x)
           tensor-to-bivector
           (λ x → x)
bivector-roundtrip-BCSquare =
  section-BCSquare bivector-to-tensor tensor-to-bivector
    bivector-tensor-roundtrip

------------------------------------------------------------------------
-- N-4: Capstone — three BC instances, two combinators, one module.
--
-- The substrate's BC primitive #5 is load-bearing across:
--
--   #1 poly-mult-BCSquare        (factor-via-pair, *P-via-tensor-eq)
--   #2 bilinform-eval-BCSquare   (factor-via-pair, bilin-via-tensor-agrees)
--   #3 bivector-roundtrip-BCSquare (section, bivector-tensor-roundtrip)
--
-- Each is a one-line application of a named BC combinator. The cells
-- carry the universal-property content; the combinators carry the
-- categorical shape.
--
-- Per [[project-3plus1-parity-universal]]: each BCSquare's cell is the
-- structural content of the corresponding factorization or section.
--
-- Substrate-wide implication: any bilinear b : V → W → U factors
-- through TensorProduct via pair +F a unique linear b̃ (factor-via-pair);
-- any bridge with a one-sided round-trip closes as a section BCSquare
-- (section-BCSquare). The combinators name these universal-property
-- shapes; the instances apply them.
--
-- Deferred follow-ons:
--
--   * **Retraction BCSquare (other direction)**: bivector-to-tensor ∘
--     tensor-to-bivector ≡ id on the antisymmetric subspace of
--     TensorProduct 4 4. Requires the AntisymmetricTensor n subtype.
--
--   * **BC composition**: combinators for vertical / horizontal pasting
--     of BCSquares (the 2-cell calculus).
--
--   * **Adjunction-cell BCSquare**: an explicit combinator for "BC
--     square arising from an adjunction unit/counit" pattern, naming
--     factor-via-pair as one of its instances.
--
--   * **More instances**: dim-3 ↔ dim-4 SymBilinForm bridge,
--     ReservedBridge gauge family, V₄-orbit / chirality split, etc.
------------------------------------------------------------------------
