------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeCong
--
-- Section 4 of Coxeter.Core. Congruence at the normalize level —
-- the chirality pair lifting `normalize b₁ ≡ normalize b₂` to
-- `normalize (a ++ b₁) ≡ normalize (a ++ b₂)`:
--
--   NormalizeCong.Right  — cong on the right operand (a fixed, b varies)
--   NormalizeCong.Left   — cong on the left  operand (b fixed, a varies)
--
-- Both are derived from the asymmetric distributors in
-- NormalizeAppend (Right uses normalize-append-right; Left uses
-- normalize-append). The pair is exposed as sibling files so the
-- similarity checker can surface the chirality structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core.NormalizeCong
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.NormalizeCong.Right
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public

open import Substrate.Groups.Coxeter.Core.NormalizeCong.Left
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib public
