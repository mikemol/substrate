------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Quad
--
-- 4-operand distributor — used for V₄-4-product and Z₄ identities.
-- Cons `a` onto normalize-triple b c d.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

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

open import Substrate.Groups.Coxeter.Core.HigherArity.Step
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib
open import Substrate.Groups.Coxeter.Core.HigherArity.Triple
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-quad : (a b c d : Word) →
                 normalize (a ++ (b ++ (c ++ d))) ≡
                 normalize (normalize a ++ (normalize b ++
                            (normalize c ++ normalize d)))
normalize-quad a b c d = normalize-cons a (normalize-triple b c d)
