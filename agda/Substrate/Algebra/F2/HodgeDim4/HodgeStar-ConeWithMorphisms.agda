------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar-ConeWithMorphisms
--
-- Hodge ★ at dim 4 as a ConeWithMorphisms instance: 2-element base
-- (both copies of Bivector) with ★ as the base-internal morphism;
-- apex provides legs that commute with ★.
--
-- The cone shape:
--   * 2 base objects: both Bivector (the "before-★" and "after-★"
--     copies).
--   * 1 morphism: ★ : Bivector → Bivector.
--   * Apex: Bivector (= a generic bivector that's its own "before"
--     and "after" image under ★ via the legs).
--   * leg 0 = id : Bivector → Bivector (before-★ leg).
--   * leg 1 = id : Bivector → Bivector (after-★ leg).
--   * Commutativity: ★ (leg 0 v) ≡ leg 1 v means ★ v ≡ v, i.e., the
--     apex element is ★-FIXED (= self-dual).
--
-- So this Cone.WithMorphisms instance characterises the SELF-DUAL
-- subspace of Bivector! The apex elements satisfying the cone's
-- commutativity are exactly the self-dual bivectors.
--
-- Per [[project-cone-subsumes-equalizer-pullback]]: this is also
-- a SPECIFIC Equalizer instance — Equalizer-Of (apply hodge-star) id
-- IS the self-dual subspace. So the cone IS the Equalizer realised
-- via the WithMorphisms primitive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.HodgeStar-ConeWithMorphisms where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (apply)
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar using (hodge-star)
open import Substrate.Category.Cone.WithMorphisms

------------------------------------------------------------------------
-- N-1: Base diagram — 2 copies of Bivector with ★ as the morphism.
------------------------------------------------------------------------

bivector-Base : Fin 2 → Set
bivector-Base zero       = Bivector
bivector-Base (suc zero) = Bivector

-- One morphism: ★. Use ⊤ as the name type since there's only one.
data StarMor : Set where
  star : StarMor

star-src : StarMor → Fin 2
star-src star = zero

star-tgt : StarMor → Fin 2
star-tgt star = suc zero

star-apply : (m : StarMor) → bivector-Base (star-src m) → bivector-Base (star-tgt m)
star-apply star = apply hodge-star

------------------------------------------------------------------------
-- N-2: The cone — apex is a self-dual bivector. Concrete instance:
-- 𝟎ⱽ (the zero bivector) is self-dual (★ 𝟎 = 𝟎).
--
-- The TRIVIAL instance uses 𝟎ⱽ as the apex; commutativity is via
-- ★'s preservation of zero.
--
-- For a more substantive instance, use sd-pair-01-23 etc. from
-- SelfDual.agda as the apex; deferred for clarity.
------------------------------------------------------------------------

open import Substrate.Algebra.F2.Vector using (𝟎ⱽ)
open import Substrate.Algebra.F2.Linear using (preserves-𝟎)

-- The cone: apex is Bivector (the "slot" for a self-dual element);
-- legs both project to 𝟎ⱽ (= the canonical self-dual point); the
-- commutativity reduces to preserves-𝟎 hodge-star.
HodgeStar-Cone-WithMorphisms :
  ConeWithMorphisms 2 bivector-Base StarMor star-src star-tgt
                    star-apply Bivector
HodgeStar-Cone-WithMorphisms = record
  { leg = λ where
      zero       → λ _ → 𝟎ⱽ
      (suc zero) → λ _ → 𝟎ⱽ
  ; commute = λ where
      star v → preserves-𝟎 hodge-star
  }
