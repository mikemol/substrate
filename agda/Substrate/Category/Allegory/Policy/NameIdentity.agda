------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.NameIdentity
--
-- Defines: NameIdentity
--
-- POLICIES P1-P5 ARE ONE POLICY, and this is the term that says so.
-- The operator states them separately —
--
--   P1  "We delete all barrels.  Barrels are re-exports, which are banned."
--   P2  "I believe I have a ban on `private`, too.  Basically, I dislike
--        anything that munges with namespaces and visibility."
--   P3  "We have a ban on `public` anyway"
--   P4  ⟡ban-decompose: no using / renaming / hiding / as on Substrate imports
--   P5  "A collision IS a misnaming once you consider the entire repo as a
--        single namespace.  That's WHY we rename-at-source."
--
-- — but every banned construct breaks ONE law: the name a consumer writes
-- must be the name the definition carries.  `renaming` relabels it, `as`
-- re-prefixes it, `using`/`hiding` restrict which names arrive, `public`
-- re-sites a name to a module that did not define it, and `private`
-- withholds one that exists.  Five bans because Agda offers five ways to
-- break the same identity, not five policies.
--
-- ⚑ AND P5 IS THE REPAIR, NOT A SIBLING.  When two definitions collide,
-- the ban forbids inserting a filter — a filter is another non-identity
-- arrow.  You move the DEFINITION so the identity holds again.  That is
-- exactly the operator's reading: a collision is already a misnaming, so
-- rename-at-source restores a law rather than working around a clash.
--
-- ⚑ THE ORDER IS THE POLICY, and it is `_⊆_` — Allegory.agda:50, the
-- PRIMITIVE pointwise implication of fibers, declared at Step 0 before
-- composition and meet.  `use ⊆ def` reads: every name arriving at a use
-- site is implied by the definition site.  No coreflexive machinery is
-- needed (and none exists in this tree — searched `coreflexive`,
-- `partial-id`, `subidentity`, `domain`; the word occurs only in prose,
-- describing other things).  The order the allegory already has IS the
-- policy.
--
-- ⟡policy-allegory: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.NameIdentity where

open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Policy.Corpus


-- `use` relates a site to the names visible there; `def` relates a site
-- to the names it defines.  The policy is that `use` is below `def` — a
-- use site introduces nothing its definition site does not carry.
--
-- Each banned construct is a witness of FAILURE: it makes `use` contain a
-- pair `def` does not, so the inclusion breaks and the module is out of
-- compliance.  Compliance is not "no directive appears in the text"; it
-- is this inclusion, which is what makes the policy checkable rather than
-- syntactic.
NameIdentity : {Site Name : Set} → Corpus Site
             → (Site → Name → Set) → (Site → Name → Set) → Set
NameIdentity _ use def = use ⊆ def
