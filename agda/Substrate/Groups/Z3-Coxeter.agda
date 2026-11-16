------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter
--
-- ℤ/3ℤ as a Coxeter-style presentation: ⟨a | a³ = ε⟩.
--
-- Thin instance of Substrate.Groups.Coxeter.Cyclic 2. Cyclic provides
-- Gen / Canonical-ex / canonical-cover-ex / σ / insert / insert-canonical-ex
-- / inv / inv-canonical-ex / the parametric c-pos pattern synonym AND
-- the ListPresentation + WithLemmas surface (normalize / _·_ / _≈_ / ε /
-- normalize-distrib / etc.). Consumers use `(Z₃.c-pos k)` for the
-- k-th canonical witness (k ∈ Fin 3); no per-arity pattern names are
-- needed. This file just supplies:
--   * canonical-cover (tuple-style dispatcher over (c-pos zero/₁/₂))
--   * same-canonical (single-Gen decidability)
--   * cube-identity + inv-distrib-canonical (Z₃-specific theorems)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter where
-- ⚑ `Cyclic.Inverse` DISSOLVED (771283c8) — `inv` is `Inverse.Inv`'s (Ⓐ¹²′).
-- Z3 is the only Zn instance carrying this edge; the other four reach `inv`
-- transitively and so never named the dissolved parent.
open import Substrate.Groups.Coxeter.Cyclic.Inverse.Inv 2
open import Substrate.Groups.Coxeter.Cyclic.NthPower 2 using (nth-power-identity)
open import Substrate.Groups.Coxeter.Cyclic.Core 2 using (_·_; _≈_; ε)
-- ⚑ WAS `using (Gen; gen-≟; a)` — the ListPresentation application below needs
-- `insert` too, which the filter excluded (Ⓐ¹²″).  Taken bare, which is what the
-- ban wants regardless: the filter was hiding that this module depends on Base's
-- `insert` at all.
open import Substrate.Groups.Coxeter.Cyclic.Base 2

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃)
open import Substrate.Foundation.Product using (Σ; _×_; _,_)
open import Substrate.Foundation.Negation.Dec

open import Substrate.Groups.Coxeter.Word public
-- ⚑ `normalize` IS NOT `Existential`'s (Ⓐ¹²) — it belongs to `ListPresentation`
-- and arrived through Existential's own open.  A `using` naming a non-export is
-- only a WARNING, so it bound nothing and failed at the use site.
-- ⚑ TAKEN BARE, then renamed separately.  A single clause cannot both RENAME
-- `Canonical-ex` and pass it as a ListPresentation argument — the rename removes
-- the spelling the application needs.  The body uses `Canonical-ex`, so both
-- spellings must be in scope: the bare open supplies the argument, the `using ()
-- renaming` supplies the body's name.
-- ⚑⚑ TWO DISTINCT `Canonical` TYPES, AND THE ALIAS WAS HIDING WHICH IS WHICH.
-- `Base.Canonical-at : Word Gen → Fin (suc n) → Set` is FIN-INDEXED; the
-- `Existential.Canonical-ex : Word Gen → Set` is the single-index existential
-- view (`Σ (Fin (suc n)) (Canonical-ex w)`).  The old clause renamed the SECOND
-- to the FIRST's spelling while a `using (Gen; gen-≟; a)` filter kept the first
-- out of scope — so the collision could not fire and one name meant two types
-- depending on which import you read (Ⓐ¹²″).
--
-- ⚑ I FIRST RETIRED THE ALIAS AS REDUNDANT AND THAT WAS WRONG: the body's uses
-- are single-argument, i.e. the existential view, so pointing them at Base's
-- Fin-indexed type gave `(Fin (fsuc 2) → Set) should be a sort`.  Both types are
-- genuinely needed here; the fix is DISTINCT SPELLINGS, not one alias.
open import Substrate.Groups.Coxeter.Cyclic.Existential 2
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
-- ⚑ `InvCanonical.InvInv` DISSOLVED (771283c8) into six leaves;
-- `inv-inv-canonical-ex` is `InvInvCanonicalEx`'s.
open import Substrate.Groups.Coxeter.Cyclic.InvCanonical.InvInv.InvInvCanonicalEx 2

