------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ArrowOfArrow.L0Source
--
-- Defines: L0-Source
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ArrowOfArrow; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ArrowOfArrow.L0Source where

open import Substrate.Category.UniversalProperty
open import Substrate.Category.UniversalProperty.Morphism
-- ⚑ THE LOCAL `variable` BLOCK IS DELETED, NOT RE-PRIVATISED. Each leaf of this
-- split carried its own copy of the same generalizable variables AND imports
-- `UPArrow2`, which declares them too — so once the flattened blocks were repaired
-- and `private` dropped, every `S₁` was [AmbiguousName] against the sibling's.
--
-- ⚑ RESTORING `private` WOULD ALSO FIX IT AND IS THE WRONG FIX. `private` is banned
-- here precisely because it implies a leak worth hiding, and the leak is real: four
-- leaves declaring one variable set is duplication, not encapsulation. `UPArrow2`
-- is the cluster root (it imports no sibling), so it OWNS the variables and the
-- others inherit them. One declaration, no modifier, no ambiguity.
open import Substrate.Category.UniversalProperty.ArrowOfArrow.UPArrow2



-- shim accessors: the L0 objects are params, read back off the type.
L0-Source : {A : UPArrowP S₁ T₁ W₁} {B : UPArrowP S₂ T₂ W₂}
          → UPArrow² A B → UPArrowP S₁ T₁ W₁
L0-Source {A = A} _ = A
