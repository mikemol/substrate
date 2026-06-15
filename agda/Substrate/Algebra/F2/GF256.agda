------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256
--
-- GF(2⁸) = F₂[x]/(x⁸+x⁴+x³+x+1), the Rijndael field, as a `Ring` on the
-- byte carrier `Vector 8`. Multiplication `gmul a b = reduce-mod-m (a *P b)`
-- is a THIN SKIN over `Polynomial.RingLaws`' `_*P_`; `reduce-mod-m` is the
-- Horner fold (digit-on-demand), whose only kernel `xtime` (·x mod m) reuses
-- the modulus as data (`m-lo`).
--
-- `reduce-mod-m` is proven a RING HOMOMORPHISM (additive `reduce-+ⱽ`,
-- multiplicative `reduce-*-hom`), so `gmul`'s ring laws are `_*P_`'s laws
-- PULLED THROUGH `reduce` — not re-proven; the graded length-`subst`s vanish
-- at the fixed carrier 8. Built via the fold ⇒ NO polynomial long division.
-- Capstone: `GF256-Ring : Ring (Vector 8)`.
--
-- FIPS-197 §4.2 `{57}·{13}={fe}` holds by `refl` through this `gmul`.
-- The multiplicative inverse (⇒ `Field`) is deferred to the EEA construction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256 where

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; _·_; +-identityˡ; +-assoc;
  ·-comm; ·-assoc; ·-distribˡ-+) renaming (+-comm to +F-comm)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)

m-lo : Vector 8
m-lo = 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟙 ∷ 𝟙 ∷ 𝟘 ∷ 𝟘 ∷ 𝟘 ∷ []

xtime : Vector 8 → Vector 8
xtime (b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ b7 ∷ []) =
  (𝟘 ∷ b0 ∷ b1 ∷ b2 ∷ b3 ∷ b4 ∷ b5 ∷ b6 ∷ []) +ⱽ (b7 *ₛ m-lo)

-- F₂ helpers (re-derived, as in RingLaws)
·-distribʳ : (x y z : F₂) → (x + y) · z ≡ x · z + y · z
·-distribʳ x y z = trans (·-comm (x + y) z)
                   (trans (·-distribˡ-+ z x y) (cong₂ _+_ (·-comm z x) (·-comm z y)))
rearrange : (w x y z : F₂) → (w + x) + (y + z) ≡ (w + y) + (x + z)
rearrange w x y z =
  trans (+-assoc w x (y + z))
  (trans (cong (w +_) (sym (+-assoc x y z)))
  (trans (cong (λ t → w + (t + z)) (+F-comm x y))
  (trans (cong (w +_) (+-assoc y x z)) (sym (+-assoc w y (x + z))))))

-- A1a: xtime preserves +ⱽ. Per-position: distribʳ (split (u7+v7)·b) + 4-term rearrange.
xtime-+ⱽ : (u v : Vector 8) → xtime (u +ⱽ v) ≡ xtime u +ⱽ xtime v
xtime-+ⱽ (u0 ∷ u1 ∷ u2 ∷ u3 ∷ u4 ∷ u5 ∷ u6 ∷ u7 ∷ [])
         (v0 ∷ v1 ∷ v2 ∷ v3 ∷ v4 ∷ v5 ∷ v6 ∷ v7 ∷ []) =
  cong₂ _∷_ p0 (cong₂ _∷_ (q u0 v0 𝟙) (cong₂ _∷_ (q u1 v1 𝟘) (cong₂ _∷_ (q u2 v2 𝟙)
   (cong₂ _∷_ (q u3 v3 𝟙) (cong₂ _∷_ (q u4 v4 𝟘) (cong₂ _∷_ (q u5 v5 𝟘)
    (cong₂ _∷_ (q u6 v6 𝟘) refl)))))))
  where
    q : (a b c : F₂) → (a + b) + (u7 + v7) · c ≡ (a + u7 · c) + (b + v7 · c)
    q a b c = trans (cong ((a + b) +_) (·-distribʳ u7 v7 c)) (rearrange a b (u7 · c) (v7 · c))
    p0 : 𝟘 + (u7 + v7) · 𝟙 ≡ (𝟘 + u7 · 𝟙) + (𝟘 + v7 · 𝟙)
    p0 = trans (+-identityˡ ((u7 + v7) · 𝟙))
         (trans (·-distribʳ u7 v7 𝟙)
                (sym (cong₂ _+_ (+-identityˡ (u7 · 𝟙)) (+-identityˡ (v7 · 𝟙)))))

