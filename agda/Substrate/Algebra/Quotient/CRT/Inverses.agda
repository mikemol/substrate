------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT.Inverses
--
-- The minimal ℕ coprimality content for CRT: a pair of modular inverses
-- (invN = N⁻¹ mod M, invM = M⁻¹ mod N). From them the CRT idempotents glue
-- cleanly: e₁ = N·invN is ≡ 1 mod M (the inverse property, directly) and
-- ≡ 0 mod N (a multiple of N, via mod-mult-hom + suc-mod-self); e₂ mirrors.
--
-- This is the layer combine ← idempotents ← INVERSES. The remaining step
-- inverses ← Bézout (the ℤ→ℕ residue of the Bézout coefficient) is the one
-- focused target left to derive CRT from gcd = 1.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT.Inverses where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-periodic)
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-mult-hom)
open import Substrate.Algebra.Quotient.CRT.Idempotents using (CRTIdempotents)

-- (suc n) mod (suc n) ≡ 0 — the modulus is 0 mod itself.
suc-mod-self : (n : ℕ) → (suc n) mod-suc n ≡ 0
suc-mod-self n = mod-suc-periodic 0 n

-- a multiple of the modulus is 0 mod the modulus: (suc n · k) mod (suc n) ≡ 0.
modulus-multiple : (n k : ℕ) → (suc n * k) mod-suc n ≡ 0
modulus-multiple n k =
  trans (mod-mult-hom (suc n) k n)
        (cong (λ z → (z * (k mod-suc n)) mod-suc n) (suc-mod-self n))

------------------------------------------------------------------------
-- The modular-inverse data and the idempotents it yields.
------------------------------------------------------------------------

record ModInverses (m n : ℕ) : Set where
  field
    invN invM : ℕ
    -- N · invN ≡ 1 (mod M)   and   M · invM ≡ 1 (mod N)
    invN-inv : (suc n * invN) mod-suc m ≡ 1
    invM-inv : (suc m * invM) mod-suc n ≡ 1

idempotents-from-inverses : {m n : ℕ} → ModInverses m n → CRTIdempotents m n
idempotents-from-inverses {m} {n} inv = record
  { e₁ = suc n * ModInverses.invN inv
  ; e₂ = suc m * ModInverses.invM inv
  ; e₁-mod-m = ModInverses.invN-inv inv
  ; e₁-mod-n = modulus-multiple n (ModInverses.invN inv)
  ; e₂-mod-m = modulus-multiple m (ModInverses.invM inv)
  ; e₂-mod-n = ModInverses.invM-inv inv
  }
