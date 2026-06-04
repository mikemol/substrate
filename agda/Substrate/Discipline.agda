------------------------------------------------------------------------
-- Substrate.Discipline
--
-- The clarified foundation's discipline rules, expressed as theorems
-- and structural claims at the Agda type level. This module is the
-- explicit bridge between catalog/clarified_foundation.md § Discipline
-- rules and the cocycle abstractions in Substrate.Cocycle.
--
-- Rules that the type system mechanically enforces (or makes
-- structurally available):
--
--   Rule 1  (gauge-versus-invariant separation):
--     The Σ-type structure of TotalSpace separates Invariant from
--     Fiber as distinct types; projecting TotalSpace → Invariant is
--     definitionally gauge-equivariant.
--
--   Rule 5  (content-address by invariant only):
--     Any gauge-invariant function on TotalSpace is determined by
--     its values on invariants — two fiber elements over the same
--     invariant receive equal values under any gauge-invariant
--     function. Proved via torsor transitivity.
--
--   Rule 11 (isomorphic-storage vs orbit-collapse-with-virtual-recovery):
--     The ICS → WCS direction is functorial (Downcast). The reverse
--     requires a Section — a choice of canonical representative per
--     invariant. Section IS the Type-D rigidification move; ICS has
--     no Section field, making rigidification literally inexpressible
--     in the strong-discipline shape.
--
-- Rules not encoded here (because they live above the abstraction
-- layer — naming conventions, parameterisation, audit framing — and
-- become documentation conventions inside each instance rather than
-- type-level obligations on the abstraction):
--
--   Rule 2  (empty-bridge prohibition):    naming
--   Rule 3  (AXES parametrisation):        naming
--   Rule 4  (anchor parametrisation):      naming
--   Rule 6  (PAIRINGS labels):             naming
--   Rule 7  (bit-position layout):         naming
--   Rule 8  (chirality sign convention):   naming
--   Rule 9  (existence-form findings):     audit framing
--   Rule 10 (charter discipline):          audit framing
--
-- See: catalog/clarified_foundation.md § Discipline rules.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Discipline where

open import Substrate.Foundation.Product using (Σ; Σ-syntax; _,_; proj₁; proj₂; ∃; -,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Cocycle as Cocycle
  using (IsomorphicCocycleStructure; WeakCocycleStructure;
         Action; IsTorsor)

------------------------------------------------------------------------
-- Rule 1 — Gauge-versus-invariant separation.
--
-- For any IsomorphicCocycleStructure, the projection to Invariant is
-- gauge-equivariant. The catalog's text version of this rule:
--
--   "Every [gauge] item must appear in code as a parameter or
--    convention comment, never as a verified contract or content-
--    address."
--
-- At the Agda level, the structural separation already lives in the
-- type signature of ICS: Invariant and Fiber are distinct types, and
-- TotalSpace = Σ Invariant Fiber. The projection is `proj₁` —
-- inherently gauge-invariant because total-act only affects the
-- second component.
------------------------------------------------------------------------

module Rule1 (𝒞 : IsomorphicCocycleStructure) where

  open IsomorphicCocycleStructure 𝒞
  open Cocycle.Downcast 𝒞

  -- The named claim. Reduces to refl by construction.
  project-gauge-equivariant :
    (g : SetoidGroup.Carrier Gauge) (x : TotalSpace) →
    project (total-act g x) ≡ project x
  project-gauge-equivariant = proj-gauge-inv

  -- Constructive corollary: every function on Invariant lifts to a
  -- gauge-invariant function on TotalSpace. This is the "canonical
  -- way to address by invariant" — a function whose contract speaks
  -- only of the invariant cannot, by typing, depend on the fiber.
  lift-from-invariant :
    ∀ {ℓa} {A : Set ℓa} (f : Invariant → A) → TotalSpace → A
  lift-from-invariant f x = f (project x)

  lift-is-gauge-invariant :
    ∀ {ℓa} {A : Set ℓa} (f : Invariant → A)
    (g : SetoidGroup.Carrier Gauge) (x : TotalSpace) →
    lift-from-invariant f (total-act g x) ≡ lift-from-invariant f x
  lift-is-gauge-invariant f g x = cong f (project-gauge-equivariant g x)

------------------------------------------------------------------------
-- Rule 5 — Content-address by invariant only.
--
-- Any gauge-invariant function on TotalSpace takes equal values on
-- any two elements of the same fiber. The catalog's text version:
--
--   "Receipts content-address by orbit_key (V_4-invariant), never by
--    v4_delta (which encodes the canonical choice). v4_delta is
--    derivable from (signature, canonical-choice-function) and can
--    be recomputed if needed; it is not part of the address."
--
-- The Agda statement, made precise: a gauge-invariant function
-- cannot distinguish between two fiber elements over the same
-- invariant. Proved via the torsor's transitivity (= the gauge can
-- move between any two fiber elements over the same invariant).
------------------------------------------------------------------------

