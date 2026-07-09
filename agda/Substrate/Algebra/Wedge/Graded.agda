------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Graded
--
-- THE GRADED WEDGE — the indexed lift of Algebra.Wedge.DivStr. The plain
-- DivStr has an UN-indexed carrier C : Set and a non-dependent recon :
-- C → C → C → C; that is exactly what blocked founding the WitnessTower as
-- a single DivStr (WitnessTower.Wedge.Action's obstruction note): the rung
-- step's base is a Perm n and its remainder a Fin (suc n), both indexed by
-- the SAME grade n — a link an un-indexed carrier cannot hold.
--
-- The fix is to make THE INDEX THE GRADE: a ℕ-graded carrier C : ℕ → Set,
-- a per-grade remainder/digit type R : ℕ → Set, and a grade-RAISING
-- reconstruction recon n : C n → R n → C (suc n). Then the rung step is a
-- single graded wedge, not a per-rung family — and the grade index is the
-- handle the grading conjectures (#2/#3/#4) hang on.
--
-- NOT "plain DivStr ⊂ GradedWedge" (a former overclaim — there is no such
-- degenerate embedding; the plain recon C→C→C→C and the grade-raising recon
-- C n → R n → C (suc n) are different shapes). The relation between the plain
-- and graded wedges is the FORMAL ALLEGORY: graded descent is the Φ-chain
-- refinement of `Category.Allegory.Refinement` (ALG-7), as F₂.Polynomial.Wedge.
-- TraceDescent realises it for F₂[x]. The allegory, not an embedding, is the
-- bridge between the two grades.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Graded where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; sym)

------------------------------------------------------------------------
-- 1. The graded carrier interface: a ℕ-graded carrier + a grade-raising
--    reconstruction from a base (grade n) and a digit (the remainder R n).
------------------------------------------------------------------------

-- ⟡set1-paydown: the ℕ-graded carrier family C : ℕ → Set and the remainder
-- family R : ℕ → Set are Set-VALUED families, so — per the substrate stance
-- (families are module params, never fields, [[set1-carrier-always-parameterize]])
-- — they become module parameters, not record fields. GradedDivStr then drops
-- Set₁ → Set; consumers write `GradedDivStr C R`, and the old `C G` / `R G`
-- projections are replaced by the parameters C / R directly (`recon G` stays a
-- field projection).
module _ (C : ℕ → Set) (R : ℕ → Set) where

  record GradedDivStr : Set where
    field
      recon : (n : ℕ) → C n → R n → C (suc n)    -- the grade-raising reconstruction

  open GradedDivStr public

------------------------------------------------------------------------
-- 2. The graded wedge: a grade-(n+1) element a, decomposed against a base
--    b at grade n by a remainder rem, with witness a ≡ recon n b rem.
--    (C R inferred implicitly from the GradedDivStr argument.)
------------------------------------------------------------------------

module _ {C : ℕ → Set} {R : ℕ → Set} where

  record GradedWedge (G : GradedDivStr C R) (n : ℕ)
                     (a : C (suc n)) (b : C n) : Set where
    field
      rem      : R n
      wedge-eq : a ≡ recon G n b rem

  open GradedWedge public

  ----------------------------------------------------------------------
  -- 3. The reads — the graded projections, matching the plain wedge's.
  ----------------------------------------------------------------------

  -- FORGETFUL: evaluate the witness back to the grade-(n+1) element.
  gforget : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n} →
            GradedWedge G n a b → C (suc n)
  gforget {G} {n} {b = b} w = recon G n b (rem w)

  gforget-correct : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n}
                    (w : GradedWedge G n a b) → gforget w ≡ a
  gforget-correct w = sym (wedge-eq w)

  -- PRESENTED: keep the remainder = the cell = the grade-n digit.
  gcell : {G : GradedDivStr C R} {n : ℕ} {a : C (suc n)} {b : C n} →
          GradedWedge G n a b → R n
  gcell w = rem w
