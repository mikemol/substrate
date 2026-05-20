------------------------------------------------------------------------
-- Substrate.Category.SubobjectClassifier
--
-- S7 of the S-arc. Ω = subobject classifier: object such that
-- subobjects of A correspond bijectively to morphisms A → Ω.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.SubobjectClassifier where

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

record SubobjectClassifier
  {ℓO ℓM : Level}
  (C : CategoryOf {ℓO} {ℓM}) : Set ℓO where
  field
    Ω    : CategoryOf.Obj C
    -- True : 1 → Ω + pullback-characterisation: user obligations.
