------------------------------------------------------------------------
-- Eliza.Manifold
--
-- The chamber-step action: a ParamEndomap `Gen → Chamber → Chamber`
-- realising the A₃ Coxeter system's action on its 24 chambers.
--
-- Per Substrate.Category.Coalgebra.FiniteOrder, each generator is an
-- order-2 endomap on Chamber: `apply g (apply g x) ≡ x`. The braid
-- relations between distinct generators are the order-2 / order-3
-- entries of the A₃ Coxeter matrix:
--
--   (s₁s₂)³ = e   and   (s₂s₃)³ = e   and   (s₁s₃)² = e
--
-- These are postulated here as the manifold's CONTRACT; the concrete
-- bijection of Chamber to S₄ permutation-tuples lives in the Python.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Manifold where

open import Eliza.Prelude    using (_≡_; _,_)
open import Eliza.Alphabets  using (Gen; s₁; s₂; s₃; Chamber; e; w₀)
open import Eliza.Transducer using (StatefulTransducer)

------------------------------------------------------------------------
-- 1. The chamber action — postulated.
------------------------------------------------------------------------

postulate
  apply : Gen → Chamber → Chamber

------------------------------------------------------------------------
-- 2. The Coxeter relations. Each generator is an involution; the
-- pairwise products satisfy the A₃ braid orders. Stated pointwise to
-- avoid funext.
------------------------------------------------------------------------

postulate
  -- s_i² = e  (involution at every chamber)
  involution-s₁ : (x : Chamber) → apply s₁ (apply s₁ x) ≡ x
  involution-s₂ : (x : Chamber) → apply s₂ (apply s₂ x) ≡ x
  involution-s₃ : (x : Chamber) → apply s₃ (apply s₃ x) ≡ x

  -- (s₁s₂)³ = e
  braid-12 : (x : Chamber) →
             apply s₁ (apply s₂ (apply s₁ (apply s₂ (apply s₁ (apply s₂ x))))) ≡ x

  -- (s₂s₃)³ = e
  braid-23 : (x : Chamber) →
             apply s₂ (apply s₃ (apply s₂ (apply s₃ (apply s₂ (apply s₃ x))))) ≡ x

  -- (s₁s₃)² = e  (the disjoint generators commute)
  commute-13 : (x : Chamber) →
               apply s₁ (apply s₃ x) ≡ apply s₃ (apply s₁ x)

------------------------------------------------------------------------
-- 3. The manifold as a StatefulTransducer Gen Chamber Chamber.
--
-- Output = new state = new chamber. The Engine's chamber-walking
-- layer instantiates this; trajectories are the runStateful unfolding.
------------------------------------------------------------------------

manifold-step : StatefulTransducer Gen Chamber Chamber
manifold-step = record
  { s₀   = e
  ; step = λ x g → let y = apply g x in y , y
  }
