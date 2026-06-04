------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product
--
-- THE COMMON STRUCTURE of DivStr and GradedDivStr (find it, recursively): the
-- WEDGE PRODUCT — a ℕ-graded carrier with a unit and a 2-input/1-output product
-- whose output grade is the SUM of the input grades (degrees add, like the
-- exterior algebra wedge ∧). A graded monoid.
--
--   _∧_ : C i → C j → C (i + j)     two input dimensions (i, j), one output (i+j)
--
-- THE THREE LENSES the user named, all realised here:
--   * "wedge product, two input dimensions, one output dimension" — _∧_ itself;
--     the three grades (i, j, i+j) are the three degrees of freedom, and forcing
--     each gives a different DivStr-slice.
--   * "each QUOTE is a signal to lift by a grade" — quote = the term-algebra's
--     Free step / an associativity bracket. `power b q : C q` is the q-DEEP TERM:
--     each ∧ is one quote/bracket, lifting the grade by one. AND the division
--     QUOTIENT MAY BE THE SAME THING (user): "q copies of b" (the wedge's
--     quotient) IS exactly this q-deep term b ∧ b ∧ ⋯ — count and quote-depth
--     are one. Witnessed for Vec by power-replicate (q copies = replicate q a =
--     the q-deep ∧-term [a]^∧q). So quotient = quote = grade: three names for one
--     operation — division-count, term-bracket-depth, and exterior degree.
--   * "DivStr is GradedDivStr with a DOF forced to zero, flattening folded into
--     the residue" — GradedDivStr is the +1-step slice (j forced to 1: each step
--     wedges with a grade-1 increment); plain DivStr collapses all grades to a
--     point and the lost grade reappears as the count q in the residue. The
--     +1-step derivation is `graded-of-product`; the full grade-collapse-to-plain
--     (q as the folded grade) is the next brick.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Product where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; _++_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)

------------------------------------------------------------------------
-- 1. The wedge product: a ℕ-graded carrier with unit and a degree-adding
--    2-in/1-out product (a graded monoid).
------------------------------------------------------------------------

record GradedProduct : Set₁ where
  field
    C   : ℕ → Set
    u   : C 0                              -- the grade-0 unit (the empty wedge)
    _∧_ : {i j : ℕ} → C i → C j → C (i + j)

open GradedProduct public

------------------------------------------------------------------------
-- 2. quot q = lift by q grades: the q-fold wedge of a grade-1 generator.
--    "q copies of b" of the plain wedge, with the quotient as the grade.
------------------------------------------------------------------------

power : (P : GradedProduct) (b : C P 1) (q : ℕ) → C P q
power P b zero    = u P
power P b (suc n) = _∧_ P b (power P b n)

-- the general q-deep term of a grade-i element: C (q * i). (power is i = 1.)
gpower : (P : GradedProduct) {i : ℕ} (b : C P i) (q : ℕ) → C P (q * i)
gpower P b zero    = u P
gpower P b (suc n) = _∧_ P b (gpower P b n)

------------------------------------------------------------------------
-- 3. GradedDivStr is the +1-step slice: each step wedges with a grade-1
--    increment (on the left, so the output grade 1 + n = suc n). The residue
--    type is the grade-1 part — the increment.
------------------------------------------------------------------------

graded-of-product : GradedProduct → GradedDivStr
graded-of-product P = record
  { C = C P ; R = λ _ → C P 1 ; recon = λ n b r → _∧_ P r b }

------------------------------------------------------------------------
-- 4. Vec is the wedge product on append: _∧_ = _++_, unit = []. Then the
--    q-fold wedge of a singleton is q copies (replicate), and the +1-step
--    recon recovers cons.
------------------------------------------------------------------------

vec-product : (A : Set) → GradedProduct
vec-product A = record { C = Vec A ; u = [] ; _∧_ = _++_ }

-- QUOTIENT = QUOTE, witnessed: the division "q copies of a" equals the q-deep
-- ∧-term [a]^∧q equals replicate q a. The wedge's count and the term-algebra's
-- bracket-depth are the same operation.
power-replicate : (A : Set) (a : A) (q : ℕ) →
                  power (vec-product A) (a ∷ []) q ≡ replicate q a
power-replicate A a zero    = refl
power-replicate A a (suc n) = cong (a ∷_) (power-replicate A a n)

-- the +1-step recon recovers cons: prepending the singleton [a] = consing a.
vec-recon-cons : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
                 GradedDivStr.recon (graded-of-product (vec-product A)) n v (a ∷ []) ≡ a ∷ v
vec-recon-cons A n v a = refl

------------------------------------------------------------------------
-- 5. DivStr is the FLATTENED wedge product: collapse the grade into the carrier
--    (Σ ℕ C — the grade folded into the element, i.e. the residue), the count q
--    becoming the grade lifted. recon q (i,b) (j,r) = the q-deep term of b,
--    then r. So a plain DivStr is GradedProduct with the grade DOF folded away.
--    (flatten (vec-product A) ≅ List-div: Σ ℕ Vec ≅ List, q copies ++ r.)
------------------------------------------------------------------------

flatten-recon : (P : GradedProduct) → ℕ → Σ ℕ (C P) → Σ ℕ (C P) → Σ ℕ (C P)
flatten-recon P q (i , b) (j , r) = (q * i) + j , _∧_ P (gpower P b q) r

flatten : GradedProduct → DivStr
flatten P = record { C = Σ ℕ (C P) ; z = 0 , u P ; recon = flatten-recon P }
