------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Nat
--
-- Defines: suc, zero, ℕ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Nat where




------------------------------------------------------------------------
-- The natural-number datatype + BUILTIN.
------------------------------------------------------------------------

data ℕ : Set where
  zero : ℕ
  suc  : ℕ → ℕ

{-# BUILTIN NATURAL ℕ #-}

-- KNOWN ISSUE (Agda 2.8.0) — do NOT bind BUILTIN NATPLUS / NATTIMES downstream.
-- This module binds BUILTIN NATURAL but deliberately NOT NATPLUS / NATTIMES.
-- Any module downstream of substrate that binds either crashes Agda with an
-- INTERNAL ERROR (DuplicateBuiltinBinding -> Signature.hs:983), not a clean
-- user-facing error. Same root as why a String carrier is banned in the prose
-- engine: Agda.Builtin.String transitively drags in Agda.Builtin.Nat, whose
-- NATPLUS/NATTIMES bindings then duplicate against this cone. Consequence for
-- consumers: closed numeric values must stay syntactic (proofs at big-valued
-- types must never whnf them) rather than being rebound to fast builtin
-- arithmetic.

------------------------------------------------------------------------
-- Arithmetic.
------------------------------------------------------------------------
