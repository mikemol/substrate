------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.Corpus
--
-- Defines: Corpus
-- The carrier the repo's Agda-code policies are relations OVER: a corpus
-- is a type of definition-sites, nothing more.  Two sites, one relation
-- between them — that is the whole shape a policy has.
--
-- ⚑ THIS IS A PARAMETER, NOT A FIELD, and that is the difference between
-- Set₀ and Set₁ (set1-carrier-always-parameterize).  A record HOLDING a
-- `Site : Set` would pin every policy at `Set (lsuc _)`; a record taking
-- it threads the caller's level through and contributes none of its own.
-- The measured instance is Rel-Allegory, deleted for exactly this: its
-- `Obj := Set` / `Hom := A → B → Set` instantiation was the Set₁ source,
-- while the RECORD was already parameterized.  Debt relocates to the
-- instantiation site; it does not evaporate.
--
-- ⟡policy-allegory: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.Corpus where


-- A corpus is presented by its site type.  `Site` is what a definition
-- IS for the purpose of the policies: a name together with wherever it
-- lives.  Nothing about splitting, deduplication or naming needs more
-- structure than this, which is why the record has no fields — every
-- policy below is a RELATION on Site, supplied by the consumer.
record Corpus (Site : Set) : Set where
  constructor mkCorpus
