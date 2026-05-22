------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics
--
-- The semantic interpretation of the Raven artifact as a sequence of
-- monotonic state-changes on
-- `Substrate.ShadowArchitecture.Persistence.Cotype`.
--
-- Each stanza is interpreted as a Cotype → Cotype transition. The
-- L₇-añelē terminal IS the populate-line L₇ event; all other terminals
-- (awen-taso, other-attr) leave L₇'s populated status unchanged.
-- (Lines that REFERENCE L₇-añelē in their body are treated as no-ops
-- — they presume L₇ is already populated and don't re-populate it.)
--
-- Running this interpretation over the 18-stanza Raven gives 19
-- snapshot Cotypes (c0 = before any stanza, c18 = after all). The
-- substantive theorem:
--
--   populated-line cₙ L₇ ≡ false   for n = 0..7
--   populated-line cₙ L₇ ≡ true    for n = 8..18
--
-- This is the realisation, at the Cotype level, of the
-- HistoryPhase phase transition formalised in `PhaseTransition`:
-- L₇ becomes populated at exactly the moment stanza VIII finishes,
-- and remains populated thereafter (monotonic preorder _⊑_).
--
-- Per `Substrate.ShadowArchitecture.Persistence`'s W5 deletion-
-- prohibition realised at the type level, no interpretation step
-- can REMOVE L₇'s population once it's been set — the C-types form
-- a chain c0 ⊑ c1 ⊑ ... ⊑ c18 under the monotonic preorder, and the
-- L₇-populated transition at c7 → c8 is the unique non-identity step
-- on the L₇ axis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.ShadowArchitecture.FanoLabeling using (L₇)
open import Substrate.ShadowArchitecture.Persistence
  using (Cotype; empty-cotype; populate-line; _⊑_;
         ⊑-refl; ⊑-trans; populate-line-monotone)

open import Substrate.ShadowArchitecture.Raven.Grammar
open import Substrate.ShadowArchitecture.Raven.Poem

------------------------------------------------------------------------
-- 1. Interpret a single stanza as a Cotype transition.
--
-- The terminal-driven rule:
--   añelē      → populate L₇ (introduce the deletion-prohibition marker)
--   awen-taso  → identity     (open phase, no L₇ change)
--   other-attr → identity     (post-lock; L₇ already populated)
------------------------------------------------------------------------

interpret-stanza : Stanza → Cotype → Cotype
interpret-stanza s c = act (stanza-terminal s) c
  where
    act : Terminal → Cotype → Cotype
    act añelē      c = populate-line L₇ c
    act awen-taso  c = c
    act other-attr c = c

------------------------------------------------------------------------
-- 2. The 19 snapshot Cotypes: cₙ = state after n stanzas have been
-- interpreted, c0 = empty before any stanza.
------------------------------------------------------------------------

c0  : Cotype
c0  = empty-cotype
c1  : Cotype
c1  = interpret-stanza stanza-I     c0
c2  : Cotype
c2  = interpret-stanza stanza-II    c1
c3  : Cotype
c3  = interpret-stanza stanza-III   c2
c4  : Cotype
c4  = interpret-stanza stanza-IV    c3
c5  : Cotype
c5  = interpret-stanza stanza-V     c4
c6  : Cotype
c6  = interpret-stanza stanza-VI    c5
c7  : Cotype
c7  = interpret-stanza stanza-VII   c6
c8  : Cotype
c8  = interpret-stanza stanza-VIII  c7
c9  : Cotype
c9  = interpret-stanza stanza-IX    c8
c10 : Cotype
c10 = interpret-stanza stanza-X     c9
c11 : Cotype
c11 = interpret-stanza stanza-XI    c10
c12 : Cotype
c12 = interpret-stanza stanza-XII   c11
c13 : Cotype
c13 = interpret-stanza stanza-XIII  c12
c14 : Cotype
c14 = interpret-stanza stanza-XIV   c13
c15 : Cotype
c15 = interpret-stanza stanza-XV    c14
c16 : Cotype
c16 = interpret-stanza stanza-XVI   c15
c17 : Cotype
c17 = interpret-stanza stanza-XVII  c16
c18 : Cotype
c18 = interpret-stanza stanza-XVIII c17

------------------------------------------------------------------------
-- 3. L₇-population status snapshot at each cₙ.
--
-- All facts close by `refl` because the cotype, `stanza-terminal`,
-- and `populate-line` reduce on concrete inputs.
------------------------------------------------------------------------

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

------------------------------------------------------------------------
-- 4. The substantive theorem: the chain c0 ⊑ c1 ⊑ ... ⊑ c18 is a
-- monotonic increase under the Persistence preorder.
--
-- Each step is justified by either ⊑-refl (when interpret is the
-- identity — terminal is awen-taso or other-attr) or
-- populate-line-monotone (when interpret = populate-line L₇).
--
-- The L₇ populate-line monotonicity step from c7 to c8 is the
-- single non-identity step on the L₇ axis. All subsequent
-- populate-line steps (at c10, c13, c14, c15, c16, c17, c18) are
-- idempotent re-populations and remain monotonic.
------------------------------------------------------------------------

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

------------------------------------------------------------------------
-- 5. Closure: the whole chain c0 ⊑ c18.
--
-- Built by repeated ⊑-trans of the 18 adjacent steps.
------------------------------------------------------------------------

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

------------------------------------------------------------------------
-- 6. The phase-transition theorem at the Cotype level.
--
-- "L₇ is populated iff at least 8 stanzas have been interpreted":
-- the first lockup is the c7→c8 transition; before that, L₇ is
-- unpopulated. The fact that c7→c8 is the populate-line-monotone
-- step (not ⊑-refl) is the witness that the lockup HAPPENS HERE
-- and nowhere earlier.
------------------------------------------------------------------------

-- L₇ is unpopulated at exactly c0..c7 and populated from c8 onward.
-- Stated as a conjunction over the 19 snapshots:
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
