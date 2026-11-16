------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Oplusobj
--
-- Defines: ⊕objₚ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Oplusobj where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Vec.Properties.LookupComptabulate
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.WitnessTower.SnGroup
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
open import Substrate.WitnessTower.Wedge.OrientationSumComm
open import Substrate.WitnessTower.Wedge.OrientationProductComm
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Obj



------------------------------------------------------------------------
-- S3 — THE TWO OBJECT-MONOID PRODUCTS. Objₚ is grade-⊤, so both products are
-- the trivial GradedProductOver: the object monoid is degenerate, and ALL of
-- the rig's non-trivial symmetry lives in the Sₙ morphisms (S2).
------------------------------------------------------------------------

⊕objₚ : GradedProductOver _ℕ+_ 0 Objₚ
⊕objₚ = record { u = ⋆ ; _∧_ = λ _ _ → ⋆ }
