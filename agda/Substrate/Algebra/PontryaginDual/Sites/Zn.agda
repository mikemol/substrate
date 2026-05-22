------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Sites.Zn
--
-- Concrete site: Z/(suc n)'s Pontryagin dual is Z/(suc n) (cyclic
-- groups are self-dual).
--
-- For Z/(suc n), characters are χ_k(j) = ζ^(jk) where ζ is a
-- primitive (suc n)-th root of unity. The map k ↦ χ_k gives an
-- isomorphism Z/(suc n) → (Z/(suc n))^.
--
-- Per [[roll-our-own-via-word-algebra]]: the cyclic group's
-- characters can be represented as Coxeter words on the cyclic
-- generator g. Per [[expose-generator-not-orbit]]: cyclic generator
-- g is exposed; the orbit is the dual group itself.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Sites.Zn where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.PontryaginDual

------------------------------------------------------------------------
-- Z/(suc n) as the carrier of its own Pontryagin dual.
--
-- We use `suc n` to guarantee Z/(suc n) is non-empty (always has at
-- least the identity character χ_0). Characters χ_k : Z/(suc n) →
-- U(1) are indexed by Fin (suc n) — the substrate identifies a
-- character with its frequency index.
--
-- For now the dual group operations are placeholders for the
-- cyclic-addition-modulo-(suc n) operations (the substrate's
-- modular-reduction primitive _mod-suc_ is in Substrate.Algebra.Nat.Mod).
-- A follow-on slice can swap these for the actual modular ops.

ℤ/n-as-Self-Dual : (n : ℕ) → PontryaginDual (Fin (suc n)) (Fin (suc n))
ℤ/n-as-Self-Dual n = record
  { Chars     = Fin (suc n)
  ; dual-mult = λ a _ → a               -- TODO: cyclic addition mod (suc n)
  ; dual-id   = zero {n}                -- identity character χ_0
  ; dual-inv  = λ a → a                 -- TODO: (suc n) ∸ a
  }
