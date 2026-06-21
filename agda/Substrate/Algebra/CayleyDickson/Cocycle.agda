------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Cocycle
--
-- ⊙.morton (foundation): the F₂ⁿ-indexing of the Cayley-Dickson basis — the
-- structure conjecture C3 (Morton ≅ Cayley-Dickson via the cocycle) rests on.
--
-- The 2ⁿ-dimensional algebra `Carrier n` has a basis indexed by F₂ⁿ: a bit
-- string is the doubling PATH (false = real half, true = imaginary half), and
-- `e n idx` is the unit with 1ℚ at that leaf. The index group op is XOR (F₂ⁿ
-- addition), and the basis product carries a SIGN-COCYCLE: eᵢ·eⱼ = ε(i,j)·e_{i⊕j}.
--
-- Built here: the index→basis map `e`, the index XOR, the cocycle at the ℂ
-- corner (ε(1,1) = −1, i.e. i² = −1 recast in the F₂ⁿ frame), and — the deep
-- result — the GENERIC PRODUCT LAW `prod`: eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j} for ALL n,
-- with the explicit recursive 2-cochain `ε`. The basis product lands on the
-- XOR'd index (the F₂ⁿ grading = Morton/Z-order) carrying the sign-cocycle ε.
-- Morton order = the TRIVIAL cochain (ε ≡ false, pure XOR, no signs); CD = this
-- NONTRIVIAL ε, whose noncommutativity ε(i,j) ≠ ε(j,i) is `CommuteEdge.mul-noncomm-ℍ`
-- (and whose strict 2-cocycle identity fails exactly at the 𝕆 associator — the
-- nonassociativity, NOT claimed here).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Cocycle where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; subst; trans; sym)
open import Substrate.Foundation.Bool using (Bool; true; false; not; _xor_)
open import Substrate.Foundation.Bool.Properties using (xor-comm; xor-assoc; xor-same; xor-identityʳ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; zipWith)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.CayleyDickson
  using (Carrier; mul; neg; conj; ≈#; zero#; one#; i; i²≈−1)
open import Substrate.Algebra.CayleyDickson.Setoid
  using (≈#-refl; ≈#-sym; ≈#-trans; neg-zero#; conj-zero#; mul-oneˡ; mul-oneʳ;
         add-cong; sub-cong; mul-cong; neg-cong; add-zeroˡ; add-zeroʳ; sub-zeroʳ;
         mul-zeroˡ; mul-zeroʳ; neg-invol; mul-negˡ; mul-negʳ)

-- F₂ⁿ index → CD basis unit: 1ℚ at the leaf addressed by the n bits.
e : (n : ℕ) → Vec Bool n → Carrier n
e zero    []           = one# 0                  -- the scalar unit 1
e (suc n) (false ∷ bs) = e n bs , zero# n        -- real half
e (suc n) (true  ∷ bs) = zero# n , e n bs        -- imaginary half

-- The index group operation is F₂ⁿ addition = pointwise XOR, i.e. the
-- carrier-home `Vec.zipWith _xor_` (reused, no new Vec operator).

-- THE SIGN-COCYCLE at the ℂ corner: e[1]·e[1] ≈# −e[1⊕1] = −e[0] — so ε(1,1) = −1
-- (i² = −1 in the F₂ⁿ-cocycle frame; the index adds via XOR (zipWith _xor_), the
-- sign is ε). The cocycle's nontriviality is `CommuteEdge.mul-noncomm-ℍ` (level 2).
ℂ-sign-cocycle :
  ≈# 1 (mul 1 (e 1 (true ∷ [])) (e 1 (true ∷ [])))
       (neg 1 (e 1 (zipWith _xor_ (true ∷ []) (true ∷ []))))
ℂ-sign-cocycle = i²≈−1

------------------------------------------------------------------------
-- CONJUGATION ON A BASIS UNIT: conj eᵢ = ±eᵢ — the scalar is fixed, every
-- imaginary unit is negated. (The first prerequisite of the recursive product
-- law: the CD doubling product conjugates one factor.) `imag?` = "index has a
-- true bit" (= an imaginary unit); `sgn` applies the resulting ± sign.
------------------------------------------------------------------------

imag? : {n : ℕ} → Vec Bool n → Bool
imag? []           = false
imag? (true  ∷ _)  = true
imag? (false ∷ bs) = imag? bs

sgn : Bool → (n : ℕ) → Carrier n → Carrier n
sgn true  n x = neg n x
sgn false n x = x

conj-on-basis : (n : ℕ) (idx : Vec Bool n) →
                ≈# n (conj n (e n idx)) (sgn (imag? idx) n (e n idx))
conj-on-basis zero    []           = ≈#-refl 0 (e 0 [])
conj-on-basis (suc n) (true  ∷ is) =
    ≈#-trans n (conj-zero# n) (≈#-sym n (neg-zero# n))
  , ≈#-refl n (neg n (e n is))
conj-on-basis (suc n) (false ∷ is) with imag? is | conj-on-basis n is
... | false | ih = ih , neg-zero# n
... | true  | ih = ih , ≈#-refl n (neg n (zero# n))

------------------------------------------------------------------------
-- COCYCLE NORMALIZATION: e₀·eᵢ ≈# eᵢ ≈# eᵢ·e₀ — the scalar unit e₀ (the
-- all-false index) is the identity, so ε(0,i) = ε(i,0) = +1. The first FULL case
-- of the recursive product law eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j}: when one index is 0,
-- i⊕0 = i and the sign is trivial. (Rests on CD's two-sided identity mul-one,
-- since e₀ = the all-false index = the unit 1.)
------------------------------------------------------------------------

