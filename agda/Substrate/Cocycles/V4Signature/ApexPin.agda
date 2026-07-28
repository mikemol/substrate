------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.ApexPin
--
-- ⟡apex-pin — pins the CY-5 signature cocycle's GAUGE (V₄-Group-Setoid,
-- Substrate.Cocycles.V4Signature.V4GroupSetoid) to the WITNESS TOWER'S
-- APEX factor (apex-V₄, Substrate.WitnessTower.WholeTower). Both are, by
-- construction, `to-setoid V₄-Group` — the SAME normal form — so the
-- identification is `refl`. Stating it makes CY-5 literally a reading of
-- the tower's rung-3 apex, rather than a parallel use of the same V₄.
--
-- WHY THIS MATTERS (routing, not new content): the witness tower is the
-- substrate's transport hub — WholeTower identifies the whole tower with
-- S₄ = V₄ ⋊ (Z₃ ⋊ Z₂), its apex factor being V₄. The V4Signature cocycle
-- arc (CY-5, chirality Q-9, the 24≅S₄ bijection) is built on the SAME V₄
-- but imported directly from Groups.V4, leaving it tower-ADJACENT rather
-- than tower-MANIFEST. This module's dependency cone contains BOTH the
-- tower apex (via WholeTower) and the cocycle gauge (via V4GroupSetoid),
-- and the `refl` below witnesses that the cocycle's gauge IS the tower
-- apex — so CY-5's V₄-orbit structure transports through the tower like
-- everything else on the group/simplex spine.
--
-- Zero postulates, --safe --without-K. Verified (agda 2.6.3) alongside its
-- full cone incl. WholeTower.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.ApexPin where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

open import Substrate.Groups.V4.Bijection using (V₄)

-- the tower apex (rung-3 factor of the whole tower = S₄)
open import Substrate.WitnessTower.WholeTower using (apex-V₄)

-- the CY-5 cocycle's gauge
open import Substrate.Cocycles.V4Signature.V4GroupSetoid using (V₄-Group-Setoid)

------------------------------------------------------------------------
-- THE PIN. Both sides are `to-setoid V₄-Group : SetoidGroup V₄ _≡_`.
-- Definitionally equal ⇒ refl.
------------------------------------------------------------------------

apex-is-cy5-gauge : apex-V₄ ≡ V₄-Group-Setoid
apex-is-cy5-gauge = refl

-- The symmetric reading, for consumers who hold the cocycle gauge and want
-- the tower apex (same term; both directions are refl).
cy5-gauge-is-apex : V₄-Group-Setoid ≡ apex-V₄
cy5-gauge-is-apex = refl
