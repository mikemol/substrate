------------------------------------------------------------------------
-- Substrate.Groups.V4.Axioms.RightCancelEpsilon
--
-- a · b ≡ b forces a ≡ ε.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Axioms.RightCancelEpsilon where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Groups.V4.Operations using (_·_; ε; v4×v4-cover)

·-right-cancel-ε : (a b : V₄) → a · b ≡ b → a ≡ ε
·-right-cancel-ε = v4×v4-cover _
  ( ((λ _ → refl) , (λ _ → refl) , (λ _ → refl) , (λ _ → refl))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  , ((λ ()) , (λ ()) , (λ ()) , (λ ()))
  )
