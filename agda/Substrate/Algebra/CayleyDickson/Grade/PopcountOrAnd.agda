------------------------------------------------------------------------
-- C2 ℕ+ C4 at the DEGREE level: popcount(i∨j) ℕ+ popcount(i∧j) = popcount i ℕ+
-- popcount j. The defect popcount(i∧j) IS the cancellation; it is 0 exactly when
-- i,j have disjoint supports — i.e. when the degree grading is additive.
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.PopcountOrAnd where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Vec
open import Substrate.Algebra.CayleyDickson.Grade.Bit
open import Substrate.Algebra.CayleyDickson.Grade.Popcount
open import Substrate.Algebra.CayleyDickson.Grade.Shuffle
open import Substrate.Algebra.CayleyDickson.Grade.BitOrAnd
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans

popcount-or-and : (n : ℕ) (i j : Vec Bool n) →
                  popcount (zipWith _∨_ i j) ℕ+ popcount (zipWith _∧_ i j)
                  ≡ popcount i ℕ+ popcount j
popcount-or-and zero    []       []       = refl
popcount-or-and (suc n) (a ∷ is) (b ∷ js) =
  trans (shuffle (bit (a ∨ b)) (popcount (zipWith _∨_ is js))
                 (bit (a ∧ b)) (popcount (zipWith _∧_ is js)))
  (trans (cong₂ _ℕ+_ (bit-or-and a b) (popcount-or-and n is js))
         (shuffle (bit a) (bit b) (popcount is) (popcount js)))
