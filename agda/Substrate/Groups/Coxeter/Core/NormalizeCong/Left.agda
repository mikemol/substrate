------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeCong.Left
--
-- normalize-cong-left b eq :
--   normalize (a₁ ++ b) ≡ normalize (a₂ ++ b)
-- given eq : normalize a₁ ≡ normalize a₂.
--
-- Mirror of NormalizeCong.Right — pulled out as a sibling so the
-- chirality pair is exposed at the file boundary. Closes via the
-- left asymmetric distributor: peel normalize off the left operand
-- on both sides, apply cong, peel back.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong)

module Substrate.Groups.Coxeter.Core.NormalizeCong.Left
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

normalize-cong-left : (b : Word) {a₁ a₂ : Word} →
                      normalize a₁ ≡ normalize a₂ →
                      normalize (a₁ ++ b) ≡ normalize (a₂ ++ b)
normalize-cong-left b {a₁} {a₂} eq =
  trans (normalize-append a₁ b)
  (trans (cong (λ x → normalize (x ++ b)) eq)
         (sym (normalize-append a₂ b)))
