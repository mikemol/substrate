{-# OPTIONS --safe --without-K #-}
-- Round 8 pin (INDEPENDENT): one round on the concrete prior state S7 (the handoff)
-- under the concrete key M7 → S8. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round8 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r8 : round M7 S7 ≡ S8
r8 = refl
