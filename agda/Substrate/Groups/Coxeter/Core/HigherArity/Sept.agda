------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.HigherArity.Sept
--
-- 7-operand distributor — used for Z₇ Coxeter seventh-power identity.
-- Compose normalize-append on `a` with normalize-cong-right on
-- normalize-sext b c d e f g.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans)

module Substrate.Groups.Coxeter.Core.HigherArity.Sept
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
open import Substrate.Groups.Coxeter.Core.HigherArity.Sext
  Word _++_ Canonical normalize normalize-canonical canonical-is-fixed normalize-distrib

normalize-sept : (a b c d e f g : Word) →
                 normalize (a ++ (b ++ (c ++ (d ++ (e ++ (f ++ g)))))) ≡
                 normalize (normalize a ++ (normalize b ++
                            (normalize c ++ (normalize d ++
                             (normalize e ++ (normalize f ++ normalize g))))))
normalize-sept a b c d e f g =
  trans (normalize-append a (b ++ (c ++ (d ++ (e ++ (f ++ g))))))
        (normalize-cong-right (normalize a) (normalize-sext b c d e f g))
