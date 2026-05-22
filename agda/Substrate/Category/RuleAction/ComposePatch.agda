------------------------------------------------------------------------
-- Substrate.Category.RuleAction.ComposePatch
--
-- compose-patch : F₂Patch concatenation (matches Python's
-- tuple-of-pairs semantics; later substitutions at the same index
-- overwrite earlier — resolved by the runtime).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RuleAction.ComposePatch where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.Category.RuleAction.F2Patch using (F₂Patch)

compose-patch : F₂Patch → F₂Patch → F₂Patch
compose-patch []       ys = ys
compose-patch (x ∷ xs) ys = x ∷ compose-patch xs ys
