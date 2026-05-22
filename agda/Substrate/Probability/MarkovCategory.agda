------------------------------------------------------------------------
-- Substrate.Probability.MarkovCategory
--
-- MK3-MK10: the substrate's first-class Markov category primitive.
--
-- A Markov category (per Fritz, "A synthetic approach to Markov kernels,
-- conditional independence and theorems on sufficient statistics") is
-- a symmetric monoidal category C such that:
--   (1) Every object X has a commutative comonoid structure (copy, delete).
--   (2) The tensor unit I is terminal: every X has a unique map X → I,
--       which equals the counit (= delete morphism).
--   (3) Morphisms compose, tensor, and respect the comonoid structure
--       up to specific laws.
--
-- Standard examples: FinStoch (Markov kernels on finite sets), Stoch
-- (Markov kernels on measurable spaces). The substrate uses Markov
-- categories to anchor:
--   * Bayesian inference (ConjugateMonad)
--   * Filtering (StochasticLens, MK11)
--   * Probability conservation (terminal-unit ensures distributions
--     marginalise to 1)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Probability.MarkovCategory where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ ℓm : Level

------------------------------------------------------------------------
-- MK3: The Markov category record.

record MarkovCategory : Set (lsuc (ℓ ⊔ ℓm)) where
  field
    Obj    : Set ℓ
    Hom    : Obj → Obj → Set ℓm

    -- Identity and composition.
    id-M   : ∀ {X} → Hom X X
    comp-M : ∀ {X Y Z} → Hom Y Z → Hom X Y → Hom X Z

    -- Tensor product on objects and on morphisms.
    Unit-M : Obj
    tensor : Obj → Obj → Obj
    tensor-M : ∀ {X X' Y Y'} → Hom X Y → Hom X' Y' →
               Hom (tensor X X') (tensor Y Y')

    -- Copy and delete (= comonoid structure on each object).
    copy-M   : ∀ {X} → Hom X (tensor X X)
    delete-M : ∀ {X} → Hom X Unit-M

    -- MK4: Terminal unit law — the unique morphism X → Unit is the
    --      delete morphism. This is what makes the category Markov:
    --      probability mass is conserved.
    terminal-unit-uniqueness :
      ∀ {X} (f : Hom X Unit-M) → f ≡ delete-M

open MarkovCategory public

------------------------------------------------------------------------
-- MK5: Determinism predicate.
--
-- A morphism f : X → Y is DETERMINISTIC iff it commutes with copy:
--   copy_Y ∘ f ≡ (f ⊗ f) ∘ copy_X.
-- In FinStoch, deterministic kernels = functions.

record IsDeterministic
       (M : MarkovCategory {ℓ} {ℓm})
       {X Y : Obj M}
       (f : Hom M X Y) : Set ℓm where
  field
    det-law :
      comp-M M (copy-M M {Y}) f
      ≡
      comp-M M (tensor-M M f f) (copy-M M {X})

open IsDeterministic public

------------------------------------------------------------------------
-- MK6: Almost-sure equality.
--
-- f, g : X → Y are a.s. equal w.r.t. p : Unit → X iff f ∘ p ≡ g ∘ p.

record AlmostSurelyEqual
       (M : MarkovCategory {ℓ} {ℓm})
       {X Y : Obj M}
       (p : Hom M (Unit-M M) X)
       (f g : Hom M X Y) : Set ℓm where
  field
    as-eq : comp-M M f p ≡ comp-M M g p

open AlmostSurelyEqual public

------------------------------------------------------------------------
-- MK7-MK10: Conditional structure, marginalisation, sufficient
-- statistic, Bayesian inversion. Each is a record built over a
-- given MarkovCategory; concrete instances supply the operators.

record ConditionalStructure
       (M : MarkovCategory {ℓ} {ℓm}) : Set (lsuc (ℓ ⊔ ℓm)) where
  field
    conditional : ∀ {X Y} →
                  Hom M (Unit-M M) (tensor M X Y) →
                  Hom M Y X

open ConditionalStructure public

record Marginalisation
       (M : MarkovCategory {ℓ} {ℓm}) : Set (lsuc (ℓ ⊔ ℓm)) where
  field
    marginal : ∀ {X Y} →
               Hom M (Unit-M M) (tensor M X Y) →
               Hom M (Unit-M M) X

open Marginalisation public

record SufficientStatistic
       (M : MarkovCategory {ℓ} {ℓm}) : Set (lsuc (ℓ ⊔ ℓm)) where
  field
    sufficient-factor :
      ∀ {Θ X T} →
      Hom M Θ X →            -- the model X | Θ
      Hom M X T →            -- the statistic
      Hom M T X              -- factorisation X ← T (abstracted)

open SufficientStatistic public

record BayesianInversion
       (M : MarkovCategory {ℓ} {ℓm}) : Set (lsuc (ℓ ⊔ ℓm)) where
  field
    bayes-inverse :
      ∀ {X Y} →
      Hom M (Unit-M M) X →   -- prior
      Hom M X Y →            -- forward kernel
      Hom M Y X              -- Bayesian inverse

open BayesianInversion public

------------------------------------------------------------------------
-- Categorical reading.
--
-- A Markov category is a synthetic axiomatization of probabilistic
-- reasoning. The substrate uses it to anchor:
--   * ConjugateMonad as a Kleisli structure
--   * StochasticLens as bidirectional Markov morphisms
--   * CascadedCoalgebra as coalgebras over a Markov category's tensor
--
-- Per [[homology-cohomology-recursion]]: copy IS the homology cycle's
-- branching; delete IS the cohomology contraction.
--
-- Per [[3plus1-parity-universal]]: (copy, delete, swap) + chirality
-- = 3+1 at the Markov category level.
--
-- Per [[expose-generator-not-orbit]]: MarkovCategory is the generator;
-- FinStoch, Stoch are orbits.
------------------------------------------------------------------------
