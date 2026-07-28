------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-Z4-x-FreeCyclic
--
-- A 3-axis strict-monoid: Z₃ × Z₄ × FreeCyclic, with componentwise
-- composition. Demonstrates that the substrate's DirectProduct
-- pattern iterates: nested products give arbitrarily many composition
-- axes.
--
-- The underlying Word is a 3-pair (Word Z₃-Base.Gen × Word Z₄-Base.Gen ×
-- Word F.Gen). Composition is componentwise ++ on each axis.
-- Identity is the triple-ε.
--
-- Why direct definition instead of nested DirectProduct? Substrate's
-- DirectProduct.agda makes `_++-prod_` private (to avoid a putative
-- name clash with Core); this prevents directly cascading DirectProduct.
-- The direct definition here demonstrates the structure cleanly
-- without needing to refactor DirectProduct.
--
-- Per [[project-graded-bicategorical-arc]]: instance of the n-axis
-- composition pattern. Z₃ × Z₄ × FreeCyclic has 3 commuting cyclic
-- structures (orders 3, 4, ∞) tensored together. The grading
-- (FreeCyclic component) sits naturally as the "degree axis."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-Z4-x-FreeCyclic where
open import Substrate.Groups.Z3-Coxeter using (++-assoc)

open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Coxeter.Cyclic.Base 3 as Z₄-Base
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.FreeCyclic-Coxeter as F
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-identity-right)

------------------------------------------------------------------------
-- N-1: The 3-axis Word type.
------------------------------------------------------------------------

Word3 : Set
Word3 = Word Z₃-Base.Gen × Word Z₄-Base.Gen × Word F.Gen

------------------------------------------------------------------------
-- N-2: The 3-axis identity.
------------------------------------------------------------------------

ε3 : Word3
ε3 = ([] , [] , [])

------------------------------------------------------------------------
-- N-3: Componentwise composition.
------------------------------------------------------------------------

_++3_ : Word3 → Word3 → Word3
(a₁ , a₂ , a₃) ++3 (b₁ , b₂ , b₃) = (a₁ ++ b₁ , a₂ ++ b₂ , a₃ ++ b₃)

infixr 5 _++3_

------------------------------------------------------------------------
-- N-4: Strict associativity (via componentwise ++-assoc).
------------------------------------------------------------------------

++3-assoc :
  (a b c : Word3) → (a ++3 b) ++3 c ≡ a ++3 (b ++3 c)
++3-assoc (a₁ , a₂ , a₃) (b₁ , b₂ , b₃) (c₁ , c₂ , c₃) =
  cong₂ _,_ (Z₃.++-assoc a₁ b₁ c₁)
            (cong₂ _,_ (Z₄.++-assoc a₂ b₂ c₂)
                       (++-assoc a₃ b₃ c₃))

------------------------------------------------------------------------
-- N-5: Identity laws.
------------------------------------------------------------------------

++3-identity-left : (a : Word3) → ε3 ++3 a ≡ a
++3-identity-left (a₁ , a₂ , a₃) = refl

++3-identity-right : (a : Word3) → a ++3 ε3 ≡ a
++3-identity-right (a₁ , a₂ , a₃) =
  cong₂ _,_ (++-identity-right a₁)
            (cong₂ _,_ (++-identity-right a₂) (++-identity-right a₃))

------------------------------------------------------------------------
-- N-6: Capstone — 3-axis strict-monoid structure.
--
-- After this slice:
--
--   * Word3 = Z₃.Word × Z₄.Word × F.Word (3-pair).
--   * ε3, _++3_, ++3-assoc, ++3-identity-{left,right} : strict monoid
--     structure on Word3.
--
-- Three commuting cyclic structures (orders 3, 4, ∞) composed via
-- componentwise ++. The FreeCyclic axis gives the ℕ-grading (slice
-- 5's pattern applied to the third component).
--
-- This generalizes: any number of commuting Coxeter instances can
-- be composed via componentwise ++ on the n-pair, with all monoid
-- laws inherited componentwise from each component's Word laws.
--
-- A full Strict2Monoid instance with the normalize-based 2-cells
-- (≈) requires either (a) nesting DirectProduct (currently blocked
-- by the private _++-prod_) or (b) defining the 3-axis normalize
-- directly (componentwise). Deferred until needed.
--
-- Per [[project-graded-bicategorical-arc]]: the 3-axis structure
-- demonstrates that the substrate's composition iterates cleanly.
-- The strict-2-monoid + n-fold-product pattern gives strict n-fold
-- compositional structures for free, modulo the privacy refactor.
------------------------------------------------------------------------
