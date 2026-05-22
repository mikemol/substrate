------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Triple
--
-- 3-operand distributor:
--   normalize (a ++ (b ++ c)) ≡
--   normalize (normalize a ++ (normalize b ++ normalize c))
-- Compose normalize-append (peel `a`) with normalize-cong-right on
-- normalize-distrib b c. Base case of the arity ladder.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans)

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

open import Substrate.Groups.Coxeter.Core.NormalizeAppend
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib
open import Substrate.Groups.Coxeter.Core.NormalizeCongRight
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-triple : (a b c : Word) →
                   normalize (a ++ (b ++ c)) ≡
                   normalize (normalize a ++ (normalize b ++ normalize c))
normalize-triple a b c =
  trans (normalize-append a (b ++ c))
        (normalize-cong-right (normalize a) (normalize-distrib b c))
