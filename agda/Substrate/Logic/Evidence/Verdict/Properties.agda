------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Properties
--
-- The crossbar identities (el-atlas S4/S5): the rail-swap and the
-- verdict-level dual are involutions, and `verdict` INTERTWINES them —
-- the square
--
--        Evidence --verdict--> Verdict
--          |                     |
--        swapE                 swapV
--          v                     v
--        Evidence --verdict--> Verdict
--
-- commutes.  Every case holds by refl after δ-reduction through
-- `verdict`/`swapE`/`swapV`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Properties where

open import Substrate.Foundation.Bool using (true; false)
open import Substrate.Foundation.Eq   using (_≡_; refl)

open import Substrate.Logic.Evidence.Verdict

------------------------------------------------------------------------
-- S5: both swaps are involutions.
------------------------------------------------------------------------

swapE-involutive : (e : Evidence) → swapE (swapE e) ≡ e
swapE-involutive ⟨ p , n ⟩ = refl

swapV-involutive : (v : Verdict) → swapV (swapV v) ≡ v
swapV-involutive P = refl
swapV-involutive F = refl
swapV-involutive U = refl
swapV-involutive V = refl

------------------------------------------------------------------------
-- S4, the crossbar: verdict ∘ swapE ≡ swapV ∘ verdict (pointwise).
------------------------------------------------------------------------

intertwine : (e : Evidence) → verdict (swapE e) ≡ swapV (verdict e)
intertwine ⟨ true  , false ⟩ = refl
intertwine ⟨ false , true  ⟩ = refl
intertwine ⟨ true  , true  ⟩ = refl
intertwine ⟨ false , false ⟩ = refl
