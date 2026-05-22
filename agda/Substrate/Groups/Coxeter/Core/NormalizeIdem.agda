------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeIdem
--
-- Section 2 of Coxeter.Core. Normalize is idempotent: derived from
-- canonical-is-fixed + normalize-canonical.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq using (_≡_)

module Substrate.Groups.Coxeter.Core.NormalizeIdem
  (Word : Set)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  where

normalize-idem : (w : Word) → normalize (normalize w) ≡ normalize w
normalize-idem w = canonical-is-fixed (normalize-canonical w)
