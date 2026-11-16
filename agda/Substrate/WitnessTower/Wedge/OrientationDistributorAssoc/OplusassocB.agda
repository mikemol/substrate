------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OplusassocB
--
-- Defines: δ-⊕assoc-B
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationDistributorAssoc; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.OplusassocB where

open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Inject
open import Substrate.Foundation.Fin.Combine
open import Substrate.Foundation.Fin.Combine.Assoc.ToNatInjectPlus
open import Substrate.WitnessTower.Wedge.OrientationHexagon
open import Substrate.WitnessTower.Wedge.OrientationDistributor
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P1
open import Substrate.WitnessTower.Wedge.OrientationDistributorAssoc.P2



------------------------------------------------------------------------
-- Per-block coherence: both paths route each block to the same value (toℕ).
------------------------------------------------------------------------

-- B-block: (b+c)+d form = inject+ d (inject+ c j) ;  b+(c+d) form = inject+ (c+d) j.
δ-⊕assoc-B : ∀ a b c d (i : Fin a) (j : Fin b) →
             toℕ (p1 a b c d (combine i (inject+ d (inject+ c j))))
               ≡ toℕ (p2 a b c d (combine i (inject+ (c ℕ+ d) j)))
δ-⊕assoc-B a b c d i j =
  trans (trans (cong toℕ (trans (cong (δ a b c ⊕map (λ x → x)) (δ-inject a (b ℕ+ c) d i (inject+ c j)))
                                (trans (⊕map-inject (δ a b c) (λ x → x) (combine i (inject+ c j)))
                                       (cong (inject+ (a * d)) (δ-inject a b c i j)))))
               (trans (toℕ-inject+ (a * d) (inject+ (a * c) (combine i j)))
                      (toℕ-inject+ (a * c) (combine i j))))
        (sym (trans (cong toℕ (trans (cong ((λ x → x) ⊕map δ a c d) (δ-inject a b (c ℕ+ d) i j))
                                     (⊕map-inject (λ x → x) (δ a c d) (combine i j))))
                    (toℕ-inject+ (a * c ℕ+ a * d) (combine i j))))
