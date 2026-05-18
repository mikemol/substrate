------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.TensorProductView
--
-- Demonstrates that polynomial multiplication's `outer` from
-- Substrate.Algebra.F2.Polynomial IS the `pair` (universal bilinear
-- map / unit of ⊗-Hom adjunction) from Substrate.Category.TensorProduct.
--
-- After this slice:
--   outer p q ≡ pair p q                            (definitionally)
--   _*P_ p q = anti-diag-sum (pair p q)             (via the bridge)
--
-- Per [[feedback-categorical-name-first]]: polynomial multiplication's
-- `outer` was named at the substrate's polynomial level; this slice
-- recognises it as a concrete instance of the categorical `pair`
-- (TensorProduct's universal map). The structural identity
-- `outer ≡ pair` makes the categorical handle visible at the use
-- site.
--
-- Slice 2 of 3 in the TensorProduct + EEA trio.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.TensorProductView where

open import Data.Nat using (ℕ) renaming (_+_ to _ℕ+_)
open import Data.Vec using (Vec; []; _∷_)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Polynomial
  using (Polynomial; _*P_; outer; anti-diag-sum)
open import Substrate.Category.TensorProduct
  using (TensorProduct; pair)

------------------------------------------------------------------------
-- N-1: outer IS pair — definitional equivalence.
--
-- Both `outer` (from Polynomial) and `pair` (from TensorProduct) are
-- defined as:
--   []      _ ↦ []
--   (a ∷ p) q ↦ (a *ₛ q) ∷ recurse
--
-- where outer uses `·c` (the polynomial-named scalar mul) and pair
-- uses `*ₛ` (the Vector-named scalar mul) — but `·c` is defined as
-- `*ₛ` in Polynomial.agda. So outer = pair definitionally.
--
-- This is a structural identity; the proof is refl.
------------------------------------------------------------------------

outer-is-pair :
  ∀ {n m} (p : Polynomial n) (q : Polynomial m) →
  outer p q ≡ pair p q
outer-is-pair []      q = refl
outer-is-pair (a ∷ p) q = cong ((a *ₛ q) ∷_) (outer-is-pair p q)

------------------------------------------------------------------------
-- N-2: Polynomial multiplication via TensorProduct's pair.
--
-- Substitute `pair` for `outer` in the polynomial-multiplication
-- factorization. The result is the same multiplication, expressed
-- through the categorical primitive.
------------------------------------------------------------------------

_*P-via-tensor_ :
  ∀ {n m} → Polynomial n → Polynomial m → Polynomial (n ℕ+ m)
_*P-via-tensor_ p q = anti-diag-sum (pair p q)

-- The two formulations agree pointwise.
*P-via-tensor-eq :
  ∀ {n m} (p : Polynomial n) (q : Polynomial m) →
  (p *P q) ≡ (p *P-via-tensor q)
*P-via-tensor-eq p q = cong anti-diag-sum (outer-is-pair p q)

------------------------------------------------------------------------
-- N-3: Capstone — polynomial multiplication categorically named.
--
-- After this slice, polynomial multiplication's structural identity
-- with the ⊗-Hom adjunction's composition is explicit:
--
--   _*P_ p q  =  anti-diag-sum (outer p q)        [Polynomial def]
--            ≡  anti-diag-sum (pair p q)          [outer ≡ pair]
--            =  _*P-via-tensor_ p q               [TensorProduct view]
--
-- Per [[feedback-categorical-name-first]]: `outer` and `pair` name
-- the same operation; this slice surfaces the equivalence. Downstream
-- code that produces an `outer p q` IS producing a TensorProduct
-- element; reciprocally, TensorProduct's universal property applies
-- directly to polynomial multiplication.
--
-- Substrate-wide implication: any future operation defined via
-- `outer` (universal bilinear) immediately benefits from
-- TensorProduct's universal property (= bilinear ↔ linear bijection).
-- The polynomial-multiplication case IS the canonical example.
--
-- Deferred follow-ons:
--
--   * **anti-diag-sum as a Linear-record**: package anti-diag-sum
--     as `Linear (TensorProduct n m) (Polynomial (n + m))` — i.e.,
--     prove its bilinearity / linearity in the tensor product
--     structure. Currently a plain function.
--
--   * **Other bilinear operations via pair**: any bilinear op on
--     V × W → U can be factored via `pair + specific-linear-out`.
--     Future operations (inner product when n = m, antisymmetric
--     pairings, etc.) follow this template.
--
--   * **Polynomial multiplication as a Hom in F₂[x]'s algebra
--     structure**: F₂[x] is an algebra; *P is its multiplication;
--     the algebra structure is captured by a Hom from F₂[x] ⊗ F₂[x]
--     to F₂[x]. anti-diag-sum IS this Hom (modulo the size
--     adjustment for polynomial truncation).
------------------------------------------------------------------------
