------------------------------------------------------------------------
-- The one commutation the shift costs. The partial product carries the
-- MULTIPLICAND's width n; padding it by `suc m` high zeros lands it at
-- `n + suc m`, while the answer lives at `suc (m + n)` — the two differ by
-- nothing but commutativity. Confining the transport to this single
-- equation is why MulU indexes at `m + n` and not `n + m`: recursing on
-- the FIRST operand makes both `zero + n` and `suc m + n` reduce, so the
-- doubling side needs no transport at all. The other convention costs two.
-- Context: Substrate/Algebra/Wedge/BinMul/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinMul.ShiftFits where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans
shift-fits m n = trans (+ℕ-suc n m) (cong suc (+ℕ-comm n m))
