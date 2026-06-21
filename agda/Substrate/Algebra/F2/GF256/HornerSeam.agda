{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.HornerSeam
--
-- Closing the seam between the two GF(2⁸) reductions by LIFTING their shared
-- shape.  `reduce-mod-f` (graded field, FromCommRing F₂-CommRing) and
-- `reduce-mod-m` (GF256, concrete F₂) are line-for-line the same left-Horner
-- fold, differing only in four parameters.  `fold-cong` proves
-- parameter-equality ⟹ fold-equality once; the whole seam then collapses to
-- the byte identity `ytime ≡ xtime`, which lifts from the ELEMENT bridge
-- `ring-+ ≡ +` / `ring-* ≡ ·` (the field reaches F₂ through a CommutativeRing
-- record, so these are propositional, not definitional — but they close by a
-- 4-way case-split).  Everything here is structural: peak RSS ≈ 0.1 GiB.
------------------------------------------------------------------------
module Substrate.Algebra.F2.GF256.HornerSeam where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; _·_)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; 𝟎ⱽ; _*ₛ_)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit using (m-lo)
open import Substrate.Algebra.F2.Polynomial using (_*P_; outer; anti-diag-sum) renaming (pad-end to pad-c)
open import Substrate.Algebra.F2.GF256.Xtime using (xtime)
open import Substrate.Algebra.F2.GF256.Reduce using (reduce-mod-m)
open import Substrate.Algebra.F2.GF256.Mul using (gmul)
import Substrate.Algebra.Polynomial.Graded.Mod as Mod
import Substrate.Algebra.Polynomial.Graded.Quotient as Quot
open Mod.Over F₂-CommRing 7 m-lo
  using (ytime; reduce-mod-f; _+P_; _·c_; x-shift; shift-to-suc-on-left; pad-end)
  renaming (_+_ to _+r_; _*_ to _·r_; outer to outer-g; anti-diag-sum to adg-g; _*P_ to _*Pg_)
open Quot.Over F₂-CommRing 7 m-lo using (_*Q_)

------------------------------------------------------------------------
-- The element bridge: the field's CommutativeRing-projected ops are F₂'s.

+e : (a b : F₂) → (a +r b) ≡ (a + b)
+e 𝟘 𝟘 = refl
+e 𝟘 𝟙 = refl
+e 𝟙 𝟘 = refl
+e 𝟙 𝟙 = refl

·e : (a b : F₂) → (a ·r b) ≡ (a · b)
·e 𝟘 𝟘 = refl
·e 𝟘 𝟙 = refl
·e 𝟙 𝟘 = refl
·e 𝟙 𝟙 = refl

-- lifted to vectors (the graded +P / ·c are the vector +ⱽ / *ₛ).
+P≡+ⱽ : ∀ {n} (u v : Vec F₂ n) → u +P v ≡ u +ⱽ v
+P≡+ⱽ []      []      = refl
+P≡+ⱽ (a ∷ u) (b ∷ v) = cong₂ _∷_ (+e a b) (+P≡+ⱽ u v)

·c≡*ₛ : ∀ {n} (c : F₂) (v : Vec F₂ n) → c ·c v ≡ c *ₛ v
·c≡*ₛ c []      = refl
·c≡*ₛ c (a ∷ v) = cong₂ _∷_ (·e c a) (·c≡*ₛ c v)

------------------------------------------------------------------------
-- The one irreducible obligation: the ·x kernels agree on a byte.
-- After the 8-bit match, 𝟘∷vinit r = 𝟘∷b0..b6 and vlast r = b7 by computation,
-- so only the +P→+ⱽ and ·c→*ₛ rewrites remain.

ytime-is-xtime : (r : Vector 8) → ytime r ≡ xtime r
ytime-is-xtime (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ b7 ∷ []) =
  trans (+P≡+ⱽ (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ []) (b7 ·c m-lo))
        (cong (_+ⱽ_ (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ [])) (·c≡*ₛ b7 m-lo))

------------------------------------------------------------------------
-- The shared shape and its congruence (the induction, proved once).

fold : {C : Set} (z : C) (inj : F₂ → C) (add : C → C → C) (kx : C → C)
     → ∀ {n} → Vec F₂ n → C
fold z inj add kx []      = z
fold z inj add kx (a ∷ q) = add (inj a) (kx (fold z inj add kx q))

