------------------------------------------------------------------------
-- Substrate.Algebra.F1.AsModule
--
-- F1m3 of the F₁-modules arc per [scratch/m_mod_arc_plan.md].
--
-- The categorical identification:
--
--   F₁-Module ≡ PointedSet
--   F₁-Module-Hom ≡ PointedSetMap
--
-- F₁ has no genuine scalars (only "0" as multiplicative-identity-
-- absent and a single trivial element); the action of F₁ on a
-- "module" reduces to selecting the basepoint. Equivalently:
-- F₁-modules are "sets with a basepoint, no addition, no scalar
-- multiplication."
--
-- Substrate-honest scope: we surface the EQUIVALENCE as named
-- structure. The "F₁-Module" type alias defaults to PointedSet;
-- "F₁-Module-Hom" defaults to PointedSetMap. The full categorical
-- equivalence (functor in both directions + identity on objects /
-- morphisms) is a propositional consequence at this slice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.AsModule where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Algebra.PointedSet using (PointedSet)
open import Substrate.Algebra.PointedSet.Map
  using (PointedSetMap; id-PointedSetMap; compose-PointedSetMap)

------------------------------------------------------------------------
-- 1. The categorical identification.
------------------------------------------------------------------------

-- ⟡set1-paydown: PointedSet is now the carrier-indexed family; F₁-Module and its
-- Hom / id / compose thread the carrier(s).
F₁-Module : Set → Set
F₁-Module = PointedSet

F₁-Module-Hom : {A B : Set} → F₁-Module A → F₁-Module B → Set
F₁-Module-Hom P Q = PointedSetMap P Q

------------------------------------------------------------------------
-- 2. The trivial F₁-Module (basepoint only).
------------------------------------------------------------------------

⊤-F₁-Module : F₁-Module ⊤
⊤-F₁-Module = Substrate.Algebra.PointedSet.⊤-Pointed

-- A cleaner shortcut: directly re-export.
open import Substrate.Algebra.PointedSet
  using (⊤-Pointed) public

------------------------------------------------------------------------
-- 3. Category structure on F₁-Module.
------------------------------------------------------------------------

id-F₁-Hom : {A : Set} (P : F₁-Module A) → F₁-Module-Hom P P
id-F₁-Hom = id-PointedSetMap

compose-F₁-Hom :
  {A B D : Set} {P : F₁-Module A} {Q : F₁-Module B} {R : F₁-Module D} →
  F₁-Module-Hom Q R →
  F₁-Module-Hom P Q →
  F₁-Module-Hom P R
compose-F₁-Hom = compose-PointedSetMap

------------------------------------------------------------------------
-- 4. Capstone for F1m3.
--
-- F₁-Module = PointedSet identified. The category of F₁-modules
-- IS the category of pointed sets. F1m4 builds GL(n, F₁) = Sₙ via
-- the basepoint-preserving bijections of (Fin (n+1), 0).
------------------------------------------------------------------------
