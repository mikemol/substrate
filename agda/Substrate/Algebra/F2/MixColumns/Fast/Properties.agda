{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.MixColumns.Fast.Properties  (PROOF half)
--
-- Certifies the cheap `MixColumns.Fast.mix-fast` (table ⊕ XOR) against the
-- abstract `mix` (Proof, generic `gmul`): the coefficient bridges
--   xtime-tab a ≡ gmul c02 a,  xtime-tab a ⊕ a ≡ gmul c03 a,  a ≡ gmul c01 a
-- give `mix-fast≡mix`, hence the decrypt round-trip `mix-fast-round-trip`.
-- Importing THIS module deserializes GF256's `gmul` + MixColumns.Proof; the
-- forward path (MixColumns.Fast) does not. The algebra is preserved here.
------------------------------------------------------------------------

module Substrate.Algebra.F2.MixColumns.Fast.Properties where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_)
open import Substrate.Algebra.F2.GF256 using (gmul; gmul-comm; gmul-identityˡ)
open import Substrate.Algebra.F2.MixColumns.Base using (c01; c02; c03)
open import Substrate.Algebra.F2.MixColumns.Scale using (gmul-c02; gmul-c03)
open import Substrate.Algebra.F2.MixColumns.Proof using (mix; inv; mixcolumns-round-trip)
open import Substrate.Algebra.F2.GF256.XtimeTable using (xtime-tab; xtime-tab≡xtime)
open import Substrate.Algebra.F2.MixColumns.Fast using (mix-fast)

-- the three coefficient bridges (xtime-tab form ≡ the gmul product `mix` uses).
xt-c02 : (a : Vector 8) → xtime-tab a ≡ gmul c02 a
xt-c02 a = trans (xtime-tab≡xtime a) (sym (trans (gmul-comm c02 a) (gmul-c02 a)))

xt-c03 : (a : Vector 8) → (xtime-tab a +ⱽ a) ≡ gmul c03 a
xt-c03 a = trans (cong (_+ⱽ a) (xtime-tab≡xtime a))
                 (sym (trans (gmul-comm c03 a) (gmul-c03 a)))

id-c01 : (a : Vector 8) → a ≡ gmul c01 a
id-c01 a = sym (gmul-identityˡ a)

-- mix-fast ≡ mix, per column entry (each a slot-by-slot cong₂ over the bridges).
mix-fast≡mix : (col : Vec (Vector 8) 4) → mix-fast col ≡ mix col
mix-fast≡mix (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
  cong₂ _∷_ (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (xt-c02 a0) (xt-c03 a1)) (cong₂ _+ⱽ_ (id-c01 a2) (id-c01 a3)))
  (cong₂ _∷_ (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (id-c01 a0) (xt-c02 a1)) (cong₂ _+ⱽ_ (xt-c03 a2) (id-c01 a3)))
  (cong₂ _∷_ (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (id-c01 a0) (id-c01 a1)) (cong₂ _+ⱽ_ (xt-c02 a2) (xt-c03 a3)))
  (cong₂ _∷_ (cong₂ _+ⱽ_ (cong₂ _+ⱽ_ (xt-c03 a0) (id-c01 a1)) (cong₂ _+ⱽ_ (id-c01 a2) (xt-c02 a3)))
  refl)))

-- the round-trip for the cheap mix, via the equality + the abstract round-trip.
mix-fast-round-trip : (col : Vec (Vector 8) 4) → inv (mix-fast col) ≡ col
mix-fast-round-trip col = trans (cong inv (mix-fast≡mix col)) (mixcolumns-round-trip col)
