------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatSym.PermUIP
--
-- Defines: perm-UIP
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatSym; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatSym.PermUIP where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec.Properties.EqDec
open import Substrate.Foundation.Vec.Properties.Private
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Assoc
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Comp
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom2
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.HomEq
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Id
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.LeftId
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.LookupSubst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Obj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Oplusobj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.OrientationRigCatPerm
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Otimesobj
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Private
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.RightId
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstCompose
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFinUip
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstFuse
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstIdperm
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.SubstSymL
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.UipNat
open import Substrate.Foundation.Eq
open import Substrate.WitnessTower.Wedge.OrientationRigCatSym.Private



------------------------------------------------------------------------
-- S0 — Perm n is a SET (UIP). Vec (Fin n) n has decidable equality
-- (≡-dec on Fin _≟ᶠ_), so Hedberg gives uniqueness of identity proofs. This
-- is what makes the Iso round-trip proofs a proposition — no funext.
------------------------------------------------------------------------

perm-UIP : {n : ℕ} {σ τ : Perm n} (p q : σ ≡ τ) → p ≡ q
perm-UIP {n} = Decidable⇒UIP (≡-dec (_≟ᶠ_ {n}))
