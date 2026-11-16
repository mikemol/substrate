------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT.FromTrace
--
-- The last link, closing the whole CRT chain from gcd = 1:
--   combine ← idempotents ← inverses ← BÉZOUT (modular EEA fold).
-- From a coprimality trace, bezout-mod gives (s·M ℕ+ t·N) ≡ 1 (mod M); since
-- s·M ≡ 0 (mod M), the coefficient t is N⁻¹ mod M. Two such traces assemble
-- the full CRT-Witness — no hand-given inverses or idempotents.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT.FromTrace where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul using (*-comm)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-add-hom)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.BezoutMod using (bezout-mod)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.Quotient.CRT using (CRT-Witness; combine)
-- ⚑ DEAD CLAUSE ENTRY, found by `--clause-audit --unused` (ⓉCLAUSE-UNUSED).
-- This file reaches the CRT witness through `FromIdempotents.crt-witness`
-- (below) and never names the record type itself.
open import Substrate.Algebra.Quotient.CRT.Idempotents
open import Substrate.Algebra.Quotient.CRT.Inverses
  using (ModInverses; idempotents-from-inverses; modulus-multiple)
open import Substrate.Algebra.Quotient.CRT.FromIdempotents using (crt-witness)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. The modular inverse of N = suc n, mod M = suc m, from a coprime trace.
------------------------------------------------------------------------

inverse-from-trace :
  {m n : ℕ} → EEATrace (suc m) (suc n) 1 →
  Σ ℕ (λ invN → (suc n * invN) mod-suc m ≡ 1 mod-suc m)
inverse-from-trace {m} {n} tr with bezout-mod m tr
... | (s , t , eq) = t , proof
  where
    mod-idem-m : (a : ℕ) → (a mod-suc m) mod-suc m ≡ a mod-suc m
    mod-idem-m a = mod-suc-id (a mod-suc m) m (mod-suc-bound a m)
    sM-zero : (s * suc m) mod-suc m ≡ 0
    sM-zero = trans (cong (_mod-suc m) (*-comm s (suc m))) (modulus-multiple m s)
    drop : ((s * suc m) ℕ+ (t * suc n)) mod-suc m ≡ (t * suc n) mod-suc m
    drop = trans (mod-add-hom (s * suc m) (t * suc n) m)
                 (trans (cong (λ z → (z ℕ+ ((t * suc n) mod-suc m)) mod-suc m) sM-zero)
                        (mod-idem-m (t * suc n)))
    proof : (suc n * t) mod-suc m ≡ 1 mod-suc m
    proof = trans (cong (_mod-suc m) (*-comm (suc n) t)) (trans (sym drop) eq)

------------------------------------------------------------------------
-- 2. For M = suc (suc m) ≥ 2, the residue of 1 is 1.
------------------------------------------------------------------------

one-mod : (m : ℕ) → 1 mod-suc (suc m) ≡ 1
one-mod m = mod-suc-id 1 (suc m) (s≤s (s≤s z≤n))

------------------------------------------------------------------------
-- 3. Assemble the full CRT-Witness from two coprime traces (M,N ≥ 2).
------------------------------------------------------------------------

crt-from-traces :
  {m n : ℕ} →
  EEATrace (suc (suc m)) (suc (suc n)) 1 →
  EEATrace (suc (suc n)) (suc (suc m)) 1 →
  CRT-Witness (suc m) (suc n)
crt-from-traces {m} {n} traceMN traceNM =
  crt-witness (idempotents-from-inverses inverses)
  where
    invN-data = inverse-from-trace {suc m} {suc n} traceMN
    invM-data = inverse-from-trace {suc n} {suc m} traceNM
    inverses : ModInverses (suc m) (suc n)
    inverses = record
      { invN = proj₁ invN-data
      ; invM = proj₁ invM-data
      ; invN-inv = trans (proj₂ invN-data) (one-mod m)
      ; invM-inv = trans (proj₂ invM-data) (one-mod n)
      }

------------------------------------------------------------------------
-- Oracles: 5⁻¹ mod 3 = 2; and ℤ/15 ≅ ℤ/3 × ℤ/5 entirely from gcd traces.
------------------------------------------------------------------------

inv-5-mod-3-value : proj₁ (inverse-from-trace {2} {4} (proj₂ (compute-trace 3 5))) ≡ 2
inv-5-mod-3-value = refl

witness-3-5 : CRT-Witness 2 4
witness-3-5 = crt-from-traces {1} {3}
  (proj₂ (compute-trace 3 5)) (proj₂ (compute-trace 5 3))

-- combine(1,2) = 22 (≡ 1 mod 3, ≡ 2 mod 5) — all from gcd computation.
combine-1-2 : combine witness-3-5 (1 , 2) ≡ 22
combine-1-2 = refl
