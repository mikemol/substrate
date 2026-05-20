------------------------------------------------------------------------
-- Substrate.Category.WedgeProduct
--
-- The categorical primitive for the rank-2 wedge pairing
--   ∧ : V × V → Λ²V
-- as the universal alternating bilinear map.
--
-- L4 of the 20-slice L-arc. Specialised rank-2 slice of L3
-- [[ExteriorAlgebra]]; named separately because the rank-2 case
-- captures the bivector structure used throughout HodgeDim4 +
-- physics (angular momentum, 2-form fields, etc.) without needing
-- the full graded-algebra apparatus.
--
-- The substrate-level universal property: WedgeProduct V is the
-- universal alternating bilinear map ω : V × V → W such that
-- ω(v, v) = 0. Any alternating bilinear map V × V → W' factors
-- through it.
--
-- Per [[categorical-name-first]]: "wedge product" / "Λ²" / "rank-2
-- exterior product" are standard names. The universal property is
-- "the cokernel of the symmetrisation map V ⊗ V → S²V"; equivalently,
-- "the antisymmetrisation V ⊗ V → V ∧ V".
--
-- Per [[expose-generator-not-orbit]]: the generator is the pairing
-- ∧ + the alternating relation v ∧ v = 0L; the orbit (Λ²V's basis =
-- 2-subsets of a basis of V) emerges by extension.
--
-- Specific instances:
--   * L6 Bivector.AsExterior: HodgeDim4 ∧²(F₂⁴) instantiates both
--     L3 (full Λ(F₂⁴)) and L4 (the rank-2 piece directly)
--   * 3-dim cross product (deferred; ℝ³ ∧² ≅ ℝ³ via Hodge ★)
--   * 2-form fields (deferred; continuous-side via discrete
--     inference rules)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.WedgeProduct where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality using (_≡_)

private
  variable
    ℓV ℓL : Level

------------------------------------------------------------------------
-- The WedgeProduct record.
--
-- Bundles:
--   * V_base : Set — the degree-1 vector space
--   * Lambda2 : Set — the rank-2 wedge target Λ²(V_base)
--   * 0L : Lambda2, _+L_ — additive structure on Lambda2
--   * _∧_ : V_base → V_base → Lambda2 — the wedge pairing
--   * alternating : (v : V_base) → (v ∧ v) ≡ 0L
--
-- From alternating + bilinearity (implicit at the substrate level;
-- supplied by V_base + Lambda2 being vector spaces in concrete
-- instances), anti-commutativity follows:
--   (v +V w) ∧ (v +V w) = v∧v + v∧w + w∧v + w∧w = 0
--   ⇒ v∧w + w∧v = 0
--   ⇒ v∧w = -(w∧v)
-- (the derivation requires negation in Lambda2; the substrate
-- primitive states the alternating axiom only).
------------------------------------------------------------------------

record WedgeProduct : Set (lsuc (ℓV ⊔ ℓL)) where
  constructor mkWedgeProduct
  field
    V_base       : Set ℓV
    Lambda2      : Set ℓL
    0L           : Lambda2
    _+L_         : Lambda2 → Lambda2 → Lambda2
    _∧_          : V_base → V_base → Lambda2
    alternating  : (v : V_base) → (v ∧ v) ≡ 0L

------------------------------------------------------------------------
-- Capstone — rank-2 wedge primitive in place.
--
-- L4 of the L-arc. Foundation for:
--   * L5 GenericHodgeStar (the Λᵏ ≅ Λⁿ⁻ᵏ duality, of which rank-2 ↔
--     rank-(n-2) is the most common substrate case)
--   * L6 Bivector.AsExterior (HodgeDim4 ∧²(F₂⁴) ≅ F₂⁶ instance)
--   * L7 HodgeStar.AsGenericHodge (the existing HodgeStar at
--     HodgeDim4 instantiates the generic Hodge duality)
--
-- After L4: substrate has both the full graded-algebra primitive
-- (L3 ExteriorAlgebra) and the rank-2 slice (L4 WedgeProduct).
-- Most HodgeDim4 content lives at rank-2; the rank-2 primitive is
-- ergonomic for those callers.
--
-- Per [[cone-subsumes-equalizer-pullback]] analog: L4 is a
-- specialisation of L3 (rank-2 slice). The full algebra is the
-- universal target; L4 is the ergonomic specialisation. Both
-- primitives coexist, with L4 being a derivable rank-2 view of L3.
--
-- Next: L5 GenericHodgeStar (substrate-side Λᵏ ↔ Λⁿ⁻ᵏ duality
-- primitive).
------------------------------------------------------------------------
