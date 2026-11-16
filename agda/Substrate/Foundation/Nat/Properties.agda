------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties
--
-- Substrate-native properties of ℕ, aggregating the per-concern
-- submodules: Add (associativity/commutativity/identity of addition),
-- Mul (multiplication + distributivity), Order (≤ / < helpers).
--
-- This module does not re-export: the ⟡helper-sweep retired
-- `open … public` here, so a consumer imports the submodule that
-- owns the name.
--
-- Per the file-size discipline: each submodule is small enough to
-- rewrite in one pass. Consumers bind at the owning submodule
-- rather than through this aggregate.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties where