-- e₀ : the all-false index, and the fact it IS the unit 1.
falses : (n : ℕ) → Vec Bool n
falses zero    = []
falses (suc n) = false ∷ falses n

e-falses : (n : ℕ) → e n (falses n) ≡ one# n
e-falses zero    = refl
e-falses (suc n) = cong (_, zero# n) (e-falses n)

-- ε(i, 0) = +1 : right-multiplying by the scalar e₀ fixes eᵢ.
prod-unitʳ : (n : ℕ) (i : Vec Bool n) → ≈# n (mul n (e n i) (e n (falses n))) (e n i)
prod-unitʳ n i rewrite e-falses n = mul-oneʳ n (e n i)

-- ε(0, i) = +1 : left-multiplying by the scalar e₀ fixes eᵢ.
prod-unitˡ : (n : ℕ) (i : Vec Bool n) → ≈# n (mul n (e n (falses n)) (e n i)) (e n i)
prod-unitˡ n i rewrite e-falses n = mul-oneˡ n (e n i)

------------------------------------------------------------------------
-- THE GENERIC PRODUCT LAW: eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j} for all n.  The basis
-- product lands on the XOR'd index (the F₂ⁿ grading = Morton/Z-order) carrying a
-- SIGN-COCYCLE ε. This is the structure conjecture C3 (Morton ≅ Cayley-Dickson):
-- ε is the nontrivial 2-cocycle whose graded loss is the commute-edge ladder.
--
-- `sgn` helpers: how the ± sign threads through pairs / zero / mul / neg / xor.
------------------------------------------------------------------------

≈#-from-≡ : (n : ℕ) {x y : Carrier n} → x ≡ y → ≈# n x y
≈#-from-≡ n {x} e = subst (≈# n x) e (≈#-refl n x)

sgn-cons : (b : Bool) (n : ℕ) (p q : Carrier n) →
           ≈# (suc n) (sgn b (suc n) (p , q)) (sgn b n p , sgn b n q)
sgn-cons true  n p q = ≈#-refl n (neg n p) , ≈#-refl n (neg n q)
sgn-cons false n p q = ≈#-refl n p , ≈#-refl n q

sgn-zero# : (b : Bool) (n : ℕ) → ≈# n (sgn b n (zero# n)) (zero# n)
sgn-zero# true  n = neg-zero# n
sgn-zero# false n = ≈#-refl n (zero# n)

sgn-cong : (b : Bool) (n : ℕ) {x y : Carrier n} → ≈# n x y → ≈# n (sgn b n x) (sgn b n y)
sgn-cong true  n p = neg-cong n p
sgn-cong false n p = p

mul-sgn-r : (b : Bool) (n : ℕ) (x y : Carrier n) →
            ≈# n (mul n x (sgn b n y)) (sgn b n (mul n x y))
mul-sgn-r true  n x y = mul-negʳ n x y
mul-sgn-r false n x y = ≈#-refl n (mul n x y)

