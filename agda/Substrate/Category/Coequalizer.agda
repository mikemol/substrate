------------------------------------------------------------------------
-- Substrate.Category.Coequalizer
--
-- Dual of Substrate.Category.Equalizer. For (f, g : A → B), the
-- coequalizer is the universal map h : B → Z such that h ∘ f ≡ h ∘ g
-- pointwise. Where Equalizer materialises a SUBTYPE of A (the points
-- where f and g agree), Coequalizer materialises the UNIVERSAL
-- PROPERTY on B-out-going maps.
--
-- Per [[project-agda-cubical-extraction-discipline]] (no HITs): the
-- quotient carrier B/~ (where ~ identifies f a with g a) is not
-- introduced as a new type. Instead the substrate captures
-- "coequalising maps out of B" — i.e., the universal property at
-- the level of factorisations — which is structurally equivalent
-- to the quotient's universal property in the absence of HITs.
-- Mirrors [[substrate-algebra-quotient]] / Substrate.Algebra.Quotient.
--
-- Per the skeleton-as-pullback principle: once Equalizer is lifted
-- to a CategoryOf-level record, Coequalizer absorbs as Equalizer on
-- Opposite via opposite-Functor. At the current Set-level resolution
-- the two primitives sit side-by-side; the absorption happens at the
-- next abstraction lift.
--
-- Dual companions:
--   * IsCoequalising  ~ IsEqualised
--   * Coequalises h   ~ membership in Equalizer-Of
--   * coequalizer-factor ~ equalizer-factor (codomain-side dual)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Coequalizer where

open import Level using (Level)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Function using (id)

open import Substrate.Category.Coalgebra using (Endomap; FixedPoint; fixed)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- IsCoequalising — point-level coequalising predicate.
--
-- For h : B → Z to coequalise (f, g : A → B), it must collapse the
-- pair (f a, g a) for every a : A. This is the dual of IsEqualised:
-- where IsEqualised lifts a point of A through the agreement of f
-- and g, IsCoequalising forces a B-out-going map to identify the
-- f/g images.
------------------------------------------------------------------------

record IsCoequalising
       {A B Z : Set ℓ} (f g : A → B) (h : B → Z) (a : A) : Set ℓ where
  field
    coequalised : h (f a) ≡ h (g a)

open IsCoequalising public

------------------------------------------------------------------------
-- Coequalises — the universal property at the codomain level.
--
-- A map h : B → Z coequalises (f, g) iff it collapses (f a, g a) for
-- every a. This is the substrate-honest formulation of "h factors
-- through the coequalizer B / (f∼g)" without materialising the
-- quotient carrier.
--
-- The universal property: any h coequalising (f, g) IS the factoring
-- map. There is no separate `coequalizer-factor` here because, in the
-- absence of HITs, h itself plays the role of the factorisation.
-- The non-trivial content is the COEQUALISES predicate; the
-- factorisation is its content.
------------------------------------------------------------------------

Coequalises : {A B Z : Set ℓ} (f g : A → B) (h : B → Z) → Set ℓ
Coequalises {A = A} f g h = (a : A) → h (f a) ≡ h (g a)

------------------------------------------------------------------------
-- coequalizer-factor — the factorisation as a coequalising map.
--
-- Given (f, g : A → B) and a map h : B → Z together with a
-- pointwise commutation h ∘ f ≡ h ∘ g, this packages h as the unique
-- coequalising factor. Dual shape to equalizer-factor: equalizer
-- ingests "Z → A with agreement" and produces "Z → Equalizer-Of f g";
-- coequalizer ingests "B → Z with collapsing" and produces the
-- coequaliser-map itself.
------------------------------------------------------------------------

coequalizer-factor :
  {A B Z : Set ℓ} (f g : A → B)
  (h : B → Z) →
  ((a : A) → h (f a) ≡ h (g a)) →
  Coequalises f g h
coequalizer-factor _ _ _ commutes = commutes

------------------------------------------------------------------------
-- coequalizer-factor-commutes — the factorisation IS the map.
--
-- Trivial at this resolution (the factor IS h); recorded for shape
-- parity with equalizer-factor-commutes.
------------------------------------------------------------------------

coequalizer-factor-commutes :
  {A B Z : Set ℓ} (f g : A → B)
  (h : B → Z) (commutes : (a : A) → h (f a) ≡ h (g a)) →
  (b : B) → h b ≡ h b
coequalizer-factor-commutes _ _ _ _ _ = refl

------------------------------------------------------------------------
-- Cokernel-At — dual of Kernel-At.
--
-- The cokernel of f : A → B at a base point b is the coequalising
-- predicate for f against the constant-b function (= the universal
-- map collapsing the f-image down to b's class).
------------------------------------------------------------------------

Cokernel-At : {A B Z : Set ℓ} → (A → B) → B → (B → Z) → A → Set ℓ
Cokernel-At f b h a = IsCoequalising f (λ _ → b) h a

------------------------------------------------------------------------
-- Bridge to Coalgebra primitive — h coequalises (γ, id) iff h
-- identifies every x with γ x.
--
-- Dual of Equalizer's fixed-point bridge. Where Equalizer's bridge
-- says "fixed points are equalised points," Coequalizer's bridge
-- says "the coequaliser of γ vs id is the universal map collapsing
-- each orbit to a single value" — i.e., maps invariant under γ.
------------------------------------------------------------------------

coequalises→γ-invariant :
  {X Z : Set ℓ} {γ : Endomap X} {h : X → Z} →
  Coequalises γ id h → (x : X) → h (γ x) ≡ h x
coequalises→γ-invariant ce x = ce x

γ-invariant→coequalises :
  {X Z : Set ℓ} {γ : Endomap X} {h : X → Z} →
  ((x : X) → h (γ x) ≡ h x) → Coequalises γ id h
γ-invariant→coequalises inv = inv
