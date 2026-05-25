------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeAppend.Right
--
-- normalize-append-right:
--   normalize (a ++ b) ≡ normalize (a ++ normalize b)
-- The "right" asymmetric distributor — pulls normalize through to the
-- right operand. Derived from normalize-distrib + normalize-idem,
-- mirror of normalize-append.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_; trans; sym; cong; trans-sym)

module Substrate.Groups.Coxeter.Core.NormalizeAppend.Right
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

normalize-append-right : (a b : Word) →
                         normalize (a ++ b) ≡ normalize (a ++ normalize b)
normalize-append-right a b =
  trans-sym (normalize-distrib a b)
            (trans (normalize-distrib a (normalize b))
                   (cong (λ x → normalize (normalize a ++ x))
                         (normalize-idem b)))
