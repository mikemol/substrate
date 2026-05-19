------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Core
--
-- Abstract Coxeter Core. Parameterized over a Word type with a
-- monoid structure (++/ε with associativity + identity laws) and a
-- normalization function with canonical-form predicate. The shape
-- of Word is opaque — this Core works equally well for `List Gen`
-- (Coxeter group presentations via generator words) and for
-- `Word₁ × Word₂` (direct products of Coxeter groups), among other
-- encodings.
--
-- Per [[feedback-v4-typeclass-architecture]] applied at the most
-- abstract level: any normalization-bearing monoid satisfying the
-- below interface inherits the entire foundation (group ops, bridge
-- lemmas, clash macro, composition helpers).
--
-- INSTANTIATIONS (existing or planned):
--   * Substrate.Groups.Coxeter.ListPresentation : List Gen + insert
--     — the original Coxeter presentation via word algebras.
--   * Substrate.Groups.Coxeter.DirectProduct    : Word₁ × Word₂
--     — combinator producing the product Coxeter group.
--
-- ADAPTER WRAPPERS use this Core; THEOREMS (finite enumerations like
-- V₄-4-product) live with the specific instance.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Data.Empty using (⊥; ⊥-elim)
open import Relation.Nullary using (Dec; yes; no)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong; _≢_)

module Substrate.Groups.Coxeter.Core
  -- Carrier with monoid structure.
  (Word : Set)
  (_++_ : Word → Word → Word)
  (ε-in : Word)
  (++-assoc : (a b c : Word) → (a ++ b) ++ c ≡ a ++ (b ++ c))
  -- Normalizer + canonical form predicate.
  (Canonical : Word → Set)
  (normalize : Word → Word)
  (normalize-canonical : (w : Word) → Canonical (normalize w))
  (canonical-is-fixed : {w : Word} → Canonical w → normalize w ≡ w)
  -- The homomorphism property (the only input that's actually a
  -- proof obligation per instance — everything else is structural or
  -- mechanical).
  (normalize-distrib :
    (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ normalize b))
  where

