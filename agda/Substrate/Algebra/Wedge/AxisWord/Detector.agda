------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.AxisWord.Detector
--
-- OBLIGATION A2 — FAITHFULNESS of the detector grade (scratch/
-- dent_system_primer.md §8). The carrier (AxisWord) never annihilates; the
-- DETECTOR is a separate reading that measures whether two factors are the
-- same direction. This module builds that detector grade over any
-- decidable-equality alphabet and proves it FAITHFUL:
--
--   detect a b ≡ 𝟘  ⟺  a ≡ b        (kernel = the diagonal = non-distinctions)
--   detect a b ≡ 𝟙  ⟺  ¬ (a ≡ b)    (nonzero ⟺ a real distinction)
--
-- This is exactly A2: `ker(grade) = 0` on the category of DISTINCTIONS — the
-- detector annihilates nothing that was a real distinction. It is NOT a claim
-- that the carrier annihilates; `detect a a = 𝟘` is the measurement that a
-- with itself forces no new distinction, while the carrier still retains the
-- repeated word (count = 2). The two layers, made code, on one alphabet.
--
-- (The discriminated k-d alphabet `Fin k × Fin t` — axis × threshold — is
-- another instance: there `detect` separates a genuine refinement, same axis
-- at a different threshold, from a vacuous repeat. Any Dec-equality alphabet
-- works; below we instantiate at the bare axis alphabet `Fin k` to tie to
-- AxisWord directly.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.AxisWord.Detector where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; 𝟘≢𝟙; 𝟙≢𝟘)
open import Substrate.Algebra.Wedge.AxisWord using (count; self-wedge-multiplicity)

------------------------------------------------------------------------
-- Slice 11. The detector grade of a decision: 𝟘 = same direction (no
--           distinction), 𝟙 = distinct.
------------------------------------------------------------------------

detect-dec : {A : Set} {a b : A} → Dec (a ≡ b) → F₂
detect-dec (yes _) = 𝟘
detect-dec (no  _) = 𝟙

module Detector {A : Set} (_≟A_ : (a b : A) → Dec (a ≡ b)) where

  detect : A → A → F₂
  detect a b = detect-dec (a ≟A b)

  ------------------------------------------------------------------------
  -- Slice 12. Self-pairing measures 𝟘: a with itself forces no distinction.
  ------------------------------------------------------------------------

  detect-refl : (a : A) → detect a a ≡ 𝟘
  detect-refl a with a ≟A a
  ... | yes _  = refl
  ... | no  ¬p = ⊥-elim (¬p refl)

  ------------------------------------------------------------------------
  -- Slice 13. The kernel is exactly the diagonal: grade 𝟘 ⟺ equal; and a
  --           genuine distinction always measures 𝟙.
  ------------------------------------------------------------------------

  detect-kernel : {a b : A} → detect a b ≡ 𝟘 → a ≡ b
  detect-kernel {a} {b} eq with a ≟A b
  ... | yes p  = p
  ... | no  ¬p = ⊥-elim (𝟙≢𝟘 eq)

  detect-distinct : {a b : A} → ¬ (a ≡ b) → detect a b ≡ 𝟙
  detect-distinct {a} {b} ne with a ≟A b
  ... | yes p  = ⊥-elim (ne p)
  ... | no  ¬p = refl

  ------------------------------------------------------------------------
  -- Slice 14. FAITHFULNESS (A2): nonzero grade ⟹ a real distinction — no
  --           real distinction lands in the kernel. With detect-distinct this
  --           is the full equivalence detect a b ≡ 𝟙 ⟺ ¬ (a ≡ b).
  ------------------------------------------------------------------------

  detect-faithful : {a b : A} → detect a b ≡ 𝟙 → ¬ (a ≡ b)
  detect-faithful {a} {b} eq ab =
    𝟘≢𝟙 (trans (sym (trans (sym (cong (detect a) ab)) (detect-refl a))) eq)

------------------------------------------------------------------------
-- Slice 15. Instantiate at the bare axis alphabet (Fin k) and exhibit the
--           two layers on one self-pairing: the CARRIER retains the repeated
--           axis (count = 2, never-annihilate) while the DETECTOR reads grade
--           𝟘 (no distinction). The reconciliation, as code.
------------------------------------------------------------------------

module DF (k : ℕ) = Detector {Fin k} (λ a b → a ≟ b)

carrier-vs-detector : (k : ℕ) (i : Fin k) →
  (count i (i ∷ i ∷ []) ≡ 2)        -- carrier: repetition retained
  × (DF.detect k i i ≡ 𝟘)            -- detector: self-pairing = no distinction
carrier-vs-detector k i = self-wedge-multiplicity i , DF.detect-refl k i
