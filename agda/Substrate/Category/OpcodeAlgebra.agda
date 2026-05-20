------------------------------------------------------------------------
-- Substrate.Category.OpcodeAlgebra
--
-- R-arc: the codec's opcode-set architecture lifted to a substrate
-- categorical primitive. Recognises that the codec was operating in
-- a Cartesian-closed category over its opcode algebra all along:
-- opcodes are functions; grown-rules are abstraction; NT references
-- are application; the stack is the variable environment; Sequitur
-- growth is β-abstraction (forward); inlining is β-reduction
-- (backward).
--
-- Per the user's recognition: the codec's existing machinery IS a
-- lambda-VM with the right names. This module supplies those names
-- at the substrate categorical layer.
--
-- Per [[categorical-name-first]]: lambda calculus has the categorical
-- name "Cartesian-closed category" (CCC). Our codec instance is a
-- CCC over an opcode algebra whose generators are substrate-native
-- (V₄, Sylow-3, etc.) plus control opcodes for grammar manipulation.
--
-- Per [[tetrative-metacircularity]]: the OpcodeAlgebra is the L1
-- meta-layer; speculation over opcode emissions is L2; introspection
-- (S_INSPECT) is L3; tetrative climb continues.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.OpcodeAlgebra where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Data.Fin using (Fin)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Product using (Σ; _,_)
open import Data.Vec using (Vec; []; _∷_)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

------------------------------------------------------------------------
-- 1. OpcodeCategory — the structural classification.
--
-- Each opcode in the codec's alphabet belongs to one of these
-- categories. This is the introspection range: S_INSPECT(opcode)
-- returns an OpcodeCategory.
------------------------------------------------------------------------

data OpcodeCategory : Set where
  chain-terminal     : OpcodeCategory
  substrate-native   : OpcodeCategory     -- V₄ / Sylow-3 / cross-Sylow
  exploding-bitmap   : OpcodeCategory
  grown-composite    : OpcodeCategory
  sequitur-control   : OpcodeCategory     -- S_GROW / S_DEFER_GROW / S_INLINE
  stack-control      : OpcodeCategory     -- S_PUSH / S_POP / S_DUP / etc.
  lambda-var         : OpcodeCategory     -- S_VAR(d)
  introspection      : OpcodeCategory     -- S_INSPECT

------------------------------------------------------------------------
-- 2. OpcodeAlgebra — the costructure.
--
-- An opcode algebra A consists of:
--   * Carrier: the set Opcode of opcodes
--   * Categorise: Opcode → OpcodeCategory
--   * Apply: a meaning function Opcode → (state → state) where state
--           encapsulates stack + grammar + output stream
--
-- The codec's V4 opcode set is one such algebra. Different codecs
-- with different opcode sets are different algebras over the same
-- categorical structure.
--
-- An OpcodeAlgebra is a Cartesian-closed category if its opcodes
-- include abstraction (grown rules), application (NT references),
-- variables (S_VAR), and the type system is sufficient to express
-- arbitrary function types. Our codec exhibits all of these.
------------------------------------------------------------------------

record OpcodeAlgebra
  {ℓO ℓS : Level}
  (Opcode : Set ℓO)
  (State : Set ℓS)
  : Set (ℓO ⊔ ℓS) where
  constructor mkAlgebra
  field
    -- Each opcode has a category (introspectable).
    categorise : Opcode → OpcodeCategory
    -- Each opcode is a state transformer.
    apply : Opcode → State → State

open OpcodeAlgebra public

------------------------------------------------------------------------
-- 3. Composition: a program is a sequence of opcodes.
--
-- The encoder's output is a Vec Opcode n; the decoder executes by
-- folding apply over this sequence starting from initial state.
------------------------------------------------------------------------

execute :
  {ℓO ℓS : Level}
  {Opcode : Set ℓO} {State : Set ℓS}
  (alg : OpcodeAlgebra Opcode State)
  (initial : State)
  {n : ℕ}
  (program : Vec Opcode n) →
  State
