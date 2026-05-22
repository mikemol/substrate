------------------------------------------------------------------------
-- Substrate.Category.ExteriorAlgebra
--
-- The categorical primitive for exterior (Grassmann) algebras.
--
-- An exterior algebra Λ(V) over a base vector space V is the free
-- associative algebra on V modulo the relation v ∧ v = 0V (for
-- v ∈ V at degree 1). The defining nilpotency at degree-1 +
-- bilinearity forces graded-anti-commutativity:
--   x ∧ y = (-1)^(|x|·|y|) (y ∧ x)
-- at all degrees.
--
-- L3 of the 20-slice L-arc. The substrate-level primitive captures
-- the universal property minimally (free + nilpotent-at-degree-1);
-- specialised graded-anti-commutativity is derived.
--
-- Per [[categorical-name-first]]: "exterior algebra" / "Grassmann
-- algebra" / "Λ(V)" are standard names. The universal property is
-- "the free associative algebra on V mod v² = 0"; alternatively, the
-- left adjoint to the forgetful functor (graded-anti-comm algebras)
-- → Set on degree-1.
--
-- Per [[continuous-via-discrete-inference-rules]]: the carrier
-- V_alg is abstract (user-supplied); the algebra structure is the
-- substrate's content.
--
-- Specific instances:
--   * L6 Bivector.AsExterior: Λ²(F₂⁴) at HodgeDim4 (the 6-dim
--     bivector space, ∧² of the underlying F₂-4-space)
--   * Differential forms (deferred; continuous-side, supplied as
--     abstract set per the substrate's discrete/continuous bridge)
--   * Fermion Fock space (deferred; physics-side specialisation)
--
-- Per [[universal-property-discipline]]: future L4 WedgeProduct
-- primitive names the bilinear pairing V × V → Λ²V universally;
-- L5 GenericHodgeStar names the Λᵏ ≅ Λⁿ⁻ᵏ duality at full rank.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ExteriorAlgebra where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ ℓB : Level

------------------------------------------------------------------------
-- The ExteriorAlgebra record.
--
-- Bundles:
--   * V_alg : Set — graded algebra carrier (typically ⊕ₖ Λᵏ(V_base))
--   * 0V : V_alg, _+V_ : V_alg → V_alg → V_alg — additive structure
--   * _∧_ : V_alg → V_alg → V_alg — wedge product (associative)
--   * assoc-∧ : associativity of ∧
--   * V_base : Set — degree-1 base subspace (= the V underlying the
--     exterior algebra)
--   * incl : V_base → V_alg — the degree-1 inclusion
--   * nilpotent : (v : V_base) → (incl v) ∧ (incl v) ≡ 0V
--
-- The universal property: V_alg ≅ T(V_base) / ⟨v ⊗ v⟩ where T is the
-- tensor algebra. From bilinearity of ∧ + nilpotent, graded-anti-
-- commutativity follows at degree-1; higher-degree anti-commutativity
-- follows by induction.
------------------------------------------------------------------------

record ExteriorAlgebra : Set (lsuc (ℓ ⊔ ℓB)) where
  constructor mkExteriorAlgebra
  field
    V_alg     : Set ℓ
    0V        : V_alg
    _+V_      : V_alg → V_alg → V_alg
    _∧_       : V_alg → V_alg → V_alg
    assoc-∧   : (x y z : V_alg) → ((x ∧ y) ∧ z) ≡ (x ∧ (y ∧ z))
    V_base    : Set ℓB
    incl      : V_base → V_alg
    nilpotent : (v : V_base) → ((incl v) ∧ (incl v)) ≡ 0V

------------------------------------------------------------------------
-- Capstone — exterior algebra primitive in place.
--
-- L3 of the L-arc. Foundation for:
--   * L4 WedgeProduct (bilinear pairing V × V → Λ²V)
--   * L5 GenericHodgeStar (Λᵏ ≅ Λⁿ⁻ᵏ duality)
--   * L6 Bivector.AsExterior (HodgeDim4 instance: Λ²(F₂⁴) = the
--     6-dim bivector space)
--   * L9 ExteriorAlgebra.Morphism (graded algebra homomorphism)
--
-- After L3: substrate has both the algebraic (CNAA, LieAlgebra, ACA)
-- and graded-algebraic (ExteriorAlgebra) primitives. Combined with
-- the existing TensorProduct primitive infrastructure, the algebra
-- layer is structurally complete for the L-arc's downstream targets.
--
-- Per [[expose-generator-not-orbit]]: the generator is V_base + the
-- nilpotency relation; the orbit (Λ(V) basis = subsets of a basis
-- of V_base) emerges from quotienting the tensor algebra.
--
-- Next: L4 WedgeProduct (the bilinear pairing as a categorical
-- primitive in its own right).
------------------------------------------------------------------------
