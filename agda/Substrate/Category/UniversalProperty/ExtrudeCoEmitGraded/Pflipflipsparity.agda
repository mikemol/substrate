------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipflipsparity
--
-- Defines: pflip-flips-parity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflipflipsparity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.N-to-F2-Parity
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flip
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.F2flipinvolutive
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Pflip
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- and pflip FLIPS THE CHIRALITY BIT (parity): parity (pflip n) ≡ f2-flip (parity n) — the stepwise action (350).
pflip-flips-parity : (n : ℕ) → parity (pflip n) ≡ f2-flip (parity n)
pflip-flips-parity zero          = refl
pflip-flips-parity (suc zero)    = refl
pflip-flips-parity (suc (suc n)) =
  -- parity (pflip (n+2)) = 𝟙⊕(𝟙⊕ parity (pflip n)) ≡ parity (pflip n)  [the x⊕x=𝟘 cancellation]
  -- and f2-flip (parity (n+2)) = f2-flip (𝟙⊕(𝟙⊕ parity n)) ≡ f2-flip (parity n).
  trans (f2-flip-involutive (parity (pflip n)))
        (trans (pflip-flips-parity n)
               (sym (cong f2-flip (f2-flip-involutive (parity n)))))
