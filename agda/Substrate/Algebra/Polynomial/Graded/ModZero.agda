------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.ModZero  (B-EEA-INV, crux)
--
-- The modulus reduces to zero: `reduce-mod-f b-poly ≡ 𝟎C`, over any
-- CommutativeRing.  b-poly = y^(suc d) − f-lo is the divisor; modulo itself it
-- is 0.  This is the key fact behind reading the inverse off a Bézout identity
-- (B-EEA-INV → AI-8): in `s·a + t·m = 1`, the `t·m` term vanishes mod m, so
-- `reduce(s·a) = 1`.
--
-- Proof: split b-poly = y^(suc d) +P snoc(−f-lo)𝟘; the monomial reduces to f-lo
-- (the defining modulus relation `reduce-y-shift` + `ytime` on the monomial),
-- the snoc-𝟘 part reduces to −f-lo (`reduce` ignores trailing zeros), and
-- f-lo +P −f-lo ≡ 𝟎C (`+P-inverseʳ`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.ModZero where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using () renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.Div as D

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
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

  -- THE BRIDGE: from the convCoeff Bézout (convCoeff s a + convCoeff t m ≡ nth g,
  -- ∀k) to reduce-level additivity — pad both products into one +P, push reduce
  -- through, match g by reduce-cong-nth.  (B-INV-DROP then drops the t·m term.)
  reduce-split : {ns na nt nm ng : ℕ}
                 (sv : Poly ns) (av : Poly na) (tv : Poly nt) (mv : Poly nm) (gv : Poly ng)
               → ((k : ℕ) → convCoeff sv av k + convCoeff tv mv k ≡ nth gv k)
               → reduce-mod-f (sv *P av) +P reduce-mod-f (tv *P mv) ≡ reduce-mod-f gv
  reduce-split {ns} {na} {nt} {nm} sv av tv mv gv bez = trans (sym redW) (reduce-cong-nth W gv nthW)
    where
      U  = pad-end (nt ℕ+ nm) (sv *P av)
      V′ = subst Poly (+ℕ-comm (nt ℕ+ nm) (ns ℕ+ na)) (pad-end (ns ℕ+ na) (tv *P mv))
      W  = U +P V′
      redW : reduce-mod-f W ≡ reduce-mod-f (sv *P av) +P reduce-mod-f (tv *P mv)
      redW = trans (reduce-+P U V′)
             (cong₂ _+P_ (reduce-pad-end (nt ℕ+ nm) (sv *P av))
                         (trans (reduce-subst (+ℕ-comm (nt ℕ+ nm) (ns ℕ+ na)) (pad-end (ns ℕ+ na) (tv *P mv)))
                                (reduce-pad-end (ns ℕ+ na) (tv *P mv))))
      nthW : (k : ℕ) → nth W k ≡ nth gv k
      nthW k = trans (nth-+P U V′ k)
               (trans (cong₂ _+_
                         (trans (nth-pad-end (nt ℕ+ nm) (sv *P av) k) (nth-*P sv av k))
                         (trans (nth-subst (+ℕ-comm (nt ℕ+ nm) (ns ℕ+ na)) (pad-end (ns ℕ+ na) (tv *P mv)) k)
                                (trans (nth-pad-end (ns ℕ+ na) (tv *P mv) k) (nth-*P tv mv k))))
                      (bez k))

  -- B-INV-DROP: the t·m term DROPS (it is a multiple of the modulus).  From a
  -- Bézout against the divisor b-poly, reduce(s·a) ≡ reduce g.  Mirrors ℕ `drop`.
  reduce-drop : {ns na nt ng : ℕ}
                (sv : Poly ns) (av : Poly na) (tv : Poly nt) (gv : Poly ng)
              → ((k : ℕ) → convCoeff sv av k + convCoeff tv b-poly k ≡ nth gv k)
              → reduce-mod-f (sv *P av) ≡ reduce-mod-f gv
  reduce-drop sv av tv gv bez =
    trans (sym (+P-identityʳ (reduce-mod-f (sv *P av))))
    (trans (cong (reduce-mod-f (sv *P av) +P_) (sym (modulus-multiple tv)))
           (reduce-split sv av tv b-poly gv bez))

  -- B-INV-READ: the inverse property in the quotient ring.  From a Bézout
  -- against b-poly with gcd = unit, a *Q (reduce s) ≡ 𝟙.  Mirrors ℕ `proof`.
  reduce-read : {ns nt ng : ℕ}
                (s : Poly ns) (a : Poly (suc d)) (t : Poly nt) (g : Poly ng)
              → ((k : ℕ) → convCoeff s a k + convCoeff t b-poly k ≡ nth g k)
              → reduce-mod-f g ≡ oneC
              → a *Q (reduce-mod-f s) ≡ oneC
  reduce-read {ns} s a t g bez gunit =
    trans (sym (reduce-*-hom a s))
    (trans (trans (cong reduce-mod-f (*P-comm a s)) (reduce-subst (+ℕ-comm ns (suc d)) (s *P a)))
    (trans (reduce-drop s a t g bez) gunit))
