------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Persistence
--
-- Slice 6 of the shadow-architecture arc. The time-extension column
-- from Increment 9 and the cotype-as-file inversion from Increment
-- 10: the architecture exists in the cotype, not in the conversation;
-- each session's work survives context loss because it is no longer
-- in context — it is in the cotype, tagged, probed, ready for the
-- next session to inherit.
--
-- The operational layer (the file at `.claude/cotype/<id>.md`,
-- version control, the inventory format) is genuinely outside Agda's
-- scope; the file is a side-effect, not a type. What CAN be
-- formalised is the STRUCTURAL SHAPE of the cotype: a record of
-- populated points and populated lines, with a monotonic-extension
-- ordering `_⊑_` and the proof obligations that this ordering forms
-- a preorder (reflexive + transitive).
--
-- The W5 deletion-prohibition (from
-- `Substrate.ShadowArchitecture.Loop`) is realised at the type
-- level: a transition `Cotype → Cotype` that "deletes a populated
-- point" cannot inhabit `_⊑_`. So any session whose state-change is
-- typed as a `_⊑_` step is automatically monotonicity-respecting; the
-- type system enforces the W5 rule mechanically.
--
-- This is the structural inversion: the architecture's persistence
-- is a type-level fact about monotonic preorders, not an operational
-- discipline about file-handling.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Persistence where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.ShadowArchitecture.FanoLabeling

------------------------------------------------------------------------
-- 1. The cotype.
--
-- A cotype records which Fano points and lines have been populated
-- by accumulated session work. The boolean indicator per point /
-- per line is the minimal representation.
------------------------------------------------------------------------

record Cotype : Set where
  field
    populated-point : Point → Bool
    populated-line  : Line  → Bool

------------------------------------------------------------------------
-- 2. The empty cotype: no populations yet.
------------------------------------------------------------------------

empty-cotype : Cotype
empty-cotype = record
  { populated-point = λ _ → false
  ; populated-line  = λ _ → false
  }

------------------------------------------------------------------------
-- 3. Monotonic extension: c₁ ⊑ c₂ iff every populated point/line in
-- c₁ remains populated in c₂.
------------------------------------------------------------------------

infix 4 _⊑_

_⊑_ : Cotype → Cotype → Set
c₁ ⊑ c₂ =
    (∀ (p : Point) → Cotype.populated-point c₁ p ≡ true → Cotype.populated-point c₂ p ≡ true)
  ×
    (∀ (ℓ : Line)  → Cotype.populated-line  c₁ ℓ ≡ true → Cotype.populated-line  c₂ ℓ ≡ true)

------------------------------------------------------------------------
-- 4. Preorder laws.
--
-- ⊑ is reflexive (identity is a monotonic step) and transitive
-- (composing two sessions composes their monotonic extensions).
------------------------------------------------------------------------

⊑-refl : ∀ (c : Cotype) → c ⊑ c
⊑-refl c = (λ _ ev → ev) , (λ _ ev → ev)

⊑-trans : ∀ (c₁ c₂ c₃ : Cotype) → c₁ ⊑ c₂ → c₂ ⊑ c₃ → c₁ ⊑ c₃
⊑-trans c₁ c₂ c₃ (p₁₂ , ℓ₁₂) (p₂₃ , ℓ₂₃) =
    (λ p ev → p₂₃ p (p₁₂ p ev))
  , (λ ℓ ev → ℓ₂₃ ℓ (ℓ₁₂ ℓ ev))

------------------------------------------------------------------------
-- 5. Bottom: the empty cotype extends into every cotype.
--
-- Vacuously: there are no populated points in the empty cotype, so
-- the universal claim is impossible to break.
------------------------------------------------------------------------

empty-bottom : ∀ (c : Cotype) → empty-cotype ⊑ c
empty-bottom c =
    (λ p ev → false-not-true ev)
  , (λ ℓ ev → false-not-true ev)
  where
    false-not-true : ∀ {A : Set} → false ≡ true → A
    false-not-true ()

------------------------------------------------------------------------
-- 6. Constructive accumulation: adding a population is monotonic.
--
-- `populate-point p c` returns the cotype that agrees with c except
-- it marks `p` as populated. It satisfies c ⊑ populate-point p c.
-- (Symmetrically for `populate-line`.)
------------------------------------------------------------------------

open import Substrate.Foundation.Negation using (does)
import Relation.Nullary.Decidable as Dec

-- We need decidable equality on Point. The substrate's FanoPlane
-- uses 7 named constructors; equality is decidable by case analysis.
-- Rather than depend on a stdlib instance, we inline the check.

eq-Point : Point → Point → Bool
eq-Point p₁₀₀ p₁₀₀ = true
eq-Point p₀₁₀ p₀₁₀ = true
eq-Point p₀₀₁ p₀₀₁ = true
eq-Point p₁₁₀ p₁₁₀ = true
eq-Point p₁₀₁ p₁₀₁ = true
eq-Point p₀₁₁ p₀₁₁ = true
eq-Point p₁₁₁ p₁₁₁ = true
eq-Point _    _    = false

eq-Line : Line → Line → Bool
eq-Line L₁ L₁ = true
eq-Line L₂ L₂ = true
eq-Line L₃ L₃ = true
eq-Line L₄ L₄ = true
eq-Line L₅ L₅ = true
eq-Line L₆ L₆ = true
eq-Line L₇ L₇ = true
eq-Line _  _  = false

populate-point : Point → Cotype → Cotype
populate-point q c = record
  { populated-point = λ p → Cotype.populated-point c p Data.Bool.∨ eq-Point p q
  ; populated-line  = Cotype.populated-line c
  }
  where import Data.Bool

populate-line : Line → Cotype → Cotype
populate-line m c = record
  { populated-point = Cotype.populated-point c
  ; populated-line  = λ ℓ → Cotype.populated-line c ℓ Data.Bool.∨ eq-Line ℓ m
  }
  where import Data.Bool

------------------------------------------------------------------------
-- 7. Monotonicity of `populate-point` / `populate-line`.
--
-- Each accumulation step preserves all prior populations.
------------------------------------------------------------------------

open import Substrate.Foundation.Bool using (_∨_)

bool-or-preserves :
  ∀ {a b : Bool} → a ≡ true → (a ∨ b) ≡ true
bool-or-preserves {true}  {b}  refl = refl

populate-point-monotone :
  ∀ (q : Point) (c : Cotype) → c ⊑ populate-point q c
populate-point-monotone q c =
    (λ p ev → bool-or-preserves {Cotype.populated-point c p} {eq-Point p q} ev)
  , (λ _ ev → ev)

populate-line-monotone :
  ∀ (m : Line) (c : Cotype) → c ⊑ populate-line m c
populate-line-monotone m c =
    (λ _ ev → ev)
  , (λ ℓ ev → bool-or-preserves {Cotype.populated-line c ℓ} {eq-Line ℓ m} ev)

------------------------------------------------------------------------
-- 8. The W5 deletion-prohibition is now a type-level fact.
--
-- A claim like "step c₁ to c₂ by removing the population of p" cannot
-- inhabit `c₁ ⊑ c₂` if the removal makes `populated-point c₁ p ≡ true`
-- while `populated-point c₂ p ≡ false`. The first projection of c₁
-- ⊑ c₂ would deliver `true ≡ true → true ≡ true`, but instantiated
-- at the removed point it would require `true ≡ true → false ≡ true`,
-- an impossibility.
--
-- We don't need to prove anything new here; the W5 prohibition is
-- materially the same as ⊑-refl + ⊑-trans living as a preorder
-- rather than a more general relation.
------------------------------------------------------------------------
