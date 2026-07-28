------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
--
-- ⟡sign-hom-perm — THE PERMUTATION SIGN HOMOMORPHISM sign : Perm n → Bool
-- (false = even, true = odd), with multiplicativity
--
--     sign-hom : sign (compose σ τ) ≡ sign σ xor sign τ
--
-- computed as the PARITY OF THE INVERSION COUNT (a xor-fold over pairs), and
-- proven multiplicative by REDUCING to ONE combinatorial lemma via the
-- just-landed `coxeter-complete` (OrientationRigCatPermCoxeterGeneral.Properties):
-- every permutation is a word in adjacent transpositions, so multiplicativity
-- is an induction on the CoxGen derivation whose only non-formal step is the
--
--   THE CRUX — flip-lemma :  sign (compose σ (sadj n j)) ≡ not (sign σ)
--
-- right-multiplying by the adjacent transposition sadj swaps two ADJACENT
-- ENTRIES of σ, changing the inversion parity by exactly one. Proven at the
-- vector level (`sign-swap`: swapping two distinct adjacent entries flips the
-- parity, since every unaffected pair contributes twice — cancels in the
-- xor-fold — and only the swapped pair itself flips) plus the bridge
-- `compose σ (sadj n j) ≡ swapAdj j σ` (sadj realizes the index transposition
-- `tp`, and swapAdj is precomposition with it).
--
-- THE REDUCTION (coxeter-complete pays off here):
--   signW      : CoxGen τ → Bool          -- parity of the #cox-s constructors
--   sign-mult  : sign (compose σ τ) ≡ sign σ xor signW g        (induction on g)
--   sign-wd    : sign τ ≡ signW g                               (sign-mult at σ=id)
--   sign-hom   : sign (compose σ τ) ≡ sign σ xor sign τ         (via coxeter-complete)
--
-- HONEST SCOPE — FULL theorem: zero postulates, zero holes, --safe --without-K,
-- GREEN. One faithful STRENGTHENING vs. the loose task statement: the flip-lemma
-- and hence sign-mult / sign-hom require `IsPerm σ` on the LEFT factor as well.
-- This is NECESSARY, not incidental: for a non-injective σ (e.g. σ = [0,0]) the
-- two swapped values can coincide, the swapped pair does NOT flip, and both
-- flip-lemma and sign-hom are FALSE (checked: σ=[0,0], τ=s₁ gives
-- sign(compose)=false but sign σ xor sign τ = true). The numpy verification was
-- "over all PERMS", so it never exhibited the counterexample; the injectivity
-- hypothesis restores exactly it. So `sign-hom` here takes IsPerm σ AND IsPerm τ.
--
-- This module declares NO data/record (pure proof side): it freely imports the
-- proof-carrying modules (SnGroup, CoxeterGeneral.Properties, …).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermSign where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; suc-injective)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Sucinjective
open import Substrate.Foundation.Fin.Op2
open import Substrate.Foundation.Fin.Properties using (toℕ-injective)
open import Substrate.Foundation.Fin.Raise using (raise)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; map; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate; vec-ext)
open import Substrate.Foundation.Eq using (_≡_; _≢_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Bool using (Bool; true; false; not; _xor_)
open import Substrate.Foundation.Bool.Properties
  using (xor-comm; xor-assoc; xor-identityˡ; xor-identityʳ)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.SnGroup
  using (apply-injective; apply-compose; apply-id; compose-id-left; compose-id-right;
         compose-is-perm)
open import Substrate.WitnessTower.CyclicGrounding using (compose-assoc)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; lookup-map)
open import Substrate.WitnessTower.Wedge.OrientationDistributor
  using (blockSum; blockSum-inject; blockSum-raise)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
  using (s₁; sadj; inj1; CoxGen; cox-id; cox-s; cox-∘)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
  using (coxeter-complete; toℕ-inj1)

------------------------------------------------------------------------
-- 0. Small Bool / ℕ helpers (pure, case-analytical).
------------------------------------------------------------------------

