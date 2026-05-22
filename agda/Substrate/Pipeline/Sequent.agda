------------------------------------------------------------------------
-- Substrate.Pipeline.Sequent
--
-- The structural rules of sequent calculus, lifted to the brick layer.
-- Every wire between two bricks IS a Sequent brick — a structural
-- derivation that the upstream's D-out is acceptable as the downstream's
-- D-in. In a properly-modelled pipeline, the wires are not implicit
-- (refl-proofs hiding in `compose`) but explicit bricks that the user
-- can inject, inspect, and modify.
--
-- The structural rules:
--
--   identity:   A ⊢ A           — the trivial wire (D-out ≡ D-in).
--   cut:        Γ ⊢ A   A ⊢ B   — composition (discharge intermediate).
--               ─────────────
--                  Γ ⊢ B
--   weakening:  Γ ⊢ A           — add an unused assumption to context.
--               ───────────
--               Γ, B ⊢ A
--   contraction: Γ, A, A ⊢ B    — merge duplicate assumptions.
--                ───────────
--                Γ, A ⊢ B
--   exchange:   Γ, A, B, Δ ⊢ C  — swap two assumptions in context.
--               ─────────────
--               Γ, B, A, Δ ⊢ C
--   coerce:     Γ ⊢ A   iso : A ≃ B  — apply a known isomorphism.
--               ──────────────────
--                     Γ ⊢ B
--
-- Each is realised as a Sequent brick with a `step` function that
-- implements the rule. Sequent bricks are pure transforms (no state)
-- and their primary witnessing is **D⇒D**: they transform data
-- without state, with Compute being their structural-rule label.
--
-- Per the substrate's category-theoretic discipline, this is the
-- substrate-honest read of "wires between bricks": every wire is a
-- 2-cell in the brick category, and the 2-cell IS a sequent
-- derivation. The pipeline is then a two-coloured composition:
--
--   brick ⟶ sequent ⟶ brick ⟶ sequent ⟶ brick ⟶ …
--
-- with the bricks doing computation and the sequents doing
-- type-coherence reasoning.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Sequent where

open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂; swap)
open import Substrate.Pipeline.Brick

------------------------------------------------------------------------
-- 1. The structural rules.
------------------------------------------------------------------------

data SequentRule : Set where
  identity    : SequentRule
  cut         : SequentRule
  weakening   : SequentRule
  contraction : SequentRule
  exchange    : SequentRule
  coerce      : SequentRule

------------------------------------------------------------------------
-- 2. A Sequent brick: pure transform with a structural-rule label.
--
-- A Sequent brick has no state (S-in = S-out = ⊤). Its step is its
-- derivation. The `rule` field names the structural rule it implements;
-- the `witnesses` is always D⇒D (we extend the original 6-axis schema
-- with the trivial morphism for pure data transforms — see note below).
--
-- Note: in the original 6-morphism schema, pure data-to-data transforms
-- are absorbed into D⇒S with S = ⊤. Sequents inherit that convention
-- but are tagged with their structural rule for inspection.
------------------------------------------------------------------------

record SequentType : Set₁ where
  field
    A : Set     -- input data type
    B : Set     -- output data type

sequent→BrickType : SequentType → BrickType
sequent→BrickType S = record
  { D-in  = SequentType.A S
  ; D-out = SequentType.B S
  ; S-in  = ⊤
  ; S-out = ⊤
  }

record Sequent (S : SequentType) : Set₁ where
  open SequentType S
  field
    rule       : SequentRule
    derivation : A → B
    -- Sequents preserve trivial state (S = ⊤). The homomorphism-tag
    -- for a sequent is its rule (informational).

-- A Sequent is a Brick.
sequent-as-brick : ∀ {S} → Sequent S → Brick (sequent→BrickType S)
sequent-as-brick {S} seq = record
  { witnesses = D⇒S  -- trivial S = ⊤, so D⇒S degenerates to D→D
  ; step      = λ (a , _) → Sequent.derivation seq a , tt
  ; homomorphism-tag = SequentRule  -- the rule itself names the
                                     -- structural property preserved
  }

------------------------------------------------------------------------
-- 3. The standard structural rules as concrete Sequents.
------------------------------------------------------------------------

-- Identity: A ⊢ A. The trivial wire — used when D-out and D-in are
-- the SAME type and no transformation is needed. This was the
-- implicit `refl` in compose; making it explicit here.
identity-sequent : (A : Set) → Sequent (record { A = A ; B = A })
identity-sequent A = record
  { rule       = identity
  ; derivation = λ a → a
  }

-- Weakening: A ⊢ A, B  (add an unused B to the context).
-- As a brick: input is A, output is A × B for some chosen B-value.
-- We need a B-value to do this. Provide it as a parameter.
weakening-sequent : (A B : Set) → B → Sequent (record { A = A ; B = A × B })
weakening-sequent A B b = record
  { rule       = weakening
  ; derivation = λ a → a , b
  }

