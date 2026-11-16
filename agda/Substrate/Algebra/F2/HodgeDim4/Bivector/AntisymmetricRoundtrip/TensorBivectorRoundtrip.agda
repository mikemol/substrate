------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.TensorBivectorRoundtrip
--
-- Defines: tensor-bivector-roundtrip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.TensorBivectorRoundtrip where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Vec
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
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
open import Substrate.Category.TensorProduct
open import Substrate.Category.TensorProduct.AntisymmetricTensor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Sym
open import Substrate.Algebra.F2.HodgeDim4.Bivector.AntisymmetricRoundtrip.TensorBivectorRoundtripRaw



------------------------------------------------------------------------
-- N-2: tensor-bivector-roundtrip — subtype version.
--
-- The AntisymmetricTensor subtype carries the symmetry +F diagonal-
-- zero witnesses by construction; the round-trip restated at the
-- subtype is a one-line wrapper around the raw version.
------------------------------------------------------------------------

tensor-bivector-roundtrip :
  (T : AntisymmetricTensor 4) →
  bivector-to-tensor (tensor-to-bivector (tensor T)) ≡ tensor T
tensor-bivector-roundtrip T =
  tensor-bivector-roundtrip-raw (tensor T) (symmetric T) (diag-zero T)

------------------------------------------------------------------------
-- N-3: Capstone — reverse round-trip closes.
--
-- After this slice, the Bivector ↔ TensorProduct 4 4 bridge is a
-- BIJECTION on the antisymmetric subspace:
--
--   bivector-tensor-roundtrip : tensor-to-bivector ∘ bivector-to-tensor ≡ id
--   tensor-bivector-roundtrip : bivector-to-tensor ∘ tensor-to-bivector ≡ id
--     (on AntisymmetricTensor 4 inputs)
--
-- The two directions package together as the substrate's first
-- iso-BCSquare instance (slice 10).
--
-- Per [[project-3plus1-parity-universal]]: the 6-dim Bivector at F₂⁴
-- IS the 6-dim antisymmetric subspace of TensorProduct 4 4 — same
-- categorical object via two presentations. The bridge is the
-- identification.
------------------------------------------------------------------------
