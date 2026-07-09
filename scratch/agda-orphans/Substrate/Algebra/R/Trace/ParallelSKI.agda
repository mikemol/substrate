{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ParallelSKI — ⟡ski-parallel-CR: FULL SKI confluence,
-- the case Newman CANNOT reach (S∙x∙y∙z ⇒ x∙z∙(y∙z) DUPLICATES z ⟹ non-SN, e.g.
-- SII(SII) loops). The Tait–Martin-Löf route: parallel reduction ⇛ (contract any
-- set of redexes at once), its DIAMOND property (via the complete development a*
-- and the Takahashi lemma a ⇛ b → b ⇛ a*), then CR of ⇒ (since ⇒* = ⇛*).
--
-- The diamond needs NEITHER SN NOR local-confluence-only — it is the direct global
-- property, complementary to Newman's WCR+SN. Full SKI is confluent BY THE DIAMOND.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ParallelSKI where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)

------------------------------------------------------------------------
-- 1. Combinator terms + full SKI one-step reduction (β-I, β-K, β-S + congruence).
------------------------------------------------------------------------
data Tm : Set where
  S K I : Tm
  _∙_   : Tm → Tm → Tm

infixl 7 _∙_

data _⇒_ : Tm → Tm → Set where
  β-I    : (x : Tm)             → (I ∙ x) ⇒ x
  β-K    : (x y : Tm)          → ((K ∙ x) ∙ y) ⇒ x
  β-S    : (x y z : Tm)        → (((S ∙ x) ∙ y) ∙ z) ⇒ ((x ∙ z) ∙ (y ∙ z))
  cong-l : {f f' : Tm} (g : Tm) → f ⇒ f' → (f ∙ g) ⇒ (f' ∙ g)
  cong-r : (f : Tm) {g g' : Tm} → g ⇒ g' → (f ∙ g) ⇒ (f ∙ g')

------------------------------------------------------------------------
-- 2. Parallel reduction ⇛: contract any set of redexes simultaneously.
------------------------------------------------------------------------
data _⇛_ : Tm → Tm → Set where
  ⇛S   : S ⇛ S
  ⇛K   : K ⇛ K
  ⇛I   : I ⇛ I
  ⇛app : {f f' g g' : Tm} → f ⇛ f' → g ⇛ g' → (f ∙ g) ⇛ (f' ∙ g')
  ⇛βI  : {x x' : Tm}                → x ⇛ x' → (I ∙ x) ⇛ x'
  ⇛βK  : {x x' y y' : Tm}           → x ⇛ x' → y ⇛ y' → ((K ∙ x) ∙ y) ⇛ x'
  ⇛βS  : {x x' y y' z z' : Tm}      → x ⇛ x' → y ⇛ y' → z ⇛ z'
                                    → (((S ∙ x) ∙ y) ∙ z) ⇛ ((x' ∙ z') ∙ (y' ∙ z'))

-- ⇛ is reflexive.
par-refl : (a : Tm) → a ⇛ a
par-refl S       = ⇛S
par-refl K       = ⇛K
par-refl I       = ⇛I
par-refl (f ∙ g) = ⇛app (par-refl f) (par-refl g)

------------------------------------------------------------------------
-- 3. The COMPLETE DEVELOPMENT a*: contract ALL redexes currently in a (structural,
-- terminating — each recursive call is on a strict subterm). The redex patterns
-- come first; the catch-all handles non-redex applications.
------------------------------------------------------------------------
_* : Tm → Tm
S *                     = S
K *                     = K
I *                     = I
(I ∙ x) *               = x *
((K ∙ x) ∙ y) *         = x *
(((S ∙ x) ∙ y) ∙ z) *   = ((x *) ∙ (z *)) ∙ ((y *) ∙ (z *))
(f ∙ g) *               = (f *) ∙ (g *)

------------------------------------------------------------------------
-- 4. THE TAKAHASHI LEMMA: a ⇛ b → b ⇛ a*. Every parallel reduct of a develops
-- (in one more parallel step) to the complete development a*. Induction on a ⇛ b.
-- The hard case is ⇛app on a redex-shaped term: invert the left sub-derivation to
-- recognise the redex, then fire the corresponding β into a*.
------------------------------------------------------------------------
takahashi : {a b : Tm} → a ⇛ b → b ⇛ (a *)
takahashi ⇛S = ⇛S
takahashi ⇛K = ⇛K
takahashi ⇛I = ⇛I
-- β-redex parallel steps: reduct develops to the contractum's development.
takahashi (⇛βI px)       = takahashi px
takahashi (⇛βK px py)    = takahashi px
takahashi (⇛βS px py pz) =
  ⇛app (⇛app (takahashi px) (takahashi pz)) (⇛app (takahashi py) (takahashi pz))
-- ⇛app on a ROOT REDEX (f∙g reduces at the root): 3 shapes — I∙g, (K∙x)∙g, ((S∙x)∙y)∙g.
takahashi (⇛app ⇛I pg)                     = ⇛βI (takahashi pg)                 -- (I ∙ g)* = g*
takahashi (⇛app (⇛app ⇛K px) pg)           = ⇛βK (takahashi px) (takahashi pg)  -- ((K∙x)∙g)* = x*
takahashi (⇛app (⇛app (⇛app ⇛S px) py) pg) =                                    -- (((S∙x)∙y)∙g)*
  ⇛βS (takahashi px) (takahashi py) (takahashi pg)
-- ⇛app on ANY OTHER application (not a root redex): (f∙g)* = f*∙g*, develop both.
takahashi (⇛app pf pg)                     = ⇛app (takahashi pf) (takahashi pg)

------------------------------------------------------------------------
-- 5. THE DIAMOND: a ⇛ b, a ⇛ c ⟹ both develop to a* — converge at a*.
------------------------------------------------------------------------
diamond : {a b c : Tm} → a ⇛ b → a ⇛ c → Σ Tm (λ d → (b ⇛ d) × (c ⇛ d))
diamond {a} p q = (a *) , (takahashi p , takahashi q)
