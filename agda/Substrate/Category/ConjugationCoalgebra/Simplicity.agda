------------------------------------------------------------------------
-- Substrate.Category.ConjugationCoalgebra.Simplicity
--
-- Simplicity as a RECOGNIZER over the conjugation trace.
--
-- The term-algebra side CONSTRUCTS a group (build it up from
-- generators + relations: algebra, structure flowing in).  Simplicity
-- is the dual: it does not construct anything — it OBSERVES the group
-- by unfolding conjugation (coalgebra, structure flowing out).  A
-- group is simple iff its only normal subgroups are {e} and the whole
-- group; "normal subgroup" unfolds to "a union of conjugacy classes
-- closed under the operation", so the object the recognizer reads is
-- exactly the conjugation trace already packaged by
-- `ConjugationCoalgebra` (rep-classes + membership + the
-- conjugation-respects-class orbit law).
--
-- This module turns the SIMPLICITY STATEMENT into something uniform
-- and shared: `IsSimple` is one definition, parametric over any
-- conjugation coalgebra.  Per-group simplicity claims (Aₙ for n ≥ 5,
-- PSL(n,q), the sporadics) become *instantiations* of this one
-- recognizer rather than bespoke top-level theorems — the compact /
-- expressive payoff.
--
-- GAUGE-HONEST BOUNDARY (do not let this get rigidified):
--   * The recognizer compresses the STATEMENT and shares the lattice
--     machinery.  It does NOT make the WITNESS free.  `IsSimple K` is
--     a one-liner; producing the proof for a specific K (e.g. Aₙ) is
--     genuine mathematics.
--   * `IsSimple` is `Set`-valued — a property, not in general a
--     decision.  It is a terminating decision (Bool over a finite
--     trace) only when `Class` is finite and membership/≈ decidable;
--     otherwise it is an Ω-valued observation.  See the FINITE note at
--     the foot of the file.
--
-- Algebra/coalgebra duality realised, per [[homology-cohomology-
-- recursion]] and [[coalgebraic-not-consumer-driven]]: term algebra =
-- construct; this = recognize; `GaloisAdjunction` (T4) is the bridge.
--
-- SCOPED-CLASSICAL POLICY: this module is the reference model for
-- docs/governance/scoped-classical-hypotheses.md.  The classical
-- converse (Shadow 3c) is a SCOPED HYPOTHESIS, not a postulate; the
-- finite case (Shadow 5) discharges it constructively.  Read that
-- policy before adding other scoped-classical results.
--
-- Shadows (per decomposable-by-entailment):
--   1. NormalSubgroup       — the trace-closed predicate.
--   2. IsTrivial/IsWhole/IsSimple — the recognizer (lattice form).
--   3. refute-simple        — the "reject" certificate (PROVEN).
--   3b. NonSimplicityWitness — the "attempt by default" type;
--       inhabited iff not simple, uninhabited iff simple (PROVEN both
--       directions modulo the anti-LEM seam — see Shadow 3b).
--   3c. Decidable / Classical — the scoped converse ¬witness→simple
--       under the WEAKEST sufficient hypothesis (dec-proper + two
--       ¬¬-stabilities); full LEM is a thin derived instance (PROVEN).
--   4. WithOrbits.saturated — the rep-class trace bridge (PROVEN).
--   5. WithOrbits.Finite — the finite discharge: decides properness by
--       sweeping the finite rep-class trace, giving ¬witness→simple
--       CONSTRUCTIVELY (no LEM) when the trace is finite (PROVEN).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ConjugationCoalgebra.Simplicity where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Product using (∃-syntax; _,_)
open import Substrate.Foundation.Negation using (Dec; yes; no; dec-¬; from-¬¬)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Fin.Exists using (Fin-∃?)
open import Substrate.Foundation.Eq using (sym; subst)
open import Substrate.Algebra.Bijection using (_↔_)
open import Substrate.Category.ConjugationCoalgebra using (ConjugationCoalgebra)

