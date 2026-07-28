------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Bijection.AsDagger
--
-- P2 of the P-arc. F₂-Linear Bijections (forward + backward + 2-sided
-- inverse) as M4 DaggerCategory instance. Closes M-arc residue row.
--
-- Thin projection from Substrate.Category.DaggerCategory.AsNamed:
-- the substrate's "named DaggerCategory" skeleton, with
-- `named-DaggerCategory` renamed to `Bijection-AsDagger` for this
-- specialisation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.Linear.Bijection.AsDagger
  {ℓO ℓM : Level}
  {Obj : Set ℓO} {Mor : Obj → Obj → Set ℓM}
  (Bij-Dag : DaggerCategory Obj Mor)
  where

open import Substrate.Category.DaggerCategory.AsNamed Bij-Dag
  renaming (named-DaggerCategory to Bijection-AsDagger)

