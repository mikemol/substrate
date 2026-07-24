{-# OPTIONS --safe --without-K #-}
-- Sharded round-fold, rounds 4..6: fold round [k4,k5,k6] s3 ≡ s6, sealed opaque.
module Substrate.Algebra.F2.AES.KAT.FullFcShardB where

open import Substrate.Foundation.Eq using (_≡_; trans; cong)
open import Substrate.Foundation.Vec using (_∷_; [])
open import Substrate.Algebra.F2.AES.Round using (State; round)
open import Substrate.Algebra.F2.AES.Cipher using (fold)
open import Substrate.Algebra.F2.AES.KAT.Trace using (S3; S4; S5; S6; M3; M4; M5)
open import Substrate.Algebra.F2.AES.KAT.Round4 using (r4)
open import Substrate.Algebra.F2.AES.KAT.Round5 using (r5)
open import Substrate.Algebra.F2.AES.KAT.Round6 using (r6)

module AssembleFcB
  (s3 s4 s5 s6 k4 k5 k6 : State)
  (e4 : round k4 s3 ≡ s4) (e5 : round k5 s4 ≡ s5) (e6 : round k6 s5 ≡ s6)
  where
  fcB : fold round (k4 ∷ k5 ∷ k6 ∷ []) s3 ≡ s6
  fcB = trans (cong (fold round (k5 ∷ k6 ∷ [])) e4)
        (trans (cong (fold round (k6 ∷ [])) e5)
               (cong (fold round []) e6))

open AssembleFcB S3 S4 S5 S6 M3 M4 M5 r4 r5 r6 using (fcB)

opaque
  fcB-C : fold round (M3 ∷ M4 ∷ M5 ∷ []) S3 ≡ S6
  fcB-C = fcB
