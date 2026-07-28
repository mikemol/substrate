------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Prime.Properties
--
-- The proofs for `Algebra.Nat.Prime`: divisibility as the div-mod wedge with
-- remainder 0, decidable divisibility (the converse via mod uniqueness), the
-- bounded least-divisor search, and the factorisation EXISTENCE theorem
-- `factorize!` — every positive ℕ is a product of primes, the wedge iterated by
-- least prime divisor, well-founded on the strictly-decreasing quotient. This
-- is the FTA-existence half = the surjectivity the Ω3-L-primes ℤ-power codec
-- needs (every positive ℚ is a product of prime powers).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Prime.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_; _≤_; _<_; s≤s; z≤n; _≟_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂; _×_)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.List using (List; []; _∷_; _++_; foldr)
open import Substrate.Foundation.List.Any using (Any; here; there; _∈_)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm; +-identityʳ)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-comm; *-assoc; *-identityʳ; *-identityˡ; *-suc)
open import Substrate.Foundation.Nat.Properties.Order
  using (m≤m+n; n≤m+n; ≤-refl; ≤-suc-r; <-suc-r; <-suc-self; <→≤; <-irrefl;
         ≤-trans; ≤-<-trans; ≤-tight; *-monoʳ-≤)
open import Substrate.Algebra.Nat.Divides.Type using (_∣_; divides)
open import Substrate.Algebra.Nat.Divides.Refl using (∣-refl)
open import Substrate.Algebra.Nat.Divides.Trans using (∣-trans)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)
open import Substrate.Algebra.Nat.DivMod.DivSuc using (_div-suc_)
open import Substrate.Algebra.Nat.DivMod.Reconstruction using (div-mod-eq)
open import Substrate.Algebra.Nat.DivMod.Unique using (divmod-unique)
open import Substrate.Algebra.Nat.WellFounded using (<-wellFounded)
open import Substrate.Algebra.Quotient
open import Substrate.Algebra.Nat.GCD.GcdPos using (gcd-pos)
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft using (gcd-divides-left)
open import Substrate.Algebra.Nat.GCD.GcdDividesRight using (gcd-divides-right)
open import Substrate.Algebra.Z.Euclid using (euclid)
open import Substrate.Algebra.Nat.Prime using (IsPrime; product; AllPrime; []ᴾ; _∷ᴾ_; Factored)

------------------------------------------------------------------------
-- 1. The wedge with remainder 0: a zero remainder IS divisibility, the
--    quotient (the wedge residue) the cofactor.
------------------------------------------------------------------------

mod0→∣ : (n d : ℕ) → n mod-suc d ≡ 0 → suc d ∣ n
mod0→∣ n d eq =
  divides (n div-suc d)
    (trans (div-mod-eq n d)
           (cong (λ r → r + (n div-suc d) * suc d) eq))

-- the bridge fires computationally: 2 ∣ 6 (6 mod 2 = 0 by refl).
2∣6 : 2 ∣ 6
2∣6 = mod0→∣ 6 1 refl

------------------------------------------------------------------------
-- 2. Decidable divisibility: the converse (a divisor forces remainder 0, by
--    mod uniqueness), so `suc d ∣? n` decides via `n mod-suc d ≟ 0`.
------------------------------------------------------------------------

∣→mod0 : (n d : ℕ) → suc d ∣ n → n mod-suc d ≡ 0
∣→mod0 n d (divides q n≡q*sd) =
  sym (proj₂ (divmod-unique q (n div-suc d) zero (n mod-suc d) d
                (s≤s z≤n) (mod-suc-bound n d) eqn))
  where
    eqn : q * suc d + zero ≡ (n div-suc d) * suc d + (n mod-suc d)
    eqn = trans (+-identityʳ (q * suc d))
           (trans (sym n≡q*sd)
             (trans (div-mod-eq n d)
                    (+-comm (n mod-suc d) ((n div-suc d) * suc d))))

_∣suc?_ : (d n : ℕ) → Dec (suc d ∣ n)
d ∣suc? n with (n mod-suc d) ≟ zero
... | yes eq  = yes (mod0→∣ n d eq)
... | no  ¬eq = no λ div → ¬eq (∣→mod0 n d div)

-- a divisor of a positive number is ≤ it.
∣→≤ : (d n : ℕ) → d ∣ suc n → d ≤ suc n
∣→≤ d n (divides zero ())
∣→≤ d n (divides (suc q) eq) =
  subst (λ x → d ≤ x) (sym eq) (m≤m+n d (q * d))

------------------------------------------------------------------------
-- 3. The bounded least-divisor search → a primality decision.
------------------------------------------------------------------------

