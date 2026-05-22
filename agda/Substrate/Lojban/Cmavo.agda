------------------------------------------------------------------------
-- Substrate.Lojban.Cmavo
--
-- L6 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Functorial wrappers for scope/tense cmavo. A cmavo wrapper is a
-- Sem→Sem map lifted to Bridi via bridi-postcompose; the functorial
-- nature is automatic from L5. This slice formalises PU (past/
-- present/future tense markers) and NA (negation) as the small
-- working set; SE/TE/VE conversion, attitudinals (UI), and MEX are
-- deferred per the arc plan.
--
-- Per [[feedback-categorical-name-first]]: "functorial wrapper" is
-- the abstract pattern. Each cmavo class is an Sem-endofunction; the
-- substrate's lift to bridi is the standard postcompose.
--
-- Per [[feedback-grothendieck-coherence-rule]]: wrapper composition
-- preserves the postcompose structure; identity-cmavo and composed-
-- cmavo coherences are stated here and consumed by L7.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Cmavo where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Lojban.Bridi
  using (Bridi; bridi-postcompose; interpret; interpret-postcompose)

private
  variable
    ℓA ℓB : Level
    n : ℕ

------------------------------------------------------------------------
-- 1. The generic CmavoWrapper record.
--
-- A wrapper is a Sem→Sem function lifted to bridi via postcompose.
-- Concrete cmavo (PU, NA, etc.) construct CmavoWrappers; uniformity
-- means functoriality + composition are proved once at the wrapper
-- level rather than per cmavo.
------------------------------------------------------------------------

record CmavoWrapper (Sumti : Set ℓA) (Sem : Set ℓB) : Set (ℓA ⊔ ℓB) where
  constructor mkCmavo
  field
    sem-op : Sem → Sem

open CmavoWrapper public

------------------------------------------------------------------------
-- 2. Apply a wrapper to a bridi.
--
-- The canonical lift: bridi-postcompose with the wrapper's sem-op.
------------------------------------------------------------------------

apply-cmavo :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  CmavoWrapper Sumti Sem →
  Bridi n Sumti Sem → Bridi n Sumti Sem
apply-cmavo cw b = bridi-postcompose (sem-op cw) b

------------------------------------------------------------------------
-- 3. Interpretation coherence.
--
-- Interpreting an apply-cmavo bridi factors through the wrapper's
-- sem-op. Direct corollary of interpret-postcompose at L5.
------------------------------------------------------------------------

interpret-apply-cmavo :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (cw : CmavoWrapper Sumti Sem) (b : Bridi n Sumti Sem) →
  interpret (apply-cmavo cw b) ≡ sem-op cw (interpret b)
interpret-apply-cmavo cw b = interpret-postcompose (sem-op cw) b

------------------------------------------------------------------------
-- 4. Identity cmavo (semantic no-op).
--
-- The KU-like wrapper: structurally a terminator with no semantic
-- effect. Useful as the unit of cmavo composition.
------------------------------------------------------------------------

identity-cmavo :
  {Sumti : Set ℓA} {Sem : Set ℓB} → CmavoWrapper Sumti Sem
identity-cmavo = mkCmavo (λ s → s)

apply-identity-cmavo :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (b : Bridi n Sumti Sem) →
  interpret (apply-cmavo identity-cmavo b) ≡ interpret b
apply-identity-cmavo _ = refl

------------------------------------------------------------------------
-- 5. Composition of cmavo wrappers.
--
-- (cw₂ ∘-cmavo cw₁) applies cw₁ first, then cw₂ — matching the
-- order of bridi-postcompose composition.
------------------------------------------------------------------------

infixr 8 _∘-cmavo_

_∘-cmavo_ :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  CmavoWrapper Sumti Sem →
  CmavoWrapper Sumti Sem →
  CmavoWrapper Sumti Sem
cw₂ ∘-cmavo cw₁ = mkCmavo (λ s → sem-op cw₂ (sem-op cw₁ s))

apply-cmavo-compose :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (cw₂ cw₁ : CmavoWrapper Sumti Sem) (b : Bridi n Sumti Sem) →
  interpret (apply-cmavo (cw₂ ∘-cmavo cw₁) b)
    ≡ sem-op cw₂ (sem-op cw₁ (interpret b))
apply-cmavo-compose _ _ _ = refl

------------------------------------------------------------------------
-- 6. PU : tense markers (pu / ca / ba).
--
-- Parametric in the tense-denotation. A consumer (L9 examples;
-- L10 CCC bridge) supplies tense-sem : TenseMarker → Sem → Sem
-- describing how each tense modifies a semantic value.
------------------------------------------------------------------------

data TenseMarker : Set where
  pu : TenseMarker   -- past
  ca : TenseMarker   -- present
  ba : TenseMarker   -- future

module WithTense
  {ℓA ℓB : Level}
  (Sumti : Set ℓA) (Sem : Set ℓB)
  (tense-sem : TenseMarker → Sem → Sem)
  where

  PU : TenseMarker → CmavoWrapper Sumti Sem
  PU t = mkCmavo (tense-sem t)

------------------------------------------------------------------------
-- 7. NA : negation.
--
-- Parametric in the semantic negation. A consumer supplies
-- `negate : Sem → Sem`. For Sem = "bridi as a proposition,"
-- negate flips truth value; for richer Sem, negate may be more
-- structured.
------------------------------------------------------------------------

module WithNegation
  {ℓA ℓB : Level}
  (Sumti : Set ℓA) (Sem : Set ℓB)
  (negate : Sem → Sem)
  where

  NA : CmavoWrapper Sumti Sem
  NA = mkCmavo negate
