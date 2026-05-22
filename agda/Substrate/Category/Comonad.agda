------------------------------------------------------------------------
-- Substrate.Category.Comonad
--
-- R2 of the R-arc. Comonad primitive: dual of R1 Monad.
--
-- Substrate-native dual-witnessing: a Comonad on C IS a Monad on
-- Opposite C. The duality between Monad and Comonad is now
-- structurally absorbed by the Opposite primitive — there is no
-- separate Comonad record to maintain; the type alias makes the
-- duality formal rather than cultural.
--
-- Per [[homology-cohomology-recursion]]: this is the recursive
-- moment where a catalogued dual concept (Comonad) becomes a formal
-- artefact of its primal (Monad) via the Opposite witness.
--
-- Field correspondence under the alias:
--   Comonad's S ≡ Monad-on-Opposite's T  (endofunctor)
--   Comonad's ε ≡ Monad-on-Opposite's η  (counit ≡ unit-on-opp;
--                                         arrow direction flipped
--                                         since NT direction reverses
--                                         in Opposite)
--   Comonad's δ ≡ Monad-on-Opposite's μ  (comult ≡ mult-on-opp)
--
-- Consumers access via Monad.T / Monad.η / Monad.μ rather than the
-- historical S / ε / δ. The semantic content is identical.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Comonad where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Monad using (Monad)
open import Substrate.Category.Opposite using (Opposite)

Comonad :
  {ℓO ℓM : Level} → CategoryOf {ℓO} {ℓM} → Set (lsuc (ℓO ⊔ ℓM))
Comonad C = Monad (Opposite C)
