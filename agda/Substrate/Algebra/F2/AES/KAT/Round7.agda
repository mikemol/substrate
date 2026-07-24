{-# OPTIONS --safe --without-K #-}
-- Round 7 pin (INDEPENDENT): one round on the concrete prior state S6 (the handoff)
-- under the concrete key M6 → S7. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round7 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
opaque
  unfolding round
  r7 : round M6 S6 ≡ S7
  r7 = refl
