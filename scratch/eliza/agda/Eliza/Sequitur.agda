------------------------------------------------------------------------
-- Eliza.Sequitur
--
-- Online grammar induction over Word α. Each repeated digram in the
-- observed Word becomes a new nonterminal; rule references compound
-- recursively (Nevill-Manning & Witten 1997).
--
-- The grammar is a DAG of `Nonterminal → Word (Terminal ⊎ Nonterminal)`
-- rules — what the user called an SPPF for memoised traces. The
-- substrate-honest move is to instantiate this at MULTIPLE levels:
--
--   * Char-level   Sequitur α = Char.    Captures literal phrases.
--   * Gen-level    Sequitur α = Gen.     3-symbol alphabet; very compressible.
--   * Chamber-lvl  Sequitur α = Chamber. 24-symbol; captures Coxeter equivalences.
--   * Orbit-level  Sequitur α = Orbit.   6-symbol; cocycle-invariant grammar.
--
-- All four instantiate the same `Grammar α` interface defined below.
-- The orbit-level grammar is the substrate's payoff: gauge-equivalent
-- text fragments (different chars, same V₄-coset trajectory) collapse
-- to identical rules.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Sequitur where

open import Eliza.Prelude using (ℕ; _⊎_; inl; inr; _×_; _,_)
open import Eliza.Word    using (Word; []; _∷_)

------------------------------------------------------------------------
-- 1. Nonterminal IDs. Drawn from ℕ for the skeleton; the Python uses
-- monotonic integers.
------------------------------------------------------------------------

Nonterminal : Set
Nonterminal = ℕ

------------------------------------------------------------------------
-- 2. A symbol in a grammar rule: either a terminal from α or a
-- reference to an earlier nonterminal.
------------------------------------------------------------------------

Symbol : Set → Set
Symbol α = α ⊎ Nonterminal

------------------------------------------------------------------------
-- 3. A rule body: Word over Symbol α. Compact, sharable, recursive.
------------------------------------------------------------------------

Rule : Set → Set
Rule α = Word (Symbol α)

------------------------------------------------------------------------
-- 4. The Grammar state. Postulated as an abstract type with:
--   * a top-level rule (the sequence seen so far, compressed),
--   * a finite map Nonterminal → Rule α,
--   * a "digram index" for fast digram lookup (implementation detail).
------------------------------------------------------------------------

postulate
  Grammar       : Set → Set
  empty-grammar : (α : Set) → Grammar α

  -- The current top-level production (everything observed, packed).
  top-rule : {α : Set} → Grammar α → Rule α

  -- The map from nonterminal IDs to their right-hand sides.
  nonterminal-body : {α : Set} → Grammar α → Nonterminal → Rule α

  -- How many distinct nonterminals exist.
  n-nonterminals : {α : Set} → Grammar α → ℕ

------------------------------------------------------------------------
-- 5. The online update: extend the top-level rule by one symbol;
-- canonicalise (introduce new nonterminals for digrams that now repeat,
-- collapse nonterminals used only once).
------------------------------------------------------------------------

postulate
  observe : {α : Set} → Grammar α → α → Grammar α

------------------------------------------------------------------------
-- 6. Sequitur's two structural invariants:
--
--   * Digram uniqueness: no digram appears more than once across all
--     rule bodies.
--   * Rule utility: every nonterminal is referenced at least twice
--     (singleton nonterminals are collapsed).
--
-- Stated as postulated properties of `observe`.
------------------------------------------------------------------------

postulate
  digram-unique :
    {α : Set} (g : Grammar α) → Set
    -- ∀ digram d, the count of d across all rule bodies of g ≤ 1.

  rule-utility :
    {α : Set} (g : Grammar α) → Set
    -- ∀ nonterminal n in g, n appears in ≥ 2 places in the grammar.

  observe-preserves-invariants :
    {α : Set} (g : Grammar α) (x : α) →
    digram-unique g →
    rule-utility g →
    digram-unique (observe g x) × rule-utility (observe g x)

------------------------------------------------------------------------
-- 7. Multi-level Sequitur. The Engine maintains one Grammar per
-- alphabet level (Char, Gen, Chamber, Orbit). Per the substrate's
-- Cocycle Rule 5: the orbit-level grammar is the GAUGE-INVARIANT
-- compression — different routings of equivalent text produce the
-- same orbit-level grammar.
--
-- Stated as the structural payoff this module commits to.
------------------------------------------------------------------------

postulate
  orbit-grammar-is-gauge-invariant :
    -- For any V₄-equivariant router pair, the orbit-level grammar
    -- after observing the same input via either router is identical.
    -- Full statement deferred — depends on Eliza.Orbit + Eliza.Router
    -- machinery composing through Eliza.Engine.
    Set
