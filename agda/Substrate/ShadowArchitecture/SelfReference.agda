------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.SelfReference
--
-- Slice 1.4 of the shadow-architecture arc. The two ★ load-bearing
-- self-references in the Fano plane that the shadow-architecture
-- document surfaces as architectural facts (Increments 2-3, 7):
--
--   ★ L₆-normal = 110 (mediated-composite). L₆ = {001, 110, 111}
--     is the "guard-reconstitution" line. Its normal-vector 110 is
--     also a point ON L₆, so L₆ is self-incident through its normal.
--     Operational reading: the redirect target of the guard's
--     "001 alone" rejection is 110 specifically because 110 is
--     perpendicular to L₆ AND lies on L₆.
--
--   ★ L₇-normal = 111 (triadic-full). L₇ = {110, 101, 011} is the
--     "pure-composite-diagonal" — the only line whose points are all
--     weight-2. Its normal-vector 111 is NOT on L₇, so L₇ is
--     non-self-incident; together {111, L₇} form a non-incident
--     S₃-fixed pair.
--
-- These two facts are the architectural pivots: L₆ carries the
-- guard-reconstitution semantics; L₇ carries the S₃-symmetric core.
--
-- Both close by `refl` (or by constructor disjointness for the
-- non-incidence) given the definitions in `Duality` and
-- `FanoLabeling`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.SelfReference where

open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.ShadowArchitecture.FanoLabeling
open import Substrate.ShadowArchitecture.Duality using (normal-vector)
open import Substrate.ShadowArchitecture.Weight
  using (point-orbit; line-orbit; wt-3)

------------------------------------------------------------------------
-- 1. Point-on-line predicate.
--
-- A point p lies on line ℓ iff p equals one of the three points in
-- `line-points ℓ`. We unfold per-line rather than introducing a
-- pattern-matching `with` clause, so the disjunction is visible at
-- the use-site.
------------------------------------------------------------------------

infix 4 _on_

_on_ : Point → Line → Set
p on L₁ = (p ≡ p₁₀₀) ⊎ ((p ≡ p₀₁₀) ⊎ (p ≡ p₁₁₀))
p on L₂ = (p ≡ p₁₀₀) ⊎ ((p ≡ p₀₀₁) ⊎ (p ≡ p₁₀₁))
p on L₃ = (p ≡ p₀₁₀) ⊎ ((p ≡ p₀₀₁) ⊎ (p ≡ p₀₁₁))
p on L₄ = (p ≡ p₁₀₀) ⊎ ((p ≡ p₀₁₁) ⊎ (p ≡ p₁₁₁))
p on L₅ = (p ≡ p₀₁₀) ⊎ ((p ≡ p₁₀₁) ⊎ (p ≡ p₁₁₁))
p on L₆ = (p ≡ p₀₀₁) ⊎ ((p ≡ p₁₁₀) ⊎ (p ≡ p₁₁₁))
p on L₇ = (p ≡ p₁₁₀) ⊎ ((p ≡ p₁₀₁) ⊎ (p ≡ p₀₁₁))

------------------------------------------------------------------------
-- 2. ★ L₆ self-reference: normal-vector L₆ ≡ 110 AND 110 on L₆.
------------------------------------------------------------------------

L₆-normal-is-110 : normal-vector L₆ ≡ p₁₁₀
L₆-normal-is-110 = refl

L₆-110-on-line : p₁₁₀ on L₆
L₆-110-on-line = inj₂ (inj₁ refl)

L₆-self-incident : normal-vector L₆ on L₆
L₆-self-incident = L₆-110-on-line

------------------------------------------------------------------------
-- 3. ★ L₇ self-reference: normal-vector L₇ ≡ 111 AND 111 NOT on L₇.
--
-- The non-incidence is constructor-disjointness on the underlying
-- Point data constructors (e₁₂₃ ≢ e₁₂, e₁₂₃ ≢ e₁₃, e₁₂₃ ≢ e₂₃).
-- Each disjunct closes by `()`.
------------------------------------------------------------------------

L₇-normal-is-111 : normal-vector L₇ ≡ p₁₁₁
L₇-normal-is-111 = refl

L₇-111-non-incident : ¬ (p₁₁₁ on L₇)
L₇-111-non-incident (inj₁ ())
L₇-111-non-incident (inj₂ (inj₁ ()))
L₇-111-non-incident (inj₂ (inj₂ ()))

L₇-non-self-incident : ¬ (normal-vector L₇ on L₇)
L₇-non-self-incident = L₇-111-non-incident

------------------------------------------------------------------------
-- 4. The S₃-fixed pair: {111, L₇} are the unique S₃-fixed point and
-- the unique S₃-fixed line.
--
-- Each is the unique inhabitant of the wt-3 orbit (point side: only
-- p₁₁₁; line side: only L₇), and they are non-incident — the
-- architecture's axis-symmetric core that survives any relabelling
-- of the three coordinates.
------------------------------------------------------------------------

p₁₁₁-only-wt-3 : ∀ (p : Point) → point-orbit p ≡ wt-3 → p ≡ p₁₁₁
p₁₁₁-only-wt-3 p₁₀₀ ()
p₁₁₁-only-wt-3 p₀₁₀ ()
p₁₁₁-only-wt-3 p₀₀₁ ()
p₁₁₁-only-wt-3 p₁₁₀ ()
p₁₁₁-only-wt-3 p₁₀₁ ()
p₁₁₁-only-wt-3 p₀₁₁ ()
p₁₁₁-only-wt-3 p₁₁₁ refl = refl

L₇-only-wt-3 : ∀ (ℓ : Line) → line-orbit ℓ ≡ wt-3 → ℓ ≡ L₇
L₇-only-wt-3 L₁ ()
L₇-only-wt-3 L₂ ()
L₇-only-wt-3 L₃ ()
L₇-only-wt-3 L₄ ()
L₇-only-wt-3 L₅ ()
L₇-only-wt-3 L₆ ()
L₇-only-wt-3 L₇ refl = refl

------------------------------------------------------------------------
-- 5. The fixed pair is non-incident. Combines (3) and (4): the unique
-- wt-3 point is not on the unique wt-3 line.
------------------------------------------------------------------------

S₃-fixed-pair-non-incident :
  ∀ (p : Point) (ℓ : Line) →
  point-orbit p ≡ wt-3 → line-orbit ℓ ≡ wt-3 → ¬ (p on ℓ)
S₃-fixed-pair-non-incident p ℓ ep eℓ p-on-ℓ =
  let p≡111 = p₁₁₁-only-wt-3 p ep
      ℓ≡L₇  = L₇-only-wt-3 ℓ eℓ
  in subst-on-line p≡111 ℓ≡L₇ p-on-ℓ
  where
    -- Substituting both p and ℓ to their unique values turns the
    -- assumed incidence into `p₁₁₁ on L₇`, which is contradicted by
    -- `L₇-111-non-incident`.
    subst-on-line :
      ∀ {p ℓ} → p ≡ p₁₁₁ → ℓ ≡ L₇ → p on ℓ → ⊥
    subst-on-line refl refl p-on-ℓ = L₇-111-non-incident p-on-ℓ
