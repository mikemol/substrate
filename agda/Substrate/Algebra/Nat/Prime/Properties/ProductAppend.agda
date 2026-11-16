------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties.ProductAppend
--
-- Defines: product-++
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Nat.Prime.Properties; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties.ProductAppend where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.List
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Algebra.Quotient.ApproxcanonicalEq
open import Substrate.Algebra.Quotient.Canonical
open import Substrate.Algebra.Quotient.CanonicalEqApprox
open import Substrate.Algebra.Quotient.IdemCanonical
open import Substrate.Algebra.Quotient.KerQuotient
open import Substrate.Algebra.Quotient.KerRel
open import Substrate.Algebra.Quotient.Quotient
open import Substrate.Algebra.Quotient.SplitCanonical
open import Substrate.Algebra.Nat.Prime
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- 9. Ⓝ.iso2: the ⊕ STRUCTURE — the iso is a MONOID HOMOMORPHISM, not just a
--    bijection. `product` carries (List ℕ, ++, []) → (ℕ, ·, 1): concatenating
--    factor lists MULTIPLIES the values, i.e. ADDING exponents (++ = multiset
--    union) ↦ multiplying — the additive ⊕ of ℚ₊ ≅ ⊕primesℤ, at the ℕ⁺ level.
--    (This is the hom that turns · into ℕ+, the engine of L_OR = LogSumExp.)
------------------------------------------------------------------------

-- product is a monoid hom: product (xs ++ ys) ≡ product xs · product ys.
product-++ : (xs ys : List ℕ) → product (xs ++ ys) ≡ product xs * product ys
product-++ []       ys = sym (*-identityˡ (product ys))
product-++ (x ∷ xs) ys =
  trans (cong (x *_) (product-++ xs ys))
        (sym (*-assoc x (product xs) (product ys)))
