------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsGenericHodge
--
-- L7 of the L-arc. The HodgeDim4 Hodge ★ : Vector 6 ≅ Vector 6 as
-- an instance of L5 [[GenericHodgeStar]].
--
-- The Hodge ★ at grade 2 in F₂⁴ is precisely the substrate's
-- canonical Λᵏ ↔ Λⁿ⁻ᵏ duality at n = 4, k = 2 (so n-k = 2 also):
-- the duality is an involution Λ²(F₂⁴) ≅ Λ²(F₂⁴).
--
-- Per [[reserved-selfdual-bijection-gauge]]: this is one of 168
-- F₂-linear bijections in the GaugeTorsor; the canonical
-- representative anchors the gauge family.
--
-- Per [[universal-property-discipline]]: the GenericHodgeStar
-- primitive (L5) captures the bijection structure abstractly; this
-- module discharges the obligation for HodgeDim4.
--
-- Per [[torsion-element-universal]]: this same ★ is also a HasOrder
-- order-2 instance (already established in Substrate.Algebra.F2.
-- HodgeDim4.HodgeStar). The L7 view + the HasOrder view are two
-- universal-property identifications of the same operator.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsGenericHodge where

open import Data.Nat using (ℕ)
open import Data.Fin using (Fin; zero; suc)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar
  using (hodge-star; hodge-involution)

open import Substrate.Category.GenericHodgeStar
  using (GenericHodgeStar; mkGenericHodgeStar)

------------------------------------------------------------------------
-- HodgeDim4 ★ as a GenericHodgeStar instance.
--
-- At n = 4, k = 2 (so n - k = 2): both LamK and LamNk are Vector 6,
-- and star = star-inv = apply hodge-star (because ★² = id).
--
-- section + retraction are both witnessed by hodge-involution.
------------------------------------------------------------------------

HodgeStar-AsGenericHodge : GenericHodgeStar
HodgeStar-AsGenericHodge = mkGenericHodgeStar
  4                                  -- n = 4
  (suc (suc zero))                   -- k = 2 ∈ Fin 5
  (Vector 6)                         -- LamK = Λ²(F₂⁴)
  (Vector 6)                         -- LamNk = Λ²(F₂⁴) (since n-k = 2)
  (apply hodge-star)                 -- star
  (apply hodge-star)                 -- star-inv = star (involution)
  hodge-involution                   -- section
  hodge-involution                   -- retraction

------------------------------------------------------------------------
-- Capstone — Hodge ★ as L5 GenericHodgeStar instance.
--
-- L7 of the L-arc. Closes the substrate's universal-property
-- identifications of the canonical HodgeDim4 ★ operator:
--   * Order-2 endomap (HasOrder via HasOrder-from-perm)
--   * Universal property of FreeLinearization (HodgeStar-
--     FreeLinearization)
--   * Cone instance (HodgeStar-ConeWithMorphisms)
--   * GTorsor representative (the 168-orbit's anchor in
--     GaugeTorsor.AtlasCatalogue)
--   * L5 GenericHodgeStar instance (THIS)
--
-- The five views all identify the same bijection from different
-- universal-property angles; per [[universal-property-discipline]],
-- this multi-view identification IS the canonical substrate
-- treatment of the Hodge dual.
--
-- After L7: the L-arc bridges (L6 + L7) are in place; HodgeDim4
-- consumes the new algebra primitives.
--
-- Next: L8 LieAlgebra.Morphism (Lie homomorphism layer for the
-- L8-L10 Grothendieck-closure mini-arc).
------------------------------------------------------------------------
