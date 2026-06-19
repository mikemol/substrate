------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.Round  (AI-11: the AES round + per-round round-trip)
--
-- Assembles the four AES layers on the 4×4-byte State and proves that the
-- inverse round undoes the round (InvRound ∘ Round ≡ id), for both the normal
-- round (with MixColumns) and the final round (without).  This is the inductive
-- step of the full decrypt∘encrypt round-trip.
--
-- The reusable costructure is "a reversible layer": each layer L has an inverse
-- invL with `invL ∘ L ≡ id`, and the round telescopes through them.  Two generic
-- combinators discharge three of the four layers:
--   map-rt        — SubBytes (sbox-rt, AI-10) and MixColumns (per-column, AI-9)
--   zipWith-self  — AddRoundKey (XOR self-inverse, bit→byte→col→state)
-- ShiftRows is an explicit byte permutation, so its round-trip is `refl`.
-- Fully --safe --without-K, 0 postulates; fast (no reflection over the EEA).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.Round where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; zipWith)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2 using (F₂; _+_; +-assoc; +-identityˡ; +-self-inverse)
-- B-deep: canonical table S-box + re-derived round-trip (= the GF-inversion
-- S-box, proven via SBoxTable.sbox≡gf); cheap to force.
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable using (sbox; inv-sbox; sbox-rt)
open import Substrate.Algebra.F2.MixColumns.Proof using (mixcolumns-round-trip)
  renaming (inv to mix-inv)
-- forward MixColumns FORCES through the proved xtime TABLE (MixColumns.Fast); the
-- gmul construction is retained as the theorem mix-fast≡mix (so this is cheap to
-- evaluate, e.g. the full-encrypt KAT, while the round-trip is preserved).
open import Substrate.Algebra.F2.MixColumns.Fast using (mix-fast; mix-fast-round-trip)

-- the AES state: 4 columns of 4 bytes; a byte is a Vec F₂ 8.
Byte  : Set
Byte  = Vec F₂ 8
Col   : Set
Col   = Vec Byte 4
State : Set
State = Vec Col 4

------------------------------------------------------------------------
-- two generic reversibility combinators (the reusable costructure).
------------------------------------------------------------------------
map-rt : {A : Set} {n : ℕ} (f g : A → A) → ((x : A) → g (f x) ≡ x)
       → (v : Vec A n) → map g (map f v) ≡ v
map-rt f g rt []       = refl
map-rt f g rt (x ∷ xs) = cong₂ _∷_ (rt x) (map-rt f g rt xs)

zipWith-self : {A : Set} {n : ℕ} (op : A → A → A)
             → ((k x : A) → op k (op k x) ≡ x)
             → (k v : Vec A n) → zipWith op k (zipWith op k v) ≡ v
zipWith-self op self []       []       = refl
zipWith-self op self (k ∷ ks) (x ∷ xs) = cong₂ _∷_ (self k x) (zipWith-self op self ks xs)

------------------------------------------------------------------------
-- SubBytes (reuse the S-box round-trip, AI-10).
------------------------------------------------------------------------
SubBytes    : State → State
SubBytes    = map (map sbox)
InvSubBytes : State → State
InvSubBytes = map (map inv-sbox)
sub-rt : (s : State) → InvSubBytes (SubBytes s) ≡ s
sub-rt = map-rt (map sbox) (map inv-sbox) (map-rt sbox inv-sbox sbox-rt)

------------------------------------------------------------------------
-- MixColumns (reuse AI-9 per-column round-trip).
------------------------------------------------------------------------
MixColumns    : State → State
MixColumns    = map mix-fast
InvMixColumns : State → State
InvMixColumns = map mix-inv
mix-rt : (s : State) → InvMixColumns (MixColumns s) ≡ s
mix-rt = map-rt mix-fast mix-inv mix-fast-round-trip

------------------------------------------------------------------------
-- AddRoundKey (XOR; self-inverse, bit→byte→col→state).
------------------------------------------------------------------------
bit-self : (k x : F₂) → k + (k + x) ≡ x
bit-self k x = trans (sym (+-assoc k k x)) (trans (cong (_+ x) (+-self-inverse k)) (+-identityˡ x))

