------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsCompactClosed
--
-- O1 of the O-arc. F₂-Linear with joint SM + † coherence (= rigid
-- symmetric monoidal dagger category, "compact closed" in Selinger).
--
-- Per [[grothendieck-coherence-rule]]: the joint compatibility of
-- N7 SymmetricMonoidal + N8 DaggerCategory was an EMERGENT orphan
-- after the N-arc; O1 names it structurally as the bundle of both
-- + a compact-closed-coherence obligation (user-supplied).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.SymmetricMonoidal using (SymmetricMonoidal)
open import Substrate.Category.DaggerCategory using (DaggerCategory)

module Substrate.Algebra.F2.Linear.AsCompactClosed
  {ℓO ℓM : Level}
  (F2L-SM : SymmetricMonoidal {ℓO} {ℓM})
  (F2L-Dag : DaggerCategory {ℓO} {ℓM})
  where

F2Linear-AsCompactClosed-SM : SymmetricMonoidal
F2Linear-AsCompactClosed-SM = F2L-SM

F2Linear-AsCompactClosed-Dagger : DaggerCategory
F2Linear-AsCompactClosed-Dagger = F2L-Dag

------------------------------------------------------------------------
-- Compact-closed coherence (= rigid + ⊗-† compatibility) is the user
-- obligation; substrate names the SM + † pair as the joint structure.
------------------------------------------------------------------------
