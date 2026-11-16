------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconj
--
-- Defines: coemit-stardivstr-conj
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitstardivstrconj where

open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


------------------------------------------------------------------------
-- (3) coemit-stardivstr: HONEST-PARTIAL, with a precise reason. StarDivStr.conj-conj demands Agda's INTENSIONAL
--     _≡_ : conj (conj x) ≡ x. On RealTrace the constructed ≡ IS ~ (351: the totality of the orbit's actions);
--     intensional ≡ on a coinductive carrier is not that construction (it would need funext/quotients — and
--     D-safe-no-postulate forbids postulating it). So the record as written does NOT admit RealTrace directly:
--     it wants a carrier whose Agda-≡ already IS the totality (a finite Vector, as Face is; or a quotient/setoid).
--     What coemit HAS is every component, with ~ in place of ≡ — i.e. the StarDivStr over the ~-setoid.
------------------------------------------------------------------------
-- the conjugation exists (bar) and is involutive in the CONSTRUCTED equality (~) — the StarDivStr data, ~-valued.
coemit-stardivstr-conj : RealTrace → RealTrace
coemit-stardivstr-conj = bar
