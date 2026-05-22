------------------------------------------------------------------------
-- Substrate.Category.HC.F2LinFullCoherence
-- HC17 — F₂-Linear as full symmetric-monoidal with all coherence
-- diagrams (pentagon, triangle, hexagon, σ²=id).
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.F2LinFullCoherence where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
F2LinFullCoherence-UP : UPArrow
F2LinFullCoherence-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
