------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeCong.Right
--
-- normalize-cong-right a eq :
--   normalize (a ++ b₁) ≡ normalize (a ++ b₂)
-- given eq : normalize b₁ ≡ normalize b₂.
--
-- Closes via the right asymmetric distributor: peel normalize off the
-- right operand on both sides, apply cong, peel back. Mirror of
-- NormalizeCong.Left — exposed as a sibling pair so the similarity
-- checker can surface the chirality structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong)

module Substrate.Groups.Coxeter.Core.NormalizeCong.Right
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.NormalizeAppend
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-cong-right : (a : Word) {b₁ b₂ : Word} →
                       normalize b₁ ≡ normalize b₂ →
                       normalize (a ++ b₁) ≡ normalize (a ++ b₂)
normalize-cong-right a {b₁} {b₂} eq =
  trans (normalize-append-right a b₁)
  (trans (cong (λ x → normalize (a ++ x)) eq)
         (sym (normalize-append-right a b₂)))
