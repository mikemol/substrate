{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CFBezoutBridge.Properties — THE BRIDGE: Minv(q) acting
-- on (s', t') is EXACTLY step-bezout's coefficient update (t', s' − t'·q). Split from
-- CFBezoutBridge per def/proof separation (the Z.Properties* imports live here).
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CFBezoutBridge.Properties where
open import Substrate.Algebra.Z.Add
open import Substrate.Algebra.Z.Sub
open import Substrate.Algebra.Z.Mul

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.OneInt
open import Substrate.Algebra.Z.ZeroInt

open import Substrate.Algebra.Z.Properties.MulFull using (*ℤ-identityˡ; *ℤ-zeroˡ)
open import Substrate.Algebra.Z.Properties.Add using (+ℤ-identityˡ)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left; *ℤ-comm)
open import Substrate.Algebra.R.Trace.CFBezoutBridge
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Trans

bezout-step-is-Minv :
  (q : ℕ) (s' t' : ℤ) →
  act (Minv q) (s' , t') ≡ (t' , (s' -ℤ (t' *ℤ (+ q))))
bezout-step-is-Minv q s' t' = cong₂ _,_ comp₁ comp₂
  where
    -- component 1: (0·s') + (1·t') = 0 + t' = t'
    comp₁ : ((0ℤ *ℤ s') +ℤ (1ℤ *ℤ t')) ≡ t'
    comp₁ = trans (cong₂ _+ℤ_ (*ℤ-zeroˡ s') (*ℤ-identityˡ t')) (+ℤ-identityˡ t')
    -- component 2: (1·s') + ((-q)·t') = s' + (-(q·t')) = s' - t'·q
    comp₂ : ((1ℤ *ℤ s') +ℤ ((-ℤ (+ q)) *ℤ t')) ≡ (s' -ℤ (t' *ℤ (+ q)))
    comp₂ = cong₂ _+ℤ_ (*ℤ-identityˡ s')
                  (trans (neg-*-left (+ q) t') (cong -ℤ_ (*ℤ-comm (+ q) t')))
