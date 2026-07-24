{-# OPTIONS --safe --without-K #-}
-- Sharded round-fold, rounds 7..9: fold round [k7,k8,k9] s6 ≡ s9, sealed opaque.
module Substrate.Algebra.F2.AES.KAT.FullFcShardC where

open import Substrate.Foundation.Eq using (_≡_; trans; cong)
open import Substrate.Foundation.Vec using (_∷_; [])
open import Substrate.Algebra.F2.AES.Round using (State; round)
open import Substrate.Algebra.F2.AES.Cipher using (fold)
open import Substrate.Algebra.F2.AES.KAT.Trace using (S6; S7; S8; S9; M6; M7; M8)
open import Substrate.Algebra.F2.AES.KAT.Round7 using (r7)
open import Substrate.Algebra.F2.AES.KAT.Round8 using (r8)
open import Substrate.Algebra.F2.AES.KAT.Round9 using (r9)

module AssembleFcC
  (s6 s7 s8 s9 k7 k8 k9 : State)
  (e7 : round k7 s6 ≡ s7) (e8 : round k8 s7 ≡ s8) (e9 : round k9 s8 ≡ s9)
  where
  fcC : fold round (k7 ∷ k8 ∷ k9 ∷ []) s6 ≡ s9
  fcC = trans (cong (fold round (k8 ∷ k9 ∷ [])) e7)
        (trans (cong (fold round (k9 ∷ [])) e8)
               (cong (fold round []) e9))

open AssembleFcC S6 S7 S8 S9 M6 M7 M8 r7 r8 r9 using (fcC)

opaque
  fcC-C : fold round (M6 ∷ M7 ∷ M8 ∷ []) S6 ≡ S9
  fcC-C = fcC
