------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorCoherence
--
-- ⟡rig-13c-agda — a Laplaza rig-category coherence, FORMALIZED (guided by the numpy
-- discovery, scripts/rig_coherence.py, which verified all the diagrams commute).
--
-- The distributivity–braiding hexagon: the distributor δ commutes with the ⊕-braiding.
--
--   δ-⊕braid : blockSwap (a·b) (a·c) (δ a b c k)
--            ≡ δ a c b ((id ⊗map blockSwap b c) k)
--
--   (A⊗(B⊕C) --δ--> (A⊗B)⊕(A⊗C) --σ--> (A⊗C)⊕(A⊗B)  =
--    A⊗(B⊕C) --id⊗σ--> A⊗(C⊕B) --δ--> (A⊗C)⊕(A⊗B))
--
-- Proof (the numpy-confirmed toℕ/lookup pattern): decompose k = combine i k' (subst over
-- combine-remQuot so splitAt-view cases the VARIABLE k'); in the b-part both sides reduce
-- via δ-inject / blockSwap-L / ⊗map-combine / δ-raise to raise (a·c) (combine i j), and in
-- the c-part to inject+ (a·b) (combine i l). Also builds the functorial ⊗-on-morphisms
-- layer (_⊗map_), the ⊗ analog of OrientationHexagon's ⊕map.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorCoherence where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.WitnessTower.Wedge.OrientationSumComm
  using (blockSwap; blockSwap-L; blockSwap-R)
open import Substrate.WitnessTower.Wedge.OrientationDistributor using (δ; δ-inject; δ-raise)

------------------------------------------------------------------------
-- 1. The functorial ⊗ on MORPHISMS (the ⊗ analog of ⊕map): act by f on the first factor,
--    g on the second, through combine/remQuot.
------------------------------------------------------------------------

_⊗map_ : ∀ {m n m' n'} → (Fin m → Fin m') → (Fin n → Fin n') →
         Fin (m * n) → Fin (m' * n')
(_⊗map_ {m} {n} {m'} {n'} f g) x =
  combine (f (proj₁ (remQuot {m} n x))) (g (proj₂ (remQuot {m} n x)))

⊗map-combine : ∀ {m n m' n'} (f : Fin m → Fin m') (g : Fin n → Fin n') (i : Fin m) (j : Fin n) →
               (f ⊗map g) (combine i j) ≡ combine (f i) (g j)
⊗map-combine f g i j = cong (λ pr → combine (f (proj₁ pr)) (g (proj₂ pr))) (remQuot-combine i j)

------------------------------------------------------------------------
-- 2. THE DISTRIBUTIVITY–BRAIDING HEXAGON. δ commutes with the ⊕-braiding.
------------------------------------------------------------------------

δ-⊕braid : ∀ a b c (k : Fin (a * (b + c))) →
           blockSwap (a * b) (a * c) (δ a b c k)
             ≡ δ a c b ((_⊗map_ {a} {b + c} {a} {c + b} (λ x → x) (blockSwap b c)) k)
δ-⊕braid a b c k =
  subst (λ z → blockSwap (a * b) (a * c) (δ a b c z)
                 ≡ δ a c b ((_⊗map_ {a} {b + c} {a} {c + b} (λ x → x) (blockSwap b c)) z))
        (combine-remQuot a (b + c) k)
        (aux (proj₁ (remQuot {a} (b + c) k)) (proj₂ (remQuot {a} (b + c) k)))
  where
  aux : (i : Fin a) (k' : Fin (b + c)) →
        blockSwap (a * b) (a * c) (δ a b c (combine i k'))
          ≡ δ a c b ((_⊗map_ {a} {b + c} {a} {c + b} (λ x → x) (blockSwap b c)) (combine i k'))
  aux i k' with splitAt-view b {c} k'
  ... | fromₗ j =
    trans (trans (cong (blockSwap (a * b) (a * c)) (δ-inject a b c i j))
                 (blockSwap-L (a * b) (a * c) (combine i j)))
      (sym (trans (cong (δ a c b)
                        (trans (⊗map-combine (λ x → x) (blockSwap b c) i (inject+ c j))
                               (cong (combine i) (blockSwap-L b c j))))
                  (δ-raise a c b i j)))
  ... | fromᵣ l =
    trans (trans (cong (blockSwap (a * b) (a * c)) (δ-raise a b c i l))
                 (blockSwap-R (a * b) (a * c) (combine i l)))
      (sym (trans (cong (δ a c b)
                        (trans (⊗map-combine (λ x → x) (blockSwap b c) i (raise b l))
                               (cong (combine i) (blockSwap-R b c l))))
                  (δ-inject a c b i l)))
