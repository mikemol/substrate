{-# OPTIONS --safe --without-K #-}
-- Sharded round-fold, rounds 1..3: fold round [k1,k2,k3] s0 ≡ s3, sealed opaque.
module Substrate.Algebra.F2.AES.KAT.FullFcShardA where

open import Substrate.Foundation.Eq using (_≡_; trans; cong)
open import Substrate.Foundation.Vec using (_∷_; [])
open import Substrate.Algebra.F2.AES.Round using (State; round)
open import Substrate.Algebra.F2.AES.Cipher using (fold)
open import Substrate.Algebra.F2.AES.KAT.Trace using (S0; S1; S2; S3; M0; M1; M2)
open import Substrate.Algebra.F2.AES.KAT.Round1 using (r1)
open import Substrate.Algebra.F2.AES.KAT.Round2 using (r2)
open import Substrate.Algebra.F2.AES.KAT.Round3 using (r3)

module AssembleFcA
  (s0 s1 s2 s3 k1 k2 k3 : State)
  (e1 : round k1 s0 ≡ s1) (e2 : round k2 s1 ≡ s2) (e3 : round k3 s2 ≡ s3)
  where
  fcA : fold round (k1 ∷ k2 ∷ k3 ∷ []) s0 ≡ s3
  fcA = trans (cong (fold round (k2 ∷ k3 ∷ [])) e1)
        (trans (cong (fold round (k3 ∷ [])) e2)
               (cong (fold round []) e3))

open AssembleFcA S0 S1 S2 S3 M0 M1 M2 r1 r2 r3 using (fcA)

opaque
  fcA-C : fold round (M0 ∷ M1 ∷ M2 ∷ []) S0 ≡ S3
  fcA-C = fcA
