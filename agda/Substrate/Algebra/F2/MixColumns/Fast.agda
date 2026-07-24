{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.MixColumns.Fast  (lean / DEF half)
--
-- The evaluation-CHEAP forward MixColumns `mix-fast`, computed through the
-- proved `xtime` TABLE (GF256.XtimeTable) — a lookup ⊕ XOR, GF-ring-FREE. The
-- abstract `mix` (Proof, via generic `gmul`) is memory-heavy to force over a
-- ten-round encrypt; this computes the SAME columns cheaply. The certification
-- that `mix-fast ≡ mix` (via the coefficient bridges) and the decrypt
-- round-trip live in `MixColumns.Fast.Properties` — so the forward cipher path
-- (this module) never deserializes GF256's `gmul` / MixColumns.Proof.
------------------------------------------------------------------------

module Substrate.Algebra.F2.MixColumns.Fast where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_)
open import Substrate.Algebra.F2.GF256.XtimeTable using (xtime-tab)

-- the cheap forward mix: same column outputs, computed via xtime-tab (a lookup) ⊕.
-- grouping matches `dot4 _ _ _ _` = (slot₀ ⊕ slot₁) ⊕ (slot₂ ⊕ slot₃).
mix-fast : Vec (Vector 8) 4 → Vec (Vector 8) 4
mix-fast (a0 ∷ a1 ∷ a2 ∷ a3 ∷ []) =
  ((xtime-tab a0 +ⱽ (xtime-tab a1 +ⱽ a1)) +ⱽ (a2 +ⱽ a3)) ∷            -- 02 03 01 01
  ((a0 +ⱽ xtime-tab a1) +ⱽ ((xtime-tab a2 +ⱽ a2) +ⱽ a3)) ∷            -- 01 02 03 01
  ((a0 +ⱽ a1) +ⱽ (xtime-tab a2 +ⱽ (xtime-tab a3 +ⱽ a3))) ∷            -- 01 01 02 03
  (((xtime-tab a0 +ⱽ a0) +ⱽ a1) +ⱽ (a2 +ⱽ xtime-tab a3)) ∷ []          -- 03 01 01 02
