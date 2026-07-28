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
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Fin.Combine.RemQuotInverse using (remQuot-combine)
open import Substrate.Foundation.Fin.Combine.CombineRemQuotInverse using (combine-remQuot)
open import Substrate.Foundation.Fin.Combine.Assoc using (toℕ-inject+; toℕ-combine)
open import Substrate.Foundation.Fin.SplitAt using (splitAt)
open import Substrate.Foundation.Fin.SplitAt.InjectIdentity using (splitAt-inject)
open import Substrate.Foundation.Fin.SplitAt.RaiseIdentity using (splitAt-raise)
open import Substrate.Foundation.Fin.SplitAt.View using (splitAt-view; fromₗ; fromᵣ)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Product using (_,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.WitnessTower.Wedge.OrientationSumComm
  using (blockSwap; blockSwap-L; blockSwap-R)
open import Substrate.WitnessTower.Wedge.OrientationProductComm
  using (factorSwap; factorSwap-combine)
open import Substrate.WitnessTower.Wedge.OrientationHexagon using (_⊕map_; ⊕map-inject; ⊕map-raise)
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

------------------------------------------------------------------------
-- 3. δ over the ⊕-unit 0: δ a b 0 is value-preserving (the ⊕-unit distributor coherence).
--    (Every index is in the b-part — the 0-part is empty; δ-inject then toℕ, one b+0=b step.)
------------------------------------------------------------------------

δ-⊕unit0 : ∀ a b (k : Fin (a * (b + 0))) → toℕ (δ a b 0 k) ≡ toℕ k
δ-⊕unit0 a b k =
  subst (λ z → toℕ (δ a b 0 z) ≡ toℕ z) (combine-remQuot a (b + 0) k)
        (aux (proj₁ (remQuot {a} (b + 0) k)) (proj₂ (remQuot {a} (b + 0) k)))
  where
  aux : (i : Fin a) (k' : Fin (b + 0)) → toℕ (δ a b 0 (combine i k')) ≡ toℕ (combine i k')
  aux i k' with splitAt-view b {0} k'
  ... | fromₗ j =
    trans (trans (cong toℕ (δ-inject a b 0 i j))
                 (trans (toℕ-inject+ (a * 0) (combine i j)) (toℕ-combine i j)))
          (trans (cong (λ z → toℕ i * z + toℕ j) (sym (+-identityʳ b)))
                 (sym (trans (toℕ-combine i (inject+ 0 j))
                             (cong (toℕ i * (b + 0) +_) (toℕ-inject+ 0 j)))))
  ... | fromᵣ ()

------------------------------------------------------------------------
-- 4. The RIGHT distributor δR, and the ⊗-braiding distributor coherence: the left and
--    right distributors are conjugate by the ⊗-braiding (factorSwap).
------------------------------------------------------------------------

δR : ∀ b c a → Fin ((b + c) * a) → Fin (b * a + c * a)
δR b c a k with remQuot {b + c} a k
... | (k1 , i) with splitAt b {c} k1
...   | inj₁ j = inject+ (c * a) (combine j i)
...   | inj₂ l = raise (b * a) (combine l i)

δR-inject : ∀ b c a (j : Fin b) (i : Fin a) →
             δR b c a (combine (inject+ c j) i) ≡ inject+ (c * a) (combine j i)
δR-inject b c a j i
  rewrite remQuot-combine {b + c} {a} (inject+ c j) i | splitAt-inject b {c} j = refl

δR-raise : ∀ b c a (l : Fin c) (i : Fin a) →
            δR b c a (combine (raise b l) i) ≡ raise (b * a) (combine l i)
δR-raise b c a l i
  rewrite remQuot-combine {b + c} {a} (raise b l) i | splitAt-raise b {c} l = refl

δ-⊗braid : ∀ a b c (k : Fin ((b + c) * a)) →
           δR b c a k
             ≡ (factorSwap a b ⊕map factorSwap a c) (δ a b c (factorSwap (b + c) a k))
δ-⊗braid a b c k =
  subst (λ z → δR b c a z
                 ≡ (factorSwap a b ⊕map factorSwap a c) (δ a b c (factorSwap (b + c) a z)))
        (combine-remQuot (b + c) a k)
        (aux (proj₁ (remQuot {b + c} a k)) (proj₂ (remQuot {b + c} a k)))
  where
  aux : (k1 : Fin (b + c)) (i : Fin a) →
        δR b c a (combine k1 i)
          ≡ (factorSwap a b ⊕map factorSwap a c) (δ a b c (factorSwap (b + c) a (combine k1 i)))
  aux k1 i with splitAt-view b {c} k1
  ... | fromₗ j =
    trans (δR-inject b c a j i)
      (sym (trans (cong (λ z → (factorSwap a b ⊕map factorSwap a c) (δ a b c z))
                        (factorSwap-combine (inject+ c j) i))
           (trans (cong (factorSwap a b ⊕map factorSwap a c) (δ-inject a b c i j))
           (trans (⊕map-inject (factorSwap a b) (factorSwap a c) (combine i j))
                  (cong (inject+ (c * a)) (factorSwap-combine i j))))))
  ... | fromᵣ l =
    trans (δR-raise b c a l i)
      (sym (trans (cong (λ z → (factorSwap a b ⊕map factorSwap a c) (δ a b c z))
                        (factorSwap-combine (raise b l) i))
           (trans (cong (factorSwap a b ⊕map factorSwap a c) (δ-raise a b c i l))
           (trans (⊕map-raise (factorSwap a b) (factorSwap a c) (combine i l))
                  (cong (raise (b * a)) (factorSwap-combine i l))))))