-- A1b: xtime preserves *ₛ. Per-position: ·-assoc to move c out, then ·-distribˡ-+ back.
xtime-*ₛ : (c : F₂) (w : Vector 8) → xtime (c *ₛ w) ≡ c *ₛ xtime w
xtime-*ₛ c (w0 ∷ w1 ∷ w2 ∷ w3 ∷ w4 ∷ w5 ∷ w6 ∷ w7 ∷ []) =
  cong₂ _∷_ p0 (cong₂ _∷_ (q w0 𝟙) (cong₂ _∷_ (q w1 𝟘) (cong₂ _∷_ (q w2 𝟙)
   (cong₂ _∷_ (q w3 𝟙) (cong₂ _∷_ (q w4 𝟘) (cong₂ _∷_ (q w5 𝟘)
    (cong₂ _∷_ (q w6 𝟘) refl)))))))
  where
    q : (a b : F₂) → (c · a) + (c · w7) · b ≡ c · (a + w7 · b)
    q a b = trans (cong ((c · a) +_) (·-assoc c w7 b)) (sym (·-distribˡ-+ c a (w7 · b)))
    p0 : 𝟘 + (c · w7) · 𝟙 ≡ c · (𝟘 + w7 · 𝟙)
    p0 = trans (+-identityˡ ((c · w7) · 𝟙))
         (trans (·-assoc c w7 𝟙) (sym (cong (c ·_) (+-identityˡ (w7 · 𝟙)))))

-- ===== A3: reduce-mod-m is F₂-linear (Horner induction, A1 at the step) =====
open import Substrate.Algebra.F2 using (·-absorbʳ)
open import Substrate.Algebra.F2.Vector using (𝟎ⱽ; +ⱽ-identityˡ; +ⱽ-comm; +ⱽ-assoc;
  *ₛ-distribˡ-+ⱽ; lookup-*ₛ; lookup-𝟎; ≡-from-lookup)

reduce-mod-m : ∀ {n} → Vec F₂ n → Vector 8
reduce-mod-m []      = 𝟎ⱽ
reduce-mod-m (a ∷ q) = (a ∷ 𝟎ⱽ) +ⱽ xtime (reduce-mod-m q)

*ₛ-zeroʳ : ∀ {n} (c : F₂) → (c *ₛ 𝟎ⱽ {n}) ≡ 𝟎ⱽ {n}
*ₛ-zeroʳ c = ≡-from-lookup _ _
  (λ i → trans (lookup-*ₛ c 𝟎ⱽ i)
         (trans (cong (c ·_) (lookup-𝟎 i)) (trans (·-absorbʳ c) (sym (lookup-𝟎 i)))))

+ⱽ-rearrange : ∀ {n} (a b c d : Vector n) → (a +ⱽ b) +ⱽ (c +ⱽ d) ≡ (a +ⱽ c) +ⱽ (b +ⱽ d)
+ⱽ-rearrange a b c d =
  trans (+ⱽ-assoc a b (c +ⱽ d))
  (trans (cong (a +ⱽ_) (sym (+ⱽ-assoc b c d)))
  (trans (cong (λ t → a +ⱽ (t +ⱽ d)) (+ⱽ-comm b c))
  (trans (cong (a +ⱽ_) (+ⱽ-assoc c b d)) (sym (+ⱽ-assoc a c (b +ⱽ d))))))

