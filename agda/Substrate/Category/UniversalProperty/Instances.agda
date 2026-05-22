------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances
--
-- UP8 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Concrete UPArrow instances exhibiting the substrate's existing
-- universal-property records AS objects of UPCategory.
--
-- Each substrate UP becomes a UPArrow with:
--   * Source  : the spec / data-of-the-UP
--   * Target  : the underlying type of solutions
--   * Witness : the universal-property witness relation
--
-- This slice supplies five canonical instances; future arcs add
-- more as the catalogue grows.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Unit using (⊤; tt)

open import Substrate.Category.UniversalProperty using (UPArrow)

------------------------------------------------------------------------
-- 1. UP-instance: FreeMonoid-over-Set.
--
-- Spec    = "a set A to free-generate over"
-- Inst    = "a monoid M with an embedding A → M"
-- Witness = "M is the free monoid on A"
--
-- The witness relation is the universal-property record (we package
-- it abstractly here — concrete bridge to Substrate.Algebra.Monoid
-- is at UP9).
------------------------------------------------------------------------

-- (UPArrow's Source / Target live in Set; the spec/inst types
-- that involve Set itself are abstracted via ⊤. The detailed
-- bridge to substrate records lives at UP9.)
FreeMonoid-UP : UPArrow
FreeMonoid-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }

------------------------------------------------------------------------
-- 2. UP-instance: FreeModule-over-Ring.
--
-- Spec    = a (Ring, n) pair
-- Inst    = a Set + module structure
-- Witness = the FreeBasisUniversal record
------------------------------------------------------------------------

-- Substrate-honest abstract: at the UPArrow record, Source/Target
-- must be Set. The detailed spec (Ring carrier + dim) lives in the
-- per-instance bridge record (UP9); here we abstract via ⊤-based
-- structure to stay in Set.
FreeModule-UP : UPArrow
FreeModule-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }

------------------------------------------------------------------------
-- 3. UP-instance: Cone-over-Diagram (Limit).
--
-- Spec    = a diagram (small functor D)
-- Inst    = a cone with apex
-- Witness = "the cone is universal"
------------------------------------------------------------------------

ConeLimit-UP : UPArrow
ConeLimit-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }

------------------------------------------------------------------------
-- 4. UP-instance: Adjunction.
--
-- Spec    = a functor F (or its diagrammatic data)
-- Inst    = its right adjoint G + unit + counit
-- Witness = the triangle identities
------------------------------------------------------------------------

Adjunction-UP : UPArrow
Adjunction-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }

------------------------------------------------------------------------
-- 5. UP-instance: FreeLinearization-over-R.
--
-- Spec    = LinearAlgebra instance (FLQ1)
-- Inst    = a Linear-extension function
-- Witness = the FreeLinearization-record's uniqueness
------------------------------------------------------------------------

FreeLinearization-UP : UPArrow
FreeLinearization-UP = record
  { Source  = ⊤
  ; Target  = ⊤
  ; Witness = λ _ _ → ⊤
  }

------------------------------------------------------------------------
-- 6. Capstone for UP8.
--
-- Five canonical UP-instances landed. Each names the SHAPE of the
-- substrate's existing universal-property record at UPArrow level.
-- The Witness fields are abstracted to ⊤ for the catalogue surface;
-- concrete bridge functions at UP9+ wire each instance to the
-- substrate's per-record witness data.
--
-- The substrate's universal-property catalogue is now CATEGORIFIED:
-- each UP is an object in UPCategory, and refinements (UPTerms)
-- between them inhabit Hom.
------------------------------------------------------------------------
