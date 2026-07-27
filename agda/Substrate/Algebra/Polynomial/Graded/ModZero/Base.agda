------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.ModZero.Base
--
-- snoc/vinit/vlast interaction with `reduce-mod-f`, the monomial relation
-- y^(suc d) ≡ f-lo, THE CRUX `reduce-modulus-zero`, `modulus-multiple`, and the
-- nth-determinacy lemmas `reduce-zero-nth` / `reduce-cong-nth`.
--
-- ⟡mod-content-squeeze (propagation): ModZero measured 150MB. MEASURED: its floor with
-- the F+Mod opens alone is 90MB and adding the Quotient and Div opens costs ZERO (90/90/90),
-- so the 60MB is ModZero's OWN CONTENT — the parents did not need splitting, this file did.
-- Split at the Bézout-inverse boundary; each part carries ~30MB over the shared floor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.ModZero.Base where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using () renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as D


module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  -- ⟡public-policy: NO RE-EXPORT. Bind at the sources.
  open F.Over CR
  open M.Over CR d f-lo
  open Q.Over CR d f-lo
  open D.Over CR d f-lo

  private variable n m : ℕ

  -- vlast / vinit of a snoc.
  vlast-snoc : (w : Poly n) (x : A) → vlast (snoc w x) ≡ x
  vlast-snoc []      x = refl
  vlast-snoc (a ∷ w) x = vlast-snoc w x

  vinit-snoc : (w : Poly n) (x : A) → vinit (snoc w x) ≡ w
  vinit-snoc []      x = refl
  vinit-snoc (a ∷ w) x = cong (a ∷_) (vinit-snoc w x)

  -- reduce ignores a trailing zero.
  reduce-snoc-zero : (w : Poly n) → reduce-mod-f (snoc w 𝟘) ≡ reduce-mod-f w
  reduce-snoc-zero []      = trans (reduce-y-shift []) ytime-zero
  reduce-snoc-zero (a ∷ w) =
    cong (λ z → (a ∷ replicate d 𝟘) +P ytime z) (reduce-snoc-zero w)

  -- the monomial y^(suc d) reduces to f-lo (the defining modulus relation).
  monomial : Poly (suc (suc d))
  monomial = snoc (replicate (suc d) 𝟘) 𝟙

  reduce-monomial : reduce-mod-f monomial ≡ f-lo
  reduce-monomial =
    trans (reduce-y-shift (snoc (replicate d 𝟘) 𝟙))
    (trans (cong ytime (reduce-idempotent (snoc (replicate d 𝟘) 𝟙)))
           ytime-M')
    where
      ytime-M' : ytime (snoc (replicate d 𝟘) 𝟙) ≡ f-lo
      ytime-M' =
        trans (cong₂ _+P_ (cong (𝟘 ∷_) (vinit-snoc (replicate d 𝟘) 𝟙))
                          (cong (_·c f-lo) (vlast-snoc (replicate d 𝟘) 𝟙)))
        (trans (cong ((𝟘 ∷ replicate d 𝟘) +P_) (·c-identityˡ f-lo))
               (+P-identityˡ f-lo))

  -- THE CRUX: the modulus b-poly reduces to 0.
  reduce-modulus-zero : reduce-mod-f b-poly ≡ replicate (suc d) 𝟘
  reduce-modulus-zero =
    trans (cong reduce-mod-f bp≡)
    (trans (reduce-+P monomial (snoc (-P f-lo) 𝟘))
    (trans (cong₂ _+P_ reduce-monomial
                       (trans (reduce-snoc-zero (-P f-lo)) (reduce-idempotent (-P f-lo))))
           (+P-inverseʳ f-lo)))
    where
      bp≡ : b-poly ≡ monomial +P snoc (-P f-lo) 𝟘
      bp≡ = sym (trans (snoc-+P (replicate (suc d) 𝟘) (-P f-lo) 𝟙 𝟘)
                       (cong₂ snoc (+P-identityˡ (-P f-lo)) (+-identityʳ 𝟙)))

  -- a MULTIPLE of the modulus reduces to 0 (poly `modulus-multiple`): the exact
  -- analog of ℕ's `modulus-multiple = mod-mult-hom + suc-mod-self`, here
  -- `reduce-*P-expand` (the ×P bridge) + `reduce-modulus-zero` + `hsum-zeroʳ`.
  -- This is the term that vanishes in the Bézout inverse read (B-EEA-INV).
  modulus-multiple : (q : Poly m) → reduce-mod-f (q *P b-poly) ≡ replicate (suc d) 𝟘
  modulus-multiple q =
    trans (reduce-*P-expand q b-poly)
          (trans (cong (hsum q) reduce-modulus-zero) (hsum-zeroʳ q))

  ------------------------------------------------------------------------
  -- B-INV-SPLIT: reduce respects the coefficient-wise Bézout sum.
  ------------------------------------------------------------------------

  -- reduce of an all-zero-coefficient poly is 𝟎C (any length).
  reduce-zero-nth : (u : Poly n) → ((k : ℕ) → nth u k ≡ 𝟘)
                  → reduce-mod-f u ≡ replicate (suc d) 𝟘
  reduce-zero-nth []      h = refl
  reduce-zero-nth (a ∷ u) h =
    trans (cong₂ (λ x z → (x ∷ replicate d 𝟘) +P ytime z) (h 0) (reduce-zero-nth u (λ k → h (suc k))))
          (trans (cong ((𝟘 ∷ replicate d 𝟘) +P_) ytime-zero) (+P-identityˡ (replicate (suc d) 𝟘)))

  -- reduce is determined by the coefficients (nth), across lengths.
  reduce-cong-nth : {n′ : ℕ} (u : Poly n) (v : Poly n′)
                  → ((k : ℕ) → nth u k ≡ nth v k) → reduce-mod-f u ≡ reduce-mod-f v
  reduce-cong-nth []      v       h = sym (reduce-zero-nth v (λ k → sym (h k)))
  reduce-cong-nth (a ∷ u) []      h = reduce-zero-nth (a ∷ u) h
  reduce-cong-nth (a ∷ u) (b ∷ v) h =
    cong₂ (λ x z → (x ∷ replicate d 𝟘) +P ytime z) (h 0) (reduce-cong-nth u v (λ k → h (suc k)))
