------------------------------------------------------------------------
-- Substrate.Category.LimitUniversalProperty
--
-- The LIMIT / cofree half of the center — the genuine DUAL of
-- Category.FreeUniversalProperty, completing the symmetric picture:
--
--   colimit side   FreeUP   (unit η : B → F ; map OUT: extend)
--   limit side     LimitUP  (legs π : L → Base i ; map IN: mediate)
--
-- All arrows reversed. FreeUP states "free over generators": for any
-- target + map FROM the basis, a unique map OUT of the free object.
-- LimitUP states "limit of a diagram": for any apex + maps TO the base
-- (a cone), a unique map INTO the limit. This is Category.Cone given the
-- content-bearing universal property Cone itself lacked (Cone had only the
-- leg shape; this adds mediate + commutes + uniqueness).
--
-- Uniqueness is OBSERVATIONAL (up to agreement on all legs), funext-free —
-- the dual of FreeUP stating extend-unique pointwise on the carrier. Two
-- maps into a limit are "equal" exactly when they agree after every
-- projection; that is the limit's natural equality, and --without-K has no
-- funext to make it propositional on the function-typed apex.
--
-- Per [[project_cone_subsumes_equalizer_pullback]]: Equalizer / Pullback
-- are LimitUP at special base diagrams; this names the universal property
-- they share. Discrete base here (a product); base-diagram morphisms add
-- a commutativity side-condition (deferred, as in Cone).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.LimitUniversalProperty where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.Cone using (Cone)
open import Substrate.Category.UniversalProperty using (UPArrowP; mkUP)

------------------------------------------------------------------------
-- 1. THE LIMIT CENTER. Dual of FreeUP. (Discrete base ⇒ product.)
------------------------------------------------------------------------

-- ⟡rc-cheap (⟡set1-rerank2): VESTIGIAL record — the obligations are PARAMETERS
-- (params never raise the sort), Set₁→Set with an empty body.
record LimitUP (n : ℕ) (Base : Fin n → Set) (L : Set)
  -- the legs (projections) — dual to FreeUP's unit η.
  (leg : (i : Fin n) → L → Base i)
  -- THE universal property: every cone (apex A + maps to the base)
  -- factors through L by a mediating map — dual to extend …
  (mediate :
      {A : Set} → ((i : Fin n) → A → Base i) → (A → L))
  -- … which commutes with the legs (π ∘ mediate ≡ f) — dual to
  -- extend-extends …
  (mediate-commutes :
      {A : Set} (f : (i : Fin n) → A → Base i) (i : Fin n) (a : A) →
      leg i (mediate f a) ≡ f i a)
  -- … and is the UNIQUE such map, observationally (any commuting g
  -- agrees with mediate after every projection) — dual to
  -- extend-unique, funext-free.
  (mediate-unique :
      {A : Set} (f : (i : Fin n) → A → Base i) (g : A → L) →
      ((i : Fin n) (a : A) → leg i (g a) ≡ f i a) →
      (a : A) (i : Fin n) → leg i (g a) ≡ leg i (mediate f a))
  : Set where

------------------------------------------------------------------------
-- 2. A LimitUP forgets to the existing Cone shape (so Category.Cone is
--    exactly the data of a LimitUP minus the universal property).
------------------------------------------------------------------------

LimitUP→Cone : {n : ℕ} {Base : Fin n → Set} {L : Set}
               {leg : (i : Fin n) → L → Base i}
               {mediate : {A : Set} → ((i : Fin n) → A → Base i) → (A → L)}
               {mc : {A : Set} (f : (i : Fin n) → A → Base i) (i : Fin n) (a : A) →
                     leg i (mediate f a) ≡ f i a}
               {mu : {A : Set} (f : (i : Fin n) → A → Base i) (g : A → L) →
                     ((i : Fin n) (a : A) → leg i (g a) ≡ f i a) →
                     (a : A) (i : Fin n) → leg i (g a) ≡ leg i (mediate f a)} →
               LimitUP n Base L leg mediate mc mu → Cone n Base L
LimitUP→Cone {leg = leg} lim = record { leg = leg }

------------------------------------------------------------------------
-- 3. NON-VACUITY: the dependent product IS the limit of a discrete base.
--    leg = projection, mediate = tupling. (Dual to free-Set.)
------------------------------------------------------------------------

-- the product's UP data, NAMED (consumers read these instead of the ex-projections).
product-leg : (n : ℕ) (Base : Fin n → Set) (i : Fin n) → ((j : Fin n) → Base j) → Base i
product-leg n Base i g = g i

product-mediate : (n : ℕ) (Base : Fin n → Set) {A : Set}
                → ((i : Fin n) → A → Base i) → A → (i : Fin n) → Base i
product-mediate n Base f a i = f i a

product-LimitUP :
  (n : ℕ) (Base : Fin n → Set)
  → LimitUP n Base ((i : Fin n) → Base i)
      (product-leg n Base)
      (product-mediate n Base)
      (λ f i a → refl)
      (λ f g g-comm a i → g-comm i a)
product-LimitUP n Base = record {}

------------------------------------------------------------------------
-- 4. A LimitUP IS a (content-bearing) UPArrow, per apex A — DUAL of
--    FreeUP-UPArrow (Source/Target roles swapped):
--      Source  = cones with apex A (maps A → Base i)   (the "problem")
--      Target  = mediating maps A → L                  (the "solution")
--      Witness = the candidate IS a cone-map for the problem.
------------------------------------------------------------------------

LimitUP-W :
  {n : ℕ} {Base : Fin n → Set} {L : Set} →
  (leg : (i : Fin n) → L → Base i) → (A : Set) →
  ((i : Fin n) → A → Base i) → (A → L) → Set
LimitUP-W {n} leg A f g = (i : Fin n) (a : A) → leg i (g a) ≡ f i a

LimitUP-UPArrow :
  {n : ℕ} {Base : Fin n → Set} {L : Set}
  (leg : (i : Fin n) → L → Base i) → (A : Set) →
  UPArrowP ((i : Fin n) → A → Base i) (A → L) (LimitUP-W leg A)
LimitUP-UPArrow leg A = mkUP

------------------------------------------------------------------------
-- The center is now symmetric, both sides content-bearing:
--   colimit  FreeUP   (Category.FreeUniversalProperty) + PresentedUP
--   limit    LimitUP  (here)                            + (Cone shape)
-- over one AlgebraClass-indexed / Cone-indexed family, all UPArrow
-- instances. Equalizer / Pullback are LimitUP at non-discrete bases
-- (deferred, per Cone). See [[project_center_free_universal_property]].
------------------------------------------------------------------------
