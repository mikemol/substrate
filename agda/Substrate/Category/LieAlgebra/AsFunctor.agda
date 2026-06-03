------------------------------------------------------------------------
-- Substrate.Category.LieAlgebra.AsFunctor
--
-- Substrate-level naming of the underlying-Lie functor Assoc → Lie.
--
-- M6 of the M-arc. Every associative algebra A carries a Lie-algebra
-- structure A_Lie with bracket [x, y] = xy - yx. This assignment is
-- functorial: an associative-algebra homomorphism f : A → B preserves
-- the commutator, so f also defines a Lie-morphism A_Lie → B_Lie.
--
-- The underlying-Lie functor U_Lie : Assoc → Lie is the RIGHT
-- ADJOINT to M7's universal enveloping algebra functor U : Lie →
-- Assoc:
--   Hom_Lie(L, U_Lie(A)) ≅ Hom_Assoc(U(L), A)
-- This is the substrate's first canonical adjunction at the algebra
-- level.
--
-- Per [[grothendieck-coherence-rule]]: this functor closes one half
-- of the M-arc's Lie/Assoc bridge; M7 closes the other half. Together
-- they witness the Lie ⊣ Assoc adjunction at the substrate functor
-- level.
--
-- Thin projection of [[Category.Functor.AsNamed]] (the AsNamed-family
-- cone witness); see that module for the shared functor-naming pattern.
-- This file supplies only the underlying-Lie-specific math.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.LieAlgebra.AsFunctor
  {ℓOA ℓMA ℓOL ℓML : Level}
  (Assoc : CategoryOf {ℓOA} {ℓMA})
  (Lie : CategoryOf {ℓOL} {ℓML})
  (U-Lie : Functor Assoc Lie)
  where

------------------------------------------------------------------------
-- 1. U-Lie as the substrate's named underlying-Lie functor.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  Assoc Lie U-Lie public
  renaming (named-Functor to UnderlyingLie-Functor)
------------------------------------------------------------------------
-- 2. Capstone — U_Lie : Assoc → Lie as a substrate Functor.
--
-- M6 of the M-arc. With M6 landed, the substrate has the
-- "associative-algebra-to-Lie-via-commutator" assignment as a
-- proper functor.
--
-- After M6 + M7 (U : Lie → Assoc), the substrate witnesses the
-- adjunction:
--   U ⊣ U_Lie
-- (= universal enveloping is left adjoint to underlying-Lie). This
-- IS the canonical Lie/Assoc adjunction in category theory; the
-- substrate's M6 + M7 name the two functors structurally.
--
-- Per [[universal-property-discipline]]: the FULL adjunction record
-- (with unit + counit + triangle identities) layers on top via the
-- substrate's existing Adjunction primitive (#4) — a downstream
-- slice composes M6 + M7 + Adjunction into the Lie ⊣ Assoc
-- adjunction object.
--
-- Concrete usage:
--   * Matrix algebras → matrix Lie algebras with commutator bracket
--     (= the standard sl_n, gl_n constructions)
--   * Group algebras → Lie algebras via "infinitesimal" structure
--     (deferred; requires more infrastructure)
--
-- Next: M7 UniversalEnvelopingAlgebra.AsFunctor (U : Lie → Assoc).
------------------------------------------------------------------------