addKey : State → State → State
addKey = zipWith (zipWith (zipWith _+_))
add-rt : (k s : State) → addKey k (addKey k s) ≡ s
add-rt = zipWith-self (zipWith (zipWith _+_))
           (zipWith-self (zipWith _+_) (zipWith-self _+_ bit-self))

------------------------------------------------------------------------
-- ShiftRows (explicit byte permutation; round-trip by refl).
------------------------------------------------------------------------
ShiftRows : State → State
ShiftRows ((b00 ∷ b01 ∷ b02 ∷ b03 ∷ []) ∷ (b10 ∷ b11 ∷ b12 ∷ b13 ∷ [])
         ∷ (b20 ∷ b21 ∷ b22 ∷ b23 ∷ []) ∷ (b30 ∷ b31 ∷ b32 ∷ b33 ∷ []) ∷ []) =
   (b00 ∷ b11 ∷ b22 ∷ b33 ∷ []) ∷ (b10 ∷ b21 ∷ b32 ∷ b03 ∷ [])
 ∷ (b20 ∷ b31 ∷ b02 ∷ b13 ∷ []) ∷ (b30 ∷ b01 ∷ b12 ∷ b23 ∷ []) ∷ []
InvShiftRows : State → State
InvShiftRows ((b00 ∷ b01 ∷ b02 ∷ b03 ∷ []) ∷ (b10 ∷ b11 ∷ b12 ∷ b13 ∷ [])
            ∷ (b20 ∷ b21 ∷ b22 ∷ b23 ∷ []) ∷ (b30 ∷ b31 ∷ b32 ∷ b33 ∷ []) ∷ []) =
   (b00 ∷ b31 ∷ b22 ∷ b13 ∷ []) ∷ (b10 ∷ b01 ∷ b32 ∷ b23 ∷ [])
 ∷ (b20 ∷ b11 ∷ b02 ∷ b33 ∷ []) ∷ (b30 ∷ b21 ∷ b12 ∷ b03 ∷ []) ∷ []
shift-rt : (s : State) → InvShiftRows (ShiftRows s) ≡ s
shift-rt ((b00 ∷ b01 ∷ b02 ∷ b03 ∷ []) ∷ (b10 ∷ b11 ∷ b12 ∷ b13 ∷ [])
        ∷ (b20 ∷ b21 ∷ b22 ∷ b23 ∷ []) ∷ (b30 ∷ b31 ∷ b32 ∷ b33 ∷ []) ∷ []) = refl

------------------------------------------------------------------------
-- THE ROUND + its inverse + per-round round-trip.
-- round       = AddRoundKey ∘ MixColumns ∘ ShiftRows ∘ SubBytes  (FIPS-197 §5.1)
-- final-round = AddRoundKey ∘ ShiftRows ∘ SubBytes               (no MixColumns)
------------------------------------------------------------------------
round : State → State → State
round k s = addKey k (MixColumns (ShiftRows (SubBytes s)))
inv-round : State → State → State
inv-round k t = InvSubBytes (InvShiftRows (InvMixColumns (addKey k t)))

round-rt : (k s : State) → inv-round k (round k s) ≡ s
round-rt k s =
  trans (cong (λ x → InvSubBytes (InvShiftRows (InvMixColumns x)))
              (add-rt k (MixColumns (ShiftRows (SubBytes s)))))
  (trans (cong (λ x → InvSubBytes (InvShiftRows x)) (mix-rt (ShiftRows (SubBytes s))))
  (trans (cong InvSubBytes (shift-rt (SubBytes s)))
         (sub-rt s)))

final-round : State → State → State
final-round k s = addKey k (ShiftRows (SubBytes s))
inv-final-round : State → State → State
inv-final-round k t = InvSubBytes (InvShiftRows (addKey k t))

final-round-rt : (k s : State) → inv-final-round k (final-round k s) ≡ s
final-round-rt k s =
  trans (cong (λ x → InvSubBytes (InvShiftRows x)) (add-rt k (ShiftRows (SubBytes s))))
  (trans (cong InvSubBytes (shift-rt (SubBytes s)))
         (sub-rt s))
