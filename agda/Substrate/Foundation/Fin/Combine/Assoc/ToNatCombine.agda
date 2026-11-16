------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.Assoc.ToNatCombine
--
-- Defines: toℕ-combine
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Fin.Combine.Assoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.Assoc.ToNatCombine where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatInjectPlus
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatRaise



-- combine IS the linear index i·n ℕ+ j.
toℕ-combine : ∀ {m n} (i : Fin m) (j : Fin n) → toℕ (combine i j) ≡ toℕ i * n ℕ+ toℕ j
toℕ-combine {suc m} {n} zero    j = toℕ-inject+ (m * n) j
toℕ-combine {suc m} {n} (suc i) j =
  trans (toℕ-raise n (combine i j))
        (trans (cong (n ℕ+_) (toℕ-combine i j))
               (sym (+ℕ-assoc n (toℕ i * n) (toℕ j))))