2≤→¬<2 : (d : ℕ) → 2 ≤ d → d < 2 → ⊥
2≤→¬<2 d 2≤d d<2 = <-irrefl 2 (≤-<-trans 2≤d d<2)

≤→<⊎≡ : (d b : ℕ) → d ≤ b → (d < b) ⊎ (d ≡ b)
≤→<⊎≡ zero    zero    _         = inj₂ refl
≤→<⊎≡ zero    (suc b) _         = inj₁ (s≤s z≤n)
≤→<⊎≡ (suc d) zero    ()
≤→<⊎≡ (suc d) (suc b) (s≤s d≤b) with ≤→<⊎≡ d b d≤b
... | inj₁ d<b = inj₁ (s≤s d<b)
... | inj₂ d≡b = inj₂ (cong suc d≡b)

-- given no divisor in [2,c) and c < n, either c ∣ n (a proper divisor found)
-- or the no-divisor certificate extends to [2, suc c).
step-candidate : (n c : ℕ) → c < n →
  ((d : ℕ) → 2 ≤ d → d < c → ¬ (d ∣ n)) →
  (Σ ℕ (λ d → (2 ≤ d) × (d < n) × (d ∣ n))) ⊎
  ((d : ℕ) → 2 ≤ d → d < suc c → ¬ (d ∣ n))
step-candidate n zero          _   _    =
  inj₂ (λ d 2≤d d<1 → ⊥-elim (2≤→¬<2 d 2≤d (<-suc-r d<1)))
step-candidate n (suc zero)    _   _    =
  inj₂ (λ d 2≤d d<2 → ⊥-elim (2≤→¬<2 d 2≤d d<2))
