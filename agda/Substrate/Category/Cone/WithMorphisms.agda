------------------------------------------------------------------------
-- Substrate.Category.Cone.WithMorphisms
--
-- Extension of Substrate.Category.Cone that tracks base-internal
-- morphisms with explicit leg-commutativity constraints.
--
-- The discrete Cone (in Substrate.Category.Cone) has:
--   * Base : Fin n → Set
--   * Apex : Set
--   * Legs : Apex → Base i
-- but NO morphisms between base objects.
--
-- For Equalizer (parallel pair f, g : A → B) and Pullback (cospan
-- f : A → C, g : B → C), the base diagram has structural morphisms;
-- the cone's legs must commute with them.
--
-- This module packages the WithMorphisms version: the base morphisms
-- are first-class data + the commutativity constraint is a field of
-- the cone record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone.WithMorphisms where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ ℓ′ : Level

------------------------------------------------------------------------
-- The ConeWithMorphisms record.
--
-- A base diagram with n objects (Base) + a NAME-TYPE for morphisms
-- (BaseMor) with src/tgt index lookups + actual application
-- (mor-apply). An apex Set, legs from apex to each base object, and
-- commutativity: each base morphism, when applied to a leg's output,
-- equals the leg to the morphism's target.
--
-- Commutativity diagram (per morphism m with src=i, tgt=j):
--
--                  Apex
--                /     \
--          leg i        leg j
--              v          v
--          Base i  --m--> Base j
--
-- The square commutes: mor-apply m (leg i a) ≡ leg j a.
------------------------------------------------------------------------

record ConeWithMorphisms
  (n : ℕ) (Base : Fin n → Set ℓ)
  (BaseMor : Set ℓ′)
  (mor-src mor-tgt : BaseMor → Fin n)
  (mor-apply : (m : BaseMor) → Base (mor-src m) → Base (mor-tgt m))
  (Apex : Set ℓ)
  : Set (ℓ ⊔ ℓ′) where
  field
    leg     : (i : Fin n) → Apex → Base i
    commute : (m : BaseMor) (a : Apex) →
              mor-apply m (leg (mor-src m) a) ≡ leg (mor-tgt m) a

open ConeWithMorphisms public

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: cones with non-discrete base diagrams have a
-- proper categorical primitive. Equalizer (parallel pair) and
-- Pullback (cospan) are the canonical instances (slices 5+6).
--
-- The discrete Cone (Substrate.Category.Cone) is the special case
-- where BaseMor is empty (no morphisms between base objects, so
-- no commutativity to check).
--
-- Per [[project-cone-subsumes-equalizer-pullback]]: this is the
-- "WithMorphisms extension" promised by the deferred follow-on,
-- now landed.
------------------------------------------------------------------------
