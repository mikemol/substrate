------------------------------------------------------------------------
-- Substrate.Algebra.Z.Residue
--
-- The ℤ→ℕ residue modℤ z m — the canonical ℕ representative of z mod
-- (suc m). The negative case uses negmod (the additive-inverse residue
-- M ∸ (x mod M), re-reduced). This is the foundation for the modℤ ring
-- homomorphism (next), which closes inverses ← Bézout (and thus CRT from
-- gcd = 1): invN = modℤ (Bézout-coefficient) m.
--
-- The key correctness fact here: negmod IS the additive inverse mod M —
-- (x + negmod x) ≡ 0 (mod M) — so the residue is well-defined.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Residue where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_; _<_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Sub using (∸-+-id)
open import Substrate.Foundation.Nat.Properties.Order using (<→≤)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; suc-mod-suc-self)
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-+-right)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)

------------------------------------------------------------------------
-- 1. negmod x m : the residue of (−x) mod (suc m).
------------------------------------------------------------------------

negmod : ℕ → ℕ → ℕ
negmod x m = (suc m ∸ (x mod-suc m)) mod-suc m

-- (Ⓓ: the local suc-mod-self re-proved Nat.Mod's suc-mod-suc-self (in scope
-- via the open import above); use it directly.)

-- negmod is the additive inverse mod (suc m): (x + negmod x) ≡ 0.
negmod-inverse : (x m : ℕ) → ((x mod-suc m) + negmod x m) mod-suc m ≡ 0
negmod-inverse x m =
  trans (mod-+-right (x mod-suc m) (suc m ∸ (x mod-suc m)) m)
        (trans (cong (_mod-suc m)
                     (trans (+-comm (x mod-suc m) (suc m ∸ (x mod-suc m)))
                            (∸-+-id (suc m) (x mod-suc m) (<→≤ (mod-suc-bound x m)))))
               (suc-mod-suc-self m))

------------------------------------------------------------------------
-- 2. The residue modℤ : ℤ → ℕ → ℕ.
------------------------------------------------------------------------

modℤ : ℤ → ℕ → ℕ
modℤ (+ a)    m = a mod-suc m
modℤ (-suc a) m = negmod (suc a) m

-- on nonnegatives it is just ℕ mod (definitional).
modℤ-+pos : (a m : ℕ) → modℤ (+ a) m ≡ a mod-suc m
modℤ-+pos a m = refl

-- the residue always lands in {0, …, m}.
modℤ-bound : (z : ℤ) (m : ℕ) → modℤ z m < suc m
modℤ-bound (+ a)    m = mod-suc-bound a m
modℤ-bound (-suc a) m = mod-suc-bound (suc m ∸ (suc a mod-suc m)) m
