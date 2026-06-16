------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Mod
--
-- R[y] mod a monic f of degree (suc d): carrier `Poly (suc d)`, with the
-- reduction `y^(suc d) ≡ f-lo` supplied as DATA (`f-lo : Poly (suc d)`).
-- This generalizes GF256's `reduce-mod-m` / `xtime` / `m-lo` to any
-- `CommutativeRing` — GF(2⁸) is the instance R=F₂, d=7, f-lo = m-lo.
--
-- The kernel is `ytime` = ·y mod f (generalizing `xtime` = ·x mod m); GF256's
-- `xtime` is hand-unrolled at length 8, so the generic `ytime` and its linearity
-- are NEW (length-`d`-generic induction via `vinit`/`vlast`), not a verbatim port.
-- `reduce-mod-f` is then the Horner fold, F₂-additive (`reduce-+P`).
--
-- THIS FILE (B2 additive core): support poly-laws, `ytime` + `ytime-+P`,
-- `reduce-mod-f` + `reduce-+P`. Scalar linearity / the *P bridge / idempotence
-- (B2-EXPAND, B2-IDEM) build on top.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.Mod where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  open F.Over CR public   -- Poly, _+P_, _·c_, nth(-ext), 𝟘/_+_, the ring laws, rearrange, ·-distribʳ …

  private variable n : ℕ

  -- generic polynomial abelian-group laws we need (proved via nth-ext):
  +P-identityˡ : (v : Poly n) → (replicate n 𝟘) +P v ≡ v
  +P-identityˡ {n} v = nth-ext _ v (λ k →
    trans (nth-+P (replicate n 𝟘) v k)
          (trans (cong (_+ nth v k) (nth-replicate n k)) (+-identityˡ (nth v k))))

  +P-rearrange : (a b c e : Poly n) → (a +P b) +P (c +P e) ≡ (a +P c) +P (b +P e)
  +P-rearrange a b c e = nth-ext _ _ (λ k →
    trans (nth-+P (a +P b) (c +P e) k)
    (trans (cong₂ _+_ (nth-+P a b k) (nth-+P c e k))
    (trans (rearrange (nth a k) (nth b k) (nth c k) (nth e k))
    (trans (sym (cong₂ _+_ (nth-+P a c k) (nth-+P b e k)))
           (sym (nth-+P (a +P c) (b +P e) k))))))

  -- scalar distributes over the coefficient sum.
  ·c-distribˡ : (a b : A) (v : Poly n) → (a + b) ·c v ≡ (a ·c v) +P (b ·c v)
  ·c-distribˡ a b []      = refl
  ·c-distribˡ a b (x ∷ v) = cong₂ _∷_ (·-distribʳ a b x) (·c-distribˡ a b v)

  -- vinit / vlast: drop / take the top coefficient (generic length).
  vinit : Poly (suc n) → Poly n
  vinit {zero}  (x ∷ []) = []
  vinit {suc _} (x ∷ v)  = x ∷ vinit v
  vlast : Poly (suc n) → A
  vlast {zero}  (x ∷ []) = x
  vlast {suc _} (x ∷ v)  = vlast v

  vinit-+P : (u v : Poly (suc n)) → vinit (u +P v) ≡ vinit u +P vinit v
  vinit-+P {zero}  (x ∷ []) (y ∷ []) = refl
  vinit-+P {suc _} (x ∷ u)  (y ∷ v)  = cong ((x + y) ∷_) (vinit-+P u v)
  vlast-+P : (u v : Poly (suc n)) → vlast (u +P v) ≡ vlast u + vlast v
  vlast-+P {zero}  (x ∷ []) (y ∷ []) = refl
  vlast-+P {suc _} (x ∷ u)  (y ∷ v)  = vlast-+P u v

  -- the kernel: ·y mod f. Shift up by one (`𝟘 ∷ vinit`) + fold the y^(suc d)
  -- overflow (`vlast`) back through f-lo. = GF256 `xtime`, length-generic.
  ytime : Poly (suc d) → Poly (suc d)
  ytime v = (𝟘 ∷ vinit v) +P (vlast v ·c f-lo)

  ytime-+P : (u v : Poly (suc d)) → ytime (u +P v) ≡ ytime u +P ytime v
  ytime-+P u v =
    trans (cong₂ _+P_ (cong₂ _∷_ (sym (+-identityˡ 𝟘)) (vinit-+P u v))
                      (trans (cong (_·c f-lo) (vlast-+P u v))
                             (·c-distribˡ (vlast u) (vlast v) f-lo)))
          (+P-rearrange (𝟘 ∷ vinit u) (𝟘 ∷ vinit v) (vlast u ·c f-lo) (vlast v ·c f-lo))

  -- reduce mod f: the Horner fold (digit-on-demand), F₂-additive.
  reduce-mod-f : Poly n → Poly (suc d)
  reduce-mod-f []      = replicate (suc d) 𝟘
  reduce-mod-f (a ∷ q) = (a ∷ replicate d 𝟘) +P ytime (reduce-mod-f q)

  reduce-+P : (u v : Poly n) → reduce-mod-f (u +P v) ≡ reduce-mod-f u +P reduce-mod-f v
  reduce-+P []      []      = sym (+P-identityˡ (replicate (suc d) 𝟘))
  reduce-+P (a ∷ u) (b ∷ v) =
    trans (cong₂ _+P_ (cong ((a + b) ∷_) (sym (+P-identityˡ (replicate d 𝟘))))
                      (trans (cong ytime (reduce-+P u v))
                             (ytime-+P (reduce-mod-f u) (reduce-mod-f v))))
          (+P-rearrange (a ∷ replicate d 𝟘) (b ∷ replicate d 𝟘)
                        (ytime (reduce-mod-f u)) (ytime (reduce-mod-f v)))
