------------------------------------------------------------------------
-- Substrate.Axes.Cover
--
-- Four-case cover over Axis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.Cover where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Axes.Axis using (Axis; D; C; S; W)

axis-cover :
  ∀ {ℓ} (P : Axis → Set ℓ) →
  P D × P C × P S × P W →
  ∀ a → P a
axis-cover _ (p , _ , _ , _) D = p
axis-cover _ (_ , p , _ , _) C = p
axis-cover _ (_ , _ , p , _) S = p
axis-cover _ (_ , _ , _ , p) W = p
