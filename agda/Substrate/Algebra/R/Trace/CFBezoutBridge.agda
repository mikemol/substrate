{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CFBezoutBridge — ⟡N1b-Matrix-bezout (DEFINITIONS):
-- the 2×2 ℤ-matrix, the inverse CF-step matrix M(q)⁻¹, and its action on a
-- coefficient column. The bridge THEOREM (act (Minv q) = step-bezout's update) is
-- in the .Properties sibling (def/proof separation: the Z.Properties* imports live
-- there). See .Properties for `bezout-step-is-Minv`.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CFBezoutBridge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_; 0ℤ; 1ℤ)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)

-- a 2×2 matrix over ℤ, and its action on a coefficient column (s, t).
record Matℤ : Set where
  constructor mat
  field a b c d : ℤ
open Matℤ

-- M(q)⁻¹ = [[0,1],[1,−q]] : the inverse CF-step matrix (det −1, the swap).
Minv : ℕ → Matℤ
Minv q = mat 0ℤ 1ℤ 1ℤ (-ℤ (+ q))

-- action on a column: [[a,b],[c,d]] · (s,t) = (a·s + b·t, c·s + d·t).
act : Matℤ → (ℤ × ℤ) → (ℤ × ℤ)
act (mat a b c d) (s , t) = ((a *ℤ s) +ℤ (b *ℤ t)) , ((c *ℤ s) +ℤ (d *ℤ t))
