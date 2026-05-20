------------------------------------------------------------------------
-- Eliza.Router
--
-- Stateless transducer Char → Gen. The current Python implementation
-- is `ord(ch) % 3`, a content-blind 3-way partition. The skeleton
-- abstracts this as ANY function Char → Gen — the per-instance choice
-- is a gauge selection.
--
-- Per Substrate.Discipline Rule 1 (gauge-versus-invariant separation):
-- the specific routing function is a GAUGE. The Engine's
-- gauge-invariant outputs (orbit-level statistics, grammar at the
-- orbit level) must not depend on which routing function is chosen —
-- that's the entailment claim this module's interface commits to,
-- spelled out in `route-is-gauge`.
--
-- The proposed `class-level router` (vowel/consonant/punct) per
-- inspiration #5 from the agda/Substrate read is just another
-- instantiation of this interface; the skeleton accommodates both.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Router where

open import Eliza.Prelude    using (_≡_)
open import Eliza.Alphabets  using (Char; Gen)
open import Eliza.Transducer using (Transducer; run)
open import Eliza.Word       using (Word)

------------------------------------------------------------------------
-- 1. The Router interface. Any concrete router is an inhabitant of
-- `Router` — the skeleton does not pick.
------------------------------------------------------------------------

Router : Set
Router = Transducer Char Gen

------------------------------------------------------------------------
-- 2. Two canonical instantiations, both postulated (the Char type is
-- abstract in the skeleton, so we cannot define them constructively):
--
--   * ord-mod-3: the current router. Each Char's codepoint mod 3.
--   * class-router: vowel/consonant/other → s₁/s₂/s₃. The proposed
--     class-level router from the agda/Substrate inspiration list.
------------------------------------------------------------------------

postulate
  ord-mod-3   : Router
  class-router : Router

------------------------------------------------------------------------
-- 3. Lifting to Word. Routes a Word Char to a Word Gen.
------------------------------------------------------------------------

route : Router → Word Char → Word Gen
route = run

------------------------------------------------------------------------
-- 4. The gauge claim — postulated as the Engine's obligation.
--
-- Any function whose contract speaks only of orbit-level statistics
-- must be insensitive to the choice between two routers, AS LONG AS
-- the two routers are V₄-equivariant (i.e., they induce the same
-- partition of Char up to V₄-orbit of generators). This is the
-- Rule-5 lift from Discipline.agda specialised to the routing layer.
--
-- Stated as a postulate here; proved (or refuted) downstream when
-- specific routers are formalised against specific Engine outputs.
------------------------------------------------------------------------

postulate
  route-is-gauge :
    {A : Set}
    (downstream-orbit-statistic : Word Gen → A)
    (r₁ r₂ : Router) →
    -- (V₄-equivariance premise, elided) →
    (w : Word Char) →
    downstream-orbit-statistic (route r₁ w) ≡
    downstream-orbit-statistic (route r₂ w)
