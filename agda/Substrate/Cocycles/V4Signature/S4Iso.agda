------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.S4Iso
--
-- S10 of slice 3: the bijection TotalSpace ≃ S_4 — the catalog's
-- "the 24 ARE S_4" identification (M41 v19) made constructive.
--
-- TotalSpace of the CY-5 cocycle = Σ OrbitKey (λ _ → V_4) — pairs of
-- (orbit-key, V_4 fiber-position). Under the V_4 ⋊ S_3 ≅ S_4
-- factorisation (proved in Substrate.Groups.SemidirectProduct), each
-- such pair corresponds bijectively to a permutation in S_4.
--
-- This file establishes the forward direction:
--   total-to-s4 : TotalSpace → Permutation
-- via:
--   total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok
--
-- where orbit-key-to-stab-d : OrbitKey → Permutation maps each of
-- the 6 orbit-keys to a specific S_3 representative in Stab(D):
--
--     (α-pair, even) ↔ identity     (D fixed, C fixed, S↔S, W↔W)
--     (α-pair, odd)  ↔ (SW)         (D fixed, C fixed, S↔W)
--     (β-pair, even) ↔ (CSW)        (D fixed, C→S→W→C)
--     (β-pair, odd)  ↔ (CS)         (D fixed, S fixed, C↔S — wait, W fixed)
--     (γ-pair, even) ↔ (CWS)        (D fixed, C→W→S→C)
--     (γ-pair, odd)  ↔ (CW)         (D fixed, C↔W, S fixed)
--
-- The reverse direction (s4-to-total) and the round-trip proofs are
-- deferred to a follow-on session — see TODO at file end. The
-- round-trip requires defining stab-d-to-orbit-key, which case-
-- analyses on (apply σ C, apply σ S) for σ ∈ Stab(D); 9 cases (some
-- impossible) before the valid 6.
--
-- See: catalog/cocycles.md § CY-5 — "The 24 ARE S_4".
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.S4Iso where

open import Level using (0ℓ)
open import Data.Product using (_,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _≈_; _·_; _⁻¹; ε)
  renaming (apply to applyₛ; invₐ to invₐₛ)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.SemidirectProduct
  using (Stab-D; v-for; s-for; s-for-fixes-D; factorisation)
open import Substrate.Cocycles.V4Signature
  using (Pairing; α-pair; β-pair; γ-pair;
         Chirality; even; odd;
         OrbitKey;
         CY5-V4Signature)
open import Substrate.Cocycle using (IsomorphicCocycleStructure)

------------------------------------------------------------------------
-- Builder for Stab(D) elements.
--
-- Each non-identity element of Stab(D) permutes {C, S, W} while
-- fixing D. We define each as an explicit Permutation record.
------------------------------------------------------------------------

-- Identity in Stab(D): the S_4 identity (already defined as ε).
stab-id : Permutation
stab-id = ε

