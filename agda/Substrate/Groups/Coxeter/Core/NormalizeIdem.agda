------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core.NormalizeIdem
--
-- Section 2 of Coxeter.Core. Normalize is idempotent: derived from
-- canonical-is-fixed + normalize-canonical.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}


-- ⚑ `_≡_` is used in the TELESCOPE below, so its import must PRECEDE the
-- module header: a parameter list is scope-checked before anything inside
-- `where`.  The splitter emits the prelude AFTER the header (correct for a
-- body, wrong for a telescope), so every leaf whose parameters mention `≡`
-- inherited this.  MEASURED: 6 of the Core leaves.
open import Substrate.Foundation.Eq
open import Substrate.Algebra.Quotient.Canonical

module Substrate.Groups.Coxeter.Core.NormalizeIdem
  (Word : Set)
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  where

normalize-idem : (w : Word) → normalize (normalize w) ≡ normalize w
normalize-idem w = canonical-is-fixed (normalize-canonical w)