-- boolean strict-less on ℕ; matched on the 2nd arg so `_ <ᵇ zero` = false.
_<ᵇ_ : ℕ → ℕ → Bool
_     <ᵇ zero  = false
zero  <ᵇ suc _ = true
suc m <ᵇ suc n = m <ᵇ n

-- trichotomy as a Bool identity: distinct ⇒ exactly one is the lesser.
ltb-not : (a b : ℕ) → ¬ (a ≡ b) → (a <ᵇ b) ≡ not (b <ᵇ a)
ltb-not zero    zero    ne = ⊥-elim (ne refl)
ltb-not zero    (suc b) ne = refl
ltb-not (suc a) zero    ne = refl
ltb-not (suc a) (suc b) ne = ltb-not a b (λ e → ne (cong suc e))

-- a xor (not b) ≡ not (a xor b).
xor-not-r : (a b : Bool) → a xor (not b) ≡ not (a xor b)
xor-not-r true  true  = refl
xor-not-r true  false = refl
xor-not-r false true  = refl
xor-not-r false false = refl

-- b xor true ≡ not b.
xor-trueʳ : (b : Bool) → b xor true ≡ not b
xor-trueʳ true  = refl
xor-trueʳ false = refl

-- the four-term rearrangement at the heart of the base flip: replacing the
-- lead bit by its negation and swapping the two middle bits ⇒ overall negation.
flipBool : (a px py sz : Bool) →
           ((not a) xor py) xor (px xor sz) ≡ not ((a xor px) xor (py xor sz))
flipBool true  true  true  true  = refl
flipBool true  true  true  false = refl
flipBool true  true  false true  = refl
flipBool true  true  false false = refl
flipBool true  false true  true  = refl
flipBool true  false true  false = refl
flipBool true  false false true  = refl
flipBool true  false false false = refl
flipBool false true  true  true  = refl
flipBool false true  true  false = refl
flipBool false true  false true  = refl
flipBool false true  false false = refl
flipBool false false true  true  = refl
flipBool false false true  false = refl
flipBool false false false true  = refl
flipBool false false false false = refl

-- a ℕ never equals its own successor.
n≢sucn : (a : ℕ) → ¬ (a ≡ suc a)
n≢sucn zero    ()
n≢sucn (suc a) e = n≢sucn a (suc-injective e)

------------------------------------------------------------------------
-- 1. sign — parity of the inversion count of an image vector, as a xor-fold.
--    finLt y x = "y < x": counts (position-of-x , position-of-y) as an
--    inversion when x precedes y and x > y.
------------------------------------------------------------------------

finLt : {m : ℕ} → Fin m → Fin m → Bool
finLt i j = toℕ i <ᵇ toℕ j

-- parity of the number of tail entries strictly below the head value x.
parityLess : {m n : ℕ} → Fin m → Vec (Fin m) n → Bool
parityLess x []       = false
parityLess x (y ∷ ys) = finLt y x xor parityLess x ys

sign : {m n : ℕ} → Vec (Fin m) n → Bool
sign []       = false
sign (x ∷ xs) = parityLess x xs xor sign xs

------------------------------------------------------------------------
-- 2. The adjacent-swap index map `tp`, its involutivity, and the
--    swap-on-vectors operation `swapAdj` (precomposition with `tp`).
------------------------------------------------------------------------

tp : {n : ℕ} → Fin n → Fin (suc n) → Fin (suc n)
tp zero    zero          = suc zero
tp zero    (suc zero)    = zero
tp zero    (suc (suc i)) = suc (suc i)
tp (suc j) zero          = zero
tp (suc j) (suc i)       = suc (tp j i)

tp-inv : {n : ℕ} (j : Fin n) (i : Fin (suc n)) → tp j (tp j i) ≡ i
tp-inv zero    zero          = refl
tp-inv zero    (suc zero)    = refl
tp-inv zero    (suc (suc i)) = refl
tp-inv (suc j) zero          = refl
tp-inv (suc j) (suc i)       = cong suc (tp-inv j i)

tp-injective : {n : ℕ} (j : Fin n) (a b : Fin (suc n)) → tp j a ≡ tp j b → a ≡ b
tp-injective j a b e = trans (sym (tp-inv j a)) (trans (cong (tp j) e) (tp-inv j b))

