------------------------------------------------------------------------
-- Substrate.Kelen.RelationCompose
--
-- D2 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- Closes the deferred relation-composition operation flagged in C5
-- (Substrate.Kelen.Fragment). Defines `_∘ᴿ_ : KelenWord → KelenWord
-- → KelenWord` as the free-monoid composition (concatenation),
-- along with the standard monoid laws (associativity, identity).
--
-- Per [[feedback-categorical-name-first]]: at the free-monoid layer,
-- relation composition IS word concatenation — the same shape
-- Lojban's free-monoid arc used. The DIFFERENCE between Kēlen and
-- Lojban at this level is structural classification (Free-relation
-- vs Free-monoid cell of the lattice), not the underlying
-- composition operation; semantic relation composition (the
-- intensional sense of "composing relations as subsets of products")
-- is deferred to a future arc that integrates with
-- Substrate.Category.RuleAction.
--
-- Per [[feedback-comments-dont-overclaim]]: this slice closes the
-- WORD-LEVEL composition obligation. The semantic relation algebra
-- (Rel-category morphisms, dagger structure, residuals) is still
-- deferred.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.RelationCompose where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-assoc;
         ++-identity-left; ++-identity-right)
open import Substrate.Kelen.Fragment using (Relational; KelenWord; ε; single)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid using (MonoidOn)

------------------------------------------------------------------------
-- 1. Relation composition at the word level.
--
-- R₁ ∘ᴿ R₂ = R₁ then R₂ (categorical-convention: read right-to-left
-- as relation composition; here we use the FREE convention where
-- word concatenation IS the composition, so the left operand goes
-- first in the resulting word).
------------------------------------------------------------------------

infixr 5 _∘ᴿ_

_∘ᴿ_ : KelenWord → KelenWord → KelenWord
_∘ᴿ_ = _++_

------------------------------------------------------------------------
-- 2. Identity laws.
--
-- The empty word ε is the two-sided identity for ∘ᴿ. Inherited
-- from Coxeter.Word's ++-identity-left / ++-identity-right.
------------------------------------------------------------------------

∘ᴿ-identityˡ : (w : KelenWord) → ε ∘ᴿ w ≡ w
∘ᴿ-identityˡ = ++-identity-left

∘ᴿ-identityʳ : (w : KelenWord) → w ∘ᴿ ε ≡ w
∘ᴿ-identityʳ = ++-identity-right

------------------------------------------------------------------------
-- 3. Associativity.
--
-- (w₁ ∘ᴿ w₂) ∘ᴿ w₃ ≡ w₁ ∘ᴿ (w₂ ∘ᴿ w₃). Inherited from Coxeter.Word's
-- ++-assoc. Together with the identity laws, this makes
-- (KelenWord, _∘ᴿ_, ε) a monoid — the FREE relation monoid at the
-- linguistic site.
------------------------------------------------------------------------

∘ᴿ-assoc :
  (w₁ w₂ w₃ : KelenWord) →
  (w₁ ∘ᴿ w₂) ∘ᴿ w₃ ≡ w₁ ∘ᴿ (w₂ ∘ᴿ w₃)
∘ᴿ-assoc = ++-assoc

------------------------------------------------------------------------
-- 4. Lifting basic relationals to words via single + composition.
--
-- A common pattern: build a composed relation from two atomic
-- relationals. E.g., (la ∘ᴿ pa) = la-then-pa-composed.
------------------------------------------------------------------------

compose-relationals : Relational → Relational → KelenWord
compose-relationals r₁ r₂ = single r₁ ∘ᴿ single r₂

------------------------------------------------------------------------
-- 5. Worked examples.
--
-- Two atomic relationals composed; demonstrates the operation works.
------------------------------------------------------------------------

open import Substrate.Kelen.Fragment using (la; nā; pa; jana)

-- la then pa (composed): la ∘ᴿ pa
example-la-then-pa : KelenWord
example-la-then-pa = compose-relationals la pa

-- Associativity check at concrete values.
example-assoc :
  ((single la ∘ᴿ single pa) ∘ᴿ single jana)
    ≡ (single la ∘ᴿ (single pa ∘ᴿ single jana))
example-assoc = ∘ᴿ-assoc (single la) (single pa) (single jana)

------------------------------------------------------------------------
-- 6. Capstone.
--
-- The Kēlen word-level relation composition is the free monoid on
-- the four relationals. Per [[project-language-as-free-construction-classification]]
-- this puts Kēlen's free-relation cell on the same footing as
-- Lojban's free-monoid cell AT THE FREE LEVEL; the linguistic
-- distinction is in how the structure is INTERPRETED (relations vs.
-- functions), not in the free-construction shape.
--
-- Deferred for future arcs:
--   * Semantic relation composition (Rel-category morphisms)
--   * Dagger structure (relation reversal)
--   * Residuals / Galois connections
------------------------------------------------------------------------

------------------------------------------------------------------------
-- GROUNDED: (KelenWord, _∘ᴿ_, ε) IS a substrate-named `MonoidOn` — the free
-- relation monoid on the relationals, an instance of the word-algebra center's
-- free-monoid (Category.FreeUniversalProperty.FreeMonoid; cf. its `word-monoid`
-- for any `Word Gen`). The bare laws above witness the named primitive.
------------------------------------------------------------------------

∘ᴿ-MonoidOn : MonoidOn KelenWord
∘ᴿ-MonoidOn = record
  { ε       = ε
  ; _∙_     = _∘ᴿ_
  ; ∙-assoc = ∘ᴿ-assoc
  ; ε-left  = ∘ᴿ-identityˡ
  ; ε-right = ∘ᴿ-identityʳ
  }
