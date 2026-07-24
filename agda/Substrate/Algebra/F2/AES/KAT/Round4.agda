{-# OPTIONS --safe --without-K #-}
-- Round 4 pin (INDEPENDENT): one round on the concrete prior state S3 (the handoff)
-- under the concrete key M3 → S4. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round4 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r4 : round M3 S3 ≡ S4
r4 = refl