-- Contraction: A, A ⊢ A (merge duplicate). Takes (A × A) and returns
-- one of them — we pick the first, but contraction is order-agnostic
-- when both copies are identical (which is the typical scenario).
contraction-sequent : (A : Set)
                    → Sequent (record { A = A × A ; B = A })
contraction-sequent A = record
  { rule       = contraction
  ; derivation = proj₁
  }

-- Exchange: A × B ⊢ B × A. Swap two parallel streams.
exchange-sequent : (A B : Set)
                 → Sequent (record { A = A × B ; B = B × A })
exchange-sequent A B = record
  { rule       = exchange
  ; derivation = swap
  }

-- Coercion: A ⊢ B via a named isomorphism. The user provides the
-- forward direction; the inverse is the consumer's responsibility
-- (e.g., for round-trip codecs, see Galois pairs in Brick.agda).
coerce-sequent : (A B : Set) → (A → B) → Sequent (record { A = A ; B = B })
coerce-sequent A B f = record
  { rule       = coerce
  ; derivation = f
  }

-- Cut: Γ ⊢ A and A ⊢ B yield Γ ⊢ B. As a brick: chain two derivations.
-- This is essentially function composition for sequents — the
-- structural-rule analog of compose in Composition.agda.
cut-sequent : ∀ {A B C : Set}
            → Sequent (record { A = A ; B = B })
            → Sequent (record { A = B ; B = C })
            → Sequent (record { A = A ; B = C })
cut-sequent s₁ s₂ = record
  { rule       = cut
  ; derivation = λ a → Sequent.derivation s₂ (Sequent.derivation s₁ a)
  }

------------------------------------------------------------------------
-- 4. Inserting a Sequent between two Bricks.
--
-- This is the structural promotion the user asked for: instead of
-- requiring D-out₁ ≡ D-in₂ directly, we permit any Sequent between
-- them whose A type matches D-out₁ and whose B type matches D-in₂.
-- The Sequent bridges the gap.
--
-- The composed brick's behaviour: run b₁, apply the sequent's
-- derivation, run b₂. State threading is preserved (we don't touch
-- S edges).
------------------------------------------------------------------------

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong)

-- For composition with sequents, we need both the sequent's A and B
-- to match the surrounding bricks. Specifying via `refl` proofs:
compose-via-sequent
  : ∀ {T₁ T₂ : BrickType}
  → (b₁ : Brick T₁)
  → (S : SequentType)
  → (seq : Sequent S)
  → (b₂ : Brick T₂)
  → BrickType.D-out T₁ ≡ SequentType.A S
  → SequentType.B S    ≡ BrickType.D-in  T₂
  → BrickType.S-out T₁ ≡ BrickType.S-in  T₂
  → Brick (record
      { D-in  = BrickType.D-in  T₁
      ; D-out = BrickType.D-out T₂
      ; S-in  = BrickType.S-in  T₁
      ; S-out = BrickType.S-out T₂
      })