step-candidate n (suc (suc c')) c<n none with (suc c') ∣suc? n
... | yes c∣n  = inj₁ (suc (suc c') , s≤s (s≤s z≤n) , c<n , c∣n)
... | no ¬c∣n  = inj₂ ext
  where
    ext : (d : ℕ) → 2 ≤ d → d < suc (suc (suc c')) → ¬ (d ∣ n)
    ext d 2≤d (s≤s d≤ssc') d∣n with ≤→<⊎≡ d (suc (suc c')) d≤ssc'
    ... | inj₁ d<ssc' = none d 2≤d d<ssc' d∣n
    ... | inj₂ d≡ssc' = ¬c∣n (subst (λ x → x ∣ n) d≡ssc' d∣n)

-- search all candidates below `bound` for a proper divisor of n.
search : (n bound : ℕ) → bound ≤ n →
  (Σ ℕ (λ d → (2 ≤ d) × (d < n) × (d ∣ n))) ⊎
  ((d : ℕ) → 2 ≤ d → d < bound → ¬ (d ∣ n))
search n zero    _     = inj₂ (λ d _ ())
search n (suc b) sb≤n with search n b (≤-trans (≤-suc-r (≤-refl b)) sb≤n)
... | inj₁ found = inj₁ found
... | inj₂ none  = step-candidate n b sb≤n none

-- n ≥ 2 is prime, or has a proper divisor.
primality-decision : (n : ℕ) → 2 ≤ n →
  IsPrime n ⊎ (Σ ℕ (λ d → (2 ≤ d) × (d < n) × (d ∣ n)))
primality-decision zero       ()
primality-decision (suc zero) (s≤s ())
primality-decision (suc (suc n'')) 2≤n with search (suc (suc n'')) (suc (suc n'')) (≤-refl _)
... | inj₁ found = inj₂ found
... | inj₂ none  = inj₁ (2≤n , prime-proof)
  where
    prime-proof : (d : ℕ) → d ∣ suc (suc n'') → 2 ≤ d → d ≡ suc (suc n'')
    prime-proof d d∣n 2≤d with ≤→<⊎≡ d (suc (suc n'')) (∣→≤ d (suc n'') d∣n)
    ... | inj₁ d<n = ⊥-elim (none d 2≤d d<n d∣n)
    ... | inj₂ d≡n = d≡n

------------------------------------------------------------------------
-- 4. The factorisation EXISTENCE theorem: the div-mod wedge iterated by the
--    least prime divisor, well-founded on the strictly-decreasing quotient.
------------------------------------------------------------------------

-- a positive quotient against a factor ≥ 2 strictly decreases: q < q·p.
q<q*p : (q' p : ℕ) → 2 ≤ p → suc q' < suc q' * p
q<q*p q' p 2≤p = ≤-trans sucq≤q*2 q*2≤q*p
  where
    q*2≡q+q : suc q' * 2 ≡ suc q' + suc q'
    q*2≡q+q = trans (*-suc (suc q') (suc zero)) (cong (suc q' +_) (*-identityʳ (suc q')))
    sucq≤q+q : suc (suc q') ≤ suc q' + suc q'
    sucq≤q+q = s≤s (n≤m+n q' (suc q'))
    sucq≤q*2 : suc (suc q') ≤ suc q' * 2
    sucq≤q*2 = subst (λ x → suc (suc q') ≤ x) (sym q*2≡q+q) sucq≤q+q
    q*2≤q*p : suc q' * 2 ≤ suc q' * p
    q*2≤q*p = *-monoʳ-≤ (suc q') 2≤p

-- every n ≥ 2 has a PRIME divisor (recurse a proper divisor down to a prime).
prime-divisor : (n : ℕ) → Acc _<_ n → 2 ≤ n → Σ ℕ (λ p → IsPrime p × (p ∣ n))
prime-divisor n (acc rec) 2≤n with primality-decision n 2≤n
... | inj₁ n-prime              = n , n-prime , ∣-refl
... | inj₂ (d , 2≤d , d<n , d∣n) =
      let ih = prime-divisor d (rec d d<n) 2≤d
      in proj₁ ih , proj₁ (proj₂ ih) , ∣-trans (proj₂ (proj₂ ih)) d∣n

-- THE EXISTENCE THEOREM: every positive ℕ is a product of primes.
factorize : (n : ℕ) → Acc _<_ n → 1 ≤ n → Factored n
factorize zero            _         ()
factorize (suc zero)      _         _ = [] , []ᴾ , refl
factorize (suc (suc n'')) (acc rec) _
  with prime-divisor (suc (suc n'')) (<-wellFounded _) (s≤s (s≤s z≤n))
... | (p , p-prime , divides zero ())
... | (p , p-prime , divides (suc q') n≡q*p) =
      let q<n = subst (λ x → suc q' < x) (sym n≡q*p)
                  (q<q*p q' p (proj₁ p-prime))
          ih  = factorize (suc q') (rec (suc q') q<n) (s≤s z≤n)
      in p ∷ proj₁ ih
       , p-prime ∷ᴾ proj₁ (proj₂ ih)
       , trans (cong (p *_) (proj₂ (proj₂ ih)))
               (trans (*-comm p (suc q')) (sym n≡q*p))

-- the wrapper: well-foundedness supplied.
factorize! : (n : ℕ) → 1 ≤ n → Factored n
factorize! n = factorize n (<-wellFounded n)

------------------------------------------------------------------------
-- 7. UNIQUENESS kernel (Ⓝ.u): Euclid's lemma for PRIMES. The coprime-form
--    `euclid` rides on `bezout-ℤ` (the EEA trace's residue, never-discarded);
--    a prime is coprime to anything it does not divide (its only divisors are 1
--    and itself), so it LIFTS to: p ∣ a·b ⟹ p∣a or p∣b — the heart of FTA
--    uniqueness (the multiset of primes is forced).
------------------------------------------------------------------------

prime-divides-product : ∀ {p} → IsPrime p → (a b : ℕ) → p ∣ (a * b) → (p ∣ a) ⊎ (p ∣ b)
prime-divides-product {zero}    pp _ _ _    with proj₁ pp
... | ()
prime-divides-product {suc zero} pp _ _ _   with proj₁ pp
... | (s≤s ())
prime-divides-product {suc (suc m'')} pp a b p∣ab with gcd-pos a (suc m'')
... | (zero    , gcd≡1) = inj₂ (euclid a (suc m'') b gcd≡1 p∣ab)
... | (suc g'' , gcd≡g) = inj₁ (subst (λ x → x ∣ a) g≡p g∣a)
  where
    g∣a : suc (suc g'') ∣ a
    g∣a = subst (λ x → x ∣ a) gcd≡g (gcd-divides-left a (suc (suc m'')))
    g∣p : suc (suc g'') ∣ suc (suc m'')
    g∣p = subst (λ x → x ∣ suc (suc m'')) gcd≡g (gcd-divides-right a (suc (suc m'')))
    g≡p : suc (suc g'') ≡ suc (suc m'')
    g≡p = proj₂ pp (suc (suc g'')) g∣p (s≤s (s≤s z≤n))

-- a prime dividing a prime forces equality (immediate from IsPrime: the divisor
-- is ≥ 2, so it IS the prime). The atom uniqueness rests on.
prime∣prime→≡ : ∀ {p q} → IsPrime p → IsPrime q → p ∣ q → p ≡ q
prime∣prime→≡ pp qq p∣q = proj₂ qq _ p∣q (proj₁ pp)

-- THE CAPSTONE: a prime dividing a product of primes IS one of them. By
-- induction on the prime list using `prime-divides-product` at each step; the
-- empty case is impossible (a prime ≥2 cannot divide the empty product 1).
-- Combined with existence (factorize!), this forces the prime multiset — FTA
-- uniqueness in the form the codec needs (the "log" is well-defined).
prime-∈-product : ∀ {p qs} → IsPrime p → AllPrime qs → p ∣ product qs → p ∈ qs
prime-∈-product {p} {[]}       pp []ᴾ          p∣1
  with ≤-trans (proj₁ pp) (∣→≤ p zero p∣1)
... | (s≤s ())
prime-∈-product {p} {q ∷ rest} pp (qp ∷ᴾ restp) p∣qr
  with prime-divides-product pp q (product rest) p∣qr
... | inj₁ p∣q    = here (prime∣prime→≡ pp qp p∣q)
... | inj₂ p∣rest = there (prime-∈-product pp restp p∣rest)

------------------------------------------------------------------------
-- 8. Ⓝ.iso: the prime factorisation as a SPLIT-CANONICAL retraction.
--    `factorize!` gives product ∘ factorize ≡ id (the existence round-trip), a
--    retraction — so by the split-idempotent apex (`split-Canonical`) the
--    positive naturals ARE a section-based quotient: ℕ⁺ ≅ {canonical prime
--    factorisations} (the image of `factorize`), NO quotient type. (A positive
--    n is `suc m`; the carrier value is `pred (product ps)`, so the retraction
--    is total: pred (product (factorize (suc m))) = pred (suc m) = m.)
--    The same apex as eval/reify, ℚ reduce, the wedge recon (project_split_idempotent_apex).
------------------------------------------------------------------------

private
  pred : ℕ → ℕ
  pred zero    = zero
  pred (suc n) = n

-- F : the carrier value (positive n ↦ n−1, so the retraction is total on ℕ).
factor-value : List ℕ → ℕ
factor-value ps = pred (product ps)

-- s : the section — the prime factorisation of the positive number suc m.
factor-section : ℕ → List ℕ
factor-section m = proj₁ (factorize! (suc m) (s≤s z≤n))

-- F ∘ s ≡ id: pred (product (factorize (suc m))) ≡ pred (suc m) ≡ m.
factor-retract : (m : ℕ) → factor-value (factor-section m) ≡ m
factor-retract m = cong pred (proj₂ (proj₂ (factorize! (suc m) (s≤s z≤n))))

-- the section's product is the original positive: product (factorize (suc m)) ≡ suc m.
-- (The existence round-trip, exposed directly for the ℚ₊ lift.)
factor-section-product : (m : ℕ) → product (factor-section m) ≡ suc m
factor-section-product m = proj₂ (proj₂ (factorize! (suc m) (s≤s z≤n)))

-- THE ISO: the split idempotent factor-section ∘ factor-value is a Canonical
-- for ker factor-value — ℕ⁺ ≅ canonical prime factorisations, from the
-- retraction alone (uniqueness/.u2 then characterises the image as THE multiset).
factor-Canonical : Canonical (ker-Quotient factor-value)
factor-Canonical = split-Canonical factor-value factor-section factor-retract

------------------------------------------------------------------------
-- 9. Ⓝ.iso2: the ⊕ STRUCTURE — the iso is a MONOID HOMOMORPHISM, not just a
--    bijection. `product` carries (List ℕ, ++, []) → (ℕ, ·, 1): concatenating
--    factor lists MULTIPLIES the values, i.e. ADDING exponents (++ = multiset
--    union) ↦ multiplying — the additive ⊕ of ℚ₊ ≅ ⊕primesℤ, at the ℕ⁺ level.
--    (This is the hom that turns · into +, the engine of L_OR = LogSumExp.)
------------------------------------------------------------------------

-- product is a monoid hom: product (xs ++ ys) ≡ product xs · product ys.
product-++ : (xs ys : List ℕ) → product (xs ++ ys) ≡ product xs * product ys
product-++ []       ys = sym (*-identityˡ (product ys))
product-++ (x ∷ xs) ys =
  trans (cong (x *_) (product-++ xs ys))
        (sym (*-assoc x (product xs) (product ys)))

-- the unit: product [] ≡ 1 (the empty factorisation is the multiplicative
-- identity = the zero exponent vector). Definitional, named for the hom.
product-[] : product [] ≡ 1
product-[] = refl
