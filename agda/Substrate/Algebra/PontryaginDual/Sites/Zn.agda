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

open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Nat using (ℕ; suc; _+_; _∸_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Algebra.PontryaginDual
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)

------------------------------------------------------------------------
-- Z/(suc n) as the carrier of its own Pontryagin dual.
--
-- We use `suc n` to guarantee Z/(suc n) is non-empty (always has at
-- least the identity character χ_0). Characters χ_k : Z/(suc n) →
-- U(1) are indexed by Fin (suc n) — the substrate identifies a
-- character with its frequency index.
--
-- The dual group operations ARE the cyclic-addition-modulo-(suc n)
-- operations: χ_a · χ_b = χ_(a+b mod suc n), and χ_a's inverse is
-- χ_(suc n ∸ a mod suc n). They reuse the substrate-native modular
-- reduction `_mod-suc_` (Substrate.Algebra.Nat.Mod); `mod-suc-bound`
-- supplies the `< suc n` witness `fromℕ<` needs to land back in
-- Fin (suc n).
--
-- Note (gauge): there is no group-law field on PontryaginDual, so
-- these definitions are not yet *proved* to satisfy the abelian-group
-- axioms here; they are the correct operations as DATA. A follow-on
-- slice can add the law witnesses (assoc / id / inv via the Mod
-- arithmetic lemmas).

-- cyclic addition on Fin (suc n): (toℕ a + toℕ b) reduced mod (suc n).
add-mod : (n : ℕ) → Fin (suc n) → Fin (suc n) → Fin (suc n)
add-mod n a b = fromℕ< (mod-suc-bound (toℕ a + toℕ b) n)

-- additive inverse on Fin (suc n): (suc n ∸ toℕ a) reduced mod (suc n).
neg-mod : (n : ℕ) → Fin (suc n) → Fin (suc n)
neg-mod n a = fromℕ< (mod-suc-bound (suc n ∸ toℕ a) n)

-- Chars is now a module parameter of PontryaginDual (⟡set1-paydown); the carrier
-- Fin (suc n) is supplied positionally as the first argument.
ℤ/n-as-Self-Dual : (n : ℕ) → PontryaginDual (Fin (suc n)) (Fin (suc n)) (Fin (suc n))
ℤ/n-as-Self-Dual n = record
  { dual-mult = add-mod n               -- cyclic addition mod (suc n)
  ; dual-id   = zero {n}                -- identity character χ_0
  ; dual-inv  = neg-mod n               -- (suc n) ∸ a, mod (suc n)
  }
