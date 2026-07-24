------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.Cipher  (AI-12c: the forward AES-128 cipher)  — lean / forward half
--
-- AES-128 encryption: k₀ pre-whiten · 9 middle rounds · k₁₀ final round
-- (FIPS-197 §5.1), lifted over the 11 round keys through the cheap tables
-- (`round`/`final-round` from AES.Round). GF-inverse-FREE, so the full-encrypt
-- KAT forces only table lookups.
--
-- The structural decrypt∘encrypt round-trip (`decrypt`/`cipher-rt`, which force
-- the per-round inverses) lives in `Cipher.RoundTrip`.
-- Fully --safe --without-K, 0 postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.Cipher where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2.AES.Round using (State; round; final-round; addKey)

------------------------------------------------------------------------
-- generic forward fold (the cipher-level composition combinator).
------------------------------------------------------------------------
fold : {A S : Set} {n : ℕ} (f : A → S → S) → Vec A n → S → S
fold f []       s = s
fold f (k ∷ ks) s = fold f ks (f k s)

------------------------------------------------------------------------
-- AES-128: k₀ pre-whiten · 9 middle rounds · k₁₀ final round (FIPS-197 §5.1).
------------------------------------------------------------------------
encrypt : State → Vec State 9 → State → State → State
encrypt k0 mid k10 s = final-round k10 (fold round mid (addKey k0 s))
