------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Div  (AI-17 B-DIVa + B-DIVb)
--
-- Polynomial division-with-remainder over R[y], for any `CommutativeRing R`,
-- by the monic divisor `b = y^(suc d) − f-lo` (given by its low part f-lo).
--
-- The FREE projection of the vec-graded uncons-fold whose PRESENTED projection
-- is `reduce-mod-f` (B2): `divmod a = (q-div a , r-div a)` where the remainder
-- `r-div a ≡ reduce-mod-f a` and the quotient is the shed top-digit (`vlast`
-- inside `ytime`). Verified by the recon-eq, coefficient-wise (the `*P` is
-- length-additive, so the natural statement is `nth`-form):
--
--   recon-nth : nth a k ≡ nth (q-div a *P b-poly) k + nth (r-div a) k
--
-- The heart is `KEY` — the f-lo CANCELLATION: `ytime`'s reduction term
-- `vlast·f-lo` cancels `b`'s `vlast·(-f-lo)`, leaving the pure shift; that is
-- precisely why the shed digit IS the quotient digit. Feeds B-EEA (Bézout) → AI-8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.Div where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.Quotient as Q

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  open Q.Over CR d f-lo public   -- Mod (ytime, ·c laws, nth-*P, convCoeff…) + B3 (-P, +P laws)
  private variable n : ℕ

  -- append at the top (the y^(suc d) slot).
  snoc : Poly n → A → Poly (suc n)
  snoc []      x = x ∷ []
  snoc (a ∷ v) x = a ∷ snoc v x

  snoc-+P : (u v : Poly n) (x y : A) → snoc u x +P snoc v y ≡ snoc (u +P v) (x + y)
  snoc-+P []      []      x y = refl
  snoc-+P (a ∷ u) (b ∷ v) x y = cong ((a + b) ∷_) (snoc-+P u v x y)

  snoc-·c : (c : A) (v : Poly n) (x : A) → c ·c snoc v x ≡ snoc (c ·c v) (c * x)
  snoc-·c c []      x = refl
  snoc-·c c (a ∷ v) x = cong ((c * a) ∷_) (snoc-·c c v x)

  snoc-vinit-vlast : (v : Poly (suc n)) → snoc (vinit v) (vlast v) ≡ v
  snoc-vinit-vlast {zero}  (x ∷ []) = refl
  snoc-vinit-vlast {suc n} (x ∷ v)  = cong (x ∷_) (snoc-vinit-vlast v)

  -- the divisor b = y^(suc d) − f-lo, as a Poly (suc (suc d)).
  b-poly : Poly (suc (suc d))
  b-poly = snoc (-P f-lo) 𝟙

  -- ytime's reduction term cancels b's low part, leaving the pure shift.
  P1 : (v : Poly (suc d)) → ytime v +P (vlast v ·c -P f-lo) ≡ 𝟘 ∷ vinit v
  P1 v = trans (+P-assoc (𝟘 ∷ vinit v) (vlast v ·c f-lo) (vlast v ·c -P f-lo))
         (trans (cong ((𝟘 ∷ vinit v) +P_) (sym (·c-+P-distrib (vlast v) f-lo (-P f-lo))))
         (trans (cong (λ z → (𝟘 ∷ vinit v) +P (vlast v ·c z)) (+P-inverseʳ f-lo))
         (trans (cong ((𝟘 ∷ vinit v) +P_) (·c-zeroʳ (vlast v)))
                (+P-identityʳ (𝟘 ∷ vinit v)))))

  P2 : (v : Poly (suc d)) → 𝟘 + (vlast v * 𝟙) ≡ vlast v
  P2 v = trans (+-identityˡ (vlast v * 𝟙)) (*-identityʳ (vlast v))

  -- THE KEY: the raw shift 𝟘∷v = mod-shift (ytime, padded) + quotient-digit·b.
  KEY : (v : Poly (suc d)) → snoc (ytime v) 𝟘 +P (vlast v ·c b-poly) ≡ 𝟘 ∷ v
  KEY v =
    trans (cong (snoc (ytime v) 𝟘 +P_) (snoc-·c (vlast v) (-P f-lo) 𝟙))
    (trans (snoc-+P (ytime v) (vlast v ·c -P f-lo) 𝟘 (vlast v * 𝟙))
    (trans (cong₂ snoc (P1 v) (P2 v))
           (cong (𝟘 ∷_) (snoc-vinit-vlast v))))

  -- divmod: the Free projection — quotient = shed digits, remainder = reduce-mod-f.
  divmod : Poly n → (Poly n × Poly (suc d))
  divmod []      = [] , replicate (suc d) 𝟘
  divmod (a ∷ q) = let (Q' , r') = divmod q
                   in (vlast r' ∷ Q') , ((a ∷ replicate d 𝟘) +P ytime r')
  q-div : Poly n → Poly n
  q-div a = proj₁ (divmod a)
  r-div : Poly n → Poly (suc d)
  r-div a = proj₂ (divmod a)

  -- the remainder IS reduce-mod-f (the Presented projection, B2).
  r-div-is-reduce : (a : Poly n) → r-div a ≡ reduce-mod-f a
  r-div-is-reduce []      = refl
  r-div-is-reduce (a ∷ q) = cong (λ z → (a ∷ replicate d 𝟘) +P ytime z) (r-div-is-reduce q)

  -- snoc-ing a 𝟘 at the top is invisible to nth.
  nth-snoc-zero : (w : Poly n) (k : ℕ) → nth (snoc w 𝟘) k ≡ nth w k
  nth-snoc-zero []      zero    = refl
  nth-snoc-zero []      (suc k) = refl
  nth-snoc-zero (a ∷ w) zero    = refl
  nth-snoc-zero (a ∷ w) (suc k) = nth-snoc-zero w k

  -- KEY at the nth level.
  KEY-nth : (v : Poly (suc d)) (k : ℕ) → nth (𝟘 ∷ v) k ≡ nth (ytime v) k + (vlast v * nth b-poly k)
  KEY-nth v k =
    trans (cong (λ z → nth z k) (sym (KEY v)))
    (trans (nth-+P (snoc (ytime v) 𝟘) (vlast v ·c b-poly) k)
           (cong₂ _+_ (nth-snoc-zero (ytime v) k) (nth-·c (vlast v) b-poly k)))

  private
    r0 : (V c Y : A) → V + (c + Y) ≡ c + (Y + V)
    r0 V c Y = trans (sym (+-assoc V c Y))
               (trans (cong (_+ Y) (+-comm V c))
               (trans (+-assoc c V Y) (cong (c +_) (+-comm V Y))))
    rS : (a b Y : A) → b + (Y + a) ≡ (a + b) + Y
    rS a b Y = trans (cong (b +_) (+-comm Y a))
               (trans (sym (+-assoc b a Y)) (cong (_+ Y) (+-comm b a)))

  -- THE RECON-EQ: a ≡ q-div a *P b-poly +P r-div a, coefficient-wise
  -- (convCoeff (q-div a) b-poly = nth (q-div a *P b-poly), via nth-*P).
  recon-nth : (a : Poly n) (k : ℕ) → nth a k ≡ convCoeff (q-div a) b-poly k + nth (r-div a) k
  recon-nth []      k = sym (trans (cong (𝟘 +_) (nth-replicate (suc d) k)) (+-identityˡ 𝟘))
  recon-nth (c ∷ q) zero =
    sym (trans (cong ((vlast (r-div q) * nth b-poly zero) +_)
                     (nth-+P (c ∷ replicate d 𝟘) (ytime (r-div q)) zero))
        (trans (r0 (vlast (r-div q) * nth b-poly zero) c (nth (ytime (r-div q)) zero))
        (trans (cong (c +_) (sym (KEY-nth (r-div q) zero))) (+-identityʳ c))))
  recon-nth (c ∷ q) (suc k) =
    trans (recon-nth q k)
    (trans (cong (convCoeff (q-div q) b-poly k +_) (KEY-nth (r-div q) (suc k)))
    (trans (rS (vlast (r-div q) * nth b-poly (suc k)) (convCoeff (q-div q) b-poly k)
              (nth (ytime (r-div q)) (suc k)))
           (cong (((vlast (r-div q) * nth b-poly (suc k)) + convCoeff (q-div q) b-poly k) +_)
                 (sym (trans (nth-+P (c ∷ replicate d 𝟘) (ytime (r-div q)) (suc k))
                      (trans (cong (_+ nth (ytime (r-div q)) (suc k)) (nth-replicate d k))
                             (+-identityˡ (nth (ytime (r-div q)) (suc k)))))))))