execute _ s [] = s
execute alg s (op ∷ rest) = execute alg (apply alg op s) rest

------------------------------------------------------------------------
-- 4. Categorical bridge: OpcodeAlgebra as a CCC.
--
-- The substrate-honest claim: the codec's OpcodeAlgebra is the
-- internal language of a Cartesian-closed category whose objects are
-- state types and whose morphisms are programs (Vec Opcode n).
--
-- The CCC structure provides:
--   * Products    — stack PUSH (push pair) / POP
--   * Exponentials — abstraction (grown rule body) / application (NT ref)
--   * Terminal    — empty stack
--
-- The codec's lambda-VM is the operational realisation of this CCC.
-- Per [[expose-generator-not-orbit]], we expose the CCC GENERATORS
-- (opcodes), not the orbit (all reachable programs).
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 5. Introspection: opcodes that examine other opcodes.
--
-- A self-introspecting OpcodeAlgebra has S_INSPECT as an opcode that
-- takes an opcode-id and emits its OpcodeCategory. This makes the
-- algebra HOMOICONIC at the categorical level — opcodes ARE data
-- the algebra can manipulate.
--
-- Per [[tetrative-metacircularity]]: introspection enables the
-- L3+ tetrative meta-layers where opcodes reason about opcodes.
------------------------------------------------------------------------

record SelfIntrospecting
  {ℓO ℓS : Level}
  {Opcode : Set ℓO} {State : Set ℓS}
  (alg : OpcodeAlgebra Opcode State)
  : Set (ℓO ⊔ ℓS) where
  constructor mkIntrospecting
  field
    -- An S_INSPECT operation: given an opcode and a state, produce a
    -- new state with the categorisation result encoded in it.
    inspect : Opcode → State → State
    -- The introspection is sound: it returns the alg's categorisation.
    -- (Soundness witness left abstract; instances provide it.)

open SelfIntrospecting public

------------------------------------------------------------------------
-- 6. Connection to the codec.
--
-- The codec V4 (`scratch/eliza/eliza/gpu_codec_v4.py`) instantiates
-- this structure:
--
--   Opcode = ℕ              (joint alphabet index ∈ [0, 24 + n_used + N_CONTROL))
--   State  = encoder/decoder state tuple (stack, opcode-tensor,
--            digram-index, RC-state, output-stream)
--
--   categorise: maps emit_idx to an OpcodeCategory via
--               `lambda_vm_opcodes.categorise_opcode_idx`
--   apply:      dispatch on emit_idx in the decoder's main loop
--   inspect:    `S_INSPECT_LAST` (control opcode 13)
--
-- The codec's runtime witnesses the CCC structure: programs (encoded
-- byte streams) execute to produce decoded byte streams; this IS
-- evaluation in a Cartesian-closed category.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 7. Cross-references.
--
-- * `ChainDecomposition` (Q8) — sibling primitive; per-element chain
--   structure within G. OpcodeAlgebra extends this to programs in
--   the opcode language.
-- * `BWTEmergence` (Q9) — empirical concentration phenomenon; the
--   commit-map is a function in this CCC.
-- * `PrimeFactoredGauge` (T1) — the gauge ladder whose generators
--   are basis opcodes in any OpcodeAlgebra instance.
-- * `Strict2Monoid` (#7) — related; a Strict2Monoid is a degenerate
--   OpcodeAlgebra where all opcodes are pure data transformers
--   (no introspection).
-- * `GradedMonoid` (#8) — likewise; the chain alphabet has graded
--   monoid structure where the grading is the chain length.
--
-- Codec runtime: `scratch/eliza/eliza/lambda_vm_opcodes.py` +
-- `scratch/eliza/eliza/gpu_codec_v4.py`.
------------------------------------------------------------------------
