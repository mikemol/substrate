------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.Mod.Expand
--
-- B2b scalar linearity (`ytime-·c`, `reduce-·c`) and the B2c support tier for the ×P
-- bridge: the zero/shift lemmas, `reduce-pad-end`, and `hsum` + `hsum-ytime`.
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

module Substrate.Algebra.Polynomial.Graded.Mod.Expand where

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
import Substrate.Algebra.Polynomial.Graded.Mod.Core as Core

module Over {A : Set} (CR : CommutativeRing A) (d : ℕ) (f-lo : Vec A (suc d)) where
  open F.Over CR             -- NON-public (applied directly, not inherited)
  open Core.Over CR d f-lo   -- NON-public: Expand re-exports only what Expand defines

  private variable n m : ℕ

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
