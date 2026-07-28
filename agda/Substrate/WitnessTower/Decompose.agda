------------------------------------------------------------------------
-- Substrate.WitnessTower.Decompose
--
-- The INVERSE of the witnessing-insertion move: every permutation of
-- Fin (suc n) is insert-at its own head over a unique smaller permutation.
-- This is the heart of "the tower is complete" — insert-at is surjective
-- onto Sₙ, so the enumeration misses nothing — and (with uniqueness)
-- duplicate-free.
--
--   σ  =  insert-at (lookup σ zero) (decomp-tail σ)
--   ╰ any bijection      ╰ where 0 goes   ╰ the rest, punched out of its way
--
-- decomp-tail is itself a permutation (so induction applies), proved via
-- punchOut-injective — which falls straight out of the punchIn∘punchOut
-- round-trip, no case analysis.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Decompose where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Sucinjective
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; map; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Fin.Punctured using (punchIn; punchOut; punchIn-punchOut)

open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.IsPermutation using (IsPerm; lookup-map)

------------------------------------------------------------------------
-- 0. Vec extensionality (pointwise lookup ⟹ equal) and punchOut injective.
------------------------------------------------------------------------

lookup-ext : {A : Set} {n : ℕ} (v w : Vec A n) →
             ((i : Fin n) → lookup v i ≡ lookup w i) → v ≡ w
lookup-ext []      []      _ = refl
lookup-ext (x ∷ v) (y ∷ w) h =
  cong₂ _∷_ (h zero) (lookup-ext v w (λ i → h (suc i)))
  where open import Substrate.Foundation.Eq using (cong₂)

-- punchOut is injective: distinct inputs (off k) punch to distinct outputs.
-- Derived from punchIn (punchOut x) ≡ x — no case split.
punchOut-injective :
  {n : ℕ} {k i j : Fin (suc n)}
  (i≢ : ¬ (i ≡ k)) (j≢ : ¬ (j ≡ k)) →
  punchOut {k = k} {i = i} i≢ ≡ punchOut {k = k} {i = j} j≢ → i ≡ j
punchOut-injective {k = k} i≢ j≢ eq =
  trans (sym (punchIn-punchOut i≢))
        (trans (cong (punchIn k) eq) (punchIn-punchOut j≢))

------------------------------------------------------------------------
-- 1. The head and the tail of a permutation.
------------------------------------------------------------------------

-- where the witness index (0) goes.
decomp-head : {n : ℕ} → Perm (suc n) → Fin (suc n)
decomp-head σ = lookup σ zero

-- the tail values avoid the head, BY injectivity (else suc i ≡ zero).
tail-≢-head :
  {n : ℕ} (σ : Perm (suc n)) → IsPerm σ →
  (i : Fin n) → ¬ (lookup σ (suc i) ≡ lookup σ zero)
tail-≢-head σ perm i eq with perm (suc i) zero eq
... | ()

-- the smaller permutation: punch each tail value out of the head's slot.
decomp-tail : {n : ℕ} (σ : Perm (suc n)) → IsPerm σ → Perm n
decomp-tail σ perm =
  tabulate (λ i → punchOut {k = lookup σ zero} {i = lookup σ (suc i)}
                            (tail-≢-head σ perm i))

------------------------------------------------------------------------
-- 2. The tail is a permutation (induction can recurse on it).
------------------------------------------------------------------------

decomp-tail-perm :
  {n : ℕ} (σ : Perm (suc n)) (perm : IsPerm σ) → IsPerm (decomp-tail σ perm)
decomp-tail-perm σ perm i j eq = fin-suc-injective (perm (suc i) (suc j) tails-eq)
  where
    f = λ i → punchOut {k = lookup σ zero} {i = lookup σ (suc i)}
                        (tail-≢-head σ perm i)
    -- eq : lookup (tabulate f) i ≡ lookup (tabulate f) j ; strip tabulate.
    fi≡fj : f i ≡ f j
    fi≡fj = trans (sym (lookup∘tabulate f i)) (trans eq (lookup∘tabulate f j))
    tails-eq : lookup σ (suc i) ≡ lookup σ (suc j)
    tails-eq = punchOut-injective (tail-≢-head σ perm i) (tail-≢-head σ perm j) fi≡fj

------------------------------------------------------------------------
-- 3. Reconstruction: σ ≡ insert-at (head) (tail). insert-at is surjective.
------------------------------------------------------------------------

decomp-correct :
  {n : ℕ} (σ : Perm (suc n)) (perm : IsPerm σ) →
  σ ≡ insert-at (decomp-head σ) (decomp-tail σ perm)
decomp-correct σ perm = lookup-ext σ (insert-at (decomp-head σ) (decomp-tail σ perm)) pointwise
  where
    p  = lookup σ zero
    dt = decomp-tail σ perm
    f  = λ i → punchOut {k = lookup σ zero} {i = lookup σ (suc i)}
                         (tail-≢-head σ perm i)
    pointwise : (i : Fin _) → lookup σ i ≡ lookup (insert-at p dt) i
    pointwise zero    = refl
    pointwise (suc i) =
      -- lookup (insert-at p dt) (suc i) = punchIn p (lookup dt i)
      --                                 = punchIn p (f i) = lookup σ (suc i)
      sym (trans (lookup-map (punchIn p) dt i)
                 (trans (cong (punchIn p) (lookup∘tabulate f i))
                        (punchIn-punchOut (tail-≢-head σ perm i))))

------------------------------------------------------------------------
-- 4. Packaged: every permutation of Fin (suc n) decomposes as a head
--    position + a smaller permutation that reconstructs it.
------------------------------------------------------------------------

decompose :
  {n : ℕ} (σ : Perm (suc n)) → IsPerm σ →
  Σ (Fin (suc n)) λ p →
  Σ (Perm n) λ σ' →
  IsPerm σ' × (σ ≡ insert-at p σ')
decompose σ perm =
  decomp-head σ , decomp-tail σ perm , decomp-tail-perm σ perm , decomp-correct σ perm
