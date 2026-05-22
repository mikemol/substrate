------------------------------------------------------------------------
-- Substrate.Category.Comonoid
--
-- MK1: a comonoid in a symmetric monoidal category C is an object X
-- equipped with a comultiplication Δ : X → X ⊗ X and a counit
-- ε : X → I satisfying the dual of the monoid laws (coassociativity,
-- counit).
--
-- Foundation for Markov categories (MK3): every object in a Markov
-- category carries a commutative comonoid structure (copy + delete).
--
-- Per [[categorical-name-first]]: comonoid is standard category
-- theory; this is the substrate-friendly capture.
-- Per the DBE constructive-completeness criterion: the record carries
-- (Carrier, comult, counit) — enough to invoke both operations on
-- any element of the carrier.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonoid where

open import Level using (Level) renaming (suc to lsuc)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- A comonoid record parameterised by:
--   Tensor : the binary tensor functor's action on objects
--   Unit   : the monoidal unit object
--
-- Given these, a comonoid on X consists of:
--   comult : X → Tensor X X      (comultiplication / copy)
--   counit : X → Unit             (counit / delete)
--
-- Laws (coassociativity, counit) stated structurally; concrete
-- instances supply equations.

record Comonoid
       (Carrier : Set ℓ)
       (Tensor : Set ℓ → Set ℓ → Set ℓ)
       (Unit : Set ℓ) : Set ℓ where
  field
    comult : Carrier → Tensor Carrier Carrier
    counit : Carrier → Unit

open Comonoid public

------------------------------------------------------------------------
-- The substrate's interpretation:
-- in a Markov category, Tensor = ⊗ (cartesian product or tensor of
-- probability spaces), Unit = terminal object (the singleton). The
-- comultiplication is the "copy" morphism that duplicates an object's
-- state; the counit is the "delete" / marginalise morphism.
--
-- Per [[coalgebraic-not-consumer-driven]]: comonoids are coalgebras
-- for the "duplicate" comonad on C — coalgebraic structure at the
-- lowest level, suitable to compose monadic structures on top.
------------------------------------------------------------------------
