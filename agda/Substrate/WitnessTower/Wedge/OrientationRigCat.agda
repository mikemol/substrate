------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCat
--
-- ⟡rig-UP-cat-graded — THE Set₀-GRADED RIG CATEGORY (the arc's 6th "same
-- move": dissolve the Set₁ carrier by PARAMETERIZATION).
--
-- Category.SymmetricMonoidal lands in Set (lsuc …) ONLY because CategoryOf
-- FIELDS `Obj : Set` (the set1-carrier-always-parameterize trap).
-- Category.Site already shows the fix: PARAMETERIZE Obj/Hom (module params,
-- not fields). Applied here, GRADED: the objects are indexed by grades
-- (Obj : ℕ → Set) and the morphisms are a grade-respecting Hom family. Then
-- the rig-category structure — the category (id, ∘, laws), the two monoidal
-- products on objects (⊕ over (ℕ,+,0), ⊗ over (ℕ,*,1)), and the braidings
-- as morphisms — is a record that TYPE-CHECKS AT `Set` (NOT Set (lsuc …)).
-- That green compile at `: Set` IS the dissolution.
--
-- HONEST SCOPE: this is the FORMALIZABLE (Set₀-graded) categorical
-- structure — a DIFFERENT theorem than the Set₁ one (initiality quantified
-- over large rig CATEGORIES, an irreducible grade-collapse). The claim is
-- precisely: the rig-category structure is Set₀ WHEN Obj/Hom are
-- parameterized. It is NOT "eliminated THE Set₁".
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCat where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; _∧_; u)

------------------------------------------------------------------------
-- S1 — THE DISSOLUTION. Obj and Hom are MODULE PARAMETERS (mirroring
-- Category.Site's CoverData), so no Set-valued FIELD forces the record up
-- a universe. The bundle lands in `Set`.
--
--   Obj : ℕ → Set                       -- objects, indexed by grade
--   Hom : {i j} → Obj i → Obj j → Set   -- grade-respecting morphisms
--
-- The two object-level products reuse the committed GradedProductOver:
--   ⊕obj : GradedProductOver _+_ 0 Obj   (the additive monoid on objects)
--   ⊗obj : GradedProductOver _*_ 1 Obj   (the multiplicative monoid)
-- Their unit/combine are `u`/`_∧_` from OrientationBimonoidal.
--
-- The braidings are genuine MORPHISMS (not the Fin-level index swaps): for
-- a : Obj i, b : Obj j the additive braiding is a Hom (a⊕b) (b⊕a). Because
-- a⊕b : Obj (i+j) and b⊕a : Obj (j+i) are DISTINCT graded objects, the two
-- half-braids compose to an endomorphism with no transport, so the
-- symmetry law is stated cleanly as an involution against idHom.
------------------------------------------------------------------------

record GradedRigCat
  (Obj : ℕ → Set)
  (Hom : {i j : ℕ} → Obj i → Obj j → Set) : Set where
  field
    ----------------------------------------------------------------
    -- the category
    ----------------------------------------------------------------
    idHom : {i : ℕ} (a : Obj i) → Hom a a
    _∘_   : {i j k : ℕ} {a : Obj i} {b : Obj j} {c : Obj k} →
            Hom b c → Hom a b → Hom a c
    left-id  : {i j : ℕ} {a : Obj i} {b : Obj j} (f : Hom a b) →
               (idHom b ∘ f) ≡ f
    right-id : {i j : ℕ} {a : Obj i} {b : Obj j} (f : Hom a b) →
               (f ∘ idHom a) ≡ f
    assoc    : {i j k l : ℕ}
               {a : Obj i} {b : Obj j} {c : Obj k} {d : Obj l}
               (f : Hom a b) (g : Hom b c) (h : Hom c d) →
               ((h ∘ g) ∘ f) ≡ (h ∘ (g ∘ f))

    ----------------------------------------------------------------
    -- the two monoidal products ON OBJECTS (the rig, decategorified
    -- onto the object monoid): ⊕ over (ℕ,+,0), ⊗ over (ℕ,*,1).
    ----------------------------------------------------------------
    ⊕obj : GradedProductOver _+_ 0 Obj
    ⊗obj : GradedProductOver _*_ 1 Obj

    ----------------------------------------------------------------
    -- the braidings AS MORPHISMS, with the symmetry (involution) law.
    ----------------------------------------------------------------
    braid⊕ : {i j : ℕ} (a : Obj i) (b : Obj j) →
             Hom (_∧_ ⊕obj a b) (_∧_ ⊕obj b a)
    braid⊗ : {i j : ℕ} (a : Obj i) (b : Obj j) →
             Hom (_∧_ ⊗obj a b) (_∧_ ⊗obj b a)
    braid⊕-invol : {i j : ℕ} (a : Obj i) (b : Obj j) →
                   (braid⊕ b a ∘ braid⊕ a b) ≡ idHom (_∧_ ⊕obj a b)
    braid⊗-invol : {i j : ℕ} (a : Obj i) (b : Obj j) →
                   (braid⊗ b a ∘ braid⊗ a b) ≡ idHom (_∧_ ⊗obj a b)

open GradedRigCat public

-- grade-indexed singleton object: ⋆ {n} : Objₛ n, and n is a parameter
-- of the type, so the grade is recoverable (unlike ⊤, which erases it).
-- Proof-free (the object family of the skeletal instance); the inhabiting
-- rig-category over it — which needs +-comm / *-comm / Hedberg UIP — lives
-- in .Properties.orientationRigCatₛ.
data Objₛ (n : ℕ) : Set where
  ⋆ : Objₛ n
