{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.AES  (AI-19: the verified-AES capstone)
--
-- One import point for the whole machine-checked AES-128 result.  Re-exports
-- the headline theorems; `--safe --without-K`, zero postulates throughout.
--
--   THE FIELD
--     GF2⁸-Field      : Field (Poly 8)              GF(2⁸)=F₂[x]/(x⁸+x⁴+x³+x+1)   [AI-8]
--
--   THE LAYERS (each inverse undoes its forward map)
--     sbox-rt         : inv-sbox (sbox a)        ≡ a   SubBytes               [AI-10]
--     mixcolumns-round-trip : inv (mix col)      ≡ col MixColumns             [AI-9]
--     round-rt        : inv-round k (round k s)  ≡ s   the round              [AI-11]
--     final-round-rt  : … (final round, no MixColumns)                       [AI-11]
--
--   THE CIPHER  (decrypt ∘ encrypt ≡ id, --safe, 0 postulates)
--     cipher-rt       : decrypt ks (encrypt ks s)         ≡ s  (round keys)  [AI-12c]
--     cipher-key-rt   : decrypt-key key (encrypt-key key s) ≡ s (master key) [AI-12k]
--
--   FIPS-197 CORRECTNESS  (the verified construction IS the standard — NOT just
--   self-consistent).  These are CONCRETE reflections (slow to normalise), kept
--   in their own modules so this hub stays fast; cite them directly:
--     • Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable.Properties.sbox-is-aes [AI-7s]
--         byte-val (sbox a) ≡ AES-SBOX[byte-val a]   ∀a  (verified S-box = the table)
--     • Substrate.Algebra.F2.AES.KAT.keysched-kat                            [AI-7k]
--         keyExpansion (FIPS-A.1 key) ≡ the published first round key
--     • the Octave oracle (mat260 oracle/run_aes_oracle.py) cross-checks the
--       MATLAB ∥ Python ports against the FIPS-197 KATs and each other.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.AES where

-- AI-8 — GF(2⁸) is a field.
open import Substrate.Algebra.F2.Polynomial.Wedge.AsField using (GF2⁸-Field) public

-- AI-9 — MixColumns and its round-trip.
open import Substrate.Algebra.F2.MixColumns.Proof using (mix; mixcolumns-round-trip) public

-- AI-10 — the S-box and its round-trip.
-- B-deep: canonical table S-box (= the GF-inversion S-box, proven by
-- SBoxTable.Properties.sbox≡gf); cheap to force, FIPS rigor preserved.
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable using (sbox) public
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable.Properties using (inv-sbox; sbox-rt) public

-- AI-11 — the AES round (normal + final) and their round-trips.
open import Substrate.Algebra.F2.AES.Round using (State; round; final-round) public
open import Substrate.Algebra.F2.AES.Round.RoundTrip
  using (inv-round; inv-final-round; round-rt; final-round-rt) public

-- AI-12c — the cipher and its round-trip (round-key-parametric).
open import Substrate.Algebra.F2.AES.Cipher using (encrypt) public
open import Substrate.Algebra.F2.AES.Cipher.RoundTrip using (decrypt; cipher-rt) public

-- AI-12k — the complete master-key cipher, key schedule, and round-trip.
open import Substrate.Algebra.F2.AES.KeySchedule using (keyExpansion; encrypt-key) public
open import Substrate.Algebra.F2.AES.KeySchedule.RoundTrip using (decrypt-key; cipher-key-rt) public
