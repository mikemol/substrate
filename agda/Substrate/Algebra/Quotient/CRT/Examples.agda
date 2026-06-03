------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT.Examples
--
-- Oracle: ℤ/15 ≅ ℤ/3 × ℤ/5 via the CRT combine. Idempotents e₁=10
-- (≡1 mod 3, ≡0 mod 5), e₂=6 (≡0 mod 3, ≡1 mod 5); all facts by refl.
-- The CRT-Witness construction typechecks the combine-mod proofs; the
-- combine value is checked concretely.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT.Examples where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Quotient.CRT using (CRT-Witness; combine)
open import Substrate.Algebra.Quotient.CRT.Idempotents using (CRTIdempotents)
open import Substrate.Algebra.Quotient.CRT.FromIdempotents using (crt-witness)

-- the idempotents for (M,N) = (3,5), i.e. (suc 2, suc 4).
idem-3-5 : CRTIdempotents 2 4
idem-3-5 = record
  { e₁ = 10 ; e₂ = 6
  ; e₁-mod-m = refl ; e₁-mod-n = refl
  ; e₂-mod-m = refl ; e₂-mod-n = refl
  }

witness-3-5 : CRT-Witness 2 4
witness-3-5 = crt-witness idem-3-5

-- combine(1,2) = 1·10 + 2·6 = 22  (and 22 ≡ 1 mod 3, ≡ 2 mod 5).
combine-1-2 : combine witness-3-5 (1 , 2) ≡ 22
combine-1-2 = refl
