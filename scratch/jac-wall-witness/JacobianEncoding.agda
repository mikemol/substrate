{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncoding — ⟡jac-encoding-bridge (shared eval).
--
-- The evaluator `evalℚ x y z : MPoly → ℚ` and its `+P`/`*P` → `+ℚ`/`*ℚ`
-- HOMOMORPHISM machinery, used by `JacobianEncodingBridge` to identify HALF A's
-- curried-ℚ `C.fᵢ` with HALF B's `MPoly` `R.fᵢ`.
--
-- ⚑⚑ TWO REPO-SPECIFIC OBSTRUCTIONS, and the two devices that clear them — this
-- module is half of the ⟡jac-encoding-bridge ROSETTA STONE.
--
-- (1) `_≈ℚ_` is a TRANSPARENT cross-multiplication `≡` and `ℚ` is an eta-record,
--     so `_·_`/`_⊹_` (= `*ℚ`/`+ℚ`) REDUCE to `mkℚ …`. A nested `≈ℚ-trans` then
--     has to recover its middle endpoint through `num`/`den-1`, which are not
--     injective — so Agda leaves the endpoint an unsolved meta (even the trivial
--     `assoc-lll` fails this way). The repo's own ℚ laws (Q/Properties/Field)
--     dodge it by pattern-matching `(mkℚ n d)` and reasoning at the ℤ level, a
--     style infeasible for a degree-9 polynomial. The DEVICE here: a LOCAL
--     `_IsRelatedTo_` data wrapper (NOT an stdlib import) that carries the
--     endpoints as DATA INDICES, so `_≈⟨_⟩_` recovers them rigidly. (Route A of
--     the Rosetta Stone spells the same endpoints out explicitly instead.)
-- (2) `evalℚ (concrete R.fᵢ)` would eagerly DISTRIBUTE the polynomial and blow
--     ℚ-arithmetic past the ~1 GB full-build heap cap. The DEVICE: `evalℚ`/
--     `evalT`/`monoval` are `opaque`, so `evalℚ R.fᵢ` stays a rigid, un-distributed
--     term outside this block; the hom lemmas unfold it only where they must.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncoding where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 1ℤ; -ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; 0ℚ; 1ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Neg using (-ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Embeddings using (ℤ→ℚ)
open import Substrate.Algebra.Q.Properties.Field
  using ( +ℚ-assoc; +ℚ-identityˡ; +ℚ-identityʳ
        ; *ℚ-comm; *ℚ-assoc; *ℚ-identityˡ; *ℚ-identityʳ
        ; zero-absorbˡ; zero-absorbʳ; distribˡ; distribʳ )
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong; *ℚ-cong)

import Substrate.Algebra.Z.JacobianResidue as R
open R using (Mono; Term; MPoly; mono; term; addM; mulT; scaleT; _*P_; _+P_)

------------------------------------------------------------------------
-- 0. Parse-friendly aliases + a LOCAL ≈ℚ equational-reasoning wrapper.
--    `_≈ℚ_` is a transparent (non-injective) equality, so a bare transitivity
--    combinator cannot recover its middle endpoints; the `_IsRelatedTo_` data
--    wrapper exposes them as data indices. (Local — not imported from anywhere.)
------------------------------------------------------------------------

infixl 25 _·_
infixl 24 _⊹_

_·_ : ℚ → ℚ → ℚ
_·_ = _*ℚ_

_⊹_ : ℚ → ℚ → ℚ
_⊹_ = _+ℚ_

infix  1 begin_
infixr 2 _≈⟨_⟩_
infix  3 _∎ℚ

data _IsRelatedTo_ (a b : ℚ) : Set where
  relTo : a ≈ℚ b → a IsRelatedTo b

begin_ : {a b : ℚ} → a IsRelatedTo b → a ≈ℚ b
begin relTo p = p

_≈⟨_⟩_ : (a : ℚ) {b c : ℚ} → a ≈ℚ b → b IsRelatedTo c → a IsRelatedTo c
a ≈⟨ p ⟩ relTo q = relTo (≈ℚ-trans p q)

_∎ℚ : (a : ℚ) → a IsRelatedTo a
a ∎ℚ = relTo (≈ℚ-refl a)

------------------------------------------------------------------------
-- 1. Generic ℚ rearrangements (from assoc/comm/cong).
------------------------------------------------------------------------

-- ((a·b)·c)·d ≈ a·(b·(c·d))
assoc-lll : (a b c d : ℚ) → ((a · b) · c) · d ≈ℚ a · (b · (c · d))
assoc-lll a b c d = begin
  ((a · b) · c) · d
    ≈⟨ *ℚ-assoc (a · b) c d ⟩
  (a · b) · (c · d)
    ≈⟨ *ℚ-assoc a b (c · d) ⟩
  a · (b · (c · d)) ∎ℚ

-- (a·b)·(c·d) ≈ (a·c)·(b·d)
swap4 : (a b c d : ℚ) → (a · b) · (c · d) ≈ℚ (a · c) · (b · d)
swap4 a b c d = begin
  (a · b) · (c · d)
    ≈⟨ *ℚ-assoc a b (c · d) ⟩
  a · (b · (c · d))
    ≈⟨ *ℚ-cong (≈ℚ-refl a) (≈ℚ-sym (*ℚ-assoc b c d)) ⟩
  a · ((b · c) · d)
    ≈⟨ *ℚ-cong (≈ℚ-refl a) (*ℚ-cong (*ℚ-comm b c) (≈ℚ-refl d)) ⟩
  a · ((c · b) · d)
    ≈⟨ *ℚ-cong (≈ℚ-refl a) (*ℚ-assoc c b d) ⟩
  a · (c · (b · d))
    ≈⟨ ≈ℚ-sym (*ℚ-assoc a c (b · d)) ⟩
  (a · c) · (b · d) ∎ℚ

-- (p·p')·((q·q')·(r·r')) ≈ (p·(q·r))·(p'·(q'·r'))
swap6 : (p p′ q q′ r r′ : ℚ)
      → (p · p′) · ((q · q′) · (r · r′))
      ≈ℚ (p · (q · r)) · (p′ · (q′ · r′))
swap6 p p′ q q′ r r′ = begin
  (p · p′) · ((q · q′) · (r · r′))
    ≈⟨ *ℚ-cong (≈ℚ-refl (p · p′)) (swap4 q q′ r r′) ⟩
  (p · p′) · ((q · r) · (q′ · r′))
    ≈⟨ swap4 p p′ (q · r) (q′ · r′) ⟩
  (p · (q · r)) · (p′ · (q′ · r′)) ∎ℚ

------------------------------------------------------------------------
-- 2. `powℚ` and its two ℤ/ℚ bridge lemmas.
------------------------------------------------------------------------

powℚ : ℚ → ℕ → ℚ
powℚ w zero    = 1ℚ
powℚ w (suc n) = w · powℚ w n

-- powℚ is a monoid hom (ℕ,+,0) → (ℚ, ·, 1ℚ), up to ≈ℚ.
powℚ-+ : (w : ℚ) (a b : ℕ) → powℚ w (a + b) ≈ℚ (powℚ w a) · (powℚ w b)
powℚ-+ w zero    b = ≈ℚ-sym (*ℚ-identityˡ (powℚ w b))
powℚ-+ w (suc a) b = begin
  w · powℚ w (a + b)
    ≈⟨ *ℚ-cong (≈ℚ-refl w) (powℚ-+ w a b) ⟩
  w · ((powℚ w a) · (powℚ w b))
    ≈⟨ ≈ℚ-sym (*ℚ-assoc w (powℚ w a) (powℚ w b)) ⟩
  (w · powℚ w a) · powℚ w b ∎ℚ

-- ℤ→ℚ is multiplicative (definitionally: both are mkℚ (k *ℤ l) 0).
ℤ→ℚ-*ℚ-hom : (k l : ℤ) → ℤ→ℚ (k *ℤ l) ≈ℚ (ℤ→ℚ k) · (ℤ→ℚ l)
ℤ→ℚ-*ℚ-hom k l = ≈ℚ-refl (ℤ→ℚ (k *ℤ l))

------------------------------------------------------------------------
-- 3. `-ℚ` pulls through `·` and respects `≈ℚ` (carries f₃'s negatives).
------------------------------------------------------------------------

-- (-ℚ a) · b ≈ -ℚ (a · b): same denominator, numerators by neg-*-left.
neg-·-l : (a b : ℚ) → (-ℚ a) · b ≈ℚ (-ℚ (a · b))
neg-·-l a b =
  cong (_*ℤ (+ suc (den-1 ((-ℚ a) · b)))) (neg-*-left (num a) (num b))

-- -ℚ is a congruence for ≈ℚ (same denominators; numerators via neg-*-left).
neg-cong : {a b : ℚ} → a ≈ℚ b → (-ℚ a) ≈ℚ (-ℚ b)
neg-cong {a} {b} H =
  trans (neg-*-left (num a) (+ suc (den-1 b)))
  (trans (cong -ℤ_ H)
         (sym (neg-*-left (num b) (+ suc (den-1 a)))))

------------------------------------------------------------------------
-- 4. The evaluator + its homomorphism lemmas, at a fixed rational point.
--    `evalℚ`/`evalT`/`monoval` are `opaque` (see header): rigid outside, so
--    `evalℚ R.fᵢ` never distributes and the ≈ℚ endpoints stay recoverable.
------------------------------------------------------------------------

module Ev (x y z : ℚ) where

  opaque

    monoval : Mono → ℚ
    monoval (mono a b c) = (powℚ x a) · ((powℚ y b) · (powℚ z c))

    evalT : Term → ℚ
    evalT (term m k) = (ℤ→ℚ k) · monoval m

    evalℚ : MPoly → ℚ
    evalℚ []      = 0ℚ
    evalℚ (t ∷ p) = evalT t ⊹ evalℚ p

    -- 4.2 Term-level product hom (monoval a monoid hom; ℤ→ℚ multiplicative).
    monoval-hom : (m n : Mono) → monoval (addM m n) ≈ℚ (monoval m) · (monoval n)
    monoval-hom (mono a b c) (mono a′ b′ c′) = begin
      (powℚ x (a + a′)) · ((powℚ y (b + b′)) · (powℚ z (c + c′)))
        ≈⟨ *ℚ-cong (powℚ-+ x a a′) (*ℚ-cong (powℚ-+ y b b′) (powℚ-+ z c c′)) ⟩
      ((powℚ x a) · (powℚ x a′)) · (((powℚ y b) · (powℚ y b′)) · ((powℚ z c) · (powℚ z c′)))
        ≈⟨ swap6 (powℚ x a) (powℚ x a′) (powℚ y b) (powℚ y b′) (powℚ z c) (powℚ z c′) ⟩
      ((powℚ x a) · ((powℚ y b) · (powℚ z c))) · ((powℚ x a′) · ((powℚ y b′) · (powℚ z c′))) ∎ℚ

    evalT-mulT : (t u : Term) → evalT (mulT t u) ≈ℚ (evalT t) · (evalT u)
    evalT-mulT (term m k) (term n l) = begin
      (ℤ→ℚ (k *ℤ l)) · monoval (addM m n)
        ≈⟨ *ℚ-cong (ℤ→ℚ-*ℚ-hom k l) (monoval-hom m n) ⟩
      ((ℤ→ℚ k) · (ℤ→ℚ l)) · ((monoval m) · (monoval n))
        ≈⟨ swap4 (ℤ→ℚ k) (ℤ→ℚ l) (monoval m) (monoval n) ⟩
      ((ℤ→ℚ k) · (monoval m)) · ((ℤ→ℚ l) · (monoval n)) ∎ℚ

    -- 4.3 The three structural homomorphism lemmas.
    evalℚ-++ : (p q : MPoly) → evalℚ (p ++ q) ≈ℚ (evalℚ p) ⊹ (evalℚ q)
    evalℚ-++ []      q = ≈ℚ-sym (+ℚ-identityˡ (evalℚ q))
    evalℚ-++ (t ∷ p) q = begin
      evalT t ⊹ evalℚ (p ++ q)
        ≈⟨ +ℚ-cong (≈ℚ-refl (evalT t)) (evalℚ-++ p q) ⟩
      evalT t ⊹ ((evalℚ p) ⊹ (evalℚ q))
        ≈⟨ ≈ℚ-sym (+ℚ-assoc (evalT t) (evalℚ p) (evalℚ q)) ⟩
      (evalT t ⊹ evalℚ p) ⊹ evalℚ q ∎ℚ

    evalℚ-scaleT : (t : Term) (p : MPoly) → evalℚ (scaleT t p) ≈ℚ (evalT t) · (evalℚ p)
    evalℚ-scaleT t []       = ≈ℚ-sym (zero-absorbʳ (evalT t))
    evalℚ-scaleT t (u ∷ us) = begin
      evalT (mulT t u) ⊹ evalℚ (scaleT t us)
        ≈⟨ +ℚ-cong (evalT-mulT t u) (evalℚ-scaleT t us) ⟩
      ((evalT t) · (evalT u)) ⊹ ((evalT t) · (evalℚ us))
        ≈⟨ ≈ℚ-sym (distribˡ (evalT t) (evalT u) (evalℚ us)) ⟩
      (evalT t) · (evalT u ⊹ evalℚ us) ∎ℚ

    evalℚ-*P : (p q : MPoly) → evalℚ (p *P q) ≈ℚ (evalℚ p) · (evalℚ q)
    evalℚ-*P []      q = ≈ℚ-sym (zero-absorbˡ (evalℚ q))
    evalℚ-*P (t ∷ p) q = begin
      evalℚ (scaleT t q ++ (p *P q))
        ≈⟨ evalℚ-++ (scaleT t q) (p *P q) ⟩
      (evalℚ (scaleT t q)) ⊹ (evalℚ (p *P q))
        ≈⟨ +ℚ-cong (evalℚ-scaleT t q) (evalℚ-*P p q) ⟩
      ((evalT t) · (evalℚ q)) ⊹ ((evalℚ p) · (evalℚ q))
        ≈⟨ ≈ℚ-sym (distribʳ (evalT t) (evalℚ p) (evalℚ q)) ⟩
      (evalT t ⊹ evalℚ p) · (evalℚ q) ∎ℚ

    -- Left-nested `*P` products, evaluated.
    eval-*P3 : (a b c : MPoly)
      → evalℚ (a *P b *P c) ≈ℚ ((evalℚ a) · (evalℚ b)) · (evalℚ c)
    eval-*P3 a b c = begin
      evalℚ (a *P b *P c)
        ≈⟨ evalℚ-*P (a *P b) c ⟩
      (evalℚ (a *P b)) · (evalℚ c)
        ≈⟨ *ℚ-cong (evalℚ-*P a b) (≈ℚ-refl (evalℚ c)) ⟩
      ((evalℚ a) · (evalℚ b)) · (evalℚ c) ∎ℚ

    eval-*P4 : (a b c d : MPoly)
      → evalℚ (a *P b *P c *P d) ≈ℚ (((evalℚ a) · (evalℚ b)) · (evalℚ c)) · (evalℚ d)
    eval-*P4 a b c d = begin
      evalℚ (a *P b *P c *P d)
        ≈⟨ evalℚ-*P (a *P b *P c) d ⟩
      (evalℚ (a *P b *P c)) · (evalℚ d)
        ≈⟨ *ℚ-cong (eval-*P3 a b c) (≈ℚ-refl (evalℚ d)) ⟩
      (((evalℚ a) · (evalℚ b)) · (evalℚ c)) · (evalℚ d) ∎ℚ

    eval-*P5 : (a b c d e : MPoly)
      → evalℚ (a *P b *P c *P d *P e)
      ≈ℚ ((((evalℚ a) · (evalℚ b)) · (evalℚ c)) · (evalℚ d)) · (evalℚ e)
    eval-*P5 a b c d e = begin
      evalℚ (a *P b *P c *P d *P e)
        ≈⟨ evalℚ-*P (a *P b *P c *P d) e ⟩
      (evalℚ (a *P b *P c *P d)) · (evalℚ e)
        ≈⟨ *ℚ-cong (eval-*P4 a b c d) (≈ℚ-refl (evalℚ e)) ⟩
      ((((evalℚ a) · (evalℚ b)) · (evalℚ c)) · (evalℚ d)) · (evalℚ e) ∎ℚ

    -- 4.4 Generator / coefficient values.
    evalℚ-single : (m : Mono) (k : ℤ) → evalℚ (term m k ∷ []) ≈ℚ (ℤ→ℚ k) · (monoval m)
    evalℚ-single m k = +ℚ-identityʳ ((ℤ→ℚ k) · monoval m)

    monoval-100 : monoval (mono 1 0 0) ≈ℚ x
    monoval-100 = begin
      (x · 1ℚ) · (1ℚ · 1ℚ)
        ≈⟨ *ℚ-cong (*ℚ-identityʳ x) (*ℚ-identityˡ 1ℚ) ⟩
      x · 1ℚ
        ≈⟨ *ℚ-identityʳ x ⟩
      x ∎ℚ

    monoval-010 : monoval (mono 0 1 0) ≈ℚ y
    monoval-010 = begin
      1ℚ · ((y · 1ℚ) · 1ℚ)
        ≈⟨ *ℚ-identityˡ ((y · 1ℚ) · 1ℚ) ⟩
      (y · 1ℚ) · 1ℚ
        ≈⟨ *ℚ-identityʳ (y · 1ℚ) ⟩
      y · 1ℚ
        ≈⟨ *ℚ-identityʳ y ⟩
      y ∎ℚ

    monoval-001 : monoval (mono 0 0 1) ≈ℚ z
    monoval-001 = begin
      1ℚ · (1ℚ · (z · 1ℚ))
        ≈⟨ *ℚ-identityˡ (1ℚ · (z · 1ℚ)) ⟩
      1ℚ · (z · 1ℚ)
        ≈⟨ *ℚ-identityˡ (z · 1ℚ) ⟩
      z · 1ℚ
        ≈⟨ *ℚ-identityʳ z ⟩
      z ∎ℚ

    monoval-000 : monoval (mono 0 0 0) ≈ℚ 1ℚ
    monoval-000 = begin
      1ℚ · (1ℚ · 1ℚ)
        ≈⟨ *ℚ-identityˡ (1ℚ · 1ℚ) ⟩
      1ℚ · 1ℚ
        ≈⟨ *ℚ-identityˡ 1ℚ ⟩
      1ℚ ∎ℚ

  -- 4.5 Generators / coefficients (outside `opaque`: they compose the opaque
  --     facts above, no unfolding of evalℚ needed).
  gen-X : evalℚ R.X ≈ℚ x
  gen-X = ≈ℚ-trans (evalℚ-single (mono 1 0 0) 1ℤ)
                   (≈ℚ-trans (*ℚ-identityˡ (monoval (mono 1 0 0))) monoval-100)

  gen-Y : evalℚ R.Y ≈ℚ y
  gen-Y = ≈ℚ-trans (evalℚ-single (mono 0 1 0) 1ℤ)
                   (≈ℚ-trans (*ℚ-identityˡ (monoval (mono 0 1 0))) monoval-010)

  gen-Z : evalℚ R.Z₁ ≈ℚ z
  gen-Z = ≈ℚ-trans (evalℚ-single (mono 0 0 1) 1ℤ)
                   (≈ℚ-trans (*ℚ-identityˡ (monoval (mono 0 0 1))) monoval-001)

  gen-𝟙 : evalℚ R.𝟙P ≈ℚ 1ℚ
  gen-𝟙 = ≈ℚ-trans (evalℚ-single (mono 0 0 0) 1ℤ)
                   (≈ℚ-trans (*ℚ-identityˡ (monoval (mono 0 0 0))) monoval-000)

  gen-kP : (k : ℤ) → evalℚ (R.kP k) ≈ℚ ℤ→ℚ k
  gen-kP k = begin
    evalℚ (R.kP k)
      ≈⟨ evalℚ-single (mono 0 0 0) k ⟩
    (ℤ→ℚ k) · monoval (mono 0 0 0)
      ≈⟨ *ℚ-cong (≈ℚ-refl (ℤ→ℚ k)) monoval-000 ⟩
    (ℤ→ℚ k) · 1ℚ
      ≈⟨ *ℚ-identityʳ (ℤ→ℚ k) ⟩
    ℤ→ℚ k ∎ℚ

  -- u = 1+xy , v = 4+3xy (matching C's where-bound locals).
  gen-u : evalℚ R.u ≈ℚ (1ℚ ⊹ (x · y))
  gen-u = begin
    evalℚ R.u
      ≈⟨ evalℚ-++ R.𝟙P (R.X *P R.Y) ⟩
    (evalℚ R.𝟙P) ⊹ (evalℚ (R.X *P R.Y))
      ≈⟨ +ℚ-cong gen-𝟙 (evalℚ-*P R.X R.Y) ⟩
    1ℚ ⊹ ((evalℚ R.X) · (evalℚ R.Y))
      ≈⟨ +ℚ-cong (≈ℚ-refl 1ℚ) (*ℚ-cong gen-X gen-Y) ⟩
    1ℚ ⊹ (x · y) ∎ℚ

  gen-v : evalℚ R.v ≈ℚ ((ℤ→ℚ (+ 4)) ⊹ ((ℤ→ℚ (+ 3)) · (x · y)))
  gen-v = begin
    evalℚ R.v
      ≈⟨ evalℚ-++ (R.kP (+ 4)) (R.kP (+ 3) *P R.X *P R.Y) ⟩
    (evalℚ (R.kP (+ 4))) ⊹ (evalℚ (R.kP (+ 3) *P R.X *P R.Y))
      ≈⟨ +ℚ-cong (gen-kP (+ 4)) (eval-*P3 (R.kP (+ 3)) R.X R.Y) ⟩
    (ℤ→ℚ (+ 4)) ⊹ (((evalℚ (R.kP (+ 3))) · (evalℚ R.X)) · (evalℚ R.Y))
      ≈⟨ +ℚ-cong (≈ℚ-refl (ℤ→ℚ (+ 4))) (*ℚ-cong (*ℚ-cong (gen-kP (+ 3)) gen-X) gen-Y) ⟩
    (ℤ→ℚ (+ 4)) ⊹ (((ℤ→ℚ (+ 3)) · x) · y)
      ≈⟨ +ℚ-cong (≈ℚ-refl (ℤ→ℚ (+ 4))) (*ℚ-assoc (ℤ→ℚ (+ 3)) x y) ⟩
    (ℤ→ℚ (+ 4)) ⊹ ((ℤ→ℚ (+ 3)) · (x · y)) ∎ℚ
