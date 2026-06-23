------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Cyclotomic
--
-- Ⓕ.cyclotomic — the prerequisite primitive for the JEA-Pi cotype's Φ_p
-- multiplicity findings (warrant f072 / the f090_2 family). The cotype's
-- load-bearing identity is the cyclotomic factorization x^L − 1 = ∏_{m|L} Φ_m,
-- EVALUATED at the orbit operator T (a ring element, with T^L = 𝟙 on an orbit
-- of length L). Stated SUBTRACTION-FREE so it lives over a commutative
-- SEMIRING (no negation): the substrate's sub-free coordinate (cf. the
-- Matrix-Tree sub-free Kirchhoff solve, Φ1′).
--
-- THEOREM `geom-factor`:   𝟙 + x · (Σ_{i<n} xⁱ)  ≡  (Σ_{i<n} xⁱ) + xⁿ
--   This is the subtraction-free form of  (x − 𝟙) · Σ_{i<n} xⁱ = xⁿ − 𝟙
--   (the geometric-sum / cyclotomic factorization). Specialise at the orbit
--   operator with xⁿ = 𝟙 to get  x · Φ ≡ Φ  i.e. (x − 𝟙)·Φ_p(x) = 0 — the
--   kernel relation the f090_2 Φ_p-multiplicity counts.
--
-- `Φ x p = Σ_{i<p} xⁱ` is EXACTLY the cyclotomic polynomial Φ_p when p is prime
-- (for prime p the only proper divisor is 1, Φ₁ = x − 𝟙, and x^p − 𝟙 = Φ₁·Φ_p);
-- `geom-factor` at p is its factor identity.
--
-- GAP (named, NOT built here — borrowed-name discipline): the general
-- x^L − 1 = ∏_{m|L} Φ_m for COMPOSITE L (the full f072 face-action generality)
-- needs the divisor recursion / polynomial division — deferred to Ⓕ.face.
-- This module proves the prime + geometric-sum core, which is what Ⓕ.mult needs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Cyclotomic where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans; sym)
open import Substrate.Foundation.Nat.Properties.Add
  using (+-assoc; +-identityˡ; +-identityʳ)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-distribˡ-+; *-zeroʳ)

------------------------------------------------------------------------
-- Over any commutative semiring (flat bundle, friction-free — the
-- Polynomial.Graded `Over` pattern, with only the laws this proof uses).
------------------------------------------------------------------------

module Over {A : Set}
  (_⊕_ : A → A → A) (_⊗_ : A → A → A) (𝟘 𝟙 : A)
  (⊕-assoc     : (a b c : A) → (a ⊕ b) ⊕ c ≡ a ⊕ (b ⊕ c))
  (⊕-identityˡ : (a : A) → 𝟘 ⊕ a ≡ a)
  (⊕-identityʳ : (a : A) → a ⊕ 𝟘 ≡ a)
  (⊗-distribˡ  : (a b c : A) → a ⊗ (b ⊕ c) ≡ (a ⊗ b) ⊕ (a ⊗ c))
  (⊗-zeroʳ     : (a : A) → a ⊗ 𝟘 ≡ 𝟘)
  where

  infixr 8 _^_
  _^_ : A → ℕ → A
  x ^ zero  = 𝟙
  x ^ suc n = x ⊗ (x ^ n)

  -- Σ_{i<n} xⁱ  (the cyclotomic numerator; the prime Φ_p at n = p)
  geomSum : A → ℕ → A
  geomSum x zero    = 𝟘
  geomSum x (suc n) = geomSum x n ⊕ (x ^ n)

  -- THE factorization, subtraction-free: 𝟙 ⊕ x·Σ = Σ ⊕ xⁿ  ⟺ (x−𝟙)·Σ = xⁿ−𝟙.
  geom-factor : (x : A) (n : ℕ) → 𝟙 ⊕ (x ⊗ geomSum x n) ≡ geomSum x n ⊕ (x ^ n)
  geom-factor x zero =
    trans (trans (cong (𝟙 ⊕_) (⊗-zeroʳ x)) (⊕-identityʳ 𝟙))
          (sym (⊕-identityˡ 𝟙))
  geom-factor x (suc n) =
    trans (cong (𝟙 ⊕_) (⊗-distribˡ x (geomSum x n) (x ^ n)))
    (trans (sym (⊕-assoc 𝟙 (x ⊗ geomSum x n) (x ⊗ (x ^ n))))
           (cong (_⊕ (x ⊗ (x ^ n))) (geom-factor x n)))

  -- The cyclotomic Φ_p (exact at prime p) and its factor identity.
  Φ : A → ℕ → A
  Φ x p = geomSum x p

  Φ-factor : (x : A) (p : ℕ) → 𝟙 ⊕ (x ⊗ Φ x p) ≡ Φ x p ⊕ (x ^ p)
  Φ-factor x p = geom-factor x p

------------------------------------------------------------------------
-- Concrete witness: the commutative semiring ℕ (Σ_{i<n} xⁱ ∈ ℕ).
------------------------------------------------------------------------

module ℕ-cyclotomic = Over _+_ _*_ 0 1 +-assoc +-identityˡ +-identityʳ *-distribˡ-+ *-zeroʳ

-- e.g. Σ_{i<2} xⁱ = 1 + x; the factor identity holds: 1 + x·(1+x) = (1+x) + x².
_ : (x : ℕ) → 1 + (x * ℕ-cyclotomic.geomSum x 2) ≡ ℕ-cyclotomic.geomSum x 2 + (ℕ-cyclotomic._^_ x 2)
_ = λ x → ℕ-cyclotomic.geom-factor x 2
