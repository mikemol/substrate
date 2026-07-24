{-# OPTIONS --safe --without-K #-}
-- Round 1 pin (INDEPENDENT): one round on the concrete prior state S0 (the handoff)
-- under the concrete key M0 → S1. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round1 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r1 : round M0 S0 ≡ S1
r1 = refl
