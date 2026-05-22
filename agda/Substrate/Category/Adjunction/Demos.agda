------------------------------------------------------------------------
-- Substrate.Category.Adjunction.Demos
--
-- Concrete demonstrations that the `linear-adjunction` from
-- Substrate.Category.Adjunction's universal property IS the M-3.5
-- inference rule. Re-derives `apply-linear-from-images-basis` and
-- `linear-extensionality`-style results via the adjunction's unit /
-- counit / extension-unique.
--
-- Substrate-relevant: gives a template for retrofitting any
-- apply-linear-from-images-basis or linear-extensionality call site
-- as an adjunction invocation. Substrate-wide retrofit sweep is a
-- separate slice; this file provides the patterns to apply.
--
-- Per `feedback_categorical_name_first`: the adjunction's universal
-- property IS the inference rule; demonstrations show concrete
-- equivalence to M-3.5's existing lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Adjunction.Demos where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal
  using (linear-extensionality)

open import Substrate.Category.Adjunction
  using (IsLinearAdjunction; linear-adjunction; images-of-linear;
         linear-extension-unique)

------------------------------------------------------------------------
-- N-1: M-3.5 apply-linear-from-images-basis via adjunction.unit.
--
-- The substrate's existing M-3.5 lemma `apply-linear-from-images-basis`
-- IS literally `IsLinearAdjunction.unit linear-adjunction`.
--
-- Per the IsLinearAdjunction instance `linear-adjunction`:
--   unit = apply-linear-from-images-basis
-- So `IsLinearAdjunction.unit linear-adjunction f i ≡
--     apply-linear-from-images-basis f i` definitionally.
--
-- This is a refl-level equivalence — same content, named with its
-- universal property.
------------------------------------------------------------------------

apply-linear-from-images-basis-via-adjunction :
  ∀ {n m} (f : Fin n → Vector m) (i : Fin n) →
  apply (linear-from-images f) (basis i) ≡ f i
apply-linear-from-images-basis-via-adjunction =
  IsLinearAdjunction.unit linear-adjunction

-- Direct equivalence: the two definitions agree at every input.
apply-linear-from-images-basis≡adjunction-unit :
  ∀ {n m} (f : Fin n → Vector m) (i : Fin n) →
  apply-linear-from-images-basis f i
    ≡ IsLinearAdjunction.unit linear-adjunction f i
apply-linear-from-images-basis≡adjunction-unit _ _ = refl

------------------------------------------------------------------------
-- N-2: linear-extensionality-style derivation via
-- linear-extension-unique.
--
-- Standard usage: "if L agrees with M on basis vectors, then L agrees
-- with M on all vectors." Reframed via adjunction:
--
--   Any L : Linear n m that takes basis i to f i (= R L = f) IS
--   linear-from-images f at apply-level.
--
-- linear-extension-unique packages this: given an agreement
-- hypothesis on basis, conclude agreement on all v with linear-from-
-- images f.
------------------------------------------------------------------------

-- Counit at any L: applying L IS applying its canonical reconstruction.
counit-application :
  ∀ {n m} (T : Linear n m) (v : Vector n) →
  apply (linear-from-images (images-of-linear T)) v ≡ apply T v
counit-application = IsLinearAdjunction.counit linear-adjunction

-- For any linear map L : Linear n m and any function f : Fin n → Vector m
-- that agrees with L's basis images: L v equals linear-from-images f v
-- on every v. This is the universal mapping property in action — packages
-- "agreement on basis lifts to agreement on all vectors" through the
-- adjunction.
adjunction-extension :
  ∀ {n m} (L : Linear n m) (f : Fin n → Vector m) →
  ((i : Fin n) → apply L (basis i) ≡ f i) →
  (v : Vector n) → apply L v ≡ apply (linear-from-images f) v
adjunction-extension L f agree = linear-extension-unique f L agree

------------------------------------------------------------------------
-- N-3: Capstone — adjunction primitive's reach demonstrated.
--
-- After this slice, the substrate has concrete demonstrations that:
--
--   * `apply-linear-from-images-basis` IS literally the adjunction's
--     unit (= `IsLinearAdjunction.unit linear-adjunction`).
--
--   * `linear-extensionality` is re-derivable via `linear-extension-
--     unique` (the adjunction's universal mapping property packaged
--     directly).
--
-- Substrate-wide retrofit pattern: any call site of M-3.5 lemmas can
-- be replaced with the corresponding adjunction-named version. The
-- demotion is structural (renames per-instance lemma calls to
-- universal-property citations), not LoC-reducing — but it makes the
-- categorical content explicit at every use site.
--
-- Per `feedback_categorical_name_first`: M-3.5's lemmas ARE the
-- substrate's instances of the linear-extension adjunction's universal
-- property. The retrofit pattern surfaces this; the actual sweep
-- across the substrate is a separate slice.
--
-- Concrete retrofit candidates (deferred):
--
--   * Stabiliser.agda's `s₁-on-eᵢ`, `s₂-on-eᵢ` helpers (6 calls).
--   * StabiliserClosure.agda's apply-then-basis chains (now demoted
--     to congruence-compose-3 corollary; less M-3.5 surface remaining).
--   * CongruenceBridge.agda's `congruence-act-bridge-3` uses 18
--     `bilinear-form-of-bridge-3` calls — these are about bilinear
--     forms, not adjunctions, so out of scope.
--   * HodgeStar.agda's `hodge-involution-basis` uses 2
--     `apply-linear-from-images-basis` calls.
--
-- Total retrofit-able sites: ~10 across the dim-3 / dim-4 metric-gauge
-- arc + Hodge work. Sweep would be a separate slice; this demo
-- provides the templates.
------------------------------------------------------------------------
