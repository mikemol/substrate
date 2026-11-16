------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.HodgeStarOnTensor
--
-- Defines: hodge-star-on-tensor
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.HodgeStarOnTensor where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Fin.Cover
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Product
open import Substrate.Groups.Coxeter.CanonicalCover
open import Substrate.Foundation.Eq
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
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.Bivector.TensorProductBridge
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar
open import Substrate.Category.TensorProduct.AntisymmetricTensor
open import Substrate.Algebra.F2.HodgeDim4.Bivector.HodgeStarOnTensor.AntisymmetricFromBivector



------------------------------------------------------------------------
-- N-3: hodge-star-on-tensor — Hodge ★ lifted to AntisymmetricTensor 4.
--
-- Route through the bridge: descend to Bivector, apply hodge-star,
-- ascend back to AntisymmetricTensor 4. The output is automatically
-- antisymmetric (bivector-to-tensor's image always is).
------------------------------------------------------------------------

hodge-star-on-tensor : AntisymmetricTensor 4 → AntisymmetricTensor 4
hodge-star-on-tensor T =
  antisymmetric-from-bivector (apply hodge-star (tensor-to-bivector (tensor T)))

------------------------------------------------------------------------
-- N-4: Capstone — Hodge ★ at the TensorProduct level.
--
-- After this slice:
--
--   * antisymmetric-from-bivector : Bivector → AntisymmetricTensor 4
--     packages any Bivector as an antisymmetric tensor.
--
--   * hodge-star-on-tensor : AntisymmetricTensor 4 → AntisymmetricTensor 4
--     applies Hodge ★ at the TensorProduct level.
--
-- Substrate-wide consequence: any HodgeDim4 work that operated on
-- Bivector can now be re-expressed at the AntisymTensor level via
-- this lift. The complement-position involution is now first-class
-- at the TensorProduct level.
--
-- Per [[project-torsion-element-universal]]: hodge-star-on-tensor
-- inherits hodge-star's order-2 structure via the bridge round-trips.
-- The HasOrder witness at the TensorProduct level lifts cleanly
-- through tensor-bivector-roundtrip +F bivector-tensor-roundtrip.
--
-- Deferred follow-ons:
--
--   * **HasOrder-hodge-star-on-tensor**: lift HasOrder via the
--     bridge round-trips. Requires the AntisymTensor inner_~_ /
--     iterate equation to chase through the conversions.
--
--   * **Direct definition without bridge routing**: hodge-star-on-
--     tensor could be defined as a transformation of the underlying
--     tensor directly (swap rows i↔complement i and reshape). The
--     bridge-routed definition is the structural reading;
--     the direct definition would be a definitional / efficiency
--     optimisation.
------------------------------------------------------------------------
