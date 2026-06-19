{-# OPTIONS --safe #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KAT.Full
--
-- THE FULL-ENCRYPT KNOWN-ANSWER TEST, FIPS-197 Appendix C.1 — the master-key form:
--   encrypt-key (to-state key-C1) (to-state pt-C1) ≡ to-state ct-C1   (encrypt-kat-C1)
--
-- The single-≡ statement WHNF-cascades two deep chains (the 10-round composition AND
-- the key-schedule word recursion) → blowup (> 30 min, > 5.6 GB / OOM at 8 GB). Both
-- are dissolved by the parameterized-module pattern (cf. Algebra.F2.MixColumns.Proof.G):
-- the proof is assembled inside `Assemble`, ABSTRACT over every key/state, where
-- `round`/`fold`/`nextRoundKey` are stuck (neutral) on the abstract arguments — so NO
-- composition and NO schedule chain is ever normalised. The concrete one-step pins
-- (KAT.KeyPins for the schedule, KAT.Round1…Round9 for the rounds, KAT.Pre, fin) are
-- supplied at instantiation. Crucially the instantiation is by `open` (NOT a
-- type-annotated re-declaration), so the substituted type transits the module boundary
-- WITHOUT a conversion check — Agda never re-normalises the composition. ~seconds, --safe.
--
-- Every step is still verified by `refl`: each key-schedule step (KeyPins), each round
-- (RoundN), the pre-whiten (Pre) and final round (fin) — the module only threads them.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KAT.Full where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂)
open import Substrate.Foundation.Vec using (_∷_; [])
open import Substrate.Algebra.F2.AES.Round using (State; round; final-round; addKey)
open import Substrate.Algebra.F2.AES.Cipher using (fold)
open import Substrate.Algebra.F2.AES.KeySchedule
  using (encrypt-key; nextRoundKey; rkmid; rk10; rc1; rc2; rc3; rc4; rc5; rc6; rc7; rc8; rc9; rc10)
open import Substrate.Algebra.F2.AES.KAT using (to-state; key-C1)
open import Substrate.Algebra.F2.AES.KAT.Trace
open import Substrate.Algebra.F2.AES.KAT.Pre using (pre)
open import Substrate.Algebra.F2.AES.KAT.KeyPins
open import Substrate.Algebra.F2.AES.KAT.Round1 using (r1)
open import Substrate.Algebra.F2.AES.KAT.Round2 using (r2)
open import Substrate.Algebra.F2.AES.KAT.Round3 using (r3)
open import Substrate.Algebra.F2.AES.KAT.Round4 using (r4)
open import Substrate.Algebra.F2.AES.KAT.Round5 using (r5)
open import Substrate.Algebra.F2.AES.KAT.Round6 using (r6)
open import Substrate.Algebra.F2.AES.KAT.Round7 using (r7)
open import Substrate.Algebra.F2.AES.KAT.Round8 using (r8)
open import Substrate.Algebra.F2.AES.KAT.Round9 using (r9)

fin : final-round K10 S9 ≡ Sct
fin = refl

