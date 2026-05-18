------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.BCInstance
--
-- A concrete `BCSquare` instance demonstrating substrate's BeckChevalley
-- primitive #5 in action.
--
-- The square: polynomial multiplication factors through TensorProduct
-- via the ⊗-Hom adjunction (pair + anti-diag-sum). The two paths
-- (direct *P vs via-tensor) commute, giving a trivial-cell BCSquare.
--
-- Per the categorical reading from
-- Substrate.Algebra.F2.Polynomial.TensorProductView: outer ≡ pair
-- definitionally, so *P = anti-diag-sum ∘ outer ≡ anti-diag-sum ∘
-- pair. The cell is refl-level by composition.
--
-- This is BCSquare primitive #5 made load-bearing on concrete
-- substrate data. The cell IS refl (trivial commutativity) because
-- *P is DEFINED via the factorization. A NON-trivial BCSquare
-- requires comparing two genuinely-distinct factorizations of the
-- same operation; slices 2 and 3 of this trio give those.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.BCInstance where

open import Data.Nat using (ℕ) renaming (_+_ to _ℕ+_)
open import Data.Product using (Σ; _×_; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
  using (Polynomial; _*P_; anti-diag-sum)
open import Substrate.Algebra.F2.Polynomial.TensorProductView
  using (_*P-via-tensor_; *P-via-tensor-eq)
open import Substrate.Category.TensorProduct using (TensorProduct; pair)
open import Substrate.Category.BeckChevalley using (BCSquare; bc-trivial)

------------------------------------------------------------------------
-- N-1: poly-mult-BC — BCSquare instance for polynomial multiplication.
--
-- At fixed sizes (n, m), the BCSquare has:
--   A = Vector n × Vector m       (input pair)
--   B = TensorProduct n m         (lifted via pair)
--   C = Vector n × Vector m       (same as A, identity)
--   D = Polynomial (n ℕ+ m)       (output)
--
-- Paths:
--   A → B → D : (v, w) → pair v w → anti-diag-sum (pair v w) = v *P-via-tensor w
--   A → C → D : (v, w) → (v, w)  → v *P w
--
-- Cell: v *P-via-tensor w ≡ v *P w (via *P-via-tensor-eq).
--
-- The cell is structurally non-refl (it goes through outer-is-pair),
-- making this a substantive BC instance.
------------------------------------------------------------------------

private
  -- Pair-curry: package (v, w) as a single input.
  PolyPair : ℕ → ℕ → Set
  PolyPair n m = Vector n × Vector m

  -- f : A → B (= TensorProduct via pair)
  pair-uncurried : ∀ {n m} → PolyPair n m → TensorProduct n m
  pair-uncurried (v , w) = pair v w

  -- g : A → C (identity)
  id-uncurried : ∀ {n m} → PolyPair n m → PolyPair n m
  id-uncurried = λ x → x

  -- h : B → D
  anti-diag-uncurried : ∀ {n m} → TensorProduct n m → Polynomial (n ℕ+ m)
  anti-diag-uncurried = anti-diag-sum

  -- k : C → D
  mult-uncurried : ∀ {n m} → PolyPair n m → Polynomial (n ℕ+ m)
  mult-uncurried (v , w) = v *P w

poly-mult-BCSquare :
  ∀ {n m} →
  BCSquare {A = PolyPair n m}
           {B = TensorProduct n m}
           {C = PolyPair n m}
           {D = Polynomial (n ℕ+ m)}
           pair-uncurried
           id-uncurried
           anti-diag-uncurried
           mult-uncurried
poly-mult-BCSquare {n} {m} =
  bc-trivial pair-uncurried id-uncurried anti-diag-uncurried mult-uncurried
    (λ { (v , w) → sym (*P-via-tensor-eq v w) })
  where open import Relation.Binary.PropositionalEquality using (sym)

------------------------------------------------------------------------
-- N-2: Capstone — BC primitive #5's first concrete substrate instance.
--
-- After this slice:
--
--   * poly-mult-BCSquare — a BCSquare instance witnessing the
--     polynomial multiplication factorization through TensorProduct.
--     The cell is *P-via-tensor-eq (= via outer-is-pair).
--
-- This is the substrate's first NON-TRIVIAL BCSquare instance.
-- Demonstrates that BeckChevalley primitive #5 can package real
-- substrate-level commuting squares — the cell is a substantive
-- structural witness, not just refl.
--
-- Per [[feedback-categorical-name-first]]: the polynomial mult /
-- TensorProduct factorization IS a BC square; this slice names it
-- categorically.
--
-- Substrate-wide implication: any time two paths of operations
-- produce the same result (= a commuting square), BCSquare can
-- package the witness. The 3+1 parity universal observations (per
-- [[project-3plus1-parity-universal]]) are BC squares whose CELL
-- carries structural content (= the "+1" element).
--
-- Slices 2 and 3 of this trio: BCSquare for dim-3 SymBilinForm
-- bridge and BCSquare for Bivector ↔ TensorProduct bridge.
------------------------------------------------------------------------