-- A3a: additivity. base = sym +ⱽ-identityˡ; step = head-split + xtime-+ⱽ(IH) + 4-term rearrange.
reduce-+ⱽ : ∀ {n} (u v : Vec F₂ n) → reduce-mod-m (u +ⱽ v) ≡ reduce-mod-m u +ⱽ reduce-mod-m v
reduce-+ⱽ []      []      = sym (+ⱽ-identityˡ 𝟎ⱽ)
reduce-+ⱽ (a ∷ u) (b ∷ v) =
  trans (cong₂ _+ⱽ_ (cong ((a + b) ∷_) (sym (+ⱽ-identityˡ 𝟎ⱽ)))
                    (trans (cong xtime (reduce-+ⱽ u v))
                           (xtime-+ⱽ (reduce-mod-m u) (reduce-mod-m v))))
        (+ⱽ-rearrange (a ∷ 𝟎ⱽ) (b ∷ 𝟎ⱽ) (xtime (reduce-mod-m u)) (xtime (reduce-mod-m v)))

-- A3b: scalar-linearity. base = sym *ₛ-zeroʳ; step = head-split + xtime-*ₛ(IH) + *ₛ-distribˡ.
reduce-*ₛ : ∀ {n} (c : F₂) (v : Vec F₂ n) → reduce-mod-m (c *ₛ v) ≡ c *ₛ reduce-mod-m v
reduce-*ₛ c []      = sym (*ₛ-zeroʳ c)
reduce-*ₛ c (a ∷ v) =
  trans (cong₂ _+ⱽ_ (cong ((c · a) ∷_) (sym (*ₛ-zeroʳ c)))
                    (trans (cong xtime (reduce-*ₛ c v))
                           (xtime-*ₛ c (reduce-mod-m v))))
        (sym (*ₛ-distribˡ-+ⱽ c (a ∷ 𝟎ⱽ) (xtime (reduce-mod-m v))))

-- ===== A4: reduce of a product = Horner sum over the left factor (the *-hom bridge) =====
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Nat.Properties renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Eq using (subst)
open import Substrate.Algebra.F2.Vector using (*ₛ-absorbˡ)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_; shift-to-suc-on-left;
  pad-end; x-shift; _·c_)

reduce-x-shift : ∀ {n} (q : Vec F₂ n) → reduce-mod-m (𝟘 ∷ q) ≡ xtime (reduce-mod-m q)
reduce-x-shift q = +ⱽ-identityˡ (xtime (reduce-mod-m q))

xtime-zero : xtime 𝟎ⱽ ≡ 𝟎ⱽ
xtime-zero = trans (+ⱽ-identityˡ (𝟘 *ₛ m-lo)) (*ₛ-absorbˡ m-lo)

reduce-𝟎ⱽ : ∀ {n} → reduce-mod-m (𝟎ⱽ {n}) ≡ 𝟎ⱽ
reduce-𝟎ⱽ {zero}  = refl
reduce-𝟎ⱽ {suc n} =
  trans (cong (λ z → (𝟘 ∷ 𝟎ⱽ) +ⱽ xtime z) (reduce-𝟎ⱽ {n}))
        (trans (cong ((𝟘 ∷ 𝟎ⱽ) +ⱽ_) xtime-zero) (+ⱽ-identityˡ 𝟎ⱽ))

reduce-subst : ∀ {a b} (eq : a ≡ b) (v : Polynomial a)
             → reduce-mod-m (subst Polynomial eq v) ≡ reduce-mod-m v
reduce-subst refl v = refl

reduce-pad-end : ∀ {n} (k : ℕ) (v : Polynomial n)
               → reduce-mod-m (pad-end k v) ≡ reduce-mod-m v
reduce-pad-end k []      = reduce-𝟎ⱽ {k}
reduce-pad-end k (x ∷ v) = cong (λ z → (x ∷ 𝟎ⱽ) +ⱽ xtime z) (reduce-pad-end k v)

