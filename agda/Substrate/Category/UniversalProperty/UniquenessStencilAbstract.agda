{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.UniquenessStencilAbstract — ⟡uniqueness-stencil-
-- abstract: the GENERIC uniqueness stencil over ANY Lawvere fixed-point, dissolving the
-- cross-form difficulty (Trace vs RealTrace vs Fam) the CrossMul way.
--
-- THE CROSS-FORM DIFFICULTY (operator): the first two layers are PER-SOURCE (for each
-- start state s, the target is uniquely determined), while the ν-whole layer is at the
-- MAP level (any map h satisfying the head/tail agreement is equivalent to the whole
-- solution). Unifying the CARRIERS (Trace/RealTrace/Fam) is the wrong move — it is the
-- cross-form wall.
--
-- THE CrossMul DISSOLUTION (grounded in Wedge.CrossMul): CrossMix is a COSPAN A → R ← B —
-- two carriers meet in a common R via Bridges (codecs), NEVER unified. R is GIVEN. So here
-- the stencil abstracts over the carrier POLYMORPHICALLY: each layer is a UNIQUENESS-INTO-A-
-- TARGET whose EQUALITY-RELATION (≡ for μ/step, ~ for ν-whole) is a PARAMETER — the codec
-- into a common "answer" relation, not a unified carrier. And the per-source / map-level
-- split is the ARROW-CATEGORY level: a per-source layer quantifies the SOURCE (an object of
-- the arrow category); a map-level layer quantifies the MAP (a morphism). Same stencil, two
-- quantification levels — exactly why the repo is grounded in arrow categories + allegory.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.UniquenessStencilAbstract where

open import Substrate.Foundation.Eq using (_≡_)

------------------------------------------------------------------------
-- ① THE POLYMORPHIC LAYER SHAPES. A layer is a uniqueness statement RELATIVE TO a target
-- relation Rel (the "frame": ≡ or ~) — abstracting over the carrier, NOT unifying it (the
-- CrossMul move: the relation is the common R the carriers bridge into).
------------------------------------------------------------------------

-- PER-SOURCE layer (μ-fold, ν-step): for each source s, any admissible answer t agreeing
-- (via Wit) with the solver IS the solve — up to Rel. Quantifies the SOURCE (arrow-cat OBJECT).
-- Adm gates it (⊤ for μ unconditional, a bound for ν-step) — the CrossMul "coherence" slot.
PerSource :
  {S T : Set}                              -- source / target carriers (POLYMORPHIC — not unified)
  (Rel   : T → T → Set)                    -- the frame relation on the target (≡ here)
  (solve : S → T)                          -- the solver
  (Adm   : S → T → Set)                    -- the admissibility gate (⊤ / bound)
  (Wit   : S → T → Set)                    -- the witness spec
  → Set
PerSource {S} {T} Rel solve Adm Wit =
  (s : S) (t : T) → Adm s t → Wit s t → Rel t (solve s)

-- MAP-LEVEL layer (ν-whole): any map h into the target agreeing (via the coalgebra Agree
-- conditions) with the canonical solution is Rel-equivalent to it, AT EVERY source.
-- Quantifies the MAP h (arrow-cat MORPHISM), not the source — the level the ν-whole needs.
MapLevel :
  {S T : Set}
  (Rel  : T → T → Set)                     -- the frame relation (~ here)
  (canon : S → T)                          -- the canonical (whole) solution — e.g. ana
  (Agree : (S → T) → Set)                  -- the head/tail agreement conditions on a map h
  → Set
MapLevel {S} {T} Rel canon Agree =
  (h : S → T) → Agree h → (s : S) → Rel (h s) (canon s)

------------------------------------------------------------------------
-- ② THE ABSTRACT STENCIL: a Lawvere fixed-point's uniqueness = THREE layers over TWO
-- frames, carriers POLYMORPHIC (the CrossMul cospan: each layer bridges into its frame's
-- relation, carriers never unified). μ-fold + ν-step are PER-SOURCE (≡ frame); ν-whole is
-- MAP-LEVEL (~ frame). The ≡/~ asymmetry is STRUCTURAL: two PerSource + one MapLevel.
------------------------------------------------------------------------
record UniquenessStencil : Set₁ where
  field
    -- the μ carriers/relation (≡ frame, inductive)
    Sμ Tμ    : Set
    Relμ     : Tμ → Tμ → Set
    -- the ν-whole carriers/relation (~ frame, coinductive) — DIFFERENT carriers, NOT unified
    Sν Tν    : Set
    Relν     : Tν → Tν → Set
    -- LAYER 1 — μ-fold: per-source, UNCONDITIONAL (Adm = ⊤-like, folded into the field).
    μ-fold   : {solve : Sμ → Tμ} {Adm : Sμ → Tμ → Set} {Wit : Sμ → Tμ → Set}
               → PerSource Relμ solve Adm Wit
    -- LAYER 2 — ν-step: per-source, BOUNDED (Adm = the smallness bound).
    ν-step   : {solve : Sμ → Tμ} {Adm : Sμ → Tμ → Set} {Wit : Sμ → Tμ → Set}
               → PerSource Relμ solve Adm Wit
    -- LAYER 3 — ν-whole: MAP-LEVEL, up-to Relν (~). The carrier is Sν/Tν (coinductive form).
    ν-whole  : {canon : Sν → Tν} {Agree : (Sν → Tν) → Set}
               → MapLevel Relν canon Agree

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the cross-form wall dissolved by CrossMul-style
-- polymorphism, not carrier-unification): the abstract stencil abstracts over the carriers
-- (Sμ/Tμ for the ≡ frame, Sν/Tν for the ~ frame) POLYMORPHICALLY — they are NEVER unified
-- (no Trace ≟ RealTrace ≟ Fam), exactly as CrossMix meets two carriers in a common R via
-- codecs without unifying them. Each layer bridges into its FRAME RELATION (Relμ = ≡,
-- Relν = ~) — the relation is the common "answer" target, the CrossMul R. The per-source /
-- map-level split is the ARROW-CATEGORY level: PerSource quantifies the SOURCE (an object),
-- MapLevel quantifies the MAP h (a morphism) — which is why the repo is grounded in arrow
-- categories + allegory: the ν-whole's map-level uniqueness IS a statement about morphisms
-- into the terminal object, not about a unified carrier. The ≡/~ asymmetry is STRUCTURAL:
-- TWO PerSource layers (μ-fold ≡, ν-step ≡) + ONE MapLevel layer (ν-whole ~). The either/or
-- "unify the carriers vs give up on the abstract stencil" DISSOLVES: neither — abstract
-- over the carriers polymorphically and bridge each layer into its frame relation (the
-- CrossMul cospan), and the three concrete instances (trace/wedge, Kleene, fixpoint)
-- inhabit UniquenessStencil by supplying their own Sμ/Tμ/Sν/Tν/Rel + the three layer proofs
-- — WITHOUT their carriers ever being made equal. The generic module is REAL: the cross-
-- form difficulty was a false wall, dissolved by the arrow-category/CrossMul polymorphism.
------------------------------------------------------------------------
