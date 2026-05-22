------------------------------------------------------------------------
-- Substrate.Category.GTorsor
--
-- The G-torsor categorical primitive: a set X with a free transitive
-- right-action of a group G. Equivalently, a "principal G-bundle over
-- a point" — the data-side analogue of a coset space where the
-- specific basepoint is unfixed.
--
-- Substrate primitive joining Cone / FieldBond / FieldTower /
-- FieldFanOut in the categorical primitive ladder. Used to capture
-- gauge-freedom spaces structurally: any space of "structurally-
-- equivalent representations" forms a torsor over the group of
-- structure-preserving symmetries.
--
-- The motivating substrate instance:
-- Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor —
-- the space of F₂-linear bijections Vector 3 ↔ SelfDual is a
-- GL(3, F₂)-torsor of order 168, packaging the original gauge
-- freedom of [[reserved-selfdual-bijection-gauge]] as a single
-- universal-property object.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- "G-torsor" IS the standard categorical name. The universal property
-- is the free + transitive action structure.
--
-- Per [[expose-generator-not-orbit]]: the action IS the generator;
-- the orbit (full set of points) is automatically reachable from
-- any basepoint via the action.
--
-- Scope discipline: this slice defines the abstract primitive with
-- minimum axioms. Specific instances (GaugeTorsor at HodgeDim4,
-- V₄-coset structures, etc.) land in dedicated instance modules.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GTorsor where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

-- (Level variables introduced per-record / per-function below.)

------------------------------------------------------------------------
-- 1. GTorsor — the record.
--
-- Parameters: a group (G, _·G_, εG) with carrier-level equivalence
-- _≈G_ and a carrier X with equivalence _≈X_. The record bundles a
-- right-action (act : G → X → X) with the action axioms (act-εG = id,
-- act-·G = composition) plus the torsor properties: transitive (any
-- two points are related by some g) and free (that g is unique).
--
-- Equivalences are taken as parameters rather than fixing
-- propositional equality, because substrate carriers often carry
-- functional content (e.g., GL3F2 records hold Linear maps whose
-- equality requires funext); pointwise / structural equivalences
-- side-step the funext dependency per substrate discipline.
--
-- Group axioms (associativity, identity, inverse) are presupposed —
-- the user supplies a genuine group structure on G when constructing
-- a GTorsor. Substrate-pattern minimum-axioms record.
------------------------------------------------------------------------

record GTorsor {ℓG ℓX ℓEG ℓEX : Level}
               (G : Set ℓG) (X : Set ℓX)
               (_·G_ : G → G → G) (εG : G)
               (_≈G_ : G → G → Set ℓEG)
               (_≈X_ : X → X → Set ℓEX) :
               Set (ℓG ⊔ ℓX ⊔ ℓEG ⊔ ℓEX) where
  constructor mkGTorsor
  field
    act         : G → X → X
    act-id      : (x : X) → act εG x ≈X x
    act-·G      : (g h : G) (x : X) → act (g ·G h) x ≈X act g (act h x)
    transitive  : (x y : X) → Σ G (λ g → act g x ≈X y)
    free        : (x : X) (g₁ g₂ : G) → act g₁ x ≈X act g₂ x → g₁ ≈G g₂

open GTorsor public

------------------------------------------------------------------------
-- 2. Derived: from a basepoint, every torsor element is reachable.
--
-- This is just the transitive field bundled with named projections;
-- included for downstream readability and to expose the "orbit-of-
-- basepoint = full set" fact via clean accessors.
------------------------------------------------------------------------

orbit-element :
  {ℓG ℓX ℓEG ℓEX : Level}
  {G : Set ℓG} {X : Set ℓX} {_·G_ : G → G → G} {εG : G}
  {_≈G_ : G → G → Set ℓEG} {_≈X_ : X → X → Set ℓEX}
  (τ : GTorsor G X _·G_ εG _≈G_ _≈X_) →
  (x₀ x : X) → G
orbit-element τ x₀ x = proj₁ (transitive τ x₀ x)

orbit-element-act :
  {ℓG ℓX ℓEG ℓEX : Level}
  {G : Set ℓG} {X : Set ℓX} {_·G_ : G → G → G} {εG : G}
  {_≈G_ : G → G → Set ℓEG} {_≈X_ : X → X → Set ℓEX}
  (τ : GTorsor G X _·G_ εG _≈G_ _≈X_) →
  (x₀ x : X) → _≈X_ (act τ (orbit-element τ x₀ x) x₀) x
orbit-element-act τ x₀ x = proj₂ (transitive τ x₀ x)

------------------------------------------------------------------------
-- 3. Capstone — substrate primitive ready for instances.
--
-- The motivating instance:
--
--   Substrate.Algebra.F2.HodgeDim4.ReservedBridge.GaugeTorsor —
--   X = F₂-linear bijections Vector 3 ↔ SelfDual
--   G = GL(3, F₂) (= GL3F2 with multiplication = composition)
--   act g φ = φ ∘ apply (L g)   (pre-composition by the linear
--                                 endomorphism's apply function)
--   transitive: any other bijection ψ matches via g = φ⁻¹ ∘ ψ
--   free: pre-composition by g₁ vs g₂ agreeing on the basepoint
--         φ implies g₁ = g₂ (by φ's bijectivity)
--
-- After this primitive lands, the substrate's gauge-freedom space at
-- HodgeDim4 (and analogous gauge spaces elsewhere) is no longer "168
-- ad-hoc alternatives" — it's the single object "a GL(3, F₂)-torsor
-- with a chosen basepoint" with orbit elements (Alt-A, Alt-B,
-- Sylow-canonical bridges) as named witnesses, not as primitive
-- definitions.
------------------------------------------------------------------------
