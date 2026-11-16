------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Assoc.CombineAssoc
--
-- Defines: combine-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin.Combine.Assoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Assoc.CombineAssoc where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatSubst
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatCombine
open import Substrate.Foundation.Fin.Combine.Assoc.Arith



------------------------------------------------------------------------
-- 3. THE ASSOCIATOR. Both sides have toℕ = a·n·p ℕ+ b·p ℕ+ c; toℕ-injective closes it.
------------------------------------------------------------------------

combine-assoc : ∀ {m n p} (a : Fin m) (b : Fin n) (c : Fin p) →
  subst Fin (*-assoc m n p) (combine (combine a b) c) ≡ combine a (combine b c)
combine-assoc {m} {n} {p} a b c = toℕ-injective (
  trans (toℕ-subst (*-assoc m n p) (combine (combine a b) c))
  (trans (toℕ-combine (combine a b) c)
  (trans (cong (λ z → z * p ℕ+ toℕ c) (toℕ-combine a b))
  (trans (arith (toℕ a) n (toℕ b) p (toℕ c))
  (trans (cong (toℕ a * (n * p) ℕ+_) (sym (toℕ-combine b c)))
         (sym (toℕ-combine a (combine b c))))))))
