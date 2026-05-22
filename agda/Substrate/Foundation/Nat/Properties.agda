------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties
--
-- Substrate-native properties of ℕ. Thin re-export shim over the
-- per-concern submodules: Add (associativity/commutativity/identity
-- of addition), Mul (multiplication + distributivity), Order
-- (≤ / < helpers).
--
-- Per the file-size discipline: each submodule is small enough to
-- rewrite in one pass; this shim preserves the public interface so
-- downstream imports continue to work unchanged.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties where

open import Substrate.Foundation.Nat.Properties.Add   public
open import Substrate.Foundation.Nat.Properties.Mul   public
open import Substrate.Foundation.Nat.Properties.Order public
