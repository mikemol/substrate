------------------------------------------------------------------------
-- Substrate.WitnessTower.Counting
--
-- The falling factorial P(n,k) = n·(n−1)···(n−k+1), completing the
-- witness-tower counting trio:
--   * factorial n   (Enumerate)  = |perms n|      — the FULL permutations,
--   * falling  n k  (here)       = ordered no-repeat k-selections from n,
--   * words    n k  (Enumerate)  = |words n k| ≡ nᵏ — the length-k sequences.
--
-- Same running-product fold as factorial, but the rung multiplier is the
-- shrinking free count (n ∸ i), not the full alphabet size. The wedge-eq
--   n! ≡ P(n,k) · (n−k)!    (exact, remainder 0)
-- proves P(n,k) is the exact integer quotient n!/(n−k)!.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Counting where

open import Substrate.Foundation.Nat  using (ℕ; zero; suc; _*_; _∸_; _≤_; s≤s)
open import Substrate.Foundation.Eq   using (_≡_; refl; cong; trans; sym)
open import Substrate.Foundation.Nat.Properties.Mul   using (*-comm; *-assoc; *-identityˡ)
open import Substrate.Foundation.Nat.Properties.Sub   using (∸-suc-l)
open import Substrate.Foundation.Nat.Properties.Order using (≤-suc-r)
open import Substrate.WitnessTower.Enumerate using (factorial)

-- P(n,k): k rungs, each rung places one of the (n ∸ i) symbols not yet used.
falling : ℕ → ℕ → ℕ
falling n zero    = suc zero
falling n (suc k) = (n ∸ k) * falling n k

-- THE WEDGE-EQ (exact division, remainder 0):  n! ≡ P(n,k) · (n−k)!.
-- Proved by induction on k; the one ℕ fact used is ∸-suc-l
-- (k ≤ m ⇒ suc m ∸ k ≡ suc (m ∸ k)), which unfolds one factorial rung.
falling-factorial : (n k : ℕ) → k ≤ n → factorial n ≡ falling n k * factorial (n ∸ k)
falling-factorial n zero _ = sym (*-identityˡ (factorial n))
falling-factorial (suc m) (suc k) (s≤s k≤m) =
  trans (falling-factorial (suc m) k (≤-suc-r k≤m))
  (trans (cong (λ z → falling (suc m) k * factorial z) (∸-suc-l m k k≤m))
  (trans (sym (*-assoc (falling (suc m) k) (suc (m ∸ k)) (factorial (m ∸ k))))
  (trans (cong (_* factorial (m ∸ k)) (*-comm (falling (suc m) k) (suc (m ∸ k))))
         (cong (λ z → (z * falling (suc m) k) * factorial (m ∸ k)) (sym (∸-suc-l m k k≤m))))))

-- Smoke: P(5,2) = 5·4 = 20 (kept small so the check does not whnf a big value).
falling-5-2 : falling 5 2 ≡ 20
falling-5-2 = refl
