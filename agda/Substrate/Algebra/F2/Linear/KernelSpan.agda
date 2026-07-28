------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.KernelSpan
--
-- Ⓕ.spectral — dissolving the "dimension needs Gaussian elimination" wall.
--
-- "Dimension of a subspace" is an INCOMPLETE type, because "subspace" is
-- an incomplete type — a typehole: a skeleton with a hole where the basis
-- goes. Completing it does NOT mean EXTRACTING a canonical basis (Gaussian
-- elimination); it means FILLING the hole with a basis the structure
-- already hands you (for the cycle operator: the orbit decomposition). The
-- change to that basis is a CrossMul by (dest-basis / source-basis) — the
-- cospan A → R ← B of Wedge.CrossMul, units cancelling.
--
-- This module proves the load-bearing half at the OPERATOR level (the way
-- spectral-kernel worked — no coordinates):
--
--   kernel-comb-in-ker : every linear combination of a SUPPLIED family of
--     kernel vectors stays in the kernel.
--
-- so a d-element kernel family `b : Fin d → Vector n` extends (via
-- FromImages — the basis is supplied, not extracted) to a linear map
-- F₂ᵈ → ker L. The proof is `linear-extensionality` (agree on basis ⟹
-- agree everywhere) against the zero map: NOTHING is solved for, nothing
-- is eliminated. The remaining half (the family is independent + spans ALL
-- of ker L, giving the iso F₂ᵈ ≅ ker L and hence dim = d) is supplied by
-- the concrete orbit basis in Ⓕ.spectral-bridge, with d = mult2/2·degΦ_p.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.KernelSpan where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply; _∘L_; id-L)
open import Substrate.Algebra.F2.Linear.Cyclotomic using (𝟘L)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Algebra.F2.Linear.Kernel using (inKer)

------------------------------------------------------------------------
-- Any linear combination of a supplied family of kernel vectors is in the
-- kernel. Operator-level: the composite L ∘L (the family's linear span)
-- agrees with the zero map on every basis vector (each family member is in
-- ker L), hence everywhere (linear-extensionality). No coordinates solved.
------------------------------------------------------------------------

kernel-comb-in-ker :
  ∀ {d n m} (L : Linear n m) (b : Fin d → Vector n) →
  (∀ i → inKer L (b i)) →
  (x : Vector d) → inKer L (apply (linear-from-images b) x)
kernel-comb-in-ker L b b∈ker =
  linear-extensionality (L ∘L linear-from-images b) 𝟘L
    (λ i → trans (cong (apply L) (apply-linear-from-images-basis b i)) (b∈ker i))

------------------------------------------------------------------------
-- Dimension of ker L, as an INCOMPLETE type completed by a SUPPLIED basis.
--
-- `KernelDim L d` is the split iso F₂ᵈ ⇄ ker L: `into` lands d basis
-- vectors in ker L, `retract` splits it (indep ⟹ they are independent),
-- and the two are mutually inverse ON ker L (spans ⟹ they span ALL of it).
-- d IS the dimension — SUPPLIED (the typehole's filler), never extracted.
-- "subspace is an incomplete type, and that's fine": d is a parameter, the
-- basis a witness; nothing is solved for, no Gaussian elimination.
------------------------------------------------------------------------

record KernelDim {n m : ℕ} (L : Linear n m) (d : ℕ) : Set where
  field
    into     : Linear d n
    retract  : Linear n d
    into-ker : (x : Vector d) → inKer L (apply into x)
    indep    : (x : Vector d) → apply retract (apply into x) ≡ x
    spans    : (v : Vector n) → inKer L v → apply into (apply retract v) ≡ v

-- Smart constructor: a SUPPLIED family `b` of d kernel vectors, made
-- independent by a `retract` and shown to span ker L, IS a KernelDim — its
-- `into-ker` is automatic (kernel-comb-in-ker). This is the shape the orbit
-- basis of a cycle operator takes to witness dim (ker Φ_p(T)) = mult·degΦ_p:
-- supply the basis (the action gives it) + the retract (its CrossMul inverse).
fromFamily :
  ∀ {d n m} (L : Linear n m) (b : Fin d → Vector n) →
  (∀ i → inKer L (b i)) →
  (r : Linear n d) →
  ((x : Vector d) → apply r (apply (linear-from-images b) x) ≡ x) →
  ((v : Vector n) → inKer L v → apply (linear-from-images b) (apply r v) ≡ v) →
  KernelDim L d
fromFamily L b b∈ker r indep spans = record
  { into = linear-from-images b ; retract = r
  ; into-ker = kernel-comb-in-ker L b b∈ker
  ; indep = indep ; spans = spans }

-- Non-vacuity: the kernel of the zero map is the WHOLE space (dim n), with
-- the identity as the supplied iso. (So the typehole IS inhabitable at the
-- top — n, not a vacuous 0.)
KernelDim-𝟘L : ∀ {n} → KernelDim (𝟘L {n} {n}) n
KernelDim-𝟘L = record
  { into = id-L ; retract = id-L
  ; into-ker = λ _ → refl ; indep = λ _ → refl ; spans = λ _ _ → refl }
