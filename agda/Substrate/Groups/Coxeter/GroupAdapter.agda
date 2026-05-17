------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.GroupAdapter
--
-- Lifts a Coxeter Core plus an inverse operation to a stdlib Group
-- bundle (Algebra.Bundles.Group).
--
-- The Core gives us _·_, _≈_, ε at the Word level; this module
-- packages those plus inv into an `IsGroup` and a `Group` bundle so
-- downstream combinators (SemidirectProductGroup) and consumers can
-- treat any Coxeter instance as a generic Group.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]: this
-- is the shadow that turns "Coxeter Core" into a stdlib-citizen, so
-- combinators that take Group bundles (rather than Coxeter Cores)
-- can consume any Coxeter instance.
--
-- INPUTS (14 parameters):
--   * Core (9): Word, _++_, ε-in, ++-assoc, Canonical, normalize,
--     normalize-canonical, canonical-is-fixed, normalize-distrib.
--   * Identity (3): canonical-ε, ε-left-++, ε-right-++.
--   * Inversion (3): inv, inv-canonical, inv-left-canonical,
--     inv-right-canonical (4 actually).
--
-- USERS (planned):
--   * Substrate.Groups.Z2-Coxeter-Group  (lift Z2-Coxeter)
--   * Substrate.Groups.Z3-Coxeter-Group  (lift Z3-Coxeter)
--   * Substrate.Groups.V4-Coxeter-Group  (alternative to V4.agda's
--     4-ctor adapter)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Algebra.Bundles using (Group)
open import Algebra.Structures using (IsMagma; IsSemigroup; IsMonoid; IsGroup)
open import Level using (0ℓ)
open import Relation.Binary using (IsEquivalence)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong)