------------------------------------------------------------------------
-- Tuple-style canonical-cover, built on the parametric c-pos pattern
-- synonym (no per-Zₙ legacy ladder needed).
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.SameCanonical.SameCanonicalViaGen
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Neq
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.GenDec
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert
-- ⚑ RENAMED `canonical-cover` → `canonical-cover-tuple` (Ⓐ¹²″).  `Base` defines
-- a `canonical-cover` of its own (Base.agda:63) and this is a DIFFERENT thing —
-- the Z3-specific tuple form taking three explicit positions, versus Base's
-- generic Fin-indexed cover.  The old `using (Gen; gen-≟; a)` filter on Base kept
-- the generic one out of scope so the clash could not fire; widening the import
-- surfaced it.  Ban-compliant remedy is rename at source, and the SPECIALIZATION
-- is what renames: the generic name belongs to the generic definition.
canonical-cover-tuple :
  ∀ {ℓ} (P : ∀ {w} → Canonical-ex w → Set ℓ) →
  P (c-pos zero) × P (c-pos ₁) × P (c-pos ₂) →
  ∀ {w} (c : Canonical-ex w) → P c
canonical-cover-tuple _ (p , _ , _) (c-pos zero) = p
canonical-cover-tuple _ (_ , p , _) (c-pos ₁)    = p
canonical-cover-tuple _ (_ , _ , p) (c-pos ₂)    = p

------------------------------------------------------------------------
-- Decidable equality.
------------------------------------------------------------------------


same-canonical : {w₁ w₂ : Word Gen} → Canonical-ex w₁ → Canonical-ex w₂ → Dec (w₁ ≡ w₂)
same-canonical = same-canonical-via-Gen gen-≟

------------------------------------------------------------------------
-- Z/3-specific theorem: every element cubes to ε. Specialization of
-- the generic nth-power-identity from Coxeter.Cyclic at n = 2
-- (apply-power-suc w 2 = (w · w) · w by definition).
------------------------------------------------------------------------

cube-identity : (w : Word Gen) → ((w · w) · w) ≈ ε
cube-identity = nth-power-identity

------------------------------------------------------------------------
-- Z/3 is abelian: inv distributes over the product. 9 refls via
-- nested cover (3 outer × 3 inner) on canonical inputs.
------------------------------------------------------------------------

inv-distrib-canonical : {w₁ w₂ : Word Gen} → Canonical-ex w₁ → Canonical-ex w₂ →
                        normalize (inv (normalize (w₁ ++ w₂))) ≡
                        normalize (inv w₁ ++ inv w₂)
-- ⚑ ALL FOUR SITES TAKE THE TUPLE COVER, not Base's Fin-indexed `canonical-cover`
-- (Ⓐ¹²″).  The rename at the definition had to be carried to its uses, and the
-- symptom of missing one is a `Σ _A _B !=< (k : Fin (fsuc 2)) → …` mismatch —
-- the generic cover expecting a Fin function where a triple was supplied.
inv-distrib-canonical c₁ c₂ = canonical-cover-tuple
  (λ {w₁} _ → ∀ {w₂} (c₂' : Canonical-ex w₂) →
              normalize (inv (normalize (w₁ ++ w₂))) ≡
              normalize (inv w₁ ++ inv w₂))
  ( canonical-cover-tuple
      (λ {w₂} _ → normalize (inv (normalize ([] ++ w₂))) ≡
                  normalize (inv [] ++ inv w₂))
      (refl , refl , refl)
  , canonical-cover-tuple
      (λ {w₂} _ → normalize (inv (normalize ((a ∷ []) ++ w₂))) ≡
                  normalize (inv (a ∷ []) ++ inv w₂))
      (refl , refl , refl)
  , canonical-cover-tuple
      (λ {w₂} _ → normalize (inv (normalize ((a ∷ a ∷ []) ++ w₂))) ≡
                  normalize (inv (a ∷ a ∷ []) ++ inv w₂))
      (refl , refl , refl)
  )
  c₁ c₂
