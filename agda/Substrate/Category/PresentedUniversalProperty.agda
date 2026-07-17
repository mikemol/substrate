------------------------------------------------------------------------
-- Substrate.Category.PresentedUniversalProperty
--
-- The quotient half of the center: a PRESENTATION = free object modulo
-- relations, with the COEQUALIZER universal property. Together with
-- Category.FreeUniversalProperty (the free half) this is the colimit side
-- of the center; the limit/cofree dual is Category.Cone.
--
--   Free(generators)  ──quotient──▶  Presented = Free / relations
--
-- The universal property (stated once, with content, mirroring FreeUP):
-- for any structured target M and any A-HOMOMORPHISM h : F → M that
-- RESPECTS the relations (h (lhs r) ≡ h (rhs r)), there is a UNIQUE
-- A-hom factor : P → M with factor ∘ quotient ≡ h.
--
-- Realization note (--without-K, no HITs per the cubical discipline): a
-- quotient SET F/R is not formable, so the presented object P is given
-- concretely per-instance (canonical representatives) with quotient = the
-- normalization onto them. THIS IS EXACTLY Coxeter.Core's (Word, normalize,
-- Canonical) interface — so Coxeter.Core IS the quotient half, and Cyclic
-- (Word·one-gen / aⁿ⁺¹) and a future Sₙ-as-type-A (Word·transpositions /
-- braid) are its instances, both "free-then-quotient".
--
-- Relations are given in pair form: R indexes relations, lhs/rhs : R → F
-- their two sides (so the coequalizer is of lhs, rhs : R ⇉ F).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PresentedUniversalProperty where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Category.FreeOverBasis
  using (AlgebraClass; Has-structure; Hom-preserves; trivial-AlgebraClass)
open import Substrate.Category.UniversalProperty using (UPArrowP; mkUP)

------------------------------------------------------------------------
-- 1. THE QUOTIENT CENTER. Coequalizer of lhs, rhs : R ⇉ F in A-algebras.
------------------------------------------------------------------------

-- ⟡rc-algebraclass-chain (⟡set1-rerank2): the ∀-over-Set obligations (factor + its
-- three laws) forced the record to Set₁; they are PARAMETERS now, and quotient/
-- pres-has move with them (the laws cite both). The two Set₀ obligations that cite
-- only params (quotient-hom, quotient-respects) REMAIN fields — the record keeps
-- real content and drops to Set.
record PresentedUP
  {Has : Set → Set}
  {HomP : {M N : Set} → Has M → Has N → (M → N) → Set}
  (A : AlgebraClass Has HomP)
  (F : Set) (F-has : Has-structure A F)     -- the free object (an A-algebra)
  (R : Set) (lhs rhs : R → F)               -- the relations
  (P : Set)                                 -- the presented object (canonical reps)
  (quotient : F → P)
  (pres-has : Has-structure A P)
  -- the universal property: a relation-respecting A-hom factors uniquely.
  (factor :
      {M : Set} (hM : Has-structure A M)
      (h : F → M) → Hom-preserves A F-has hM h →
      ((r : R) → h (lhs r) ≡ h (rhs r)) → (P → M))
  (factor-preserves :
      {M : Set} (hM : Has-structure A M)
      (h : F → M) (hh : Hom-preserves A F-has hM h)
      (hr : (r : R) → h (lhs r) ≡ h (rhs r)) →
      Hom-preserves A pres-has hM (factor hM h hh hr))
  (factor-factors :
      {M : Set} (hM : Has-structure A M)
      (h : F → M) (hh : Hom-preserves A F-has hM h)
      (hr : (r : R) → h (lhs r) ≡ h (rhs r)) (x : F) →
      factor hM h hh hr (quotient x) ≡ h x)
  (factor-unique :
      {M : Set} (hM : Has-structure A M)
      (h : F → M) (hh : Hom-preserves A F-has hM h)
      (hr : (r : R) → h (lhs r) ≡ h (rhs r))
      (k : P → M) → Hom-preserves A pres-has hM k →
      ((x : F) → k (quotient x) ≡ h x) →
      (y : P) → k y ≡ factor hM h hh hr y)
  : Set where
  field
    quotient-hom      : Hom-preserves A F-has pres-has quotient
    quotient-respects : (r : R) → quotient (lhs r) ≡ quotient (rhs r)

open PresentedUP public

------------------------------------------------------------------------
-- 2. Free = the EMPTY presentation (no relations). P = F, quotient = id.
--    Shows free is the R = ⊥ instance — the two halves connect. (id-is-hom
--    is per-AlgebraClass, so it's a hypothesis, not assumed.)
------------------------------------------------------------------------

Free-as-Presented :
  {Has : Set → Set}
  {HomP : {M N : Set} → Has M → Has N → (M → N) → Set}
  {A : AlgebraClass Has HomP} {F : Set} (F-has : Has-structure A F) →
  Hom-preserves A F-has F-has (λ x → x) →
  PresentedUP A F F-has ⊥ (λ ()) (λ ()) F
    (λ x → x)
    F-has
    (λ _ h _ _ → h)
    (λ _ _ hh _ → hh)
    (λ _ _ _ _ _ → refl)
    (λ _ _ _ _ k _ k-ext y → k-ext y)
Free-as-Presented {A = A} {F} F-has id-hom = record
  { quotient-hom      = id-hom
  ; quotient-respects = λ ()
  }

------------------------------------------------------------------------
-- 3. Non-vacuity: the empty presentation over the trivial AlgebraClass
--    (everything ⊤). Concrete inhabitant with no per-class obligations.
------------------------------------------------------------------------

presented-Set : (F : Set) → PresentedUP trivial-AlgebraClass F tt ⊥ (λ ()) (λ ()) F
    (λ x → x) tt (λ _ h _ _ → h) (λ _ _ hh _ → hh)
    (λ _ _ _ _ _ → refl) (λ _ _ _ _ k _ k-ext y → k-ext y)
presented-Set F = Free-as-Presented {A = trivial-AlgebraClass} {F} tt tt

------------------------------------------------------------------------
-- 4. A PresentedUP IS a content-bearing UPArrow, per target M.
--      Source  = maps out of the free object F        (the "problem")
--      Target  = maps out of the presented object P   (the "solution")
--      Witness = the solution factors the problem through the quotient.
------------------------------------------------------------------------

PresentedUP-W :
  {F : Set} {P : Set} →
  (F → P) → (M : Set) → (F → M) → (P → M) → Set
PresentedUP-W {F = F} quotient M h k = (x : F) → k (quotient x) ≡ h x

PresentedUP-UPArrow :
  {F : Set} {P : Set} →
  (quotient : F → P) → (M : Set) →
  UPArrowP (F → M) (P → M) (PresentedUP-W quotient M)
PresentedUP-UPArrow quotient M = mkUP

------------------------------------------------------------------------
-- INSTANCES TO WIRE (visible as "free-then-quotient" siblings):
--   * Coxeter.Cyclic n  — Word(one gen) / (aⁿ⁺¹ = ε); P = canonical
--                         a^0..a^n, quotient = normalize. The substrate's
--                         existing Coxeter.Core normalize/Canonical data
--                         IS this PresentedUP's (P, quotient, factor).
--   * Sₙ as type Aₙ₋₁   — Word(transpositions) / braid relations; the
--                         witness-tower Sₙ is the ACTION of this presented
--                         group (Cayley, via WitnessTower.SymBridge).
-- Free half: [[project_center_free_universal_property]] (FreeUP;
-- Coxeter.Word proved free monoid). Limit/cofree dual: Category.Cone.
------------------------------------------------------------------------
