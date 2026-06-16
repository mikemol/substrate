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

open import Substrate.Foundation.Nat using (ℕ; zero; suc; s≤s; z≤n; s≤s-injective)
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Nat.Properties using () renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Fin using (Fin; toℕ; fromℕ<) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-fromℕ<; toℕ-injective)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  open F.Over CR public   -- Poly, _+P_, _·c_, nth(-ext), 𝟘/_+_, the ring laws, rearrange, ·-distribʳ …

  private variable n m : ℕ

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

  -- 7. (B2b) scalar linearity: ytime and reduce-mod-f preserve ·c.
  ·c-+P-distrib : (c : A) (u v : Poly n) → c ·c (u +P v) ≡ (c ·c u) +P (c ·c v)
  ·c-+P-distrib c []      []      = refl
  ·c-+P-distrib c (x ∷ u) (y ∷ v) = cong₂ _∷_ (*-distribˡ c x y) (·c-+P-distrib c u v)

  ·c-assoc : (c a : A) (v : Poly n) → c ·c (a ·c v) ≡ (c * a) ·c v
  ·c-assoc c a []      = refl
  ·c-assoc c a (x ∷ v) = cong₂ _∷_ (sym (*-assoc c a x)) (·c-assoc c a v)

  ·c-zeroʳ : (c : A) → c ·c (replicate n 𝟘) ≡ replicate n 𝟘
  ·c-zeroʳ {zero}  c = refl
  ·c-zeroʳ {suc n} c = cong₂ _∷_ (*-absorbʳ c) (·c-zeroʳ {n} c)

  vinit-·c : (c : A) (v : Poly (suc n)) → vinit (c ·c v) ≡ c ·c vinit v
  vinit-·c {zero}  c (x ∷ []) = refl
  vinit-·c {suc _} c (x ∷ v)  = cong ((c * x) ∷_) (vinit-·c c v)
  vlast-·c : (c : A) (v : Poly (suc n)) → vlast (c ·c v) ≡ c * vlast v
  vlast-·c {zero}  c (x ∷ []) = refl
  vlast-·c {suc _} c (x ∷ v)  = vlast-·c c v

  ytime-·c : (c : A) (v : Poly (suc d)) → ytime (c ·c v) ≡ c ·c ytime v
  ytime-·c c v =
    trans (cong₂ _+P_ (cong₂ _∷_ (sym (*-absorbʳ c)) (vinit-·c c v))
                      (trans (cong (_·c f-lo) (vlast-·c c v)) (sym (·c-assoc c (vlast v) f-lo))))
          (sym (·c-+P-distrib c (𝟘 ∷ vinit v) (vlast v ·c f-lo)))

  reduce-·c : (c : A) (v : Poly n) → reduce-mod-f (c ·c v) ≡ c ·c reduce-mod-f v
  reduce-·c c []      = sym (·c-zeroʳ {suc d} c)
  reduce-·c c (a ∷ v) =
    trans (cong₂ _+P_ (cong ((c * a) ∷_) (sym (·c-zeroʳ {d} c)))
                      (trans (cong ytime (reduce-·c c v)) (ytime-·c c (reduce-mod-f v))))
          (sym (·c-+P-distrib c (a ∷ replicate d 𝟘) (ytime (reduce-mod-f v))))

  -- 8. (B2c) the ×P bridge: reduce-mod-f (p *P q) ≡ hsum p (reduce-mod-f q).
  vinit-zero : vinit (replicate (suc n) 𝟘) ≡ replicate n 𝟘
  vinit-zero {zero}  = refl
  vinit-zero {suc n} = cong (𝟘 ∷_) (vinit-zero {n})
  vlast-zero : vlast (replicate (suc n) 𝟘) ≡ 𝟘
  vlast-zero {zero}  = refl
  vlast-zero {suc n} = vlast-zero {n}

  reduce-y-shift : (q : Poly n) → reduce-mod-f (𝟘 ∷ q) ≡ ytime (reduce-mod-f q)
  reduce-y-shift q = +P-identityˡ (ytime (reduce-mod-f q))

  ytime-zero : ytime (replicate (suc d) 𝟘) ≡ replicate (suc d) 𝟘
  ytime-zero =
    trans (cong₂ _+P_ (cong (𝟘 ∷_) (vinit-zero {d}))
                      (trans (cong (_·c f-lo) (vlast-zero {d})) (·c-absorbˡ f-lo)))
          (+P-identityˡ (replicate (suc d) 𝟘))

  reduce-𝟎P : reduce-mod-f (replicate n 𝟘) ≡ replicate (suc d) 𝟘
  reduce-𝟎P {zero}  = refl
  reduce-𝟎P {suc n} =
    trans (cong (λ z → (𝟘 ∷ replicate d 𝟘) +P ytime z) (reduce-𝟎P {n}))
          (trans (cong ((𝟘 ∷ replicate d 𝟘) +P_) ytime-zero)
                 (+P-identityˡ (replicate (suc d) 𝟘)))

  reduce-subst : ∀ {a b} (eq : a ≡ b) (v : Poly a)
               → reduce-mod-f (subst Poly eq v) ≡ reduce-mod-f v
  reduce-subst refl v = refl

  reduce-pad-end : (k : ℕ) (v : Poly n) → reduce-mod-f (pad-end k v) ≡ reduce-mod-f v
  reduce-pad-end k []      = reduce-𝟎P {k}
  reduce-pad-end k (x ∷ v) = cong (λ z → (x ∷ replicate d 𝟘) +P ytime z) (reduce-pad-end k v)

  hsum : Poly n → Poly (suc d) → Poly (suc d)
  hsum []      r = replicate (suc d) 𝟘
  hsum (a ∷ p) r = (a ·c r) +P hsum p (ytime r)

  hsum-ytime : (p : Poly n) (r : Poly (suc d)) → ytime (hsum p r) ≡ hsum p (ytime r)
  hsum-ytime []      r = ytime-zero
  hsum-ytime (a ∷ p) r =
    trans (ytime-+P (a ·c r) (hsum p (ytime r)))
          (cong₂ _+P_ (ytime-·c a r) (hsum-ytime p (ytime r)))

  reduce-*P-expand : (p : Poly n) (q : Poly m) → reduce-mod-f (p *P q) ≡ hsum p (reduce-mod-f q)
  reduce-*P-expand {n = zero}  {m = m} []      q = reduce-𝟎P {m}
  reduce-*P-expand {n = suc n} {m = m} (a ∷ p) q =
    trans (reduce-+P (shift-to-suc-on-left (pad-end (suc n) (a ·c q))) (x-shift (p *P q)))
    (trans (cong₂ _+P_
              (trans (reduce-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)))
                     (trans (reduce-pad-end (suc n) (a ·c q)) (reduce-·c a q)))
              (trans (reduce-y-shift (p *P q)) (cong ytime (reduce-*P-expand p q))))
           (cong ((a ·c reduce-mod-f q) +P_) (hsum-ytime p (reduce-mod-f q))))

  -- 9. (B2d) idempotence + ring-hom. FOUNDATION + kernel tools (the kernel itself,
  --    hsum-one-basis, is the one piece GF256 brute-forced with 8 refls).
  *-identityʳ : (a : A) → a * 𝟙 ≡ a
  *-identityʳ a = trans (*-comm a 𝟙) (*-identityˡ a)

  +P-identityʳ : (v : Poly n) → v +P replicate n 𝟘 ≡ v
  +P-identityʳ {n} v = nth-ext _ v (λ k →
    trans (nth-+P v (replicate n 𝟘) k)
          (trans (cong (nth v k +_) (nth-replicate n k)) (+-identityʳ (nth v k))))

  oneC : Poly (suc d)
  oneC = 𝟙 ∷ replicate d 𝟘

  -- reduce p = hsum p oneC: the Horner fold IS evaluation at the xtime-powers of the unit.
  reduce-eq-hsum : (p : Poly n) → reduce-mod-f p ≡ hsum p oneC
  reduce-eq-hsum []      = refl
  reduce-eq-hsum (a ∷ q) =
    cong₂ _+P_ (cong₂ _∷_ (sym (*-identityʳ a)) (sym (·c-zeroʳ {d} a)))
               (trans (cong ytime (reduce-eq-hsum q)) (hsum-ytime q oneC))

  xpow : ℕ → Poly (suc d) → Poly (suc d)
  xpow zero    r = r
  xpow (suc k) r = xpow k (ytime r)

  xpow-ytime : (k : ℕ) (r : Poly (suc d)) → xpow k (ytime r) ≡ ytime (xpow k r)
  xpow-ytime zero    r = refl
  xpow-ytime (suc k) r = xpow-ytime k (ytime r)

  -- hsum is the basis-weighted sum (the fold = Σᵢ pᵢ ·c ytimeⁱ r).
  hsum-is-sum : (p : Poly n) (r : Poly (suc d))
              → hsum p r ≡ sum (λ (i : Fin n) → nth p (toℕ i) ·c xpow (toℕ i) r)
  hsum-is-sum []      r = refl
  hsum-is-sum (a ∷ p) r = cong ((a ·c r) +P_) (hsum-is-sum p (ytime r))

  -- KERNEL TOOLS: vlast = the top coefficient; ytime with zero top coeff is just the shift.
  vlast-nth : (v : Poly (suc n)) → vlast v ≡ nth v n
  vlast-nth {zero}  (x ∷ []) = refl
  vlast-nth {suc n} (x ∷ v)  = vlast-nth v

  ytime-shift : (v : Poly (suc d)) → vlast v ≡ 𝟘 → ytime v ≡ 𝟘 ∷ vinit v
  ytime-shift v hyp =
    trans (cong ((𝟘 ∷ vinit v) +P_) (trans (cong (_·c f-lo) hyp) (·c-absorbˡ f-lo)))
          (+P-identityʳ (𝟘 ∷ vinit v))

  -- KERNEL (the cost-evaporation move: ytime on a zero-top vector is a PURE shift,
  -- so xpow k oneC telescopes basis-by-basis — no Fin/degree scaffolding needed.
  -- This is the part GF256 brute-forced with 8 refls; generically it's the single
  -- shift lemma ytime-basis-shift = ytime-shift ∘ (top coeff = 𝟘) ∘ vinit-basis.)
  inj : ∀ {n} → Fin n → Fin (suc n)
  inj fz     = fz
  inj (fs i) = fs (inj i)

  inj-toℕ : ∀ {n} (i : Fin n) → toℕ (inj i) ≡ toℕ i
  inj-toℕ fz     = refl
  inj-toℕ (fs i) = cong suc (inj-toℕ i)

  <-irrefl : (n : ℕ) → n <ℕ n → ⊥
  <-irrefl (suc n) (s≤s p) = <-irrefl n p

  -- vinit drops the (zero) top of a low basis vector → the basis one dim down.
  vinit-basis : ∀ {n} (i : Fin n) → vinit (basis {suc n} (inj i)) ≡ basis {n} i
  vinit-basis {suc n} fz     = cong (𝟙 ∷_) (vinit-zero {n})
  vinit-basis {suc n} (fs i) = cong (𝟘 ∷_) (vinit-basis {n} i)

  -- a low basis vector has zero top coefficient (its 𝟙 sits below position d).
  vlast-basis-inj : (i : Fin d) → vlast (basis {suc d} (inj i)) ≡ 𝟘
  vlast-basis-inj i =
    trans (vlast-nth (basis (inj i)))
          (nth-basis-other (inj i) d
            (λ e → <-irrefl (toℕ (inj i))
                     (subst (λ z → toℕ (inj i) <ℕ z) e
                            (subst (_<ℕ d) (sym (inj-toℕ i)) (toℕ-bound i)))))

  ytime-basis-shift : (i : Fin d) → ytime (basis {suc d} (inj i)) ≡ basis {suc d} (fs i)
  ytime-basis-shift i =
    trans (ytime-shift (basis (inj i)) (vlast-basis-inj i))
          (cong (𝟘 ∷_) (vinit-basis i))

  ≤-step : ∀ {a b} → a ≤ℕ b → a ≤ℕ suc b
  ≤-step z≤n     = z≤n
  ≤-step (s≤s p) = s≤s (≤-step p)

  -- ytimeⁱ of the unit = the i-th basis vector (no reduction below degree suc d).
  -- Recurse on the EXPONENT k (decoupled from the carrier d); bridge Fin indices
  -- by toℕ alone (toℕ-injective), so each ytime is a pure basis shift.
  pow-basis-ℕ : (k : ℕ) (lt : k <ℕ suc d) → xpow k oneC ≡ basis (fromℕ< lt)
  pow-basis-ℕ zero    lt = refl
  pow-basis-ℕ (suc k) lt =
    trans (xpow-ytime k oneC)
    (trans (cong ytime (pow-basis-ℕ k (≤-step lt')))
    (trans (cong (λ z → ytime (basis z))
              (toℕ-injective (trans (toℕ-fromℕ< (≤-step lt'))
                                    (sym (trans (inj-toℕ j) (toℕ-fromℕ< lt'))))))
    (trans (ytime-basis-shift j)
           (cong basis (toℕ-injective (trans (cong suc (toℕ-fromℕ< lt'))
                                             (sym (toℕ-fromℕ< lt))))))))
    where
      lt' = s≤s-injective lt
      j   = fromℕ< lt'

  hsum-one-basis : (i : Fin (suc d)) → xpow (toℕ i) oneC ≡ basis i
  hsum-one-basis i =
    trans (pow-basis-ℕ (toℕ i) (toℕ-bound i))
          (cong basis (toℕ-injective (toℕ-fromℕ< (toℕ-bound i))))

  -- evaluation at the unit reconstructs p (basis-decomposition closes it).
  hsum-oneC-id : (p : Poly (suc d)) → hsum p oneC ≡ p
  hsum-oneC-id p =
    trans (hsum-is-sum p oneC)
          (trans (sum-cong (λ i → cong (nth p (toℕ i) ·c_) (hsum-one-basis i)))
                 (sym (basis-decomp p)))

  -- the Canonical: reduce-mod-f is the identity on already-reduced (carrier) polys.
  reduce-idempotent : (p : Poly (suc d)) → reduce-mod-f p ≡ p
  reduce-idempotent p = trans (reduce-eq-hsum p) (hsum-oneC-id p)

  -- reduce is a ring homomorphism in the multiplicative slot.
  reduce-*-hom : (p : Poly n) (q : Poly m)
               → reduce-mod-f (p *P q) ≡ reduce-mod-f (p *P reduce-mod-f q)
  reduce-*-hom p q =
    trans (reduce-*P-expand p q)
          (sym (trans (reduce-*P-expand p (reduce-mod-f q))
                      (cong (hsum p) (reduce-idempotent (reduce-mod-f q)))))
