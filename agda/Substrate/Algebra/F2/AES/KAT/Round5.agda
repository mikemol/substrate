{-# OPTIONS --safe #-}
-- Round 5 pin (INDEPENDENT): one round on the concrete prior state S4 (the handoff)
-- under the concrete key M4 → S5. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round5 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r5 : round M4 S4 ≡ S5
r5 = refl
