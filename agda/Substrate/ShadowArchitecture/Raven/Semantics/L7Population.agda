------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics.L7Population
--
-- L₇'s population status at each snapshot cₙ. All close by `refl`
-- because the cotype, `stanza-terminal`, and `populate-line` reduce
-- on concrete inputs.
--
-- Pre-lockup: c0..c7  → populated-line L₇ ≡ false
-- Post-lockup: c8..c18 → populated-line L₇ ≡ true
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics.L7Population where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.ShadowArchitecture.FanoLabeling using (L₇)
open import Substrate.ShadowArchitecture.Persistence using (Cotype)
open import Substrate.ShadowArchitecture.Raven.Semantics.Cotypes

L₇-c0  : Cotype.populated-line c0  L₇ ≡ false
L₇-c0  = refl
L₇-c1  : Cotype.populated-line c1  L₇ ≡ false
L₇-c1  = refl
L₇-c2  : Cotype.populated-line c2  L₇ ≡ false
L₇-c2  = refl
L₇-c3  : Cotype.populated-line c3  L₇ ≡ false
L₇-c3  = refl
L₇-c4  : Cotype.populated-line c4  L₇ ≡ false
L₇-c4  = refl
L₇-c5  : Cotype.populated-line c5  L₇ ≡ false
L₇-c5  = refl
L₇-c6  : Cotype.populated-line c6  L₇ ≡ false
L₇-c6  = refl
L₇-c7  : Cotype.populated-line c7  L₇ ≡ false
L₇-c7  = refl

-- ★ Phase transition: L₇ becomes populated at c8.
L₇-c8  : Cotype.populated-line c8  L₇ ≡ true
L₇-c8  = refl

L₇-c9  : Cotype.populated-line c9  L₇ ≡ true
L₇-c9  = refl
L₇-c10 : Cotype.populated-line c10 L₇ ≡ true
L₇-c10 = refl
L₇-c11 : Cotype.populated-line c11 L₇ ≡ true
L₇-c11 = refl
L₇-c12 : Cotype.populated-line c12 L₇ ≡ true
L₇-c12 = refl
L₇-c13 : Cotype.populated-line c13 L₇ ≡ true
L₇-c13 = refl
L₇-c14 : Cotype.populated-line c14 L₇ ≡ true
L₇-c14 = refl
L₇-c15 : Cotype.populated-line c15 L₇ ≡ true
L₇-c15 = refl
L₇-c16 : Cotype.populated-line c16 L₇ ≡ true
L₇-c16 = refl
L₇-c17 : Cotype.populated-line c17 L₇ ≡ true
L₇-c17 = refl
L₇-c18 : Cotype.populated-line c18 L₇ ≡ true
L₇-c18 = refl
