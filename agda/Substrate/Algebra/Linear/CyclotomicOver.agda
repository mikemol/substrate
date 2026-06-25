------------------------------------------------------------------------
-- Substrate.Algebra.Linear.CyclotomicOver
--
-- Ⓕ.tower-abstract — the cyclotomic OPERATOR Φ_p(T) = Σ_{i<p} Tⁱ and its
-- factor / orbit-fixed identities, PARAMETRIC over any law-bearing linear
-- algebra (the flat-bundle pattern, like Algebra.Polynomial.Cyclotomic.Over).
--
-- F₂ and ℚ are two CARRIERS of one cyclotomic operator: each supplies the
-- Vector comm-monoid + the linear-map ops (idL/∘L/+L/𝟘L) with their
-- apply-equations + linearity, and instantiates this module to get ΦL,
-- ΦL-factor, ΦL-orbit-fixed for free. (Algebra.F2.Linear.Cyclotomic becomes
-- the F₂ instance; Algebra.Q.Linear the ℚ instance; CrossMul the bridge.)
--
-- `Linear` is opaque here (no constructor), so the linear-map operations are
-- taken as parameters WITH their characterizing apply-equations — exactly the
-- interface a concrete instance exposes (refl in F₂). Statements are in
-- apply-form so they read off the apply-equations, no record-reduction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)

module Substrate.Algebra.Linear.CyclotomicOver
  {Vector : ℕ → Set} {Linear : ℕ → ℕ → Set}
  (apply : ∀ {n m} → Linear n m → Vector n → Vector m)
  (_+ⱽ_ : ∀ {n} → Vector n → Vector n → Vector n)
  (𝟎ⱽ : ∀ {n} → Vector n)
  (+ⱽ-assoc     : ∀ {n} (u v w : Vector n) → ((u +ⱽ v) +ⱽ w) ≡ (u +ⱽ (v +ⱽ w)))
  (+ⱽ-comm      : ∀ {n} (u v : Vector n) → (u +ⱽ v) ≡ (v +ⱽ u))
  (+ⱽ-identityˡ : ∀ {n} (v : Vector n) → (𝟎ⱽ +ⱽ v) ≡ v)
  (+ⱽ-identityʳ : ∀ {n} (v : Vector n) → (v +ⱽ 𝟎ⱽ) ≡ v)
  (+ⱽ-selfinv   : ∀ {n} (v : Vector n) → (v +ⱽ v) ≡ 𝟎ⱽ)
  (idL : ∀ {n} → Linear n n)
  (apply-idL : ∀ {n} (v : Vector n) → apply idL v ≡ v)
  (_∘L_ : ∀ {n m k} → Linear m k → Linear n m → Linear n k)
  (apply-∘L : ∀ {n m k} (L : Linear m k) (M : Linear n m) (v : Vector n) →
              apply (L ∘L M) v ≡ apply L (apply M v))
  (_+L_ : ∀ {n m} → Linear n m → Linear n m → Linear n m)
  (apply-+L : ∀ {n m} (L M : Linear n m) (v : Vector n) →
              apply (L +L M) v ≡ (apply L v +ⱽ apply M v))
  (𝟘L : ∀ {n m} → Linear n m)
  (apply-𝟘L : ∀ {n m} (v : Vector n) → apply (𝟘L {n} {m}) v ≡ 𝟎ⱽ)
  (preserves-+ : ∀ {n m} (L : Linear n m) (u v : Vector n) →
                 apply L (u +ⱽ v) ≡ (apply L u +ⱽ apply L v))
  (preserves-𝟎 : ∀ {n m} (L : Linear n m) → apply L 𝟎ⱽ ≡ 𝟎ⱽ)
  where

------------------------------------------------------------------------
-- Powers, geometric sum, the cyclotomic operator Φ_p(T) = Σ_{i<p} Tⁱ.
------------------------------------------------------------------------

powL : ∀ {n} → ℕ → Linear n n → Linear n n
powL zero    T = idL
powL (suc i) T = T ∘L powL i T

geomSumL : ∀ {n} → Linear n n → ℕ → Linear n n
geomSumL T zero    = 𝟘L
geomSumL T (suc k) = geomSumL T k +L powL k T

ΦL : ∀ {n} → Linear n n → ℕ → Linear n n
ΦL T p = geomSumL T p

apply-pow-suc : ∀ {n} (T : Linear n n) (i : ℕ) (v : Vector n) →
                apply (powL (suc i) T) v ≡ apply T (apply (powL i T) v)
apply-pow-suc T i v = apply-∘L T (powL i T) v

apply-geom-suc : ∀ {n} (T : Linear n n) (k : ℕ) (v : Vector n) →
                 apply (geomSumL T (suc k)) v ≡ (apply (geomSumL T k) v +ⱽ apply (powL k T) v)
apply-geom-suc T k v = apply-+L (geomSumL T k) (powL k T) v

------------------------------------------------------------------------
-- The factor identity (apply-form): 𝟙 + T·Φ_p ≡ Φ_p + Tᵖ.
------------------------------------------------------------------------

ΦL-factor : ∀ {n} (T : Linear n n) (p : ℕ) (v : Vector n) →
            (v +ⱽ apply T (apply (geomSumL T p) v))
              ≡ (apply (geomSumL T p) v +ⱽ apply (powL p T) v)
ΦL-factor T zero v =
  trans (trans (cong (v +ⱽ_) (trans (cong (apply T) (apply-𝟘L v)) (preserves-𝟎 T)))
               (+ⱽ-identityʳ v))
        (sym (trans (cong₂ _+ⱽ_ (apply-𝟘L v) (apply-idL v)) (+ⱽ-identityˡ v)))
ΦL-factor T (suc k) v =
  trans (cong (v +ⱽ_)
              (trans (cong (apply T) (apply-geom-suc T k v))
                     (preserves-+ T (apply (geomSumL T k) v) (apply (powL k T) v))))
  (trans (sym (+ⱽ-assoc v (apply T (apply (geomSumL T k) v)) (apply T (apply (powL k T) v))))
  (trans (cong (_+ⱽ apply T (apply (powL k T) v)) (ΦL-factor T k v))
         (cong₂ _+ⱽ_ (sym (apply-geom-suc T k v)) (sym (apply-pow-suc T k v)))))

------------------------------------------------------------------------
-- Orbit specialization: on a p-orbit (Tᵖ v ≡ v), every Φ_p(T)-image is
-- T-fixed (the eigenvalue-1 / kernel relation).
------------------------------------------------------------------------

ΦL-orbit-fixed : ∀ {n} (T : Linear n n) (p : ℕ) (v : Vector n) →
                 apply (powL p T) v ≡ v →
                 apply T (apply (ΦL T p) v) ≡ apply (ΦL T p) v
ΦL-orbit-fixed T p v hyp =
  trans (sym (+ⱽ-identityˡ tΦv))
  (trans (cong (_+ⱽ tΦv) (sym (+ⱽ-selfinv v)))
  (trans (+ⱽ-assoc v v tΦv)
  (trans (cong (v +ⱽ_) eq)
  (trans (cong (v +ⱽ_) (+ⱽ-comm Φv v))
  (trans (sym (+ⱽ-assoc v v Φv))
  (trans (cong (_+ⱽ Φv) (+ⱽ-selfinv v))
         (+ⱽ-identityˡ Φv)))))))
  where
    Φv  = apply (ΦL T p) v
    tΦv = apply T Φv
    eq : (v +ⱽ tΦv) ≡ (Φv +ⱽ v)
    eq = trans (ΦL-factor T p v) (cong (Φv +ⱽ_) hyp)
