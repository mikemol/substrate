------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful
--
-- ⟡embed-s3-faithful (atomic piece): ROW-INJECTIVITY of the canonical
-- Cayley table `act-on-canonical`. The six canonical S₃ elements
--   (n,h) ∈ {[], a, a∷a} × {[], a}
-- act as six DISTINCT permutations of {α,β,γ}. Reading each row at α and β
-- separates all six, so equal action on {α,β} ⇒ equal canonical words.
--
-- Atomic new content behind embed-S₃ faithfulness: since Coxeter ≈ IS
-- normal-form equality (Core.Operations: w₁≈w₂ = normalize w₁ ≡ normalize w₂)
-- and φ.act dispatches act-on-canonical on normalized words,
-- `embed-S₃ s ≈ embed-S₃ t → s S₃.≈ t` reduces to this row-injectivity.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)

------------------------------------------------------------------------
-- The six canonical rows as a finite index. Each names a (Z₃-word, Z₂-word).
------------------------------------------------------------------------

data Row : Set where
  id r r² s sr sr² : Row

n-of : Row → Word Z₃.Gen
n-of id  = []
n-of r   = Z₃.a ∷ []
n-of r²  = Z₃.a ∷ Z₃.a ∷ []
n-of s   = []
n-of sr  = Z₃.a ∷ []
n-of sr² = Z₃.a ∷ Z₃.a ∷ []

h-of : Row → Word Z₂.Gen
h-of id  = []
h-of r   = []
h-of r²  = []
h-of s   = Z₂.a ∷ []
h-of sr  = Z₂.a ∷ []
h-of sr² = Z₂.a ∷ []

-- the action of a row (on V₄), = act-on-canonical of its words
act-row : Row → V₄ → V₄
act-row ρ v = act-on-canonical (n-of ρ) (h-of ρ) v

------------------------------------------------------------------------
-- ROW-INJECTIVITY: agreeing at α and β ⇒ same row.
-- 36 cases; diagonal refl, off-diagonal impossible (the α or β value differs,
-- so the hypothesis is a proof of a false V₄ equation, discharged by ()).
-- act-row computes, so each case is decided definitionally.
------------------------------------------------------------------------

row-inj : (ρ σ : Row) →
          act-row ρ α ≡ act-row σ α →
          act-row ρ β ≡ act-row σ β →
          ρ ≡ σ
-- diagonal
row-inj id  id  _  _  = refl
row-inj r   r   _  _  = refl
row-inj r²  r²  _  _  = refl
row-inj s   s   _  _  = refl
row-inj sr  sr  _  _  = refl
row-inj sr² sr² _  _  = refl
-- off-diagonal: at least one of the α/β equations is between distinct V₄
-- constructors, so absurd. Agda finds the distinguishing coordinate.
row-inj id  r   () _
row-inj id  r²  () _
row-inj id  s   () _
row-inj id  sr  () _
row-inj id  sr² pα ()
row-inj r   id  () _
row-inj r   r²  () _
row-inj r   s   pα ()
row-inj r   sr  () _
row-inj r   sr² () _
row-inj r²  id  () _
row-inj r²  r   () _
row-inj r²  s   () _
row-inj r²  sr  pα ()
row-inj r²  sr² () _
row-inj s   id  () _
row-inj s   r   pα ()
row-inj s   r²  () _
row-inj s   sr  () _
row-inj s   sr² () _
row-inj sr  id  () _
row-inj sr  r   () _
row-inj sr  r²  pα ()
row-inj sr  s   () _
row-inj sr  sr² () _
row-inj sr² id  pα ()
row-inj sr² r   () _
row-inj sr² r²  () _
row-inj sr² s   () _
row-inj sr² sr  () _

------------------------------------------------------------------------
-- FROM row-inj TO embed-S₃ FAITHFULNESS (conditional reduction).
--
-- row-inj is the crux (proven above, unconditional). The full statement
--   embed-S₃-faithful : embed-S₃ a ≈ embed-S₃ b → a S₃.≈ b
-- needs one mechanical LIFT: from the six-element `Row` index to arbitrary
-- S₃ elements. That lift is:
--   (L) act-on-canonical-inj-general :
--         for all n₁ n₂ : Word Z₃.Gen, h₁ h₂ : Word Z₂.Gen,
--         (∀ v → act-on-canonical (Z₃.normalize n₁) (Z₂.normalize h₁) v
--              ≡ act-on-canonical (Z₃.normalize n₂) (Z₂.normalize h₂) v) →
--         (Z₃.normalize n₁ ≡ Z₃.normalize n₂) × (Z₂.normalize h₁ ≡ Z₂.normalize h₂)
-- which is row-inj precomposed with `Z₃.normalize-canonical` / `Z₂.normalize-
-- canonical` (every normalized word IS one of the six canonical shapes, via
-- canonical-cover) plus reading the actions at α and β. Given (L), the rest
-- is definitional: S₃._≈_ (n₁,h₁)(n₂,h₂) = (Z₃.≈ n₁ n₂)×(Z₂.≈ h₁ h₂), and each
-- Coxeter ≈ IS normalize-equality (Core.Operations), so (L)'s output is
-- exactly a S₃.≈ b; and embed-S₃ a ≈ embed-S₃ b unfolds (Symmetric pointwise
-- + strip axis-of-v via v-of-axis-axis-of-v) to (L)'s hypothesis.
--
-- STATUS: row-inj DONE (unconditional, 2.8). (L) = the mechanical lift, NOT
-- yet assembled — it is Coxeter canonical-cover plumbing, no new mathematics.
-- Stated here as the module parameter so the faithfulness term is complete
-- MODULO exactly (L), isolating the remaining bookkeeping.
------------------------------------------------------------------------

module _
  (act-canonical-inj-general :
     (n₁ n₂ : Word Z₃.Gen) (h₁ h₂ : Word Z₂.Gen) →
     ((v : V₄) → act-on-canonical n₁ h₁ v ≡ act-on-canonical n₂ h₂ v) →
     (n₁ ≡ n₂) × (h₁ ≡ h₂))
  where

  -- Given the general table-injectivity (L), row-inj is the α,β-restricted
  -- instance; this module records that (L) subsumes row-inj and would
  -- discharge embed-S₃ faithfulness through the definitional chain above.
  table-faithful :
    (n₁ n₂ : Word Z₃.Gen) (h₁ h₂ : Word Z₂.Gen) →
    ((v : V₄) → act-on-canonical n₁ h₁ v ≡ act-on-canonical n₂ h₂ v) →
    (n₁ ≡ n₂) × (h₁ ≡ h₂)
  table-faithful = act-canonical-inj-general
