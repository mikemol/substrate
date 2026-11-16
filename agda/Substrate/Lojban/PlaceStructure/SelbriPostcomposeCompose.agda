------------------------------------------------------------------------
-- Substrate.Lojban.PlaceStructure.SelbriPostcomposeCompose
--
-- Defines: selbri-postcompose-compose
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.PlaceStructure; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.PlaceStructure.SelbriPostcomposeCompose where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Lojban.PlaceStructure.Private
open import Substrate.Lojban.PlaceStructure.Selbri
open import Substrate.Lojban.PlaceStructure.SelbriPostcompose
open import Substrate.Lojban.Fragment.Carriers
open import Substrate.Lojban.Bridi



------------------------------------------------------------------------
-- 4. Composition preservation (pointwise).
--
-- Post-composing with (g ∘ f) factors through post-composing with f
-- then with g. Together with §3 this is the functor-law obligation
-- that L7 discharges at the coherent level.
------------------------------------------------------------------------

selbri-postcompose-compose :
  {Sumti : Set ℓA} {Sem : Set ℓB} {Sem' : Set ℓC} {Sem'' : Set ℓD} →
  (f : Sem → Sem') (g : Sem' → Sem'') →
  (S : Selbri n Sumti Sem) →
  (args : Vec Sumti n) →
  apply (selbri-postcompose (λ x → g (f x)) S) args
    ≡ apply (selbri-postcompose g (selbri-postcompose f S)) args
selbri-postcompose-compose _ _ _ _ = refl
