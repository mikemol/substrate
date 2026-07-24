{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KAT.Full
--
-- THE FULL-ENCRYPT KNOWN-ANSWER TEST, FIPS-197 Appendix C.1 — the master-key form:
--   encrypt-key (to-state key-C1) (to-state pt-C1) ≡ to-state ct-C1   (encrypt-kat-C1)
--
-- SHARDED. The single-≡ statement WHNF-cascades two deep chains (the 10-round
-- composition AND the key-schedule word recursion) → blowup. The abstract-module +
-- opaque-op pattern (cap128-schedule-seal) keeps every `round`/`fold`/`nextRoundKey`
-- neutral, and the ⟡il-shard lever SHARDS the two chains across modules so NO single
-- module elaborates the deep fold or the deep schedule nest:
--   * FullKeySched      — the key schedule `rkmid mk ≡ ms` / `rk10 mk ≡ k10`, sealed.
--   * FullFcShard{A,B,C} — the 9-round fold split into three `fold round [3 keys] p ≡ q`
--                          midpoints, each sealed opaque.
--   * FullShardCore.fold-++ — the composition primitive that stitches them.
-- This module is the thin AGGREGATOR: it imports only the sealed shard-handles + the
-- boundary pins (Pre, RoundFin), composes the round-fold via `fold-++`, and assembles
-- the FIPS statement. Every module (this + the shards) is <128 MB; every step is still
-- verified by `refl` (KeyPins / RoundN / Pre / fin), just sharded. --safe --without-K.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KAT.Full where

open import Substrate.Foundation.Eq using (_≡_; trans; cong; cong₂)
open import Substrate.Foundation.Vec using (Vec; _∷_; []; _++_)
open import Substrate.Algebra.F2.AES.Round using (State; round; final-round; addKey)
open import Substrate.Algebra.F2.AES.Cipher using (fold)
open import Substrate.Algebra.F2.AES.KeySchedule using (encrypt-key)
open import Substrate.Algebra.F2.AES.KAT using (to-state; key-C1)
open import Substrate.Algebra.F2.AES.KAT.Trace using (Spt; Sct; S0; S3; S6; S9; K10; M0; M1; M2; M3; M4; M5; M6; M7; M8)
open import Substrate.Algebra.F2.AES.KAT.Pre using (pre)
open import Substrate.Algebra.F2.AES.KAT.RoundFin using (fin)
open import Substrate.Algebra.F2.AES.KAT.FullShardCore using (fold-++)
open import Substrate.Algebra.F2.AES.KAT.FullKeySched using (rkmid-eq-C; rk10-eq-C)
open import Substrate.Algebra.F2.AES.KAT.FullFcShardA using (fcA-C)
open import Substrate.Algebra.F2.AES.KAT.FullFcShardB using (fcB-C)
open import Substrate.Algebra.F2.AES.KAT.FullFcShardC using (fcC-C)

mk : State
mk = to-state key-C1

msA msB msC : Vec State 3
msA = M0 ∷ M1 ∷ M2 ∷ []
msB = M3 ∷ M4 ∷ M5 ∷ []
msC = M6 ∷ M7 ∷ M8 ∷ []

ms : Vec State 9
ms = M0 ∷ M1 ∷ M2 ∷ M3 ∷ M4 ∷ M5 ∷ M6 ∷ M7 ∷ M8 ∷ []

-- the deep round-fold, composed from the three sealed shard-midpoints (fold-++).
fc : fold round ms S0 ≡ S9
fc = trans (fold-++ round msA (msB ++ msC) S0)
     (trans (cong (fold round (msB ++ msC)) fcA-C)
     (trans (fold-++ round msB msC S3)
     (trans (cong (fold round msC) fcB-C)
            fcC-C)))

-- encrypt-key mk spt ≡def final-round (rk10 mk) (fold round (rkmid mk) (addKey mk spt)).
encrypt-kat-C1 : encrypt-key mk Spt ≡ Sct
encrypt-kat-C1 =
  trans (cong₂ (λ k m → final-round k (fold round m (addKey mk Spt))) rk10-eq-C rkmid-eq-C)
  (trans (cong (λ x → final-round K10 (fold round ms x)) pre)
  (trans (cong (final-round K10) fc) fin))
