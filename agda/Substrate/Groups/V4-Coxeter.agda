------------------------------------------------------------------------
-- Substrate.Groups.V4-Coxeter
--
-- V₄ as a Coxeter presentation: ⟨A, B | A² = B² = ε, AB = BA⟩.
--
-- This file is the V₄ INSTANTIATION of Substrate.Groups.Coxeter.Core.
-- The per-construct work (Gen, Canonical, insert, the 3 invariants
-- that depend on V₄'s specific relations) lives here. The scalable
-- foundation (Word, normalize, _·_, _≈_, _≉_, ε, the bridge lemmas,
-- clash, ++-assoc-4) is inherited from Core via instantiation.
--
-- Per [[feedback-v4-typeclass-architecture]] applied at the Coxeter
-- level: ~280 lines of reusable Core inherited; the V₄-specific work
-- is ~250 lines (Gen + insert + Canonical + insert-involution +
-- insert-commute + insert-append-lemma + same-canonical + eval-
-- canonical + V₄-4-product).
--
-- See: catalog/cocycles.md § CY-5 — V₄ ⋊ S₃ ≅ S₄;
--      Substrate.Groups.V4 — the parallel 4-ctor representation;
--      Substrate.Groups.Coxeter.Core — the parametric foundation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.V4-Coxeter where

open import Substrate.Groups.Coxeter.Word public
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; cong₂; _≢_; sym-trans; cong-trans)

------------------------------------------------------------------------
-- 1. V₄-specific data: generators, canonical forms, insert.
------------------------------------------------------------------------

data Gen : Set where
  A B : Gen

data Canonical : Word Gen → Set where
  c-ε  : Canonical []
  c-A  : Canonical (A ∷ [])
  c-B  : Canonical (B ∷ [])
  c-AB : Canonical (A ∷ B ∷ [])

insert : Gen → Word Gen → Word Gen
insert A []           = A ∷ []
insert A (A ∷ [])     = []
insert A (B ∷ [])     = A ∷ B ∷ []
insert A (A ∷ B ∷ []) = B ∷ []
insert B []           = B ∷ []
insert B (A ∷ [])     = A ∷ B ∷ []
insert B (B ∷ [])     = []
insert B (A ∷ B ∷ []) = A ∷ []
insert g w            = g ∷ w  -- fallback structural safety

insert-canonical : (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w)
insert-canonical A c-ε  = c-A
insert-canonical A c-A  = c-ε
insert-canonical A c-B  = c-AB
insert-canonical A c-AB = c-B
insert-canonical B c-ε  = c-B
insert-canonical B c-A  = c-AB
insert-canonical B c-B  = c-ε
insert-canonical B c-AB = c-A

------------------------------------------------------------------------
-- 2. Open the ListPresentation wrapper with V₄'s atoms.
--
-- ListPresentation defines Word = Word Gen + normalize + normalize-
-- canonical and exposes the WithLemmas sub-module that takes the
-- per-relation obligations.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical c-ε insert insert-canonical public

------------------------------------------------------------------------
-- 3. V₄-specific Coxeter relations (lifted to the insert level).
--
-- insert-involution: insert g · insert g = id on canonical (A² = ε,
-- B² = ε). 8 refl cases.
--
-- insert-commute: insert A and insert B commute on canonical (AB =
-- BA). 10 refl cases (g = h trivial; g ≠ h × 4 canonical forms × 2).
------------------------------------------------------------------------

insert-involution : (g : Gen) {w : Word Gen} → Canonical w →
                    insert g (insert g w) ≡ w
insert-involution A c-ε  = refl
insert-involution A c-A  = refl
insert-involution A c-B  = refl
insert-involution A c-AB = refl
insert-involution B c-ε  = refl
insert-involution B c-A  = refl
insert-involution B c-B  = refl
insert-involution B c-AB = refl

insert-commute : (g h : Gen) {w : Word Gen} → Canonical w →
                 insert g (insert h w) ≡ insert h (insert g w)
