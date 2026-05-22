------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Sext
--
-- 6-operand distributor — used for Zₙ Coxeter sixth-power identities.
-- Cons `a` onto normalize-quint b c d e f.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core.HigherArity.Sext
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
open import Substrate.Groups.Coxeter.Core.HigherArity.Quint
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-sext : (a b c d e f : Word) →
                 normalize (a ++ (b ++ (c ++ (d ++ (e ++ f))))) ≡
                 normalize (normalize a ++ (normalize b ++
                            (normalize c ++ (normalize d ++
                             (normalize e ++ normalize f)))))
normalize-sext a b c d e f = normalize-cons a (normalize-quint b c d e f)
