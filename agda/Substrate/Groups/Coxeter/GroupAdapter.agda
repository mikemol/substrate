------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.GroupAdapter
--
-- Lifts a Coxeter Core plus an inverse operation to a substrate-native
-- SetoidGroup bundle (Substrate.Algebra.SetoidGroup).
--
-- Phase-2: stdlib `Algebra.Bundles.Group` / `Algebra.Structures` /
-- `Relation.Binary` imports REMOVED. The output is a substrate-native
-- `SetoidGroup-bundle : SetoidGroup` instead of `Group-bundle : Group 0ℓ 0ℓ`.
-- A `Group-bundle` alias is retained for backward compatibility with
-- downstream callers.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; cong-trans; sym-trans)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

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
  (ε-left-++ : (w : Word) → ε-in ++ w ≡ w)
  (ε-right-++ : (w : Word) → w ++ ε-in ≡ w)
  (inv : Word → Word)
  (inv-canonical : {w : Word} → Canonical w → Canonical (inv w))
  (inv-left-canonical : {w : Word} → Canonical w →
    normalize (inv w ++ w) ≡ ε-in)
  (inv-right-canonical : {w : Word} → Canonical w →
    normalize (w ++ inv w) ≡ ε-in)
  where

------------------------------------------------------------------------
-- 1. Open Coxeter Core (inherits _·_, _≈_, ε, normalize-* lemmas).
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.Core
  Word _++_ ε-in ++-assoc Canonical normalize normalize-canonical
  canonical-is-fixed normalize-distrib public

------------------------------------------------------------------------
-- 2. Word-level inv.
------------------------------------------------------------------------

inv-word : Word → Word
inv-word w = inv (normalize w)

------------------------------------------------------------------------
-- 3. ε is canonical.
------------------------------------------------------------------------

normalize-ε : normalize ε ≡ ε
normalize-ε = canonical-is-fixed canonical-ε

------------------------------------------------------------------------
-- 4. ≈ equivalence-relation witnesses.
------------------------------------------------------------------------

≈-refl : ∀ {w} → w ≈ w
≈-refl = refl

≈-sym : ∀ {w₁ w₂} → w₁ ≈ w₂ → w₂ ≈ w₁
≈-sym = sym

≈-trans : ∀ {w₁ w₂ w₃} → w₁ ≈ w₂ → w₂ ≈ w₃ → w₁ ≈ w₃
≈-trans = trans

------------------------------------------------------------------------
-- 5. _·_ is ≈-congruent.
------------------------------------------------------------------------

·-cong : ∀ {a₁ a₂ b₁ b₂} → a₁ ≈ a₂ → b₁ ≈ b₂ → a₁ · b₁ ≈ a₂ · b₂
·-cong {a₁} {a₂} {b₁} {b₂} a-eq b-eq =
  trans (normalize-idem (a₁ ++ b₁))
  (trans (normalize-distrib a₁ b₁)
  (cong-trans (λ x → normalize (x ++ normalize b₁)) a-eq
  (cong-trans (λ x → normalize (normalize a₂ ++ x)) b-eq
  (sym-trans (normalize-distrib a₂ b₂)
         (sym (normalize-idem (a₂ ++ b₂)))))))

------------------------------------------------------------------------
-- 6. _·_ associative w.r.t. _≈_.
------------------------------------------------------------------------

·-assoc : ∀ a b c → (a · b) · c ≈ a · (b · c)
·-assoc a b c =
  trans (normalize-idem ((a · b) ++ c))
  (sym-trans (normalize-append (a ++ b) c)
  (cong-trans normalize (++-assoc a b c)
  (trans (normalize-append-right a (b ++ c))
         (sym (normalize-idem (a ++ (b · c)))))))

------------------------------------------------------------------------
-- 7. ε identities for _·_ at ≈ level.
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
-- 8. inv-word inverse laws.
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
-- 9. inv-word ≈-congruent.
------------------------------------------------------------------------

inv-word-cong : ∀ {w₁ w₂} → w₁ ≈ w₂ → inv-word w₁ ≈ inv-word w₂
inv-word-cong {w₁} {w₂} eq =
  trans (canonical-is-fixed (inv-canonical (normalize-canonical w₁)))
  (cong-trans inv eq
         (sym (canonical-is-fixed (inv-canonical (normalize-canonical w₂)))))

------------------------------------------------------------------------
-- 10. Substrate-native SetoidGroup bundle.
------------------------------------------------------------------------

SetoidGroup-bundle : SetoidGroup Word _≈_
SetoidGroup-bundle = record
  { _∙_       = _·_
  ; ε         = ε
  ; _⁻¹       = inv-word
  ; ≈-refl    = λ _ → ≈-refl
  ; ≈-sym     = ≈-sym
  ; ≈-trans   = ≈-trans
  ; ∙-assoc   = ·-assoc
  ; ε-left    = ε-left
  ; ε-right   = ε-right
  ; inv-left  = inv-l
  ; inv-right = inv-r
  ; ∙-cong    = ·-cong
  ; ⁻¹-cong   = inv-word-cong
  }

-- Backward-compat alias.
Group-bundle : SetoidGroup Word _≈_
Group-bundle = SetoidGroup-bundle
