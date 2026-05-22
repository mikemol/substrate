------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector.AsExterior
--
-- L6 of the L-arc. The HodgeDim4 bivector space Λ²(F₂⁴) as an
-- instance of L4 [[WedgeProduct]]: bilinear pairing
--   ∧ : Vector 4 × Vector 4 → Vector 6
-- with alternating axiom v ∧ v ≡ 𝟎ⱽ.
--
-- The existing Bivector module bundled the bivector type
-- (= Vector 6) and the complement involution but not the wedge
-- pairing itself. This module supplies the wedge + instantiates
-- L4 WedgeProduct.
--
-- Per [[universal-property-discipline]]: the wedge structure is
-- exposed as the substrate's L4 WedgeProduct universal property at
-- HodgeDim4; downstream sites can now consume the rank-2 wedge via
-- the categorical primitive rather than the F₂-specific definition.
--
-- Per [[3plus1-parity-universal]] + [[reserved-selfdual-bijection-
-- gauge]]: the bivector space carries the chirality F₂ via the
-- complement involution (Hodge ★, see L7 bridge); the wedge is the
-- underlying graded structure on which the chirality acts.
--
-- The wedge formula (lex-ordered 2-blade basis):
--   (u ∧ v)[ij] = u_i · v_j + u_j · v_i (in F₂)
-- alternating: (v ∧ v)[ij] = v_i · v_j + v_j · v_i = 2·v_i·v_j = 𝟘
--              via ·-comm + +-self-inverse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector.AsExterior where

open import Level using (Level)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ; _+ⱽ_)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)

open import Substrate.Category.WedgeProduct using (WedgeProduct; mkWedgeProduct)

------------------------------------------------------------------------
-- The wedge product Vector 4 × Vector 4 → Vector 6.
--
-- Lex-ordered 2-blade basis (matching Bivector.b₀₁..b₂₃):
--   index 0: e₀ ∧ e₁  → u₀·v₁ + u₁·v₀
--   index 1: e₀ ∧ e₂  → u₀·v₂ + u₂·v₀
--   index 2: e₀ ∧ e₃  → u₀·v₃ + u₃·v₀
--   index 3: e₁ ∧ e₂  → u₁·v₂ + u₂·v₁
--   index 4: e₁ ∧ e₃  → u₁·v₃ + u₃·v₁
--   index 5: e₂ ∧ e₃  → u₂·v₃ + u₃·v₂
------------------------------------------------------------------------

wedge : Vector 4 → Vector 4 → Bivector
wedge (u₀ ∷ u₁ ∷ u₂ ∷ u₃ ∷ []) (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ []) =
    ((u₀ · v₁) + (u₁ · v₀))
  ∷ ((u₀ · v₂) + (u₂ · v₀))
  ∷ ((u₀ · v₃) + (u₃ · v₀))
  ∷ ((u₁ · v₂) + (u₂ · v₁))
  ∷ ((u₁ · v₃) + (u₃ · v₁))
  ∷ ((u₂ · v₃) + (u₃ · v₂))
  ∷ []

------------------------------------------------------------------------
-- The alternating axiom: v ∧ v ≡ 𝟎ⱽ.
--
-- For each of the 6 components: v_i · v_j + v_j · v_i = (v_i · v_j) +
-- (v_i · v_j) (by ·-comm) = 𝟘 (by +-self-inverse).
------------------------------------------------------------------------

alternating-wedge : (v : Vector 4) → wedge v v ≡ 𝟎ⱽ
alternating-wedge (v₀ ∷ v₁ ∷ v₂ ∷ v₃ ∷ []) =
  helper v₀ v₁ v₂ v₃
  where
    -- Componentwise: v_i · v_j + v_j · v_i = (v_i · v_j) + (v_i · v_j)
    -- = 𝟘. F₂ has only 4 values for each pair; case-split closes.
    helper : (a b c d : F₂) →
             (((a · b) + (b · a)) ∷
              ((a · c) + (c · a)) ∷
              ((a · d) + (d · a)) ∷
              ((b · c) + (c · b)) ∷
              ((b · d) + (d · b)) ∷
              ((c · d) + (d · c)) ∷ []) ≡ 𝟎ⱽ
    helper 𝟘 𝟘 𝟘 𝟘 = refl
    helper 𝟘 𝟘 𝟘 𝟙 = refl
    helper 𝟘 𝟘 𝟙 𝟘 = refl
    helper 𝟘 𝟘 𝟙 𝟙 = refl
    helper 𝟘 𝟙 𝟘 𝟘 = refl
    helper 𝟘 𝟙 𝟘 𝟙 = refl
    helper 𝟘 𝟙 𝟙 𝟘 = refl
    helper 𝟘 𝟙 𝟙 𝟙 = refl
    helper 𝟙 𝟘 𝟘 𝟘 = refl
    helper 𝟙 𝟘 𝟘 𝟙 = refl
    helper 𝟙 𝟘 𝟙 𝟘 = refl
    helper 𝟙 𝟘 𝟙 𝟙 = refl
    helper 𝟙 𝟙 𝟘 𝟘 = refl
    helper 𝟙 𝟙 𝟘 𝟙 = refl
    helper 𝟙 𝟙 𝟙 𝟘 = refl
    helper 𝟙 𝟙 𝟙 𝟙 = refl

------------------------------------------------------------------------
-- The L4 WedgeProduct instance: HodgeDim4 ∧²(F₂⁴) as the universal
-- rank-2 wedge.
------------------------------------------------------------------------

Bivector-AsExterior : WedgeProduct
Bivector-AsExterior = mkWedgeProduct
  (Vector 4)
  Bivector
  𝟎ⱽ
  _+ⱽ_
  wedge
  alternating-wedge

------------------------------------------------------------------------
-- Capstone — Bivector as L4 WedgeProduct instance.
--
-- L6 of the L-arc. The first concrete substrate instance of the new
-- algebra primitives.
--
-- After L6: the bivector space at HodgeDim4 carries the L4
-- WedgeProduct universal property. Downstream sites (HodgeStar
-- bridges, alternative-bridges, gauge torsor) now see the wedge
-- structure abstractly.
--
-- Next: L7 HodgeStar.AsGenericHodge (existing HodgeStar bijection
-- as L5 GenericHodgeStar instance).
------------------------------------------------------------------------
