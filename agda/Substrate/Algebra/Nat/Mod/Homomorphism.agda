------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.Homomorphism
--
-- Modular reduction AS A RING HOMOMORPHISM — the seam bridge between
-- ℕ-truth and ℤ/(suc m)-truth, returned as content (not discharged):
--
--   mod-add-hom  : (a ℕ+ b) mod m ≡ ((a mod m) ℕ+ (b mod m)) mod m
--   mod-mult-hom : (a * b) mod m ≡ ((a mod m) * (b mod m)) mod m
--
-- This is the "reduction-as-homomorphism" wedge — the oriented proof of how
-- ℕ-arithmetic and modular arithmetic relate, the prerequisite for the CRT
-- splitter and Euler/units. Both proven the same way: a = (a mod m) ℕ+
-- (a div m)·(suc m) [div-mod-eq], and adding/multiplying-in any multiple of
-- the modulus is invisible mod the modulus [mod-periodic-mult, via
-- mod-suc-periodic].
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.Homomorphism where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-assoc; *-comm; *-distribʳ-+)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Nat.Nat.DivSuc
open import Substrate.Algebra.Nat.DivMod.Reconstruction using (div-mod-eq)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. Adding a multiple of the modulus is invisible mod the modulus.
------------------------------------------------------------------------

mod-periodic-mult : (x k m : ℕ) → (x ℕ+ k * suc m) mod-suc m ≡ x mod-suc m
mod-periodic-mult x zero    m = cong (_mod-suc m) (+ℕ-identityʳ x)
mod-periodic-mult x (suc k) m =
  trans (cong (_mod-suc m)
              (trans (cong (x ℕ+_) (+ℕ-comm (suc m) (k * suc m)))
                     (sym (+ℕ-assoc x (k * suc m) (suc m)))))
        (trans (mod-suc-periodic (x ℕ+ k * suc m) m)
               (mod-periodic-mult x k m))

------------------------------------------------------------------------
-- 2. Addition homomorphism.
------------------------------------------------------------------------

mod-+-left : (a b m : ℕ) → ((a mod-suc m) ℕ+ b) mod-suc m ≡ (a ℕ+ b) mod-suc m
mod-+-left a b m =
  sym (trans (cong (_mod-suc m) eq)
             (mod-periodic-mult ((a mod-suc m) ℕ+ b) (a div-suc m) m))
  where
    eq : a ℕ+ b ≡ ((a mod-suc m) ℕ+ b) ℕ+ (a div-suc m) * suc m
    eq = trans (cong (_ℕ+ b) (div-mod-eq a m))
               (trans (+ℕ-assoc (a mod-suc m) ((a div-suc m) * suc m) b)
                      (trans (cong ((a mod-suc m) ℕ+_)
                                   (+ℕ-comm ((a div-suc m) * suc m) b))
                             (sym (+ℕ-assoc (a mod-suc m) b ((a div-suc m) * suc m)))))

mod-+-right : (a b m : ℕ) → (a ℕ+ (b mod-suc m)) mod-suc m ≡ (a ℕ+ b) mod-suc m
mod-+-right a b m =
  trans (cong (_mod-suc m) (+ℕ-comm a (b mod-suc m)))
        (trans (mod-+-left b a m) (cong (_mod-suc m) (+ℕ-comm b a)))

mod-add-hom : (a b m : ℕ) →
              (a ℕ+ b) mod-suc m ≡ ((a mod-suc m) ℕ+ (b mod-suc m)) mod-suc m
mod-add-hom a b m =
  trans (sym (mod-+-left a b m)) (sym (mod-+-right (a mod-suc m) b m))

------------------------------------------------------------------------
-- 3. Multiplication homomorphism (same shape, * for ℕ+).
------------------------------------------------------------------------

mod-*-left : (a b m : ℕ) → ((a mod-suc m) * b) mod-suc m ≡ (a * b) mod-suc m
mod-*-left a b m =
  sym (trans (cong (_mod-suc m) eq)
             (mod-periodic-mult ((a mod-suc m) * b) ((a div-suc m) * b) m))
  where
    factor : ((a div-suc m) * suc m) * b ≡ ((a div-suc m) * b) * suc m
    factor = trans (*-assoc (a div-suc m) (suc m) b)
                   (trans (cong ((a div-suc m) *_) (*-comm (suc m) b))
                          (sym (*-assoc (a div-suc m) b (suc m))))
    eq : a * b ≡ ((a mod-suc m) * b) ℕ+ ((a div-suc m) * b) * suc m
    eq = trans (cong (_* b) (div-mod-eq a m))
               (trans (*-distribʳ-+ b (a mod-suc m) ((a div-suc m) * suc m))
                      (cong (((a mod-suc m) * b) ℕ+_) factor))

mod-*-right : (a b m : ℕ) → (a * (b mod-suc m)) mod-suc m ≡ (a * b) mod-suc m
mod-*-right a b m =
  trans (cong (_mod-suc m) (*-comm a (b mod-suc m)))
        (trans (mod-*-left b a m) (cong (_mod-suc m) (*-comm b a)))

mod-mult-hom : (a b m : ℕ) →
               (a * b) mod-suc m ≡ ((a mod-suc m) * (b mod-suc m)) mod-suc m
mod-mult-hom a b m =
  trans (sym (mod-*-left a b m)) (sym (mod-*-right (a mod-suc m) b m))
