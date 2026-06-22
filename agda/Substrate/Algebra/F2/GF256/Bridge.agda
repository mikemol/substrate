{-# OPTIONS --safe --without-K #-}
------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Bridge
--
-- The REDUCE-LEVEL half of the field/GF256 seam — the part that needs neither
-- `gmul` nor `_*Q_`, so it can live BELOW `Mul`/`Idempotent` and be imported by
-- anything in GF256 that wants to transport a graded fact to the concrete F₂
-- world.  It bottoms out in the element bridge `ring-+ ≡ +` / `ring-* ≡ ·`
-- (4-way case-split), lifted through `+P`/`·c`, the `ytime`/`xtime` kernel, the
-- Horner fold (`fold-cong`), and the `outer`/`anti-diag-sum` convolution:
--   reduce-eq : reduce-mod-f ≡ reduce-mod-m      (the two reductions are one)
--   *P-eq     : _*Pg_ ≡ _*P_                     (the two multiplies are one)
-- `HornerSeam` caps this with `*Q ≡ gmul`; this module is what other transports
-- (e.g. the `hsum` family) reuse without the circularity through `Mul`.
-- Structural throughout; peak RSS ≈ 0.1 GiB.
------------------------------------------------------------------------
module Substrate.Algebra.F2.GF256.Bridge where

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
open import Substrate.Algebra.F2.GF256.Expand using (hsum)
import Substrate.Algebra.Polynomial.Graded.Mod as Mod
open Mod.Over F₂-CommRing 7 m-lo
  using (ytime; reduce-mod-f; _+P_; _·c_; x-shift; shift-to-suc-on-left; pad-end)
  renaming (_+_ to _+r_; _*_ to _·r_; outer to outer-g; anti-diag-sum to adg-g; _*P_ to _*Pg_; hsum to hsum-g)

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

ytime-is-xtime : (r : Vector 8) → ytime r ≡ xtime r
ytime-is-xtime (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ b7 ∷ []) =
  trans (+P≡+ⱽ (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ []) (b7 ·c m-lo))
        (cong (_+ⱽ_ (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ [])) (·c≡*ₛ b7 m-lo))

------------------------------------------------------------------------
-- ⋈-CONG.  The generic Vec F₂ fold and its congruence — proved once, for an
-- ARBITRARY result type R and an ARBITRARY relation _≈_ on it.  `fold` (reduce)
-- and `thread` (hsum) below are the SAME `gfold`, into C and into C→C; their
-- congruences are this ONE `gfold-cong`, instantiated at _≡_ and at pointwise-≡.
-- This is the schema ⋈-STRUCT generalizes: a graded↔F₂ transport IS a `gfold-cong`
-- fed the element bridge.  (The Fin-indexed `sum-cong` in Idempotent is the same
-- idea over a different functor — a container-fold would absorb it too; → STRUCT.)

gfold : {R : Set} (e : R) (c : F₂ → R → R) → ∀ {n} → Vec F₂ n → R
gfold e c []      = e
gfold e c (a ∷ q) = c a (gfold e c q)

gfold-cong : {R : Set} (_≈_ : R → R → Set) {e₁ e₂ : R} {c₁ c₂ : F₂ → R → R}
           → e₁ ≈ e₂ → (∀ a {r₁ r₂} → r₁ ≈ r₂ → c₁ a r₁ ≈ c₂ a r₂)
           → ∀ {n} (v : Vec F₂ n) → gfold e₁ c₁ v ≈ gfold e₂ c₂ v
gfold-cong _≈_ ee ec []      = ee
gfold-cong _≈_ ee ec (a ∷ q) = ec a (gfold-cong _≈_ ee ec q)

-- reduce's fold: the kernel `kx` lands on the RESULT.  fold = gfold into C.
fold : {C : Set} (z : C) (inj : F₂ → C) (add : C → C → C) (kx : C → C)
     → ∀ {n} → Vec F₂ n → C
fold z inj add kx = gfold z (λ a r → add (inj a) (kx r))

fold-cong : {C : Set} {z₁ z₂ : C} {i₁ i₂ : F₂ → C} {p₁ p₂ : C → C → C} {k₁ k₂ : C → C}
          → z₁ ≡ z₂ → (∀ a → i₁ a ≡ i₂ a) → (∀ u v → p₁ u v ≡ p₂ u v) → (∀ c → k₁ c ≡ k₂ c)
          → ∀ {n} (v : Vec F₂ n) → fold z₁ i₁ p₁ k₁ v ≡ fold z₂ i₂ p₂ k₂ v
fold-cong {i₂ = i₂} {p₁ = p₁} {k₁ = k₁} ez ei ep ek =
  gfold-cong _≡_ ez (λ a er → trans (cong₂ p₁ (ei a) (trans (cong k₁ er) (ek _))) (ep (i₂ a) _))

-- the two reductions ARE this fold (refl-inductions over their own clauses).
reduce-mod-f-fold : ∀ {n} (v : Vec F₂ n)
  → reduce-mod-f v ≡ fold (replicate 8 𝟘) (λ a → a ∷ replicate 7 𝟘) _+P_ ytime v
reduce-mod-f-fold []      = refl
reduce-mod-f-fold (a ∷ q) = cong (λ z → (a ∷ replicate 7 𝟘) +P ytime z) (reduce-mod-f-fold q)

reduce-mod-m-fold : ∀ {n} (v : Vec F₂ n)
  → reduce-mod-m v ≡ fold 𝟎ⱽ (λ a → a ∷ 𝟎ⱽ) _+ⱽ_ xtime v
reduce-mod-m-fold []      = refl
reduce-mod-m-fold (a ∷ q) = cong (λ z → (a ∷ 𝟎ⱽ) +ⱽ xtime z) (reduce-mod-m-fold q)

-- ★ the two reductions are one function.
reduce-eq : ∀ {n} (v : Vec F₂ n) → reduce-mod-f v ≡ reduce-mod-m v
reduce-eq v =
  trans (reduce-mod-f-fold v)
  (trans (fold-cong refl (λ a → refl) +P≡+ⱽ ytime-is-xtime v)
         (sym (reduce-mod-m-fold v)))

------------------------------------------------------------------------
-- Lifting the bridge through the convolution (outer / anti-diag-sum, identical
-- up to ·c/+P and the op-free helpers).

outer-eq : ∀ {n m} (p : Vec F₂ n) (q : Vec F₂ m) → outer-g p q ≡ outer p q
outer-eq []      q = refl
outer-eq (a ∷ p) q = cong₂ _∷_ (·c≡*ₛ a q) (outer-eq p q)

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

-- ★ the two multiplies are one.
*P-eq : ∀ {n m} (p : Vec F₂ n) (q : Vec F₂ m) → p *Pg q ≡ p *P q
*P-eq p q = trans (cong adg-g (outer-eq p q)) (adg-eq (outer p q))

------------------------------------------------------------------------
-- hsum's fold: the kernel `adv` lands on the THREADED ARGUMENT.  `hsum (a∷p) r =
-- add (scale a r) (hsum p (adv r))` is the SAME `gfold` — but into C→C, the result
-- being a function of the threaded `r`.  So `thread`'s congruence is `gfold-cong`
-- at POINTWISE-≡ (no funext needed: the relation is pointwise by construction).
-- `reduce` and `hsum` differ only in whether the result type is C or C→C — that is
-- the entire content of "the second fold scheme", named by ⋈-CONG.

thread : {C : Set} (z : C) (scale : F₂ → C → C) (add : C → C → C) (adv : C → C)
       → ∀ {n} → Vec F₂ n → C → C
thread z scale add adv = gfold (λ _ → z) (λ a rec r → add (scale a r) (rec (adv r)))

thread-cong : {C : Set} {z₁ z₂ : C} {s₁ s₂ : F₂ → C → C} {p₁ p₂ : C → C → C} {a₁ a₂ : C → C}
            → z₁ ≡ z₂ → (∀ x r → s₁ x r ≡ s₂ x r) → (∀ u v → p₁ u v ≡ p₂ u v) → (∀ r → a₁ r ≡ a₂ r)
            → ∀ {n} (v : Vec F₂ n) (r : C) → thread z₁ s₁ p₁ a₁ v r ≡ thread z₂ s₂ p₂ a₂ v r
thread-cong {s₂ = s₂} {p₁ = p₁} {a₁ = a₁} ez es ep ea =
  gfold-cong (λ f g → ∀ r → f r ≡ g r) (λ _ → ez)
    (λ x {_} {rec₂} erec r →
       trans (cong₂ p₁ (es x r) (trans (erec (a₁ r)) (cong rec₂ (ea r)))) (ep (s₂ x r) _))

-- the two hsums ARE this thread (refl-inductions over their own clauses).
hsum-g-thread : ∀ {n} (p : Vec F₂ n) (r : Vector 8) → hsum-g p r ≡ thread (replicate 8 𝟘) _·c_ _+P_ ytime p r
hsum-g-thread []      r = refl
hsum-g-thread (a ∷ p) r = cong ((a ·c r) +P_) (hsum-g-thread p (ytime r))

hsum-m-thread : ∀ {n} (p : Vec F₂ n) (r : Vector 8) → hsum p r ≡ thread 𝟎ⱽ _*ₛ_ _+ⱽ_ xtime p r
hsum-m-thread []      r = refl
hsum-m-thread (a ∷ p) r = cong ((a *ₛ r) +ⱽ_) (hsum-m-thread p (xtime r))

-- ★ the two hsums are one — lifted from thread-cong, no new content.
hsum-bridge : ∀ {n} (p : Vec F₂ n) (r : Vector 8) → hsum-g p r ≡ hsum p r
hsum-bridge p r =
  trans (hsum-g-thread p r)
  (trans (thread-cong refl ·c≡*ₛ +P≡+ⱽ ytime-is-xtime p r)
         (sym (hsum-m-thread p r)))