hsum : ∀ {n} → Polynomial n → Vector 8 → Vector 8
hsum []      r = 𝟎ⱽ
hsum (a ∷ p) r = (a *ₛ r) +ⱽ hsum p (xtime r)

hsum-xtime : ∀ {n} (p : Polynomial n) (r : Vector 8) → xtime (hsum p r) ≡ hsum p (xtime r)
hsum-xtime []      r = xtime-zero
hsum-xtime (a ∷ p) r =
  trans (xtime-+ⱽ (a *ₛ r) (hsum p (xtime r)))
        (cong₂ _+ⱽ_ (xtime-*ₛ a r) (hsum-xtime p (xtime r)))

reduce-*P-expand : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
                 → reduce-mod-m (p *P q) ≡ hsum p (reduce-mod-m q)
reduce-*P-expand {zero}  {m} []      q = reduce-𝟎ⱽ {m}
reduce-*P-expand {suc n} {m} (a ∷ p) q =
  trans (reduce-+ⱽ (shift-to-suc-on-left (pad-end (suc n) (a ·c q))) (x-shift (p *P q)))
  (trans (cong₂ _+ⱽ_
            (trans (reduce-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)))
                   (trans (reduce-pad-end (suc n) (a ·c q)) (reduce-*ₛ a q)))
            (trans (reduce-x-shift (p *P q)) (cong xtime (reduce-*P-expand p q))))
         (cong ((a *ₛ reduce-mod-m q) +ⱽ_) (hsum-xtime p (reduce-mod-m q))))

-- ===== A6: reduce-idempotent (reduce p ≡ p for p : Vector 8) =====
open import Substrate.Algebra.F2 using (·-identityʳ)

one₈ : Vector 8
one₈ = 𝟙 ∷ 𝟎ⱽ

-- reduce p = hsum p 𝟙₈ (general): the fold IS Horner evaluation at xtime-powers of the unit.
reduce-eq-hsum : ∀ {n} (p : Polynomial n) → reduce-mod-m p ≡ hsum p one₈
reduce-eq-hsum []      = refl
reduce-eq-hsum (a ∷ q) =
  cong₂ _+ⱽ_ (cong₂ _∷_ (sym (·-identityʳ a)) (sym (*ₛ-zeroʳ a)))
             (trans (cong xtime (reduce-eq-hsum q)) (hsum-xtime q one₈))

open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Vector.Universal using (sum; basis-decomp)

xpow : ℕ → Vector 8 → Vector 8
xpow zero    r = r
xpow (suc k) r = xpow k (xtime r)

sum-cong : ∀ {n m} {f g : Fin n → Vector m} → (∀ i → f i ≡ g i) → sum f ≡ sum g
sum-cong {zero}  _  = refl
sum-cong {suc _} eq = cong₂ _+ⱽ_ (eq fz) (sum-cong (λ i → eq (fs i)))

-- hsum is the basis-weighted sum (the fold = Σᵢ pᵢ ·ₛ xtimeⁱ r).
hsum-is-sum : ∀ {n} (p : Polynomial n) (r : Vector 8)
            → hsum p r ≡ sum (λ i → lookup p i *ₛ xpow (toℕ i) r)
hsum-is-sum []      r = refl
hsum-is-sum (a ∷ p) r = cong (λ z → (a *ₛ r) +ⱽ z) (hsum-is-sum p (xtime r))

-- the validated off-by-one, as a total Fin-8 fact (8 refl clauses).
hsum-one-basis : (i : Fin 8) → xpow (toℕ i) one₈ ≡ basis i
hsum-one-basis fz = refl
hsum-one-basis (fs fz) = refl
hsum-one-basis (fs (fs fz)) = refl
hsum-one-basis (fs (fs (fs fz))) = refl
hsum-one-basis (fs (fs (fs (fs fz)))) = refl
hsum-one-basis (fs (fs (fs (fs (fs fz))))) = refl
hsum-one-basis (fs (fs (fs (fs (fs (fs fz)))))) = refl
hsum-one-basis (fs (fs (fs (fs (fs (fs (fs fz))))))) = refl

