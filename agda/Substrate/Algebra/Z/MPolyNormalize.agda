{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.MPolyNormalize — ⟡jac-poly-normalize (RUNG 3a), DEFS.
--
-- The DEFINITION layer: the sorted-insert canonicalizer `normalize`, the
-- boolean sorted-invariant `isSortedB`, and the ordering scaffolding
-- (`_<M_` relational lex, `ltMᵇ` boolean lex, `triM` trichotomy). This
-- module declares datatypes, so its import closure is kept proof-free
-- (no `*.Properties`); ALL proofs live in `MPolyNormalize.Properties`.
--
-- `triM` carries only the `_<M_` witness (proof-free); the `¬(m≡n)` legs
-- consumed by `coeff-insertT` are re-derived in `.Properties` via `<M→≢`.
--
-- RUNG 3b's `NormPoly`-Semiring and RUNG 3c's native det build on top of
-- `normalize`/`isSortedB` here and the homomorphism/canonicity proofs there.
------------------------------------------------------------------------

module Substrate.Algebra.Z.MPolyNormalize where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂; subst)
open import Substrate.Algebra.Z using (ℤ; +_; 0ℤ; 1ℤ; _≟ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.JacobianResidue
  using (Mono; mono; Term; term; MPoly; coeff; eqM; eqℕ; 𝔹; tt; ff; and)

------------------------------------------------------------------------
-- Small proof-free helpers on Mono / 𝔹.
------------------------------------------------------------------------

fst₃ snd₃ thd₃ : Mono → ℕ
fst₃ (mono a _ _) = a
snd₃ (mono _ b _) = b
thd₃ (mono _ _ c) = c

and-l : {x y : 𝔹} → and x y ≡ tt → x ≡ tt
and-l {tt} _ = refl
and-r : {x y : 𝔹} → and x y ≡ tt → y ≡ tt
and-r {tt} e = e
and-tt : {x y : 𝔹} → x ≡ tt → y ≡ tt → and x y ≡ tt
and-tt {x} {y} ex ey = trans (cong (λ b → and b y) ex) ey

ff≢tt : ff ≡ tt → ⊥
ff≢tt ()

cong₃ : {A B C D : Set} (g : A → B → C → D) {a a' : A} {b b' : B} {c c' : C} →
        a ≡ a' → b ≡ b' → c ≡ c' → g a b c ≡ g a' b' c'
cong₃ g refl refl refl = refl

------------------------------------------------------------------------
-- Trichotomy on ℕ (proof-free: witnesses come from the `_≤_` constructors).
------------------------------------------------------------------------

data TriN (a b : ℕ) : Set where
  ltN : a < b → TriN a b
  eqN : a ≡ b → TriN a b
  gtN : b < a → TriN a b

triℕ : (a b : ℕ) → TriN a b
triℕ zero    zero    = eqN refl
triℕ zero    (suc b) = ltN (s≤s z≤n)
triℕ (suc a) zero    = gtN (s≤s z≤n)
triℕ (suc a) (suc b) with triℕ a b
... | ltN p = ltN (s≤s p)
... | eqN p = eqN (cong suc p)
... | gtN p = gtN (s≤s p)

------------------------------------------------------------------------
-- The lex-strict Mono order: relational `_<M_` and boolean `ltMᵇ`.
------------------------------------------------------------------------

data _<M_ : Mono → Mono → Set where
  <x : {a b c d e f : ℕ} → a < d → mono a b c <M mono d e f
  <y : {a b c e f : ℕ}   → b < e → mono a b c <M mono a e f
  <z : {a b c f : ℕ}     → c < f → mono a b c <M mono a b f

-- boolean lex, driven by triℕ RESULTS (so the bridge lemmas' `with triℕ …`
-- also reduces `ltMᵇ` — the Bcase idiom, at the ordering layer).
lex3 : {a d b e c f : ℕ} → TriN a d → TriN b e → TriN c f → 𝔹
lex3 (ltN _) _        _        = tt
lex3 (gtN _) _        _        = ff
lex3 (eqN _) (ltN _)  _        = tt
lex3 (eqN _) (gtN _)  _        = ff
lex3 (eqN _) (eqN _)  (ltN _)  = tt
lex3 (eqN _) (eqN _)  (eqN _)  = ff
lex3 (eqN _) (eqN _)  (gtN _)  = ff

ltMᵇ : Mono → Mono → 𝔹
ltMᵇ (mono a b c) (mono d e f) = lex3 (triℕ a d) (triℕ b e) (triℕ c f)

------------------------------------------------------------------------
-- Trichotomy on Mono — carries only the `_<M_` witness (PROOF-FREE); the
-- `¬(m≡n)` legs live in `.Properties`.
------------------------------------------------------------------------

data TriM (m n : Mono) : Set where
  ltM  : m <M n → TriM m n
  eqM≡ :  m ≡ n → TriM m n
  gtM  : n <M m → TriM m n

triM : (m n : Mono) → TriM m n
triM (mono a b c) (mono d e f) with triℕ a d
... | ltN p = ltM (<x p)
... | gtN p = gtM (<x p)
... | eqN refl with triℕ b e
...   | ltN q = ltM (<y q)
...   | gtN q = gtM (<y q)
...   | eqN refl with triℕ c f
...     | ltN r = ltM (<z r)
...     | gtN r = gtM (<z r)
...     | eqN refl = eqM≡ refl

------------------------------------------------------------------------
-- Nonzero-coefficient test.
------------------------------------------------------------------------

nzB : ℤ → 𝔹
nzB k with k ≟ℤ 0ℤ
... | yes _ = ff
... | no  _ = tt

------------------------------------------------------------------------
-- Sorted-insert (combine on equal Mono, drop zero coeff) + normalize.
------------------------------------------------------------------------

consNZ : Mono → ℤ → MPoly → MPoly
consNZ m k p with k ≟ℤ 0ℤ
... | yes _ = p
... | no  _ = term m k ∷ p

insertT : Mono → ℤ → MPoly → MPoly
insertT m k []               = consNZ m k []
insertT m k (term n d ∷ p) with triM m n
... | ltM  _ = consNZ m k (term n d ∷ p)
... | eqM≡ _ = consNZ n (k +ℤ d) p
... | gtM  _ = term n d ∷ insertT m k p

normalize : MPoly → MPoly
normalize []             = []
normalize (term m k ∷ p) = insertT m k (normalize p)

------------------------------------------------------------------------
-- coeff-cons eliminator: the unconditional boolean case (makes coeff-cons refl).
------------------------------------------------------------------------

Bcase : 𝔹 → ℤ → ℤ → ℤ
Bcase tt a b = a
Bcase ff a b = b

------------------------------------------------------------------------
-- isSortedB : strictly-ascending keys ∧ all-coefficients-nonzero. The ONE
-- boolean invariant (RUNG 3b's NormPoly needs BOTH: keys for canonicity,
-- nonzero to forbid `[term m 0]` ≡-collision with `[]`).
------------------------------------------------------------------------

isSortedB : MPoly → 𝔹
isSortedB []                        = tt
isSortedB (term m k ∷ [])           = nzB k
isSortedB (term m k ∷ term n d ∷ p) = and (nzB k) (and (ltMᵇ m n) (isSortedB (term n d ∷ p)))

-- `m` is a strict lower bound for the head key of q (or q empty).
minB : Mono → MPoly → 𝔹
minB m []              = tt
minB m (term n d ∷ _)  = ltMᵇ m n