swapAdj : {A : Set} {n : ℕ} → Fin n → Vec A (suc n) → Vec A (suc n)
swapAdj zero    (x ∷ y ∷ zs) = y ∷ x ∷ zs
swapAdj (suc j) (x ∷ xs)     = x ∷ swapAdj j xs

-- swapAdj is precomposition with tp.
swapAdj-lookup : {A : Set} {n : ℕ} (j : Fin n) (v : Vec A (suc n)) (i : Fin (suc n)) →
                 lookup (swapAdj j v) i ≡ lookup v (tp j i)
swapAdj-lookup zero    (x ∷ y ∷ zs) zero          = refl
swapAdj-lookup zero    (x ∷ y ∷ zs) (suc zero)    = refl
swapAdj-lookup zero    (x ∷ y ∷ zs) (suc (suc i)) = refl
swapAdj-lookup (suc j) (x ∷ xs)     zero          = refl
swapAdj-lookup (suc j) (x ∷ xs)     (suc i)       = swapAdj-lookup j xs i

------------------------------------------------------------------------
-- 3. sadj realizes the index transposition tp (same ⊕-recursion as its
--    two swap-action lemmas in CoxeterGeneral.Properties).
------------------------------------------------------------------------

sadj-realizes : (n : ℕ) (j : Fin n) (i : Fin (suc n)) →
                lookup (sadj n j) i ≡ tp j i
sadj-realizes (suc n) zero    zero          = blockSum-inject s₁ (id-perm n) zero
sadj-realizes (suc n) zero    (suc zero)    = blockSum-inject s₁ (id-perm n) (suc zero)
sadj-realizes (suc n) zero    (suc (suc i)) =
  trans (blockSum-raise s₁ (id-perm n) i) (cong (raise 2) (apply-id i))
sadj-realizes (suc n) (suc j) zero          =
  blockSum-inject (id-perm 1) (sadj n j) zero
sadj-realizes (suc n) (suc j) (suc i)       =
  trans (blockSum-raise (id-perm 1) (sadj n j) i) (cong suc (sadj-realizes n j i))

-- the bridge: right-multiplying by sadj swaps the two adjacent entries.
bridge : {n : ℕ} (σ : Perm (suc n)) (j : Fin n) →
         compose σ (sadj n j) ≡ swapAdj j σ
bridge σ j = apply-injective (λ i →
  trans (apply-compose σ (sadj _ j) i)
        (trans (cong (lookup σ) (sadj-realizes _ j i))
               (sym (swapAdj-lookup j σ i))))

------------------------------------------------------------------------
-- 4. The vector-level flip: parityLess is swap-invariant; sign flips when
--    two DISTINCT adjacent entries are swapped.
------------------------------------------------------------------------

-- structural "the two swapped entries differ".
AdjNeq : {m n : ℕ} → Fin n → Vec (Fin m) (suc n) → Set
AdjNeq zero    (x ∷ y ∷ _) = ¬ (x ≡ y)
AdjNeq (suc j) (x ∷ xs)    = AdjNeq j xs

-- parityLess is invariant under an adjacent swap (xor-fold reordering).
pLess-swap : {m n : ℕ} (x : Fin m) (j : Fin n) (v : Vec (Fin m) (suc n)) →
             parityLess x (swapAdj j v) ≡ parityLess x v
pLess-swap x zero (a ∷ b ∷ zs) =
  trans (sym (xor-assoc (finLt b x) (finLt a x) (parityLess x zs)))
        (trans (cong (λ w → w xor parityLess x zs) (xor-comm (finLt b x) (finLt a x)))
               (xor-assoc (finLt a x) (finLt b x) (parityLess x zs)))
pLess-swap x (suc j) (a ∷ xs) =
  cong (λ w → finLt a x xor w) (pLess-swap x j xs)

-- distinct swapped adjacent entries ⇒ the sign flips.
sign-swap : {m n : ℕ} (j : Fin n) (v : Vec (Fin m) (suc n)) →
            AdjNeq j v → sign (swapAdj j v) ≡ not (sign v)
