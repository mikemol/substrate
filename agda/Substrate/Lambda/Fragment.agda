------------------------------------------------------------------------
-- Substrate.Lambda.Fragment
--
-- C6 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Lambda calculus / SKI combinators as the **Free CCC** witness —
-- the purest-form cell of the classification, what Lojban
-- approximates and the substrate's R-arc lambda-VM
-- ([[project-rarc-lambda-vm-recognition]]) operationally realises.
--
-- Basis: the SKI combinators (S, K, I) plus optional auxiliary
-- combinators (B, C). The free Cartesian Closed Category over
-- these IS the SKI-calculus expression algebra.
--
-- Per the peer-review observation: "your VM is already this — this
-- recovers the pure form of what Lojban approximates." The
-- substrate's OpcodeAlgebra has been the categorical home all
-- along; C6 makes the alignment explicit at the witness layer.
--
-- The fragment captures only the BASIS + free-monoid layer; full
-- β-reduction semantics is the R-arc's domain
-- ([[project-rarc-lambda-vm-recognition]] supplies it).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lambda.Fragment where

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; mkFreeOverBasis;
         LanguageWitness; mkWitness;
         FreeConstructionClass; Free-CCC;
         WitnessName; Lambda)

------------------------------------------------------------------------
-- 1. The SKI combinator basis.
--
-- Three primitive combinators generating the entire untyped lambda
-- calculus:
--   S = λ x y z. (x z)(y z)   — substitution
--   K = λ x y. x              — constant
--   I = λ x. x                — identity
--
-- (B, C are derivable but included as named combinators for
-- ergonomic worked examples.)
------------------------------------------------------------------------

data Combinator : Set where
  S : Combinator   -- S x y z = (x z)(y z)
  K : Combinator   -- K x y = x
  I : Combinator   -- I x = x
  B : Combinator   -- B = S(KS)K     — composition
  C : Combinator   -- C = S(BBS)(KK) — swap

------------------------------------------------------------------------
-- 2. SKI expressions as Coxeter words over combinators.
--
-- A linear "applicative" sequence; richer expression trees (with
-- explicit branching) are deferred to the substrate's existing
-- OpcodeAlgebra / lambda-VM infrastructure where the R-arc
-- already provides the CCC structure.
------------------------------------------------------------------------

SKIWord : Set
SKIWord = Word Combinator

ε : SKIWord
ε = []

single : Combinator → SKIWord
single c = c ∷ []

------------------------------------------------------------------------
-- 3. Worked examples.
--
-- I = SKK (the classic SKI-encoding of identity using only S and K)
-- — the fragment can express it as a Word.
------------------------------------------------------------------------

-- The pure identity (single combinator I).
expr-I : SKIWord
expr-I = I ∷ []

-- The SKK form of identity: a 3-combinator word.
expr-SKK : SKIWord
expr-SKK = S ∷ K ∷ K ∷ []

-- B as a composed expression: S(KS)K — when applied to the basis,
-- this performs function composition.
expr-B-derived : SKIWord
expr-B-derived = S ∷ K ∷ S ∷ K ∷ []

------------------------------------------------------------------------
-- 4. The FreeOverBasis instance.
------------------------------------------------------------------------

lambda-free-structure : FreeOverBasis Combinator SKIWord
lambda-free-structure = mkFreeOverBasis single

lambda-witness : LanguageWitness
lambda-witness = mkWitness
  Lambda
  Combinator
  SKIWord
  lambda-free-structure
  Free-CCC

------------------------------------------------------------------------
-- 5. The bridge note.
--
-- The substrate's R-arc lambda-VM ([[project-rarc-lambda-vm-recognition]])
-- IS the operational realisation of this Free CCC. The OpcodeAlgebra
-- primitive (Substrate.Category.OpcodeAlgebra) supplies the
-- categorical home; β-reduction is the Sequitur inline-rule
-- operation. C6's witness records that the Lambda/SKI cell of the
-- linguistic classification IS the same categorical object the
-- codec arc has been operating within. Per
-- [[feedback-categorical-name-first]]: "Free CCC" names what the
-- substrate's R-arc has been doing all along.
------------------------------------------------------------------------