module Rule5 (𝒞 : IsomorphicCocycleStructure) where

  open IsomorphicCocycleStructure 𝒞
  open Cocycle.Downcast 𝒞

  -- The named theorem.
  content-by-invariant :
    ∀ {ℓa} {A : Set ℓa}
    (f : TotalSpace → A) →
    ((g : SetoidGroup.Carrier Gauge) (x : TotalSpace) →
     f (total-act g x) ≡ f x) →
    (i : Invariant) (t₁ t₂ : Fiber i) →
    f (i , t₁) ≡ f (i , t₂)
  content-by-invariant f f-inv i t₁ t₂
    with IsTorsor.transitive (fiber-torsor i) t₁ t₂
  -- By torsor transitivity, the witness g sends t₁ to t₂.
  -- Then f (i , t₂) = f (i , g · t₁) = f (total-act g (i , t₁))
  --                 = f (i , t₁)  (by gauge-invariance).
  ... | g , g·t₁≡t₂ =
    trans (sym (f-inv g (i , t₁)))
          (cong (λ t → f (i , t)) g·t₁≡t₂)

------------------------------------------------------------------------
-- Rule 11 — Isomorphic-storage vs orbit-collapse-with-virtual-recovery.
--
-- Two disciplines, asymmetric in the type structure:
--
--   * Strong (isomorphic storage)        = IsomorphicCocycleStructure
--     No section field. The total space IS Σ Invariant Fiber by
--     construction; there is no "canonical-per-orbit" coordinate to
--     pick. Rigidification is inexpressible.
--
--   * Weak (orbit-collapse + virtual recovery) = WeakCocycleStructure
--     Has Base, Invariant, project. A `Section` (defined below) is
--     OPTIONAL extra data: a chosen canonical representative per
--     invariant. With a Section, the structure becomes a Type-D
--     rigidification candidate.
--
-- The ICS → WCS direction is functorial (Substrate.Cocycle.Downcast):
-- no choices required. The reverse direction requires (a) a section
-- AND (b) a torsor structure on each fiber-as-orbit — neither comes
-- for free from a WCS.
--
-- The catalog's text version:
--   "The strong version eliminates rather than fixes the Type-D
--    verifier-contract rigidification at CY-5."
--
-- "Eliminates" at the Agda level: ICS has no Section field; one
-- cannot SHOW a section without leaving the strong shape.
------------------------------------------------------------------------

-- A Section of a weak cocycle structure: a choice of canonical
-- representative per invariant. The Type-D rigidification move.
record Section (𝒲 : WeakCocycleStructure) : Set where      -- ⟦shape:1650cc88 representative,projects-to⟧
  open WeakCocycleStructure 𝒲
  field
    -- The chosen canonical for each invariant.
    representative : Invariant → Base
    -- The choice actually lands in the right orbit.
    projects-to   : (i : Invariant) → project (representative i) ≡ i

------------------------------------------------------------------------
-- The asymmetry, made structural: every ICS Downcasts to a WCS, but
-- adding a Section to the result is an ACTIVE CHOICE that the strong
-- discipline rejects.
------------------------------------------------------------------------

