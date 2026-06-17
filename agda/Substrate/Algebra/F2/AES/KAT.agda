{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KAT  (AI-7k: FIPS-197 known-answer pinning)
--
-- Pins the Agda AES to the FIPS-197 test vectors by COMPUTATION.  The verified
-- cipher is FIPS-correct component-by-component:
--   * S-box  = the canonical AES table      — `SBoxTable.sbox-is-aes` (AI-7s, proof)
--   * MixColumns = the FIPS circulant       — `MixColumns` (AI-9, round-trip + coeffs)
--   * ShiftRows  = the explicit FIPS perm    — `Round.ShiftRows`
--   * KeySchedule = the FIPS-197 §5.2 schedule — pinned HERE:
--
-- `keysched-kat` : the Agda `keyExpansion` of the FIPS-197 Appendix A.1 key
--   reproduces the published first round key  d6aa74fd d2af72fa daa678f1 d6ab76fe
--   — EXACTLY, by `refl`.  This validates RotWord / SubWord / Rcon / the XOR
--   chain against the FIPS worked example.
--
-- NOTE on the full encrypt KAT (`encrypt-key key-C1 pt-C1 ≡ ct-C1`): deferred.
-- Normalising the verified MixColumns `gmul` over a 10-round encrypt (~250 GF
-- products) is far too memory-heavy to evaluate here.  The end-to-end
-- composition is instead validated by the Octave oracle (`run_aes_oracle.py`),
-- which runs the FIPS-KAT-identical MATLAB/Python ports; every Agda component is
-- independently FIPS-pinned (above).  --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KAT where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; head)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.AES.Round using (Byte; Col; State)
open import Substrate.Algebra.F2.AES.KeySchedule using (keyExpansion)

-- ℕ → byte (8 bits, LSB-first) and Vec ℕ 16 → State (column-major).
odd : ℕ → F2.F₂
odd zero          = F2.𝟘
odd (suc zero)    = F2.𝟙
odd (suc (suc n)) = odd n
half : ℕ → ℕ
half zero          = 0
half (suc zero)    = 0
half (suc (suc n)) = suc (half n)
nb : ℕ → Byte
nb n =  odd n                                            ∷ odd (half n)
     ∷ odd (half (half n))                               ∷ odd (half (half (half n)))
     ∷ odd (half (half (half (half n))))                 ∷ odd (half (half (half (half (half n)))))
     ∷ odd (half (half (half (half (half (half n))))))   ∷ odd (half (half (half (half (half (half (half n))))))) ∷ []

to-state : Vec ℕ 16 → State
to-state (a0 ∷ a1 ∷ a2 ∷ a3 ∷ a4 ∷ a5 ∷ a6 ∷ a7 ∷ a8 ∷ a9 ∷ a10 ∷ a11 ∷ a12 ∷ a13 ∷ a14 ∷ a15 ∷ []) =
    (nb a0  ∷ nb a1  ∷ nb a2  ∷ nb a3  ∷ [])
  ∷ (nb a4  ∷ nb a5  ∷ nb a6  ∷ nb a7  ∷ [])
  ∷ (nb a8  ∷ nb a9  ∷ nb a10 ∷ nb a11 ∷ [])
  ∷ (nb a12 ∷ nb a13 ∷ nb a14 ∷ nb a15 ∷ []) ∷ []

-- FIPS-197 Appendix A.1 cipher key and its first round key (published schedule).
key-C1 : Vec ℕ 16
key-C1 = 0 ∷ 1 ∷ 2 ∷ 3 ∷ 4 ∷ 5 ∷ 6 ∷ 7 ∷ 8 ∷ 9 ∷ 10 ∷ 11 ∷ 12 ∷ 13 ∷ 14 ∷ 15 ∷ []
k1-expected : Vec ℕ 16   -- d6aa74fd d2af72fa daa678f1 d6ab76fe
k1-expected = 214 ∷ 170 ∷ 116 ∷ 253 ∷ 210 ∷ 175 ∷ 114 ∷ 250
            ∷ 218 ∷ 166 ∷ 120 ∷ 241 ∷ 214 ∷ 171 ∷ 118 ∷ 254 ∷ []

-- THE KEY-SCHEDULE KNOWN-ANSWER TEST (RotWord/SubWord/Rcon/XOR vs FIPS-197).
keysched-kat : head (proj₁ (proj₂ (keyExpansion (to-state key-C1)))) ≡ to-state k1-expected
keysched-kat = refl
