------------------------------------------------------------------------
-- Substrate.Invented.LieFragment
--
-- C7 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- The **Free Lie algebra** witness — substrate-INVENTED, not from
-- an existing conlang. The cell is the "unexplored quadrant" the
-- peer review flagged: no real conlang occupies the Lie-algebra
-- cell, so the substrate invents a tiny sketch to demonstrate the
-- cell is reachable.
--
-- DELIBERATELY SMALL per the peer-review recommendation: this slice
-- "demonstrates the cell is reachable, not overbuilds Lie." Three
-- generators + bracket-expression tree + FreeOverBasis instance.
-- The full Lie-algebra structure (Jacobi identity, anti-commutativity)
-- lives at Substrate.Category.LieAlgebra; this fragment provides
-- the SYNTACTIC witness of the cell, not the semantic theory.
--
-- The arc trajectory implied: a future arc could build a fuller
-- "Lie-algebraic conlang" — a constructed language whose
-- compositional structure is bracket-based rather than monoid /
-- module / relation / CCC. Per
-- [[project-language-as-free-construction-classification]] this is
-- one of the INVENTED cells the substrate could generate.
--
-- Per [[feedback-categorical-name-first]]: "free Lie algebra over
-- generators" is the standard name; substrate's LieAlgebra
-- primitive supplies the full theory.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment where

open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; mkFreeOverBasis;
         LanguageWitness; mkWitness;
         FreeConstructionClass; Free-Lie;
         WitnessName; LieFrag)

------------------------------------------------------------------------
-- 1. Three generator "directions".
--
-- The minimal Lie basis. In the substrate's invented-language
-- reading: each generator is a primitive "direction of action,"
-- and the bracket captures non-commutative interaction between
-- two directions.
------------------------------------------------------------------------

data LieGen : Set where
  x : LieGen
  y : LieGen
  z : LieGen

------------------------------------------------------------------------
-- 2. Bracket-expression tree.
--
-- The free carrier: either a generator or a bracket of two
-- sub-expressions. Captures the binary-tree structure of Lie
-- expressions before quotienting by Jacobi + anti-commutativity.
-- (Quotienting is the LieAlgebra primitive's job, not this fragment's.)
------------------------------------------------------------------------

data LieExpr : Set where
  gen     : LieGen → LieExpr
  bracket : LieExpr → LieExpr → LieExpr

------------------------------------------------------------------------
-- 3. Unit and example expressions.
------------------------------------------------------------------------

η-LieGen : LieGen → LieExpr
η-LieGen = gen

-- Single generator
expr-x : LieExpr
expr-x = gen x

-- The bracket [x, y]
expr-xy : LieExpr
expr-xy = bracket (gen x) (gen y)

-- The Jacobi-flavoured nested bracket [x, [y, z]]
expr-jacobi-1 : LieExpr
expr-jacobi-1 = bracket (gen x) (bracket (gen y) (gen z))

-- Another Jacobi component [y, [z, x]]
expr-jacobi-2 : LieExpr
expr-jacobi-2 = bracket (gen y) (bracket (gen z) (gen x))

------------------------------------------------------------------------
-- 4. The FreeOverBasis instance.
------------------------------------------------------------------------

lie-free-structure : FreeOverBasis LieGen LieExpr
lie-free-structure = mkFreeOverBasis η-LieGen

lie-witness : LanguageWitness LieGen LieExpr
lie-witness = mkWitness
  LieFrag
  lie-free-structure
  Free-Lie

------------------------------------------------------------------------
-- 5. Deferred per [[feedback-coalgebraic-not-consumer-driven]].
--
-- A fuller treatment would:
--   * quotient LieExpr by anti-commutativity ([x, y] = -[y, x])
--   * quotient by Jacobi ([x, [y, z]] + [y, [z, x]] + [z, [x, y]] = 0)
--   * connect to Substrate.Category.LieAlgebra
--   * provide an integer-coefficient bracketing
--
-- All deferred. C7's contribution: the cell is reachable, the
-- shape of the basis-to-bracket-tree free construction is named,
-- and a future arc can pick up from this witness.
------------------------------------------------------------------------
