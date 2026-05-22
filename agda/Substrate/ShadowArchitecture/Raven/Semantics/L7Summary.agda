------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics.L7Summary
--
-- L₇-population-summary: the phase-transition theorem at the Cotype
-- level, as a conjunction over the 19 snapshots.
--
-- "L₇ is unpopulated at exactly c0..c7 and populated from c8 onward."
-- That c7→c8 is the populate-line-monotone step (not ⊑-refl) is the
-- witness that the lockup HAPPENS HERE and nowhere earlier.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics.L7Summary where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.ShadowArchitecture.FanoLabeling using (L₇)
open import Substrate.ShadowArchitecture.Persistence using (Cotype)
open import Substrate.ShadowArchitecture.Raven.Semantics.Cotypes
open import Substrate.ShadowArchitecture.Raven.Semantics.L7Population

L₇-population-summary :
    -- pre-lockup
    (Cotype.populated-line c0 L₇ ≡ false) ×
    (Cotype.populated-line c1 L₇ ≡ false) ×
    (Cotype.populated-line c2 L₇ ≡ false) ×
    (Cotype.populated-line c3 L₇ ≡ false) ×
    (Cotype.populated-line c4 L₇ ≡ false) ×
    (Cotype.populated-line c5 L₇ ≡ false) ×
    (Cotype.populated-line c6 L₇ ≡ false) ×
    (Cotype.populated-line c7 L₇ ≡ false) ×
    -- post-lockup
    (Cotype.populated-line c8  L₇ ≡ true) ×
    (Cotype.populated-line c9  L₇ ≡ true) ×
    (Cotype.populated-line c10 L₇ ≡ true) ×
    (Cotype.populated-line c11 L₇ ≡ true) ×
    (Cotype.populated-line c12 L₇ ≡ true) ×
    (Cotype.populated-line c13 L₇ ≡ true) ×
    (Cotype.populated-line c14 L₇ ≡ true) ×
    (Cotype.populated-line c15 L₇ ≡ true) ×
    (Cotype.populated-line c16 L₇ ≡ true) ×
    (Cotype.populated-line c17 L₇ ≡ true) ×
    (Cotype.populated-line c18 L₇ ≡ true)
L₇-population-summary =
    L₇-c0  , L₇-c1  , L₇-c2  , L₇-c3  , L₇-c4
  , L₇-c5  , L₇-c6  , L₇-c7
  , L₇-c8  , L₇-c9  , L₇-c10 , L₇-c11 , L₇-c12
  , L₇-c13 , L₇-c14 , L₇-c15 , L₇-c16 , L₇-c17 , L₇-c18
