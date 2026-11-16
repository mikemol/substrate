------------------------------------------------------------------------
-- Substrate.WitnessTower.CodewordCountTies.ResRoundtrip
--
-- Defines: res-roundtrip
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.CodewordCountTies; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CodewordCountTies.ResRoundtrip where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Vec
open import Substrate.Cocycles.V4Signature.Codeword.IsReserved
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Foundation.Nat.Plus
open import Substrate.WitnessTower.CodewordCountTies.ResTovec3
open import Substrate.WitnessTower.CodewordCountTies.Vec3Tores
open import Substrate.Foundation.Product



-- with the proof components handled, the OTHER roundtrip closes: matching on
-- the IsReserved proofs (p3 : b3 ≡ false, p4 : b4 ≡ false) specialises the bits
-- to false, so the reconstruction is exact. Hence res→vec3 is surjective and
-- Reserved ≅ Vec Bool 3 is a FULL bijection ⟹ |Reserved| is EXACTLY 8.
res-roundtrip : (r : Reserved) → vec3→res (res→vec3 r) ≡ r
res-roundtrip ((b0 , b1 , b2 , b3 , b4) , (p3 , p4)) = reconstruct b3 b4 p3 p4
  where
    reconstruct : (b3 b4 : Bool) (p3 : b3 ≡ false) (p4 : b4 ≡ false) →
                  ((b0 , b1 , b2 , false , false) , (refl , refl))
                  ≡ ((b0 , b1 , b2 , b3 , b4) , (p3 , p4))
    reconstruct .false .false refl refl = refl
