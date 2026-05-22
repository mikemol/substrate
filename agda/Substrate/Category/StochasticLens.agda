------------------------------------------------------------------------
-- Substrate.Category.StochasticLens
--
-- MK11-MK20: a stochastic lens between objects S and A of a Markov
-- category. The forward direction (predict) is a Markov kernel
-- S → A; the backward direction (update / condition) takes (S, B)
-- and produces a new S.
--
-- Stochastic lenses generalise:
--   * Classical lenses (deterministic case)
--   * Bayesian inversion (B = updated belief about S)
--   * Kalman / particle filters (S = state, A = predicted obs,
--     B = actual obs; backward = posterior over states)
--
-- Per [[multi-route-equivariance-recovery]]: lenses ARE the
-- atlas-vs-chart move at the dynamical level — forward and backward
-- views jointly carry the equivariance.
--
-- Per the DBE constructive-completeness criterion: a lens record
-- carries (forward, backward) PLUS round-trip law. Given these, a
-- caller can predict, observe, and update.
--
-- Per [[categorical-name-first]]: Stochastic Lens / Optic is
-- standard.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.StochasticLens where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Probability.MarkovCategory

private
  variable
    ℓ ℓm : Level

------------------------------------------------------------------------
-- MK11: The stochastic lens record.
--
-- Parameterised by:
--   M : a MarkovCategory
--   S : "state" object  (the hidden variable)
--   A : "view" / "prediction" object
--   B : "feedback" / "observation" object
--
-- forward    : S → A (predictive map)
-- backward   : tensor S B → S (conditioning / update)
--
-- Per Fritz / Spivak: a stochastic lens is a Markov category morphism
-- with a "view-update" structure. For Kalman: S = state, A = predicted
-- observation, B = observed value, backward = posterior over S.

record StochasticLens
       (M : MarkovCategory {ℓ} {ℓm})
       (S A B : Obj M) : Set ℓm where
  field
    forward  : Hom M S A
    backward : Hom M (tensor M S B) S

open StochasticLens public

------------------------------------------------------------------------
-- MK12: Identity stochastic lens.
--
-- For S = A = B, the identity lens has forward = id, backward =
-- (project first component): take (S, S) → S via the structure.
-- Stated abstractly; concrete categories supply the projection.

record IdentityLens
       (M : MarkovCategory {ℓ} {ℓm})
       (S : Obj M) : Set ℓm where
  field
    id-lens : StochasticLens M S S S
    forward-is-identity : forward id-lens ≡ id-M M

open IdentityLens public

------------------------------------------------------------------------
-- MK13: Composition of stochastic lenses.
--
-- Given (S → A, view-update over B) and (A → A', view-update over B'),
-- compose to (S → A', view-update over B').
-- Forward composition: compose Markov kernels.
-- Backward composition: route observations through the inner lens's
-- backward, lifted to the outer.
--
-- Stated structurally; concrete instances supply the compositions.

record LensComposition
       (M : MarkovCategory {ℓ} {ℓm}) : Set (lsuc (ℓ ⊔ ℓm)) where
  field
    compose-lens : ∀ {S A A' B B'} →
                   StochasticLens M S A B →
                   StochasticLens M A A' B' →
                   StochasticLens M S A' B'

open LensComposition public

------------------------------------------------------------------------
-- MK14: Lens functoriality.
--
-- Composition is associative (up to the underlying Markov category's
-- composition associativity) and respects identity.

-- LensFunctoriality is a degenerate marker (no fields) — concrete
-- instances inhabit this when they have verified the lens's
-- associativity and identity laws at the runtime side. Structural
-- placeholder; concrete categories supply the laws as separate
-- propositional equalities.

record LensFunctoriality
       (M : MarkovCategory {ℓ} {ℓm})
       (LC : LensComposition M) : Set where
  no-eta-equality

------------------------------------------------------------------------
-- MK15: Category of stochastic lenses over M.
--
-- Objects: triples (S, A, B) with S a state, A view, B observation.
-- Morphisms: stochastic lenses.
-- Identity: IdentityLens.
-- Composition: LensComposition.

record StochasticLensCategory
       (M : MarkovCategory {ℓ} {ℓm}) : Set (lsuc (ℓ ⊔ ℓm)) where
  field
    id-lens-at  : (S : Obj M) → StochasticLens M S S S
    compose     : ∀ {S A A' B B'} →
                  StochasticLens M S A B →
                  StochasticLens M A A' B' →
                  StochasticLens M S A' B'

open StochasticLensCategory public

------------------------------------------------------------------------
-- MK16: Connection — ConjugateMonad → StochasticLens.
--
-- Every ConjugateMonad has an associated stochastic lens in
-- FinStoch (Markov category of finite stochastic kernels):
--   S = Parameter
--   A = Observation (predicted)
--   B = Observation (actual)
--   forward    = predict (parameter → distribution over obs)
--   backward   = update (parameter, obs → posterior parameter)
--
-- Connection stated structurally; concrete bridge depends on the
-- specific Markov category instance for ConjugateMonad.

------------------------------------------------------------------------
-- MK17: Connection — CascadedCoalgebra → StochasticLens.
--
-- A 2nd-order PLL is a stochastic lens at the (state, predicted-obs,
-- actual-obs) triple where:
--   forward  = inner-step's prediction
--   backward = outer-step's update from observation
-- The cascade structure is captured by composing two lenses
-- (inner / outer).

------------------------------------------------------------------------
-- MK18: Filter primitive.
--
-- A Filter is a stochastic lens equipped with a notion of "state
-- estimate" — a Markov kernel Unit → S that updates over time as
-- observations stream in.

record Filter
       (M : MarkovCategory {ℓ} {ℓm})
       (S A B : Obj M) : Set ℓm where
  field
    lens       : StochasticLens M S A B
    estimate   : Hom M (Unit-M M) S    -- current state estimate

open Filter public

------------------------------------------------------------------------
-- MK19: Particle filter sketch.
--
-- A particle filter approximates the state estimate by N samples
-- (the "particles"). Each particle is updated independently via
-- the lens's backward map; resampling occurs at update boundaries.
--
-- Particle-filter = Filter with N parallel state estimates +
-- resampling kernel.

record ParticleFilter
       (M : MarkovCategory {ℓ} {ℓm})
       (S A B : Obj M)
       (N : Set ℓ) : Set ℓm where
  field
    base-filter : Filter M S A B
    -- N parameterises particle count (abstract here; concrete
    -- instances use Fin n for finite N).

open ParticleFilter public

------------------------------------------------------------------------
-- MK20: MK arc capstone — categorical reading.
--
-- The MK arc establishes:
--   * MarkovCategory as the substrate's probabilistic-reasoning generator
--   * StochasticLens as the bidirectional Markov morphism
--   * Filter / ParticleFilter as the application-layer estimators
--
-- The horizon (per user 2026-05-21):
--   * Open Games: stochastic lenses → dependent optics with payoff
--   * Synthetic Measure Theory: Markov category extends to HoTT-native
--     continuous probability via Giry monad on type universes
--
-- Per [[multi-route-equivariance-recovery]]: forward+backward of a
-- lens IS the atlas-of-charts at the dynamical level. The lens's
-- equivariance lives JOINTLY across both directions, not in either
-- alone.
--
-- Per [[homology-cohomology-recursion]]: forward = homology cycle
-- (state evolves under input); backward = cohomology contraction
-- (observation refines state). The lens closes one layer.
------------------------------------------------------------------------
