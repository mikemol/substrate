------------------------------------------------------------------------
-- MULTIPLICATION — shift-and-add, LSB-first, on bare bits:
--
--     mulU : Bin m → Bin n → Bin (m ℕ+ n)          -- widths ADD
--     (a ∷ as) · bs  =  (a AND bs)  ℕ+  2·(as · bs)
--
-- The width law IS the signature: `m ℕ+ n` is not a fact to check but where
-- the answer lives. A machine-word carrier computes that width, asserts it
-- fits, and escalates when it does not; here the same rule is the return
-- type. `2·x` is a `false` cons, because doubling in an LSB-first numeral
-- IS the constructor, so nothing here is a reified per-step record — the
-- computation is structural recursion on bare bits and the certificate is
-- a separate theorem over the same bits.
--
-- ⚑ WHY `addBits` MAY DISCARD ITS CARRY HERE — and what that owes. An
-- m-bit numeral times an n-bit numeral is at most
-- (2ᵐ−1)(2ⁿ−1) = 2ᵐ⁺ⁿ − 2ᵐ − 2ⁿ ℕ+ 1 < 2ᵐ⁺ⁿ, so the product always fits the
-- predicted width and every intermediate carry-out is `false`. That is the
-- SOUNDNESS of the prediction, and it is the honest debt of this leaf: it
-- is TRUE and it is NOT PROVED HERE. `carryOut` is discarded on the ground
-- that it vanishes; turning that ground into a term is the accompanying
-- theorem, not a field of `mulU`.
--
-- ⚑ ALSO NOT PROVED HERE: value (mulU as bs) ≡ value as * value bs.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.MulU where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinArith.AddBits
open import Substrate.Algebra.Wedge.BinMul.Zeros
open import Substrate.Algebra.Wedge.BinMul.Sel
open import Substrate.Algebra.Wedge.BinMul.PadHi
open import Substrate.Algebra.Wedge.BinMul.ShiftFits
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Subst

mulU : {m n : ℕ} → Bin m → Bin n → Bin (m ℕ+ n)
mulU {zero}  {n} []       _  = zeros n
mulU {suc m} {n} (a ∷ as) bs =
  addBits false
    (subst Bin (shift-fits m n) (padHi (suc m) (sel a bs)))
    (false ∷ mulU as bs)
