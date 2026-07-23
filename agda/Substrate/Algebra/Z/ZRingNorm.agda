{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.ZRingNorm — a REFLECTIVE ℤ-ring normalizer over k
-- opaque variables: the engine that AUTO-GENERATES the reduction (the
-- extruder that extrudes the proof over N local steps).
--
-- Reflect an ℤ expression as `ZE`; `norm : ZE → Canon` computes its
-- sum-of-sorted-monomials canonical form; `norm-sound : ⟦ e ⟧ ≡ evalC (norm e)`
-- (in ZRingNorm/Sound) is the value-preserving proof, spread over the
-- structural recursion (each case one local ring lemma — bounded memory).
-- A ℤ ring identity `a ≡ b` is then: reflect both, check `norm eₐ ≡ norm e_b`
-- (refl — same canonical), and `⟦eₐ⟧ ≡ evalC(norm eₐ) ≡ evalC(norm e_b) ≡ ⟦e_b⟧`.
-- No hand trace; no balloon.  This LAYER 1: data + interpretation + arithmetic.
------------------------------------------------------------------------

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.JacobianResidue using (𝔹; tt; ff; and; eqℕ)
open import Substrate.Algebra.Z.MPolyNormalize using (TriN; ltN; eqN; gtN; triℕ)
open import Substrate.Foundation.List using (List; []; _∷_)

module Substrate.Algebra.Z.ZRingNorm (k : ℕ) (ρ : Vec ℤ k) where

------------------------------------------------------------------------
-- ① reflected ℤ-ring expressions over k opaque variables.
------------------------------------------------------------------------

data ZE : Set where
  var : Fin k → ZE
  lit : ℤ → ZE
  _⊕_ : ZE → ZE → ZE
  _⊗_ : ZE → ZE → ZE

infixl 6 _⊕_
infixl 7 _⊗_

------------------------------------------------------------------------
-- ② exponent vectors + monomials + canonical forms.
------------------------------------------------------------------------

Exps : Set
Exps = Vec ℕ k

record Mon : Set where
  constructor mkMon
  field
    co : ℤ            -- coefficient
    ex : Exps         -- exponent vector
open Mon public

Canon : Set
Canon = List Mon

powℤ : ℤ → ℕ → ℤ
powℤ b zero    = + 1
powℤ b (suc n) = b *ℤ powℤ b n

------------------------------------------------------------------------
-- ③ interpretation.
------------------------------------------------------------------------

evalE′ : {n : ℕ} → Vec ℤ n → Vec ℕ n → ℤ
evalE′ []       []       = + 1
evalE′ (v ∷ vs) (e ∷ es) = powℤ v e *ℤ evalE′ vs es

evalE : Exps → ℤ
evalE e = evalE′ ρ e

evalM : Mon → ℤ
evalM (mkMon c e) = c *ℤ evalE e

evalC : Canon → ℤ
evalC []       = 0ℤ
evalC (m ∷ ms) = evalM m +ℤ evalC ms

⟦_⟧ : ZE → ℤ
⟦ var i ⟧ = lookup ρ i
⟦ lit c ⟧ = c
⟦ a ⊕ b ⟧ = ⟦ a ⟧ +ℤ ⟦ b ⟧
⟦ a ⊗ b ⟧ = ⟦ a ⟧ *ℤ ⟦ b ⟧

------------------------------------------------------------------------
-- ④ canonical arithmetic.
------------------------------------------------------------------------

zeros : (n : ℕ) → Vec ℕ n
zeros zero    = []
zeros (suc n) = zero ∷ zeros n

oneE : Exps
oneE = zeros k

unitE′ : {n : ℕ} → Fin n → Vec ℕ n
unitE′ Fin.zero    = suc zero ∷ zeros _
unitE′ (Fin.suc j) = zero ∷ unitE′ j

unitE : Fin k → Exps
unitE i = unitE′ i

addE : {n : ℕ} → Vec ℕ n → Vec ℕ n → Vec ℕ n
addE []       []       = []
addE (a ∷ as) (b ∷ bs) = (a + b) ∷ addE as bs

eqE : {n : ℕ} → Vec ℕ n → Vec ℕ n → 𝔹
eqE []       []       = tt
eqE (a ∷ as) (b ∷ bs) = and (eqℕ a b) (eqE as bs)

ltE : {n : ℕ} → Vec ℕ n → Vec ℕ n → 𝔹
ltE []       []       = ff
ltE (a ∷ as) (b ∷ bs) with triℕ a b
... | ltN _ = tt
... | gtN _ = ff
... | eqN _ = ltE as bs

-- insert a monomial into a sorted canon, combining like exponents.
-- (no zero-coeff pruning: none arises for cancellation-free identities like
--  the cube; pruning is a clean later enhancement for cancelling identities.)
insertM : Mon → Canon → Canon
insertM m [] = m ∷ []
insertM (mkMon c e) (mkMon c′ e′ ∷ ms) with eqE e e′
... | tt = mkMon (c +ℤ c′) e ∷ ms
... | ff with ltE e e′
...   | tt = mkMon c e ∷ mkMon c′ e′ ∷ ms
...   | ff = mkMon c′ e′ ∷ insertM (mkMon c e) ms

addC : Canon → Canon → Canon
addC []       d = d
addC (m ∷ ms) d = insertM m (addC ms d)

scaleC : Mon → Canon → Canon
scaleC _          []                = []
scaleC (mkMon c e) (mkMon c′ e′ ∷ ms) =
  insertM (mkMon (c *ℤ c′) (addE e e′)) (scaleC (mkMon c e) ms)

mulC : Canon → Canon → Canon
mulC []       _ = []
mulC (m ∷ ms) d = addC (scaleC m d) (mulC ms d)

------------------------------------------------------------------------
-- ⑤ the normalizer.
------------------------------------------------------------------------

norm : ZE → Canon
norm (var i) = mkMon (+ 1) (unitE i) ∷ []
norm (lit c) = mkMon c oneE ∷ []
norm (a ⊕ b) = addC (norm a) (norm b)
norm (a ⊗ b) = mulC (norm a) (norm b)
