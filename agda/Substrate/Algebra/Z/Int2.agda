------------------------------------------------------------------------
-- Substrate.Algebra.Z.Int2
--
-- Defines: -ℤ_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Int2 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Z.Int



------------------------------------------------------------------------
-- 3. Negation.
--
-- - (+ 0)      = + 0           (zero is self-negating)
-- - (+ suc n)  = -suc n
-- - (-suc n)   = + suc n
------------------------------------------------------------------------

-ℤ_ : ℤ → ℤ
-ℤ (+ zero)    = + zero
-ℤ (+ suc n)   = -suc n
-ℤ (-suc n)    = + suc n
