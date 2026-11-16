------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Properties.Mul.TimesDistribLPlus
--
-- Defines: *-distribˡ-+
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat.Properties.Mul; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Properties.Mul.TimesDistribLPlus where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Foundation.Eq.Trans



*-distribˡ-+ : (a m n : ℕ) → a * (m ℕ+ n) ≡ a * m ℕ+ a * n
*-distribˡ-+ zero    _ _ = refl
*-distribˡ-+ (suc a) m n =
  let ih = *-distribˡ-+ a m n
      lemma : (m ℕ+ n) ℕ+ (a * (m ℕ+ n)) ≡ (m ℕ+ a * m) ℕ+ (n ℕ+ a * n)
      lemma = cong-trans ((m ℕ+ n) ℕ+_) ih
              (trans (+ℕ-assoc m n (a * m ℕ+ a * n))
                     (cong-trans (m ℕ+_)
                        (sym-trans (+ℕ-assoc n (a * m) (a * n))
                           (cong-trans (_ℕ+ (a * n)) (+ℕ-comm n (a * m))
                              (+ℕ-assoc (a * m) n (a * n))))
                        (sym (+ℕ-assoc m (a * m) (n ℕ+ a * n)))))
  in lemma
