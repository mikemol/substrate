{-# OPTIONS --safe --without-K --guardedness #-}

-- Empirical check of the Bcase reformulation for RUNG 3a coeff-cons.
module bcase-probe where

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

-- ---- helpers copied verbatim from polynorm-probe ----
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
  cong₃ mono (eqℕ-sound (and-l {eqℕ a d} h))
             (eqℕ-sound (and-l {eqℕ b e} (and-r {eqℕ a d} h)))
             (eqℕ-sound (and-r {eqℕ b e} (and-r {eqℕ a d} h)))

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
-- THE Bcase REFORMULATION (the deliverable under test)
------------------------------------------------------------------------

Bcase : 𝔹 → ℤ → ℤ → ℤ
Bcase tt a b = a
Bcase ff a b = b

coeff-cons : (j m : Mono) (k : ℤ) (p : MPoly) →
             coeff j (term m k ∷ p) ≡ Bcase (eqM j m) (k +ℤ coeff j p) (coeff j p)
coeff-cons j m k p with eqM j m
... | tt = refl
... | ff = refl

coeff-++ : (m : Mono) (p q : MPoly) → coeff m (p ++ q) ≡ coeff m p +ℤ coeff m q
coeff-++ m [] q = sym (+ℤ-identityˡ (coeff m q))
coeff-++ m (term n k ∷ p) q with eqM m n
... | tt = trans (cong (k +ℤ_) (coeff-++ m p q)) (sym (+ℤ-assoc k (coeff m p) (coeff m q)))
... | ff = coeff-++ m p q

coeff-consNZ : (j m : Mono) (k : ℤ) (p : MPoly) →
               coeff j (consNZ m k p) ≡ coeff j (term m k ∷ p)
coeff-consNZ j m k p with k ≟ℤ 0ℤ
... | no  _ = refl
... | yes k≡0 = trans eq (sym (coeff-cons j m k p))
  where
    eq : coeff j p ≡ Bcase (eqM j m) (k +ℤ coeff j p) (coeff j p)
    eq with eqM j m
    ... | tt = sym (trans (cong (_+ℤ coeff j p) k≡0) (+ℤ-identityˡ (coeff j p)))
    ... | ff = refl

coeff-insertT : (j m : Mono) (k : ℤ) (p : MPoly) →
                coeff j (insertT m k p) ≡ coeff j (term m k ∷ p)
coeff-insertT j m k [] = coeff-consNZ j m k []
coeff-insertT j m k (term n d ∷ p) with triM m n
... | ltM _ = coeff-consNZ j m k (term n d ∷ p)
... | eqM≡ refl =
      trans (coeff-consNZ j m (k +ℤ d) p)
      (trans (coeff-cons j m (k +ℤ d) p)
      (trans mid (sym (coeff-cons j m k (term m d ∷ p)))))
  where
    -- m ≡ n case. LHS reduced to Bcase(eqM j m)((k+d)+coeff j p)(coeff j p);
    -- RHS reduced to Bcase(eqM j m)(k + coeff j (term m d ∷ p))(coeff j (term m d ∷ p)).
    -- `rewrite coeff-cons j m d p` FIRST collapses the inner coeff to a Bcase on the
    -- SAME eqM j m, so the outer `with eqM j m` drives all occurrences together.
    mid : Bcase (eqM j m) ((k +ℤ d) +ℤ coeff j p) (coeff j p)
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term m d ∷ p)) (coeff j (term m d ∷ p))
    mid rewrite coeff-cons j m d p with eqM j m
    ... | tt = +ℤ-assoc k d (coeff j p)
    ... | ff = refl
coeff-insertT j m k (term n d ∷ p) | gtM m≢n =
      trans (coeff-cons j n d (insertT m k p))
      (trans mid
             (sym (coeff-cons j m k (term n d ∷ p))))
  where
    -- gt case: the two conses are on DIFFERENT monos (m ≢ n), so peel BOTH via
    -- coeff-cons + IH, then split on BOTH eqM j m and eqM j n. The (tt,tt) corner
    -- (j≡m AND j≡n) is impossible by m≢n; the other three are refl.
    mid : Bcase (eqM j n) (d +ℤ coeff j (insertT m k p)) (coeff j (insertT m k p))
        ≡ Bcase (eqM j m) (k +ℤ coeff j (term n d ∷ p))  (coeff j (term n d ∷ p))
    mid rewrite coeff-insertT j m k p | coeff-cons j m k p | coeff-cons j n d p
              with eqM j m in ejm | eqM j n in ejn
    ... | tt | tt = ⊥-elim (m≢n (trans (sym (eqM-sound {j} {m} ejm)) (eqM-sound {j} {n} ejn)))
    ... | tt | ff = refl
    ... | ff | tt = refl
    ... | ff | ff = refl

coeff-normalize : (j : Mono) (p : MPoly) → coeff j (normalize p) ≡ coeff j p
coeff-normalize j []             = refl
coeff-normalize j (term m k ∷ p) =
  trans (coeff-insertT j m k (normalize p))
  (trans (coeff-cons j m k (normalize p))
  (trans step (sym (coeff-cons j m k p))))
  where
    step : Bcase (eqM j m) (k +ℤ coeff j (normalize p)) (coeff j (normalize p))
         ≡ Bcase (eqM j m) (k +ℤ coeff j p)            (coeff j p)
    step with eqM j m
    ... | tt = cong (k +ℤ_) (coeff-normalize j p)
    ... | ff = coeff-normalize j p

-- concrete non-vacuity pole: x + x normalizes so coeff x = 2
xP : MPoly
xP = term (mono 1 0 0) 1ℤ ∷ term (mono 1 0 0) 1ℤ ∷ []

pole-x+x : coeff (mono 1 0 0) (normalize xP) ≡ + 2
pole-x+x = refl