fold-cong : {C : Set} {z₁ z₂ : C} {i₁ i₂ : F₂ → C} {p₁ p₂ : C → C → C} {k₁ k₂ : C → C}
          → z₁ ≡ z₂ → (∀ a → i₁ a ≡ i₂ a) → (∀ u v → p₁ u v ≡ p₂ u v) → (∀ c → k₁ c ≡ k₂ c)
          → ∀ {n} (v : Vec F₂ n) → fold z₁ i₁ p₁ k₁ v ≡ fold z₂ i₂ p₂ k₂ v
fold-cong ez ei ep ek []      = ez
fold-cong {i₂ = i₂} {p₁ = p₁} {k₁ = k₁} ez ei ep ek (a ∷ q) =
  trans (cong₂ p₁ (ei a) (cong k₁ (fold-cong ez ei ep ek q)))
        (trans (cong (p₁ (i₂ a)) (ek _)) (ep (i₂ a) _))

-- the two reductions ARE this fold (refl-inductions over their own clauses).
reduce-mod-f-fold : ∀ {n} (v : Vec F₂ n)
  → reduce-mod-f v ≡ fold (replicate 8 𝟘) (λ a → a ∷ replicate 7 𝟘) _+P_ ytime v
reduce-mod-f-fold []      = refl
reduce-mod-f-fold (a ∷ q) = cong (λ z → (a ∷ replicate 7 𝟘) +P ytime z) (reduce-mod-f-fold q)

reduce-mod-m-fold : ∀ {n} (v : Vec F₂ n)
  → reduce-mod-m v ≡ fold 𝟎ⱽ (λ a → a ∷ 𝟎ⱽ) _+ⱽ_ xtime v
reduce-mod-m-fold []      = refl
reduce-mod-m-fold (a ∷ q) = cong (λ z → (a ∷ 𝟎ⱽ) +ⱽ xtime z) (reduce-mod-m-fold q)

------------------------------------------------------------------------
-- ★ THE SEAM CLOSED at the reduction level: the field's reduce and GF256's
-- are one function.  (Each boring parameter-equality is `refl`; the content
-- is `ytime-is-xtime`.)

reduce-eq : ∀ {n} (v : Vec F₂ n) → reduce-mod-f v ≡ reduce-mod-m v
reduce-eq v =
  trans (reduce-mod-f-fold v)
  (trans (fold-cong refl (λ a → refl) +P≡+ⱽ ytime-is-xtime v)
         (sym (reduce-mod-m-fold v)))

------------------------------------------------------------------------
-- Lifting the bridge through the convolution.  `outer` and `anti-diag-sum`
-- are line-for-line identical in the two modules; only `·c` and `+P` differ,
-- so `·c≡*ₛ` and `+P≡+ⱽ` carry through (the x-shift / pad helpers are op-free).

outer-eq : ∀ {n m} (p : Vec F₂ n) (q : Vec F₂ m) → outer-g p q ≡ outer p q
outer-eq []      q = refl
outer-eq (a ∷ p) q = cong₂ _∷_ (·c≡*ₛ a q) (outer-eq p q)

-- pad-end is recursive (the one helper not op-free-in-one-step); bridge by induction.
pad-eq : ∀ {n} (k : ℕ) (v : Vec F₂ n) → pad-end k v ≡ pad-c k v
pad-eq k []      = refl
pad-eq k (x ∷ v) = cong (x ∷_) (pad-eq k v)

adg-eq : ∀ {n m} (rows : Vec (Vec F₂ m) n) → adg-g rows ≡ anti-diag-sum rows
adg-eq []           = refl
adg-eq (row ∷ rows) =
  let A = shift-to-suc-on-left (pad-end _ row) in
  trans (+P≡+ⱽ A (x-shift (adg-g rows)))
        (cong₂ _+ⱽ_ (cong shift-to-suc-on-left (pad-eq _ row))
                     (cong x-shift (adg-eq rows)))

*P-eq : ∀ {n m} (p : Vec F₂ n) (q : Vec F₂ m) → p *Pg q ≡ p *P q
*P-eq p q = trans (cong adg-g (outer-eq p q)) (adg-eq (outer p q))

------------------------------------------------------------------------
-- ★★ THE SEAM CLOSED: the field's multiply (SubBytes) IS GF256's (MixColumns).
*Q-is-gmul : (a b : Vector 8) → a *Q b ≡ gmul a b
*Q-is-gmul a b = trans (cong reduce-mod-f (*P-eq a b)) (reduce-eq (a *P b))