module Substrate.Groups.Coxeter.GroupAdapter
  -- Coxeter Core inputs.
  (Word : Set)
  (_++_ : Word → Word → Word)
  (ε-in : Word)
  (++-assoc : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  (Canonical : Word → Set)
  (canonical-ε : Canonical ε-in)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  (normalize-distrib : (a b : Word) →
    normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  -- ε identity laws at the ++ level (needed because Core doesn't
  -- enforce these — they're trivial for ListPresentation, requirable
  -- for DirectProduct via componentwise laws).
  (ε-left-++ : (w : Word) → ε-in ++ w ≡ w)
  (ε-right-++ : (w : Word) → w ++ ε-in ≡ w)
  -- Inversion.
  (inv : Word → Word)
  (inv-canonical : {w : Word} → Canonical w → Canonical (inv w))
  (inv-left-canonical : {w : Word} → Canonical w →
    normalize (inv w ++ w) ≡ ε-in)
  (inv-right-canonical : {w : Word} → Canonical w →
    normalize (w ++ inv w) ≡ ε-in)
  where

------------------------------------------------------------------------
-- 1. Open Coxeter Core to inherit _·_, _≈_, _≉_, ε, normalize-{idem,
-- append,append-right,cong-right,distrib,triple,quad}, ≉-idem, clash,
-- ++-assoc-4.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.Core
  Word _++_ ε-in ++-assoc Canonical normalize normalize-canonical
  canonical-is-fixed normalize-distrib public

------------------------------------------------------------------------
-- 2. Word-level inv: normalize first to ensure inv is applied to
-- a canonical input. This is where the per-instance inv (defined on
-- canonical forms only) lifts to a total function on Words.
------------------------------------------------------------------------

inv-word : Word → Word
inv-word w = inv (normalize w)

------------------------------------------------------------------------
-- 3. ε is canonical, so normalize ε ≡ ε.
------------------------------------------------------------------------

normalize-ε : normalize ε ≡ ε
normalize-ε = canonical-is-fixed canonical-ε

------------------------------------------------------------------------
-- 4. ≈ is an equivalence relation (transport of ≡).
------------------------------------------------------------------------

≈-refl : ∀ {w} → w ≈ w
≈-refl = refl

≈-sym : ∀ {w₁ w₂} → w₁ ≈ w₂ → w₂ ≈ w₁
≈-sym = sym

≈-trans : ∀ {w₁ w₂ w₃} → w₁ ≈ w₂ → w₂ ≈ w₃ → w₁ ≈ w₃
≈-trans = trans

≈-isEquivalence : IsEquivalence _≈_
≈-isEquivalence = record
  { refl  = ≈-refl
  ; sym   = ≈-sym
  ; trans = ≈-trans
  }

------------------------------------------------------------------------
-- 5. _·_ is congruent w.r.t. _≈_.
--
-- Strategy: unfold w₁·w₂ to normalize (w₁++w₂), strip outer normalize
-- via normalize-idem, push through normalize-distrib + cong on
-- normalize, then reassemble symmetrically on the RHS.
------------------------------------------------------------------------

·-cong : ∀ {a₁ a₂ b₁ b₂} → a₁ ≈ a₂ → b₁ ≈ b₂ → a₁ · b₁ ≈ a₂ · b₂
·-cong {a₁} {a₂} {b₁} {b₂} a-eq b-eq =
  trans (normalize-idem (a₁ ++ b₁))
  (trans (normalize-distrib a₁ b₁)
  (trans (cong (λ x → normalize (x ++ normalize b₁)) a-eq)
  (trans (cong (λ x → normalize (normalize a₂ ++ x)) b-eq)
  (trans (sym (normalize-distrib a₂ b₂))
         (sym (normalize-idem (a₂ ++ b₂)))))))

------------------------------------------------------------------------
-- 6. _·_ is associative w.r.t. _≈_.
--
-- Strategy: unfold both sides, strip outer normalize-idem, use
-- normalize-append (sym) + cong of ++-assoc + normalize-append-right
-- to bridge through the unparenthesized middle form.
------------------------------------------------------------------------

·-assoc : ∀ a b c → (a · b) · c ≈ a · (b · c)
·-assoc a b c =
  trans (normalize-idem ((a · b) ++ c))
  (trans (sym (normalize-append (a ++ b) c))
  (trans (cong normalize (++-assoc a b c))
  (trans (normalize-append-right a (b ++ c))
         (sym (normalize-idem (a ++ (b · c)))))))

------------------------------------------------------------------------
-- 7. ε is left/right identity for _·_ at the ≈ level.
------------------------------------------------------------------------

ε-left : ∀ w → ε · w ≈ w
ε-left w =
  trans (normalize-idem (ε ++ w))
        (cong normalize (ε-left-++ w))

ε-right : ∀ w → w · ε ≈ w
ε-right w =
  trans (normalize-idem (w ++ ε))
        (cong normalize (ε-right-++ w))

------------------------------------------------------------------------
-- 8. inv-word is a left/right inverse for _·_ at the ≈ level.
--
-- inv-l: inv-word w · w ≈ ε.
--   normalize (inv-word w · w)
--     = normalize (normalize (inv (normalize w) ++ w))     [def _·_]
--     ≡ normalize (inv (normalize w) ++ w)                 [normalize-idem]
--     ≡ normalize (inv (normalize w) ++ normalize w)       [normalize-append-right]
--     ≡ ε-in                                                [inv-left-canonical]
--     ≡ normalize ε                                         [sym normalize-ε]
--
-- inv-r symmetric via normalize-append + inv-right-canonical.
------------------------------------------------------------------------

inv-l : ∀ w → (inv-word w · w) ≈ ε
inv-l w =
  trans (normalize-idem (inv-word w ++ w))
  (trans (normalize-append-right (inv (normalize w)) w)
  (trans (inv-left-canonical (normalize-canonical w))
         (sym normalize-ε)))

inv-r : ∀ w → (w · inv-word w) ≈ ε
inv-r w =
  trans (normalize-idem (w ++ inv-word w))
  (trans (normalize-append w (inv (normalize w)))
  (trans (inv-right-canonical (normalize-canonical w))
         (sym normalize-ε)))

------------------------------------------------------------------------
-- 9. inv-word is ≈-congruent.
--
-- w₁ ≈ w₂ means normalize w₁ ≡ normalize w₂. Then inv (normalize w₁)
-- ≡ inv (normalize w₂) by cong inv. Both sides are canonical (via
-- inv-canonical of normalize-canonical), so they equal their own
-- normalize images — i.e., inv-word w₁ ≈ inv-word w₂.
------------------------------------------------------------------------

inv-word-cong : ∀ {w₁ w₂} → w₁ ≈ w₂ → inv-word w₁ ≈ inv-word w₂
inv-word-cong {w₁} {w₂} eq =
  trans (canonical-is-fixed (inv-canonical (normalize-canonical w₁)))
  (trans (cong inv eq)
         (sym (canonical-is-fixed (inv-canonical (normalize-canonical w₂)))))

------------------------------------------------------------------------
-- 10. Assemble the stdlib Group bundle.
------------------------------------------------------------------------

isMagma : IsMagma _≈_ _·_
isMagma = record
  { isEquivalence = ≈-isEquivalence
  ; ∙-cong        = ·-cong
  }

isSemigroup : IsSemigroup _≈_ _·_
isSemigroup = record
  { isMagma = isMagma
  ; assoc   = ·-assoc
  }

isMonoid : IsMonoid _≈_ _·_ ε
isMonoid = record
  { isSemigroup = isSemigroup
  ; identity    = ε-left , ε-right
  }
  where open import Data.Product using (_,_)

isGroup : IsGroup _≈_ _·_ ε inv-word
isGroup = record
  { isMonoid = isMonoid
  ; inverse  = inv-l , inv-r
  ; ⁻¹-cong  = inv-word-cong
  }
  where open import Data.Product using (_,_)

Group-bundle : Group 0ℓ 0ℓ
Group-bundle = record
  { Carrier = Word
  ; _≈_     = _≈_
  ; _∙_     = _·_
  ; ε       = ε
  ; _⁻¹     = inv-word
  ; isGroup = isGroup
  }
