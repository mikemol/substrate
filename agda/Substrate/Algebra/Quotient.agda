------------------------------------------------------------------------
-- Substrate.Algebra.Quotient
--
-- QU1 of the QU-arc per [scratch/qu_arc_plan.md].
--
-- A `Quotient A _≈_` packages the bare equivalence-relation data on
-- a carrier A: refl, sym, trans. This is the substrate-native
-- presentation of A modulo _≈_ at its minimal commitment, suitable
-- for use as the base of QU2's UPArrow.
--
-- The substrate's quotient instances factor into two layers:
--
--   * `Quotient A _≈_`  — bare equivalence; the UP-arrow's input.
--     Surreals fit here (≈ⁿ on SurrealFinite n).
--
--   * `Canonical Q`      — extension witness when A has a
--     canonical-form function `canonical : A → A` (terminating,
--     idempotent, ≈-respecting). Coxeter Word `normalize`, ℚ gcd-
--     reduction, V4-Cosets `s-for-anchor X`, F₂ parity all live here.
--
-- The split is per [[feedback-use-vs-commit]]: the UP USES the
-- equivalence; specific instances may commit additionally to a
-- canonical-form picker, which gives decidability / normalisation
-- but is not necessary for the universal property. Per the
-- user's framing (2026-05-21): the term-algebra alignment with
-- surreals is preserved because Quotient's carrier is whatever
-- inductive type the instance provides; surreals' `⟨L ∣ R⟩` over
-- Coxeter Word IS that carrier.
--
-- Per [[project-agda-cubical-extraction-discipline]]: no HITs;
-- the quotient is encoded via (carrier, equivalence) rather than
-- a set-of-classes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Agda.Primitive using (Level; lzero; lsuc; _⊔_)

------------------------------------------------------------------------
-- 1. The base Quotient record: an equivalence relation, nothing more.
--
-- Surreals attach here directly via `_≈ⁿ_` from
-- Substrate.Conway.Equivalence.
------------------------------------------------------------------------

record Quotient {a r : Level} (A : Set a) (_≈_ : A → A → Set r) : Set (a ⊔ r) where
  field
    ≈-refl  : (a : A) → a ≈ a
    ≈-sym   : {a b : A} → a ≈ b → b ≈ a
    ≈-trans : {a b c : A} → a ≈ b → b ≈ c → a ≈ c

open Quotient public

------------------------------------------------------------------------
-- 2. The Canonical extension.
--
-- Many substrate quotients additionally provide a canonical-form
-- function. This extension witnesses that data + its three laws
-- (idempotence, respect of _≈_, soundness).
--
-- When a `Canonical Q` is in scope, we additionally have:
--   canonical-≡⇒≈ : canonical a ≡ canonical b → a ≈ b
--   ≈⇒canonical-≡ : a ≈ b → canonical a ≡ canonical b
-- giving "represents the same class" via propositional equality on
-- canonical representatives.
------------------------------------------------------------------------

record Canonical      -- ⟦shape:de760d07 {a r,canonical,canonical-idempotent⟧
  {a r : Level} {A : Set a} {_≈_ : A → A → Set r} (Q : Quotient A _≈_) : Set (a ⊔ r) where
  field
    canonical            : A → A
    canonical-idempotent : (a : A) → canonical (canonical a) ≡ canonical a
    canonical-respects-≈ : {a b : A} → a ≈ b → canonical a ≡ canonical b
    ≈-canonical          : (a : A) → a ≈ canonical a

open Canonical public

------------------------------------------------------------------------
-- 3. Derived characterisations under a Canonical extension.
------------------------------------------------------------------------

canonical-≡⇒≈ :
  {ℓ r : Level} {A : Set ℓ} {_≈_ : A → A → Set r}
  {Q : Quotient A _≈_}
  (C : Canonical Q)
  (a b : A) →
  canonical C a ≡ canonical C b → a ≈ b
canonical-≡⇒≈ {_≈_ = _≈_} {Q = Q} C a b eq = ≈-trans Q step₁ step₂
  where
    step₁ : a ≈ canonical C b
    step₁ rewrite sym eq = ≈-canonical C a

    step₂ : canonical C b ≈ b
    step₂ = ≈-sym Q (≈-canonical C b)

≈⇒canonical-≡ :
  {ℓ r : Level} {A : Set ℓ} {_≈_ : A → A → Set r}
  {Q : Quotient A _≈_}
  (C : Canonical Q)
  {a b : A} →
  a ≈ b → canonical C a ≡ canonical C b
≈⇒canonical-≡ C = canonical-respects-≈ C

------------------------------------------------------------------------
-- 3½. Retraction ⟹ Canonical: the SPLIT-IDEMPOTENT apex.
--
-- A quotient by `ker F` (F : A → B) is realized constructively WITHOUT a
-- quotient type exactly when F SPLITS — a section s : B → A with F ∘ s ≡ id.
-- Then e = s ∘ F : A → A is idempotent (a split idempotent / Karoubi), and e
-- is a `Canonical` form for `ker F`: the canonical representatives are its
-- image. So "no quotient types under --safe --without-K" is a non-issue — a
-- lossless round-trip (the ℚ↔R retraction, eval/reify, …) IS a retraction,
-- hence a section-based quotient.
--
-- This is the apex of a scattered cluster, each an (F, s, F∘s≡id) retraction
-- whose split idempotent is its canonical form: eval/reify (UPTerm/≈ᵤ;
-- `split-Canonical eval reify eval-reify`), ℚ `reduce`, the wedge `recon`
-- (a ≡ recon q b r), the EEA CF-shape, CRT `combine`, Coxeter `normalize`,
-- GenericHodgeStar `star`/`star-inv`, BeckChevalley section/retraction. The
-- "which quotient" either/or (raw / semantic / presented) collapses: each is
-- `ker (fold into a target)`; choosing the quotient = choosing the target;
-- and when that fold splits, this lemma realizes it. (cf. foldUPTerm = the
-- free-category universal extension; eval = its instance; UP4 = ker eval.)
------------------------------------------------------------------------

-- The kernel of any map, as a relation: x ≈ y iff F sends them to the same B.
KerRel : {a b : Level} {A : Set a} {B : Set b} → (A → B) → A → A → Set b
KerRel F x y = F x ≡ F y

-- Every map's kernel is an equivalence (≡ is, and KerRel just pulls it back).
ker-Quotient : {a b : Level} {A : Set a} {B : Set b}
             → (F : A → B) → Quotient A (KerRel F)
ker-Quotient F = record { ≈-refl = λ _ → refl ; ≈-sym = sym ; ≈-trans = trans }

-- A retraction F∘s≡id splits the idempotent e = s∘F, which IS a Canonical
-- form for ker F. All four laws fall out of `retract` + `cong s`.
split-Canonical :
  {a b : Level} {A : Set a} {B : Set b}
  (F : A → B) (s : B → A) (retract : (y : B) → F (s y) ≡ y) →
  Canonical (ker-Quotient F)
split-Canonical F s retract = record
  { canonical            = λ a → s (F a)
  ; canonical-idempotent = λ a → cong s (retract (F a))
  ; canonical-respects-≈ = λ e → cong s e
  ; ≈-canonical          = λ a → sym (retract (F a))
  }

------------------------------------------------------------------------
-- 4. Capstone for QU1.
--
-- Quotient + Canonical landed. QU2 lifts the base Quotient into a
-- UPArrow; surreals attach (Canonical-free) at QU7, and the other
-- four substrate instances attach with a Canonical witness at QU5,
-- QU6, QU8, QU9.
------------------------------------------------------------------------