hsum-𝟙₈-id : (p : Vector 8) → hsum p one₈ ≡ p
hsum-𝟙₈-id p =
  trans (hsum-is-sum p one₈)
  (trans (sum-cong (λ i → cong (lookup p i *ₛ_) (hsum-one-basis i)))
         (sym (basis-decomp p)))

-- A6: reducing an already-reduced byte is the identity.
reduce-idempotent : (p : Vector 8) → reduce-mod-m p ≡ p
reduce-idempotent p = trans (reduce-eq-hsum p) (hsum-𝟙₈-id p)

-- A9: reduce is a ring hom in the multiplicative slot — reducing a factor first
-- doesn't change the reduced product. Falls straight out of A4 + A6 (no keystone).
reduce-*-hom : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
             → reduce-mod-m (p *P q) ≡ reduce-mod-m (p *P reduce-mod-m q)
reduce-*-hom p q =
  trans (reduce-*P-expand p q)
        (sym (trans (reduce-*P-expand p (reduce-mod-m q))
                    (cong (hsum p) (reduce-idempotent (reduce-mod-m q)))))

-- ===== AI-6e: gmul = reduce ∘ *P, ring laws PULLED THROUGH the homs from RingLaws =====
open import Substrate.Algebra.F2.Polynomial.RingLaws using (*P-comm; *P-assoc; *P-distribʳ; *P-distribˡ)
open import Substrate.Algebra.F2.Vector using (*ₛ-identityˡ; +ⱽ-identityʳ)

hsum-zero : ∀ {n} (r : Vector 8) → hsum (𝟎ⱽ {n}) r ≡ 𝟎ⱽ
hsum-zero {zero}  r = refl
hsum-zero {suc n} r = trans (cong₂ _+ⱽ_ (*ₛ-absorbˡ r) (hsum-zero {n} (xtime r))) (+ⱽ-identityˡ 𝟎ⱽ)

hsum-zeroʳ : ∀ {n} (p : Polynomial n) → hsum p 𝟎ⱽ ≡ 𝟎ⱽ
hsum-zeroʳ []      = refl
hsum-zeroʳ (a ∷ p) =
  trans (cong₂ _+ⱽ_ (*ₛ-zeroʳ a) (trans (cong (hsum p) xtime-zero) (hsum-zeroʳ p))) (+ⱽ-identityˡ 𝟎ⱽ)

hsum-one-id : (r : Vector 8) → hsum one₈ r ≡ r
hsum-one-id r = trans (cong₂ _+ⱽ_ (*ₛ-identityˡ r) (hsum-zero {7} (xtime r))) (+ⱽ-identityʳ r)

gmul : Vector 8 → Vector 8 → Vector 8
gmul a b = reduce-mod-m (a *P b)

gmul-comm : (a b : Vector 8) → gmul a b ≡ gmul b a
gmul-comm a b = trans (cong reduce-mod-m (*P-comm a b)) (reduce-subst (+ℕ-comm 8 8) (b *P a))

gmul-distribˡ : (a b c : Vector 8) → gmul a (b +ⱽ c) ≡ gmul a b +ⱽ gmul a c
gmul-distribˡ a b c = trans (cong reduce-mod-m (*P-distribˡ a b c)) (reduce-+ⱽ (a *P b) (a *P c))

gmul-distribʳ : (a b c : Vector 8) → gmul (a +ⱽ b) c ≡ gmul a c +ⱽ gmul b c
gmul-distribʳ a b c = trans (cong reduce-mod-m (*P-distribʳ a b c)) (reduce-+ⱽ (a *P c) (b *P c))

