------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationBifunctor
--
-- ⟡rig-UP-map — the ⊕/⊗ FUNCTORIAL index-maps (_⊕map_, _⊗map_) as instances of ONE
-- GradedBifunctor. This CORRECTS the earlier "the map level does not lift" floor claim:
-- the FUNCTORIALITY laws (gmap id id = id, gmap (f∘f')(g∘g') = gmap f g ∘ gmap f' g') are
-- DECOMPOSITION-FREE statements — only their PROOFS use the ⊎/× decomposition (splitAt-view
-- / combine-remQuot). So the bifunctor-on-morphisms DOES lift to a Set₀ invariant; it just
-- needed the laws PROVEN (a build, not a pure lift — the char lemmas ⊕map-inject/raise,
-- ⊗map-combine already existed, the id/∘ laws did not).
--
--   ⊕-bifunctor : GradedBifunctor _+_    (the ⊎-split bifunctor, splitAt/[inject+,raise])
--   ⊗-bifunctor : GradedBifunctor _*_    (the ×-split bifunctor, remQuot/combine)
--
-- With this the arc's four decomposition-free invariants are complete: GradedProductOver
-- (product), GradedHomOver (hom), GradedBraid (index-swap), GradedBraidNatural (σ-naturality),
-- GradedBifunctor (product-on-morphisms) — each with both ⊕/⊗ fibres, uniform over the op.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationBifunctor where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Wedge.OrientationHexagon
  using (_⊕map_; ⊕map-inject; ⊕map-raise)
open import Substrate.WitnessTower.Wedge.OrientationDistributorCoherence
  using (_⊗map_; ⊗map-combine)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal using (GradedBifunctor)

------------------------------------------------------------------------
-- 1. ⊕map functoriality (over +, the ⊎-split). id/∘ by cases on which block x is in
--    (splitAt-view), each closed by the block-characterization ⊕map-inject / ⊕map-raise.
------------------------------------------------------------------------

⊕map-id : ∀ {m n} (x : Fin (m + n)) → _⊕map_ {m} {n} {m} {n} (λ i → i) (λ j → j) x ≡ x
⊕map-id {m} {n} x with splitAt-view m x
... | fromₗ j = ⊕map-inject {m} {n} {m} {n} (λ i → i) (λ j → j) j
... | fromᵣ i = ⊕map-raise  {m} {n} {m} {n} (λ i → i) (λ j → j) i

⊕map-∘ : ∀ {m n m' n' m'' n''}
         (f : Fin m' → Fin m'') (f' : Fin m → Fin m')
         (g : Fin n' → Fin n'') (g' : Fin n → Fin n') (x : Fin (m + n)) →
         _⊕map_ {m} {n} {m''} {n''} (λ i → f (f' i)) (λ j → g (g' j)) x
           ≡ (f ⊕map g) ((f' ⊕map g') x)
⊕map-∘ {m} {n} {m'} {n'} {m''} {n''} f f' g g' x with splitAt-view m x
... | fromₗ j = trans (⊕map-inject {m} {n} {m''} {n''} (λ i → f (f' i)) (λ j → g (g' j)) j)
                      (sym (trans (cong (f ⊕map g) (⊕map-inject {m} {n} {m'} {n'} f' g' j))
                                  (⊕map-inject {m'} {n'} {m''} {n''} f g (f' j))))
... | fromᵣ i = trans (⊕map-raise {m} {n} {m''} {n''} (λ i → f (f' i)) (λ j → g (g' j)) i)
                      (sym (trans (cong (f ⊕map g) (⊕map-raise {m} {n} {m'} {n'} f' g' i))
                                  (⊕map-raise {m'} {n'} {m''} {n''} f g (g' i))))

------------------------------------------------------------------------
-- 2. ⊗map functoriality (over *, the ×-split). _⊗map_ is DEFINED as the combine of the
--    remQuot-decomposed factors, so id reduces to combine-remQuot and ∘ to ⊗map-combine —
--    no case split needed (the decomposition is definitional in ⊗map).
------------------------------------------------------------------------

⊗map-id : ∀ {m n} (x : Fin (m * n)) → _⊗map_ {m} {n} {m} {n} (λ i → i) (λ j → j) x ≡ x
⊗map-id {m} {n} x = combine-remQuot m n x

⊗map-∘ : ∀ {m n m' n' m'' n''}
         (f : Fin m' → Fin m'') (f' : Fin m → Fin m')
         (g : Fin n' → Fin n'') (g' : Fin n → Fin n') (x : Fin (m * n)) →
         _⊗map_ {m} {n} {m''} {n''} (λ i → f (f' i)) (λ j → g (g' j)) x
           ≡ (f ⊗map g) ((f' ⊗map g') x)
⊗map-∘ {m} {n} {m'} {n'} {m''} {n''} f f' g g' x =
  sym (⊗map-combine {m'} {n'} {m''} {n''} f g
        (f' (proj₁ (remQuot {m} n x))) (g' (proj₂ (remQuot {m} n x))))

------------------------------------------------------------------------
-- 3. THE INSTANCES: both functorial index-maps package as GradedBifunctor.
------------------------------------------------------------------------

⊕-bifunctor : GradedBifunctor _+_
⊕-bifunctor = record
  { gmap    = λ {m} {n} {m'} {n'} f g → _⊕map_ {m} {n} {m'} {n'} f g
  ; gmap-id = λ {m} {n} k → ⊕map-id {m} {n} k
  ; gmap-∘  = λ {m} {n} {m'} {n'} {m''} {n''} f f' g g' k →
                ⊕map-∘ {m} {n} {m'} {n'} {m''} {n''} f f' g g' k
  }

⊗-bifunctor : GradedBifunctor _*_
⊗-bifunctor = record
  { gmap    = λ {m} {n} {m'} {n'} f g → _⊗map_ {m} {n} {m'} {n'} f g
  ; gmap-id = λ {m} {n} k → ⊗map-id {m} {n} k
  ; gmap-∘  = λ {m} {n} {m'} {n'} {m''} {n''} f f' g g' k →
                ⊗map-∘ {m} {n} {m'} {n'} {m''} {n''} f f' g g' k
  }
