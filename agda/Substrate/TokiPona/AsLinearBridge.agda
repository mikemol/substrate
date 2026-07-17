------------------------------------------------------------------------
-- Substrate.TokiPona.AsLinearBridge
--
-- T10 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]].
--
-- The categorical bridge AND the intersection with Lojban explicitly
-- surfaced. Sister slice to Lojban L10 AsCCC.
--
-- STRUCTURAL CONTRAST (the contrastive-pedagogy capstone):
--
--   Lojban L10 (AsCCC.Bridge):
--     module Bridge (State : Set) (gismu-as-opcode : Gismu → State → State)
--       — uses FREE MONOID extension (LojbanWord → (State → State, ∘, id))
--       — instantiates OpcodeAlgebra Gismu State
--
--   Toki Pona T10 (this slice):
--     module Bridge (V : Set) (nimi-as-image : Nimi → V) + monoid structure on V
--       — uses FREE LINEAR extension (NimiSpace → V via T8)
--       — instantiates OpcodeAlgebra Nimi V
--
-- Both arcs invoke a "free X over a basis" universal property; both
-- instantiate the same OpcodeAlgebra primitive
-- (Substrate.Category.OpcodeAlgebra) with different carrier classes
-- (state-transformer monoid vs. vector additive monoid).
--
-- THE INTERSECTION (recorded but not extracted per
-- [[feedback-coalgebraic-not-consumer-driven]]): The two bridge
-- modules are sister instances of a hypothetical "free construction
-- over basis" parent primitive. Extracting it would mean lifting
-- both arcs' Bridge modules to a shared abstraction — deferred
-- until a third consumer (e.g., a future linguistic or numeric arc)
-- forces it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.AsLinearBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec)
  renaming ([] to []ᵥ; _∷_ to _∷ᵥ_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Iff using (_⇔_; ⇔-refl)
  using (_≡_; refl; cong; sym)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

open import Substrate.TokiPona.SemanticSpace using (SemVec; ∅; _⊕_)
open import Substrate.TokiPona.Nimi using (Nimi; nimi-count)
open import Substrate.TokiPona.LinearAlgebra
  using (NimiFreeLinearization; free-linearize-nimi)

open import Substrate.Algebra.F2.Linear using (Linear; apply)

open import Substrate.Category.OpcodeAlgebra
  using (OpcodeAlgebra; mkAlgebra; OpcodeCategory; substrate-native;
         execute)

------------------------------------------------------------------------
-- 1. The bridge construction.
--
-- Given any target type V with a "merge" operation and identity, and
-- a nimi-image map Nimi → V, we get:
--   * An OpcodeAlgebra instance with Opcode = Nimi, State = V.
--   * Each nimi acts on V by merging its image vector with the
--     current state.
--   * Composition of nimi sequences follows the additive-monoid
--     structure on V.
--
-- Sister-shape to Lojban L10's `module Bridge`; the only difference
-- is that Lojban's monoid was (State → State, ∘, id) while Toki Pona's
-- is (V, merge, e). Both are commutative-monoid-shaped instances of
-- "free X over basis."
------------------------------------------------------------------------

module Bridge
  (V : Set)
  (_⊞_ : V → V → V)
  (e : V)
  (nimi-image : Nimi → V)
  where

  ----------------------------------------------------------------------
  -- 1a. Each nimi acts on V by merging its image into the state.
  ----------------------------------------------------------------------

  nimi-as-opcode : Nimi → V → V
  nimi-as-opcode n state = state ⊞ nimi-image n

  ----------------------------------------------------------------------
  -- 1b. The OpcodeAlgebra instance.
  --
  -- Plugs Toki Pona's vocabulary into the substrate's CCC
  -- infrastructure ([[project-rarc-lambda-vm-recognition]]).
  ----------------------------------------------------------------------

  TokiPona-OpcodeAlgebra : OpcodeAlgebra Nimi V
  TokiPona-OpcodeAlgebra = mkAlgebra
    (λ _ → substrate-native)
    nimi-as-opcode

  ----------------------------------------------------------------------
  -- 1c. Sequence-of-nimi as a program.
  --
  -- A Coxeter-Word of nimi runs as a program: each nimi merges its
  -- image into the accumulating state. The Word view ↔ Vec view
  -- agreement mirrors Lojban L10's `program-execute-agree`.
  ----------------------------------------------------------------------

  program : Word Nimi → V → V
  program []      state = state
  program (n ∷ w) state = program w (nimi-as-opcode n state)

  word→vec : (w : Word Nimi) → ℕ
  word→vec []      = zero
  word→vec (_ ∷ w) = suc (word→vec w)

  word→vec-data : (w : Word Nimi) → Vec Nimi (word→vec w)
  word→vec-data []      = []ᵥ
  word→vec-data (n ∷ w) = n ∷ᵥ word→vec-data w

  program-execute-agree :
    (state : V) (w : Word Nimi) →
    program w state ≡ execute TokiPona-OpcodeAlgebra state (word→vec-data w)
  program-execute-agree state []      = refl
  program-execute-agree state (n ∷ w) =
    program-execute-agree (nimi-as-opcode n state) w

------------------------------------------------------------------------
-- 2. The canonical instance using SemVec nimi-count as V.
--
-- Plugs in the default semantic vector space + ⊕ + ∅ + identity
-- image (each nimi → its basis vector). Produces the
-- TokiPona-OpcodeAlgebra Nimi (SemVec nimi-count) instance.
------------------------------------------------------------------------

open import Substrate.TokiPona.NimiSpace using (nimi-as-vector)

module CanonicalBridge =
  Bridge (SemVec nimi-count) _⊕_ ∅ nimi-as-vector

------------------------------------------------------------------------
-- 3. The intersection-with-Lojban statement.
--
-- Lojban L10's Bridge and Toki Pona T10's Bridge are SISTER MODULES
-- under the same universal-property shape. Recorded here as a
-- comment-block + a small symbolic alignment lemma; not yet
-- extracted to a shared parent primitive per
-- [[feedback-coalgebraic-not-consumer-driven]].
--
-- The alignment in symbols:
--
--   Universal property       Lojban L10 instance          Toki Pona T10 instance
--   -------------------      -------------------          ----------------------
--   Free X over basis        Free monoid over Gismu       Free F₂-module over Nimi
--   Carrier monoid           (State → State, ∘, id)        (V, ⊞, e)
--   Image map                Gismu → (State → State)       Nimi → V
--   Unique extension         WordAlgebra.extend (L8)       NimiFreeLinearization (T8)
--   OpcodeAlgebra plug       OpcodeAlgebra Gismu State     OpcodeAlgebra Nimi V
--
-- The "Free X over basis" row is the shared categorical primitive
-- waiting to be extracted; when a third instance forces extraction,
-- the parent primitive becomes substrate-native rather than
-- coalgebraically deferred.
------------------------------------------------------------------------

-- A symbolic record stating the alignment at the type-signature
-- level (the actual extraction is deferred).
--
-- ⟡set1-rp: carrier→param — the two shape fields (∀-over-Set) and
-- shapes-coincide were FIELDS (pinning the record at Set₁); as
-- PARAMETERS they never raise the sort — fully vestigial. Per
-- [[Substrate.Foundation.Iff]]'s ⟡rc-het-iff discipline: an ex-`≡`
-- between two Set-producing functions is stated pointwise via `⇔`
-- (logical equivalence, Set₀) rather than propositional `≡` (which
-- would force Set₁); the witness is `refl` in both directions since
-- the two shape functions are the same closed term.
record BridgeAlignment
  -- The two arcs both produce OpcodeAlgebras with substrate-
  -- native opcodes — same primitive endpoint.
  (lojban-arc-opcode-algebra-shape :
      (Opcode : Set) (State : Set) → OpcodeAlgebra Opcode State → Set)
  (tokipona-arc-opcode-algebra-shape :
      (Opcode : Set) (State : Set) → OpcodeAlgebra Opcode State → Set)
  -- The shapes coincide (modulo carrier choice), pointwise:
  (shapes-coincide :
      (Opcode State : Set) (alg : OpcodeAlgebra Opcode State) →
      lojban-arc-opcode-algebra-shape Opcode State alg ⇔
      tokipona-arc-opcode-algebra-shape Opcode State alg)
  : Set where

bridge-alignment-witness :
  BridgeAlignment
    (λ _ _ _ → ℕ → ℕ)
    (λ _ _ _ → ℕ → ℕ)
    (λ _ _ _ → ⇔-refl)
bridge-alignment-witness = record {}

------------------------------------------------------------------------
-- 4. Capstone.
--
-- T10 closes the 10-slice linear-side arc and the larger linguistic
-- Rosetta arc per [[project-linguistic-rosetta-arc]]. Every Toki
-- Pona fragment expression now has a categorical home in the
-- substrate's lambda-VM CCC, and the intersection with the Lojban
-- side is recorded for future shared-primitive extraction.
--
-- The two linguistic arcs (Lojban: discrete word-algebra; Toki Pona:
-- linear-field semantics) jointly demonstrate the substrate's
-- discrete/linear bridge ([[feedback-continuous-via-discrete-inference-rules]])
-- at a real, fully-formalised pair of sites.
------------------------------------------------------------------------
