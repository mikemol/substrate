{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CFMatrixBridge — ⟡N1b-Matrix-wire (DEFINITIONS): the
-- 2×2 CF matrix over ℕ, the CF step matrix M(a), 2×2 product, the convergent-state
-- matrix, and its determinant. The bridge THEOREMS (conv-step = matmul; det-flip
-- landed on the repo's own det4) are in the .Properties sibling (def/proof
-- separation: the R.Trace.Properties / Nat.Properties.Add imports live there).
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CFMatrixBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Algebra.Z using (ℤ)
open import Substrate.Algebra.Z.Add using (_⊖_)

-- the 2×2 CF matrix over the substrate's ℕ.
record Mat : Set where
  constructor mat
  field a b c d : ℕ
open Mat

I : Mat
I = mat (suc zero) zero zero (suc zero)

-- the CF step matrix M(a) = [[a,1],[1,0]] — det = −1, the num/den swap.
M : ℕ → Mat
M q = mat q (suc zero) (suc zero) zero

-- 2×2 product (scalar-on-left convention, so the CF step lands as a·p₁+p₀).
_·_ : Mat → Mat → Mat
(mat a b c d) · (mat e f g h) =
  mat (e * a + g * b) (f * a + h * b) (e * c + g * d) (f * c + h * d)

-- the convergent two-column state AS a matrix: [[p₁,p₀],[q₁,q₀]].
state : ℕ → ℕ → ℕ → ℕ → Mat
state p₁ q₁ p₀ q₀ = mat p₁ p₀ q₁ q₀

-- the matrix's determinant IS the substrate's det4 (definitional; see .Properties).
detM : Mat → ℤ
detM (mat a b c d) = (a * d) ⊖ (b * c)
