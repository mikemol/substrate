------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3
--
-- The action of Z/2 on Z/3 by inversion. This is the unique non-trivial
-- group homomorphism Z/2 → Aut(Z/3), and the action data for the
-- semidirect product S₃ = Z/3 ⋊ Z/2.
--
-- The Z/2 generator acts on Z/3 as the inversion automorphism
-- (a ↦ a², i.e., [a] ↔ [a, a]); Z/2's identity acts trivially.
--
-- File-per-lemma decomposition per [[s3-on-v4-file-per-lemma]]:
--
--   Act           — act-letter, act (the core dispatch)
--   Canonical     — act-letter-canonical, act-canonical, normalize-act
--   ActCong       — act-cong (depends only on canonical pair + n)
--   ActEpsilon    — act-ε (Z₂ identity acts trivially)
--   ActEpsilonN   — act-letter-ε, act-ε-N (every action fixes Z₃ identity)
--   ActDot        — act-letter-compose, act-∙ (composition compatibility)
--   ActHom        — act-letter-hom, act-hom (distributivity over Z₃ ·)
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]:
-- isolating the action in its own subtree keeps S3's composition
-- cognitively local — S3.agda just plugs this in via `φ.act-*`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3 where

open import Substrate.Groups.Actions.Z2-on-Z3.Act
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.LetterCanonical
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.ActCanonical
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical.NormalizeAct
open import Substrate.Groups.Actions.Z2-on-Z3.ActCong
open import Substrate.Groups.Actions.Z2-on-Z3.ActEpsilon
open import Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.LetterEpsilon
open import Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN.EpsilonN
open import Substrate.Groups.Actions.Z2-on-Z3.ActDot.LetterCompose
open import Substrate.Groups.Actions.Z2-on-Z3.ActDot.Dot
open import Substrate.Groups.Actions.Z2-on-Z3.ActHom.LetterHom
open import Substrate.Groups.Actions.Z2-on-Z3.ActHom.Hom
