------------------------------------------------------------------------
-- Substrate.Algebra.F2.Universal
--
-- M-1.5 of the Cocycles structural-migration plan. The universal
-- property characterising F₂ as the unique 2-element type with two
-- distinguished elements.
--
-- This file's scope is the SET-LEVEL universal property: any type
-- with exactly two distinct elements is in bijection with F₂. This
-- is the foundational bridge — every future representation of F₂
-- (Bool, Coxeter Z₂, Fin 2, ...) packages into `F₂-Like` once and
-- the iso to our F₂ follows by this single bridge.
--
-- The FIELD-LEVEL universal property (operation preservation across
-- the iso) is deferred to its own slice — to be added when the
-- first downstream consumer needs it (likely M-2's Vec F₂ n / Bool
-- interop, if any).
--
-- Status: scaffolding, no in-tree consumers yet. The point is the
-- bridge SHAPE: a universal property as a record + a constructive
-- function producing the iso. Future bridges instantiate the shape
-- per representation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Universal where

open import Substrate.Foundation.Level using (Level; suc)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym)

open import Substrate.Algebra.F2

------------------------------------------------------------------------
-- F₂-Like: the set-level characterisation of "a 2-element type
-- with two distinguished elements."
--
-- BHK reading: an inhabitant of F₂-Like is *constructive evidence*
-- that a type behaves like F₂ as a set. The witnesses are: the two
-- chosen elements, a proof of distinctness, and a completeness
-- function (a proof that every element of T is provably one of the
-- two chosen ones).
------------------------------------------------------------------------

record F₂-Like {ℓ : Level} : Set (suc ℓ) where
  field
    T   : Set ℓ
    𝟘ₜ  : T
    𝟙ₜ  : T

    -- Distinctness of the two distinguished elements.
    distinct : 𝟘ₜ ≡ 𝟙ₜ → ⊥

    -- Completeness: T has exactly 2 elements (every element is
    -- demonstrably one of the two).
    complete : (t : T) → (t ≡ 𝟘ₜ) ⊎ (t ≡ 𝟙ₜ)

------------------------------------------------------------------------
-- F₂ itself is the canonical F₂-Like (trivial instance).
------------------------------------------------------------------------

F₂-is-F₂-Like : F₂-Like
F₂-is-F₂-Like = record
  { T        = F₂
  ; 𝟘ₜ       = 𝟘
  ; 𝟙ₜ       = 𝟙
  ; distinct = 𝟘≢𝟙
  ; complete = F₂-cases
  }

------------------------------------------------------------------------
-- The universal-property bridge: F₂-Like → set-iso to F₂.
--
-- Given any L : F₂-Like, produce (to, from, to-from, from-to)
-- witnessing T ≅ F₂ as sets.
--
-- This is the BHK content. A future representation (say, Bool)
-- packages into F₂-Like; then `to` and `from` provide the bridge
-- to our F₂ without enumerating axioms.
------------------------------------------------------------------------

module _ {ℓ : Level} (L : F₂-Like {ℓ}) where
  open F₂-Like L

  to : T → F₂
  to t with complete t
  ... | inj₁ _ = 𝟘
  ... | inj₂ _ = 𝟙

  from : F₂ → T
  from 𝟘 = 𝟘ₜ
  from 𝟙 = 𝟙ₜ

  -- Backward → forward.
  to-from : (x : F₂) → to (from x) ≡ x
  to-from 𝟘 with complete 𝟘ₜ
  ... | inj₁ _    = refl
  ... | inj₂ 𝟘≡𝟙 = ⊥-elim (distinct 𝟘≡𝟙)
  to-from 𝟙 with complete 𝟙ₜ
  ... | inj₁ 𝟙≡𝟘 = ⊥-elim (distinct (sym 𝟙≡𝟘))
  ... | inj₂ _    = refl

  -- Forward → backward.
  from-to : (t : T) → from (to t) ≡ t
  from-to t with complete t
  ... | inj₁ t≡𝟘 = sym t≡𝟘
  ... | inj₂ t≡𝟙 = sym t≡𝟙
