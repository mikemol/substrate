------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics.FullChain
--
-- full-chain-c0-to-c18 : c0 ⊑ c18.
-- Built by repeated ⊑-trans over the 18 adjacent step lemmas.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics.FullChain where

open import Substrate.ShadowArchitecture.Persistence using (_⊑_; ⊑-trans)
open import Substrate.ShadowArchitecture.Raven.Semantics.Cotypes
open import Substrate.ShadowArchitecture.Raven.Semantics.Steps

full-chain-c0-to-c18 : c0 ⊑ c18
full-chain-c0-to-c18 =
  ⊑-trans c0 c1  c18 step-c0-to-c1   (
  ⊑-trans c1 c2  c18 step-c1-to-c2   (
  ⊑-trans c2 c3  c18 step-c2-to-c3   (
  ⊑-trans c3 c4  c18 step-c3-to-c4   (
  ⊑-trans c4 c5  c18 step-c4-to-c5   (
  ⊑-trans c5 c6  c18 step-c5-to-c6   (
  ⊑-trans c6 c7  c18 step-c6-to-c7   (
  ⊑-trans c7 c8  c18 step-c7-to-c8   (
  ⊑-trans c8 c9  c18 step-c8-to-c9   (
  ⊑-trans c9 c10 c18 step-c9-to-c10  (
  ⊑-trans c10 c11 c18 step-c10-to-c11 (
  ⊑-trans c11 c12 c18 step-c11-to-c12 (
  ⊑-trans c12 c13 c18 step-c12-to-c13 (
  ⊑-trans c13 c14 c18 step-c13-to-c14 (
  ⊑-trans c14 c15 c18 step-c14-to-c15 (
  ⊑-trans c15 c16 c18 step-c15-to-c16 (
  ⊑-trans c16 c17 c18 step-c16-to-c17
    step-c17-to-c18))))))))))))))))
