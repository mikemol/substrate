------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Coboundary
--
-- ⊙.dd — the GENERIC d² = 0: δ³(δ²φ) ≡ false for EVERY 2-cochain φ, making the
-- pentagon (⊙.pentagon) unconditional (`dε` closed because it is a coboundary,
-- for all cochains, not just verified at the 𝕆 witnesses).
--
-- δ³(δ²φ)(a,b,c,d) expands to a XOR of 20 φ-values; each of the 10 distinct values
-- occurs exactly TWICE (the simplicial face-pairing), so over F₂ it cancels to 0.
-- No AC solver, so: a small XOR-parity framework (`foldrB` = ⊕ of a list, a ++
-- homomorphism) flattens the tree to a list, then `remove-head-pair` cancels the
-- 10 matched pairs one at a time. The two diagonal faces are aligned first by
-- ⊕-assoc (`(a⊕b)⊕c = a⊕(b⊕c)`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Coboundary where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)
open import Substrate.Foundation.Bool using (Bool; false; _xor_)
open import Substrate.Foundation.Bool.Properties
  using (xor-assoc; xor-comm; xor-same; xor-identityˡ; xor-identityʳ)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Vec using (Vec; zipWith)
open import Substrate.Algebra.CayleyDickson.Cocycle using (δ²; δ³; ⊕-assoc)

------------------------------------------------------------------------
-- 1. The XOR-parity framework.
------------------------------------------------------------------------

foldrB : List Bool → Bool
foldrB []       = false
foldrB (x ∷ xs) = x xor foldrB xs

foldrB-++ : (xs ys : List Bool) → foldrB (xs ++ ys) ≡ foldrB xs xor foldrB ys
foldrB-++ []       ys = sym (xor-identityˡ (foldrB ys))
foldrB-++ (x ∷ xs) ys = trans (cong (x xor_) (foldrB-++ xs ys))
                              (sym (xor-assoc x (foldrB xs) (foldrB ys)))

xor-cancelˡ : (a b : Bool) → a xor (a xor b) ≡ b
xor-cancelˡ a b = trans (sym (xor-assoc a a b))
                        (trans (cong (_xor b) (xor-same a)) (xor-identityˡ b))

xor-swap : (a b c : Bool) → a xor (b xor c) ≡ b xor (a xor c)
xor-swap a b c = trans (sym (xor-assoc a b c))
                       (trans (cong (_xor c) (xor-comm a b)) (xor-assoc b a c))

-- a value heading the list cancels with its later occurrence.
remove-head-pair : (x : Bool) (bs cs : List Bool) →
                   foldrB (x ∷ (bs ++ x ∷ cs)) ≡ foldrB (bs ++ cs)
remove-head-pair x bs cs =
  trans (cong (x xor_) (foldrB-++ bs (x ∷ cs)))
  (trans (cong (x xor_) (xor-swap (foldrB bs) x (foldrB cs)))
  (trans (xor-cancelˡ x (foldrB bs xor foldrB cs))
         (sym (foldrB-++ bs cs))))

-- flatten a balanced 4-leaf XOR into the right-nested list form.
flat4 : (a b c d : Bool) → (a xor b) xor (c xor d) ≡ foldrB (a ∷ b ∷ c ∷ d ∷ [])
flat4 a b c d = trans (xor-assoc a b (c xor d))
  (cong (a xor_) (cong (b xor_) (cong (c xor_) (sym (xor-identityʳ d)))))

------------------------------------------------------------------------
-- 2. The 10-pair cancellation, as a Bool tautology over the 10 distinct values.
--    (Subscripts follow the face expansion; each vᵢ appears exactly twice.)
------------------------------------------------------------------------

dd-bool : (v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 : Bool) →
  (((((v1 xor v2) xor (v3 xor v4)) xor ((v5 xor v6) xor (v3 xor v7)))
     xor (((v8 xor v6) xor (v2 xor v9)) xor ((v10 xor v7) xor (v4 xor v9))))
   xor ((v10 xor v5) xor (v1 xor v8))) ≡ false
