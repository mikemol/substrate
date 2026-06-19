{-# OPTIONS --safe #-}
-- Round 2 pin (INDEPENDENT): one round on the concrete prior state S1 (the handoff)
-- under the concrete key M1 → S2. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round2 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r2 : round M1 S1 ≡ S2
r2 = refl
