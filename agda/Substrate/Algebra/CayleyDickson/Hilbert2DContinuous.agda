------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Hilbert2DContinuous
--
-- ⊙.hilbert∀n (PARTIAL — the ∀n ENTRY invariant) — the structural foundation for
-- the ∀n continuity of the 2D Hilbert curve, generalizing the concrete
-- `Hilbert2D.hilbert-2-continuous`. DONE here: `hilbert-entry` — the curve starts
-- at (0,0) for EVERY order n (via `hilbert-head`: hilbert n = (0,0) ∷ …, since the
-- entry quadrant A = transpose fixes the origin).
--
-- SCOPED (the remaining continuity arc, ~100 lines): the EXIT recursion
-- (lastP hilbert n = (2ⁿ−1, 0) — needs lastP-peeling through the 4 quadrant
-- transforms, which are anonymous lambdas in Hilbert2D so a small refactor naming
-- A/B/C/D would un-fiddle it); a coordinate-BOUND invariant (coords < 2ⁿ); the 4
-- transforms as Manhattan ISOMETRIES (D's reflection needs the bounded-monus lemma
-- (k∸a)∸(k∸b) ≡ b∸a); and the Cont-++ seam assembly (the 3 seams = 1 from entry/exit).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Hilbert2DContinuous where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_)
open import Substrate.Foundation.Nat.Properties.Sub using (m∸m≡0)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Product using (Σ; _×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.CayleyDickson.Hilbert2D
  using (Pt; pow2; mapL; hilbert)

------------------------------------------------------------------------
-- 1. first / last of a point-list, and how they pass through ++ and mapL.
------------------------------------------------------------------------

firstP : List Pt → Pt
firstP []      = (0 , 0)
firstP (p ∷ _) = p

lastP : List Pt → Pt
lastP []           = (0 , 0)
lastP (p ∷ [])     = p
lastP (p ∷ q ∷ ps) = lastP (q ∷ ps)

-- first of (x ∷ xs) ++ ys is the head of the left list.
firstP-++ : (p : Pt) (xs ys : List Pt) → firstP ((p ∷ xs) ++ ys) ≡ p
firstP-++ p xs ys = refl

-- last of xs ++ (q ∷ ys) is the last of the right list (the left can't be last).
lastP-++ : (xs : List Pt) (q : Pt) (ys : List Pt) → lastP (xs ++ q ∷ ys) ≡ lastP (q ∷ ys)
lastP-++ []           q ys = refl
lastP-++ (p ∷ [])     q ys = refl
lastP-++ (p ∷ r ∷ rs) q ys = lastP-++ (r ∷ rs) q ys

firstP-mapL : (f : Pt → Pt) (p : Pt) (xs : List Pt) → firstP (mapL f (p ∷ xs)) ≡ f p
firstP-mapL f p xs = refl

lastP-mapL : (f : Pt → Pt) (p : Pt) (xs : List Pt) → lastP (mapL f (p ∷ xs)) ≡ f (lastP (p ∷ xs))
lastP-mapL f p []        = refl
lastP-mapL f p (q ∷ qs)  = lastP-mapL f q qs

------------------------------------------------------------------------
-- 2. The entry/exit recursion: hilbert n starts (0,0), ends (2ⁿ−1, 0).
------------------------------------------------------------------------

-- hilbert n is non-empty AND its head is (0,0): the curve starts at the origin
-- for every order. (A = transpose fixes (0,0); the other quadrants follow it.)
hilbert-head : (n : ℕ) → Σ (List Pt) (λ ys → hilbert n ≡ (0 , 0) ∷ ys)
hilbert-head zero    = [] , refl
hilbert-head (suc n) with hilbert-head n
... | ys , eq rewrite eq = _ , refl

-- the entry point of hilbert n is (0,0), for every n.
hilbert-entry : (n : ℕ) → firstP (hilbert n) ≡ (0 , 0)
hilbert-entry n with hilbert-head n
... | ys , eq rewrite eq = refl
