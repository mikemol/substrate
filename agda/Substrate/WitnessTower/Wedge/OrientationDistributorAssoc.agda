------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationDistributorAssoc
--
-- ⟡rig-13c-assoc — the δ vs ⊕-ASSOCIATIVITY coherence (numpy-verified, Laplaza-δ-⊕assoc),
-- FORMALIZED per-block. Distributing A⊗((B⊕C)⊕D) two ways:
--   p1 = (δ_{A,B,C} ⊕ id) ∘ δ_{A,B⊕C,D}      p2 = (id ⊕ δ_{A,C,D}) ∘ δ_{A,B,C⊕D}
-- The two paths land in different grades ((a·b+a·c)+a·d vs a·b+(a·c+a·d)) — the naive
-- statement is subst-heavy. But the CONTENT is per-block: each of B,C,D routes to the same
-- output block by both paths. Stated per-block (the index given in each association form
-- directly), the +-assoc recast DISAPPEARS — each is a clean toℕ chain (D needs one +-assoc).
--
--   δ-⊕assoc-B/C/D : toℕ (p1 <index in (b+c)+d form>) ≡ toℕ (p2 <index in b+(c+d) form>)
--
-- (The lesson: the difficulty was the statement FORM, not the content — cf.
-- feedback_probe_wall_try_alternate_encoding.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationDistributorAssoc where

open import Substrate.Foundation.Nat using (ℕ; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc)
open import Substrate.Foundation.Fin using (Fin; toℕ)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.Combine.Assoc using (toℕ-inject+; toℕ-raise)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Wedge.OrientationHexagon using (_⊕map_; ⊕map-inject; ⊕map-raise)
open import Substrate.WitnessTower.Wedge.OrientationDistributor using (δ; δ-inject; δ-raise)

-- the two distribution paths, on a·((b+c)+d) [p1] and a·(b+(c+d)) [p2]:
p1 : ∀ a b c d → Fin (a * ((b + c) + d)) → Fin ((a * b + a * c) + a * d)
p1 a b c d x = (δ a b c ⊕map (λ y → y)) (δ a (b + c) d x)

p2 : ∀ a b c d → Fin (a * (b + (c + d))) → Fin (a * b + (a * c + a * d))
p2 a b c d x = ((λ y → y) ⊕map δ a c d) (δ a b (c + d) x)

------------------------------------------------------------------------
-- Per-block coherence: both paths route each block to the same value (toℕ).
------------------------------------------------------------------------

-- B-block: (b+c)+d form = inject+ d (inject+ c j) ;  b+(c+d) form = inject+ (c+d) j.
δ-⊕assoc-B : ∀ a b c d (i : Fin a) (j : Fin b) →
             toℕ (p1 a b c d (combine i (inject+ d (inject+ c j))))
               ≡ toℕ (p2 a b c d (combine i (inject+ (c + d) j)))
δ-⊕assoc-B a b c d i j =
  trans (trans (cong toℕ (trans (cong (δ a b c ⊕map (λ x → x)) (δ-inject a (b + c) d i (inject+ c j)))
                                (trans (⊕map-inject (δ a b c) (λ x → x) (combine i (inject+ c j)))
                                       (cong (inject+ (a * d)) (δ-inject a b c i j)))))
               (trans (toℕ-inject+ (a * d) (inject+ (a * c) (combine i j)))
                      (toℕ-inject+ (a * c) (combine i j))))
        (sym (trans (cong toℕ (trans (cong ((λ x → x) ⊕map δ a c d) (δ-inject a b (c + d) i j))
                                     (⊕map-inject (λ x → x) (δ a c d) (combine i j))))
                    (toℕ-inject+ (a * c + a * d) (combine i j))))

-- C-block: (b+c)+d = inject+ d (raise b l) ;  b+(c+d) = raise b (inject+ d l).
δ-⊕assoc-C : ∀ a b c d (i : Fin a) (l : Fin c) →
             toℕ (p1 a b c d (combine i (inject+ d (raise b l))))
               ≡ toℕ (p2 a b c d (combine i (raise b (inject+ d l))))
δ-⊕assoc-C a b c d i l =
  trans (trans (cong toℕ (trans (cong (δ a b c ⊕map (λ x → x)) (δ-inject a (b + c) d i (raise b l)))
                                (trans (⊕map-inject (δ a b c) (λ x → x) (combine i (raise b l)))
                                       (cong (inject+ (a * d)) (δ-raise a b c i l)))))
               (trans (toℕ-inject+ (a * d) (raise (a * b) (combine i l)))
                      (toℕ-raise (a * b) (combine i l))))
        (sym (trans (cong toℕ (trans (cong ((λ x → x) ⊕map δ a c d) (δ-raise a b (c + d) i (inject+ d l)))
                                     (trans (⊕map-raise (λ x → x) (δ a c d) (combine i (inject+ d l)))
                                            (cong (raise (a * b)) (δ-inject a c d i l)))))
                    (trans (toℕ-raise (a * b) (inject+ (a * d) (combine i l)))
                           (cong (a * b +_) (toℕ-inject+ (a * d) (combine i l))))))

-- D-block: (b+c)+d = raise (b+c) m ;  b+(c+d) = raise b (raise c m).  (one +-assoc step)
δ-⊕assoc-D : ∀ a b c d (i : Fin a) (m : Fin d) →
             toℕ (p1 a b c d (combine i (raise (b + c) m)))
               ≡ toℕ (p2 a b c d (combine i (raise b (raise c m))))
δ-⊕assoc-D a b c d i m =
  trans (trans (cong toℕ (trans (cong (δ a b c ⊕map (λ x → x)) (δ-raise a (b + c) d i m))
                                (⊕map-raise (δ a b c) (λ x → x) (combine i m))))
               (toℕ-raise (a * b + a * c) (combine i m)))
        (trans (+-assoc (a * b) (a * c) (toℕ (combine i m)))
        (sym (trans (cong toℕ (trans (cong ((λ x → x) ⊕map δ a c d) (δ-raise a b (c + d) i (raise c m)))
                                     (trans (⊕map-raise (λ x → x) (δ a c d) (combine i (raise c m)))
                                            (cong (raise (a * b)) (δ-raise a c d i m)))))
                    (trans (toℕ-raise (a * b) (raise (a * c) (combine i m)))
                           (cong (a * b +_) (toℕ-raise (a * c) (combine i m)))))))
