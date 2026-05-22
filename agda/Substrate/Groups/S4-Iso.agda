------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso
--
-- The iso S4-Composed.Carrier ↔ Permutation Axis, bridging the
-- compositional construction (V₄ ⋊ S₃ via the Coxeter framework) and
-- the permutation-based representation (Sym(Axis)).
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]]: the
-- former 682-line module is now a thin re-export shim over eight
-- submodules in S4-Iso/.
--
-- Submodule decomposition:
--   S4-Iso.Embedding      — embed-S₃ + compositional-to-perm (forward).
--   S4-Iso.Extract        — extract-s + perm-to-compositional (backward).
--   S4-Iso.Foundation     — embed-S₃-ε, embed-S₃-hom, swap-relation.
--   S4-Iso.ForwardHom     — forward-hom (compositional-to-perm is a
--                            Group homomorphism).
--   S4-Iso.ExtractCorrect — extract-s-correct (full Stab(D)-side roundtrip).
--   S4-Iso.Roundtrip      — perm-roundtrip-≈, embed-as-N-injection +
--                            small permutation algebra helpers.
--   S4-Iso.IsoTransport   — forward-ε, embed-cong, embed-S₃-cong,
--                            compositional-to-perm-cong, forward-inv.
--   S4-Iso.V4Normal       — V₄-normal-compositional (V₄ ⊳ S₄ via iso).
--
-- All public names from the original file remain available via the
-- re-exports below; existing callers need no edits.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso where

open import Substrate.Groups.S4-Iso.Embedding      public
open import Substrate.Groups.S4-Iso.Extract        public
open import Substrate.Groups.S4-Iso.Foundation     public
open import Substrate.Groups.S4-Iso.ForwardHom     public
open import Substrate.Groups.S4-Iso.ExtractCorrect public
open import Substrate.Groups.S4-Iso.Roundtrip      public
open import Substrate.Groups.S4-Iso.IsoTransport   public
open import Substrate.Groups.S4-Iso.V4Normal       public
