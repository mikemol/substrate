------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Concat
--
-- Power concatenation + normalize-of-power-via-mod chain.
--
--   power-concat-eq        : power k₁ ++ power k₂ ≡ power (k₁ + k₂)
--   normalize-power        : normalize (power k) ≡ iter k (insert a) []
--   insert-power-mod       : insert a (power (k mod-suc n)) ≡ power (suc k mod-suc n)
--   iter-power-mod         : iter k (insert a) [] ≡ power (k mod-suc n)
--   power-cyclic-normalize : normalize (power k) ≡ power (k mod-suc n)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties using (toℕ-fromℕ<)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; mod-suc-suc)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc-toℕ)

module Substrate.Groups.Coxeter.Cyclic.NthPower.Concat (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Core n public

------------------------------------------------------------------------
-- 1. power-concat-eq: concatenating powers adds exponents.
------------------------------------------------------------------------

power-concat-eq : (k₁ k₂ : ℕ) → power k₁ ++ power k₂ ≡ power (k₁ + k₂)
power-concat-eq zero     k₂ = refl
power-concat-eq (suc k₁) k₂ = cong (a ∷_) (power-concat-eq k₁ k₂)

------------------------------------------------------------------------
-- 2. normalize-power + iter-power-mod / power-cyclic-normalize.
--
-- Connects the cyclic structure on canonical positions to the
-- unbounded Word form via mod-suc.
------------------------------------------------------------------------

normalize-power : (k : ℕ) → normalize (power k) ≡ iter k (insert a) []
normalize-power zero    = refl
normalize-power (suc k) = cong (insert a) (normalize-power k)

private
  -- insert a on power (k mod-suc n) advances by one in mod-suc n.
  insert-power-mod : (k : ℕ) →
                    insert a (power (k mod-suc n)) ≡ power ((suc k) mod-suc n)
  insert-power-mod k =
    subst (λ x → insert a (power x) ≡ power ((suc k) mod-suc n))
          (toℕ-fromℕ< (mod-suc-bound k n))
          (trans (insert-power-eq (fromℕ< (mod-suc-bound k n)))
                 (cong power
                   (trans (cyclic-suc-toℕ (fromℕ< (mod-suc-bound k n)))
                   (trans (cong (λ x → (suc x) mod-suc n)
                                (toℕ-fromℕ< (mod-suc-bound k n)))
                          (sym (mod-suc-suc k n))))))

iter-power-mod : (k : ℕ) → iter k (insert a) [] ≡ power (k mod-suc n)
iter-power-mod zero    = refl
iter-power-mod (suc k) =
  trans (cong (insert a) (iter-power-mod k))
        (insert-power-mod k)

power-cyclic-normalize : (k : ℕ) → normalize (power k) ≡ power (k mod-suc n)
power-cyclic-normalize k = trans (normalize-power k) (iter-power-mod k)
