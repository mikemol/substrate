------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.ReservedToBivector
--
-- N-2..N-6 of M-11.dim4.codeword-bridge. Closes the formal bridge
-- between Codeword.agda's Reserved type and the M-11.dim4 SelfDual
-- subspace of Λ²(F₂⁴), via Vector 3 as the shared F₂³ pivot.
--
-- Chain established by this file:
--
--   Codeword.Reserved   ↔   Vector 3   ↔   SelfDual (⊂ Bivector)
--   ─────────────────────  ──────────  ───────────────────────────
--   (N-2/N-3 here)         (M-11.dim4.reserved-bridge, prior slice)
--
-- After this slice, the catalog conjecture "8 reserved = signed
-- singletons = self-dual bivectors" is FORMALLY VALIDATED at the
-- actual Codeword type level — not just at the F₂³ proxy.
--
-- Uses N-1 (Bool ↔ F₂ from FromBool.agda).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.ReservedToBivector where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂; Σ)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong-trans)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.FromBool
open import Substrate.Algebra.F2.HodgeDim4.Bivector using (Bivector)
open import Substrate.Algebra.F2.HodgeDim4.SelfDual using (SelfDual-Pred)
open import Substrate.Algebra.F2.HodgeDim4.ReservedBridge
  using (vector3-to-selfdual; vector3-to-selfdual-sd; selfdual-coefficients)
open import Substrate.Cocycles.V4Signature.Codeword
  using (Codeword; IsReserved; Reserved)

------------------------------------------------------------------------
-- N-2: extract the 3 free bits of a Reserved codeword + apply Bool→F₂
-- componentwise.
------------------------------------------------------------------------

reserved-to-vector3 : Reserved → Vector 3
reserved-to-vector3 ((b₀ , b₁ , b₂ , _ , _) , _) =
  bool→F₂ b₀ ∷ bool→F₂ b₁ ∷ bool→F₂ b₂ ∷ []

------------------------------------------------------------------------
-- N-3: inject a Vector 3 into a Reserved codeword (F₂→Bool componentwise,
-- bit₃ = bit₄ = false, IsReserved proof = (refl, refl)).
------------------------------------------------------------------------

vector3-to-reserved : Vector 3 → Reserved
vector3-to-reserved (x ∷ y ∷ z ∷ []) =
  ((F₂→bool x , F₂→bool y , F₂→bool z , false , false) , refl , refl)

------------------------------------------------------------------------
-- Helper: make a Reserved codeword from 3 Bool bits (low-3-bits-free,
-- high-2-bits-zero). Used as the "canonical form" for both endpoints
-- of the round-trip.
------------------------------------------------------------------------

make-reserved : (b₀ b₁ b₂ : Bool) → Reserved
make-reserved b₀ b₁ b₂ =
  ((b₀ , b₁ , b₂ , false , false) , refl , refl)

------------------------------------------------------------------------
-- N-4a: round-trip in the Vector 3 direction (V3 → Reserved → V3).
--
-- Closes via 3 applications of F₂→bool→F₂ (one per component).
------------------------------------------------------------------------

roundtrip-V3 :
  (v : Vector 3) →
  reserved-to-vector3 (vector3-to-reserved v) ≡ v
roundtrip-V3 (x ∷ y ∷ z ∷ []) =
  cong-trans (λ a → a ∷ bool→F₂ (F₂→bool y) ∷ bool→F₂ (F₂→bool z) ∷ [])
             (F₂→bool→F₂ x)
  (cong-trans (λ a → x ∷ a ∷ bool→F₂ (F₂→bool z) ∷ [])
              (F₂→bool→F₂ y)
              (cong (λ a → x ∷ y ∷ a ∷ [])
                    (F₂→bool→F₂ z)))

