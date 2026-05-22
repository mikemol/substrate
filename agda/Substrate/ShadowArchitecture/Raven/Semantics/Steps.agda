------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics.Steps
--
-- The 18 adjacent-step monotonicity witnesses cₙ ⊑ cₙ₊₁. Each step
-- is justified by either ⊑-refl (interpret is identity — terminal is
-- awen-taso or other-attr) or populate-line-monotone (interpret is
-- populate-line L₇).
--
-- The c7→c8 transition is the SINGLE non-identity step on the L₇
-- axis (the "lockup"). Subsequent populate-line steps at c10, c13–c18
-- are idempotent re-populations and remain monotonic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics.Steps where

open import Substrate.ShadowArchitecture.FanoLabeling using (L₇)
open import Substrate.ShadowArchitecture.Persistence
  using (_⊑_; ⊑-refl; populate-line-monotone)
open import Substrate.ShadowArchitecture.Raven.Semantics.Cotypes

step-c0-to-c1   : c0  ⊑ c1
step-c0-to-c1   = ⊑-refl c0
step-c1-to-c2   : c1  ⊑ c2
step-c1-to-c2   = ⊑-refl c1
step-c2-to-c3   : c2  ⊑ c3
step-c2-to-c3   = ⊑-refl c2
step-c3-to-c4   : c3  ⊑ c4
step-c3-to-c4   = ⊑-refl c3
step-c4-to-c5   : c4  ⊑ c5
step-c4-to-c5   = ⊑-refl c4
step-c5-to-c6   : c5  ⊑ c6
step-c5-to-c6   = ⊑-refl c5
step-c6-to-c7   : c6  ⊑ c7
step-c6-to-c7   = ⊑-refl c6

-- ★ The lockup step. c8 = populate-line L₇ c7. Non-identity.
step-c7-to-c8   : c7  ⊑ c8
step-c7-to-c8   = populate-line-monotone L₇ c7

step-c8-to-c9   : c8  ⊑ c9
step-c8-to-c9   = ⊑-refl c8
step-c9-to-c10  : c9  ⊑ c10
step-c9-to-c10  = populate-line-monotone L₇ c9
step-c10-to-c11 : c10 ⊑ c11
step-c10-to-c11 = ⊑-refl c10
step-c11-to-c12 : c11 ⊑ c12
step-c11-to-c12 = ⊑-refl c11
step-c12-to-c13 : c12 ⊑ c13
step-c12-to-c13 = populate-line-monotone L₇ c12
step-c13-to-c14 : c13 ⊑ c14
step-c13-to-c14 = populate-line-monotone L₇ c13
step-c14-to-c15 : c14 ⊑ c15
step-c14-to-c15 = populate-line-monotone L₇ c14
step-c15-to-c16 : c15 ⊑ c16
step-c15-to-c16 = populate-line-monotone L₇ c15
step-c16-to-c17 : c16 ⊑ c17
step-c16-to-c17 = populate-line-monotone L₇ c16
step-c17-to-c18 : c17 ⊑ c18
step-c17-to-c18 = populate-line-monotone L₇ c17