------------------------------------------------------------------------
-- The recognizer is parametric over a conjugation coalgebra K and an
-- equivalence _≈_ on its carrier (needed only to state "is the
-- identity" / "respects equivalence" — the coalgebra record itself
-- carries no equality).  Fixed at level 0ℓ: every finite particular
-- group (Aₙ, Zₙ, Sₙ, GL(n,F_q), the sporadic carriers) lives in Set.
-- Generalising to arbitrary ℓ is mechanical (Empty.Polymorphic).
------------------------------------------------------------------------

module Recognizer
  (K   : ConjugationCoalgebra {0ℓ})
  (_≈_ : ConjugationCoalgebra.G K → ConjugationCoalgebra.G K → Set)
  where

  open ConjugationCoalgebra K

  ----------------------------------------------------------------------
  -- Shadow 1.  A normal subgroup, coalgebraically: an element
  -- predicate closed under the group operations AND under conjugation
  -- (member-conj).  The conjugation-closure is what makes it a union
  -- of conjugacy classes — i.e. a sub-coalgebra of K that is also a
  -- subgroup.  Mirrors S₄-NormalSubgroup, but generic over K.
  ----------------------------------------------------------------------

  -- ⟡set1-paydown: `member : G → Set` is the sole Set-valued field (the Set₁
  -- source); lift it to a module parameter (the S₄-Subgroup pattern) so
  -- NormalSubgroup lands in Set.  Use sites write `NormalSubgroup member`; the
  -- other fields still project (member-resp / member-conj / …).  The remaining
  -- ∀-over-member lives only in `IsSimple`, the (irreducibly Set₁) universal
  -- property — its content, not a record.
  module _ (member : G → Set) where
    record NormalSubgroup : Set where
      field
        member-resp : {a b : G} → a ≈ b → member a → member b
        member-ε    : member ε
        member-·    : {a b : G} → member a → member b → member (a · b)
        member-⁻¹   : {a : G} → member a → member (a ⁻¹)
        member-conj : (g : G) {h : G} → member h → member ((g · h) · (g ⁻¹))

  ----------------------------------------------------------------------
  -- Shadow 2.  The two endpoints of the normal-subgroup lattice and
  -- the recognizer: K is simple iff every normal subgroup is one of
  -- the endpoints.
  ----------------------------------------------------------------------

  -- ⟡set1-paydown: `member` threads as an implicit param (inferred from N).
  IsTrivial : {member : G → Set} → NormalSubgroup member → Set
  IsTrivial {member} N = (a : G) → member a → a ≈ ε

  IsWhole : {member : G → Set} → NormalSubgroup member → Set
  IsWhole {member} N = (a : G) → member a

  -- IsSimple is the universal property — a ∀ over the member-family, so it is
  -- irreducibly Set₁ (that ∀ is its content; it is a def, not a target record).
  IsSimple : Set₁
  IsSimple = {member : G → Set} (N : NormalSubgroup member) → IsTrivial N ⊎ IsWhole N

  -- The whole group is always a normal subgroup (top of the lattice).
  -- (The bottom, {e}, needs the group identity/cong laws the coalgebra
  -- record does not expose, so it is supplied per instance.)
  whole-NS : NormalSubgroup (λ _ → ⊤)
  whole-NS = record
    { member-resp = λ _ _ → tt
    ; member-ε    = tt
    ; member-·    = λ _ _ → tt
    ; member-⁻¹   = λ _ → tt
    ; member-conj = λ _ _ → tt
    }

  ----------------------------------------------------------------------
  -- Shadow 3.  The "reject" certificate.  Exhibiting ONE proper,
  -- nontrivial normal subgroup refutes simplicity.  This is the
  -- compact, reusable way to prove a group is NOT simple: supply the
  -- witness subgroup and two elements (one nontrivial member, one
  -- non-member).  PROVEN.
  ----------------------------------------------------------------------

  refute-simple :
    {member : G → Set} (N : NormalSubgroup member) →
    (a₀ : G) → member a₀ → (a₀ ≈ ε → ⊥) →  -- nontrivial
    (b₀ : G) → (member b₀ → ⊥) →            -- proper
    IsSimple → ⊥
  refute-simple N a₀ a₀∈ a₀≉ε b₀ b₀∉ simple with simple N
  ... | inj₁ triv  = a₀≉ε (triv a₀ a₀∈)
  ... | inj₂ whole = b₀∉ (whole b₀)

  ----------------------------------------------------------------------
  -- Shadow 3b.  The "attempt by default" object.  Rather than invoking
  -- refute-simple with a hand-found witness, name the TYPE of
  -- non-simplicity witnesses: a normal subgroup that is both nontrivial
  -- (some member ≉ ε) and proper (some non-member).  This type is
  -- always well-formed; it is INHABITED iff K is not simple and
  -- UNINHABITED iff K is simple.  Nothing ever "fails" — emptiness of
  -- this type IS simplicity.
  --
  -- CONSTRUCTIVE SEAM (per [[feedback_reject_lem_in_substrate]]):
  -- "no witness was constructed" (absence of proof) is NOT IsSimple.
  -- The genuine content is `NonSimplicityWitness → ⊥`, and that is
  -- strictly WEAKER than IsSimple — recovering the decidable disjunction
  -- IsTrivial ⊎ IsWhole needs trivial-vs-whole decidable per N, i.e. a
  -- finite/decidable trace (see the FINITE note at the foot).  So:
  --   IsSimple → ¬ NonSimplicityWitness     holds unconditionally;
  --   ¬ NonSimplicityWitness → IsSimple     needs decidability.
  ----------------------------------------------------------------------

  -- ⟡set1-paydown: the witness's `member` predicate becomes a module parameter
  -- too — the record lands in Set; the existential over member is carried by
  -- the caller's implicit argument (`NonSimplicityWitness member`).
  module _ (member : G → Set) where
    record NonSimplicityWitness : Set where
      field
        N         : NormalSubgroup member
        wit-ntriv : G
        ntriv-∈   : member wit-ntriv
        ntriv-≉ε  : wit-ntriv ≈ ε → ⊥
        wit-prop  : G
        prop-∉    : member wit-prop → ⊥

  -- A witness refutes simplicity (refute-simple, repackaged).  PROVEN.
  witness→¬simple : {member : G → Set} → NonSimplicityWitness member → IsSimple → ⊥
  witness→¬simple
    record { N = N ; wit-ntriv = a₀ ; ntriv-∈ = a₀∈ ; ntriv-≉ε = a₀≉ε
           ; wit-prop = b₀ ; prop-∉ = b₀∉ }
    = refute-simple N a₀ a₀∈ a₀≉ε b₀ b₀∉

  -- Conversely, simplicity empties the witness type — the constructive
  -- half of "uninhabited iff simple".  PROVEN.  (The OTHER half,
  -- ¬NonSimplicityWitness → IsSimple, is the decidable-trace bridge and
  -- is deliberately NOT claimed here.)
  simple→¬witness : {member : G → Set} → IsSimple → NonSimplicityWitness member → ⊥
  simple→¬witness s w = witness→¬simple w s

  ----------------------------------------------------------------------
  -- Shadow 3c.  The scoped CLASSICAL bridge: ¬NonSimplicityWitness →
  -- IsSimple.  This is the converse half that the anti-LEM seam blocks
  -- constructively (per [[feedback_reject_lem_in_substrate]]).  It is
  -- offered as a SCOPED HYPOTHESIS, not a postulate — the module stays
  -- --safe and the classical dependency is visible in every user's
  -- type.  Per [[feedback_negative_findings_corpus_bound]] we take the
  -- WEAKEST sufficient principle, not full LEM:
  --
  --   * dec-proper — DECIDE whether N is proper.  Needed because
  --     IsSimple is ⊎-valued: the bridge must CHOOSE trivial-vs-whole,
  --     and a choice needs a decision, not mere ¬¬-stability.
  --   * ≈ε-stable / mem-stable — ¬¬-stability to FINISH each branch
  --     (turn "not-not in the identity / not-not a member" into the
  --     positive fact).
  --
  -- Full LEM is a strictly stronger instance (see `Classical` below);
  -- a finite/decidable trace discharges all three constructively (the
  -- next shadow — `Finite`, not yet built).
  ----------------------------------------------------------------------

  proper : {member : G → Set} → NormalSubgroup member → Set
  proper {member} N = ∃[ b ] (member b → ⊥)

  module Decidable
    (dec-proper : {member : G → Set} (N : NormalSubgroup member) → Dec (proper N))
    (≈ε-stable  : (a : G) → ((a ≈ ε → ⊥) → ⊥) → a ≈ ε)
    (mem-stable : {member : G → Set} (N : NormalSubgroup member) (b : G)
                → ((member b → ⊥) → ⊥)
                → member b)
    where

    -- The blocked converse, now PROVEN under the scoped hypotheses.
    -- Together with `simple→¬witness` this gives, in scope, the full
    -- equivalence  IsSimple ⟺ (NonSimplicityWitness → ⊥).
    ¬witness→simple : ({member : G → Set} → NonSimplicityWitness member → ⊥) → IsSimple
    ¬witness→simple no-wit N with dec-proper N
    ... | yes (b , b∉) =
          inj₁ (λ a a∈ → ≈ε-stable a (λ a≉ε →
            no-wit record
              { N = N ; wit-ntriv = a ; ntriv-∈ = a∈ ; ntriv-≉ε = a≉ε
              ; wit-prop = b ; prop-∉ = b∉ }))
    ... | no ¬proper =
          inj₂ (λ b → mem-stable N b (λ b∉ → ¬proper (b , b∉)))

  -- Full scoped LEM as a thin instance: decidability of every prop
  -- supplies dec-proper and both stabilities.  This realises the
  -- "introduce LEM, scoped" idea as a DERIVED instance of the minimal
  -- bridge — the classical knob, with the over-assumption made explicit.
  module Classical (lem : (P : Set) → Dec P) where
    open Decidable
      (λ N           → lem (proper N))
      (λ a           → from-¬¬ (lem (a ≈ ε)))
      (λ {member} N b → from-¬¬ (lem (member b)))
      public

  ----------------------------------------------------------------------
  -- Shadow 4.  The trace bridge.  `orbit` is the content that makes
  -- `in-class` a genuine conjugacy class: every class member is a
  -- conjugate of the representative.  (The base record only asserts
  -- rep ∈ its class and that conjugation preserves classes; this is
  -- the converse "the class IS the conjugation orbit of rep".)
  --
  -- Given it, every normal subgroup is CLASS-SATURATED: if it contains
  -- a class representative it contains the entire class.  Hence a
  -- normal subgroup is exactly a union of rep-classes — the recognizer
  -- genuinely reads the rep-class trace, not arbitrary element sets.
  -- PROVEN.
  ----------------------------------------------------------------------

  module WithOrbits
    (orbit : (c : Class) (h : G) → in-class c h →
             ∃[ g ] (((g · rep c) · (g ⁻¹)) ≈ h))
    where

    saturated :
      {member : G → Set} (N : NormalSubgroup member) (c : Class) →
      member (rep c) →
      (h : G) → in-class c h → member h
    saturated N c rep∈ h h∈c with orbit c h h∈c
    ... | (g , conj≈h) =
      NormalSubgroup.member-resp N conj≈h
        (NormalSubgroup.member-conj N g rep∈)

    --------------------------------------------------------------------
    -- Shadow 5.  The FINITE discharge — "recognizer over a trace" as an
    -- actual decision, with NO classical hypothesis.  When the
    -- rep-class trace is finite (Class ↔ Fin k), membership and "is the
    -- identity" are decidable, and every element lies in some class
    -- (cover), the three parameters of `Decidable` are THEOREMS, not
    -- assumptions:
    --
    --   * dec-proper — decided by SWEEPING the finite rep-class trace.
    --     Saturation collapses "∃ non-member element" to "∃ rep-class
    --     whose representative is a non-member", a finite search
    --     (Fin-∃?).  A found non-member rep IS the properness witness;
    --     if none, cover + saturation force every element into N.
    --   * ≈ε-stable / mem-stable — from decidability via dec→stable.
    --
    -- Result: `¬witness→simple` holds CONSTRUCTIVELY here.  This is the
    -- Bool face of the recognizer; the Decidable/Classical scopes are
    -- only needed when the trace is infinite.
    --------------------------------------------------------------------

    module Finite
      {k          : ℕ}
      (Class↔Fin  : Class ↔ Fin k)
      (cover      : (b : G) → ∃[ c ] in-class c b)
      (dec-≈ε     : (a : G) → Dec (a ≈ ε))
      (dec-member : {member : G → Set} (N : NormalSubgroup member) (b : G)
                  → Dec (member b))
      where

      open _↔_ Class↔Fin using (to; from; from-to)

      dec-proper : {member : G → Set} (N : NormalSubgroup member) → Dec (proper N)
      dec-proper {member} N
        with Fin-∃? (λ i → member (rep (from i)) → ⊥)
                    (λ i → dec-¬ (dec-member N (rep (from i))))
      ... | yes (i , ¬m) = yes (rep (from i) , ¬m)
      ... | no  h        = no prf
        where
          prf : proper N → ⊥
          prf (b , b∉) with cover b
          ... | (c , b∈c) with dec-member N (rep c)
          ...   | yes m = b∉ (saturated N c m b b∈c)
          ...   | no ¬m =
                  h (to c , subst (λ x → member (rep x) → ⊥)
                                  (sym (from-to c)) ¬m)

      ≈ε-stable : (a : G) → ((a ≈ ε → ⊥) → ⊥) → a ≈ ε
      ≈ε-stable a = from-¬¬ (dec-≈ε a)

      mem-stable : {member : G → Set} (N : NormalSubgroup member) (b : G)
                 → ((member b → ⊥) → ⊥)
                 → member b
      mem-stable N b = from-¬¬ (dec-member N b)

      -- The converse, now fully CONSTRUCTIVE (no LEM, no postulate).
      open Decidable dec-proper ≈ε-stable mem-stable public

