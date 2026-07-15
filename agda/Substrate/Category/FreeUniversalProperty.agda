------------------------------------------------------------------------
-- Substrate.Category.FreeUniversalProperty
--
-- The center, stated ONCE with CONTENT: the universal property of a free
-- construction — Free ⊣ Forgetful in universal-arrow form. This is the
-- thing the substrate keeps rediscovering (Coxeter Word = free monoid,
-- the witness tower's word presentation, FreeLinearization = free module,
-- UPTerm = free term algebra, FreeOverBasis = the shared shape). They are
-- all instances of ONE universal property; this names it.
--
-- WHAT WAS ALREADY THERE (so this is naming, not invention):
--   * Substrate.Category.UniversalProperty.UPArrow — the universal-
--     property-as-arrow (Source/Target/Witness span). The center's SHAPE.
--   * Substrate.Category.FreeOverBasis — the free SHAPE (basis B, carrier
--     F, unit η) + AlgebraClass (Has-structure / Hom-preserves).
-- WHAT WAS MISSING: the universal property itself — the EXISTS-UNIQUE
--   structure-preserving extension — was deferred "per-instance" and never
--   stated with content. The UPArrow Free/Adjunction instances
--   (UniversalProperty.Instances) are ⊤-placeholders (Source = Target = ⊤),
--   partly a level artifact (UPArrow.Source : Set can't hold the
--   polymorphic free UP, whose targets range over all structured Sets).
--
-- This module states it with content, reusing the existing AlgebraClass:
--   unit η : B → F, F is structured, and for ANY structured target M and
--   map f : B → M there is a UNIQUE structure-preserving extension
--   `extend` (= Eval, the semantics map) with extend ∘ η ≡ f.
--
-- The syntax/semantics reading (the substrate's Term/record/Eval pattern):
--   F = the free/SYNTACTIC carrier (the Term), η = generators-in,
--   extend = Eval (the unique map to any SEMANTIC denotation M).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeUniversalProperty where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Category.FreeOverBasis
  using (AlgebraClass; Has-structure; Hom-preserves; trivial-AlgebraClass;
         FreeOverBasis; mkFreeOverBasis)
open import Substrate.Category.UniversalProperty using (UPArrowP; mkUP)

------------------------------------------------------------------------
-- 1. THE CENTER. Free ⊣ Forgetful, universal-arrow form, with content.
--    Parametric in an AlgebraClass A (the "structure": Monoid, F₂-Module,
--    CCC, …), a basis B, and a free carrier F.
------------------------------------------------------------------------

record FreeUP (A : AlgebraClass) (B : Set) (F : Set) : Set₁ where
  field
    -- the unit: generators embed into the free carrier (η).
    unit     : B → F
    -- the free carrier itself carries the structure.
    free-has : Has-structure A F

    -- THE universal property: every map from the basis into a structured
    -- target extends to a structure-preserving map out of F …
    extend   : {M : Set} → Has-structure A M → (B → M) → (F → M)
    extend-preserves :
      {M : Set} (hM : Has-structure A M) (f : B → M) →
      Hom-preserves A free-has hM (extend hM f)
    -- … the extension agrees with f on generators (extend ∘ η ≡ f) …
    extend-extends :
      {M : Set} (hM : Has-structure A M) (f : B → M) (b : B) →
      extend hM f (unit b) ≡ f b
    -- … and it is the UNIQUE such structure-preserving extension.
    extend-unique :
      {M : Set} (hM : Has-structure A M) (f : B → M)
      (g : F → M) → Hom-preserves A free-has hM g →
      ((b : B) → g (unit b) ≡ f b) →
      (x : F) → g x ≡ extend hM f x

open FreeUP public

------------------------------------------------------------------------
-- 2. A FreeUP forgets to the existing free SHAPE (so the catalogue's
--    FreeOverBasis is exactly the data of a FreeUP minus the property).
------------------------------------------------------------------------

FreeUP→FreeOverBasis : {A : AlgebraClass} {B F : Set} →
                       FreeUP A B F → FreeOverBasis B F
FreeUP→FreeOverBasis fr = mkFreeOverBasis (unit fr)

------------------------------------------------------------------------
-- 3. A FreeUP IS a (content-bearing) UPArrow, at each structured target.
--    This repairs the ⊤-placeholder: the solve-relation is real — "g
--    extends f along the unit". (Per-target, to stay in Set: the global
--    polymorphic version is the FreeUP record itself, in Set₁.)
--      Source  = maps out of the basis        (the "problem")
--      Target  = maps out of the free carrier (the "candidate solution")
--      Witness = the candidate extends the problem along η.
------------------------------------------------------------------------

FreeUP-W : {A : AlgebraClass} {B F : Set} →
           FreeUP A B F → (M : Set) → (B → M) → (F → M) → Set
FreeUP-W {B = B} fr M f g = (b : B) → g (unit fr b) ≡ f b

FreeUP-UPArrow : {A : AlgebraClass} {B F : Set} →
                 (fr : FreeUP A B F) → (M : Set) →
                 UPArrowP (B → M) (F → M) (FreeUP-W fr M)
FreeUP-UPArrow fr M = mkUP

------------------------------------------------------------------------
-- 4. NON-VACUITY: the free Set on a set (the identity adjunction, Free ⊣
--    Forgetful for the trivial structure). F = B, η = id, Eval = the map
--    itself. Witnesses that FreeUP is inhabited with real content.
------------------------------------------------------------------------

free-Set : (B : Set) → FreeUP trivial-AlgebraClass B B
free-Set B = record
  { unit             = λ b → b
  ; free-has         = tt
  ; extend           = λ _ f → f
  ; extend-preserves = λ _ _ → tt
  ; extend-extends   = λ _ f b → refl
  ; extend-unique    = λ _ f g _ g-ext x → g-ext x
  }

------------------------------------------------------------------------
-- INSTANCES TO WIRE (the naming makes them visible as siblings, each a
-- FreeUP for its AlgebraClass — flagged, not built here):
--   * Coxeter.Word Gen      — FREE MONOID  (extend = fold; the classic
--                             free-monoid UP). The witness tower's word
--                             presentation factors through this.
--   * FreeLinearization     — FREE F₂-MODULE (extend = linear-from-images).
--   * UPTerm                — FREE TERM ALGEBRA over UPGen (extend = Eval).
-- Each becomes "a FreeUP A B F" for its A, so the parallel rediscoveries
-- collapse to one center with per-structure instances.
------------------------------------------------------------------------
