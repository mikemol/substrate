{-# OPTIONS --safe #-}
-- Round 6 pin (INDEPENDENT): one round on the concrete prior state S5 (the handoff)
-- under the concrete key M5 → S6. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round6 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r6 : round M5 S5 ≡ S6
r6 = refl
