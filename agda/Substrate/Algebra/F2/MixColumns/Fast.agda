{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.MixColumns.Fast
--
-- The evaluation-CHEAP forward MixColumns, routed through the proved `xtime`
-- TABLE (GF256.XtimeTable) — the `bd17a98` move for the diffusion layer. The
-- abstract `mix` (Proof) computes each column entry as `dot4` of GENERIC `gmul`
-- products; forcing those over a ten-round encrypt is memory-heavy. Here `mix-fast`
-- computes the SAME column via the already-proven coefficient reductions
--   gmul · c02 ≡ xtime,   gmul · c03 ≡ xtime ⊕ id,   gmul · c01 ≡ id   (Scale)
-- with `xtime` itself the cheap table lookup `xtime-tab`. `mix-fast≡mix` proves
-- they agree, so the cipher can FORCE through the table while every existing
-- theorem (round-trip, FIPS pinning) is preserved — the table IS the verified
-- MixColumns, exactly as the SBOX/XTIME tables ARE the verified S-box/·x.
------------------------------------------------------------------------

module Substrate.Algebra.F2.MixColumns.Fast where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_)
open import Substrate.Algebra.F2.GF256 using (gmul; gmul-comm; gmul-identityˡ; xtime)
open import Substrate.Algebra.F2.MixColumns.Base using (c01; c02; c03)
open import Substrate.Algebra.F2.MixColumns.Scale using (gmul-c02; gmul-c03)
open import Substrate.Algebra.F2.MixColumns.Proof using (mix; inv; mixcolumns-round-trip)
open import Substrate.Algebra.F2.GF256.XtimeTable using (xtime-tab; xtime-tab≡xtime)

-- the three coefficient bridges (xtime-tab form ≡ the gmul product `mix` uses).
xt-c02 : (a : Vector 8) → xtime-tab a ≡ gmul c02 a
xt-c02 a = trans (xtime-tab≡xtime a) (sym (trans (gmul-comm c02 a) (gmul-c02 a)))

xt-c03 : (a : Vector 8) → (xtime-tab a +ⱽ a) ≡ gmul c03 a
xt-c03 a = trans (cong (_+ⱽ a) (xtime-tab≡xtime a))
                 (sym (trans (gmul-comm c03 a) (gmul-c03 a)))

id-c01 : (a : Vector 8) → a ≡ gmul c01 a
id-c01 a = sym (gmul-identityˡ a)

-- the cheap forward mix: same column outputs, computed via xtime-tab (a lookup) ⊕.
-- grouping matches `dot4 _ _ _ _` = (slot₀ ⊕ slot₁) ⊕ (slot₂ ⊕ slot₃).
mix-fast : Vec (Vector 8) 4 → Vec (Vector 8) 4
mix-fast (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
  ((xtime-tab a0 +ⱽ (xtime-tab a1 +ⱽ a1)) +ⱽ (a2 +ⱽ a3)) ∷            -- 02 03 01 01
  ((a0 +ⱽ xtime-tab a1) +ⱽ ((xtime-tab a2 +ⱽ a2) +ⱽ a3)) ∷            -- 01 02 03 01
  ((a0 +ⱽ a1) +ⱽ (xtime-tab a2 +ⱽ (xtime-tab a3 +ⱽ a3))) ∷            -- 01 01 02 03
  (((xtime-tab a0 +ⱽ a0) +ⱽ a1) +ⱽ (a2 +ⱽ xtime-tab a3)) ∷ []          -- 03 01 01 02

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
