------------------------------------------------------------------------
-- Eliza.Orbit
--
-- The V₄-quotient cocycle structure: chambers fibre over orbits as the
-- 24 = 6 × 4 split per Substrate.Cocycles.V4Signature.
--
-- This is the eliza-side instantiation of the substrate's
-- IsomorphicCocycleStructure:
--
--   Invariant  = Orbit  (= Pairing × Chirality)
--   Gauge      = V₄     (acting on each fibre by translation)
--   Fiber i    = V₄     (regular representation; each fibre is a torsor)
--
-- The CONTRACT: every chamber decomposes uniquely as (orbit, fiber).
-- Stated as a Σ-type bijection.
--
-- Per Discipline Rule 5 (content-address by invariant only): any
-- semantically meaningful eliza output must depend only on `orbit-of`,
-- never on `fiber-of`. The OrbitsPanel + colour-coding in 17.py
-- realise this: top-by-orbit collapses the 4 fibres of each coset.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Orbit where

open import Eliza.Prelude   using (_×_; _,_; _≡_; refl)
open import Eliza.Alphabets using (Chamber; Orbit; V₄; e₄)
open import Eliza.Word      using (Word; map)

------------------------------------------------------------------------
-- 1. The two projections — postulated.
------------------------------------------------------------------------

postulate
  orbit-of  : Chamber → Orbit
  fiber-of  : Chamber → V₄

------------------------------------------------------------------------
-- 2. The reconstruction map. From (orbit, fiber) back to chamber.
------------------------------------------------------------------------

postulate
  chamber-of : Orbit → V₄ → Chamber

------------------------------------------------------------------------
-- 3. The bijection. The two round-trips compose to identity. This is
-- the cocycle's content: the chamber's data IS (orbit, fiber); nothing
-- else is gauge-relevant.
------------------------------------------------------------------------

postulate
  decompose :
    (x : Chamber) →
    chamber-of (orbit-of x) (fiber-of x) ≡ x

  reassemble-orbit :
    (o : Orbit) (v : V₄) →
    orbit-of (chamber-of o v) ≡ o

  reassemble-fiber :
    (o : Orbit) (v : V₄) →
    fiber-of (chamber-of o v) ≡ v

------------------------------------------------------------------------
-- 4. The V₄-action on chambers is "act on the fibre only" — exactly
-- the Substrate.Cocycle Downcast pattern.
------------------------------------------------------------------------

postulate
  v4-mul   : V₄ → V₄ → V₄  -- V₄'s group operation
  v4-act   : V₄ → Chamber → Chamber

  v4-act-fibers : (v : V₄) (x : Chamber) →
    orbit-of (v4-act v x) ≡ orbit-of x
  -- v4-act preserves the orbit, modifies only the fibre.

------------------------------------------------------------------------
-- 5. Lifting to Word: project a chamber-trajectory to an orbit-
-- trajectory. The substrate's Rule-1 lift `lift-from-invariant` at
-- Word level.
------------------------------------------------------------------------

project-trajectory : Word Chamber → Word Orbit
project-trajectory = map orbit-of
