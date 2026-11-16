------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Id
--
-- Defines: idᵣ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Id where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Enumerate
open import Substrate.WitnessTower.FirstAppearance
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Hom



------------------------------------------------------------------------
-- S1 — THE CATEGORY. Identity = (refl, id-perm); composition trans-es the
-- grade witnesses and composes the permutations after transporting the source
-- perm up to the shared grade. The unit/associativity laws split cleanly: the
-- grade component by UIP, the perm component by the Sₙ group laws (SnGroup /
-- CyclicGrounding) modulo the transport-fusion lemmas above.
------------------------------------------------------------------------

idᵣ : (i : ℕ) → Homᵣ i i
idᵣ i = refl , id-perm i