compose-via-sequent {T₁} {T₂} b₁ S seq b₂ refl refl refl = record
  { witnesses = Brick.witnesses b₁
  ; step      = λ (d , s) →
                  let (d₁ , s₁) = Brick.step b₁ (d , s)
                      d₁'       = Sequent.derivation seq d₁
                  in Brick.step b₂ (d₁' , s₁)
  ; homomorphism-tag = ⊤
  }

------------------------------------------------------------------------
-- 5. The pipeline becomes a two-coloured chain.
--
-- A well-formed pipeline alternates bricks and sequents:
--
--   b₁  ⟶  seq₁₂  ⟶  b₂  ⟶  seq₂₃  ⟶  b₃  ⟶  …
--
-- Each sequent's A matches the preceding brick's D-out; each
-- sequent's B matches the following brick's D-in. Pipelines with
-- consecutive bricks of literally-identical types implicitly insert
-- identity-sequents.
--
-- This is the substrate's reading of "wire": a wire is not a passive
-- equality (refl) but an active structural derivation that justifies
-- the connection. When the derivation is trivial (identity), the wire
-- is bookkeeping. When the derivation is a coercion or projection,
-- the wire carries computational content.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 6. Fixed-point Sequents: derivation loops until canonical.
--
-- The substrate-honest reading of a Sequent: D-out is shunted back
-- to D-in repeatedly until the derivation reaches a FIXED POINT,
-- at which moment the Sequent admits the next symbol on D-in.
--
-- This is exactly the Coxeter `normalize` pattern: iterate until the
-- word is in canonical form, then accept the next observation. See
-- Substrate.Groups.FreeCyclic-Coxeter's `canonical-is-fixed-Free`:
--
--   canonical-is-fixed-Free : Canonical w → normalize w ≡ w
--
-- A Sequent in this kind has signature A → A (endofunction) with a
-- `canonical` predicate and a fixed-point obligation. The Sequent's
-- step is "iterate derivation until canonical."
--
-- Structural-rule Sequents (identity, cut, weakening, ...) are the
-- DEGENERATE case where `canonical = ⊤` (always canonical, no
-- iteration). General Sequents are the substrate's coalgebraic-
-- stability pattern realised at the brick layer.
------------------------------------------------------------------------

-- The canonical-form predicate and its fixed-point obligation.
record CanonicalSpec (A : Set) : Set₁ where
  field
    Canonical       : A → Set
    -- Obligation: derivation respects canonical forms.
    -- (Implementations must provide this proof — usually by induction
    -- on the canonical predicate.)
    canonical-fixed : (derivation : A → A)
                    → (a : A)
                    → Canonical a
                    → derivation a ≡ a

-- A fixed-point Sequent: endofunction + canonical-form witness.
record SequentFixed (A : Set) : Set₁ where
  field
    derivation : A → A
    spec       : CanonicalSpec A
    -- The obligation that this specific derivation respects spec's
    -- canonical predicate. Concrete instances prove this.
    obligation : (a : A) → CanonicalSpec.Canonical spec a
                          → derivation a ≡ a

-- Iteration with a step bound (so it's terminating-by-construction in Agda).
-- A step counter ensures termination; the canonical predicate is checked
-- at each step. Returns the result when canonical, or fails (Nothing) if
-- the bound is exceeded.
open import Substrate.Foundation.Maybe using (Maybe; just; nothing)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)

iterate-to-canonical
  : ∀ {A : Set}
  → (spec : CanonicalSpec A)
  → (decide : (a : A) → Maybe (CanonicalSpec.Canonical spec a))
  → (derivation : A → A)
  → ℕ            -- max iterations
  → A → Maybe A
iterate-to-canonical spec decide _    zero    _ = nothing
iterate-to-canonical spec decide deriv (suc n) a with decide a
... | just _  = just a
... | nothing = iterate-to-canonical spec decide deriv n (deriv a)

-- A fixed-point Sequent as a Brick: each call to step iterates the
-- derivation until canonical (within the step bound), then outputs
-- the canonical form. The brick admits the next input on D-in only
-- after the previous one has reached canonical form on D-out.
fixed-point-sequent→Brick
  : ∀ {A : Set}
  → (s : SequentFixed A)
  → (decide : (a : A) → Maybe (CanonicalSpec.Canonical (SequentFixed.spec s) a))
  → ℕ
  → Brick (record { D-in = A ; D-out = Maybe A ; S-in = ⊤ ; S-out = ⊤ })
fixed-point-sequent→Brick s decide n = record
  { witnesses = D⇒S  -- pure-transform shape; the iteration is internal
  ; step      = λ (a , _) → iterate-to-canonical (SequentFixed.spec s) decide
                              (SequentFixed.derivation s) n a , tt
  ; homomorphism-tag = SequentRule
  }

------------------------------------------------------------------------
-- 7. The two kinds together: structural-rule Sequents and fixed-point
--    Sequents are both Sequents. The unifying view:
--
--      A general Sequent has shape A → A (endofunction).
--      The derivation iterates until a canonical predicate holds.
--      The canonical predicate determines when iteration stops.
--      Structural-rule Sequents have canonical = ⊤ (always canonical,
--      zero iterations: pass through).
--      Normalising Sequents have a non-trivial canonical predicate
--      (e.g., "this word has no doubled generators" for the Coxeter
--      normalizer).
--
-- A Sequent brick in a pipeline thus has TWO temporal scales:
--
--   * Inner loop: derivation iterates on the current value until
--     canonical. The brick is "busy" during this loop.
--   * Outer step: when canonical is reached, the brick produces D-out
--     and is ready to accept the next D-in.
--
-- This matches the substrate's coalgebraic step: each observation
-- on D-in triggers an inner-loop unfold to canonical, after which
-- the brick's state is in a subcoalgebra fixed point.
--
-- Related: see [[project_tetrative_metacircularity]] — the same
-- fixed-point pattern recurses at higher meta-levels.

------------------------------------------------------------------------
-- 8. Connection to the substrate's category theory.
--
-- The sequent calculus is the proof-theoretic underpinning of
-- categories. In a category C, an arrow f : A → B is a derivation
-- of B from A. The structural rules (identity, cut, weakening, etc.)
-- ARE the category's primitive operations (identity arrow,
-- composition, product/coproduct projection-injection, etc.).
--
-- The brick architecture's `compose` is the cut rule made explicit
-- at the runtime layer. The Sequent module makes ALL the structural
-- rules explicit at the brick layer.
--
-- For the codec, the practical sequents are:
--   * identity   — when types match literally (most "wires").
--   * coerce     — when types are isomorphic via a named transform.
--   * exchange   — when two parallel streams need to be swapped
--                   (e.g., to feed a Chooser's two arguments).
--   * weakening  — when a downstream brick needs additional context
--                   the upstream didn't provide (a "freshness" stamp,
--                   a default state value, etc.).
--   * contraction — when two parallel streams must be merged before
--                    the next brick consumes them.
--   * cut         — recursive composition of sequents (the rest of
--                    the structural rules build out from cut).
------------------------------------------------------------------------
