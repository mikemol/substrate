{-# OPTIONS --safe #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KAT.KeyPins
--
-- One-step key-schedule pins: each `nextRoundKey rcᵢ kᵢ₋₁ ≡ kᵢ` on a CONCRETE prior
-- round key (KAT.Trace). Each is one step (cheap, ~2 s) — NOT the deep fold (which is
-- exponential to force). KAT.Full's parameterized module threads these abstractly into
-- `rkmid`/`rk10`, so the schedule is never forced as a chain.
------------------------------------------------------------------------
module Substrate.Algebra.F2.AES.KAT.KeyPins where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.KeySchedule
  using (nextRoundKey; rc1; rc2; rc3; rc4; rc5; rc6; rc7; rc8; rc9; rc10)
open import Substrate.Algebra.F2.AES.KAT using (to-state; key-C1)
open import Substrate.Algebra.F2.AES.KAT.Trace

KP1  : nextRoundKey rc1  (to-state key-C1) ≡ M0 ;  KP1  = refl
KP2  : nextRoundKey rc2  M0 ≡ M1 ;  KP2  = refl
KP3  : nextRoundKey rc3  M1 ≡ M2 ;  KP3  = refl
KP4  : nextRoundKey rc4  M2 ≡ M3 ;  KP4  = refl
KP5  : nextRoundKey rc5  M3 ≡ M4 ;  KP5  = refl
KP6  : nextRoundKey rc6  M4 ≡ M5 ;  KP6  = refl
KP7  : nextRoundKey rc7  M5 ≡ M6 ;  KP7  = refl
KP8  : nextRoundKey rc8  M6 ≡ M7 ;  KP8  = refl
KP9  : nextRoundKey rc9  M7 ≡ M8 ;  KP9  = refl
KP10 : nextRoundKey rc10 M8 ≡ K10 ; KP10 = refl
