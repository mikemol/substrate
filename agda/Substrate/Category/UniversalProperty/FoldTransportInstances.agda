{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FoldTransportInstances — ⟡fold-transport-
-- instances: CONCRETE NON-IDENTITY transports through trace-fold-transport (172). ADD
-- 172 built the engine and fired it at φ = id (shape-id-transport); here are the real
-- transports with genuine non-identity algebra morphisms φ:
--   • shape → count  (φ = length)  : the LENGTH of the shape/CF ≡ the step count.
--   • shape → sum    (φ = sum)     : the SUM of the shape digits ≡ the quotient sum.
-- Each is length/sum ∘ shape-fold ≡ (the count/sum fold), for FREE, by the initial-
-- algebra universal property — no per-trace induction, the engine does it.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.FoldTransportInstances where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Algebra.Wedge using (DivStr; z; quot; rem; Trace; done; more; trace-fold; ℕ-div)
open import Substrate.Category.UniversalProperty.FoldTransport using (trace-fold-transport)

------------------------------------------------------------------------
-- length / sum on List (the two non-identity algebra morphisms out of List).
------------------------------------------------------------------------
length : {A : Set} → List A → ℕ
length []       = 0
length (_ ∷ xs) = suc (length xs)

sum : List ℕ → ℕ
sum []       = 0
sum (x ∷ xs) = x + sum xs

------------------------------------------------------------------------
-- ① shape → count (φ = length). shape-fold = trace-fold (λ _→[]) (λ _ w rec→quot w∷rec);
-- count-fold = trace-fold (λ _→0) (λ _ _ rec→suc rec). φ = length carries the shape
-- algebra to the count algebra: length [] = 0, length (quot w ∷ rec) = suc (length rec).
-- trace-fold-transport ⟹ length ∘ shape-fold ≡ count-fold on every trace.
------------------------------------------------------------------------
shape→count : {C : Set} {D : DivStr C} {a b g : C} (t : Trace D a b g) →
  length (trace-fold {D = D} {T = λ _ _ _ → List C} (λ _ → []) (λ _ w rec → quot w ∷ rec) t)
  ≡ trace-fold {D = D} {T = λ _ _ _ → ℕ} (λ _ → 0) (λ _ _ rec → suc rec) t
shape→count {C = C} {D = D} =
  trace-fold-transport {D = D}
    (λ _ → []) (λ _ w rec → quot w ∷ rec)          -- the shape algebra (T₁ = List)
    (λ _ → 0)  (λ _ _ rec → suc rec)                -- the count algebra (T₂ = ℕ)
    length (λ _ → refl) (λ _ _ _ → refl)            -- φ = length, base + step commute (refl)

------------------------------------------------------------------------
-- ② shape → sum (φ = sum), over ℕ-div (where C = ℕ so the digits add). sum-fold =
-- trace-fold (λ _→0) (λ _ w rec→quot w + rec). φ = sum: sum [] = 0, sum (quot w ∷ rec)
-- = quot w + sum rec. trace-fold-transport ⟹ sum ∘ shape-fold ≡ sum-fold.
------------------------------------------------------------------------
shape→sum : {a b g : ℕ} (t : Trace ℕ-div a b g) →
  sum (trace-fold {D = ℕ-div} {T = λ _ _ _ → List ℕ} (λ _ → []) (λ _ w rec → quot w ∷ rec) t)
  ≡ trace-fold {D = ℕ-div} {T = λ _ _ _ → ℕ} (λ _ → 0) (λ _ w rec → quot w + rec) t
shape→sum =
  trace-fold-transport {D = ℕ-div}
    (λ _ → []) (λ _ w rec → quot w ∷ rec)          -- the shape algebra
    (λ _ → 0)  (λ _ w rec → quot w + rec)           -- the sum algebra
    sum (λ _ → refl) (λ _ _ _ → refl)               -- φ = sum, base + step commute (refl)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — non-identity transport, the engine earns its keep):
-- ADD 172's trace-fold-transport fired at φ = id (a sanity check); HERE it fires at
-- genuine NON-IDENTITY algebra morphisms — length (List → ℕ) and sum (List ℕ → ℕ) —
-- and delivers length ∘ shape ≡ count and sum ∘ shape ≡ sum-fold FOR FREE, by the
-- initial-algebra universal property (trace-fold-unique inside the engine), NO per-trace
-- induction. This is the PAYOFF the operator named for registering the folds: pick ANY
-- fold as canonical (shape), and every derived read (count = length∘shape, digit-sum =
-- sum∘shape) transports to its own direct fold automatically. The "compute via shape
-- then post-process vs a direct fold" either/or dissolves: they are ≡ by the engine —
-- the algebra morphism φ IS the post-processing, and it commutes past the fold for free.
------------------------------------------------------------------------
