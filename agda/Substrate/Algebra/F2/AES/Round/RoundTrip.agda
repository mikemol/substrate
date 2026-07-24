------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.Round.RoundTrip  (the per-round DECRYPT round-trip)
--
-- Proves the inverse round undoes the forward round (InvRound ∘ Round ≡ id),
-- for both the normal round (with MixColumns) and the final round (without) —
-- the inductive step of the full decrypt∘encrypt round-trip.
--
-- The reusable costructure is "a reversible layer": each layer L has an inverse
-- invL with `invL ∘ L ≡ id`, and the round telescopes through them.
--   map-rt        — SubBytes (sbox-rt) and MixColumns (per-column)
--   zipWith-self  — AddRoundKey (XOR self-inverse)
-- ShiftRows is an explicit byte permutation, so its round-trip is `refl`.
--
-- Forcing THIS module deserializes the GF inverse (SBoxTable.Properties →
-- Wedge.Inverse) and MixColumns.Proof; the FORWARD round (Round) does not.
-- --safe --without-K, 0 postulates.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.Round.RoundTrip where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; zipWith)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2 using (F₂; _+_; +-assoc; +-identityˡ; +-self-inverse)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable using (sbox)
open import Substrate.Algebra.F2.Polynomial.Wedge.SBoxTable.Properties using (inv-sbox; sbox-rt)
open import Substrate.Algebra.F2.MixColumns.Proof using (mixcolumns-round-trip)
  renaming (inv to mix-inv)
open import Substrate.Algebra.F2.MixColumns.Fast using (mix-fast)
open import Substrate.Algebra.F2.MixColumns.Fast.Properties using (mix-fast-round-trip)
open import Substrate.Algebra.F2.AES.Round
  using (State; SubBytes; MixColumns; ShiftRows; addKey; round; final-round)

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
-- SubBytes⁻¹ (reuse the S-box round-trip).
------------------------------------------------------------------------
InvSubBytes : State → State
InvSubBytes = map (map inv-sbox)
sub-rt : (s : State) → InvSubBytes (SubBytes s) ≡ s
sub-rt = map-rt (map sbox) (map inv-sbox) (map-rt sbox inv-sbox sbox-rt)

------------------------------------------------------------------------
-- MixColumns⁻¹ (reuse the per-column round-trip).
------------------------------------------------------------------------
InvMixColumns : State → State
InvMixColumns = map mix-inv
mix-rt : (s : State) → InvMixColumns (MixColumns s) ≡ s
mix-rt = map-rt mix-fast mix-inv mix-fast-round-trip

------------------------------------------------------------------------
-- AddRoundKey⁻¹ (XOR self-inverse, bit→byte→col→state).
------------------------------------------------------------------------
bit-self : (k x : F₂) → k + (k + x) ≡ x
bit-self k x = trans (sym (+-assoc k k x)) (trans (cong (_+ x) (+-self-inverse k)) (+-identityˡ x))

add-rt : (k s : State) → addKey k (addKey k s) ≡ s
add-rt = zipWith-self (zipWith (zipWith _+_))
           (zipWith-self (zipWith _+_) (zipWith-self _+_ bit-self))

------------------------------------------------------------------------
-- ShiftRows⁻¹ (explicit byte permutation; round-trip by refl).
------------------------------------------------------------------------
InvShiftRows : State → State
InvShiftRows ((b00 ∷ b01 ∷ b02 ∷ b03 ∷ []) ∷ (b10 ∷ b11 ∷ b12 ∷ b13 ∷ [])
            ∷ (b20 ∷ b21 ∷ b22 ∷ b23 ∷ []) ∷ (b30 ∷ b31 ∷ b32 ∷ b33 ∷ []) ∷ []) =
   (b00 ∷ b31 ∷ b22 ∷ b13 ∷ []) ∷ (b10 ∷ b01 ∷ b32 ∷ b23 ∷ [])
 ∷ (b20 ∷ b11 ∷ b02 ∷ b33 ∷ []) ∷ (b30 ∷ b21 ∷ b12 ∷ b03 ∷ []) ∷ []
shift-rt : (s : State) → InvShiftRows (ShiftRows s) ≡ s
shift-rt ((b00 ∷ b01 ∷ b02 ∷ b03 ∷ []) ∷ (b10 ∷ b11 ∷ b12 ∷ b13 ∷ [])
        ∷ (b20 ∷ b21 ∷ b22 ∷ b23 ∷ []) ∷ (b30 ∷ b31 ∷ b32 ∷ b33 ∷ []) ∷ []) = refl

------------------------------------------------------------------------
-- THE INVERSE ROUND + per-round round-trip.
------------------------------------------------------------------------
inv-round : State → State → State
inv-round k t = InvSubBytes (InvShiftRows (InvMixColumns (addKey k t)))

opaque
  unfolding round
  round-rt : (k s : State) → inv-round k (round k s) ≡ s
  round-rt k s =
    trans (cong (λ x → InvSubBytes (InvShiftRows (InvMixColumns x)))
                (add-rt k (MixColumns (ShiftRows (SubBytes s)))))
    (trans (cong (λ x → InvSubBytes (InvShiftRows x)) (mix-rt (ShiftRows (SubBytes s))))
    (trans (cong InvSubBytes (shift-rt (SubBytes s)))
           (sub-rt s)))

inv-final-round : State → State → State
inv-final-round k t = InvSubBytes (InvShiftRows (addKey k t))

opaque
  unfolding final-round
  final-round-rt : (k s : State) → inv-final-round k (final-round k s) ≡ s
  final-round-rt k s =
    trans (cong (λ x → InvSubBytes (InvShiftRows x)) (add-rt k (ShiftRows (SubBytes s))))
    (trans (cong InvSubBytes (shift-rt (SubBytes s)))
           (sub-rt s))
