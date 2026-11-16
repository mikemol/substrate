------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.Factorize
--
-- Defines: factorize
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.Factorize where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.List
open import Substrate.Foundation.WellFounded
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Nat.Properties.Order
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Algebra.Nat.Divides.Refl
open import Substrate.Algebra.Nat.Divides.Trans
open import Substrate.Algebra.Nat.DivMod.Unique.Private
open import Substrate.Algebra.Nat.WellFounded.LtWellFounded
open import Substrate.Algebra.Nat.WellFounded.Private
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Algebra.Nat.Prime.Properties.QLtqTimesp
open import Substrate.Algebra.Nat.Prime.Properties.PrimeDivisor



-- THE EXISTENCE THEOREM: every positive ℕ is a product of primes.
factorize : (n : ℕ) → Acc _<_ n → 1 ≤ n → Factored n
factorize zero            _         ()
factorize (suc zero)      _         _ = [] , []ᴾ , refl
factorize (suc (suc n'')) (acc rec) _
  with prime-divisor (suc (suc n'')) (<-wellFounded _) (s≤s (s≤s z≤n))
... | (p , p-prime , divides zero ())
... | (p , p-prime , divides (suc q') n≡q*p) =
      let q<n = subst (λ x → suc q' < x) (sym n≡q*p)
                  (q<q*p q' p (proj₁ p-prime))
          ih  = factorize (suc q') (rec (suc q') q<n) (s≤s z≤n)
      in p ∷ proj₁ ih
       , p-prime ∷ᴾ proj₁ (proj₂ ih)
       , trans (cong (p *_) (proj₂ (proj₂ ih)))
               (trans (*-comm p (suc q')) (sym n≡q*p))