mul-sgn-l : (b : Bool) (n : ℕ) (x y : Carrier n) →
            ≈# n (mul n (sgn b n x) y) (sgn b n (mul n x y))
mul-sgn-l true  n x y = mul-negˡ n x y
mul-sgn-l false n x y = ≈#-refl n (mul n x y)

neg-sgn : (b : Bool) (n : ℕ) (x : Carrier n) → ≈# n (neg n (sgn b n x)) (sgn (not b) n x)
neg-sgn true  n x = neg-invol n x
neg-sgn false n x = ≈#-refl n (neg n x)

sgn-xor : (a b : Bool) (n : ℕ) (x : Carrier n) →
          ≈# n (sgn (a xor b) n x) (sgn a n (sgn b n x))
sgn-xor true  true  n x = ≈#-sym n (neg-invol n x)
sgn-xor true  false n x = ≈#-refl n (neg n x)
sgn-xor false b     n x = ≈#-refl n (sgn b n x)

-- The index group operation is F₂ⁿ XOR, and it is commutative (xor is).
⊕-comm : (n : ℕ) (i j : Vec Bool n) → zipWith _xor_ i j ≡ zipWith _xor_ j i
⊕-comm zero    []       []       = refl
⊕-comm (suc n) (b ∷ is) (c ∷ js) = cong₂ _∷_ (xor-comm b c) (⊕-comm n is js)

-- THE COCYCLE SIGN ε : Vec Bool n → Vec Bool n → Bool (true = −1). Read off the
-- doubling recursion: FF recurses; FT swaps order; TF picks up imag? js (conj on
-- the right factor); TT swaps, conjugates AND negates.
ε : (n : ℕ) → Vec Bool n → Vec Bool n → Bool
ε zero    []           []           = false
ε (suc n) (false ∷ is) (false ∷ js) = ε n is js
ε (suc n) (false ∷ is) (true  ∷ js) = ε n js is
ε (suc n) (true  ∷ is) (false ∷ js) = imag? js xor ε n is js
ε (suc n) (true  ∷ is) (true  ∷ js) = not (imag? js) xor ε n js is

-- eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j}.  Induction on n; the 4 doubling cases each reduce —
-- via mul-zero (off-diagonal halves vanish), conj-on-basis (the conjugated
-- factor), mul-neg (push its sign out) and the IH — to the signed XOR basis unit.
prod : (n : ℕ) (i j : Vec Bool n) →
       ≈# n (mul n (e n i) (e n j)) (sgn (ε n i j) n (e n (zipWith _xor_ i j)))
