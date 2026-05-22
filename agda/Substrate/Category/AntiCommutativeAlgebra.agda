------------------------------------------------------------------------
-- Substrate.Category.AntiCommutativeAlgebra
--
-- The categorical primitive for anti-commutative algebras:
--   * V : Set — carrier
--   * 0V : V, _+V_ : V → V → V — additive structure on V
--   * _·_ : V → V → V — bilinear product
--   * anti-comm : (x · y) +V (y · x) ≡ 0V
--                 (equivalently: x · y = -(y · x) when V has additive
--                 inverses; this stated form avoids requiring negation
--                 explicitly)
--
-- L1 of the 20-slice L-arc (Lie + Grassmann algebras). Foundational
-- sibling to X3 [[CommutativeNonAssociativeAlgebra]]:
--   * CNAA: x · y = y · x          (commutative)
--   * ACA:  x · y + y · x = 0V     (anti-commutative)
-- The two together span the bilinear-product axis. CNAA + Jordan
-- identity ⇒ Jordan algebra (X3's natural extension). ACA + Jacobi
-- ⇒ Lie algebra (L2's extension).
--
-- Per [[categorical-name-first]]: "anti-commutative algebra" is the
-- standard categorical name; "skew-commutative" / "alternating" are
-- equivalent in characteristic ≠ 2 (which is the relevant setting
-- for sl₂, so₃, gauge Lie algebras, etc.).
--
-- Per [[continuous-via-discrete-inference-rules]]: the carrier is
-- abstract (user-supplied Set); the algebra structure is the
-- substrate's content. Specific instances (sl₂, so₃, Bivector) are
-- the L-arc's targets.
--
-- Per [[coalgebraic-not-consumer-driven]]: ACA records anti-
-- commutativity AS A STRUCTURE, not as a downstream-caller-needed
-- predicate. Lie algebra (L2) consumes ACA + Jacobi; ExteriorAlgebra
-- (L3) consumes ACA at degree-1.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.AntiCommutativeAlgebra where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The AntiCommutativeAlgebra record.
--
-- Minimum-axiom record per substrate convention. Additional structure
-- (Jacobi for Lie, graded for Exterior, etc.) layers on top.
------------------------------------------------------------------------

record AntiCommutativeAlgebra : Set (lsuc ℓ) where
  constructor mkACA
  field
    V         : Set ℓ
    0V        : V
    _+V_      : V → V → V
    _·_       : V → V → V
    anti-comm : (x y : V) → ((x · y) +V (y · x)) ≡ 0V

------------------------------------------------------------------------
-- Capstone — anti-commutative algebra primitive in place.
--
-- L1 of the 20-slice L-arc. Foundation for:
--   * L2 LieAlgebra (ACA + Jacobi identity)
--   * L3 ExteriorAlgebra (graded ACA at odd degrees)
--   * L6 Bivector.AsExterior (HodgeDim4 instance)
--   * L14 sl₂, L15 so₃ (small-rank Lie algebra instances)
--   * L19 MonsterLieAlgebra (the Monster Lie algebra as Borcherds-
--     Kac-Moody Lie algebra, V♮-graded)
--
-- Per [[categorical-name-first]]: standard naming, established
-- universal property. Per [[expose-generator-not-orbit]]: the algebra
-- structure (V's basis + structure constants) IS the generator; Lie
-- group / loop group is the orbit.
--
-- Next: L2 (LieAlgebra: ACA + Jacobi).
------------------------------------------------------------------------
