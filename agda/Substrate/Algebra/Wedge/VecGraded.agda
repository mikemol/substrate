------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.VecGraded
--
-- Vec A founded as a GRADED wedge-carrier (Algebra.Wedge.Graded) — a silo top
-- (the shred's UNFOUNDED Vec, adjacent to ℕ) brought into the wedge
-- architecture. The grade is the LENGTH; the shed residue at each step is the
-- HEAD:
--   C n     = Vec A n
--   R n     = A                 the head to shed / prepend
--   recon n = a ∷_             cons the head onto the grade-n tail
--
-- Building a vector = consing heads = the graded free construction, exactly the
-- shape of WitnessTower.Wedge.Graded.tower-graded (Perm / insert-at) but with a
-- constant remainder type. Unconsing = the graded wedge: a (suc n)-vector
-- decomposes against its tail, shedding its head as the residue.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.VecGraded where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Vec using (Vec; _∷_; tail)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Wedge.Graded
  using (GradedDivStr; GradedWedge; recon; gforget; gcell)

------------------------------------------------------------------------
-- 1. Vec A as a graded wedge-carrier: C = Vec A, R = const A, recon = cons.
------------------------------------------------------------------------

-- ⟡set1-paydown: the graded families are now GradedDivStr's params (Vec A, const A).
vec-graded : (A : Set) → GradedDivStr (Vec A) (λ _ → A)
vec-graded A = record { recon = λ n v a → a ∷ v }

-- recon IS cons, definitionally.
recon-is-cons : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
                recon (vec-graded A) n v a ≡ a ∷ v
recon-is-cons A n v a = refl

------------------------------------------------------------------------
-- 2. The graded wedge = unconsing: a (suc n)-vector wedges against its tail,
--    shedding its head as the residue.
------------------------------------------------------------------------

-- the canonical step: a ∷ v wedges against v at head a.
vec-step : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
           GradedWedge (vec-graded A) n (a ∷ v) v
vec-step A n v a = record { rem = a ; wedge-eq = refl }

-- every nonempty vector IS its head consed on its tail — the uncons wedge.
vec-uncons : (A : Set) (n : ℕ) (v : Vec A (suc n)) →
             GradedWedge (vec-graded A) n v (tail v)
vec-uncons A n (a ∷ v) = record { rem = a ; wedge-eq = refl }

-- the cell read = the shed head; the forgetful read recovers the vector.
vec-cell : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
           gcell (vec-step A n v a) ≡ a
vec-cell A n v a = refl

vec-forget : (A : Set) (n : ℕ) (v : Vec A n) (a : A) →
             gforget (vec-step A n v a) ≡ a ∷ v
vec-forget A n v a = refl
