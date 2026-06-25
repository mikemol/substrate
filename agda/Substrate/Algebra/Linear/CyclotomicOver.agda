------------------------------------------------------------------------
-- Substrate.Algebra.Linear.CyclotomicOver
--
-- Ⓕ.tower-abstract — the cyclotomic OPERATOR Φ_p(T) = Σ_{i<p} Tⁱ and its
-- factor / orbit-fixed identities, PARAMETRIC over any law-bearing linear
-- algebra (the flat-bundle pattern, like Algebra.Polynomial.Cyclotomic.Over).
--
-- SETOID-PARAMETRIC. The equality `_≈_` is a PARAMETER, not fixed to `_≡_`:
--   • F₂ instantiates with ≈ = ≡ (decidable, char 2): a degenerate setoid.
--   • ℚ instantiates with ≈ = ≈ℚ (the cross-multiplication setoid the whole
--     continued-fraction substrate runs on; ℚ's ≡-laws are uninhabitable —
--     `Q.AsField.ℚ-Field-Obligation` bundles the syntactically-false inverse —
--     so the ℚ carrier is genuinely a setoid, NOT ≡).
-- The equality-regime IS the carrier axis: this is the F₂↔ℚ difference the
-- CrossMul bridge formalizes, lifted into the abstraction's own parameter.
--
-- `Linear` is opaque here (no constructor), so the linear-map operations are
-- taken as parameters WITH their characterizing apply-equations (over ≈) —
-- exactly the interface a concrete instance exposes. `apply-cong` (each map
-- respects ≈) replaces `cong (apply L)`; `+ⱽ-cong` replaces `cong₂ _+ⱽ_`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc)

module Substrate.Algebra.Linear.CyclotomicOver
  {Vector : ℕ → Set} {Linear : ℕ → ℕ → Set}
  (apply : ∀ {n m} → Linear n m → Vector n → Vector m)
  (_≈_ : ∀ {n} → Vector n → Vector n → Set)
  (≈-refl  : ∀ {n} {v : Vector n} → v ≈ v)
  (≈-sym   : ∀ {n} {u v : Vector n} → u ≈ v → v ≈ u)
  (≈-trans : ∀ {n} {u v w : Vector n} → u ≈ v → v ≈ w → u ≈ w)
  (_+ⱽ_ : ∀ {n} → Vector n → Vector n → Vector n)
  (𝟎ⱽ : ∀ {n} → Vector n)
  (+ⱽ-cong : ∀ {n} {a a′ b b′ : Vector n} → a ≈ a′ → b ≈ b′ → (a +ⱽ b) ≈ (a′ +ⱽ b′))
  (+ⱽ-assoc     : ∀ {n} (u v w : Vector n) → ((u +ⱽ v) +ⱽ w) ≈ (u +ⱽ (v +ⱽ w)))
  (+ⱽ-comm      : ∀ {n} (u v : Vector n) → (u +ⱽ v) ≈ (v +ⱽ u))
  (+ⱽ-identityˡ : ∀ {n} (v : Vector n) → (𝟎ⱽ +ⱽ v) ≈ v)
  (+ⱽ-identityʳ : ∀ {n} (v : Vector n) → (v +ⱽ 𝟎ⱽ) ≈ v)
  (idL : ∀ {n} → Linear n n)
  (apply-idL : ∀ {n} (v : Vector n) → apply idL v ≈ v)
  (apply-cong : ∀ {n m} (L : Linear n m) {a b : Vector n} → a ≈ b → apply L a ≈ apply L b)
  (_∘L_ : ∀ {n m k} → Linear m k → Linear n m → Linear n k)
  (apply-∘L : ∀ {n m k} (L : Linear m k) (M : Linear n m) (v : Vector n) →
              apply (L ∘L M) v ≈ apply L (apply M v))
  (_+L_ : ∀ {n m} → Linear n m → Linear n m → Linear n m)
  (apply-+L : ∀ {n m} (L M : Linear n m) (v : Vector n) →
              apply (L +L M) v ≈ (apply L v +ⱽ apply M v))
  (𝟘L : ∀ {n m} → Linear n m)
  (apply-𝟘L : ∀ {n m} (v : Vector n) → apply (𝟘L {n} {m}) v ≈ 𝟎ⱽ)
  (preserves-+ : ∀ {n m} (L : Linear n m) (u v : Vector n) →
                 apply L (u +ⱽ v) ≈ (apply L u +ⱽ apply L v))
  (preserves-𝟎 : ∀ {n m} (L : Linear n m) → apply L 𝟎ⱽ ≈ 𝟎ⱽ)
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
                apply (powL (suc i) T) v ≈ apply T (apply (powL i T) v)
