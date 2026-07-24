{-# OPTIONS --safe --without-K #-}
-- Round 3 pin (INDEPENDENT): one round on the concrete prior state S2 (the handoff)
-- under the concrete key M2 → S3. Constant cost (~3 s); no X-composition to carry
-- residue. KAT.Full recomposes these via fold-chain9 without re-forcing any round.
module Substrate.Algebra.F2.AES.KAT.Round3 where
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (round)
open import Substrate.Algebra.F2.AES.KAT.Trace
r3 : round M2 S2 ≡ S3
r3 = refl