-- The whole proof, ABSTRACT over master key / round keys / states — every round, fold
-- and nextRoundKey is neutral here, so nothing is forced. Threads the supplied pins.
module Assemble
  (mk spt sct s0 s1 s2 s3 s4 s5 s6 s7 s8 s9 k1 k2 k3 k4 k5 k6 k7 k8 k9 k10 : State)
  -- key-schedule step pins (kᵢ = nextRoundKey rcᵢ kᵢ₋₁, k₀ = mk):
  (kp1 : nextRoundKey rc1 mk ≡ k1) (kp2 : nextRoundKey rc2 k1 ≡ k2)
  (kp3 : nextRoundKey rc3 k2 ≡ k3) (kp4 : nextRoundKey rc4 k3 ≡ k4)
  (kp5 : nextRoundKey rc5 k4 ≡ k5) (kp6 : nextRoundKey rc6 k5 ≡ k6)
  (kp7 : nextRoundKey rc7 k6 ≡ k7) (kp8 : nextRoundKey rc8 k7 ≡ k8)
  (kp9 : nextRoundKey rc9 k8 ≡ k9) (kp10 : nextRoundKey rc10 k9 ≡ k10)
  -- pre-whiten + the 9 middle rounds + the final round:
  (p  : addKey mk spt ≡ s0)
  (e1 : round k1 s0 ≡ s1) (e2 : round k2 s1 ≡ s2) (e3 : round k3 s2 ≡ s3)
  (e4 : round k4 s3 ≡ s4) (e5 : round k5 s4 ≡ s5) (e6 : round k6 s5 ≡ s6)
  (e7 : round k7 s6 ≡ s7) (e8 : round k8 s7 ≡ s8) (e9 : round k9 s8 ≡ s9)
  (f  : final-round k10 s9 ≡ sct)
  where
  ms : _
  ms = k1 ∷ k2 ∷ k3 ∷ k4 ∷ k5 ∷ k6 ∷ k7 ∷ k8 ∷ k9 ∷ []

  -- key schedule: the real rkmid/rk10 of mk equal the concrete round keys (neutral chain).
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
  rkmid-eq : rkmid mk ≡ ms
  rkmid-eq = cong₂ _∷_ ck1 (cong₂ _∷_ ck2 (cong₂ _∷_ ck3 (cong₂ _∷_ ck4
             (cong₂ _∷_ ck5 (cong₂ _∷_ ck6 (cong₂ _∷_ ck7 (cong₂ _∷_ ck8
             (cong₂ _∷_ ck9 refl))))))))
  rk10-eq : rk10 mk ≡ k10
  rk10-eq = ck10

  -- rounds: the 9-key fold lands on s9 (neutral chain over the round pins).
  fc : fold round ms s0 ≡ s9
  fc = trans (cong (fold round (k2 ∷ k3 ∷ k4 ∷ k5 ∷ k6 ∷ k7 ∷ k8 ∷ k9 ∷ [])) e1)
       (trans (cong (fold round (k3 ∷ k4 ∷ k5 ∷ k6 ∷ k7 ∷ k8 ∷ k9 ∷ [])) e2)
       (trans (cong (fold round (k4 ∷ k5 ∷ k6 ∷ k7 ∷ k8 ∷ k9 ∷ [])) e3)
       (trans (cong (fold round (k5 ∷ k6 ∷ k7 ∷ k8 ∷ k9 ∷ [])) e4)
       (trans (cong (fold round (k6 ∷ k7 ∷ k8 ∷ k9 ∷ [])) e5)
       (trans (cong (fold round (k7 ∷ k8 ∷ k9 ∷ [])) e6)
       (trans (cong (fold round (k8 ∷ k9 ∷ [])) e7)
       (trans (cong (fold round (k9 ∷ [])) e8)
              (cong (fold round []) e9))))))))

  -- encrypt-key mk spt ≡def final-round (rk10 mk) (fold round (rkmid mk) (addKey mk spt)).
  kat : encrypt-key mk spt ≡ sct
  kat = trans (cong₂ (λ k m → final-round k (fold round m (addKey mk spt))) rk10-eq rkmid-eq)
        (trans (cong (λ x → final-round k10 (fold round ms x)) p)
        (trans (cong (final-round k10) fc) f))

-- instantiate by OPENING (no re-declaration ⇒ no conversion ⇒ no composition WHNF).
open Assemble (to-state key-C1) Spt Sct S0 S1 S2 S3 S4 S5 S6 S7 S8 S9
              M0 M1 M2 M3 M4 M5 M6 M7 M8 K10
              KP1 KP2 KP3 KP4 KP5 KP6 KP7 KP8 KP9 KP10
              pre r1 r2 r3 r4 r5 r6 r7 r8 r9 fin
  public renaming (kat to encrypt-kat-C1)
