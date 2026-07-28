------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Idempotent  (was GF256 §A6 + §A9)
--
-- `reduce-mod-m p ≡ p` for an already-reduced byte `p : Vector 8`: the fold
-- IS Horner evaluation at the `xtime`-powers of the unit, so on a byte it is
-- the basis decomposition. Capstone `reduce-*-hom` (reduce is a ring hom in
-- the multiplicative slot) falls straight out of §Expand + idempotence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Idempotent where

open import Substrate.Algebra.F2 using (𝟙; ·-identityʳ)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_; 𝟎ⱽ; basis)
open import Substrate.Algebra.F2.Vector.Universal using (sum; basis-decomp)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Algebra.F2.GF256.Xtime using (xtime)
open import Substrate.Algebra.F2.GF256.Reduce using (reduce-mod-m; *ₛ-zeroʳ)
open import Substrate.Algebra.F2.GF256.Expand using (hsum; hsum-xtime; reduce-*P-expand)

one₈ : Vector 8
one₈ = 𝟙 ∷ 𝟎ⱽ

-- reduce p = hsum p 𝟙₈ (general): the fold IS Horner evaluation at xtime-powers of the unit.
reduce-eq-hsum : ∀ {n} (p : Polynomial n) → reduce-mod-m p ≡ hsum p one₈
reduce-eq-hsum []      = refl
reduce-eq-hsum (a ∷ q) =
  cong₂ _+ⱽ_ (cong₂ _∷_ (sym (·-identityʳ a)) (sym (*ₛ-zeroʳ a)))
             (trans (cong xtime (reduce-eq-hsum q)) (hsum-xtime q one₈))

xpow : ℕ → Vector 8 → Vector 8
xpow zero    r = r
xpow (suc k) r = xpow k (xtime r)

sum-cong : ∀ {n m} {f g : Fin n → Vector m} → (∀ i → f i ≡ g i) → sum f ≡ sum g
sum-cong {zero}  _  = refl
sum-cong {suc _} eq = cong₂ _+ⱽ_ (eq fzero) (sum-cong (λ i → eq (fsuc i)))

-- hsum is the basis-weighted sum (the fold = Σᵢ pᵢ ·ₛ xtimeⁱ r).
hsum-is-sum : ∀ {n} (p : Polynomial n) (r : Vector 8)
            → hsum p r ≡ sum (λ i → lookup p i *ₛ xpow (toℕ i) r)
hsum-is-sum []      r = refl
hsum-is-sum (a ∷ p) r = cong (λ z → (a *ₛ r) +ⱽ z) (hsum-is-sum p (xtime r))

-- the validated off-by-one, as a total Fin-8 fact (8 refl clauses).
hsum-one-basis : (i : Fin 8) → xpow (toℕ i) one₈ ≡ basis i
hsum-one-basis fzero = refl
hsum-one-basis (fsuc fzero) = refl
hsum-one-basis (fsuc (fsuc fzero)) = refl
hsum-one-basis (fsuc (fsuc (fsuc fzero))) = refl
hsum-one-basis (fsuc (fsuc (fsuc (fsuc fzero)))) = refl
hsum-one-basis (fsuc (fsuc (fsuc (fsuc (fsuc fzero))))) = refl
hsum-one-basis (fsuc (fsuc (fsuc (fsuc (fsuc (fsuc fzero)))))) = refl
hsum-one-basis (fsuc (fsuc (fsuc (fsuc (fsuc (fsuc (fsuc fzero))))))) = refl

hsum-𝟙₈-id : (p : Vector 8) → hsum p one₈ ≡ p
hsum-𝟙₈-id p =
  trans (hsum-is-sum p one₈)
  (trans (sum-cong (λ i → cong (lookup p i *ₛ_) (hsum-one-basis i)))
         (sym (basis-decomp p)))

-- A6: reducing an already-reduced byte is the identity.
reduce-idempotent : (p : Vector 8) → reduce-mod-m p ≡ p
reduce-idempotent p = trans (reduce-eq-hsum p) (hsum-𝟙₈-id p)

-- A9: reduce is a ring hom in the multiplicative slot — reducing a factor first
-- doesn't change the reduced product. Falls straight out of A4 + A6 (no keystone).
reduce-*-hom : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
             → reduce-mod-m (p *P q) ≡ reduce-mod-m (p *P reduce-mod-m q)
reduce-*-hom p q =
  trans (reduce-*P-expand p q)
        (sym (trans (reduce-*P-expand p (reduce-mod-m q))
                    (cong (hsum p) (reduce-idempotent (reduce-mod-m q)))))
