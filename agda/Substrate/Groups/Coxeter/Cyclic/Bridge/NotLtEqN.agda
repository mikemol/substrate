------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Bridge.NotLtEqN
--
-- Defines: not-lt-eq-n
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.Coxeter.Cyclic.Bridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

-- ⚑ THE TELESCOPE IS THE RETIRED PARENT'S, RECOVERED FROM @771283c8~1.  The
-- decomposition dropped `(n : ℕ)` from every shard while leaving the applied
-- `open import ...Base n` that consumes it, so `n` read as unbound at the
-- import and the whole cohort failed at the same column.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Fin.Properties

module Substrate.Groups.Coxeter.Cyclic.Bridge.NotLtEqN (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Bridge.NotLtAux



not-lt-eq-n : (k : Fin (suc n)) → ¬ (toℕ k < n) → toℕ k ≡ n
not-lt-eq-n k ¬k<n = not-lt-aux (toℕ k) n (toℕ-bound k) ¬k<n
