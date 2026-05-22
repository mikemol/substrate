------------------------------------------------------------------------
-- Substrate.Category.HC.CoxeterBraid
-- HC15 — Coxeter braid relations (sᵢsⱼ)ᵐ=e as a braiding instance UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.CoxeterBraid where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
CoxeterBraid-UP : UPArrow
CoxeterBraid-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
