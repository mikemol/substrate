------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.Add
--
-- The ℤ additive-group laws — the `+` half of the operand ring EEA's
-- Bézout fold targets. Proven via the ⊖-merge lemma
-- ((p ⊖ q) +ℤ (r ⊖ s) ≡ (p+r) ⊖ (q+s)), which collapses commutativity /
-- associativity to ℕ arithmetic (since + m = m ⊖ 0 and -suc m = 0 ⊖ suc m
-- definitionally, every ℤ is some p ⊖ q).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.Add where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add
  using (+-comm; +-assoc; +-suc; +-identityʳ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_; 0ℤ)
open import Substrate.Algebra.Z.Arithmetic using (_⊖_; _+ℤ_; _-ℤ_)

------------------------------------------------------------------------
-- 1. ⊖ interacting with adding a positive / a negative (comm-free).
------------------------------------------------------------------------

⊖-+pos : (m n k : ℕ) → (m ⊖ n) +ℤ (+ k) ≡ (m + k) ⊖ n
⊖-+pos m       zero    k = refl
⊖-+pos zero    (suc n) k = refl
⊖-+pos (suc m) (suc n) k = ⊖-+pos m n k

⊖-+neg : (m n k : ℕ) → (m ⊖ n) +ℤ (-suc k) ≡ m ⊖ (n + suc k)
⊖-+neg m       zero    k = refl
⊖-+neg zero    (suc n) k = cong -suc_ (sym (+-suc n k))
⊖-+neg (suc m) (suc n) k = ⊖-+neg m n k

------------------------------------------------------------------------
-- 2. The ⊖-merge: addition of two differences is the difference of sums.
------------------------------------------------------------------------

⊖-merge : (p q r s : ℕ) → (p ⊖ q) +ℤ (r ⊖ s) ≡ (p + r) ⊖ (q + s)
⊖-merge p q r zero =
  trans (⊖-+pos p q r) (cong ((p + r) ⊖_) (sym (+-identityʳ q)))
⊖-merge p q zero (suc s) =
  trans (⊖-+neg p q s) (cong (_⊖ (q + suc s)) (sym (+-identityʳ p)))
⊖-merge p q (suc r) (suc s) =
  trans (⊖-merge p q r s) (sym (cong₂ _⊖_ (+-suc p r) (+-suc q s)))

------------------------------------------------------------------------
-- 3. Commutativity and associativity (via ⊖-merge).
------------------------------------------------------------------------

comm-⊖ : (p q r s : ℕ) → (p ⊖ q) +ℤ (r ⊖ s) ≡ (r ⊖ s) +ℤ (p ⊖ q)
comm-⊖ p q r s =
  trans (⊖-merge p q r s)
        (trans (cong₂ _⊖_ (+-comm p r) (+-comm q s)) (sym (⊖-merge r s p q)))

+ℤ-comm : (x y : ℤ) → x +ℤ y ≡ y +ℤ x
+ℤ-comm (+ a)    (+ b)    = comm-⊖ a 0 b 0
+ℤ-comm (+ a)    (-suc b) = comm-⊖ a 0 0 (suc b)
+ℤ-comm (-suc a) (+ b)    = comm-⊖ 0 (suc a) b 0
+ℤ-comm (-suc a) (-suc b) = comm-⊖ 0 (suc a) 0 (suc b)

assoc-⊖ : (p q r s u v : ℕ) →
          ((p ⊖ q) +ℤ (r ⊖ s)) +ℤ (u ⊖ v) ≡ (p ⊖ q) +ℤ ((r ⊖ s) +ℤ (u ⊖ v))
assoc-⊖ p q r s u v =
  trans (trans (cong (_+ℤ (u ⊖ v)) (⊖-merge p q r s)) (⊖-merge (p + r) (q + s) u v))
        (trans (cong₂ _⊖_ (+-assoc p r u) (+-assoc q s v))
               (sym (trans (cong ((p ⊖ q) +ℤ_) (⊖-merge r s u v))
                           (⊖-merge p q (r + u) (s + v)))))

+ℤ-assoc : (x y z : ℤ) → (x +ℤ y) +ℤ z ≡ x +ℤ (y +ℤ z)
+ℤ-assoc (+ a)    (+ b)    (+ c)    = assoc-⊖ a 0 b 0 c 0
+ℤ-assoc (+ a)    (+ b)    (-suc c) = assoc-⊖ a 0 b 0 0 (suc c)
+ℤ-assoc (+ a)    (-suc b) (+ c)    = assoc-⊖ a 0 0 (suc b) c 0
+ℤ-assoc (+ a)    (-suc b) (-suc c) = assoc-⊖ a 0 0 (suc b) 0 (suc c)
+ℤ-assoc (-suc a) (+ b)    (+ c)    = assoc-⊖ 0 (suc a) b 0 c 0
+ℤ-assoc (-suc a) (+ b)    (-suc c) = assoc-⊖ 0 (suc a) b 0 0 (suc c)
+ℤ-assoc (-suc a) (-suc b) (+ c)    = assoc-⊖ 0 (suc a) 0 (suc b) c 0
+ℤ-assoc (-suc a) (-suc b) (-suc c) = assoc-⊖ 0 (suc a) 0 (suc b) 0 (suc c)

------------------------------------------------------------------------
-- 4. Identity and inverse.
------------------------------------------------------------------------

+ℤ-identityˡ : (x : ℤ) → 0ℤ +ℤ x ≡ x
+ℤ-identityˡ (+ n)    = refl
+ℤ-identityˡ (-suc n) = refl

+ℤ-identityʳ : (x : ℤ) → x +ℤ 0ℤ ≡ x
+ℤ-identityʳ (+ m)    = cong +_ (+-identityʳ m)
+ℤ-identityʳ (-suc m) = refl

⊖-self : (m : ℕ) → m ⊖ m ≡ + 0
⊖-self zero    = refl
⊖-self (suc m) = ⊖-self m

+ℤ-inverseʳ : (x : ℤ) → x +ℤ (-ℤ x) ≡ 0ℤ
+ℤ-inverseʳ (+ zero)    = refl
+ℤ-inverseʳ (+ suc m)   = ⊖-self m
+ℤ-inverseʳ (-suc m)    = ⊖-self m

+ℤ-inverseˡ : (x : ℤ) → (-ℤ x) +ℤ x ≡ 0ℤ
+ℤ-inverseˡ x = trans (+ℤ-comm (-ℤ x) x) (+ℤ-inverseʳ x)
