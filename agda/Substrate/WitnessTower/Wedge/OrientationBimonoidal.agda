------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationBimonoidal
--
-- ⟡rig-11 — THE UNIFYING FRAME (the generic record). The recursive-common-structure
-- endpoint of the whole arc: ⊕ and ⊗ are ONE structure — a graded product over a grading
-- MONOID — differing only in the grading (ℕ,+,0) vs (ℕ,·,1).
--
--   GradedProductOver (op)(ε)(C) = { u : C ε ; _∧_ : C i → C j → C (op i j) }
--
-- The existing Algebra.Wedge.Product.GradedProduct is exactly GradedProductOver _+_ 0.
-- This module is PROOF-FREE (def/proof separation): the concrete instances (⊕-over,
-- ⊗-over) and the fact that both associators instantiate the ONE generic law live in
-- .Properties. The full four-law table (assoc/unit/comm-iso/comm-nat on both fibres, all
-- proven this arc) is documented there.
--
-- (Reuse-search catalog.db: no bimonoidal/rig-category record exists; Category.Symmetric-
-- Monoidal needs a full CategoryOf of orderings — heavier.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationBimonoidal where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; subst)

------------------------------------------------------------------------
-- The parameterized structure: a graded product over a grading operation (op, ε).
------------------------------------------------------------------------

record GradedProductOver (op : ℕ → ℕ → ℕ) (ε : ℕ) (C : ℕ → Set) : Set where
  field
    u   : C ε
    _∧_ : {i j : ℕ} → C i → C j → C (op i j)

open GradedProductOver public

-- the generic associativity law-type over the grading operation's own associativity.
GradedAssocOver : {op : ℕ → ℕ → ℕ} {ε : ℕ} {C : ℕ → Set}
                  (assoc : (x y z : ℕ) → op (op x y) z ≡ op x (op y z))
                  (P : GradedProductOver op ε C) → Set
GradedAssocOver {C = C} assoc P =
  ∀ {i j k} (a : C i) (b : C j) (c : C k) →
  subst C (assoc i j k) (_∧_ P (_∧_ P a b) c) ≡ _∧_ P a (_∧_ P b c)

------------------------------------------------------------------------
-- ⟡lift-generic — THE GRADED HOMOMORPHISM, over an arbitrary grading (op, ε) AND an
-- arbitrary TARGET EQUALITY. This is the recursive bottom of the ⊕/⊗ tower: fold-⊕
-- (the additive catamorphism-hom) and ⊗-combine (the multiplicative lookup-hom) are
-- ONE structure — a map preserving u and _∧_ — differing ONLY in the target equality:
--   * additive: the target carrier is DATA, so _≈_ = _≡_ (strict);
--   * multiplicative: the target carrier is a Fin-endofunction Fin n → Fin n, so _≈_ is
--     POINTWISE equality (lookup-extensional) — the funext-free reading of the same law.
-- The target equality is a PARAMETER, not a picked side: a homomorphism is always valued
-- in the codomain's equality. (Algebra.Wedge.Product.Hom.GradedHom is the (+,0,≡) case;
-- this generalizes the grading op AND relaxes ≡ to any _≈_, so BOTH fibres are instances.)
--
-- Law-free by design (the 3 hom fields only): instances CONSTRUCT it; id/∘ composition
-- (which would need _≈_ an equivalence) is out of scope here.
------------------------------------------------------------------------

record GradedHomOver
  {op : ℕ → ℕ → ℕ} {ε : ℕ} {Cᴾ Cᴽ : ℕ → Set}
  (P : GradedProductOver op ε Cᴾ) (Q : GradedProductOver op ε Cᴽ)
  (_≈_ : {n : ℕ} → Cᴽ n → Cᴽ n → Set) : Set where
  field
    map₀  : {n : ℕ} → Cᴾ n → Cᴽ n
    map-u : map₀ (u P) ≈ u Q
    map-∧ : {i j : ℕ} (a : Cᴾ i) (b : Cᴾ j) →
            map₀ (_∧_ P a b) ≈ _∧_ Q (map₀ a) (map₀ b)

open GradedHomOver public

------------------------------------------------------------------------
-- ⟡lift-generic (comm-iso level) — THE GRADED INDEX-BRAIDING: the involutive index-swap
-- that witnesses commutativity of a grading op up to iso. blockSwap (⟡rig-6, over +, the
-- ⊎-swap via splitAt) and factorSwap (⟡rig-8, over *, the ×-swap via remQuot) are ONE
-- structure — an order-2 self-inverse family Fin(op m n) → Fin(op n m). The naive lift
-- (abstracting the decomposition target ⊎-vs-× as a field D : ℕ → ℕ → Set) would be Set₁,
-- the enemy; but the INVARIANT is Set₀ — a family of Fin-maps with an involution law, the
-- decomposition never held. The instance-specific L/R characterizations (which mention
-- inject+ / combine) stay in the fibres; the braiding-and-involution invariant lifts here.
------------------------------------------------------------------------

record GradedBraid (op : ℕ → ℕ → ℕ) : Set where
  field
    braid       : ∀ m n → Fin (op m n) → Fin (op n m)
    braid-invol : ∀ m n (k : Fin (op m n)) → braid n m (braid m n k) ≡ k

open GradedBraid public
