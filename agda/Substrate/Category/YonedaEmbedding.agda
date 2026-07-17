------------------------------------------------------------------------
-- Substrate.Category.YonedaEmbedding
--
-- S6 of the S-arc. Yoneda embedding y : C ↪ [C^op, Set] sending
-- c ↦ Hom(_, c).
-- (Classically the Yoneda embedding is fully faithful; here `y` is a
-- supplied module parameter and full faithfulness is NOT proved —
-- prose.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.YonedaEmbedding where

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module _
  {ℓOC ℓMC ℓOP ℓMP : Level}
  {ObjC : Set ℓOC} {MorC : ObjC → ObjC → Set ℓMC}
  (C : CategoryOf ObjC MorC)
  {ObjPresheafCat : Set ℓOP} {MorPresheafCat : ObjPresheafCat → ObjPresheafCat → Set ℓMP}
  (PresheafCat : CategoryOf ObjPresheafCat MorPresheafCat)
  (y : Functor C PresheafCat)
  where

  Yoneda-Embedding : Functor C PresheafCat
  Yoneda-Embedding = y
