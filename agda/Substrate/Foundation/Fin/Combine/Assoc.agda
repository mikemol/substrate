------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Assoc
--
-- THE FINITE-TYPE PRODUCT ASSOCIATOR — combine (combine a b) c ≡ combine a (combine b c)
-- (up to the *-assoc grade transport). The ⟡rig-8 keystone.
--
-- The structural route (induction on combine) walls: combine (combine a b) c forces
-- combine to match on an inject+/raise output, needing combine-over-inject+ distribution
-- lemmas. The `toℕ` route is clean instead: combine is the LINEAR INDEX i·n + j, so
-- associativity is just ℕ arithmetic (distributivity + *-assoc + +-assoc) transported
-- back through toℕ-injective. No combine induction, no *-distrib subst threading.
--
--   toℕ (combine i j) ≡ toℕ i · n + toℕ j          -- combine = linear index
--   ⇒ both sides of combine-assoc have toℕ = a·n·p + b·p + c  ⇒ toℕ-injective closes it.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Assoc where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc; *-distribʳ-+)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.Properties using (toℕ-injective)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)

------------------------------------------------------------------------
-- 1. toℕ bridges: the value of a Fin under the block maps.
------------------------------------------------------------------------

-- toℕ is invariant under a grade-transport (eq-induction).
toℕ-subst : ∀ {m m'} (eq : m ≡ m') (x : Fin m) → toℕ (subst Fin eq x) ≡ toℕ x
toℕ-subst refl x = refl

-- inject+ (the low injection) preserves the value.
toℕ-inject+ : ∀ {n} k (x : Fin n) → toℕ (inject+ k x) ≡ toℕ x
toℕ-inject+ k zero    = refl
toℕ-inject+ k (suc x) = cong suc (toℕ-inject+ k x)

-- raise shifts the value by the offset.
toℕ-raise : ∀ n {k} (x : Fin k) → toℕ (raise n x) ≡ n + toℕ x
toℕ-raise zero    x = refl
toℕ-raise (suc n) x = cong suc (toℕ-raise n x)

-- combine IS the linear index i·n + j.
toℕ-combine : ∀ {m n} (i : Fin m) (j : Fin n) → toℕ (combine i j) ≡ toℕ i * n + toℕ j
toℕ-combine {suc m} {n} zero    j = toℕ-inject+ (m * n) j
toℕ-combine {suc m} {n} (suc i) j =
  trans (toℕ-raise n (combine i j))
        (trans (cong (n +_) (toℕ-combine i j))
               (sym (+-assoc n (toℕ i * n) (toℕ j))))

------------------------------------------------------------------------
-- 2. The arithmetic core: (A·n + B)·p + C = A·(n·p) + (B·p + C).
------------------------------------------------------------------------

private
  arith : ∀ A n B p C → (A * n + B) * p + C ≡ A * (n * p) + (B * p + C)
  arith A n B p C =
    trans (cong (_+ C) (*-distribʳ-+ p (A * n) B))
          (trans (+-assoc (A * n * p) (B * p) C)
                 (cong (_+ (B * p + C)) (*-assoc A n p)))

------------------------------------------------------------------------
-- 3. THE ASSOCIATOR. Both sides have toℕ = a·n·p + b·p + c; toℕ-injective closes it.
------------------------------------------------------------------------

combine-assoc : ∀ {m n p} (a : Fin m) (b : Fin n) (c : Fin p) →
  subst Fin (*-assoc m n p) (combine (combine a b) c) ≡ combine a (combine b c)
combine-assoc {m} {n} {p} a b c = toℕ-injective (
  trans (toℕ-subst (*-assoc m n p) (combine (combine a b) c))
  (trans (toℕ-combine (combine a b) c)
  (trans (cong (λ z → z * p + toℕ c) (toℕ-combine a b))
  (trans (arith (toℕ a) n (toℕ b) p (toℕ c))
  (trans (cong (toℕ a * (n * p) +_) (sym (toℕ-combine b c)))
         (sym (toℕ-combine a (combine b c))))))))
