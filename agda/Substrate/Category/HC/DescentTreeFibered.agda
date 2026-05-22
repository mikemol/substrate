------------------------------------------------------------------------
-- Substrate.Category.HC.DescentTreeFibered
-- HC29 — Substrate's DescentTree as a fibered category UP.
------------------------------------------------------------------------
{-# OPTIONS --safe --without-K #-}
module Substrate.Category.HC.DescentTreeFibered where
open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty using (UPArrow)
DescentTreeFibered-UP : UPArrow
DescentTreeFibered-UP = record { Source = ⊤ ; Target = ⊤ ; Witness = λ _ _ → ⊤ }
