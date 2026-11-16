------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.ShapeLicenses
--
-- Defines: ShapeLicenses
--
-- P8 — "The thesis of the repo is 'same shape fits purpose of same shape,
-- and it's not a coincidence'.  Still dedupable."
--
-- ⚑ THIS IS NOT EVIDENCE FOR DEDUPABILITY.  IT IS THE EQUALITY ALONG
-- WHICH THE COLLAPSE IS LICENSED.  The operator said it to overrule a
-- verdict of mine: I had found four `Tm` declarations with differing
-- shape hashes and concluded "different type, different purpose, so these
-- are renames, not dedupes."  That was called LLM skittishness, and
-- correctly — the thesis is that same-shape-same-purpose is not a
-- coincidence, so "they were written for different purposes" is not a
-- defence against a shape identity.
--
-- ⚑ AND THE TERM THAT SAYS SO IS `deterministic` (Maps.agda:43):
--     (a : A) (b b' : B) → R a b → R a b' → b ≡ b'
-- Same input, two outputs, they are equal.  A shape function is a
-- relation from definitions to shapes; requiring it deterministic says
-- exactly that two definitions of the same shape ARE the same.  So "same
-- shape is the proof" is not a slogan — it is a determinism claim, and
-- `det→incl` (Mono.agda:84) gives its point-free form `(f† ⨾ f) ⊆ idR`.
--
-- ⚑⚑ SO A SHAPE DIFFERENCE IS A FACT ABOUT THE FUNCTION, NOT A VERDICT.
-- If same-shape is the licensing equality, a REAL shape difference means
-- genuinely distinct definitions — but a shape difference that is an
-- artifact of a defective shape function is a MISSING licence, not an
-- absent one.  Measured: ⟦533ef80d⟧ read as evidence of difference across
-- a `Tm` group until the π-typing defect in `_agdatext.shape_decls` was
-- fixed (a declaration is a family of constructors, each a Π-type;
-- `S K I : Tm` is telescope sugar for three of them), after which the
-- shapes agreed.  The hash was not deterministic yet.  Each such defect
-- found is a determinism repair, which is why the shape function is a
-- CONSTRUCTION UNDER REPAIR and not a classifier.
--
-- ⟡policy-allegory: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.ShapeLicenses where

open import Substrate.Category.Allegory.Maps
open import Substrate.Category.Allegory.Policy.Corpus


-- `shape` relates a definition site to its shape.  The policy is that
-- this relation is deterministic: it licenses deduplication exactly when
-- it cannot send one definition to two shapes.  An `entire` shape
-- function would additionally say every definition HAS a shape; that is a
-- stronger claim than the policy needs and is deliberately not required
-- here — a definition whose shape is not yet computable is unmeasured,
-- not distinct.
ShapeLicenses : {Site Shape : Set} → Corpus Site
              → (Site → Shape → Set) → Set
ShapeLicenses _ shape = deterministic shape
