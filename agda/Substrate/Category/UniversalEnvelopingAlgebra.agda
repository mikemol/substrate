------------------------------------------------------------------------
-- Substrate.Category.UniversalEnvelopingAlgebra
--
-- The categorical primitive for universal enveloping algebras.
--
-- Given a Lie algebra L, the universal enveloping algebra U(L) is
-- the universal associative algebra equipped with a Lie homomorphism
-- ι : L → U(L)_Lie, where U(L)_Lie has bracket [x, y] = xy - yx.
--
-- Universal property: for any associative algebra A and any Lie
-- homomorphism φ : L → A_Lie, there exists a UNIQUE associative-
-- algebra homomorphism φ' : U(L) → A extending φ. This makes
-- U : Lie → Assoc the LEFT ADJOINT to the forgetful functor
-- Assoc → Lie (associative algebra ↦ underlying Lie algebra under
-- the commutator bracket).
--
-- L18 of the L-arc. Substrate's first canonical Lie-side adjunction.
--
-- Per [[categorical-name-first]]: "universal enveloping algebra" /
-- "U(g)" / "PBW basis" (Poincaré-Birkhoff-Witt) are standard names.
-- The PBW theorem: U(L) ≅ S(L) as vector spaces (symmetric algebra),
-- with explicit basis = ordered monomials in a chosen L-basis.
--
-- Per [[continuous-via-discrete-inference-rules]]: the UEA's carrier
-- U is abstract (user-supplied); the substrate captures the
-- associative-algebra structure + the Lie embedding + the bracket
-- compatibility.
--
-- Per [[expose-generator-not-orbit]]: L's basis IS the generator
-- (ordered monomials over the basis span U by PBW); the orbit is
-- the full universal enveloping algebra structure.
--
-- Specific instances (deferred to consumers):
--   * U(sl₂) = the universal enveloping algebra of sl₂ — generated
--     by E, H, F with relations [H,E]=2E, [H,F]=-2F, [E,F]=H
--   * U(g) for g semisimple = (after Verma) the source for highest-
--     weight representations
--   * L19 MonsterLieAlgebra has its own UEA (Borcherds' universal
--     enveloping vertex algebra)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalEnvelopingAlgebra where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.LieAlgebra using (LieAlgebra)

private
  variable
    ℓL ℓU : Level

------------------------------------------------------------------------
-- The UniversalEnvelopingAlgebra record.
--
-- Bundles:
--   * L : LieAlgebra — the input Lie algebra
--   * U : Set — the UEA carrier
--   * 0U : U, 1U : U, _+U_, _*U_ — associative algebra structure on U
--   * ι : L.V → U — the Lie-algebra embedding
--   * ι-bracket-relation : the embedding sends L-brackets to U-
--     commutators. Stated as ι(x ·L y) +U (ι y *U ι x) ≡ (ι x *U ι y)
--     — equivalent to ι([x,y]) = ι(x)·ι(y) - ι(y)·ι(x) but written
--     without subtraction (which requires negation on U).
--
-- The universal-property witness (uniqueness of factorisation
-- through U) is the substrate's L17-style obligation; concrete
-- instances supply it.
------------------------------------------------------------------------

record UniversalEnvelopingAlgebra (L : LieAlgebra {ℓL}) : Set (lsuc ℓU ⊔ ℓL) where
  constructor mkUEA
  field
    U                   : Set ℓU
    0U                  : U
    1U                  : U
    _+U_                : U → U → U
    _*U_                : U → U → U
    *U-assoc            : (a b c : U) → ((a *U b) *U c) ≡ (a *U (b *U c))
    ι                   : LieAlgebra.V L → U
    ι-bracket-relation  :
      (x y : LieAlgebra.V L) →
      (ι (LieAlgebra._·_ L x y) +U (ι y *U ι x)) ≡ (ι x *U ι y)

------------------------------------------------------------------------
-- Capstone — UEA primitive in place.
--
-- L18 of the L-arc. With L18 landed, the substrate has the Lie-side
-- adjunction infrastructure:
--   * U : Lie → Assoc — left adjoint to the underlying-Lie functor
--   * Concrete UEAs (U(sl₂), U(so₃), …) are constructible as L18
--     instances supplied by consumers
--
-- Per [[universal-property-discipline]]: the UEA's defining universal
-- property (= unique factorisation through U) is left as the
-- consumer's obligation. The substrate provides the structure +
-- the bracket-commutator compatibility; the uniqueness witness
-- + PBW theorem are domain-specific.
--
-- Per [[homology-cohomology-recursion]]: the UEA's homology is
-- Lie-algebra cohomology of L (Chevalley-Eilenberg complex via
-- L3 ExteriorAlgebra). The substrate's L18 + L3 + L9 close the
-- structural infrastructure for Lie cohomology calculations.
--
-- Next: L19 MonsterLieAlgebra (parametric instance of L2 LieAlgebra
-- at the Monster's Borcherds-Kac-Moody V♮-graded Lie algebra).
------------------------------------------------------------------------