------------------------------------------------------------------------
-- How a per-group simplicity claim becomes an instantiation
-- (shape only — the carrier construction is the algebra-side work):
--
--   A-coalgebra : ℕ → ConjugationCoalgebra {0ℓ}   -- construct Aₙ + its classes
--   _≈A_        : ...                              -- the carrier's equivalence
--   open Recognizer (A-coalgebra n) _≈A_
--
--   A-simple : (n : ℕ) → 5 ≤ n → IsSimple          -- the one-liner STATEMENT
--
-- `IsSimple` is shared verbatim across Aₙ, PSL(n,q), and the sporadic
-- carriers; only `A-coalgebra` and the witness differ.  The witness
-- for n ≥ 5 is real mathematics (it is the FINITE-trace recognizer
-- below applied to the 3-cycle generation argument), not free.
--
-- FINITE / decidable face (BUILT — `WithOrbits.Finite`, Shadow 5):
--   When `Class ↔ Fin k`, membership and _≈ ε_ are decidable, and the
--   classes cover the carrier, `Finite` discharges the three Decidable
--   parameters CONSTRUCTIVELY and re-exports `¬witness→simple` with no
--   classical hypothesis.  Properness is decided by sweeping the finite
--   rep-class trace (saturation collapses the element search to a class
--   search).  This is the recognizer "over a trace" as an actual
--   decision.  For infinite carriers (braids, Baumslag–Solitar) the
--   sweep need not terminate, so one falls back to the Decidable /
--   Classical scopes and `IsSimple` stays an Ω-valued observation.
--
--   (Conceptually equivalent normal-closure form: walk, for each
--   non-identity rep-class c, the closure ⟨⟨rep c⟩⟩ to a fixed point;
--   K is simple iff every such closure fills the group.)
------------------------------------------------------------------------