insert-commute A A _    = refl
insert-commute B B _    = refl
insert-commute A B c-ε  = refl
insert-commute A B c-A  = refl
insert-commute A B c-B  = refl
insert-commute A B c-AB = refl
insert-commute B A c-ε  = refl
insert-commute B A c-A  = refl
insert-commute B A c-B  = refl
insert-commute B A c-AB = refl

------------------------------------------------------------------------
-- 4. The three Core obligations: canonical-is-fixed (4 refl) +
-- insert-append-lemma (8 cases using insert-involution + insert-
-- commute).
------------------------------------------------------------------------

canonical-is-fixed-V4 : {w : Word Gen} → Canonical w → normalize w ≡ w
canonical-is-fixed-V4 c-ε  = refl
canonical-is-fixed-V4 c-A  = refl
canonical-is-fixed-V4 c-B  = refl
canonical-is-fixed-V4 c-AB = refl

insert-append-lemma-V4 :
  (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical w →
  normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma-V4 A {[]}         w₂ c-ε  = refl
insert-append-lemma-V4 A {A ∷ []}     w₂ c-A  =
  sym (insert-involution A (normalize-canonical w₂))
insert-append-lemma-V4 A {B ∷ []}     w₂ c-B  = refl
insert-append-lemma-V4 A {A ∷ B ∷ []} w₂ c-AB =
  sym (insert-involution A (insert-canonical B (normalize-canonical w₂)))
insert-append-lemma-V4 B {[]}         w₂ c-ε  = refl
insert-append-lemma-V4 B {A ∷ []}     w₂ c-A  =
  insert-commute A B (normalize-canonical w₂)
insert-append-lemma-V4 B {B ∷ []}     w₂ c-B  =
  sym (insert-involution B (normalize-canonical w₂))
insert-append-lemma-V4 B {A ∷ B ∷ []} w₂ c-AB =
  sym-trans (cong (insert A)
                  (insert-involution B (normalize-canonical w₂)))
            (sym (insert-commute B A
                    (insert-canonical B (normalize-canonical w₂))))

------------------------------------------------------------------------
-- 5. Open WithLemmas to inherit the full abstract Core surface.
--
-- This brings _·_, _≈_, _≉_, ε, normalize-idem, normalize-append,
-- normalize-append-right, normalize-cong-right, normalize-distrib,
-- normalize-triple, normalize-quad, ≉-idem, clash, ++-assoc-4 into
-- scope (re-exported via `public`).
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed-V4 insert-append-lemma-V4 public

------------------------------------------------------------------------
-- 6. Decidable equality on Canonical forms — V₄-specific (depends on
-- the 4 ctors). Used by eval-canonical's clash dispatcher.
------------------------------------------------------------------------

gen-≟ : (g₁ g₂ : Gen) → Dec (g₁ ≡ g₂)
gen-≟ A A = yes refl
gen-≟ A B = no (λ ())
gen-≟ B A = no (λ ())
gen-≟ B B = yes refl

open import Substrate.Groups.Coxeter.SameCanonical
  using (same-canonical-via-Gen)

same-canonical : {w₁ w₂ : Word Gen} → Canonical w₁ → Canonical w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- 7. V₄-specific theorem: 4 pairwise-distinct V₄ elements multiply
-- to ε. Composes flatten-product (bridge from _·_ to ++ on canonical)
-- with eval-canonical (124-pattern clash + refl enumeration).
--
-- This part DOES NOT scale to larger Coxeter groups (S₃: 720
-- orderings; S₄: 24!). It's bespoke to V₄'s |G| = 4 + abelian +
-- exponent-2 structure. Per [[feedback-v4-typeclass-architecture]]:
-- enumeration-based finite-group theorems live with the instance.
------------------------------------------------------------------------

private
  -- Bridge: (w₁ · w₂) · (w₃ · w₄) normalizes to a flat 4-arg form.
  -- Composes normalize-idem (strip outer normalize from nested _·_),
  -- sym normalize-append + sym normalize-append-right (extract inner
  -- normalizes), cong normalize ∘ ++-assoc-4 (rearrange), normalize-
  -- quad (push normalize through each operand).
  flatten-product :
    (w₁ w₂ w₃ w₄ : Word Gen) →
    normalize ((w₁ · w₂) · (w₃ · w₄)) ≡
    normalize (normalize w₁ ++ normalize w₂ ++ normalize w₃ ++ normalize w₄)
  flatten-product w₁ w₂ w₃ w₄ =
    trans (normalize-idem (normalize (w₁ ++ w₂) ++ normalize (w₃ ++ w₄)))
    (sym-trans (normalize-append (w₁ ++ w₂) (normalize (w₃ ++ w₄)))
    (sym-trans (normalize-append-right (w₁ ++ w₂) (w₃ ++ w₄))
    (cong-trans normalize (++-assoc-4 w₁ w₂ w₃ w₄)
           (normalize-quad w₁ w₂ w₃ w₄))))

  -- eval-canonical: on 4 Canonical proofs + 6 pairwise ≉, the
  -- concatenated normalize is `[]`. 124 patterns total (24 distinct
  -- refl + 100 clash-killed via canonical pairs).
  --
  -- Same combinatorial weight as Substrate.Groups.V4-Normality's
  -- V₄-4-product on V₄^4 — Agda's coverage checker doesn't propagate
  -- `no _` evidence to auto-eliminate impossible patterns, so the
  -- "clash technique" doesn't shrink this. The architectural value
  -- vs V4-Normality is that the per-instance theorem lives WITH the
  -- presentation (V4-Coxeter), not bolted on at the action level.
  eval-canonical :
    {w₁ w₂ w₃ w₄ : Word Gen}
    (c₁ : Canonical w₁) (c₂ : Canonical w₂)
    (c₃ : Canonical w₃) (c₄ : Canonical w₄) →
    w₁ ≉ w₂ → w₁ ≉ w₃ → w₁ ≉ w₄ → w₂ ≉ w₃ → w₂ ≉ w₄ → w₃ ≉ w₄ →
    normalize (w₁ ++ w₂ ++ w₃ ++ w₄) ≡ []
  -- 24 all-distinct refl cases:
  eval-canonical c-ε  c-A  c-B  c-AB _ _ _ _ _ _ = refl
  eval-canonical c-ε  c-A  c-AB c-B  _ _ _ _ _ _ = refl
  eval-canonical c-ε  c-B  c-A  c-AB _ _ _ _ _ _ = refl
  eval-canonical c-ε  c-B  c-AB c-A  _ _ _ _ _ _ = refl
  eval-canonical c-ε  c-AB c-A  c-B  _ _ _ _ _ _ = refl
  eval-canonical c-ε  c-AB c-B  c-A  _ _ _ _ _ _ = refl
  eval-canonical c-A  c-ε  c-B  c-AB _ _ _ _ _ _ = refl
  eval-canonical c-A  c-ε  c-AB c-B  _ _ _ _ _ _ = refl
  eval-canonical c-A  c-B  c-ε  c-AB _ _ _ _ _ _ = refl
  eval-canonical c-A  c-B  c-AB c-ε  _ _ _ _ _ _ = refl
  eval-canonical c-A  c-AB c-ε  c-B  _ _ _ _ _ _ = refl
  eval-canonical c-A  c-AB c-B  c-ε  _ _ _ _ _ _ = refl
  eval-canonical c-B  c-ε  c-A  c-AB _ _ _ _ _ _ = refl
  eval-canonical c-B  c-ε  c-AB c-A  _ _ _ _ _ _ = refl
  eval-canonical c-B  c-A  c-ε  c-AB _ _ _ _ _ _ = refl
  eval-canonical c-B  c-A  c-AB c-ε  _ _ _ _ _ _ = refl
  eval-canonical c-B  c-AB c-ε  c-A  _ _ _ _ _ _ = refl
  eval-canonical c-B  c-AB c-A  c-ε  _ _ _ _ _ _ = refl
  eval-canonical c-AB c-ε  c-A  c-B  _ _ _ _ _ _ = refl
  eval-canonical c-AB c-ε  c-B  c-A  _ _ _ _ _ _ = refl
  eval-canonical c-AB c-A  c-ε  c-B  _ _ _ _ _ _ = refl
  eval-canonical c-AB c-A  c-B  c-ε  _ _ _ _ _ _ = refl
  eval-canonical c-AB c-B  c-ε  c-A  _ _ _ _ _ _ = refl
  eval-canonical c-AB c-B  c-A  c-ε  _ _ _ _ _ _ = refl
  -- c₁ = c₂ kills (4 patterns × 16 wildcards):
  eval-canonical c-ε  c-ε  _ _ e₁ _ _ _ _ _ = clash c-ε  c-ε  e₁ refl
  eval-canonical c-A  c-A  _ _ e₁ _ _ _ _ _ = clash c-A  c-A  e₁ refl
  eval-canonical c-B  c-B  _ _ e₁ _ _ _ _ _ = clash c-B  c-B  e₁ refl
  eval-canonical c-AB c-AB _ _ e₁ _ _ _ _ _ = clash c-AB c-AB e₁ refl
  -- c₁ ≠ c₂, c₃ = c₁ or c₃ = c₂ (24 patterns × 4 wildcards on c₄):
  eval-canonical c-ε  c-A  c-ε  _ _ e₂ _ _  _  _  = clash c-ε  c-ε  e₂ refl
  eval-canonical c-ε  c-A  c-A  _ _ _  _ e₄ _  _  = clash c-A  c-A  e₄ refl
  eval-canonical c-ε  c-B  c-ε  _ _ e₂ _ _  _  _  = clash c-ε  c-ε  e₂ refl
  eval-canonical c-ε  c-B  c-B  _ _ _  _ e₄ _  _  = clash c-B  c-B  e₄ refl
  eval-canonical c-ε  c-AB c-ε  _ _ e₂ _ _  _  _  = clash c-ε  c-ε  e₂ refl
  eval-canonical c-ε  c-AB c-AB _ _ _  _ e₄ _  _  = clash c-AB c-AB e₄ refl
  eval-canonical c-A  c-ε  c-A  _ _ e₂ _ _  _  _  = clash c-A  c-A  e₂ refl
  eval-canonical c-A  c-ε  c-ε  _ _ _  _ e₄ _  _  = clash c-ε  c-ε  e₄ refl
  eval-canonical c-A  c-B  c-A  _ _ e₂ _ _  _  _  = clash c-A  c-A  e₂ refl
  eval-canonical c-A  c-B  c-B  _ _ _  _ e₄ _  _  = clash c-B  c-B  e₄ refl
  eval-canonical c-A  c-AB c-A  _ _ e₂ _ _  _  _  = clash c-A  c-A  e₂ refl
  eval-canonical c-A  c-AB c-AB _ _ _  _ e₄ _  _  = clash c-AB c-AB e₄ refl
  eval-canonical c-B  c-ε  c-B  _ _ e₂ _ _  _  _  = clash c-B  c-B  e₂ refl
  eval-canonical c-B  c-ε  c-ε  _ _ _  _ e₄ _  _  = clash c-ε  c-ε  e₄ refl
  eval-canonical c-B  c-A  c-B  _ _ e₂ _ _  _  _  = clash c-B  c-B  e₂ refl
  eval-canonical c-B  c-A  c-A  _ _ _  _ e₄ _  _  = clash c-A  c-A  e₄ refl
  eval-canonical c-B  c-AB c-B  _ _ e₂ _ _  _  _  = clash c-B  c-B  e₂ refl
  eval-canonical c-B  c-AB c-AB _ _ _  _ e₄ _  _  = clash c-AB c-AB e₄ refl
  eval-canonical c-AB c-ε  c-AB _ _ e₂ _ _  _  _  = clash c-AB c-AB e₂ refl
  eval-canonical c-AB c-ε  c-ε  _ _ _  _ e₄ _  _  = clash c-ε  c-ε  e₄ refl
  eval-canonical c-AB c-A  c-AB _ _ e₂ _ _  _  _  = clash c-AB c-AB e₂ refl
  eval-canonical c-AB c-A  c-A  _ _ _  _ e₄ _  _  = clash c-A  c-A  e₄ refl
  eval-canonical c-AB c-B  c-AB _ _ e₂ _ _  _  _  = clash c-AB c-AB e₂ refl
  eval-canonical c-AB c-B  c-B  _ _ _  _ e₄ _  _  = clash c-B  c-B  e₄ refl
  -- c₁, c₂, c₃ all distinct but c₄ ∈ {c₁, c₂, c₃} (72 patterns):
  eval-canonical c-ε  c-A  c-B  c-ε  _ _ e₃ _  _  _  = clash c-ε  c-ε  e₃ refl
  eval-canonical c-ε  c-A  c-B  c-A  _ _ _  _  e₅ _  = clash c-A  c-A  e₅ refl
  eval-canonical c-ε  c-A  c-B  c-B  _ _ _  _  _  e₆ = clash c-B  c-B  e₆ refl
  eval-canonical c-ε  c-A  c-AB c-ε  _ _ e₃ _  _  _  = clash c-ε  c-ε  e₃ refl
  eval-canonical c-ε  c-A  c-AB c-A  _ _ _  _  e₅ _  = clash c-A  c-A  e₅ refl
  eval-canonical c-ε  c-A  c-AB c-AB _ _ _  _  _  e₆ = clash c-AB c-AB e₆ refl
  eval-canonical c-ε  c-B  c-A  c-ε  _ _ e₃ _  _  _  = clash c-ε  c-ε  e₃ refl
  eval-canonical c-ε  c-B  c-A  c-A  _ _ _  _  _  e₆ = clash c-A  c-A  e₆ refl
  eval-canonical c-ε  c-B  c-A  c-B  _ _ _  _  e₅ _  = clash c-B  c-B  e₅ refl
  eval-canonical c-ε  c-B  c-AB c-ε  _ _ e₃ _  _  _  = clash c-ε  c-ε  e₃ refl
  eval-canonical c-ε  c-B  c-AB c-B  _ _ _  _  e₅ _  = clash c-B  c-B  e₅ refl
  eval-canonical c-ε  c-B  c-AB c-AB _ _ _  _  _  e₆ = clash c-AB c-AB e₆ refl
  eval-canonical c-ε  c-AB c-A  c-ε  _ _ e₃ _  _  _  = clash c-ε  c-ε  e₃ refl
  eval-canonical c-ε  c-AB c-A  c-A  _ _ _  _  _  e₆ = clash c-A  c-A  e₆ refl
  eval-canonical c-ε  c-AB c-A  c-AB _ _ _  _  e₅ _  = clash c-AB c-AB e₅ refl
  eval-canonical c-ε  c-AB c-B  c-ε  _ _ e₃ _  _  _  = clash c-ε  c-ε  e₃ refl
  eval-canonical c-ε  c-AB c-B  c-B  _ _ _  _  _  e₆ = clash c-B  c-B  e₆ refl
  eval-canonical c-ε  c-AB c-B  c-AB _ _ _  _  e₅ _  = clash c-AB c-AB e₅ refl
  eval-canonical c-A  c-ε  c-B  c-A  _ _ e₃ _  _  _  = clash c-A  c-A  e₃ refl
  eval-canonical c-A  c-ε  c-B  c-ε  _ _ _  _  e₅ _  = clash c-ε  c-ε  e₅ refl
  eval-canonical c-A  c-ε  c-B  c-B  _ _ _  _  _  e₆ = clash c-B  c-B  e₆ refl
  eval-canonical c-A  c-ε  c-AB c-A  _ _ e₃ _  _  _  = clash c-A  c-A  e₃ refl
  eval-canonical c-A  c-ε  c-AB c-ε  _ _ _  _  e₅ _  = clash c-ε  c-ε  e₅ refl
  eval-canonical c-A  c-ε  c-AB c-AB _ _ _  _  _  e₆ = clash c-AB c-AB e₆ refl
  eval-canonical c-A  c-B  c-ε  c-A  _ _ e₃ _  _  _  = clash c-A  c-A  e₃ refl
  eval-canonical c-A  c-B  c-ε  c-B  _ _ _  _  e₅ _  = clash c-B  c-B  e₅ refl
  eval-canonical c-A  c-B  c-ε  c-ε  _ _ _  _  _  e₆ = clash c-ε  c-ε  e₆ refl
  eval-canonical c-A  c-B  c-AB c-A  _ _ e₃ _  _  _  = clash c-A  c-A  e₃ refl
  eval-canonical c-A  c-B  c-AB c-B  _ _ _  _  e₅ _  = clash c-B  c-B  e₅ refl
  eval-canonical c-A  c-B  c-AB c-AB _ _ _  _  _  e₆ = clash c-AB c-AB e₆ refl
  eval-canonical c-A  c-AB c-ε  c-A  _ _ e₃ _  _  _  = clash c-A  c-A  e₃ refl
  eval-canonical c-A  c-AB c-ε  c-AB _ _ _  _  e₅ _  = clash c-AB c-AB e₅ refl
  eval-canonical c-A  c-AB c-ε  c-ε  _ _ _  _  _  e₆ = clash c-ε  c-ε  e₆ refl
  eval-canonical c-A  c-AB c-B  c-A  _ _ e₃ _  _  _  = clash c-A  c-A  e₃ refl
  eval-canonical c-A  c-AB c-B  c-AB _ _ _  _  e₅ _  = clash c-AB c-AB e₅ refl
  eval-canonical c-A  c-AB c-B  c-B  _ _ _  _  _  e₆ = clash c-B  c-B  e₆ refl
  eval-canonical c-B  c-ε  c-A  c-B  _ _ e₃ _  _  _  = clash c-B  c-B  e₃ refl
  eval-canonical c-B  c-ε  c-A  c-ε  _ _ _  _  e₅ _  = clash c-ε  c-ε  e₅ refl
  eval-canonical c-B  c-ε  c-A  c-A  _ _ _  _  _  e₆ = clash c-A  c-A  e₆ refl
  eval-canonical c-B  c-ε  c-AB c-B  _ _ e₃ _  _  _  = clash c-B  c-B  e₃ refl
  eval-canonical c-B  c-ε  c-AB c-ε  _ _ _  _  e₅ _  = clash c-ε  c-ε  e₅ refl
  eval-canonical c-B  c-ε  c-AB c-AB _ _ _  _  _  e₆ = clash c-AB c-AB e₆ refl
  eval-canonical c-B  c-A  c-ε  c-B  _ _ e₃ _  _  _  = clash c-B  c-B  e₃ refl
  eval-canonical c-B  c-A  c-ε  c-A  _ _ _  _  e₅ _  = clash c-A  c-A  e₅ refl
  eval-canonical c-B  c-A  c-ε  c-ε  _ _ _  _  _  e₆ = clash c-ε  c-ε  e₆ refl
  eval-canonical c-B  c-A  c-AB c-B  _ _ e₃ _  _  _  = clash c-B  c-B  e₃ refl
  eval-canonical c-B  c-A  c-AB c-A  _ _ _  _  e₅ _  = clash c-A  c-A  e₅ refl
  eval-canonical c-B  c-A  c-AB c-AB _ _ _  _  _  e₆ = clash c-AB c-AB e₆ refl
  eval-canonical c-B  c-AB c-ε  c-B  _ _ e₃ _  _  _  = clash c-B  c-B  e₃ refl
  eval-canonical c-B  c-AB c-ε  c-AB _ _ _  _  e₅ _  = clash c-AB c-AB e₅ refl
  eval-canonical c-B  c-AB c-ε  c-ε  _ _ _  _  _  e₆ = clash c-ε  c-ε  e₆ refl
  eval-canonical c-B  c-AB c-A  c-B  _ _ e₃ _  _  _  = clash c-B  c-B  e₃ refl
  eval-canonical c-B  c-AB c-A  c-AB _ _ _  _  e₅ _  = clash c-AB c-AB e₅ refl
  eval-canonical c-B  c-AB c-A  c-A  _ _ _  _  _  e₆ = clash c-A  c-A  e₆ refl
  eval-canonical c-AB c-ε  c-A  c-AB _ _ e₃ _  _  _  = clash c-AB c-AB e₃ refl
  eval-canonical c-AB c-ε  c-A  c-ε  _ _ _  _  e₅ _  = clash c-ε  c-ε  e₅ refl
  eval-canonical c-AB c-ε  c-A  c-A  _ _ _  _  _  e₆ = clash c-A  c-A  e₆ refl
  eval-canonical c-AB c-ε  c-B  c-AB _ _ e₃ _  _  _  = clash c-AB c-AB e₃ refl
  eval-canonical c-AB c-ε  c-B  c-ε  _ _ _  _  e₅ _  = clash c-ε  c-ε  e₅ refl
  eval-canonical c-AB c-ε  c-B  c-B  _ _ _  _  _  e₆ = clash c-B  c-B  e₆ refl
  eval-canonical c-AB c-A  c-ε  c-AB _ _ e₃ _  _  _  = clash c-AB c-AB e₃ refl
  eval-canonical c-AB c-A  c-ε  c-A  _ _ _  _  e₅ _  = clash c-A  c-A  e₅ refl
  eval-canonical c-AB c-A  c-ε  c-ε  _ _ _  _  _  e₆ = clash c-ε  c-ε  e₆ refl
  eval-canonical c-AB c-A  c-B  c-AB _ _ e₃ _  _  _  = clash c-AB c-AB e₃ refl
  eval-canonical c-AB c-A  c-B  c-A  _ _ _  _  e₅ _  = clash c-A  c-A  e₅ refl
  eval-canonical c-AB c-A  c-B  c-B  _ _ _  _  _  e₆ = clash c-B  c-B  e₆ refl
  eval-canonical c-AB c-B  c-ε  c-AB _ _ e₃ _  _  _  = clash c-AB c-AB e₃ refl
  eval-canonical c-AB c-B  c-ε  c-B  _ _ _  _  e₅ _  = clash c-B  c-B  e₅ refl
  eval-canonical c-AB c-B  c-ε  c-ε  _ _ _  _  _  e₆ = clash c-ε  c-ε  e₆ refl
  eval-canonical c-AB c-B  c-A  c-AB _ _ e₃ _  _  _  = clash c-AB c-AB e₃ refl
  eval-canonical c-AB c-B  c-A  c-B  _ _ _  _  e₅ _  = clash c-B  c-B  e₅ refl
  eval-canonical c-AB c-B  c-A  c-A  _ _ _  _  _  e₆ = clash c-A  c-A  e₆ refl

V₄-4-product :
  (w₁ w₂ w₃ w₄ : Word Gen) →
  w₁ ≉ w₂ → w₁ ≉ w₃ → w₁ ≉ w₄ → w₂ ≉ w₃ → w₂ ≉ w₄ → w₃ ≉ w₄ →
  ((w₁ · w₂) · (w₃ · w₄)) ≈ ε
V₄-4-product w₁ w₂ w₃ w₄ e₁ e₂ e₃ e₄ e₅ e₆ =
  trans (flatten-product w₁ w₂ w₃ w₄)
        (eval-canonical (normalize-canonical w₁) (normalize-canonical w₂)
                        (normalize-canonical w₃) (normalize-canonical w₄)
                        (≉-idem w₁ w₂ e₁) (≉-idem w₁ w₃ e₂) (≉-idem w₁ w₄ e₃)
                        (≉-idem w₂ w₃ e₄) (≉-idem w₂ w₄ e₅) (≉-idem w₃ w₄ e₆))
