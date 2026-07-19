------------------------------------------------------------------------
-- Substrate.WitnessTower.InsertionParity
--
-- ◆tighten-insertion-parity — discharge LehmerTowerMorphism's open
-- obligation (the factoradic-digit ↔ inversion-count-parity fact) via TWO
-- INDEPENDENT routes, then reconcile them (coverage: two derivations
-- cross-validate the fact; their agreement — or precise distinction — is a
-- co-apex linking the inversion-count view and the rotation/Coxeter view).
--
-- THE FACT (single-insertion parity): inserting value p at the front of a
-- permutation (insert-at p σ = p ∷ map (punchIn p) σ) flips the sign by the
-- parity of p:
--     sign (insert-at p σ) ≡ finParity-bool p  xor  sign σ        (σ a perm)
--   ⟹ signF (decode (l ◂ p)) ≡ finParity p + signF (decode l).
--
-- Route A (COUNTING): the head p contributes #{tail entries < p} inversions;
--   for a permutation the tail is exactly Fin(suc n)∖{p}, so that count is p.
-- Route B (ROTATION): insert-at p σ = map (ρ p) (insert-at 0 σ) with ρ p the
--   head-to-rank-p rotation; sign is (rotation sign) xor (relabel-invariant base).
--
-- This module first builds the SHARED pieces (finParity = parity ∘ toℕ; the
-- punchIn-order relabel invariance of sign), then each route's core.
--
-- --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.InsertionParity where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _<_; _≤_; s≤s; z≤n; suc-injective)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong; cong₂)
open import Substrate.Foundation.Bool using (Bool; true; false; _xor_; not)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map; lookup)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _≟_) renaming (_+_ to _+F_)
open import Substrate.Foundation.Hedberg using (Decidable⇒UIP)
open import Substrate.Algebra.F2.FromBool using (bool→F₂; bool→F₂-xor)
open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)

open import Substrate.Foundation.Fin.Properties using (toℕ-injective; toℕ-bound)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; insert-at-preserves; lookup-map)
open import Substrate.WitnessTower.SnGroup using (apply-id; compose-id-left; compose-id-right)
open import Substrate.WitnessTower.CyclicGrounding using (compose-assoc)
open import Substrate.WitnessTower.Decompose using (lookup-ext)
open import Substrate.WitnessTower.Wedge.OrientationRigFree using (ρ; insert-at-rot)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; decode; _◂_; decode-is-perm)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
  using (sign; parityLess; parityLess-zero; sign-map-suc; sign-id; sign-sadj;
         sign-hom; sadj-is-perm; id-perm-is-perm; finLt; _<ᵇ_;
         swapAdj; pLess-swap; bridge; id-perm-cons; signW; sign-wd)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
  using (sadj; inj1; CoxGen; cox-id; cox-s; cox-∘)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral.Properties
  using (idInsert-step; toℕ-inj1; coxeter-complete; idInsert-CoxGen)
open import Substrate.WitnessTower.LehmerTowerMorphism
  using (finParity; sign-lehmer-morphism; lehmer-graded; F₂-target)
open import Substrate.Algebra.Wedge.Graded.Morphism using (GradedDivStrMorphism)

------------------------------------------------------------------------
-- SHARED 1. finParity IS parity ∘ toℕ (the Fin-digit parity = ℕ parity).
------------------------------------------------------------------------

-- two 𝟙-additions cancel (characteristic 2): 𝟙 + (𝟙 + x) ≡ x.
two-cancel : (x : F₂) → 𝟙 +F (𝟙 +F x) ≡ x
two-cancel 𝟘 = refl
two-cancel 𝟙 = refl

finParity-is-parity : {n : ℕ} (p : Fin n) → finParity p ≡ parity (toℕ p)
finParity-is-parity zero          = refl
finParity-is-parity (suc zero)    = refl
finParity-is-parity (suc (suc p)) =
  trans (finParity-is-parity p) (sym (two-cancel (parity (toℕ p))))

------------------------------------------------------------------------
-- SHARED 2. oddB — the Bool parity of ℕ; its F₂ image is `parity`.
------------------------------------------------------------------------

oddB : ℕ → Bool
oddB zero    = false
oddB (suc n) = not (oddB n)

