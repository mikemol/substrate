{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KeySchedule.RoundTrip  (AI-12k: master-key round-trip)
--
-- The complete AES-128 master-key decrypt and its structural round-trip
--   cipher-key-rt : decrypt-key key (encrypt-key key s) ≡ s
-- lifting `Cipher.RoundTrip.cipher-rt` over the expanded key schedule (encrypt
-- and decrypt share the SAME expanded keys). Forcing THIS module deserializes
-- the per-round inverses (→ GF inverse); the forward schedule (KeySchedule)
-- does not. --safe --without-K, 0 postulates.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KeySchedule.RoundTrip where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Algebra.F2.AES.Round using (State)
open import Substrate.Algebra.F2.AES.Cipher.RoundTrip using (decrypt; cipher-rt)
open import Substrate.Algebra.F2.AES.KeySchedule using (rk0; rkmid; rk10; encrypt-key)

decrypt-key : State → State → State
decrypt-key key t = decrypt (rk0 key) (rkmid key) (rk10 key) t

-- the full structural round-trip for a MASTER KEY (decrypt∘encrypt ≡ id).
cipher-key-rt : (key s : State) → decrypt-key key (encrypt-key key s) ≡ s
cipher-key-rt key s = cipher-rt (rk0 key) (rkmid key) (rk10 key) s