-- (SW): D↔D, C↔C, S↔W. Self-inverse (involution).
stab-sw : Permutation
stab-sw = record
  { apply = ap
  ; invₐ  = ap
  ; inv-l = invo
  ; inv-r = invo
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = C
    ap S = W
    ap W = S
    invo : (x : Axis) → ap (ap x) ≡ x
    invo D = refl
    invo C = refl
    invo S = refl
    invo W = refl

-- (CS): D↔D, S↔S? — wait, (CS) swaps C and S; W is fixed.
-- D↔D, W↔W, C↔S. Self-inverse.
stab-cs : Permutation
stab-cs = record
  { apply = ap
  ; invₐ  = ap
  ; inv-l = invo
  ; inv-r = invo
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = S
    ap S = C
    ap W = W
    invo : (x : Axis) → ap (ap x) ≡ x
    invo D = refl
    invo C = refl
    invo S = refl
    invo W = refl

-- (CW): D↔D, S↔S, C↔W. Self-inverse.
stab-cw : Permutation
stab-cw = record
  { apply = ap
  ; invₐ  = ap
  ; inv-l = invo
  ; inv-r = invo
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = W
    ap S = S
    ap W = C
    invo : (x : Axis) → ap (ap x) ≡ x
    invo D = refl
    invo C = refl
    invo S = refl
    invo W = refl

-- (CSW): the 3-cycle C→S→W→C, with D fixed.
-- apply: C→S, S→W, W→C, D→D.
-- invₐ:  (CWS) = C→W, W→S, S→C, D→D.
stab-csw : Permutation
stab-csw = record
  { apply = ap
  ; invₐ  = inv-ap
  ; inv-l = il
  ; inv-r = ir
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = S
    ap S = W
    ap W = C
    inv-ap : Axis → Axis
    inv-ap D = D
    inv-ap C = W
    inv-ap S = C
    inv-ap W = S
    il : (x : Axis) → inv-ap (ap x) ≡ x
    il D = refl
    il C = refl
    il S = refl
    il W = refl
    ir : (x : Axis) → ap (inv-ap x) ≡ x
    ir D = refl
    ir C = refl
    ir S = refl
    ir W = refl

-- (CWS): the 3-cycle C→W→S→C, with D fixed. Inverse of (CSW).
stab-cws : Permutation
stab-cws = record
  { apply = ap
  ; invₐ  = inv-ap
  ; inv-l = il
  ; inv-r = ir
  }
  where
    ap : Axis → Axis
    ap D = D
    ap C = W
    ap S = C
    ap W = S
    inv-ap : Axis → Axis
    inv-ap D = D
    inv-ap C = S
    inv-ap S = W
    inv-ap W = C
    il : (x : Axis) → inv-ap (ap x) ≡ x
    il D = refl
    il C = refl
    il S = refl
    il W = refl
    ir : (x : Axis) → ap (inv-ap x) ≡ x
    ir D = refl
    ir C = refl
    ir S = refl
    ir W = refl

------------------------------------------------------------------------
-- Verification that each constructed element is in Stab(D).
------------------------------------------------------------------------

stab-id-fixes-D : Stab-D stab-id
stab-id-fixes-D = refl

stab-sw-fixes-D : Stab-D stab-sw
stab-sw-fixes-D = refl

stab-cs-fixes-D : Stab-D stab-cs
stab-cs-fixes-D = refl

stab-cw-fixes-D : Stab-D stab-cw
stab-cw-fixes-D = refl

stab-csw-fixes-D : Stab-D stab-csw
stab-csw-fixes-D = refl

stab-cws-fixes-D : Stab-D stab-cws
stab-cws-fixes-D = refl

------------------------------------------------------------------------
-- The OrbitKey → Stab(D) map.
--
-- This embodies a SPECIFIC bijection between the 6 orbit-keys and
-- the 6 elements of Stab(D). Per the catalog's isomorphic-storage
-- discipline, the choice of WHICH Stab(D) element each orbit-key
-- maps to is a CONVENTION — not a structural commitment. A future
-- session may parametrise the choice; here we encode one explicit
-- convention.
--
-- Convention: pairing-of-(D, σ(C)) determines the V_4 partition;
-- chirality is the parity of the underlying S_3 permutation.
--
--   (α, even): D & C fixed → identity
--   (α, odd):  D & C fixed, S↔W → (SW)
--   (β, even): D fixed, C→S, S→W, W→C (3-cycle, even) → (CSW)
--   (β, odd):  D & W fixed, C↔S → (CS)
--   (γ, even): D fixed, C→W, W→S, S→C (3-cycle, even) → (CWS)
--   (γ, odd):  D & S fixed, C↔W → (CW)
------------------------------------------------------------------------

orbit-key-to-stab-d : OrbitKey → Permutation
orbit-key-to-stab-d (α-pair , even) = stab-id
orbit-key-to-stab-d (α-pair , odd)  = stab-sw
orbit-key-to-stab-d (β-pair , even) = stab-csw
orbit-key-to-stab-d (β-pair , odd)  = stab-cs
orbit-key-to-stab-d (γ-pair , even) = stab-cws
orbit-key-to-stab-d (γ-pair , odd)  = stab-cw

-- Each constructed Stab(D) element fixes D (trivially).
orbit-key-to-stab-d-fixes-D :
  (ok : OrbitKey) → Stab-D (orbit-key-to-stab-d ok)
orbit-key-to-stab-d-fixes-D (α-pair , even) = stab-id-fixes-D
orbit-key-to-stab-d-fixes-D (α-pair , odd)  = stab-sw-fixes-D
orbit-key-to-stab-d-fixes-D (β-pair , even) = stab-csw-fixes-D
orbit-key-to-stab-d-fixes-D (β-pair , odd)  = stab-cs-fixes-D
orbit-key-to-stab-d-fixes-D (γ-pair , even) = stab-cws-fixes-D
orbit-key-to-stab-d-fixes-D (γ-pair , odd)  = stab-cw-fixes-D

------------------------------------------------------------------------
-- TotalSpace of the CY-5 cocycle (re-exposed from V4Signature).
--
-- TotalSpace = Σ OrbitKey (λ _ → V_4). Each element is (orbit-key,
-- V_4-fiber-position).
------------------------------------------------------------------------

TotalSpace : Set
TotalSpace = IsomorphicCocycleStructure.TotalSpace CY5-V4Signature

------------------------------------------------------------------------
-- The forward map: TotalSpace → S_4.
--
-- Constructed via the semidirect product structure: given (ok, v),
-- the permutation is (embed v) · (orbit-key-to-stab-d ok), which is
-- a V_4-element · Stab(D)-element.
------------------------------------------------------------------------

total-to-s4 : TotalSpace → Permutation
total-to-s4 (ok , v) = embed v · orbit-key-to-stab-d ok

------------------------------------------------------------------------
-- TODO (deferred to follow-on session) — S10 completion
--
-- 1. Define `stab-d-to-orbit-key : (σ : Permutation) → Stab-D σ →
--    OrbitKey`. Case analysis on (applyₛ σ C, applyₛ σ S):
--      σ(C) = C: pairing = α-pair. σ(S) = S → even; σ(S) = W → odd.
--      σ(C) = S: pairing = β-pair. σ(S) = W → even (CSW); σ(S) = C → odd (CS).
--      σ(C) = W: pairing = γ-pair. σ(S) = C → even (CWS); σ(S) = S → odd (CW).
--      Impossible cases (σ(C) = D, σ(S) = D, σ(S) = σ(C)) handled
--      via bijectivity from the Permutation record's inv-l / inv-r
--      contradicting Stab-D constraints.
--
-- 2. Define the inverse map:
--      s4-to-total σ = (stab-d-to-orbit-key (s-for σ) (s-for-fixes-D σ)
--                     , v-for σ)
--
-- 3. Prove round-trip identities:
--      total-to-s4 (s4-to-total σ) ≈ σ
--      s4-to-total (total-to-s4 (ok , v)) ≡ (ok , v)
--    Both follow from S9's factorisation-unique-V₄ + a case-analytic
--    "round trip orbit-key → stab-d → orbit-key" lemma.
--
-- 4. Package as an Iso (or Bijection from stdlib's Function.Bundles):
--      TotalSpace↔S₄ : TotalSpace ↔ Permutation
--    This is the catalog's "24 ARE S_4" identification, now a
--    type-level fact.
--
-- 5. (Stretch) Show the bijection is a GROUP isomorphism — total-to-s4
--    preserves the natural group operation on TotalSpace (induced
--    from S_4 via the bijection itself, or alternatively from the
--    V_4 ⋊ Stab(D) semidirect structure).
------------------------------------------------------------------------
