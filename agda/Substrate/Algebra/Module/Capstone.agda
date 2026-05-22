------------------------------------------------------------------------
-- Substrate.Algebra.Module.Capstone
--
-- Mod10 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- Re-exports the M-arc + Mod-arc + summarises the gap-closure /
-- retrofit map.
--
-- =====================================================================
-- TOWER SUMMARY
-- =====================================================================
--
-- ALGEBRA LADDER (M1-M10)
--   M1  Magma           — single binary op
--   M2  Semigroup       — Magma + assoc
--   M3  Monoid          — Semigroup + identity (F₁ included as ⊤)
--   M4  Group           — Monoid + inverse
--   M5  AbelianGroup    — Group + commutativity
--   M6  Semiring        — additive CommMonoid + mult Monoid + distrib
--   M7  Ring            — Semiring with additive AbelianGroup
--   M8  Field           — Ring + multiplicative inverse on non-zero
--   M9  F2 as Field     — F₂'s ring/field laws as accessor projections
--   M10 Q as Field      — ℚ's Magma scaffolding + Field obligation rec
--
-- MODULE TOWER (Mod1-Mod10)
--   Mod1 Module           — R-Module record (4 module axioms)
--   Mod2 ModuleHom        — structure-preserving map
--   Mod3 ModuleHom.Compose — identity + composition (category laws)
--   Mod4 Module.Free      — FreeCarrier A n = Vec A n + componentwise ops
--   Mod5 Module.Free.Basis — basis embedding + FreeBasisUniversal
--   Mod6 F2.AsModule      — F₂ⁿ as Module F₂-Ring
--   Mod7 Q.AsModule       — ℚⁿ as Module from ℚ-Field-Obligation
--   Mod8 Module.Free.UniqueExtension — generic linear-extensionality
--   Mod9 FreeLinearizationR.AsModule — FLR bridge to FreeBasisUniversal
--   Mod10 (this file)     — capstone + summary
--
-- =====================================================================
-- GAP-CLOSURE MAPPING
-- =====================================================================
--
-- | Audit gap                                  | Closed at | How             |
-- |--------------------------------------------|-----------|-----------------|
-- | ℚ-ring-laws (Q-arc deferreds)              | M10 + Mod7| Obligation rec  |
-- | ℚ-vector +-identity (TPQ inherits)         | Mod7      | Mod7 lifter     |
-- | ℚ-bilinearity (modify-Q-prod)              | M7 + Mod7 | Ring distrib    |
-- | ℚ-linear-extensionality (FLQ7/TPQ7)        | Mod8      | from-universal  |
-- | F₂-vector arithmetic                       | Mod6      | F₂-FreeModule   |
-- | FreeLinearizationR universal property      | Mod9      | Bridge record   |
-- | F₁ as base case                            | M3        | trivial Monoid  |
-- | RuleAction operad assoc + identity         | M3        | (mechanical)    |
-- | GeneratorOperad right-identity             | M3        | Monoid right-id |
--
-- Two sibling-tower gaps remain (B-arc respect-≈M, Conway add/trans);
-- closed by Set1-Set5 (Setoid) and G1-G10 (game-induction) arcs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Module.Capstone where

-- M-arc (algebra ladder)
open import Substrate.Algebra.Magma         public using (Magma)
open import Substrate.Algebra.Semigroup     public using (Semigroup)
open import Substrate.Algebra.Monoid        public using (Monoid; F₁-Monoid)
open import Substrate.Algebra.Group         public using (Group)
open import Substrate.Algebra.AbelianGroup  public using (AbelianGroup)
open import Substrate.Algebra.Semiring      public using (Semiring)
open import Substrate.Algebra.Ring          public using (Ring)
open import Substrate.Algebra.Field         public using (Field)

-- F₂ / ℚ as Field instances
open import Substrate.Algebra.F2.AsField    public using (F₂-Field; F₂-Ring)
open import Substrate.Algebra.Q.AsField     public
  using (ℚ-+-Magma; ℚ-·-Magma; ℚ-Field-Obligation)

-- Module tower
open import Substrate.Algebra.Module             public using (Module)
open import Substrate.Algebra.Module.Hom         public using (ModuleHom)
open import Substrate.Algebra.Module.Hom.Compose public
  using (id-ModHom; compose-ModHom)
open import Substrate.Algebra.Module.Free        public
  using (FreeCarrier; free-zero; free-+; free-scalar)
open import Substrate.Algebra.Module.Free.Basis  public
  using (basis-vec; free-basis; FreeBasisUniversal)
open import Substrate.Algebra.Module.Free.UniqueExtension public
  using (FreeModuleExtensionality;
         FreeBasisUniversalAt;
         extensionality-from-universal)

-- Module instances
open import Substrate.Algebra.F2.AsModule public
  using (F₂-FreeModule; F₂-FreeModule-on-FreeCarrier)
open import Substrate.Algebra.Q.AsModule public
  using (module Lifters)

------------------------------------------------------------------------
-- M-arc + Mod-arc closure. The substrate's algebraic foundation is
-- now a unified two-tower: every per-R / per-Vector law derives as
-- a tower-accessor projection. Sibling towers (Setoid, Conway)
-- launch from here.
------------------------------------------------------------------------
