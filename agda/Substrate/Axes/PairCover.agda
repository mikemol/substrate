------------------------------------------------------------------------
-- Substrate.Axes.PairCover
--
-- Sixteen-case cover over Axis × Axis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.PairCover where

open import Substrate.Foundation.Product using (_×_)
open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Axes.Cover using (axis-cover)

axis×axis-cover :
  ∀ {ℓ} (P : Axis → Axis → Set ℓ) →
  (P D D × P D C × P D S × P D W) ×
  (P C D × P C C × P C S × P C W) ×
  (P S D × P S C × P S S × P S W) ×
  (P W D × P W C × P W S × P W W) →
  ∀ a x → P a x
axis×axis-cover P rows a x =
  axis-cover (P a)
    (axis-cover (λ a' → P a' D × P a' C × P a' S × P a' W) rows a)
    x
