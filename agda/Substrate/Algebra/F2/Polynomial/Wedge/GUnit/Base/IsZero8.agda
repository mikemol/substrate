------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.IsZero8
--
-- Defines: is-zero8
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.IsZero8 where

open import Substrate.Foundation.Vec
open import Substrate.Foundation.Bool.Bool
-- ⚑ WAS `import Substrate.Algebra.F2 as F2` — retired barrel + banned alias.
open import Substrate.Algebra.F2.F2



is-zero8 : Vec F₂ 8 → Bool
is-zero8 (𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []) = true
is-zero8 _ = false
