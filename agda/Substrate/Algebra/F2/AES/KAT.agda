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
-- The full encrypt KAT (`encrypt-key key-C1 pt-C1 ≡ ct-C1`) is DISCHARGED in
-- `KAT.Full.encrypt-kat-C1` (was deferred — the monolithic refl blew up; see the
-- per-round/per-key decomposition + parameterized-module assembly there). The Octave
-- oracle (`run_aes_oracle.py`) remains as an independent cross-check.
-- --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KAT where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; head)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.AES.Round using (Byte; Col; State)
open import Substrate.Algebra.F2.AES.KeySchedule using (keyExpansion)
open import Substrate.Algebra.F2.MixColumns.Fast using (mix-fast)

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

------------------------------------------------------------------------
-- THE MIXCOLUMNS COMPONENT KNOWN-ANSWER TEST (the canonical Daemen–Rijmen
-- diffusion example): MixColumns column [d4 bf 5d 30] = [04 66 81 e5], by `refl`.
-- This pins the DIFFUSION layer to its published value — the missing component
-- KAT alongside `keysched-kat`. It is CHEAP because `mix-fast` forces through the
-- proved `xtime` TABLE (MixColumns.Fast → GF256.XtimeTable, `xtime-is-aes`), with
-- the GF construction retained as the theorem `mix-fast≡mix`: the table IS the
-- verified MixColumns, exactly as the SBOX table IS the verified S-box.
------------------------------------------------------------------------
mixcol-in  : Col          -- [0xd4, 0xbf, 0x5d, 0x30]
mixcol-in  = nb 212 ∷ nb 191 ∷ nb 93 ∷ nb 48 ∷ []
mixcol-out : Col          -- [0x04, 0x66, 0x81, 0xe5]
mixcol-out = nb 4 ∷ nb 102 ∷ nb 129 ∷ nb 229 ∷ []

mixcolumns-kat : mix-fast mixcol-in ≡ mixcol-out
mixcolumns-kat = refl

------------------------------------------------------------------------
-- THE FULL-ENCRYPT KAT (FIPS-197 Appendix C.1): pt-C1 → ct-C1 under key-C1.
-- NO LONGER DEFERRED — discharged in `KAT.Full.encrypt-kat-C1`:
--   encrypt-key (to-state key-C1) (to-state pt-C1) ≡ to-state ct-C1
-- The monolithic `refl` DID blow up (measured > 30 min, > 5.6 GB) — two deep chains
-- (the ten-round composition AND the exponential key-schedule word recursion)
-- normalise at once with no term sharing. `KAT.Full` dissolves both with the
-- parameterized-module pattern: assemble ABSTRACT over keys/states (round / fold /
-- nextRoundKey neutral ⇒ nothing forced), supply the concrete one-step pins
-- (KAT.KeyPins per key step, KAT.RoundN per round, KAT.Pre, KAT.Full.fin), and
-- instantiate by `open` (no conversion ⇒ no re-normalisation across the boundary).
-- Whole chain builds in ~27 s, each module ≤ 3 s — within the 600 s / 1 GB gate.
-- pt-C1 / ct-C1 live here (used by KAT.Trace); the proof is in KAT.Full.
------------------------------------------------------------------------
pt-C1 : Vec ℕ 16   -- 00112233445566778899aabbccddeeff
pt-C1 = 0 ∷ 17 ∷ 34 ∷ 51 ∷ 68 ∷ 85 ∷ 102 ∷ 119 ∷ 136 ∷ 153 ∷ 170 ∷ 187 ∷ 204 ∷ 221 ∷ 238 ∷ 255 ∷ []
ct-C1 : Vec ℕ 16   -- 69c4e0d86a7b0430d8cdb78070b4c55a
ct-C1 = 105 ∷ 196 ∷ 224 ∷ 216 ∷ 106 ∷ 123 ∷ 4 ∷ 48 ∷ 216 ∷ 205 ∷ 183 ∷ 128 ∷ 112 ∷ 180 ∷ 197 ∷ 90 ∷ []
