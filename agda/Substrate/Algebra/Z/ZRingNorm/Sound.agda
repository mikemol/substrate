{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.ZRingNorm.Sound — the value-preserving soundness of
-- the reflective ℤ-ring normalizer: norm-sound : ⟦ e ⟧ ≡ evalC (norm e).
--
-- Proven by structural recursion, each case ONE local ring lemma (the proof
-- spread over the structure — bounded memory, no materialised normal form).
-- The proof module (imports the ring Properties); ZRingNorm holds the defs.
------------------------------------------------------------------------

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.Z using (ℤ; +_; 0ℤ)
open import Substrate.Algebra.Z.Add using (_+ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-assoc; +ℤ-comm; +ℤ-identityˡ; +ℤ-identityʳ)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-identityˡ; *ℤ-identityʳ; *ℤ-zeroˡ; *ℤ-zeroʳ;
         *ℤ-distribˡ-+; *ℤ-distribʳ-+; quadℤ)
open import Substrate.Algebra.Z.JacobianResidue using (𝔹; tt; ff; and; eqℕ)
open import Substrate.Foundation.List using (List; []; _∷_)

module Substrate.Algebra.Z.ZRingNorm.Sound (k : ℕ) (ρ : Vec ℤ k) where

open import Substrate.Algebra.Z.ZRingNorm k ρ

------------------------------------------------------------------------
-- local ℕ / 𝔹 helpers.
------------------------------------------------------------------------

powℤ-add : (b : ℤ) (m n : ℕ) → powℤ b (m + n) ≡ powℤ b m *ℤ powℤ b n
powℤ-add b zero    n = sym (*ℤ-identityˡ (powℤ b n))
powℤ-add b (suc m) n =
  trans (cong (b *ℤ_) (powℤ-add b m n)) (sym (*ℤ-assoc b (powℤ b m) (powℤ b n)))

eqℕ-≡ : (a b : ℕ) → eqℕ a b ≡ tt → a ≡ b
eqℕ-≡ zero    zero    _ = refl
eqℕ-≡ (suc a) (suc b) h = cong suc (eqℕ-≡ a b h)

and-l : {u v : 𝔹} → and u v ≡ tt → u ≡ tt
and-l {tt} _ = refl
and-r : {u v : 𝔹} → and u v ≡ tt → v ≡ tt
and-r {tt} h = h

------------------------------------------------------------------------
-- exponent-vector soundness.
------------------------------------------------------------------------

evalE′-zeros : {n : ℕ} (vs : Vec ℤ n) → evalE′ vs (zeros n) ≡ + 1
evalE′-zeros []       = refl
evalE′-zeros (v ∷ vs) = trans (*ℤ-identityˡ (evalE′ vs (zeros _))) (evalE′-zeros vs)

evalE′-unit : {n : ℕ} (vs : Vec ℤ n) (i : Fin n) → evalE′ vs (unitE′ i) ≡ lookup vs i
evalE′-unit (v ∷ vs) Fin.zero =
  trans (cong ((v *ℤ powℤ v zero) *ℤ_) (evalE′-zeros vs))
        (trans (*ℤ-identityʳ (v *ℤ powℤ v zero)) (*ℤ-identityʳ v))
evalE′-unit (v ∷ vs) (Fin.suc j) =
  trans (*ℤ-identityˡ (evalE′ vs (unitE′ j))) (evalE′-unit vs j)

evalE′-add : {n : ℕ} (vs : Vec ℤ n) (e e′ : Vec ℕ n) →
             evalE′ vs (addE e e′) ≡ evalE′ vs e *ℤ evalE′ vs e′
evalE′-add []       []       []         = sym (*ℤ-identityˡ (+ 1))
evalE′-add (v ∷ vs) (a ∷ es) (b ∷ es′) =
  trans (cong₂ _*ℤ_ (powℤ-add v a b) (evalE′-add vs es es′))
        (quadℤ (powℤ v a) (powℤ v b) (evalE′ vs es) (evalE′ vs es′))

eqE-≡ : {n : ℕ} (e e′ : Vec ℕ n) → eqE e e′ ≡ tt → e ≡ e′
eqE-≡ []       []         _ = refl
eqE-≡ (a ∷ es) (b ∷ es′) h =
  cong₂ _∷_ (eqℕ-≡ a b (and-l h)) (eqE-≡ es es′ (and-r h))

evalM-mul : (c c′ : ℤ) (e e′ : Exps) →
            evalM (mkMon (c *ℤ c′) (addE e e′)) ≡ evalM (mkMon c e) *ℤ evalM (mkMon c′ e′)
