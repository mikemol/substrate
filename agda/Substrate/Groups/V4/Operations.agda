------------------------------------------------------------------------
-- Substrate.Groups.V4.Operations
--
-- The V₄ group operations: _·_, ε, inv. All routed through V4-Coxeter
-- via the bijection in Substrate.Groups.V4.Bijection.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4.Operations where

import Substrate.Groups.V4-Coxeter as C
open import Substrate.Groups.V4.Bijection
open import Substrate.Foundation.Product using (_×_; _,_)

infixl 7 _·_

_·_ : V₄ → V₄ → V₄
x · y = from-c (to-c x C.· to-c y)

ε : V₄
ε = e

inv : V₄ → V₄
inv x = x  -- V₄ is exponent-2; every element is self-inverse

------------------------------------------------------------------------
-- Constructor-cover combinators for V₄ (per
-- [[feedback-expose-generator-not-orbit-applies]]). Single, double,
-- and triple-axis Cayley-table covers built compositionally — collapses
-- N-case / N²-case / N³-case enumerations into refl tuples.
------------------------------------------------------------------------

v4-cover :
  ∀ {ℓ} (P : V₄ → Set ℓ) →
  P e × P α × P β × P γ →
  ∀ v → P v
v4-cover _ (p , _ , _ , _) e = p
v4-cover _ (_ , p , _ , _) α = p
v4-cover _ (_ , _ , p , _) β = p
v4-cover _ (_ , _ , _ , p) γ = p

v4×v4-cover :
  ∀ {ℓ} (P : V₄ → V₄ → Set ℓ) →
  (P e e × P e α × P e β × P e γ) ×
  (P α e × P α α × P α β × P α γ) ×
  (P β e × P β α × P β β × P β γ) ×
  (P γ e × P γ α × P γ β × P γ γ) →
  ∀ v w → P v w
v4×v4-cover P rows v w =
  v4-cover (P v)
    (v4-cover (λ v' → P v' e × P v' α × P v' β × P v' γ) rows v)
    w

v4×v4×v4-cover :
  ∀ {ℓ} (P : V₄ → V₄ → V₄ → Set ℓ) →
  ( ((P e e e × P e e α × P e e β × P e e γ) ×
     (P e α e × P e α α × P e α β × P e α γ) ×
     (P e β e × P e β α × P e β β × P e β γ) ×
     (P e γ e × P e γ α × P e γ β × P e γ γ))
  × ((P α e e × P α e α × P α e β × P α e γ) ×
     (P α α e × P α α α × P α α β × P α α γ) ×
     (P α β e × P α β α × P α β β × P α β γ) ×
     (P α γ e × P α γ α × P α γ β × P α γ γ))
  × ((P β e e × P β e α × P β e β × P β e γ) ×
     (P β α e × P β α α × P β α β × P β α γ) ×
     (P β β e × P β β α × P β β β × P β β γ) ×
     (P β γ e × P β γ α × P β γ β × P β γ γ))
  × ((P γ e e × P γ e α × P γ e β × P γ e γ) ×
     (P γ α e × P γ α α × P γ α β × P γ α γ) ×
     (P γ β e × P γ β α × P γ β β × P γ β γ) ×
     (P γ γ e × P γ γ α × P γ γ β × P γ γ γ))) →
  ∀ x y z → P x y z
v4×v4×v4-cover P cube x y z =
  v4×v4-cover (P x)
    (v4-cover (λ x' →
       (P x' e e × P x' e α × P x' e β × P x' e γ) ×
       (P x' α e × P x' α α × P x' α β × P x' α γ) ×
       (P x' β e × P x' β α × P x' β β × P x' β γ) ×
       (P x' γ e × P x' γ α × P x' γ β × P x' γ γ))
      cube x)
    y z