gmul-identityˡ : (b : Vector 8) → gmul one₈ b ≡ b
gmul-identityˡ b =
  trans (reduce-*P-expand one₈ b) (trans (hsum-one-id (reduce-mod-m b)) (reduce-idempotent b))

gmul-identityʳ : (b : Vector 8) → gmul b one₈ ≡ b
gmul-identityʳ b = trans (gmul-comm b one₈) (gmul-identityˡ b)

gmul-zeroˡ : (b : Vector 8) → gmul 𝟎ⱽ b ≡ 𝟎ⱽ
gmul-zeroˡ b = trans (reduce-*P-expand (𝟎ⱽ {8}) b) (hsum-zero {8} (reduce-mod-m b))

gmul-zeroʳ : (b : Vector 8) → gmul b 𝟎ⱽ ≡ 𝟎ⱽ
gmul-zeroʳ b = trans (reduce-*P-expand b (𝟎ⱽ {8}))
                     (trans (cong (hsum b) (reduce-𝟎ⱽ {8})) (hsum-zeroʳ b))

reduce-*-homˡ : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
              → reduce-mod-m (reduce-mod-m p *P q) ≡ reduce-mod-m (p *P q)
reduce-*-homˡ {n} {m} p q =
  trans (cong reduce-mod-m (*P-comm (reduce-mod-m p) q))
  (trans (reduce-subst (+ℕ-comm m 8) (q *P reduce-mod-m p))
  (trans (sym (reduce-*-hom q p))
  (trans (cong reduce-mod-m (*P-comm q p)) (reduce-subst (+ℕ-comm n m) (p *P q)))))

gmul-assoc : (a b c : Vector 8) → gmul (gmul a b) c ≡ gmul a (gmul b c)
gmul-assoc a b c =
  trans (reduce-*-homˡ (a *P b) c)
  (trans (sym (reduce-subst (+ℕ-assoc 8 8 8) ((a *P b) *P c)))
  (trans (cong reduce-mod-m (*P-assoc a b c)) (reduce-*-hom a (b *P c))))

-- ===== AI-6f: GF256-Ring : Ring (Vector 8) — climb the AsField ladder (record wiring) =====
open import Substrate.Algebra.F2.Vector using (+ⱽ-self-inverse)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Ring using (Ring)

-- ONE additive monoid, shared by the semiring AND the abelian group ⇒ +-coherent = refl.
+ⱽ-monoid : Monoid (Vector 8)
+ⱽ-monoid = record
  { semigroup = record { magma = record { _·_ = _+ⱽ_ } ; ·-assoc = +ⱽ-assoc }
  ; ε = 𝟎ⱽ ; ε-left = +ⱽ-identityˡ ; ε-right = +ⱽ-identityʳ }

-- char 2: every element is its own additive inverse (inv = id, inv-law = self-inverse).
+ⱽ-abelian : AbelianGroup (Vector 8)
+ⱽ-abelian = record
  { group = record { monoid = +ⱽ-monoid ; inv = λ v → v
                   ; inv-left = +ⱽ-self-inverse ; inv-right = +ⱽ-self-inverse }
  ; ·-comm = +ⱽ-comm }

gmul-monoid : Monoid (Vector 8)
gmul-monoid = record
  { semigroup = record { magma = record { _·_ = gmul } ; ·-assoc = gmul-assoc }
  ; ε = one₈ ; ε-left = gmul-identityˡ ; ε-right = gmul-identityʳ }

GF256-Semiring : Semiring (Vector 8)
GF256-Semiring = record
  { +-monoid = +ⱽ-monoid ; *-monoid = gmul-monoid
  ; distrib-left = gmul-distribˡ ; distrib-right = gmul-distribʳ
  ; zero-absorb-left = gmul-zeroˡ ; zero-absorb-right = gmul-zeroʳ }

GF256-Ring : Ring (Vector 8)
GF256-Ring = record { semiring = GF256-Semiring ; +-abelian = +ⱽ-abelian ; +-coherent = refl }
