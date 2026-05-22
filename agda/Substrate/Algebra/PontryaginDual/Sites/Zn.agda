------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Sites.Zn
--
-- Concrete site: Z/n's Pontryagin dual is Z/n (cyclic groups are
-- self-dual).
--
-- For Z/n, characters are χ_k(j) = ζ^(jk) where ζ = exp(2πi/n) is
-- a primitive n-th root of unity. The map k ↦ χ_k gives an
-- isomorphism Z/n → (Z/n)^.
--
-- Per [[roll-our-own-via-word-algebra]]: the cyclic group's
-- characters can be represented as Coxeter words on the cyclic
-- generator.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Sites.Zn where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; suc) renaming (zero to ℕzero)

open import Substrate.Algebra.PontryaginDual

------------------------------------------------------------------------
-- Z/(suc n) as the carrier of its own Pontryagin dual.
--
-- We use `suc n` to guarantee non-empty Z/(suc n) (always has at
-- least one element, the identity). Characters χ_k : Fin (suc n) →
-- (Fin (suc n)) are indexed by Fin (suc n).

ℤ/n-as-Self-Dual : (n : ℕ) → PontryaginDual (Fin (suc n)) (Fin (suc n))
ℤ/n-as-Self-Dual n = record
  { Chars     = Fin (suc n)
  ; dual-mult = λ a b → a                  -- stub: a + b mod (suc n)
  ; dual-id   = zero {n}                   -- identity character χ_0
  ; dual-inv  = λ a → a                    -- stub: (suc n) - a
  }

------------------------------------------------------------------------
-- Per [[roll-our-own-via-word-algebra]]: Z/n characters as Coxeter
-- words on the cyclic generator g; each χ_k = g^k.
-- Per [[expose-generator-not-orbit]]: cyclic generator g is exposed;
-- the orbit is the dual group itself.
