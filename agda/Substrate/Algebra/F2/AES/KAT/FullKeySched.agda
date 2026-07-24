{-# OPTIONS --safe --without-K #-}
-- PROBE: the AES key-schedule chain (rkmid-eq/rk10-eq) sealed in its own module,
-- to measure whether it fits <128 post-schedule-seal (Full-direct-shard path).
module Substrate.Algebra.F2.AES.KAT.FullKeySched where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂)
open import Substrate.Foundation.Vec using (Vec; _∷_; [])
open import Substrate.Algebra.F2.AES.Round using (State)
open import Substrate.Algebra.F2.AES.KeySchedule
  using (nextRoundKey; rkmid; rk10; rc1; rc2; rc3; rc4; rc5; rc6; rc7; rc8; rc9; rc10)
open import Substrate.Algebra.F2.AES.KAT using (to-state; key-C1)
open import Substrate.Algebra.F2.AES.KAT.Trace using (M0; M1; M2; M3; M4; M5; M6; M7; M8; K10)
open import Substrate.Algebra.F2.AES.KAT.KeyPins

module AssembleK
  (mk k1 k2 k3 k4 k5 k6 k7 k8 k9 k10 : State)
  (kp1 : nextRoundKey rc1 mk ≡ k1) (kp2 : nextRoundKey rc2 k1 ≡ k2)
  (kp3 : nextRoundKey rc3 k2 ≡ k3) (kp4 : nextRoundKey rc4 k3 ≡ k4)
  (kp5 : nextRoundKey rc5 k4 ≡ k5) (kp6 : nextRoundKey rc6 k5 ≡ k6)
  (kp7 : nextRoundKey rc7 k6 ≡ k7) (kp8 : nextRoundKey rc8 k7 ≡ k8)
  (kp9 : nextRoundKey rc9 k8 ≡ k9) (kp10 : nextRoundKey rc10 k9 ≡ k10)
  where
  ck1 = kp1
  ck2 = trans (cong (nextRoundKey rc2)  ck1) kp2
  ck3 = trans (cong (nextRoundKey rc3)  ck2) kp3
  ck4 = trans (cong (nextRoundKey rc4)  ck3) kp4
  ck5 = trans (cong (nextRoundKey rc5)  ck4) kp5
  ck6 = trans (cong (nextRoundKey rc6)  ck5) kp6
  ck7 = trans (cong (nextRoundKey rc7)  ck6) kp7
  ck8 = trans (cong (nextRoundKey rc8)  ck7) kp8
  ck9 = trans (cong (nextRoundKey rc9)  ck8) kp9
  ck10 = trans (cong (nextRoundKey rc10) ck9) kp10
  ms : Vec State 9
  ms = k1 ∷ k2 ∷ k3 ∷ k4 ∷ k5 ∷ k6 ∷ k7 ∷ k8 ∷ k9 ∷ []
  rkmid-eq : rkmid mk ≡ ms
  rkmid-eq = cong₂ _∷_ ck1 (cong₂ _∷_ ck2 (cong₂ _∷_ ck3 (cong₂ _∷_ ck4
             (cong₂ _∷_ ck5 (cong₂ _∷_ ck6 (cong₂ _∷_ ck7 (cong₂ _∷_ ck8
             (cong₂ _∷_ ck9 refl))))))))
  rk10-eq : rk10 mk ≡ k10
  rk10-eq = ck10

open AssembleK (to-state key-C1) M0 M1 M2 M3 M4 M5 M6 M7 M8 K10
               KP1 KP2 KP3 KP4 KP5 KP6 KP7 KP8 KP9 KP10 using (rkmid-eq; rk10-eq; ms)

opaque
  rkmid-eq-C : rkmid (to-state key-C1) ≡ ms
  rkmid-eq-C = rkmid-eq
  rk10-eq-C : rk10 (to-state key-C1) ≡ K10
  rk10-eq-C = rk10-eq
