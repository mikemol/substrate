------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetBasis
--
-- CHALLENGE: "permit ℚ to have differently-basised numerator vs denominator."
--
-- ANSWER: it is already the case, and it generalizes. ℚ = mkℚ (num : ℤ)
-- (den-1 : ℕ) ALREADY carries its numerator in one carrier (signed ℤ) and its
-- denominator in another (unsigned ℕ). And `_≈ℚ_` (Q.Equiv) is
--      p ≈ℚ q  =  num p *ℤ (+ suc (den-1 q))  ≡  num q *ℤ (+ suc (den-1 p))
-- where `+ suc (den-1 ·)` is the EMBEDDING ℕ ↪ ℤ of the denominator into ℤ.
-- So ℚ-equality is a CROSS-MULTIPLICATION across two bases, meeting in a common
-- carrier R = ℤ: exactly the CrossMul cospan  ℤ →id ℤ ←(+_) ℕ
-- (Wedge.CrossMul: `cross cm a b = mul R (embA a) (embB b)`, here
--  a *ℤ (embed d)). The numerator basis and denominator basis are DIFFERENT;
-- the equality is their bilinear cross term in R.
--
-- This module makes that literal:
--   1. HetQ A B — the generic heterogeneous quotient (num ∈ A, den ∈ B).
--   2. CrossEq — its equality via a cross-multiply ⊗ : A → B → R (= CrossMul's
--      `cross`), into a common R; refl/sym generic (trans = the carrier's
--      cross-cancellation, the "one nontrivial law", supplied per instance).
--   3. ℚ IS HetQ ℤ ℕ, and `_≈ℚ_` IS its cross-equality — both by `refl`
--      (definitional): the existing ℚ is the instance A=ℤ, B=ℕ, R=ℤ.
--   4. A GENUINELY different-radix instance: numerator a base-2 digit list,
--      denominator a base-3 digit list, equality by cross-multiplication of
--      their radix-valued values in R = ℕ. (101₂ / 12₃) ≈ (1₂ / 1₃) — "5/5 = 1/1".
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetBasis where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)

------------------------------------------------------------------------
-- 1. The heterogeneous quotient: numerator in basis A, denominator in basis B.
--    The two parts need NOT share a carrier.
------------------------------------------------------------------------

record HetQ (A B : Set) : Set where
  constructor _//_
  field
    hnum : A
    hden : B

open HetQ public

------------------------------------------------------------------------
-- 2. Equality by cross-multiplication into a common carrier R.
--    `_⊗_ : A → B → R` is CrossMul's `cross` (the cospan A → R ← B); the
--    equality p ≈H q tests the two cross terms num·den' and num'·den in R.
------------------------------------------------------------------------

module CrossEq {A B R : Set}
  (_⊗_  : A → B → R)
  (_≈R_ : R → R → Set)
  (≈R-refl : ∀ {x}   → x ≈R x)
  (≈R-sym  : ∀ {x y} → x ≈R y → y ≈R x)
  where

  _≈H_ : HetQ A B → HetQ A B → Set
  p ≈H q = (hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p)

  ≈H-refl : (p : HetQ A B) → p ≈H p
  ≈H-refl p = ≈R-refl

  ≈H-sym : {p q : HetQ A B} → p ≈H q → q ≈H p
  ≈H-sym e = ≈R-sym e

------------------------------------------------------------------------
-- 3. ℚ IS HetQ ℤ ℕ — the existing ℚ is already heterogeneous-basised.
------------------------------------------------------------------------

toHetQ : ℚ → HetQ ℤ ℕ
toHetQ q = num q // den-1 q

fromHetQ : HetQ ℤ ℕ → ℚ
fromHetQ h = mkℚ (hnum h) (hden h)

-- A definitional bijection (the carriers ARE (ℤ, ℕ), just unbundled).
htq-left-inverse : (q : ℚ) → fromHetQ (toHetQ q) ≡ q
htq-left-inverse q = refl

htq-right-inverse : (h : HetQ ℤ ℕ) → toHetQ (fromHetQ h) ≡ h
htq-right-inverse h = refl

-- ℚ's cross-multiply: numerator (ℤ) times denominator embedded ℕ ↪ ℤ. This is
-- CrossMul.cross for the cospan ℤ →id ℤ ←(+_) ℕ.
_⊗ℚ_ : ℤ → ℕ → ℤ
a ⊗ℚ d = a *ℤ (+ suc d)

open CrossEq _⊗ℚ_ _≡_ refl sym renaming (_≈H_ to _≈Hℚ_)

-- THE point: `_≈ℚ_` (cross-multiplication) IS the heterogeneous cross-equality.
-- Definitional — both unfold to num p *ℤ (+ suc (den-1 q)) ≡ num q *ℤ (+ suc (den-1 p)).
≈ℚ-is-cross : (p q : ℚ) → (p ≈ℚ q) ≡ (toHetQ p ≈Hℚ toHetQ q)
≈ℚ-is-cross p q = refl

------------------------------------------------------------------------
-- 4. A GENUINELY different-radix instance: numerator in base 2, denominator
--    in base 3 (digit lists, least-significant first). The bases differ in
--    BOTH carrier-shape AND radix; the quotient is still well-defined, with
--    equality the cross-multiplication of radix-valued values in the common R = ℕ.
------------------------------------------------------------------------

radix-value : ℕ → List ℕ → ℕ              -- base → digits (LSB first) → value
radix-value b []       = 0
radix-value b (d ∷ ds) = d + b * radix-value b ds

_⊗r_ : List ℕ → List ℕ → ℕ           -- num radix-valued base 2, den radix-valued base 3
a ⊗r d = radix-value 2 a * radix-value 3 d

open CrossEq _⊗r_ _≡_ refl sym renaming (_≈H_ to _≈Hr_)

-- 101₂ = 5 (LSB-first [1,0,1]),  12₃ = 5 (LSB-first [2,1]).
five-over-five : HetQ (List ℕ) (List ℕ)
five-over-five = (1 ∷ 0 ∷ 1 ∷ []) // (2 ∷ 1 ∷ [])

-- 1₂ = 1,  1₃ = 1.
one-over-one : HetQ (List ℕ) (List ℕ)
one-over-one = (1 ∷ []) // (1 ∷ [])

-- "5/5 = 1/1": equal across binary-vs-ternary representations, by cross-mult
-- in ℕ (5·1 ≡ 1·5). The numerator and denominator live in genuinely different
-- radix bases, yet the rational they denote is compared with no trouble.
eq-demo : five-over-five ≈Hr one-over-one
eq-demo = refl

-- And a NON-equal pair, to show the equality is discriminating: 10₂ = 2 (LSB
-- [0,1]) over 1₃ = 1 is "2/1"; not equal to 1/1 (2·1 ≢ 1·1 would not be refl).
two-over-one : HetQ (List ℕ) (List ℕ)
two-over-one = (0 ∷ 1 ∷ []) // (1 ∷ [])

-- 2/1 ≈ 2/1 trivially (refl) — witnessing the instance's reflexivity on a
-- distinct value.
two-refl : two-over-one ≈Hr two-over-one
two-refl = refl
