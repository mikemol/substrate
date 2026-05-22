------------------------------------------------------------------------
-- Substrate.TokiPona.NimiSpace
--
-- T3 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]]. The bridge from Nimi (the
-- vocabulary basis from T2) to the F₂-vector carrier from T1, via
-- Substrate.Category.FreeLinearization.
--
-- Costructure shadow #1 of the Toki Pona arc: any function
-- `Nimi → SemVec m` extends UNIQUELY to a linear map
-- `SemVec nimi-count → SemVec m`. This is the substrate's
-- FreeLinearization universal property at the linguistic site —
-- sister to Lojban's L3 Gismu + L8 WordAlgebra bridge to the free
-- monoid universal property, now realised on the linear side.
--
-- Per [[project-freelinearization-names-linear-from-images]]: the
-- substrate's #6 categorical primitive provides exactly this
-- universal property. T3 lifts it through nimi-index.
--
-- Per [[feedback-categorical-name-first]]: "free F₂-module over Nimi"
-- is the categorical name; T3 instantiates the existing record.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.NimiSpace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; lookup)
  renaming ([] to []ᵥ; _∷_ to _∷ᵥ_)

open import Substrate.TokiPona.SemanticSpace
  using (SemVec; ∅; _⊕_; basis)
open import Substrate.TokiPona.Nimi
  using (Nimi; nimi-count; nimi-index;
         jan; soweli; kili; moku; tomo; ma; telo; ilo; ijo;
         pona; ike; suli; lili; wawa; sin; toki; olin; pana;
         mi; sina; ona; ni;
         li-p; e-p; pi-p; la-p; o-p;
         en; tan; tawa; lon; kepeken)

open import Substrate.Algebra.F2.Linear using (Linear)
open import Substrate.Category.FreeLinearization using (FreeLinearization)
open import Substrate.Category.FreeLinearization.FromImages
  using (free-linearize)

------------------------------------------------------------------------
-- 1. The default one-hot embedding.
--
-- Each nimi maps to its corresponding basis vector in SemVec
-- nimi-count. This is the simplest basis-image map; T3 also
-- supports arbitrary image maps via WithTarget below.
------------------------------------------------------------------------

nimi-as-vector : Nimi → SemVec nimi-count
nimi-as-vector n = basis (nimi-index n)

------------------------------------------------------------------------
-- 2. Inverse of nimi-index via a vector table.
--
-- A Vec Nimi nimi-count holding the 32 nimi in their canonical
-- order; lookup gives Fin nimi-count → Nimi. Needed to lift an
-- image map (Nimi → SemVec m) into a Fin-indexed image map
-- (Fin nimi-count → SemVec m) for the substrate's free-linearize.
------------------------------------------------------------------------

nimi-vec : Vec Nimi nimi-count
nimi-vec =
  jan    ∷ᵥ soweli ∷ᵥ kili   ∷ᵥ moku  ∷ᵥ tomo  ∷ᵥ
  ma     ∷ᵥ telo   ∷ᵥ ilo    ∷ᵥ ijo   ∷ᵥ pona  ∷ᵥ
  ike    ∷ᵥ suli   ∷ᵥ lili   ∷ᵥ wawa  ∷ᵥ sin   ∷ᵥ
  toki   ∷ᵥ olin   ∷ᵥ pana   ∷ᵥ mi    ∷ᵥ sina  ∷ᵥ
  ona    ∷ᵥ ni     ∷ᵥ li-p   ∷ᵥ e-p   ∷ᵥ pi-p  ∷ᵥ
  la-p   ∷ᵥ o-p    ∷ᵥ en     ∷ᵥ tan   ∷ᵥ tawa  ∷ᵥ
  lon    ∷ᵥ kepeken ∷ᵥ []ᵥ

nimi-from-index : Fin nimi-count → Nimi
nimi-from-index = lookup nimi-vec

------------------------------------------------------------------------
-- 2a. Round-trip: nimi-from-index ∘ nimi-index ≡ id.
--
-- The bijection's "left inverse" half: from-index recovers the
-- original nimi after going through index. 32 cases of refl —
-- mechanical per [[feedback-expose-generator-not-orbit]] applied
-- in reverse (the bijection IS the gauge, no clever proof exists).
-- T8 (LinearAlgebra) consumes this to lift Fin-indexed extension
-- properties to Nimi-indexed ones.
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (_≡_; refl)

from-index∘index : (n : Nimi) → nimi-from-index (nimi-index n) ≡ n
from-index∘index jan      = refl
from-index∘index soweli   = refl
from-index∘index kili     = refl
from-index∘index moku     = refl
from-index∘index tomo     = refl
from-index∘index ma       = refl
from-index∘index telo     = refl
from-index∘index ilo      = refl
from-index∘index ijo      = refl
from-index∘index pona     = refl
from-index∘index ike      = refl
from-index∘index suli     = refl
from-index∘index lili     = refl
from-index∘index wawa     = refl
from-index∘index sin      = refl
from-index∘index toki     = refl
from-index∘index olin     = refl
from-index∘index pana     = refl
from-index∘index mi       = refl
from-index∘index sina     = refl
from-index∘index ona      = refl
from-index∘index ni       = refl
from-index∘index li-p     = refl
from-index∘index e-p      = refl
from-index∘index pi-p     = refl
from-index∘index la-p     = refl
from-index∘index o-p      = refl
from-index∘index en       = refl
from-index∘index tan      = refl
from-index∘index tawa     = refl
from-index∘index lon      = refl
from-index∘index kepeken  = refl

------------------------------------------------------------------------
-- 3. FreeLinearization instantiation: parametric in target dimension
-- and per-nimi image vector.
--
-- Given any semantic-image map `image : Nimi → SemVec m`, T3
-- produces the unique linear extension via the substrate's
-- free-linearize constructor. WithTarget exposes:
--   * `extension`   — the unique Linear nimi-count m
--   * The Linear's underlying apply function
--   * The basis-agreement and uniqueness witnesses (via the
--     FreeLinearization record).
------------------------------------------------------------------------

module WithTarget {m : ℕ} (image : Nimi → SemVec m) where

  fin-image : Fin nimi-count → SemVec m
  fin-image i = image (nimi-from-index i)

  free-record : FreeLinearization nimi-count m
  free-record = free-linearize fin-image

  open FreeLinearization free-record public
    using (extension; extension-on-basis; uniqueness)

------------------------------------------------------------------------
-- 4. The canonical instance: one-hot identity FreeLinearization.
--
-- Using image = nimi-as-vector gives the identity-like extension
-- (basis i ↦ basis i). Used by T9 as the default semantic universe
-- for worked examples.
------------------------------------------------------------------------

open WithTarget {m = nimi-count} nimi-as-vector public
  renaming ( extension          to nimi-extension
           ; extension-on-basis to nimi-extension-basis
           ; uniqueness         to nimi-extension-uniqueness
           )
