------------------------------------------------------------------------
-- Substrate.Algebra.Z.Properties.MulFull.SucInjectiveInt
--
-- Defines: -suc-injectiveℤ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Z.Properties.MulFull; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Properties.MulFull.SucInjectiveInt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.Z.Int
open import Substrate.Foundation.Eq



-suc-injectiveℤ : {j k : ℕ} → (-suc j) ≡ (-suc k) → j ≡ k
-suc-injectiveℤ refl = refl
