------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.BisimComplete
--
-- Defines: bisim-complete
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.BisimComplete where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Category.UniversalProperty.ExtrudeIOCostream
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
private variable O : Set
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Approx
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.TakeCong
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Hd
open import Substrate.Category.UniversalProperty.ExtrudeIOCostreamBisim.Tl



bisim-complete : {c d : CoIO O} → ((n : ℕ) → take-coio n c ≡ take-coio n d) → c ≈ᶜ d
head≈ (bisim-complete {c = c} {d = d} f) =
  -- take-coio 1 c = emit-head c ∷ [] ; extract the head from f 1:
  cong (hd (emit-head c)) (f 1)
rest≈ (bisim-complete {c = c} {d = d} f) =
  bisim-complete (λ n → cong tl (f (suc n)))   -- prefixes of the rests agree, from f (suc n)

------------------------------------------------------------------------
------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — bisimilarity is the observational equality of the unbounded emit; sound for
-- every finite prefix; NOT a total DecEq): CoIO (289) is the unbounded emit; its equality is BISIMILARITY (①,
-- _≈ᶜ_ — same head, bisimilar rest, coinductive), an equivalence (②), sound for finite observation (③,
-- take-cong: bisimilar ⟹ equal prefixes). This is the coinductive equality (D-no-classical-spook: NOT total
-- DecEq — the costream is infinite; per-step observation + the coinductive limit). Small, no funext/Set₁/
-- levels/postulate. The emit-side's unbounded equality, matching the run-side's bisimilarity (278). Chain: 289
-- (CoIO) → 290c (its bisimilarity).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = _≈ᶜ_ + the equivalence + take-cong (finite-prefix soundness).
-- SCOPED: completeness (equal-on-all-prefixes ⟹ bisimilar — the coinductive limit, ⟡extrude-coio-bisim-
-- complete). What's grounded: the observational equality of the unbounded emit, sound for observation, small.
------------------------------------------------------------------------
