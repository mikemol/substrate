------------------------------------------------------------------------
-- Substrate.Lojban.Gismu
--
-- L3 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- The vocabulary basis: a small data declaration listing 15 gismu
-- spanning all five Lojban place-structure arities (1..5). Per
-- [[feedback-expose-generator-not-orbit]] the gismu ARE the
-- generators — flat enumeration here is the correct shape because
-- gismu form a finite alphabet, not a derived orbit.
--
-- Bridges the two L1/L2 shadows:
--   * Each gismu maps to a single-symbol LojbanWord (L2 side).
--   * Each gismu has a place-structure arity (ℕ), and (given a user-
--     supplied denotation) maps to a Selbri at that arity (L1 side).
--
-- The denotation is exposed via a sub-module `WithDenotation` so the
-- semantic universe (Sumti, Sem) remains parametric. Different
-- consumers can pick different semantic carriers: L9 (Fragment) uses
-- a toy carrier for examples; L10 (AsCCC) uses the lambda-VM CCC.
-- Per [[feedback-multi-reading-ambient-discipline]]: no semantic
-- universe is privileged.
--
-- The 15-gismu choice is deliberately small (one slice's-worth of
-- worked vocabulary) and arity-balanced (1, 2, 3, 4, 5 all present).
-- Real Lojban has ~1350 gismu; the fragment can extend mechanically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Gismu where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec)

------------------------------------------------------------------------
-- 1. The Gismu enumeration.
--
-- Listed by ascending arity, each with its place-structure comment.
-- The commented place-structure is prose-level per
-- [[feedback-comments-dont-overclaim]]; the typechecker enforces
-- only the `arity` numeric.
------------------------------------------------------------------------

data Gismu : Set where
  -- 1-place
  prenu : Gismu  -- x₁ is a person
  -- 2-place
  gerku : Gismu  -- x₁ is a dog of species x₂
  mlatu : Gismu  -- x₁ is a cat of species x₂
  nelci : Gismu  -- x₁ likes x₂
  pendo : Gismu  -- x₁ is a friend of x₂
  zdani : Gismu  -- x₁ is a house of x₂
  -- 3-place
  zarci : Gismu  -- x₁ is a market for goods x₂ operated by x₃
  dunda : Gismu  -- x₁ gives x₂ to x₃
  sutra : Gismu  -- x₁ is quick at doing x₂ by standard x₃
  barda : Gismu  -- x₁ is big in property x₂ compared to x₃
  cmalu : Gismu  -- x₁ is small in property x₂ compared to x₃
  -- 4-place
  tavla : Gismu  -- x₁ talks to x₂ about x₃ in language x₄
  ckule : Gismu  -- x₁ is a school for x₂ teaching x₃ by method x₄
  melbi : Gismu  -- x₁ is beautiful to x₂ in aspect x₃ by standard x₄
  -- 5-place
  klama : Gismu  -- x₁ goes to x₂ from x₃ via x₄ using x₅

------------------------------------------------------------------------
-- 2. Arity assignment.
--
-- The numeric place-structure size. This is the only typechecker-
-- enforced part of the table.
------------------------------------------------------------------------

arity : Gismu → ℕ
arity prenu = 1
arity gerku = 2
arity mlatu = 2
arity nelci = 2
arity pendo = 2
arity zdani = 2
arity zarci = 3
arity dunda = 3
arity sutra = 3
arity barda = 3
arity cmalu = 3
arity tavla = 4
arity ckule = 4
arity melbi = 4
arity klama = 5

------------------------------------------------------------------------
-- 3. Bridge to LojbanWord (L2 side).
--
-- A gismu lifts to a one-symbol word. This is the inclusion of
-- generators into the free word algebra.
------------------------------------------------------------------------

open import Substrate.Lojban.Word Gismu using (LojbanWord; single)

gismu-to-word : Gismu → LojbanWord
gismu-to-word = single

------------------------------------------------------------------------
-- 4. Bridge to Selbri (L1 side), via parametric denotation.
--
-- The sub-module takes the semantic universe (Sumti, Sem) plus a
-- denotation function that interprets each gismu at its arity, and
-- supplies the gismu→Selbri map. Different consumers instantiate
-- the sub-module with different semantic universes — the substrate
-- does not commit to one.
------------------------------------------------------------------------

module WithDenotation
  (Sumti : Set) (Sem : Set)
  (denote : (g : Gismu) → Vec Sumti (arity g) → Sem)
  where

  open import Substrate.Lojban.PlaceStructure using (Selbri; mkSelbri)

  gismu-to-selbri : (g : Gismu) → Selbri (arity g) Sumti Sem
  gismu-to-selbri g = mkSelbri (denote g)