sign-swap zero (x ∷ y ∷ zs) h =
  trans (cong (λ w → (w xor parityLess y zs) xor (parityLess x zs xor sign zs))
              (finLt-xy))
        (flipBool (finLt y x) (parityLess x zs) (parityLess y zs) (sign zs))
  where
  finLt-xy : finLt x y ≡ not (finLt y x)
  finLt-xy = ltb-not (toℕ x) (toℕ y) (λ e → h (toℕ-injective e))
sign-swap (suc j) (x ∷ xs) h =
  trans (cong₂ _xor_ (pLess-swap x j xs) (sign-swap j xs h))
        (xor-not-r (parityLess x xs) (sign xs))

------------------------------------------------------------------------
-- 5. From IsPerm σ to AdjNeq (the swapped entries are distinct because
--    lookup is injective and the two swapped indices inj1 j / suc j differ).
------------------------------------------------------------------------

adjneq-from : {m n : ℕ} (j : Fin n) (v : Vec (Fin m) (suc n)) →
              ¬ (lookup v (inj1 j) ≡ lookup v (suc j)) → AdjNeq j v
adjneq-from zero    (x ∷ y ∷ zs) hyp = hyp
adjneq-from (suc j) (x ∷ xs)     hyp = adjneq-from j xs hyp

inj1≢suc : {n : ℕ} (j : Fin n) → ¬ (inj1 j ≡ suc j)
inj1≢suc j e = n≢sucn (toℕ j) (trans (sym (toℕ-inj1 j)) (cong toℕ e))

isperm→adjneq : {n : ℕ} (j : Fin n) (σ : Perm (suc n)) → IsPerm σ → AdjNeq j σ
isperm→adjneq j σ pf =
  adjneq-from j σ (λ e → inj1≢suc j (pf (inj1 j) (suc j) e))

------------------------------------------------------------------------
-- 6. THE FLIP-LEMMA (the crux) and the base cases.
------------------------------------------------------------------------

flip-lemma : {n : ℕ} (σ : Perm (suc n)) (j : Fin n) →
             IsPerm σ → sign (compose σ (sadj n j)) ≡ not (sign σ)
flip-lemma σ j pf =
  trans (cong sign (bridge σ j)) (sign-swap j σ (isperm→adjneq j σ pf))

-- id-perm is a permutation.
id-perm-is-perm : {n : ℕ} → IsPerm (id-perm n)
id-perm-is-perm i j e = trans (sym (apply-id i)) (trans e (apply-id j))

-- sadj is a permutation (its action is tp, which is injective).
sadj-is-perm : (n : ℕ) (j : Fin n) → IsPerm (sadj n j)
sadj-is-perm n j a b e =
  tp-injective j a b
    (trans (sym (sadj-realizes n j a)) (trans e (sadj-realizes n j b)))

-- sign of the identity is false (no inversions). id-perm(suc n) = zero ∷ ...,
-- and zero is the minimum so parityLess zero = false; the tail is the identity
-- shifted up by suc, and sign is invariant under that shift.
parityLess-zero : {m n : ℕ} (v : Vec (Fin (suc m)) n) → parityLess (zero {m}) v ≡ false
parityLess-zero []       = refl
parityLess-zero (y ∷ ys) = parityLess-zero ys

parityLess-suc : {m n : ℕ} (x : Fin m) (v : Vec (Fin m) n) →
                 parityLess (suc x) (map suc v) ≡ parityLess x v
parityLess-suc x []       = refl
parityLess-suc x (y ∷ ys) = cong (λ w → finLt y x xor w) (parityLess-suc x ys)

sign-map-suc : {m n : ℕ} (v : Vec (Fin m) n) → sign (map suc v) ≡ sign v
sign-map-suc []       = refl
sign-map-suc (x ∷ xs) = cong₂ _xor_ (parityLess-suc x xs) (sign-map-suc xs)

