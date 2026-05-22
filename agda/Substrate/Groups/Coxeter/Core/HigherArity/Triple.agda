------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Triple
--
-- 3-operand distributor:
--   normalize (a ++ (b ++ c)) ≡
--   normalize (normalize a ++ (normalize b ++ normalize c))
-- Base case of the arity ladder: cons `a` onto the binary
-- normalize-distrib for (b, c).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core.HigherArity.Triple
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

normalize-triple : (a b c : Word) →
                   normalize (a ++ (b ++ c)) ≡
                   normalize (normalize a ++ (normalize b ++ normalize c))
normalize-triple a b c = normalize-cons a (normalize-distrib b c)
