{-# OPTIONS --safe --without-K #-}
-- Round 9 pin (INDEPENDENT): one round on the concrete prior state S8 (the handoff)
-- under the concrete key M8 → S9. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round9 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r9 : round M8 S8 ≡ S9
r9 = refl
