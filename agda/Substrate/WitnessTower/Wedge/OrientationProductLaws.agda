------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProductLaws
--
-- ⟡rig-8 assoc — the ⊗ product is associative (up to the *-assoc grade transport),
-- lifting Foundation's combine-assoc (Fin.Combine.Assoc) to the tabulated Perm product.
--
--   ⊗-assoc : subst Perm (*-assoc m n p) ((σ ⊗ τ) ⊗ υ) ≡ σ ⊗ (τ ⊗ υ)
--
-- Route: the clean characterization ⊗-combine (lookup (σ⊗τ) (combine i j) = combine (σ·i)
-- (τ·j)) turns both sides, at a combine-decomposed index, into nested combines; then
-- combine-assoc (the Fin associator, proven arithmetically via toℕ) closes it, with
-- lookup-subst-Perm handling the grade transport under lookup.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProductLaws where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.Combine.Assoc using (combine-assoc)
open import Substrate.Foundation.Vec using (Vec; lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_)

------------------------------------------------------------------------
-- 1. THE CHARACTERIZATION: lookup of a product at a combine index is the combine of
--    the looked-up factors. (lookup∘tabulate, then remQuot-combine collapses remQuot.)
------------------------------------------------------------------------

⊗-combine : ∀ {m n} (σ : Perm m) (τ : Perm n) (i : Fin m) (j : Fin n) →
            lookup (σ ⊗ τ) (combine i j) ≡ combine (lookup σ i) (lookup τ j)
⊗-combine {m} {n} σ τ i j =
  trans (lookup∘tabulate _ (combine i j))
        (cong (λ pr → combine (lookup σ (proj₁ pr)) (lookup τ (proj₂ pr)))
              (remQuot-combine i j))

------------------------------------------------------------------------
-- 2. lookup under a grade-subst (eq-induction): the transport moves index and value.
------------------------------------------------------------------------

lookup-subst-Perm : ∀ {k k'} (eq : k ≡ k') (v : Perm k) (i : Fin k') →
                    lookup (subst Perm eq v) i ≡ subst Fin eq (lookup v (subst Fin (sym eq) i))
lookup-subst-Perm refl v i = refl

-- turn a subst-equality into its sym form (eq-induction).
subst-to-sym : ∀ {k k'} (eq : k ≡ k') {x : Fin k} {y : Fin k'} →
               subst Fin eq x ≡ y → x ≡ subst Fin (sym eq) y
subst-to-sym refl h = h

------------------------------------------------------------------------
-- 3. ⊗-ASSOCIATIVITY. lookup-ext pointwise: decompose the index l as combine a
--    (combine b c) via combine-remQuot; both sides become nested combines through
--    ⊗-combine; combine-assoc (the Fin associator) closes the transport.
------------------------------------------------------------------------

⊗-assoc : ∀ {m n p} (σ : Perm m) (τ : Perm n) (υ : Perm p) →
          subst Perm (*-assoc m n p) ((σ ⊗ τ) ⊗ υ) ≡ σ ⊗ (τ ⊗ υ)
⊗-assoc {m} {n} {p} σ τ υ = lookup-ext _ _ pointwise
  where
  pointwise : (l : Fin (m * (n * p))) →
              lookup (subst Perm (*-assoc m n p) ((σ ⊗ τ) ⊗ υ)) l ≡ lookup (σ ⊗ (τ ⊗ υ)) l
  pointwise l =
    trans (cong (lookup (subst Perm (*-assoc m n p) ((σ ⊗ τ) ⊗ υ))) (sym l-decomp))
          (trans lhs-at
                 (trans (sym rhs-at)
                        (cong (lookup (σ ⊗ (τ ⊗ υ))) l-decomp)))
    where
    a = proj₁ (remQuot {m} (n * p) l)
    r = proj₂ (remQuot {m} (n * p) l)
    b = proj₁ (remQuot {n} p r)
    c = proj₂ (remQuot {n} p r)

    l-decomp : combine a (combine b c) ≡ l
    l-decomp = trans (cong (combine a) (combine-remQuot n p r)) (combine-remQuot m (n * p) l)

    sym-eq : subst Fin (sym (*-assoc m n p)) (combine a (combine b c)) ≡ combine (combine a b) c
    sym-eq = sym (subst-to-sym (*-assoc m n p) (combine-assoc a b c))

    INNER : lookup ((σ ⊗ τ) ⊗ υ) (subst Fin (sym (*-assoc m n p)) (combine a (combine b c)))
            ≡ combine (combine (lookup σ a) (lookup τ b)) (lookup υ c)
    INNER = trans (cong (lookup ((σ ⊗ τ) ⊗ υ)) sym-eq)
                  (trans (⊗-combine (σ ⊗ τ) υ (combine a b) c)
                         (cong (λ z → combine z (lookup υ c)) (⊗-combine σ τ a b)))

    lhs-at : lookup (subst Perm (*-assoc m n p) ((σ ⊗ τ) ⊗ υ)) (combine a (combine b c))
             ≡ combine (lookup σ a) (combine (lookup τ b) (lookup υ c))
    lhs-at = trans (lookup-subst-Perm (*-assoc m n p) ((σ ⊗ τ) ⊗ υ) (combine a (combine b c)))
                   (trans (cong (subst Fin (*-assoc m n p)) INNER)
                          (combine-assoc (lookup σ a) (lookup τ b) (lookup υ c)))

    rhs-at : lookup (σ ⊗ (τ ⊗ υ)) (combine a (combine b c))
             ≡ combine (lookup σ a) (combine (lookup τ b) (lookup υ c))
    rhs-at = trans (⊗-combine σ (τ ⊗ υ) a (combine b c))
                   (cong (combine (lookup σ a)) (⊗-combine τ υ b c))
