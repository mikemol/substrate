------------------------------------------------------------------------
-- The recovered grade as a number — so the residue is COMPUTABLE and the
-- slack against the predicted width can be read off rather than asserted.
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.ExactWidth where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinTrim.Trimmed

exact-width : {n : ℕ} {b : Bin n} → Trimmed b → ℕ
exact-width (is-zero _)          = zero
exact-width (is-tight e _ _ _ _) = suc e
