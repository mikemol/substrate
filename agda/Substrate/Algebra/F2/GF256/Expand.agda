------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Expand  (was GF256 §A4)
--
-- The multiplicative bridge: reducing a product equals the Horner sum over
-- the left factor — `reduce-mod-m (p *P q) ≡ hsum p (reduce-mod-m q)` — built
-- from the fold + the `xtime`/linearity machinery. No polynomial long division.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Expand where

open import Substrate.Algebra.F2 using (𝟘)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_; 𝟎ⱽ; +ⱽ-identityˡ; *ₛ-absorbˡ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂; subst)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-comm to +ℕ-comm)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_; shift-to-suc-on-left;
  pad-end; x-shift; _·c_)
open import Substrate.Algebra.F2.GF256.Xtime using (m-lo; xtime; xtime-+ⱽ; xtime-*ₛ)
open import Substrate.Algebra.F2.GF256.Reduce using (reduce-mod-m; reduce-+ⱽ; reduce-*ₛ)

reduce-x-shift : ∀ {n} (q : Vec _ n) → reduce-mod-m (𝟘 ∷ q) ≡ xtime (reduce-mod-m q)
reduce-x-shift q = +ⱽ-identityˡ (xtime (reduce-mod-m q))

xtime-zero : xtime 𝟎ⱽ ≡ 𝟎ⱽ
xtime-zero = trans (+ⱽ-identityˡ (𝟘 *ₛ m-lo)) (*ₛ-absorbˡ m-lo)

reduce-𝟎ⱽ : ∀ {n} → reduce-mod-m (𝟎ⱽ {n}) ≡ 𝟎ⱽ
reduce-𝟎ⱽ {zero}  = refl
reduce-𝟎ⱽ {suc n} =
  trans (cong (λ z → (𝟘 ∷ 𝟎ⱽ) +ⱽ xtime z) (reduce-𝟎ⱽ {n}))
        (trans (cong ((𝟘 ∷ 𝟎ⱽ) +ⱽ_) xtime-zero) (+ⱽ-identityˡ 𝟎ⱽ))

reduce-subst : ∀ {a b} (eq : a ≡ b) (v : Polynomial a)
             → reduce-mod-m (subst Polynomial eq v) ≡ reduce-mod-m v
reduce-subst refl v = refl

reduce-pad-end : ∀ {n} (k : ℕ) (v : Polynomial n)
               → reduce-mod-m (pad-end k v) ≡ reduce-mod-m v
reduce-pad-end k []      = reduce-𝟎ⱽ {k}
reduce-pad-end k (x ∷ v) = cong (λ z → (x ∷ 𝟎ⱽ) +ⱽ xtime z) (reduce-pad-end k v)

hsum : ∀ {n} → Polynomial n → Vector 8 → Vector 8
hsum []      r = 𝟎ⱽ
hsum (a ∷ p) r = (a *ₛ r) +ⱽ hsum p (xtime r)

hsum-xtime : ∀ {n} (p : Polynomial n) (r : Vector 8) → xtime (hsum p r) ≡ hsum p (xtime r)
hsum-xtime []      r = xtime-zero
hsum-xtime (a ∷ p) r =
  trans (xtime-+ⱽ (a *ₛ r) (hsum p (xtime r)))
        (cong₂ _+ⱽ_ (xtime-*ₛ a r) (hsum-xtime p (xtime r)))

reduce-*P-expand : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
                 → reduce-mod-m (p *P q) ≡ hsum p (reduce-mod-m q)
reduce-*P-expand {zero}  {m} []      q = reduce-𝟎ⱽ {m}
reduce-*P-expand {suc n} {m} (a ∷ p) q =
  trans (reduce-+ⱽ (shift-to-suc-on-left (pad-end (suc n) (a ·c q))) (x-shift (p *P q)))
  (trans (cong₂ _+ⱽ_
            (trans (reduce-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)))
                   (trans (reduce-pad-end (suc n) (a ·c q)) (reduce-*ₛ a q)))
            (trans (reduce-x-shift (p *P q)) (cong xtime (reduce-*P-expand p q))))
         (cong ((a *ₛ reduce-mod-m q) +ⱽ_) (hsum-xtime p (reduce-mod-m q))))
