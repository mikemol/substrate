{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KeySchedule  (AI-12k: AES-128 key expansion)
--
-- Completes the Agda AES to a MASTER-KEY cipher.  `keyExpansion` derives the
-- 11 round keys from a 16-byte key by the FIPS-197 §5.2 schedule (per-round:
-- RotWord . SubWord + Rcon, then the 4-word XOR chain); `encrypt-key` /
-- `decrypt-key` are the full key->ciphertext cipher, and `cipher-key-rt` is
-- the complete structural round-trip `decrypt-key key (encrypt-key key s) = s`.
--
-- NOTE: the round-trip is key-schedule-AGNOSTIC (encrypt and decrypt share the
-- SAME expanded keys), so it does NOT validate keyExpansion against FIPS -- the
-- schedule is the SAME algorithm as the FIPS-KAT-validated matlab/python ports,
-- and its end-to-end FIPS-correctness is pinned by AI-7k (the known-answer test).
-- --safe --without-K, 0 postulates, fast (no reflection).
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KeySchedule where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; zipWith; replicate)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2 using (_+_)
-- B-deep: canonical S-box = the proven table lookup (cheap to force), so the
-- key-schedule KAT is a table lookup not a GF inversion. (= sbox-gf, proven.)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable using (sbox)
open import Substrate.Algebra.F2.AES.Round using (Byte; Col; State)
open import Substrate.Algebra.F2.AES.Cipher using (encrypt)

-- the key-schedule unit is a column of 4 bytes (= the State column `Col`).
𝟘b : Byte
𝟘b = replicate 8 F2.𝟘

_⊕w_ : Col → Col → Col
_⊕w_ = zipWith (zipWith _+_)

RotWord : Col → Col
RotWord (b0 ∷ b1 ∷ b2 ∷ b3 ∷ []) = b1 ∷ b2 ∷ b3 ∷ b0 ∷ []

SubWord : Col → Col
SubWord = map sbox

-- round constants Rcon[1..10] = xtime^(j-1)(1): 01 02 04 08 10 20 40 80 1b 36.
rc1  rc2  rc3  rc4  rc5  rc6  rc7  rc8  rc9  rc10 : Byte
rc1  = F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x01
rc2  = F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x02
rc3  = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x04
rc4  = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x08
rc5  = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x10
rc6  = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x20
rc7  = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟘 ∷ []   -- 0x40
rc8  = F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟙 ∷ []   -- 0x80
rc9  = F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x1b
rc10 = F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []   -- 0x36

-- one round-key step (FIPS-197 §5.2): the 4 new words from the previous 4.
nextRoundKey : Byte → State → State
nextRoundKey rc (w0 ∷ w1 ∷ w2 ∷ w3 ∷ []) =
  let t   = SubWord (RotWord w3) ⊕w (rc ∷ 𝟘b ∷ 𝟘b ∷ 𝟘b ∷ [])
      nw0 = w0 ⊕w t
      nw1 = w1 ⊕w nw0
      nw2 = w2 ⊕w nw1
      nw3 = w3 ⊕w nw2
  in nw0 ∷ nw1 ∷ nw2 ∷ nw3 ∷ []

-- KeyExpansion: master key → (k₀, the 9 middle keys, k₁₀).
keyExpansion : State → State × (Vec State 9 × State)
keyExpansion key =
  let k1 = nextRoundKey rc1  key
      k2 = nextRoundKey rc2  k1
      k3 = nextRoundKey rc3  k2
      k4 = nextRoundKey rc4  k3
      k5 = nextRoundKey rc5  k4
      k6 = nextRoundKey rc6  k5
      k7 = nextRoundKey rc7  k6
      k8 = nextRoundKey rc8  k7
      k9 = nextRoundKey rc9  k8
      k10 = nextRoundKey rc10 k9
  in key , ((k1 ∷ k2 ∷ k3 ∷ k4 ∷ k5 ∷ k6 ∷ k7 ∷ k8 ∷ k9 ∷ []) , k10)

rk0 : State → State
rk0 key = proj₁ (keyExpansion key)
rkmid : State → Vec State 9
rkmid key = proj₁ (proj₂ (keyExpansion key))
rk10 : State → State
rk10 key = proj₂ (proj₂ (keyExpansion key))

-- the COMPLETE AES-128 forward cipher: master key → ciphertext.
-- (`decrypt-key` / the master-key round-trip `cipher-key-rt` live in
--  `KeySchedule.RoundTrip` — they force the per-round inverses.)
encrypt-key : State → State → State
encrypt-key key s = encrypt (rk0 key) (rkmid key) (rk10 key) s