module Rule11 where

  -- ICS → WCS is functorial (no choices). Re-export Downcast.weak
  -- here under the rule's name.
  strong-to-weak :
    IsomorphicCocycleStructure → WeakCocycleStructure
  strong-to-weak 𝒞 = Cocycle.Downcast.weak 𝒞

  -- A "rigidified" weak cocycle: a WCS bundled with a Section.
  -- This is what the strong discipline forbids by structural absence:
  -- there is no slot in ICS where a Section would go.
  record RigidifiedWCS : Set₁ where
    field
      base       : WeakCocycleStructure
      section    : Section base

------------------------------------------------------------------------
-- Demonstration: applying the rules to our three cocycle instances.
--
-- These re-open Rule1, Rule5, Rule11 with each specific cocycle. The
-- payoff is that the imports themselves type-check, confirming the
-- rules are applicable to all three instances we've constructed.
------------------------------------------------------------------------

module Demo where

  open import Substrate.Cocycles.V4Signature
    using (CY5-V4Signature)
  open import Substrate.Cocycles.F2CubedPuncturing
    using (F2³-Puncturing-Cocycle)
  open import Substrate.Cocycles.KRule
    using (KRule-Cocycle)

  -- CY-5: strong cocycle, all three rules apply at the ICS level.
  module CY5 where
    open Rule1 CY5-V4Signature public
    open Rule5 CY5-V4Signature public
    weak : WeakCocycleStructure
    weak = Rule11.strong-to-weak CY5-V4Signature

  -- CY-4: strong cocycle, all three rules apply at the ICS level.
  module CY4 where
    open Rule1 F2³-Puncturing-Cocycle public
    open Rule5 F2³-Puncturing-Cocycle public
    weak : WeakCocycleStructure
    weak = Rule11.strong-to-weak F2³-Puncturing-Cocycle

  -- CY-2: weak cocycle. Rule 1's "project is gauge-invariant" is
  -- directly a field of WCS (project-gauge-invariant). Rule 5
  -- doesn't apply at the WCS level (no fiber structure). Rule 11's
  -- Section type IS applicable — but we don't construct one, because
  -- doing so would be the rigidification move.
  --
  -- (See KRule-Cocycle's `project-gauge-invariant` field for Rule 1.)
  --
  -- Demonstration: a Section on CY-2 (for n = 2) WOULD have shape:
  --   representative diagonal     = (zero , zero)
  --   representative off-diagonal = (zero , suc zero)
  -- We don't construct it here — the absence IS the discipline.

------------------------------------------------------------------------
-- Notes
--
-- 1. The "rules-as-types" encoding is conservative: the type system
--    catches structural violations (e.g., trying to construct a
--    section on ICS — there's no slot for it), but doesn't enforce
--    naming or audit conventions (rules 2, 3, 4, 6, 7, 8, 9, 10).
--    Those remain documentation conventions inside each instance.
--
-- 2. Rule 5's `content-by-invariant` is the load-bearing theorem of
--    this module: it formally proves what the catalog asserts about
--    receipts and addressing. The proof exploits torsor transitivity
--    — the strong-discipline structure delivers exactly the fact
--    needed for the rule to hold.
--
-- 3. Rule 11's asymmetry (no Section field on ICS, optional Section
--    on WCS) is the type-level expression of the catalog's claim:
--    "The strong version eliminates rather than fixes the Type-D
--    verifier-contract rigidification." The elimination is
--    structural — the rigidification has no home in the type.
--
-- 4. Cross-references:
--    - catalog/clarified_foundation.md § Discipline rules
--    - catalog/cocycles.md § Isomorphic storage
--    - Substrate.Cocycle — the abstractions this module quantifies
--      over (ICS, WCS, Downcast)
--    - Substrate.Cocycles.{V4Signature, F2CubedPuncturing, KRule}
--      — the three instances over which Demo demonstrates the rules
------------------------------------------------------------------------
