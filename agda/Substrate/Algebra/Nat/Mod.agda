------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod
--
-- Substrate-native modular reduction `_mod-suc_ : ℕ → ℕ → ℕ`.
--
-- The cleanest read: `a mod-suc b` is the canonical-form
-- representative of `a` in the equivalence class of `_≡[ b ]_` on ℕ
-- (the Quotient instance ℕ / ≡[b], where the divisor is `suc b`).
--
-- The substrate's [[homology-cohomology-recursion]] reading:
-- Substrate.Algebra.Quotient gives the universal property; this
-- file gives the canonical-form function for the modular instance.
-- The earlier GCD module's `construct-wedge` was a bridge to
-- stdlib's `Data.Nat.DivMod`; this module replaces it for the
-- mod-reduction-only use case.
--
-- Recursion: STRUCTURAL on `a` alone, no well-founding needed. The
-- step `(suc a) mod-suc b` uses the IH `(a mod-suc b)`:
--   - if suc (a mod-suc b) < suc b, advance the remainder by one;
--   - else (it was = b, the max), wrap to zero.
--
-- This is the substrate's first piece of "modular arithmetic from
-- scratch", with no Data.Nat.DivMod / Data.Nat.Divisibility /
-- Induction.WellFounded touchpoints.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod where

open import Substrate.Foundation.Nat
  using (ℕ; zero; suc; _+_; _<_; _≤_; _<?_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties
  using (≤-suc-r; <-suc-r; ≤-refl; <-suc-self; <-irrefl)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)

------------------------------------------------------------------------
-- 1. Modular reduction.
--
-- `a mod-suc b` returns the canonical-form representative of `a`
-- modulo `suc b`. The divisor is stored as `suc b` rather than as
-- an arbitrary positive ℕ so non-zero-ness is structural.
------------------------------------------------------------------------

_mod-suc_ : ℕ → ℕ → ℕ
zero   mod-suc _ = zero
suc a  mod-suc b with suc (a mod-suc b) <? suc b
... | yes _ = suc (a mod-suc b)
... | no  _ = zero

------------------------------------------------------------------------
-- 2. The remainder-bound.
--
-- `a mod-suc b < suc b` always: the result lives in {0, 1, …, b}.
-- Proof by induction on `a`, dispatching on the same with-clause
-- that defines `_mod-suc_`.
------------------------------------------------------------------------

mod-suc-bound : (a b : ℕ) → (a mod-suc b) < suc b
mod-suc-bound zero    b = s≤s z≤n
mod-suc-bound (suc a) b with suc (a mod-suc b) <? suc b
... | yes sr<sb = sr<sb
... | no  _     = s≤s z≤n

------------------------------------------------------------------------
-- 3. mod-suc-id — mod fixes elements below the modulus.
--
-- For a < suc b, a mod-suc b ≡ a (no wrap occurs). Proof by induction
-- on a, dispatching on the same with-clause that defines _mod-suc_.
-- The `no` branch is impossible by the bound; we discharge it via
-- the IH transported through the comparison.
------------------------------------------------------------------------

mod-suc-id : (a b : ℕ) → a < suc b → a mod-suc b ≡ a
mod-suc-id zero    _ _         = refl
mod-suc-id (suc a) b (s≤s a≤b) with suc (a mod-suc b) <? suc b
                                  | mod-suc-id a b (≤-suc-r a≤b)
... | yes _    | ih = cong suc ih
... | no  ¬lt  | ih =
  ⊥-elim (¬lt (subst (λ k → suc k < suc b) (sym ih) (s≤s a≤b)))

------------------------------------------------------------------------
-- 4. mod-suc-periodic — adding the modulus is identity in mod.
--
-- (a + suc b) mod-suc b ≡ a mod-suc b. Proof by induction on a. The
-- base case uses mod-suc-id (b mod-suc b ≡ b) + the with-clause
-- failing at suc b; the step case threads the IH through the with-
-- comparison.
------------------------------------------------------------------------

mod-suc-periodic : (a b : ℕ) → (a + suc b) mod-suc b ≡ a mod-suc b
mod-suc-periodic zero b
  with suc (b mod-suc b) <? suc b
     | mod-suc-id b b (<-suc-self b)
... | yes lt  | bmodb≡b =
  ⊥-elim (<-irrefl b (subst (λ k → suc k ≤ b) bmodb≡b (s≤s-strip lt)))
  where
    s≤s-strip : ∀ {m n} → suc m < suc n → m < n
    s≤s-strip (s≤s p) = p
... | no  _   | _        = refl
mod-suc-periodic (suc a) b
  with suc ((a + suc b) mod-suc b) <? suc b
     | suc (a mod-suc b)             <? suc b
     | mod-suc-periodic a b
... | yes _   | yes _   | ih = cong suc ih
... | yes p   | no  ¬p  | ih = ⊥-elim (¬p (subst (λ k → suc k < suc b) ih p))
... | no  ¬p  | yes p   | ih = ⊥-elim (¬p (subst (λ k → suc k < suc b) (sym ih) p))
... | no  _   | no  _   | _  = refl

------------------------------------------------------------------------
-- 5. mod-suc-suc — mod commutes with one suc-step (modulo a mod).
--
-- (suc a) mod-suc n ≡ (suc (a mod-suc n)) mod-suc n. Needed by
-- σ-iterate-toℕ for the cyclic-suc HasOrderPerm derivation: lets us
-- thread a `suc` past `mod-suc n` at no cost.
--
-- Both sides expand to a with-clause; we case-split on both
-- discriminants and discharge the impossible cross-cases via
-- mod-suc-id (a mod-suc n) ≡ (a mod-suc n) (idempotence).
------------------------------------------------------------------------

mod-suc-suc : (a n : ℕ) → (suc a) mod-suc n ≡ (suc (a mod-suc n)) mod-suc n
mod-suc-suc a n
  with suc (a mod-suc n) <? suc n
     | suc ((a mod-suc n) mod-suc n) <? suc n
     | mod-suc-id (a mod-suc n) n (mod-suc-bound a n)
... | yes _   | yes _   | aa≡a = cong suc (sym aa≡a)
... | yes p   | no  ¬q  | aa≡a = ⊥-elim (¬q (subst (λ k → suc k < suc n) (sym aa≡a) p))
... | no  ¬p  | yes q   | aa≡a = ⊥-elim (¬p (subst (λ k → suc k < suc n) aa≡a q))
... | no  _   | no  _   | _    = refl

------------------------------------------------------------------------
-- 6. Capstone.
--
-- Substrate-native `_mod-suc_` + bound + mod-suc-id + mod-suc-periodic
-- + mod-suc-suc. Downstream: cyclic-suc on Fin (suc n) + HasOrderPerm
-- (Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic).
------------------------------------------------------------------------
