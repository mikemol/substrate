------------------------------------------------------------------------
-- Substrate.Category.ConeBondArchitecture
--
-- Capstone for the Cone + Bond arc (10 slices).
--
-- Re-exports the primitives + canonical instances introduced:
--   * Cone (slice 1) — apex over finite base with legs.
--   * Cone.Product (slice 2) — discrete-base cone = product.
--   * Cone.FieldFilling (slice 3) — |apex| + |base| ≡ p^k.
--   * Cone-V4-3plus1 (slice 4) — V₄ as (3,1)-cone at 2².
--   * Cone-Hamming-7plus1 (slice 5) — Hamming(8,7) as (7,1) at 2³.
--   * Cone.EdgeApex (slice 6) — apex as morphism in Arr(C).
--   * Cone-HodgeStar-EdgeApex (slice 7) — ★ as apex-edge.
--   * FieldBond (slice 8) — oriented inter-field bond.
--   * Z6-FieldBond (slice 9) — Z/6 ≅ F₂ × F₃ via CRT.
--   * THIS capstone (slice 10).
--
-- The substrate's M:N cone universal is now formalized at three
-- generality levels:
--
--   1. Single-object apex (Cone, slice 1).
--   2. Edge apex (Cone.EdgeApex, slice 6) — apex as morphism.
--   3. Multi-field bonds (FieldBond, slice 8) — when M+N doesn't
--      fit a single prime power.
--
-- Plus the field-filling constraint (slice 3) makes explicit the
-- cardinality-fits-prime-power discipline that structurally
-- distinguishes the substrate's M:N cones from generic categorical
-- products.
--
-- Per [[project-3plus1-is-cone-instance]]: this arc realizes the
-- cone framing at the type level. Future work:
--
--   * Equalizer (substrate primitive #2) retrofit as a specific
--     Cone instance.
--   * Pullback (substrate primitive #3) retrofit as another.
--   * Generic CRT primitive for arbitrary coprime decomposition.
--   * Multi-field tower for 168 = 2³·3·7 (the substrate's
--     reserved-selfdual-bijection-gauge 168-family).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ConeBondArchitecture where

------------------------------------------------------------------------
-- Primitives.
------------------------------------------------------------------------

import Substrate.Category.Cone
import Substrate.Category.Cone.Product
import Substrate.Category.Cone.FieldFilling
import Substrate.Category.Cone.EdgeApex
import Substrate.Category.FieldBond

------------------------------------------------------------------------
-- Instances.
------------------------------------------------------------------------

import Substrate.Algebra.F2.Cone-V4-3plus1
import Substrate.Algebra.F2.Cone-Hamming-7plus1
import Substrate.Algebra.F2.HodgeDim4.Cone-HodgeStar-EdgeApex
import Substrate.Algebra.Z6-FieldBond

------------------------------------------------------------------------
-- Capstone — Cone + Bond arc complete.
--
-- 10-slice plan:
--
--   #1  Cone primitive
--   #2  Cone.Product
--   #3  Cone.FieldFilling
--   #4  Cone-V4-3plus1 (V₄ as (3,1)-cone at 2²)
--   #5  Cone-Hamming-7plus1 (Hamming(8,7) as (7,1)-cone at 2³)
--   #6  Cone.EdgeApex
--   #7  Cone-HodgeStar-EdgeApex
--   #8  FieldBond
--   #9  Z6-FieldBond (Z/6 ≅ F₂ × F₃ via CRT)
--   #10 THIS capstone
--
-- The substrate's structural-cone framework now has:
--   * The Cone primitive with field-filling constraint.
--   * Single-object and edge-apex variants.
--   * Concrete instances at small M:N shapes.
--   * Inter-field bond infrastructure for composite-counted structures.
--
-- Per [[feedback-categorical-name-first]]: the substrate's "3+1
-- parity universal" / "M:N split" / "structure + witness" patterns
-- now have CATEGORICAL NAMES (Cone, EdgeApex, FieldBond) anchored
-- to the standard categorical concepts.
--
-- Per [[project-3plus1-is-cone-instance]]: the (3,1) interpretation
-- of the substrate's 3+1 universal is one specific instance of the
-- general cone primitive; the cone shape generalizes to arbitrary
-- M:N at any prime-power filling, with bonds when M+N is composite.
--
-- Deferred follow-ons (queued for future arcs):
--
--   * **Equalizer + Pullback as Cone instances**: retrofit
--     substrate's existing primitives (#2 and #3) as Cone instances,
--     unifying the categorical primitives roadmap.
--
--   * **Generic CRT bond**: for any coprime (m, n), Z/(mn) ≅ Z/m
--     × Z/n via CRT. Needs gcd machinery; substrate has gcd-ℕ.
--
--   * **168-tower of bonds**: |PSL(2,7)| = 2³·3·7 decomposition into
--     a three-field tower with two bonds. Realizes the
--     project_reserved_selfdual_bijection_gauge sacrifice ladder.
--
--   * **Non-discrete cones**: cones with base-internal morphisms
--     (Equalizer = cone over parallel pair; Pullback = cone over
--     cospan). Adds commutativity conditions on the cone legs.
--
--   * **Multi-apex cones**: apex as multiple objects, or a category
--     of apex objects. Higher categorical depth.
------------------------------------------------------------------------