bool→F₂-oddB : (n : ℕ) → bool→F₂ (oddB n) ≡ parity n
bool→F₂-oddB zero    = refl
bool→F₂-oddB (suc n) = trans (not-lemma (oddB n))
                             (cong (𝟙 +F_) (bool→F₂-oddB n))
  where
    -- bool→F₂ (not b) ≡ 𝟙 + bool→F₂ b, matching parity (suc n) = 𝟙 + parity n.
    not-lemma : (b : Bool) → bool→F₂ (not b) ≡ (𝟙 +F bool→F₂ b)
    not-lemma true  = refl
    not-lemma false = refl

------------------------------------------------------------------------
-- SHARED 3. the p=0 base: sign (insert-at 0 σ) ≡ sign σ. insert-at 0 σ =
-- 0 ∷ map suc σ (punchIn 0 = suc); parityLess 0 = false; sign-map-suc.
------------------------------------------------------------------------

insert-zero-base : {n : ℕ} (σ : Perm n) → sign (insert-at zero σ) ≡ sign σ
insert-zero-base σ =
  trans (cong (_xor sign (map suc σ)) (parityLess-zero (map suc σ)))
        (sign-map-suc σ)

------------------------------------------------------------------------
-- SHARED 4 (◆ip-relabel). punchIn-order relabel invariance of sign.
-- insert-at p σ = p ∷ map (punchIn p) σ (Enumerate:67); the tail factor
-- map (punchIn p) reindexes but preserves the sign (finLt is order-
-- preserving under punchIn — it only shifts positions, never inverts).
------------------------------------------------------------------------

-- finLt is invariant under the (order-preserving) punchIn injection.
finLt-punchIn : {n : ℕ} (p : Fin (suc n)) (a b : Fin n) →
                finLt (punchIn p a) (punchIn p b) ≡ finLt a b
finLt-punchIn zero    a       b       = refl
finLt-punchIn (suc k) zero    zero    = refl
finLt-punchIn (suc k) zero    (suc b) = refl
finLt-punchIn (suc k) (suc a) zero    = refl
finLt-punchIn (suc k) (suc a) (suc b) = finLt-punchIn k a b

-- mirror of parityLess-suc (:285), but punchIn's head is only propositionally
-- equal (via finLt-punchIn), so cong₂ (not the cong of parityLess-suc).
parityLess-punchIn : {n k : ℕ} (p : Fin (suc n)) (x : Fin n) (v : Vec (Fin n) k) →
                     parityLess (punchIn p x) (map (punchIn p) v) ≡ parityLess x v
parityLess-punchIn p x []       = refl
parityLess-punchIn p x (y ∷ ys) =
  cong₂ _xor_ (finLt-punchIn p y x) (parityLess-punchIn p x ys)

-- mirror of sign-map-suc (:290): sign is invariant under the punchIn relabel.
sign-map-punchIn : {n k : ℕ} (p : Fin (suc n)) (v : Vec (Fin n) k) →
                   sign (map (punchIn p) v) ≡ sign v
sign-map-punchIn p []       = refl
sign-map-punchIn p (x ∷ xs) =
  cong₂ _xor_ (parityLess-punchIn p x xs) (sign-map-punchIn p xs)

