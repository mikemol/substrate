------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Quint
--
-- 5-operand distributor — used for Z₅ Coxeter fifth-power identity.
-- Cons `a` onto normalize-quad b c d e.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core.HigherArity.Quint
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
open import Substrate.Groups.Coxeter.Core.HigherArity.Quad
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-quint : (a b c d e : Word) →
                  normalize (a ++ (b ++ (c ++ (d ++ e)))) ≡
                  normalize (normalize a ++ (normalize b ++
                             (normalize c ++ (normalize d ++ normalize e))))
normalize-quint a b c d e = normalize-cons a (normalize-quad b c d e)