apply-pow-suc T i v = apply-∘L T (powL i T) v

apply-geom-suc : ∀ {n} (T : Linear n n) (k : ℕ) (v : Vector n) →
                 apply (geomSumL T (suc k)) v ≈ (apply (geomSumL T k) v +ⱽ apply (powL k T) v)
apply-geom-suc T k v = apply-+L (geomSumL T k) (powL k T) v

------------------------------------------------------------------------
-- The factor identity (apply-form): 𝟙 + T·Φ_p ≈ Φ_p + Tᵖ.
------------------------------------------------------------------------

ΦL-factor : ∀ {n} (T : Linear n n) (p : ℕ) (v : Vector n) →
            (v +ⱽ apply T (apply (geomSumL T p) v))
              ≈ (apply (geomSumL T p) v +ⱽ apply (powL p T) v)
ΦL-factor T zero v =
  ≈-trans (≈-trans (+ⱽ-cong ≈-refl (≈-trans (apply-cong T (apply-𝟘L v)) (preserves-𝟎 T)))
                   (+ⱽ-identityʳ v))
          (≈-sym (≈-trans (+ⱽ-cong (apply-𝟘L v) (apply-idL v)) (+ⱽ-identityˡ v)))
ΦL-factor T (suc k) v =
  ≈-trans (+ⱽ-cong ≈-refl
                   (≈-trans (apply-cong T (apply-geom-suc T k v))
                            (preserves-+ T (apply (geomSumL T k) v) (apply (powL k T) v))))
  (≈-trans (≈-sym (+ⱽ-assoc v (apply T (apply (geomSumL T k) v)) (apply T (apply (powL k T) v))))
  (≈-trans (+ⱽ-cong (ΦL-factor T k v) ≈-refl)
           (+ⱽ-cong (≈-sym (apply-geom-suc T k v)) (≈-sym (apply-pow-suc T k v)))))

------------------------------------------------------------------------
-- Orbit specialization: on a p-orbit (Tᵖ v ≈ v), every Φ_p(T)-image is
-- T-fixed (the eigenvalue-1 / kernel relation).
--
-- This is the ONE place that needs CANCELLATION (v +ⱽ a ≈ v +ⱽ b → a ≈ b),
-- so it is taken as an EXPLICIT argument rather than a module parameter:
-- the cyclotomic core (ΦL, ΦL-factor) is carrier-general, while cancellation
-- is carrier-specific — F₂ has it via self-inverse, ℚ via additive inverse
-- (over ≈ℚ). Exposing it here keeps the core instantiable regardless.
------------------------------------------------------------------------

ΦL-orbit-fixed : (+ⱽ-cancelˡ : ∀ {n} (v a b : Vector n) → (v +ⱽ a) ≈ (v +ⱽ b) → a ≈ b) →
                 ∀ {n} (T : Linear n n) (p : ℕ) (v : Vector n) →
                 apply (powL p T) v ≈ v →
                 apply T (apply (ΦL T p) v) ≈ apply (ΦL T p) v
ΦL-orbit-fixed +ⱽ-cancelˡ T p v hyp =
  +ⱽ-cancelˡ v tΦv Φv (≈-trans eq (+ⱽ-comm Φv v))
  where
    Φv  = apply (ΦL T p) v
    tΦv = apply T Φv
    eq : (v +ⱽ tΦv) ≈ (Φv +ⱽ v)
    eq = ≈-trans (ΦL-factor T p v) (+ⱽ-cong ≈-refl hyp)