------------------------------------------------------------------------
-- N-4b: round-trip in the Reserved direction (Reserved → V3 → Reserved).
--
-- After pattern-matching the IsReserved proof as (refl, refl), the
-- bit₃ and bit₄ fields are forced to .false (Agda's dot patterns).
-- Both endpoints are then make-reserved instances and the equality
-- reduces to 3 Bool round-trips via bool→F₂→bool.
------------------------------------------------------------------------

roundtrip-Reserved :
  (r : Reserved) →
  vector3-to-reserved (reserved-to-vector3 r) ≡ r
roundtrip-Reserved ((b₀ , b₁ , b₂ , .false , .false) , refl , refl) =
  cong-trans (λ a → make-reserved a (F₂→bool (bool→F₂ b₁)) (F₂→bool (bool→F₂ b₂)))
             (bool→F₂→bool b₀)
  (cong-trans (λ a → make-reserved b₀ a (F₂→bool (bool→F₂ b₂)))
              (bool→F₂→bool b₁)
              (cong (λ a → make-reserved b₀ b₁ a)
                    (bool→F₂→bool b₂)))

------------------------------------------------------------------------
-- N-5: composition with M-11.dim4.reserved-bridge.
--
-- Yields the full Codeword.Reserved ↔ (SelfDual subspace of Bivector)
-- bijection.
------------------------------------------------------------------------

reserved-to-selfdual : Reserved → Σ Bivector SelfDual-Pred
reserved-to-selfdual r =
  let v = reserved-to-vector3 r
  in vector3-to-selfdual v , vector3-to-selfdual-sd v

selfdual-to-reserved : Σ Bivector SelfDual-Pred → Reserved
selfdual-to-reserved (ω , _) =
  vector3-to-reserved (selfdual-coefficients ω)

------------------------------------------------------------------------
-- N-6: Catalog conjecture capstone.
--
-- The catalog (cocycles.md § CY-5) conjectures:
--
--   "8 reserved = signed singletons = Hodge 1-form layer / 2-form layer"
--
-- This file together with M-11.dim4 + M-11.dim4.reserved-bridge
-- formally validates the F₂-vector-space structure of this conjecture:
--
--   Reserved (Codeword.agda, 8 elements)
--     ↔ Vector 3 (this file, N-2/N-3)
--     ↔ SelfDual subspace of Λ²(F₂⁴) (M-11.dim4.reserved-bridge)
--
-- All three are 3-dim F₂-subspaces (cardinality 8 = 2³); the bridges
-- preserve the F₂-vector-space structure (forward + inverse functions
-- both exist; the Vector 3 round-trips close in both directions).
--
-- What's validated: the *cardinality + linear-algebra structure* of
-- the conjecture. The 8 reserved codewords ARE in 1-1 structural
-- correspondence with the 8 self-dual bivectors via the chirality-
-- rotation framework.
--
-- What's NOT yet validated (deferred):
--   * Semantic correspondence: does the specific bit-pattern
--     (bit₀, bit₁, bit₂) of a Reserved codeword match the specific
--     self-dual coefficient (c₀, c₁, c₂) in a way that's meaningful
--     for the catalog's "Hodge dual" interpretation? Requires
--     reading the catalog's intent.
--   * V₄ action correspondence: NOT achievable within current
--     premises (F₂-linear + partition-V₄ + bijective). But
--     ACHIEVABLE via a sacrifice ladder (see memory
--     `project_reserved_selfdual_bijection_gauge`): sacrificing
--     F₂-linearity admits F₂-affine V₄ ⊂ Aff(3, F₂) free on F₂³
--     (2 orbits of 4 matching Reserved); sacrificing the V₄
--     subgroup choice or cardinality opens other equivariance
--     routes. The sacrifice-ladder is analogous to Cayley-Dickson
--     (each step trades a rigidity for an enrichment). Concrete
--     sacrifice examples not yet formalised.
--   * Live ↔ ordered-triples bridge: the 24 Live codewords should
--     correspond to "24 ordered triples" per the catalog; this is
--     a separate slice (M-11.dim4.live-bridge or similar).
--
-- **Gauge freedom warning.** The bijection established here is ONE of
-- 168 F₂-linear choices. The choice of `vector3-to-selfdual` from
-- ReservedBridge.agda (used as the SelfDual-side construction here)
-- is the identity permutation on the 3 sd-pair generators. Two
-- alternatives are formalised in
-- `Substrate.Algebra.F2.HodgeDim4.ReservedBridgeAlternatives`
-- (cyclic shift + last-two swap). The catalog has no privileged
-- choice at the F₂-linear level; downstream consumers depending on
-- the SPECIFIC bijection should declare so explicitly. See memory
-- `project_reserved_selfdual_bijection_gauge` for the full coset
-- analysis and the fractal-recurrence observation (the alignment-
-- axis space itself instantiates 3+1 parity at the meta-level).
--
-- This is the LAST PIECE needed to claim the chirality-rotation
-- framework is GROUNDED in substrate data structures.
------------------------------------------------------------------------