dd-bool v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 =
  trans
    -- flatten: each balanced face → its 4-leaf list, then collapse ++.
    (trans (cong₂ _xor_ (cong₂ _xor_ (cong₂ _xor_ (flat4 v1 v2 v3 v4) (flat4 v5 v6 v3 v7))
                                     (cong₂ _xor_ (flat4 v8 v6 v2 v9) (flat4 v10 v7 v4 v9)))
                        (flat4 v10 v5 v1 v8))
    (trans (cong₂ _xor_ (cong₂ _xor_ (sym (foldrB-++ (v1 ∷ v2 ∷ v3 ∷ v4 ∷ []) (v5 ∷ v6 ∷ v3 ∷ v7 ∷ [])))
                                     (sym (foldrB-++ (v8 ∷ v6 ∷ v2 ∷ v9 ∷ []) (v10 ∷ v7 ∷ v4 ∷ v9 ∷ []))))
                        refl)
    (trans (cong (_xor foldrB (v10 ∷ v5 ∷ v1 ∷ v8 ∷ []))
                 (sym (foldrB-++ (v1 ∷ v2 ∷ v3 ∷ v4 ∷ v5 ∷ v6 ∷ v3 ∷ v7 ∷ [])
                                 (v8 ∷ v6 ∷ v2 ∷ v9 ∷ v10 ∷ v7 ∷ v4 ∷ v9 ∷ []))))
           (sym (foldrB-++ (v1 ∷ v2 ∷ v3 ∷ v4 ∷ v5 ∷ v6 ∷ v3 ∷ v7 ∷ v8 ∷ v6 ∷ v2 ∷ v9 ∷ v10 ∷ v7 ∷ v4 ∷ v9 ∷ [])
                           (v10 ∷ v5 ∷ v1 ∷ v8 ∷ []))))))
    -- cancel the 10 pairs, head-first.
    (trans (remove-head-pair v1 (v2 ∷ v3 ∷ v4 ∷ v5 ∷ v6 ∷ v3 ∷ v7 ∷ v8 ∷ v6 ∷ v2 ∷ v9 ∷ v10 ∷ v7 ∷ v4 ∷ v9 ∷ v10 ∷ v5 ∷ []) (v8 ∷ []))
    (trans (remove-head-pair v2 (v3 ∷ v4 ∷ v5 ∷ v6 ∷ v3 ∷ v7 ∷ v8 ∷ v6 ∷ []) (v9 ∷ v10 ∷ v7 ∷ v4 ∷ v9 ∷ v10 ∷ v5 ∷ v8 ∷ []))
    (trans (remove-head-pair v3 (v4 ∷ v5 ∷ v6 ∷ []) (v7 ∷ v8 ∷ v6 ∷ v9 ∷ v10 ∷ v7 ∷ v4 ∷ v9 ∷ v10 ∷ v5 ∷ v8 ∷ []))
    (trans (remove-head-pair v4 (v5 ∷ v6 ∷ v7 ∷ v8 ∷ v6 ∷ v9 ∷ v10 ∷ v7 ∷ []) (v9 ∷ v10 ∷ v5 ∷ v8 ∷ []))
    (trans (remove-head-pair v5 (v6 ∷ v7 ∷ v8 ∷ v6 ∷ v9 ∷ v10 ∷ v7 ∷ v9 ∷ v10 ∷ []) (v8 ∷ []))
    (trans (remove-head-pair v6 (v7 ∷ v8 ∷ []) (v9 ∷ v10 ∷ v7 ∷ v9 ∷ v10 ∷ v8 ∷ []))
    (trans (remove-head-pair v7 (v8 ∷ v9 ∷ v10 ∷ []) (v9 ∷ v10 ∷ v8 ∷ []))
    (trans (remove-head-pair v8 (v9 ∷ v10 ∷ v9 ∷ v10 ∷ []) [])
    (trans (remove-head-pair v9 (v10 ∷ []) (v10 ∷ []))
           (remove-head-pair v10 [] []))))))))))

------------------------------------------------------------------------
-- 3. d² = 0 : δ³(δ²φ) ≡ false for every 2-cochain φ, every a b c d.
--    Align the two diagonal faces by ⊕-assoc, then apply dd-bool to the 10
--    surviving φ-values.
------------------------------------------------------------------------

d²-zero : (n : ℕ) (φ : Vec Bool n → Vec Bool n → Bool) (a b c d : Vec Bool n) →
          δ³ (δ² φ) a b c d ≡ false
d²-zero n φ a b c d
  rewrite ⊕-assoc n a b c | ⊕-assoc n b c d =
  dd-bool (φ b c) (φ (zipWith _xor_ b c) d) (φ c d) (φ b (zipWith _xor_ c d))
          (φ (zipWith _xor_ a b) c) (φ (zipWith _xor_ a (zipWith _xor_ b c)) d)
          (φ (zipWith _xor_ a b) (zipWith _xor_ c d)) (φ a (zipWith _xor_ b c))
          (φ a (zipWith _xor_ b (zipWith _xor_ c d))) (φ a b)
