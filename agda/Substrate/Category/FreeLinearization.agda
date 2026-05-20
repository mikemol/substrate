------------------------------------------------------------------------
-- Substrate.Category.FreeLinearization
--
-- Primitive #6 in the Substrate.Category.Primitives roadmap.
-- Names the substrate's "free F₂-module from a finite set" universal
-- property as a categorical primitive.
--
-- The free F₂-module on Fin n IS Vector n; the universal property:
-- any function f : Fin n → Vector m extends uniquely to a linear map
-- Linear n m. Substrate's existing `linear-from-images` IS this
-- extension; this primitive packages the universal property as a
-- record.
--
-- Per [[feedback-categorical-name-first]]: "free F₂-module" is the
-- categorical name for what the substrate has been doing with
-- `linear-from-images`. This primitive surfaces the universal
-- property explicitly.
--
-- The original Primitives.DBE.md listed #6 as the "continuous-side
-- bridge"; at F₂ the discrete version IS the structural primitive,
-- and continuous versions (Laplacian eigenvectors etc.) would fit
-- via analogous universal properties at the continuous algebras.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearization where

open import Data.Fin using (Fin)
open import Data.Nat using (ℕ)
open import Relation.Binary.PropositionalEquality using (_≡_)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)

------------------------------------------------------------------------
-- The FreeLinearization record.
--
-- For finite n, m : ℕ, a FreeLinearization n m captures:
--   * The "free basis" images : Fin n → Vector m (= the universal
--     unit pointing at where each basis element maps).
--   * The unique linear extension : Linear n m.
--   * extension-on-basis: the extension agrees with images at each
--     basis vector.
--   * uniqueness: any other linear extension agreeing on basis must
--     equal this one pointwise on all vectors.
------------------------------------------------------------------------

record FreeLinearization (n m : ℕ) : Set where
  field
    images               : Fin n → Vector m
    extension            : Linear n m
    extension-on-basis   : (i : Fin n) → apply extension (basis i) ≡ images i
    uniqueness           : (other-ext : Linear n m) →
                           ((i : Fin n) → apply other-ext (basis i) ≡ images i) →
                           (v : Vector n) → apply extension v ≡ apply other-ext v

open FreeLinearization public

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: FreeLinearization n m packages the universal
-- property of the free F₂-module on Fin n at the categorical level.
--
-- Slice 2 (FromImages constructor) instantiates this from the
-- existing linear-from-images + apply-linear-from-images-basis +
-- linear-extensionality infrastructure.
--
-- Substrate-wide implication: the apply-linear-from-images-basis
-- universal property (per [[feedback-universal-property-discipline]])
-- IS the substrate's #6 categorical primitive, NAMED.
------------------------------------------------------------------------
