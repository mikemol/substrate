------------------------------------------------------------------------
-- Substrate.Foundation.Fin.Combine.CombineRemQuotInverse
--
-- combine-remQuot : ∀ k → combine (proj₁ (remQuot n k)) (proj₂ (remQuot n k)) ≡ k.
-- The reverse round-trip: combining the unpacked pair recovers k.
-- Proof by SplitAtView destructure on k.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Fin.Combine.CombineRemQuotInverse where

open import Substrate.Foundation.Nat using (ℕ; suc; _*_)
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.Raise
open import Substrate.Foundation.Fin.RemQuot
open import Substrate.Foundation.Fin.SplitAt
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (inj₁; inj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Fin.SplitAt.InjectIdentity using (splitAt-inject)
open import Substrate.Foundation.Fin.SplitAt.RaiseIdentity using (splitAt-raise)
open import Substrate.Foundation.Fin.SplitAt.View using (SplitAtView; fromₗ; fromᵣ; splitAt-view)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)

combine-remQuot :
  ∀ m n (k : Fin (m * n)) →
  combine (proj₁ (remQuot {m} n k)) (proj₂ (remQuot {m} n k)) ≡ k
combine-remQuot (suc m) n k with splitAt-view n {m * n} k
... | fromₗ j  with splitAt n {m * n} (inject+ (m * n) j) | splitAt-inject n {m * n} j
...   | _ | refl = refl
combine-remQuot (suc m) n k | fromᵣ i'
  with splitAt n {m * n} k | splitAt-raise n {m * n} i'
... | _ | refl = cong (raise n) (combine-remQuot m n i')
