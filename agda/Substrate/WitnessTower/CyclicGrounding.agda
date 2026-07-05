{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.CyclicGrounding — ⟡cyclic-from-the-build (Ⓖ.cyclic): the cyclic group family
-- {Zₙ} grown IN the tower's build, collapsing the Word-vs-tower distinction. The substrate's canonical
-- cyclic group is Word-based (xFreeCyclic: `Zn-Word` = a word `gᵏ` on the generator, `Zn-normalize` =
-- reduce mod n, `_Zn-++_` = concatenate-then-normalize). But a word `gᵏ` IS a build-trace: "apply the
-- generator k times". So the abstract Word-Zₙ and the tower's ⟨g⟩ ⊆ Sₙ are BISIMILAR coalgebras (both =
-- "iterate the generator, wrap at the rung"), and the family grows AS THE TOWER grows. This module grounds
-- the CONCATENATION side of that bisimulation, generically over the generator:
--
--   the word `gᵏ` IS `pow g k` (k-fold composition in the tower's build), and word-concatenation
--   `_Zn-++_` IS the tower's `compose` — `pow-hom : pow g (a + b) ≡ compose (pow g a) (pow g b)`, the
--   homomorphism (ℕ, +) → (⟨g⟩, compose). Instantiated at any order-n generator g (canonically the
--   n-cycle) this is Zₙ ⊆ Sₙ; the free/ℤ part is grounded here, the finite wrap is the order relation.
--
-- Method: ExtrudeSKIKFaces ("an attribute IS its build-trace") — but at the GROWTH level (the piece that
-- reference SCOPED as "reused-in-spirit: the full coinductive tower-growth bisimulation"), here realized
-- for the cyclic family's concatenation. `compose`-assoc/id come from SnGroup (the tower's Sₙ-as-a-group).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED (machine-checked) = `pow` (the k-fold build-trace), `compose`-
-- assoc (via SnGroup faithfulness), and `pow-hom` (`_Zn-++_` IS `compose`, the free-cyclic ℕ→⟨g⟩
-- homomorphism, for ANY generator). SCOPED (reused-in-spirit): the ORDER/WRAP `pow g (suc n) ≡ id` (=
-- `Zn-normalize`, the finite Zₙ quotient of the free ⟨g⟩) — the generic n-cycle order is already witnessed
-- by Algebra.F2.Linear.FromImages.Permutation.Cyclic.cyclic-suc-HasOrderPerm ("expose-generator-not-orbit",
-- one proof for all n); the full xFreeCyclic Word-normalize bridge; and the unbounded rung growth itself
-- (the per-generator concatenation is the grounded finite shadow).
------------------------------------------------------------------------

module Substrate.WitnessTower.CyclicGrounding where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose; id-perm)
open import Substrate.WitnessTower.SnGroup
  using (apply; apply-compose; apply-id; apply-injective; compose-id-left)

------------------------------------------------------------------------
-- ① compose is associative — read off the ACTION via SnGroup's faithfulness (`apply-injective`) and
--    homomorphism (`apply-compose`): both sides act as apply σ ∘ apply τ ∘ apply ρ. (The tower's Sₙ is a
--    group; this is the associativity half, sited with the cyclic use that needs it.)
------------------------------------------------------------------------
compose-assoc : {n : ℕ} (σ τ ρ : Perm n) →
                compose (compose σ τ) ρ ≡ compose σ (compose τ ρ)
compose-assoc σ τ ρ = apply-injective (λ i →
  trans (apply-compose (compose σ τ) ρ i)
  (trans (apply-compose σ τ (apply ρ i))
  (trans (cong (apply σ) (sym (apply-compose τ ρ i)))
         (sym (apply-compose σ (compose τ ρ) i)))))

------------------------------------------------------------------------
-- ② THE BUILD-TRACE. The word `gᵏ` on the generator g IS its k-fold composition in the tower's build.
------------------------------------------------------------------------
pow : {n : ℕ} → Perm n → ℕ → Perm n
pow g zero    = id-perm _
pow g (suc k) = compose g (pow g k)

------------------------------------------------------------------------
-- ③ THE BISIMILARITY: word-CONCATENATION IS the build's COMPOSE. `pow g` is a monoid homomorphism
--    (ℕ, +, 0) → (⟨g⟩, compose, id) — the grounding of xFreeCyclic's `_Zn-++_` as the tower's `compose`.
--    So the abstract cyclic word-op need never be recomputed: it is read off the build.
------------------------------------------------------------------------
pow-zero : {n : ℕ} (g : Perm n) → pow g zero ≡ id-perm n
pow-zero g = refl

pow-hom : {n : ℕ} (g : Perm n) (a b : ℕ) →
          pow g (a + b) ≡ compose (pow g a) (pow g b)
pow-hom g zero    b = sym (compose-id-left (pow g b))
pow-hom g (suc a) b = trans (cong (compose g) (pow-hom g a b))
                            (sym (compose-assoc g (pow g a) (pow g b)))
