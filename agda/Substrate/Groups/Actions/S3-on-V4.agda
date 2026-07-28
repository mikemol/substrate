------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4
--
-- The AGL action of S₃ on V₄: S₃ ≅ GL(V₄, F₂) ≅ Sym({α, β, γ}),
-- acting on V₄ as the natural permutation of nonzero elements (e fixed).
--
-- S₃ here is the compositional construction Z/3 ⋊ Z/2 from
-- Substrate.Groups.S3. Its 6 canonical elements correspond to the 6
-- permutations of {α, β, γ}.
--
-- DECOMPOSED 2026-05-21 per [[file-size-one-pass-rewrite]]: the
-- former 542-line module is now a thin re-export shim over six
-- submodules in S3-on-V4/.
--
-- Submodule decomposition:
--   S3-on-V4.Dispatch     — act-on-canonical + act (24-case dispatch).
--   S3-on-V4.HomRotations — hom-id, hom-rot, hom-rot² (3 × 16 refl).
--   S3-on-V4.HomSwaps     — hom-swap-{αβ,αγ,βγ} + act-hom-on-canonical
--                            + act-hom (3 × 16 refl + dispatch).
--   S3-on-V4.Axioms       — act-cong, act-ε, act-ε-N.
--   S3-on-V4.Generators   — rotate, swap-αβ, rot-pow, swap-pow,
--                            *-append, generator-order identities,
--                            *-normalize-eq.
--   S3-on-V4.Twist        — act-equals-pow, swap-rotate-twist,
--                            rot-pow-swap-twist.
--   S3-on-V4.Composition  — act-∙-canonical, act-∙ (per-block dispatch).
--
-- All public names from the original file remain available via the
-- re-exports below; existing callers (S4-Composed, etc.) need no edits.
--
-- Provides all 5 axioms for Substrate.Groups.Coxeter.SemidirectProductGroup,
-- enabling S₄ = V₄ ⋊ S₃ in Substrate.Groups.S4-Composed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4 where

open import Substrate.Groups.Actions.S3-on-V4.Dispatch
open import Substrate.Groups.Actions.S3-on-V4.HomRotations
open import Substrate.Groups.Actions.S3-on-V4.HomSwaps
open import Substrate.Groups.Actions.S3-on-V4.Axioms
open import Substrate.Groups.Actions.S3-on-V4.Generators
open import Substrate.Groups.Actions.S3-on-V4.Twist
open import Substrate.Groups.Actions.S3-on-V4.Composition
open import Substrate.Groups.Actions.S3-on-V4.AsAction