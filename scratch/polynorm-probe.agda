-- ⟡jac-poly-normalize (RUNG 3a): normalize MPoly to a sorted-by-Mono,
-- combined-coefficients, no-zero canonical form; coeff is a homomorphism.
{-# OPTIONS --safe --without-K --guardedness #-}

module polynorm-probe where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Nat.Properties.Order using (<-irrefl)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂; subst)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ; _≟ℤ_)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Properties.Add using (+ℤ-assoc; +ℤ-identityˡ)
open import Substrate.Algebra.Z.JacobianResidue
  using (Mono; mono; Term; term; MPoly; coeff; eqM; eqℕ; 𝔹; tt; ff; and)

------------------------------------------------------------------------
-- Small helpers on Mono / 𝔹 / ℕ.
------------------------------------------------------------------------

fst₃ snd₃ thd₃ : Mono → ℕ
fst₃ (mono a _ _) = a
snd₃ (mono _ b _) = b
thd₃ (mono _ _ c) = c

<→≢ : {a b : ℕ} → a < b → ¬ (a ≡ b)
<→≢ {a} lt refl = <-irrefl a lt

and-l : {x y : 𝔹} → and x y ≡ tt → x ≡ tt
and-l {tt} _ = refl
and-r : {x y : 𝔹} → and x y ≡ tt → y ≡ tt
and-r {tt} e = e

