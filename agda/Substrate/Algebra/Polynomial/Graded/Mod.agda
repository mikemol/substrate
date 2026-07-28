------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Mod
--
-- R[y] mod a monic f of degree (suc d): carrier `Poly (suc d)`, reduction supplied as
-- DATA (`f-lo`). Generalizes GF256's `reduce-mod-m`/`xtime`/`m-lo` to any
-- `CommutativeRing` — GF(2⁸) is R=F₂, d=7, f-lo = m-lo.
--
-- THE TIP: re-exports Core ⊕ Expand ⊕ this file = exactly Mod's own definitions.
-- THIS FILE: the ×P bridge `reduce-*P-expand` (+21MB, the costliest single def) plus
-- B2d idempotence + the ring-hom.
--
-- ⟡mod-content-squeeze + ⟡public-policy. MEASURED: the ~93MB LOAD FLOOR of the Graded
-- closure is irreducible (a body of ONLY `open F.Over CR public`, zero defs, costs 93MB);
-- narrowing that open to the 33 demanded names (176MB) and shallowing the parent to
-- `Laws.Linear` (174MB) both FAILED — the cost is the module APPLICATION, not the names.
-- So the file is sharded at its own section boundaries, AND each part opens `F.Over`
-- DIRECTLY and NON-PUBLICLY rather than inheriting it down a chain: a module re-exports
-- only what it DEFINES. `Mod.Over` therefore exposes Mod's own definitions and nothing
-- else; consumers needing Graded's API (Quotient: *P-comm/*P-assoc/neg/+-inverse*;
-- Bridge: anti-diag-sum/outer) import `FromCommRing` themselves instead of siphoning it
-- through a module that never uses those names.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.Mod where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; s≤s; z≤n; s≤s-injective)
  renaming (_<_ to _<ℕ_; _≤_ to _≤ℕ_)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-fromℕ<; toℕ-injective)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod.Core as Core
import Substrate.Algebra.Polynomial.Graded.Mod.Expand as Expand

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  open F.Over CR                    -- NON-public: not ours to re-export
  open Core.Over   CR d f-lo public
  open Expand.Over CR d f-lo public

  private variable n m : ℕ

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
  inj fzero     = fzero
  inj (fsuc i) = fsuc (inj i)

  inj-toℕ : ∀ {n} (i : Fin n) → toℕ (inj i) ≡ toℕ i
  inj-toℕ fzero     = refl
  inj-toℕ (fsuc i) = cong suc (inj-toℕ i)

  <-irrefl : (n : ℕ) → n <ℕ n → ⊥
  <-irrefl (suc n) (s≤s p) = <-irrefl n p

  -- vinit drops the (zero) top of a low basis vector → the basis one dim down.
  vinit-basis : ∀ {n} (i : Fin n) → vinit (basis {suc n} (inj i)) ≡ basis {n} i
  vinit-basis {suc n} fzero     = cong (𝟙 ∷_) (vinit-zero {n})
  vinit-basis {suc n} (fsuc i) = cong (𝟘 ∷_) (vinit-basis {n} i)

  -- a low basis vector has zero top coefficient (its 𝟙 sits below position d).
  vlast-basis-inj : (i : Fin d) → vlast (basis {suc d} (inj i)) ≡ 𝟘
  vlast-basis-inj i =
    trans (vlast-nth (basis (inj i)))
          (nth-basis-other (inj i) d
            (λ e → <-irrefl (toℕ (inj i))
                     (subst (λ z → toℕ (inj i) <ℕ z) e
                            (subst (_<ℕ d) (sym (inj-toℕ i)) (toℕ-bound i)))))

  ytime-basis-shift : (i : Fin d) → ytime (basis {suc d} (inj i)) ≡ basis {suc d} (fsuc i)
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
