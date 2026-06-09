------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.GcdTrace
--
-- The EEATrace witnessing gcd-ℕ a b, taken WHOLESALE from compute-trace.
--
--   gcd-trace    : (a b) → EEATrace a b (gcd-ℕ a b)
--   coprime-trace: (a b) → gcd-ℕ a b ≡ 1 → EEATrace a b 1
--
-- Crucial discipline: we obtain the trace as `proj₂ (compute-trace a b)` and
-- never inspect HOW compute-trace built it. Because `gcd-ℕ a b = proj₁
-- (compute-trace a b)` definitionally, the gcd index lines up by refl — no
-- contact with the Acc recursion (which is NOT proof-irrelevant under --without-K).
-- All continued-fraction reasoning then inducts on the EEATrace's own
-- constructors (base/step), where the shape recurrence is definitional.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.GcdTrace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; subst)
open import Substrate.Foundation.Product using (proj₂)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)

gcd-trace : (a b : ℕ) → EEATrace a b (gcd-ℕ a b)
gcd-trace a b = proj₂ (compute-trace a b)

coprime-trace : (a b : ℕ) → gcd-ℕ a b ≡ 1 → EEATrace a b 1
coprime-trace a b eq = subst (EEATrace a b) eq (gcd-trace a b)
