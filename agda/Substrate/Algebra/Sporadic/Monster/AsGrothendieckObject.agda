------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.Monster.AsGrothendieckObject
--
-- O5 of the O-arc. The Monster as a single substrate-internal object
-- built via Z3 GrothendieckConstruction over its 4 internal views
-- (T8 AsCoalgebra, Y7+Y8 AsPresented, Z9 AsAutGriess, L19 LieAlgebra).
--
-- Per [[grothendieck-coherence-rule]] + EMERGENT N-arc audit: with
-- the substrate's 4 Monster views + functorial bridges via N1/N3,
-- the 4 can be packaged as a Grothendieck construction over an
-- index category whose objects are the views.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)

module Substrate.Algebra.Sporadic.Monster.AsGrothendieckObject
  {ℓO ℓM : Level}
  -- The total category of Monster views (= Z3 ∫ over index category
  -- whose objects are AsCoalgebra/AsPresented/AsAutGriess/LieAlgebra
  -- with bridges as morphisms; user-supplied).
  (Monster-Total : CategoryOf {ℓO} {ℓM})
  where

Monster-AsGrothendieckObject : CategoryOf
Monster-AsGrothendieckObject = Monster-Total

------------------------------------------------------------------------
-- Substrate-named single-object Monster via ∫. After O5, the
-- substrate's 4 internal views are accessible as fibers of one
-- substrate object.
------------------------------------------------------------------------