cong₃ : {A B C D : Set} (g : A → B → C → D) {a a' : A} {b b' : B} {c c' : C} →
        a ≡ a' → b ≡ b' → c ≡ c' → g a b c ≡ g a' b' c'
cong₃ g refl refl refl = refl

------------------------------------------------------------------------
-- eqM ↔ ≡  (JR's eqM = and∘eqℕ; eqℕ is structural).
------------------------------------------------------------------------

private
  eqℕ-refl : (n : ℕ) → eqℕ n n ≡ tt
  eqℕ-refl zero    = refl
  eqℕ-refl (suc n) = eqℕ-refl n

  eqℕ-sound : {p q : ℕ} → eqℕ p q ≡ tt → p ≡ q
  eqℕ-sound {zero}  {zero}  _ = refl
  eqℕ-sound {suc p} {suc q} e = cong suc (eqℕ-sound e)

eqM-refl : (m : Mono) → eqM m m ≡ tt
eqM-refl (mono a b c) rewrite eqℕ-refl a | eqℕ-refl b | eqℕ-refl c = refl

eqM-sound : {m n : Mono} → eqM m n ≡ tt → m ≡ n
eqM-sound {mono a b c} {mono d e f} h =
  cong₃ mono (eqℕ-sound (and-l h))
             (eqℕ-sound (and-l (and-r h)))
             (eqℕ-sound (and-r (and-r h)))

------------------------------------------------------------------------
-- Trichotomy on Mono (lex); lt/gt carry distinctness ¬(m≡n).
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

data TriM (m n : Mono) : Set where
  ltM  : ¬ (m ≡ n) → TriM m n
  eqM≡ :    m ≡ n  → TriM m n
  gtM  : ¬ (m ≡ n) → TriM m n

triM : (m n : Mono) → TriM m n
triM (mono a b c) (mono d e f) with triℕ a d
... | ltN p = ltM (λ eq → <→≢ p (cong fst₃ eq))
... | gtN p = gtM (λ eq → <→≢ p (sym (cong fst₃ eq)))
... | eqN refl with triℕ b e
...   | ltN q = ltM (λ eq → <→≢ q (cong snd₃ eq))
...   | gtN q = gtM (λ eq → <→≢ q (sym (cong snd₃ eq)))
...   | eqN refl with triℕ c f
...     | ltN r = ltM (λ eq → <→≢ r (cong thd₃ eq))
...     | gtN r = gtM (λ eq → <→≢ r (sym (cong thd₃ eq)))
...     | eqN refl = eqM≡ refl

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
-- coeff is a homomorphism.
------------------------------------------------------------------------

-- coeff of a single cons, directed by the eqM test (each does its own `with`,
-- so nested conses on the same Mono reduce cleanly). Explicit args (inference
-- through trans-chains would leave the tail p a metavariable).
ff≢tt : ff ≡ tt → ⊥
ff≢tt ()
tt≢ff : tt ≡ ff → ⊥
tt≢ff ()

coeff-cons-tt : (j m : Mono) (k : ℤ) (p : MPoly) →
                eqM j m ≡ tt → coeff j (term m k ∷ p) ≡ k +ℤ coeff j p
coeff-cons-tt j m k p e with eqM j m in ejm
... | tt = refl
... | ff = ⊥-elim (ff≢tt e)

coeff-cons-ff : (j m : Mono) (k : ℤ) (p : MPoly) →
                eqM j m ≡ ff → coeff j (term m k ∷ p) ≡ coeff j p
coeff-cons-ff j m k p e with eqM j m in ejm
... | ff = refl
... | tt = ⊥-elim (tt≢ff e)

coeff-++ : (m : Mono) (p q : MPoly) → coeff m (p ++ q) ≡ coeff m p +ℤ coeff m q
coeff-++ m [] q = sym (+ℤ-identityˡ (coeff m q))
coeff-++ m (term n k ∷ p) q with eqM m n
... | tt = trans (cong (k +ℤ_) (coeff-++ m p q)) (sym (+ℤ-assoc k (coeff m p) (coeff m q)))
... | ff = coeff-++ m p q

coeff-consNZ : (j m : Mono) (k : ℤ) (p : MPoly) →
               coeff j (consNZ m k p) ≡ coeff j (term m k ∷ p)
coeff-consNZ j m k p with k ≟ℤ 0ℤ
... | no  _ = refl
... | yes k≡0 with eqM j m in ejm
...   | ff = sym (coeff-cons-ff j m k p ejm)
...   | tt = sym (trans (coeff-cons-tt j m k p ejm)
                        (trans (cong (_+ℤ coeff j p) k≡0) (+ℤ-identityˡ (coeff j p))))

-- inserting a term preserves every coefficient (insertT ≈ term m k ∷).
coeff-insertT : (j m : Mono) (k : ℤ) (p : MPoly) →
                coeff j (insertT m k p) ≡ coeff j (term m k ∷ p)
coeff-insertT j m k [] = coeff-consNZ j m k []
coeff-insertT j m k (term n d ∷ p) with triM m n
... | ltM _ = coeff-consNZ j m k (term n d ∷ p)
... | eqM≡ refl with eqM j m in ejm       -- m ≡ n: both sides cons on the same m
...   | tt = trans (coeff-consNZ j m (k +ℤ d) p)
                   (trans (coeff-cons-tt j m (k +ℤ d) p ejm)
                          (trans (+ℤ-assoc k d (coeff j p))
                                 (sym (trans (coeff-cons-tt j m k (term m d ∷ p) ejm)
                                             (cong (k +ℤ_) (coeff-cons-tt j m d p ejm))))))
...   | ff = trans (coeff-consNZ j m (k +ℤ d) p)
                   (trans (coeff-cons-ff j m (k +ℤ d) p ejm)
                          (sym (trans (coeff-cons-ff j m k (term m d ∷ p) ejm)
                                      (coeff-cons-ff j m d p ejm))))
coeff-insertT j m k (term n d ∷ p) | gtM m≢n with eqM j n in ejn | eqM j m in ejm
... | tt | tt = ⊥-elim (m≢n (trans (sym (eqM-sound ejm)) (eqM-sound ejn)))
... | tt | ff = trans (trans (coeff-cons-tt j n d (insertT m k p) ejn)
                             (cong (d +ℤ_) (trans (coeff-insertT j m k p) (coeff-cons-ff j m k p ejm))))
                      (sym (trans (coeff-cons-ff j m k (term n d ∷ p) ejm) (coeff-cons-tt j n d p ejn)))
... | ff | tt = trans (trans (coeff-cons-ff j n d (insertT m k p) ejn)
                             (trans (coeff-insertT j m k p) (coeff-cons-tt j m k p ejm)))
                      (sym (trans (coeff-cons-tt j m k (term n d ∷ p) ejm) (cong (k +ℤ_) (coeff-cons-ff j n d p ejn))))
... | ff | ff = trans (trans (coeff-cons-ff j n d (insertT m k p) ejn)
                             (trans (coeff-insertT j m k p) (coeff-cons-ff j m k p ejm)))
                      (sym (trans (coeff-cons-ff j m k (term n d ∷ p) ejm) (coeff-cons-ff j n d p ejn)))

coeff-normalize : (j : Mono) (p : MPoly) → coeff j (normalize p) ≡ coeff j p
coeff-normalize j []             = refl
coeff-normalize j (term m k ∷ p) with eqM j m in ejm
... | tt = trans (coeff-insertT j m k (normalize p))
                 (trans (coeff-cons-tt j m k (normalize p) ejm)
                        (trans (cong (k +ℤ_) (coeff-normalize j p)) (sym (coeff-cons-tt j m k p ejm))))
... | ff = trans (coeff-insertT j m k (normalize p))
                 (trans (coeff-cons-ff j m k (normalize p) ejm)
                        (trans (coeff-normalize j p) (sym (coeff-cons-ff j m k p ejm))))
