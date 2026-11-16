------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.MLo
--
-- Defines: m-lo
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base.MLo where

open import Substrate.Foundation.Vec
-- ⚑ WAS `import Substrate.Algebra.F2 as F2` — retired barrel + banned alias.
open import Substrate.Algebra.F2.F2



-- AES modulus low part: b-poly = x^8 +F x^4+x^3+x+1.
m-lo : Vec F₂ 8
m-lo = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []
