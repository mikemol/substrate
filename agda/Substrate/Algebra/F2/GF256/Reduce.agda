------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Reduce  (was GF256 §A3)
--
-- `reduce-mod-m`: the Horner fold (digit-on-demand), and the proof that it
-- is F₂-linear — additive (`reduce-+ⱽ`) and scalar (`reduce-*ₛ`) — by Horner
-- induction with the `xtime` linearity laws (§Xtime) at the step.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Reduce where

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; _·_; ·-absorbʳ)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_; 𝟎ⱽ; +ⱽ-identityˡ;
  +ⱽ-comm; +ⱽ-assoc; *ₛ-distribˡ-+ⱽ; lookup-*ₛ; lookup-𝟎; ≡-from-lookup)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2.GF256.Xtime using (xtime; xtime-+ⱽ; xtime-*ₛ)

reduce-mod-m : ∀ {n} → Vec F₂ n → Vector 8
reduce-mod-m []      = 𝟎ⱽ
reduce-mod-m (a ∷ q) = (a ∷ 𝟎ⱽ) +ⱽ xtime (reduce-mod-m q)

*ₛ-zeroʳ : ∀ {n} (c : F₂) → (c *ₛ 𝟎ⱽ {n}) ≡ 𝟎ⱽ {n}
*ₛ-zeroʳ c = ≡-from-lookup _ _
  (λ i → trans (lookup-*ₛ c 𝟎ⱽ i)
         (trans (cong (c ·_) (lookup-𝟎 i)) (trans (·-absorbʳ c) (sym (lookup-𝟎 i)))))

+ⱽ-rearrange : ∀ {n} (a b c d : Vector n) → (a +ⱽ b) +ⱽ (c +ⱽ d) ≡ (a +ⱽ c) +ⱽ (b +ⱽ d)
+ⱽ-rearrange a b c d =
  trans (+ⱽ-assoc a b (c +ⱽ d))
  (trans (cong (a +ⱽ_) (sym (+ⱽ-assoc b c d)))
  (trans (cong (λ t → a +ⱽ (t +ⱽ d)) (+ⱽ-comm b c))
  (trans (cong (a +ⱽ_) (+ⱽ-assoc c b d)) (sym (+ⱽ-assoc a c (b +ⱽ d))))))

-- A3a: additivity. base = sym +ⱽ-identityˡ; step = head-split + xtime-+ⱽ(IH) + 4-term rearrange.
reduce-+ⱽ : ∀ {n} (u v : Vec F₂ n) → reduce-mod-m (u +ⱽ v) ≡ reduce-mod-m u +ⱽ reduce-mod-m v
reduce-+ⱽ []      []      = sym (+ⱽ-identityˡ 𝟎ⱽ)
reduce-+ⱽ (a ∷ u) (b ∷ v) =
  trans (cong₂ _+ⱽ_ (cong ((a + b) ∷_) (sym (+ⱽ-identityˡ 𝟎ⱽ)))
                    (trans (cong xtime (reduce-+ⱽ u v))
                           (xtime-+ⱽ (reduce-mod-m u) (reduce-mod-m v))))
        (+ⱽ-rearrange (a ∷ 𝟎ⱽ) (b ∷ 𝟎ⱽ) (xtime (reduce-mod-m u)) (xtime (reduce-mod-m v)))

-- A3b: scalar-linearity. base = sym *ₛ-zeroʳ; step = head-split + xtime-*ₛ(IH) + *ₛ-distribˡ.
reduce-*ₛ : ∀ {n} (c : F₂) (v : Vec F₂ n) → reduce-mod-m (c *ₛ v) ≡ c *ₛ reduce-mod-m v
reduce-*ₛ c []      = sym (*ₛ-zeroʳ c)
reduce-*ₛ c (a ∷ v) =
  trans (cong₂ _+ⱽ_ (cong ((c · a) ∷_) (sym (*ₛ-zeroʳ c)))
                    (trans (cong xtime (reduce-*ₛ c v))
                           (xtime-*ₛ c (reduce-mod-m v))))
        (sym (*ₛ-distribˡ-+ⱽ c (a ∷ 𝟎ⱽ) (xtime (reduce-mod-m v))))
