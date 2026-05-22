------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Quad
--
-- 4-operand distributor — used for V₄-4-product and Z₄ identities.
-- Compose normalize-append on `a` with normalize-cong-right on
-- normalize-triple b c d.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans)

module Substrate.Groups.Coxeter.Core.HigherArity.Quad
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
open import Substrate.Groups.Coxeter.Core.NormalizeCong
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib
open import Substrate.Groups.Coxeter.Core.HigherArity.Triple
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-quad : (a b c d : Word) →
                 normalize (a ++ (b ++ (c ++ d))) ≡
                 normalize (normalize a ++ (normalize b ++
                            (normalize c ++ normalize d)))
normalize-quad a b c d =
  trans (normalize-append a (b ++ (c ++ d)))
        (normalize-cong-right (normalize a) (normalize-triple b c d))
