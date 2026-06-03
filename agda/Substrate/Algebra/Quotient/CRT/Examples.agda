------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.CRT.Examples
--
-- Oracle: ℤ/15 ≅ ℤ/3 × ℤ/5 via the full CRT chain
--   modular inverses → idempotents → combine.
-- Inverses of (N,M)=(5,3): 5⁻¹ mod 3 = 2, 3⁻¹ mod 5 = 2 (both by refl).
-- These yield idempotents e₁=10, e₂=6, and combine(1,2)=1·10+2·6=22
-- (≡ 1 mod 3, ≡ 2 mod 5). All by refl.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.CRT.Examples where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Quotient.CRT using (CRT-Witness; combine)
open import Substrate.Algebra.Quotient.CRT.FromIdempotents using (crt-witness)
open import Substrate.Algebra.Quotient.CRT.Inverses
  using (ModInverses; idempotents-from-inverses)

-- the modular inverses for (M,N) = (3,5): 5·2 ≡ 1 mod 3, 3·2 ≡ 1 mod 5.
inv-3-5 : ModInverses 2 4
inv-3-5 = record { invN = 2 ; invM = 2 ; invN-inv = refl ; invM-inv = refl }

-- the full chain: inverses → idempotents → CRT-Witness.
witness-3-5 : CRT-Witness 2 4
witness-3-5 = crt-witness (idempotents-from-inverses inv-3-5)

-- combine(1,2) = 1·10 + 2·6 = 22  (and 22 ≡ 1 mod 3, ≡ 2 mod 5).
combine-1-2 : combine witness-3-5 (1 , 2) ≡ 22
combine-1-2 = refl