-- id-perm(suc n) = zero ∷ (each old index raised by suc).
id-perm-cons : {n : ℕ} → id-perm (suc n) ≡ zero ∷ map suc (id-perm n)
id-perm-cons {n} = vec-ext _ _ aux
  where
  aux : (k : Fin (suc n)) →
        lookup (id-perm (suc n)) k ≡ lookup (zero ∷ map suc (id-perm n)) k
  aux zero     = apply-id zero
  aux (suc k') =
    trans (apply-id (suc k'))
          (trans (cong suc (sym (apply-id k')))
                 (sym (lookup-map suc (id-perm n) k')))

sign-id : {n : ℕ} → sign (id-perm n) ≡ false
sign-id {zero}   = refl
sign-id {suc n'} =
  trans (cong sign (id-perm-cons {n'}))
    (trans (cong (λ b → b xor sign (map suc (id-perm n')))
                 (parityLess-zero (map suc (id-perm n'))))
           (trans (sign-map-suc (id-perm n')) (sign-id {n'})))

------------------------------------------------------------------------
-- 7. THE REDUCTION via coxeter-complete: multiplicativity, well-definedness,
--    and the clean homomorphism.
------------------------------------------------------------------------

module Reduction where

  -- parity of the number of cox-s constructors in the derivation.
  signW : {n : ℕ} {τ : Perm n} → CoxGen τ → Bool
  signW cox-id      = false
  signW (cox-s j)   = true
  signW (cox-∘ g h) = signW g xor signW h

  -- every CoxGen witness is a genuine permutation.
  coxgen→isperm : {n : ℕ} {τ : Perm n} → CoxGen τ → IsPerm τ
  coxgen→isperm cox-id      = id-perm-is-perm
  coxgen→isperm (cox-s j)   = sadj-is-perm _ j
  coxgen→isperm (cox-∘ {σ = a} {τ = b} g h) =
    compose-is-perm a b (coxgen→isperm g) (coxgen→isperm h)

  -- MULTIPLICATIVITY over the derivation (needs IsPerm on the left factor).
  sign-mult : {n : ℕ} (σ : Perm n) → IsPerm σ → {τ : Perm n} (g : CoxGen τ) →
              sign (compose σ τ) ≡ sign σ xor signW g
  sign-mult σ pf cox-id =
    trans (cong sign (compose-id-right σ)) (sym (xor-identityʳ (sign σ)))
  sign-mult σ pf (cox-s j) =
    trans (flip-lemma σ j pf) (sym (xor-trueʳ (sign σ)))
  sign-mult σ pf (cox-∘ {σ = τ₁} {τ = τ₂} g h) =
    trans (cong sign (sym (compose-assoc σ τ₁ τ₂)))
      (trans (sign-mult (compose σ τ₁) (compose-is-perm σ τ₁ pf (coxgen→isperm g)) h)
        (trans (cong (λ b → b xor signW h) (sign-mult σ pf g))
               (xor-assoc (sign σ) (signW g) (signW h))))

  -- sign of τ is read off ANY derivation of τ (sign-mult at σ = id).
  sign-wd : {n : ℕ} {τ : Perm n} (g : CoxGen τ) → sign τ ≡ signW g
  sign-wd {n} {τ} g =
    trans (cong sign (sym (compose-id-left τ)))
      (trans (sign-mult (id-perm n) (id-perm-is-perm {n}) g)
             (trans (cong (λ b → b xor signW g) (sign-id {n})) (xor-identityˡ (signW g))))

  -- THE HOMOMORPHISM: sign (σ ∘ τ) = sign σ xor sign τ (both permutations).
  sign-hom : {n : ℕ} (σ τ : Perm n) → IsPerm σ → IsPerm τ →
             sign (compose σ τ) ≡ sign σ xor sign τ
  sign-hom σ τ pfσ pfτ =
    trans (sign-mult σ pfσ (coxeter-complete τ pfτ))
          (cong (λ b → sign σ xor b) (sym (sign-wd (coxeter-complete τ pfτ))))

open Reduction public

-- base case: an adjacent transposition is odd.
sign-sadj : (n : ℕ) (j : Fin n) → sign (sadj n j) ≡ true
sign-sadj n j = sign-wd (cox-s j)