prod zero    []           []           = mul-oneˡ 0 (one# 0)
prod (suc n) (false ∷ is) (false ∷ js) =
  ≈#-trans (suc n)
    ( ≈#-trans n (sub-cong n (≈#-refl n (mul n (e n is) (e n js))) (mul-zeroʳ n (conj n (zero# n))))
                 (≈#-trans n (sub-zeroʳ n (mul n (e n is) (e n js))) (prod n is js))
    , ≈#-trans n (add-cong n (mul-zeroˡ n (e n is)) (mul-zeroˡ n (conj n (e n js))))
                 (≈#-trans n (add-zeroʳ n (zero# n)) (≈#-sym n (sgn-zero# (ε n is js) n))) )
    (≈#-sym (suc n) (sgn-cons (ε n is js) n (e n (zipWith _xor_ is js)) (zero# n)))
prod (suc n) (false ∷ is) (true ∷ js) =
  ≈#-trans (suc n)
    ( ≈#-trans n (sub-cong n (mul-zeroʳ n (e n is)) (mul-zeroʳ n (conj n (e n js))))
                 (≈#-trans n (sub-zeroʳ n (zero# n)) (≈#-sym n (sgn-zero# (ε n js is) n)))
    , ≈#-trans n (add-cong n (≈#-refl n (mul n (e n js) (e n is))) (mul-zeroˡ n (conj n (zero# n))))
                 (≈#-trans n (add-zeroʳ n (mul n (e n js) (e n is)))
                            (≈#-trans n (prod n js is)
                                       (sgn-cong (ε n js is) n (≈#-from-≡ n (cong (e n) (⊕-comm n js is)))))) )
    (≈#-sym (suc n) (sgn-cons (ε n js is) n (zero# n) (e n (zipWith _xor_ is js))))
prod (suc n) (true ∷ is) (false ∷ js) =
  ≈#-trans (suc n)
    ( ≈#-trans n (sub-cong n (mul-zeroˡ n (e n js))
                            (≈#-trans n (mul-cong n (conj-zero# n) (≈#-refl n (e n is))) (mul-zeroˡ n (e n is))))
                 (≈#-trans n (sub-zeroʳ n (zero# n)) (≈#-sym n (sgn-zero# (imag? js xor ε n is js) n)))
    , ≈#-trans n (add-cong n (mul-zeroˡ n (zero# n))
                            (≈#-trans n (mul-cong n (≈#-refl n (e n is)) (conj-on-basis n js))
                                       (≈#-trans n (mul-sgn-r (imag? js) n (e n is) (e n js))
                                                  (≈#-trans n (sgn-cong (imag? js) n (prod n is js))
                                                             (≈#-sym n (sgn-xor (imag? js) (ε n is js) n (e n (zipWith _xor_ is js))))))))
                 (add-zeroˡ n (sgn (imag? js xor ε n is js) n (e n (zipWith _xor_ is js)))) )
    (≈#-sym (suc n) (sgn-cons (imag? js xor ε n is js) n (zero# n) (e n (zipWith _xor_ is js))))
prod (suc n) (true ∷ is) (true ∷ js) =
  ≈#-trans (suc n)
    ( ≈#-trans n (sub-cong n (mul-zeroˡ n (zero# n))
                            (≈#-trans n (mul-cong n (conj-on-basis n js) (≈#-refl n (e n is)))
                                       (≈#-trans n (mul-sgn-l (imag? js) n (e n js) (e n is))
                                                  (sgn-cong (imag? js) n (prod n js is)))))
                 (≈#-trans n (add-zeroˡ n (neg n (sgn (imag? js) n (sgn (ε n js is) n (e n (zipWith _xor_ js is))))))
                            (≈#-trans n (neg-sgn (imag? js) n (sgn (ε n js is) n (e n (zipWith _xor_ js is))))
                                       (≈#-trans n (≈#-sym n (sgn-xor (not (imag? js)) (ε n js is) n (e n (zipWith _xor_ js is))))
                                                  (sgn-cong (not (imag? js) xor ε n js is) n (≈#-from-≡ n (cong (e n) (⊕-comm n js is)))))))
    , ≈#-trans n (add-cong n (mul-zeroʳ n (e n js))
                            (≈#-trans n (mul-cong n (≈#-refl n (e n is)) (conj-zero# n)) (mul-zeroʳ n (e n is))))
                 (≈#-trans n (add-zeroʳ n (zero# n)) (≈#-sym n (sgn-zero# (not (imag? js) xor ε n js is) n))) )
    (≈#-sym (suc n) (sgn-cons (not (imag? js) xor ε n js is) n (e n (zipWith _xor_ is js)) (zero# n)))

------------------------------------------------------------------------
-- ⊙.assoc — THE ASSOCIATOR AS A MEASURED 3-COCHAIN. Both (eᵢ·eⱼ)·eₖ and
-- eᵢ·(eⱼ·eₖ) land at e_{i⊕j⊕k} (XOR is associative); their sign difference is
-- `dε`, the coboundary of ε. dε ≡ false ⟹ associative; the 𝕆 nonassociativity
-- (mul-nonassoc-𝕆) is precisely dε ≡ true. This MEASURES the obstruction the
-- product law left unclaimed: the nonassociativity is the cocycle's non-closure,
-- graded (ties ⊙.c5 — the associator IS the graded cost of ε).
------------------------------------------------------------------------

-- XOR is associative on the index (lifting Bool xor-assoc), and self-cancels.
⊕-assoc : (n : ℕ) (i j k : Vec Bool n) →
          zipWith _xor_ (zipWith _xor_ i j) k ≡ zipWith _xor_ i (zipWith _xor_ j k)
⊕-assoc zero    []       []       []       = refl
⊕-assoc (suc n) (a ∷ is) (b ∷ js) (c ∷ ks) = cong₂ _∷_ (xor-assoc a b c) (⊕-assoc n is js ks)

xor-cancelʳ : (a b : Bool) → (a xor b) xor b ≡ a
xor-cancelʳ a b = trans (xor-assoc a b b) (trans (cong (a xor_) (xor-same b)) (xor-identityʳ a))

-- left- and right-association each land on the signed XOR-triple basis unit.
prod-l : (n : ℕ) (i j k : Vec Bool n) →
         ≈# n (mul n (mul n (e n i) (e n j)) (e n k))
              (sgn (ε n i j xor ε n (zipWith _xor_ i j) k) n
                   (e n (zipWith _xor_ (zipWith _xor_ i j) k)))
prod-l n i j k =
  ≈#-trans n (mul-cong n (prod n i j) (≈#-refl n (e n k)))
  (≈#-trans n (mul-sgn-l (ε n i j) n (e n (zipWith _xor_ i j)) (e n k))
  (≈#-trans n (sgn-cong (ε n i j) n (prod n (zipWith _xor_ i j) k))
              (≈#-sym n (sgn-xor (ε n i j) (ε n (zipWith _xor_ i j) k) n
                                 (e n (zipWith _xor_ (zipWith _xor_ i j) k))))))

prod-r : (n : ℕ) (i j k : Vec Bool n) →
         ≈# n (mul n (e n i) (mul n (e n j) (e n k)))
              (sgn (ε n j k xor ε n i (zipWith _xor_ j k)) n
                   (e n (zipWith _xor_ i (zipWith _xor_ j k))))
prod-r n i j k =
  ≈#-trans n (mul-cong n (≈#-refl n (e n i)) (prod n j k))
  (≈#-trans n (mul-sgn-r (ε n j k) n (e n i) (e n (zipWith _xor_ j k)))
  (≈#-trans n (sgn-cong (ε n j k) n (prod n i (zipWith _xor_ j k)))
              (≈#-sym n (sgn-xor (ε n j k) (ε n i (zipWith _xor_ j k)) n
                                 (e n (zipWith _xor_ i (zipWith _xor_ j k)))))))

-- the associator 3-cochain = the coboundary dε of the 2-cochain ε.
dε : (n : ℕ) (i j k : Vec Bool n) → Bool
dε n i j k = (ε n i j xor ε n (zipWith _xor_ i j) k) xor (ε n j k xor ε n i (zipWith _xor_ j k))

-- THE MEASURED ASSOCIATOR: (eᵢ·eⱼ)·eₖ ≈# dε(i,j,k) · (eᵢ·(eⱼ·eₖ)).
associator : (n : ℕ) (i j k : Vec Bool n) →
             ≈# n (mul n (mul n (e n i) (e n j)) (e n k))
                  (sgn (dε n i j k) n (mul n (e n i) (mul n (e n j) (e n k))))
associator n i j k =
  ≈#-trans n (prod-l n i j k)
  (≈#-trans n (≈#-from-≡ n (cong (λ b → sgn b n (e n (zipWith _xor_ (zipWith _xor_ i j) k)))
                                 (sym (xor-cancelʳ (ε n i j xor ε n (zipWith _xor_ i j) k)
                                                   (ε n j k xor ε n i (zipWith _xor_ j k))))))
  (≈#-trans n (sgn-xor (dε n i j k) (ε n j k xor ε n i (zipWith _xor_ j k)) n
                       (e n (zipWith _xor_ (zipWith _xor_ i j) k)))
  (sgn-cong (dε n i j k) n
    (≈#-trans n (sgn-cong (ε n j k xor ε n i (zipWith _xor_ j k)) n
                          (≈#-from-≡ n (cong (e n) (⊕-assoc n i j k))))
                (≈#-sym n (prod-r n i j k))))))

-- COROLLARY: where the cochain vanishes, the basis product associates.
associative-at : (n : ℕ) (i j k : Vec Bool n) → dε n i j k ≡ false →
                 ≈# n (mul n (mul n (e n i) (e n j)) (e n k))
                      (mul n (e n i) (mul n (e n j) (e n k)))
associative-at n i j k p =
  ≈#-trans n (associator n i j k)
             (≈#-from-≡ n (cong (λ b → sgn b n (mul n (e n i) (mul n (e n j) (e n k)))) p))

-- GROUNDING: the 𝕆 nonassociator (CommuteEdge.mul-nonassoc-𝕆, i,j,l outside one
-- ℍ-subalgebra) is precisely dε ≡ true — the cochain detects the known failure.
dε-𝕆 : dε 3 (false ∷ false ∷ true ∷ []) (false ∷ true ∷ false ∷ []) (true ∷ false ∷ false ∷ []) ≡ true
dε-𝕆 = refl
