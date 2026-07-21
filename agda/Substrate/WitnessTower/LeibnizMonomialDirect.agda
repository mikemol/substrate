{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.LeibnizMonomialDirect — ⟡leibniz-mono-direct-product.
--
-- THE COFACTOR FOLD IS THE DIRECT INDEXED PRODUCT:
--
--     mono l M  ≡  Πⱼ M[combine j (decode l j)]
--
-- `LeibnizMonomial.mono` (⟡leibniz-det-alg) computes the Leibniz monomial of the
-- permutation `decode l` by a LehmerAlgebra fold whose step is one cofactor
-- expansion along row 0 (a `minor`). This module proves that fold equals the
-- naive product over the permutation's entries — the bridge between the Laplace
-- recursion and direct indexing.
--
-- ⚑ THE PROOF IS ATTACHED TO THE ◂-INDUCTIVE STEP (witness-tower discipline).
-- The whole content is `dprod-step`: the direct product's own step matches
-- `mono-alg`'s step, `M[combine 0 p] *A (rest on the minor)`. That IS the
-- obligation `fold-unique-over` (OrientationUniversal) would demand — the
-- initiality of the ordering tower at the FUNCTION-valued carrier MonoC. In
-- principle `mono ≐ mono` via `fold-unique-over` at the pointwise `_≐_`; in
-- practice the carrier `MonoC n = (Fin (n*n) → A) → A` hides n behind
-- multiplication, so the combinator's abstract recursion cannot pin n at each
-- level. The equivalent direct recursion on `l` pins n from `l : LehmerPath n`
-- injectively at every step — the same inductive-step attachment, in the form
-- Agda infers. (This is also why the module needs no funext: the fold's
-- function-valued carrier is compared pointwise, at each concrete matrix.)
--
-- ⚑ USE. This is step (1) of ⟡leibniz-det-perm-general (det (P σ) ≡ sign σ): the
-- naive product `Πⱼ (P σ)[j, τ j]` is trivially an indicator [τ = σ], so once
-- the fold IS that product, the determinant sum collapses. Steps (2) the
-- indicator via zero-absorb and (3) the one-hot sum-collapse over Sₙ remain.
--
-- Only a MONOID (_*A_, 1A) is required — same as the monomial it is about.
-- Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.WitnessTower.LeibnizMonomialDirect where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Vec using (Vec; _∷_; lookup; map)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
import Substrate.WitnessTower.LeibnizMonomial as LM

module Direct (A : Set) (_*A_ : A → A → A) (1A : A) where

  open LM.Mono A _*A_ 1A public using (Mat; MonoC; minor; mono-alg; mono)

  ------------------------------------------------------------------------
  -- 1. The direct indexed product Πⱼ M[combine j (decode l j)].
  ------------------------------------------------------------------------

  prodFin : {k : ℕ} → (Fin k → A) → A
  prodFin {zero}  f = 1A
  prodFin {suc k} f = f zero *A prodFin (λ i → f (suc i))

  prodFin-cong : {k : ℕ} {f g : Fin k → A} →
                 ((i : Fin k) → f i ≡ g i) → prodFin f ≡ prodFin g
  prodFin-cong {zero}  h = refl
  prodFin-cong {suc k} h = cong₂ _*A_ (h zero) (prodFin-cong (λ i → h (suc i)))

  dprod : {n : ℕ} → LehmerPath n → MonoC n
  dprod {n} l M = prodFin {n} (λ j → M (combine {n} {n} j (lookup (decode l) j)))

  ------------------------------------------------------------------------
  -- 2. The step: the direct product's ◂-recursion matches mono-alg's step.
  ------------------------------------------------------------------------

  -- lookup∘map: lookup (map f v) k ≡ f (lookup v k) — the one Vec fact needed.
  lookup∘map : {B C : Set} {n : ℕ} (f : B → C) (v : Vec B n) (k : Fin n) →
               lookup (map f v) k ≡ f (lookup v k)
  lookup∘map f (x ∷ v) zero    = refl
  lookup∘map f (x ∷ v) (suc k) = lookup∘map f v k

  dprod-step : {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) (M : Mat (suc n)) →
               dprod (l ◂ p) M
               ≡ (M (combine {suc n} {suc n} zero p) *A dprod l (minor p M))
  dprod-step {n} l p M =
    cong (M (combine {suc n} {suc n} zero p) *A_)
      (prodFin-cong {n}
        (λ k →
          trans
            (cong (λ j → M (combine {suc n} {suc n} (suc k) j))
                  (lookup∘map (punchIn p) (decode l) k))
            (sym (minor-combine k))))
    where
      -- (minor p M)(combine k j) ≡ M(combine (suc k)(punchIn p j)), by remQuot-combine.
      minor-combine : (k : Fin n) →
        minor {n} p M (combine {n} {n} k (lookup (decode l) k))
        ≡ M (combine {suc n} {suc n} (suc k) (punchIn p (lookup (decode l) k)))
      minor-combine k =
        cong (λ pr → M (combine {suc n} {suc n} (suc (proj₁ pr)) (punchIn p (proj₂ pr))))
             (remQuot-combine {n} {n} k (lookup (decode l) k))

  ------------------------------------------------------------------------
  -- 3. THE THEOREM: mono l M ≡ dprod l M. Direct recursion on l; the ◂-case
  --    is where the proof lives — mono's own step is definitional, dprod's is
  --    `dprod-step`, and the IH bridges them across the minor.
  ------------------------------------------------------------------------

  mono≡dprod : {n : ℕ} (l : LehmerPath n) (M : Mat n) → mono l M ≡ dprod l M
  mono≡dprod          start   M = refl
  mono≡dprod {suc n} (l ◂ p)  M =
    trans (cong (M (combine {suc n} {suc n} zero p) *A_) (mono≡dprod l (minor p M)))
          (sym (dprod-step l p M))
