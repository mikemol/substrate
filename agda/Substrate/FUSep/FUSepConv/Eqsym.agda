------------------------------------------------------------------------
-- Substrate.FUSep.FUSepConv.Eqsym
--
-- Defines: ≡sym
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepConv; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepConv.Eqsym where

open import Substrate.Foundation.Eq



-- ≡ helpers, local
≡sym : {A : Set} {x y : A} → x ≡ y → y ≡ x
≡sym refl = refl
