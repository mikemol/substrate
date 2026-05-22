------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeAppend.Left
--
-- normalize-append:
--   normalize (a ++ b) ≡ normalize (normalize a ++ b)
-- The "left" asymmetric distributor — pulls normalize through to the
-- left operand. Derived from normalize-distrib + normalize-idem.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong)

module Substrate.Groups.Coxeter.Core.NormalizeAppend.Left
  (Word : Set)
  (_++_ : Word → Word → Word)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

open import Substrate.Groups.Coxeter.Core.NormalizeIdem
  Word Canonical normalize normalize-canonical canonical-is-fixed

normalize-append : (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ b)
normalize-append a b =
  trans (normalize-distrib a b)
        (sym (trans (normalize-distrib (normalize a) b)
                    (cong (λ x → normalize (x ++ normalize b))
                          (normalize-idem a))))
