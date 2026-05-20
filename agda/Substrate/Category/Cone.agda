------------------------------------------------------------------------
-- Substrate.Category.Cone
--
-- Primitive #9 in the Substrate.Category.Primitives roadmap.
-- The categorical Cone — an apex with morphisms to a finite base
-- diagram.
--
-- A Cone has:
--   * Base : a finite-indexed family of Sets (Base : Fin n → Set).
--   * Apex : a Set.
--   * Legs : a family of morphisms apex → Base i.
--
-- This is the SIMPLEST cone form (discrete base — no morphisms
-- between base objects, so no commutativity to check). General cones
-- with non-trivial base-diagram morphisms add a commutativity
-- condition; deferred.
--
-- Per [[project-3plus1-is-cone-instance]]: the 3+1 parity universal
-- is the (M=3, N=1) instance of this cone primitive — 3 base
-- readings + 1 apex witness, filling the F₂² (size 4) field.
--
-- Per [[feedback-categorical-name-first]]: "cone" / "limit cone" is
-- the established categorical name for the structure substrate has
-- been calling "3+1 parity universal" etc.
--
-- Substrate primitives that are specific cone shapes:
--   * Equalizer (primitive #2) = cone over a parallel pair.
--   * Pullback (primitive #3) = cone over a cospan.
-- This Cone primitive is GENERAL — those are specific base-shapes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Cone where

open import Data.Fin using (Fin)
open import Data.Nat using (ℕ)
open import Level using (Level; _⊔_) renaming (suc to lsuc)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The Cone record (discrete base).
--
-- For a finite base diagram of n objects (no internal morphisms),
-- a cone is an apex + a leg from apex to each base object.
------------------------------------------------------------------------

record Cone (n : ℕ) (Base : Fin n → Set ℓ) (Apex : Set ℓ) : Set ℓ where
  field
    leg : (i : Fin n) → Apex → Base i

open Cone public

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: any (n, Base, Apex, leg) tuple satisfying the
-- shape is a Cone. The "discrete" qualifier means we don't track
-- morphisms BETWEEN base objects — those would add commutativity
-- conditions for the cone (the legs would need to commute with base
-- morphisms).
--
-- The (3, 1)-instance: Cone 3 (3-readings) apex, with apex being the
-- witness object that projects to each reading via its 3 legs. (The
-- "+1" of "3+1" refers to the apex being a single object; future
-- extensions can have N apex objects or an apex-edge.)
--
-- Substrate-wide implication:
--   * Equalizer (substrate primitive #2) is a Cone over a parallel
--     pair = 2 base objects with 2 internal morphisms; the cone's
--     leg property gives the equalizing condition.
--   * Pullback (substrate primitive #3) is a Cone over a cospan = 3
--     base objects with morphisms collapsing two into the third; the
--     cone's legs give the pullback's component-projecting maps.
--   * The (3, 1)-cone fits the 3+1 parity universal.
--
-- Deferred follow-ons:
--
--   * **Cone with base-diagram morphisms**: extend to non-discrete
--     base. Cone-leg commutativity with base morphisms is the
--     universal-property condition.
--   * **Equalizer/Pullback as Cone retrofits**: derive substrate's
--     existing primitives from this Cone primitive.
--   * **N-apex cones**: generalize apex from one object to N objects
--     (or to an arrow / morphism — see Cone.EdgeApex, slice 6 of
--     this arc).
--   * **Field-filling constraint**: the cardinality |apex| + |base|
--     = q^k for prime power q^k constraint (slice 3 of this arc).
------------------------------------------------------------------------