-- Re-bind ε as a body-defined name so it propagates through `open ...
-- public`. (Don't re-bind _++_ or ++-assoc — those clash with the
-- Word module's exports at the instance level.)
ε : Word
ε = ε-in

-- Note: we can't declare fixity on the module-parameter _++_ from
-- here; uses in this file write explicit parens (`a ++ (b ++ c)`).
infixl 7 _·_
infix  4 _≈_
infix  4 _≉_

------------------------------------------------------------------------
-- 1. Group operations up to normalization equivalence.
--
-- _·_ is composition modulo normalize.
-- _≈_ is equality on normal forms.
-- _≉_ is inequality on normal forms.
-- ε is provided by the user as the carrier identity.
------------------------------------------------------------------------

_·_ : Word → Word → Word
w₁ · w₂ = normalize (w₁ ++ w₂)

_≈_ : Word → Word → Set
w₁ ≈ w₂ = normalize w₁ ≡ normalize w₂

_≉_ : Word → Word → Set
w₁ ≉ w₂ = normalize w₁ ≢ normalize w₂

------------------------------------------------------------------------
-- 2. normalize idempotency (derived from canonical-is-fixed +
-- normalize-canonical).
------------------------------------------------------------------------

normalize-idem : (w : Word) → normalize (normalize w) ≡ normalize w
normalize-idem w = canonical-is-fixed (normalize-canonical w)

------------------------------------------------------------------------
-- 3. Asymmetric versions of normalize-distrib (derived).
--
-- normalize-append:        normalize (a ++ b) ≡ normalize (normalize a ++ b)
-- normalize-append-right:  normalize (a ++ b) ≡ normalize (a ++ normalize b)
--
-- Both follow from normalize-distrib + a strategic re-application
-- of normalize-distrib in the other direction, leveraging normalize-idem.
------------------------------------------------------------------------

normalize-append : (a b : Word) → normalize (a ++ b) ≡ normalize (normalize a ++ b)
normalize-append a b =
  trans (normalize-distrib a b)
        (sym (trans (normalize-distrib (normalize a) b)
                    (cong (λ x → normalize (x ++ normalize b))
                          (normalize-idem a))))

normalize-append-right : (a b : Word) →
                         normalize (a ++ b) ≡ normalize (a ++ normalize b)
normalize-append-right a b =
  trans (normalize-distrib a b)
        (sym (trans (normalize-distrib a (normalize b))
                    (cong (λ x → normalize (normalize a ++ x))
                          (normalize-idem b))))

------------------------------------------------------------------------
-- 4. cong-right at the normalize level.
--
-- normalize-cong-right a eq : normalize (a ++ b₁) ≡ normalize (a ++ b₂)
-- given eq : normalize b₁ ≡ normalize b₂.
------------------------------------------------------------------------

normalize-cong-right : (a : Word) {b₁ b₂ : Word} →
                       normalize b₁ ≡ normalize b₂ →
                       normalize (a ++ b₁) ≡ normalize (a ++ b₂)
normalize-cong-right a {b₁} {b₂} eq =
  trans (normalize-append-right a b₁)
  (trans (cong (λ x → normalize (a ++ x)) eq)
         (sym (normalize-append-right a b₂)))

------------------------------------------------------------------------
-- 5. Higher-arity distribution lemmas. Each is a short compose of
-- normalize-distrib + normalize-cong-right.
------------------------------------------------------------------------

-- Triple version (used for 3-operand products).
normalize-triple : (a b c : Word) →
                   normalize (a ++ (b ++ c)) ≡
                   normalize (normalize a ++ (normalize b ++ normalize c))
normalize-triple a b c =
  trans (normalize-append a (b ++ c))
        (normalize-cong-right (normalize a) (normalize-distrib b c))

-- Quad version (used for 4-operand products like V₄-4-product).
normalize-quad : (a b c d : Word) →
                 normalize (a ++ (b ++ (c ++ d))) ≡
                 normalize (normalize a ++ (normalize b ++
                            (normalize c ++ normalize d)))
normalize-quad a b c d =
  trans (normalize-append a (b ++ (c ++ d)))
        (normalize-cong-right (normalize a) (normalize-triple b c d))

-- Quint version (used for Zₙ Coxeter fifth-power-identity at n=5).
normalize-quint : (a b c d e : Word) →
                  normalize (a ++ (b ++ (c ++ (d ++ e)))) ≡
                  normalize (normalize a ++ (normalize b ++
                             (normalize c ++ (normalize d ++ normalize e))))
normalize-quint a b c d e =
  trans (normalize-append a (b ++ (c ++ (d ++ e))))
        (normalize-cong-right (normalize a) (normalize-quad b c d e))

------------------------------------------------------------------------
-- 6. Inequality lifting through normalize. Used by per-instance
-- finite-enumeration theorems to bridge `≉` hypotheses across the
-- implicit-Word substitution that happens when applying eval-canonical
-- to `normalize-canonical w`.
------------------------------------------------------------------------

≉-idem : (w₁ w₂ : Word) → w₁ ≉ w₂ → normalize w₁ ≉ normalize w₂
≉-idem w₁ w₂ neq p =
  neq (trans (sym (normalize-idem w₁)) (trans p (normalize-idem w₂)))

------------------------------------------------------------------------
-- 7. Clash macro: lift Canonical-level equality back to Word-level
-- via canonical-is-fixed; combine with ≉ for ⊥-elim. Used by per-
-- instance enumeration proofs.
------------------------------------------------------------------------

clash : {w₁ w₂ : Word} → Canonical w₁ → Canonical w₂ →
        w₁ ≉ w₂ → w₁ ≡ w₂ → ∀ {A : Set} → A
clash _ _ neq eq = ⊥-elim (neq (cong normalize eq))

------------------------------------------------------------------------
-- 8. 4-way associativity (used by per-instance 4-product theorems).
------------------------------------------------------------------------

++-assoc-4 : (a b c d : Word) →
             (a ++ b) ++ (c ++ d) ≡ a ++ (b ++ (c ++ d))
++-assoc-4 a b c d = ++-assoc a b (c ++ d)
