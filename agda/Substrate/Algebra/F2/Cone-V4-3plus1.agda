------------------------------------------------------------------------
-- Substrate.Algebra.F2.Cone-V4-3plus1
--
-- V₄ as the (3, 1)-shaped Cone instance + FieldFilling at 2² = 4.
--
-- Concretely: the V₄ structure presents as a Cone whose
--   * Base = 3-element set, repeated as 3 distinct "readings" of the
--     same underlying 3 elements (V₄-Nonzero as S₃ generators, Fano
--     line points, triangle edges — at the substrate level all
--     three are Fin 3).
--   * Apex = V₄ itself (≅ Fin 4 = 3 nonzero + 1 identity).
--   * Legs = projection V₄ → reading, mapping the 3 nonzero V₄
--     elements to the 3 reading-elements, with the identity ε
--     mapping uniformly to a chosen base-element.
--
-- The FieldFilling witness: |apex| + |base| = 4 + 0 = ... wait, this
-- is the (4, 3) shape if we count apex + base-objects-as-set. The
-- 3+1 = 4 interpretation has |apex| = 4 (V₄) and |conceptual carrier|
-- = 4 = 2². The cone IS the structural realization of "V₄ is the
-- 4-dim F₂-space hosting 3 readings + 1 witness."
--
-- Per [[project-3plus1-is-cone-instance]]: this is the canonical V₄
-- realization of the (3, 1)-cone with apex = single F₂² object.
--
-- Note: the choice of ε's reading-projection IS the substrate's
-- "chirality F₂" / "+1 witness" mechanism. In V₄, ε has no preferred
-- nonzero correspondent, so the projection is by CONVENTION
-- (e.g., ε ↦ first reading element). The conventional choice
-- doesn't matter structurally; it's the "+1" handle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Cone-V4-3plus1 where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₂; ₃; ₄)
open import Substrate.Foundation.Nat using (ℕ; _+_; _^_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.Cone
open import Substrate.Category.Cone.FieldFilling

------------------------------------------------------------------------
-- N-1: The three readings of V₄-Nonzero (all Fin 3 at the substrate
-- level; the readings differ only by interpretation, not by carrier).
------------------------------------------------------------------------

Base-V4 : Fin 3 → Set
Base-V4 _ = Fin 3

------------------------------------------------------------------------
-- N-2: The apex (V₄ ≅ Fin 4).
------------------------------------------------------------------------

Apex-V4 : Set
Apex-V4 = Fin 4

------------------------------------------------------------------------
-- N-3: The cone's legs.
--
-- Projection V₄ → Fin 3: V₄'s 3 nonzero elements (suc-prefixed) map
-- to their corresponding Fin 3 inhabitant; the identity ε (= zero)
-- maps to Fin 3's zero by convention (the conventional choice IS the
-- chirality F₂ — see project_3plus1_is_cone_instance.md).
--
-- The same leg-shape for all 3 readings, since all readings are
-- structurally Fin 3 at this level. (Different readings would have
-- different projections at higher levels — e.g., "S₃ reading" vs
-- "Fano reading" differ in their structural commitments, but at the
-- bare Set level, they're all Fin 3.)
------------------------------------------------------------------------

leg-V4 : Fin 4 → Fin 3
leg-V4 zero               = zero
leg-V4 (suc zero)         = zero
leg-V4 ₂   = suc zero
leg-V4 ₃ = suc (suc zero)

------------------------------------------------------------------------
-- N-4: The (3, 1) Cone instance.
------------------------------------------------------------------------

V4-3plus1-Cone : Cone 3 Base-V4 Apex-V4
V4-3plus1-Cone = record
  { leg = λ _ → leg-V4
  }

------------------------------------------------------------------------
-- N-5: The FieldFilling witness — apex size 4 + base-size 0 (apex IS
-- the 4-element carrier; the 3 readings collapse into the same 3-
-- element Set) = 4 = 2². So q=2, k=2.
--
-- Reading: V₄ as F₂² fits the (3, 1)-cone, with all 4 elements
-- accounted for by the apex itself.
------------------------------------------------------------------------

V4-FieldFilling : FieldFilling 3 1 2 2 V4-3plus1-Cone
V4-FieldFilling = record
  { fills = refl   -- 1 + 3 = 4 = 2^2 ✓
  }

------------------------------------------------------------------------
-- N-6: Capstone.
--
-- After this slice: V₄ is the substrate's first concrete Cone +
-- FieldFilling instance. The (3, 1)-shape captures the 3+1 parity
-- universal at V₄.
--
-- The FieldFilling apex-size = 1 + base-size 3 = 4 = 2^2 ✓.
--
-- Per [[project-3plus1-is-cone-instance]]: V₄'s F₂² structure is
-- the canonical (3, 1)-cone fill. The convention "ε ↦ zero" in the
-- leg projection is the chirality choice; it's GAUGE-FREE in the
-- substrate's sense — any consistent choice works, and the +1
-- handle (the apex's "extra" coverage of ε) is what holds the 3
-- readings together.
------------------------------------------------------------------------