evalM-mul c c′ e e′ =
  trans (cong ((c *ℤ c′) *ℤ_) (evalE′-add ρ e e′))
        (quadℤ c c′ (evalE e) (evalE e′))

------------------------------------------------------------------------
-- canonical-arithmetic soundness.
------------------------------------------------------------------------

insertM-sound : (m : Mon) (c : Canon) → evalC (insertM m c) ≡ evalM m +ℤ evalC c
insertM-sound (mkMon c e) []                  = refl
insertM-sound (mkMon c e) (mkMon c′ e′ ∷ ms) with eqE e e′ | eqE-≡ e e′
... | tt | ee =
  -- exponents equal: combine coefficients (rewrite only the c′ term's e → e′).
  trans (cong (_+ℤ evalC ms) (*ℤ-distribʳ-+ c c′ (evalE e)))
  (trans (+ℤ-assoc (c *ℤ evalE e) (c′ *ℤ evalE e) (evalC ms))
         (cong (λ w → (c *ℤ evalE e) +ℤ ((c′ *ℤ evalE w) +ℤ evalC ms)) (ee refl)))
... | ff | _ with ltE e e′
...   | tt = refl
...   | ff =
  trans (cong (evalM (mkMon c′ e′) +ℤ_) (insertM-sound (mkMon c e) ms))
  (trans (sym (+ℤ-assoc (evalM (mkMon c′ e′)) (evalM (mkMon c e)) (evalC ms)))
  (trans (cong (_+ℤ evalC ms) (+ℤ-comm (evalM (mkMon c′ e′)) (evalM (mkMon c e))))
         (+ℤ-assoc (evalM (mkMon c e)) (evalM (mkMon c′ e′)) (evalC ms))))

addC-sound : (c d : Canon) → evalC (addC c d) ≡ evalC c +ℤ evalC d
addC-sound []       d = sym (+ℤ-identityˡ (evalC d))
addC-sound (m ∷ ms) d =
  trans (insertM-sound m (addC ms d))
  (trans (cong (evalM m +ℤ_) (addC-sound ms d))
         (sym (+ℤ-assoc (evalM m) (evalC ms) (evalC d))))

scaleC-sound : (m : Mon) (c : Canon) → evalC (scaleC m c) ≡ evalM m *ℤ evalC c
scaleC-sound (mkMon c e) []                  = sym (*ℤ-zeroʳ (evalM (mkMon c e)))
scaleC-sound (mkMon c e) (mkMon c′ e′ ∷ ms) =
  trans (insertM-sound (mkMon (c *ℤ c′) (addE e e′)) (scaleC (mkMon c e) ms))
  (trans (cong₂ _+ℤ_ (evalM-mul c c′ e e′) (scaleC-sound (mkMon c e) ms))
         (sym (*ℤ-distribˡ-+ (evalM (mkMon c e)) (evalM (mkMon c′ e′)) (evalC ms))))

mulC-sound : (c d : Canon) → evalC (mulC c d) ≡ evalC c *ℤ evalC d
mulC-sound []       d = sym (*ℤ-zeroˡ (evalC d))
mulC-sound (m ∷ ms) d =
  trans (addC-sound (scaleC m d) (mulC ms d))
  (trans (cong₂ _+ℤ_ (scaleC-sound m d) (mulC-sound ms d))
         (sym (*ℤ-distribʳ-+ (evalM m) (evalC ms) (evalC d))))

------------------------------------------------------------------------
-- THE soundness.
------------------------------------------------------------------------

norm-sound : (e : ZE) → ⟦ e ⟧ ≡ evalC (norm e)
norm-sound (var i) =
  sym (trans (cong (λ w → ((+ 1) *ℤ w) +ℤ 0ℤ) (evalE′-unit ρ i))
      (trans (cong (_+ℤ 0ℤ) (*ℤ-identityˡ (lookup ρ i))) (+ℤ-identityʳ (lookup ρ i))))
norm-sound (lit c) =
  sym (trans (cong (λ w → (c *ℤ w) +ℤ 0ℤ) (evalE′-zeros ρ))
      (trans (cong (_+ℤ 0ℤ) (*ℤ-identityʳ c)) (+ℤ-identityʳ c)))
norm-sound (a ⊕ b) =
  trans (cong₂ _+ℤ_ (norm-sound a) (norm-sound b))
        (sym (addC-sound (norm a) (norm b)))
norm-sound (a ⊗ b) =
  trans (cong₂ _*ℤ_ (norm-sound a) (norm-sound b))
        (sym (mulC-sound (norm a) (norm b)))
