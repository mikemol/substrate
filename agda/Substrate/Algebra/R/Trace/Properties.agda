------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Properties
--
-- What earns the word "real": the convergents of a RealTrace genuinely
-- converge. The engine is the NEIGHBOUR DETERMINANT of consecutive
-- convergents, pₙqₙ₋₁ − pₙ₋₁qₙ, which is a unit — `det² ≡ +1` — UNCONDITIONALLY
-- (no hypothesis on the digits). It gives the exact spacing
-- |pₙ/qₙ − pₙ₋₁/qₙ₋₁| = 1/(qₙqₙ₋₁): consecutive convergents are Farey/Stern-Brocot
-- neighbours, so the process brackets a single real ever more tightly.
--
-- The proof is the coinductive dual of EEATrace's inductive correctness: the
-- determinant FLIPS SIGN each Wedge step (the common a·p·q term cancels), so its
-- SQUARE is a step-invariant, pinned to +1 by the seed. B2 of the substrate-ℝ
-- arc ([[project_substrate_real_arc]]); the spacing/Cauchy modulus is B2-next.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-comm; *-assoc; *-distribˡ-+; *-distribʳ-+)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_; -ℤ-involutive)
open import Substrate.Algebra.Z.Add using (_⊖_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (*ℤ-comm; neg-*-left)

open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)

------------------------------------------------------------------------
-- Two truncated-difference helpers (direct induction on the ⊖ reduction).
------------------------------------------------------------------------

-- cancel a common summand on both sides of a difference.
⊖-cancelˡ : (x m n : ℕ) → (x + m) ⊖ (x + n) ≡ m ⊖ n
⊖-cancelˡ zero    m n = refl
⊖-cancelˡ (suc x) m n = ⊖-cancelˡ x m n

-- swapping the operands negates the difference.
⊖-swap-neg : (a b : ℕ) → (b ⊖ a) ≡ -ℤ (a ⊖ b)
⊖-swap-neg zero    zero    = refl
⊖-swap-neg zero    (suc b) = refl
⊖-swap-neg (suc a) zero    = refl
⊖-swap-neg (suc a) (suc b) = ⊖-swap-neg a b

-- a square is sign-blind: (−x)² = x².
neg-sq : (x : ℤ) → (-ℤ x) *ℤ (-ℤ x) ≡ x *ℤ x
neg-sq x =
  trans (neg-*-left x (-ℤ x))
        (trans (cong -ℤ_ (trans (*ℤ-comm x (-ℤ x)) (neg-*-left x x)))
               (-ℤ-involutive (x *ℤ x)))

------------------------------------------------------------------------
-- The neighbour determinant of a convergent state (pₙ, qₙ, pₙ₋₁, qₙ₋₁).
------------------------------------------------------------------------

det4 : ℕ → ℕ → ℕ → ℕ → ℤ
det4 p₁ q₁ p₀ q₀ = (p₁ * q₀) ⊖ (p₀ * q₁)

------------------------------------------------------------------------
-- One Wedge step flips the determinant's sign. New state after digit a is
-- (a·p₁+p₀, a·q₁+q₀, p₁, q₁); the a·p₁·q₁ term is common to both products and
-- cancels, leaving the old determinant with its operands swapped = negated.
------------------------------------------------------------------------

det-flip : (a p₁ q₁ p₀ q₀ : ℕ) →
           det4 (a * p₁ + p₀) (a * q₁ + q₀) p₁ q₁ ≡ -ℤ (det4 p₁ q₁ p₀ q₀)
det-flip a p₁ q₁ p₀ q₀ =
  trans (cong₂ _⊖_ lhs rhs)
        (trans (⊖-cancelˡ ((a * p₁) * q₁) (p₀ * q₁) (p₁ * q₀))
               (⊖-swap-neg (p₁ * q₀) (p₀ * q₁)))
  where
    Yeq : p₁ * (a * q₁) ≡ (a * p₁) * q₁
    Yeq = trans (sym (*-assoc p₁ a q₁)) (cong (_* q₁) (*-comm p₁ a))

    lhs : (a * p₁ + p₀) * q₁ ≡ (a * p₁) * q₁ + p₀ * q₁
    lhs = *-distribʳ-+ q₁ (a * p₁) p₀

    rhs : p₁ * (a * q₁ + q₀) ≡ (a * p₁) * q₁ + p₁ * q₀
    rhs = trans (*-distribˡ-+ p₁ (a * q₁) q₀) (cong (_+ p₁ * q₀) Yeq)

------------------------------------------------------------------------
-- The convergent state after consuming n digits, read as its determinant.
-- (Same recurrence as Trace.convergent; here exposing both (p,q) columns.)
------------------------------------------------------------------------

det-after : ℕ → ℕ → ℕ → ℕ → ℕ → RealTrace → ℤ
det-after zero    p₁ q₁ p₀ q₀ _ = det4 p₁ q₁ p₀ q₀
det-after (suc n) p₁ q₁ p₀ q₀ r =
  det-after n (head r * p₁ + p₀) (head r * q₁ + q₀) p₁ q₁ (tail r)

------------------------------------------------------------------------
-- The square of the determinant is a STEP-INVARIANT (sign flips, square
-- doesn't), hence equal to the seed's — and the seed det4 1 0 0 1 = +1.
------------------------------------------------------------------------

det-sq : (n p₁ q₁ p₀ q₀ : ℕ) (r : RealTrace) →
         det-after n p₁ q₁ p₀ q₀ r *ℤ det-after n p₁ q₁ p₀ q₀ r
       ≡ det4 p₁ q₁ p₀ q₀ *ℤ det4 p₁ q₁ p₀ q₀
det-sq zero    p₁ q₁ p₀ q₀ r = refl
det-sq (suc n) p₁ q₁ p₀ q₀ r =
  trans (det-sq n (head r * p₁ + p₀) (head r * q₁ + q₀) p₁ q₁ (tail r))
        (trans (cong (λ z → z *ℤ z) (det-flip (head r) p₁ q₁ p₀ q₀))
               (neg-sq (det4 p₁ q₁ p₀ q₀)))

-- THE neighbour identity: |det| = 1 for every convergent of every RealTrace.
det²≡1 : (n : ℕ) (r : RealTrace) →
         det-after n 1 0 0 1 r *ℤ det-after n 1 0 0 1 r ≡ + 1
det²≡1 n r = det-sq n 1 0 0 1 r