------------------------------------------------------------------------
-- ROUTE B (◆ip-id-core). The identity-permutation single-insertion.
-- sign (insert-at p (id-perm m)) ≡ oddB (toℕ p), by the bubble fuel:
-- insert-at (suc q') id = sadj q' ∘ insert-at (inj1 q') id (idInsert-step),
-- and sign is a homomorphism sending each adjacent transposition to true.
------------------------------------------------------------------------

ip-id-aux : (k : ℕ) {m : ℕ} (p : Fin (suc m)) →
            toℕ p ≡ k → sign (insert-at p (id-perm m)) ≡ oddB k
ip-id-aux k     {m} zero     ep =
  trans (trans (insert-zero-base (id-perm m)) (sign-id {m})) (cong oddB ep)
ip-id-aux zero     (suc q') ()
ip-id-aux (suc k) {suc m} (suc q') ep =
  trans (cong sign (idInsert-step q'))
    (trans (sign-hom (sadj (suc m) q') T (sadj-is-perm (suc m) q')
                     (insert-at-preserves (inj1 q') (id-perm (suc m)) id-perm-is-perm))
           (cong₂ _xor_ (sign-sadj (suc m) q')
                        (ip-id-aux k (inj1 q') (trans (toℕ-inj1 q') (suc-injective ep)))))
  where T = insert-at (inj1 q') (id-perm (suc m))

ip-id-core : {m : ℕ} (p : Fin (suc m)) →
             sign (insert-at p (id-perm m)) ≡ oddB (toℕ p)
ip-id-core p = ip-id-aux (toℕ p) p refl

-- CO-APEX (ip-id-core ⨝ sign-wd). ip-id-aux is the SIGN-valued twin of the
-- repo's CoxGen-valued `idInsert-CoxGen` — two independent fuel inductions over
-- the SAME identity-insertion. `sign-wd` (the flagship "inversion-parity =
-- Coxeter-length-parity") bridges them: the length-parity signW of the canonical
-- adjacent-transposition word of insert-at p id EQUALS the factoradic digit
-- parity oddB (toℕ p). A checkable identification, not a prose mirror.
idInsert-signW : {m : ℕ} (p : Fin (suc m)) →
                 signW (idInsert-CoxGen p) ≡ oddB (toℕ p)
idInsert-signW p = trans (sym (sign-wd (idInsert-CoxGen p))) (ip-id-core p)

------------------------------------------------------------------------
-- ROUTE B (◆ip-route-b). Assembly via the σ-independent rotation ρ p:
-- insert-at p σ = ρ p ∘ insert-at 0 σ (insert-at-rot); ρ p = the perm
-- insert-at p id; so sign (insert-at p σ) = sign (insert-at p id) xor
-- sign (insert-at 0 σ) = oddB (toℕ p) xor sign σ. NO surjectivity.
------------------------------------------------------------------------

-- ρ p IS the perm insert-at p (id-perm m): they agree pointwise.
lookup-insert-id : {m : ℕ} (p : Fin (suc m)) (x : Fin (suc m)) →
                   lookup (insert-at p (id-perm m)) x ≡ ρ p x
lookup-insert-id p     zero    = refl
lookup-insert-id {m} p (suc j) =
  trans (lookup-map (punchIn p) (id-perm m) j) (cong (punchIn p) (apply-id j))

-- map (ρ p) (insert-at 0 σ) = compose (insert-at p id) (insert-at 0 σ).
map-ρ-compose : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) →
  map (ρ p) (insert-at zero σ) ≡ compose (insert-at p (id-perm m)) (insert-at zero σ)
map-ρ-compose {m} p σ =
  lookup-ext (map (ρ p) w) (compose A w)
    (λ i → trans (lookup-map (ρ p) w i)
                 (sym (trans (lookup∘tabulate (λ k → lookup A (lookup w k)) i)
                             (lookup-insert-id p (lookup w i)))))
  where w = insert-at zero σ
        A = insert-at p (id-perm m)

-- the single-insertion sign law, ROUTE B (rotation / Coxeter-generator route).
signB-insert : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ →
               sign (insert-at p σ) ≡ (oddB (toℕ p) xor sign σ)
signB-insert {m} p σ pf =
  trans (cong sign (insert-at-rot p σ))
    (trans (cong sign (map-ρ-compose p σ))
      (trans (sign-hom (insert-at p (id-perm m)) (insert-at zero σ)
               (insert-at-preserves p (id-perm m) id-perm-is-perm)
               (insert-at-preserves zero σ pf))
             (cong₂ _xor_ (ip-id-core p) (insert-zero-base σ))))

-- F₂ transport → the LehmerTowerMorphism insertion-parity obligation (Route B).
insertion-parity-B : {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) →
                     signF (decode (l ◂ p)) ≡ (finParity p +F signF (decode l))
insertion-parity-B l p =
  trans (cong bool→F₂ (signB-insert p (decode l) (decode-is-perm l)))
    (trans (bool→F₂-xor (oddB (toℕ p)) (sign (decode l)))
           (cong₂ _+F_ (trans (bool→F₂-oddB (toℕ p)) (sym (finParity-is-parity p))) refl))

------------------------------------------------------------------------
-- ◆ip-wire-morphism. The UNCONDITIONAL twisted-Lehmer sign-morphism —
-- discharges LehmerTowerMorphism's open `insertion-parity` parameter
-- (◆AI-3-pkg-twisted-lehmer) via Route B.
------------------------------------------------------------------------

sign-lehmer-morphism-unconditional : GradedDivStrMorphism lehmer-graded F₂-target
sign-lehmer-morphism-unconditional = sign-lehmer-morphism insertion-parity-B

------------------------------------------------------------------------
-- ROUTE A (◆ip-count-below + ◆ip-route-a) — the DISTINCT second derivation
-- via the INVERSION COUNT. F σ = parityLess p (map (punchIn p) σ) is a
-- comm xor-fold, hence permutation-invariant (F-mult over the Coxeter word,
-- NEEDS surjectivity via coxeter-complete); so F σ = F (id-perm) = the count
-- of {j < toℕ p} = oddB (toℕ p). The genuinely-new induction is idcount.
------------------------------------------------------------------------

-- the xor-fold under study.
F : {m : ℕ} (p : Fin (suc m)) → Perm m → Bool
F p v = parityLess p (map (punchIn p) v)

-- map distributes over an adjacent swap.
map-swapAdj : {A B : Set} {n : ℕ} (f : A → B) (j : Fin n) (v : Vec A (suc n)) →
              map f (swapAdj j v) ≡ swapAdj j (map f v)
map-swapAdj f zero    (x ∷ y ∷ zs) = refl
map-swapAdj f (suc j) (x ∷ xs)     = cong (f x ∷_) (map-swapAdj f j xs)

-- F is invariant under an adjacent swap of the base (comm xor-fold).
F-swap : {m : ℕ} (p : Fin (suc m)) {n : ℕ} (j : Fin n) (v : Vec (Fin m) (suc n)) →
         parityLess p (map (punchIn p) (swapAdj j v)) ≡ parityLess p (map (punchIn p) v)
F-swap p j v =
  trans (cong (parityLess p) (map-swapAdj (punchIn p) j v))
        (pLess-swap p j (map (punchIn p) v))

-- F is invariant under right-composition by ANY Coxeter-word (a permutation).
F-mult : {m : ℕ} (p : Fin (suc m)) (v : Perm m) {τ : Perm m} →
         CoxGen τ → F p (compose v τ) ≡ F p v
F-mult p v cox-id      = cong (F p) (compose-id-right v)
F-mult p v (cox-s j)   = trans (cong (F p) (bridge v j)) (F-swap p j v)
F-mult p v (cox-∘ {σ = σ'} {τ = τ'} g h) =
  trans (cong (F p) (sym (compose-assoc v σ' τ')))
        (trans (F-mult p (compose v σ') h) (F-mult p v g))

------------------------------------------------------------------------
-- idcount — the count of {j ∈ 0..m-1 : toℕ j < toℕ p} is oddB (toℕ p).
-- via punchIn-lt (finLt (punchIn p j) p = toℕ j <ᵇ toℕ p) + a ℕ-level fold.
------------------------------------------------------------------------

-- finLt is punchIn-order: punchIn p j < p ⟺ j < p (below the puncture).
punchIn-lt : {m : ℕ} (p : Fin (suc m)) (j : Fin m) →
             finLt (punchIn p j) p ≡ (toℕ j <ᵇ toℕ p)
punchIn-lt zero    j       = refl
punchIn-lt (suc k) zero    = refl
punchIn-lt (suc k) (suc j) = punchIn-lt k j

-- the ℕ-level count: xor-parity of {toℕ x <ᵇ t : x ∈ v}.
pLt : (t : ℕ) {m k : ℕ} → Vec (Fin m) k → Bool
pLt t []       = false
pLt t (x ∷ xs) = (toℕ x <ᵇ t) xor pLt t xs

-- parityLess p ∘ map (punchIn p) IS the ℕ-count at bound toℕ p.
pLt-bridge : {m k : ℕ} (p : Fin (suc m)) (v : Vec (Fin m) k) →
             parityLess p (map (punchIn p) v) ≡ pLt (toℕ p) v
pLt-bridge p []       = refl
pLt-bridge p (x ∷ xs) = cong₂ _xor_ (punchIn-lt p x) (pLt-bridge p xs)

-- shifting both the bound and the range by one is a no-op for the count.
pLt-map-suc : (t : ℕ) {m k : ℕ} (v : Vec (Fin m) k) →
              pLt (suc t) (map suc v) ≡ pLt t v
pLt-map-suc t []       = refl
pLt-map-suc t (x ∷ xs) = cong ((toℕ x <ᵇ t) xor_) (pLt-map-suc t xs)

-- toℕ p ≤ m for p : Fin (suc m).
toℕ≤m : {m : ℕ} (p : Fin (suc m)) → toℕ p ≤ m
toℕ≤m p with toℕ-bound p
... | s≤s le = le

-- the count over id-perm m, given the bound t ≤ m, is oddB t.
idcountN : (t m : ℕ) → t ≤ m → pLt t (id-perm m) ≡ oddB t
idcountN zero    m       le       = pLt-zero (id-perm m)
  where
    pLt-zero : {k : ℕ} (v : Vec (Fin m) k) → pLt zero v ≡ false
    pLt-zero []       = refl
    pLt-zero (x ∷ xs) = pLt-zero xs
idcountN (suc t) zero    ()
idcountN (suc t) (suc m) (s≤s le) =
  trans (cong (pLt (suc t) {suc m} {suc m}) id-perm-cons)
        (cong not (trans (pLt-map-suc t (id-perm m)) (idcountN t m le)))

idcount : {m : ℕ} (p : Fin (suc m)) →
          parityLess p (map (punchIn p) (id-perm m)) ≡ oddB (toℕ p)
idcount {m} p = trans (pLt-bridge p (id-perm m)) (idcountN (toℕ p) m (toℕ≤m p))

-- F is permutation-invariant ⟹ F σ = F (id-perm) = oddB (toℕ p).
count-below : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ →
              parityLess p (map (punchIn p) σ) ≡ oddB (toℕ p)
count-below {m} p σ pf =
  trans (cong (F p) (sym (compose-id-left σ)))
        (trans (F-mult p (id-perm m) (coxeter-complete σ pf)) (idcount p))

-- the single-insertion sign law, ROUTE A (inversion-count route).
signA-insert : {m : ℕ} (p : Fin (suc m)) (σ : Perm m) → IsPerm σ →
               sign (insert-at p σ) ≡ (oddB (toℕ p) xor sign σ)
signA-insert p σ pf = cong₂ _xor_ (count-below p σ pf) (sign-map-punchIn p σ)

-- F₂ transport → the same obligation, via Route A.
insertion-parity-A : {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) →
                     signF (decode (l ◂ p)) ≡ (finParity p +F signF (decode l))
insertion-parity-A l p =
  trans (cong bool→F₂ (signA-insert p (decode l) (decode-is-perm l)))
    (trans (bool→F₂-xor (oddB (toℕ p)) (sign (decode l)))
           (cong₂ _+F_ (trans (bool→F₂-oddB (toℕ p)) (sym (finParity-is-parity p))) refl))

------------------------------------------------------------------------
-- ◆ip-agree — THE CO-APEX. The two routes are PROPOSITIONALLY (not
-- definitionally) equal proofs of ONE F₂ equation; `refl` FAILS (they are
-- different terms — Route A goes through the inversion count + surjectivity,
-- Route B through the σ-independent rotation + only the generators). F₂ is
-- an h-set (Hedberg, via its decidable equality), so any two proofs agree.
--
-- CAVEAT (echoing Algebra/Q/Properties/RouteAgreement): this certifies the
-- CODOMAIN IS A PROP, NOT that the routes share content. The genuine finding
-- is the RETAINED DISTINCTION in the bodies — Route A NEEDS surjectivity
-- (coxeter-complete), Route B needs ONLY generators (sign-hom + sadj). That
-- distinction is the coverage; it is not dissolved by the agreement.
------------------------------------------------------------------------

F₂-UIP : {x y : F₂} (p q : x ≡ y) → p ≡ q
F₂-UIP = Decidable⇒UIP _≟_

route-agreement : {n : ℕ} (l : LehmerPath n) (p : Fin (suc n)) →
                  insertion-parity-A l p ≡ insertion-parity-B l p
route-agreement l p = F₂-UIP (insertion-parity-A l p) (insertion-parity-B l p)
