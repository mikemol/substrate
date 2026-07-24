------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.Round  (AI-11: the forward AES round)  — lean / forward half
--
-- The four forward AES layers on the 4×4-byte State (FIPS-197 §5.1):
--   round       = AddRoundKey ∘ MixColumns ∘ ShiftRows ∘ SubBytes
--   final-round = AddRoundKey ∘ ShiftRows ∘ SubBytes   (no MixColumns)
-- computed through the evaluation-CHEAP tables (`sbox`, `mix-fast`) — GF-inverse-
-- FREE and gmul-round-trip-FREE, so the full-encrypt KAT never deserializes the
-- ~89 MB GF-inversion closure nor MixColumns.Proof.
--
-- The per-round DECRYPT round-trips (`InvSubBytes`/`sub-rt`/`round-rt`/…, which
-- force `inv-sbox`/`sbox-rt`/`mix-fast-round-trip`) live in `Round.RoundTrip`.
-- Fully --safe --without-K, 0 postulates; fast (no reflection over the EEA).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.Round where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; zipWith)
open import Substrate.Algebra.F2 using (F₂; _+_)
-- B-deep: canonical table S-box (= the GF-inversion S-box, proven via
-- SBoxTable.Properties.sbox≡gf); cheap to force.
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable using (sbox)
-- forward MixColumns FORCES through the proved xtime TABLE (MixColumns.Fast); the
-- gmul construction is retained as the theorem mix-fast≡mix (Fast.Properties).
open import Substrate.Algebra.F2.MixColumns.Fast using (mix-fast)

-- the AES state: 4 columns of 4 bytes; a byte is a Vec F₂ 8.
Byte  : Set
Byte  = Vec F₂ 8
Col   : Set
Col   = Vec Byte 4
State : Set
State = Vec Col 4

------------------------------------------------------------------------
-- SubBytes (the table S-box).
------------------------------------------------------------------------
SubBytes    : State → State
SubBytes    = map (map sbox)

------------------------------------------------------------------------
-- MixColumns (the cheap forward mix).
------------------------------------------------------------------------
MixColumns    : State → State
MixColumns    = map mix-fast

------------------------------------------------------------------------
-- AddRoundKey (XOR; self-inverse, bit→byte→col→state).
------------------------------------------------------------------------
addKey : State → State → State
addKey = zipWith (zipWith (zipWith _+_))

------------------------------------------------------------------------
-- ShiftRows (explicit byte permutation).
------------------------------------------------------------------------
ShiftRows : State → State
ShiftRows ((b00 ∷ b01 ∷ b02 ∷ b03 ∷ []) ∷ (b10 ∷ b11 ∷ b12 ∷ b13 ∷ [])
         ∷ (b20 ∷ b21 ∷ b22 ∷ b23 ∷ []) ∷ (b30 ∷ b31 ∷ b32 ∷ b33 ∷ []) ∷ []) =
   (b00 ∷ b11 ∷ b22 ∷ b33 ∷ []) ∷ (b10 ∷ b21 ∷ b32 ∷ b03 ∷ [])
 ∷ (b20 ∷ b31 ∷ b02 ∷ b13 ∷ []) ∷ (b30 ∷ b01 ∷ b12 ∷ b23 ∷ []) ∷ []

------------------------------------------------------------------------
-- THE ROUND (FIPS-197 §5.1).
------------------------------------------------------------------------
round : State → State → State
round k s = addKey k (MixColumns (ShiftRows (SubBytes s)))

final-round : State → State → State
final-round k s = addKey k (ShiftRows (SubBytes s))
