------------------------------------------------------------------------
-- The ANF of OR lifted to the F2^n index: the ANF/Reed-Muller monomial product
-- (union) equals the CD/Morton product (XOR) corrected by the AND overlap. The
-- two index-group ops coincide EXACTLY up to that overlap. (C4, index level.)
-- Context: Substrate/Algebra/CayleyDickson/Grade/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade.OrAnf where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Or
open import Substrate.Foundation.Bool.Xor
open import Substrate.Foundation.Bool.Properties.OrXorAnd
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong2

∨-anf : (n : ℕ) (i j : Vec Bool n) →
        zipWith _∨_ i j ≡ zipWith _xor_ (zipWith _xor_ i j) (zipWith _∧_ i j)
∨-anf zero    []       []       = refl
∨-anf (suc n) (a ∷ is) (b ∷ js) = cong₂ _∷_ (or-xor-and a b) (∨-anf n is js)
