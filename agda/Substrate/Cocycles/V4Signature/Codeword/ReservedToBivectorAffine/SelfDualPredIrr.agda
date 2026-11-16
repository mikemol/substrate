------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.SelfDualPredIrr
--
-- Proof-irrelevance for SelfDual-Pred via Hedberg's theorem
-- (decidable Bivector equality → UIP).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivectorAffine.SelfDualPredIrr where

open import Substrate.Foundation.Vec.Properties.EqDec
open import Substrate.Foundation.Hedberg.DecidableEquality
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.Algebra.F2.Dec
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual using (SelfDual-Pred)
open import Substrate.Foundation.Eq

bivector-≟ : DecidableEquality Bivector
bivector-≟ = ≡-dec _≟_

bivector-uip : {x y : Bivector} (p q : x ≡ y) → p ≡ q
bivector-uip = Decidable⇒UIP bivector-≟

selfdual-pred-irr :
  (ω : Bivector) → (p q : SelfDual-Pred ω) → p ≡ q
selfdual-pred-irr _ = bivector-uip
