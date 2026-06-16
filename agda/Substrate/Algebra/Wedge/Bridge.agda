------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Bridge
--
-- THE CROSS-CARRIER BRIDGE — the on-mission constructor. A correspondence
-- between two silos D₁, D₂ (each a DivStr) is a `Bridge`: a translation of
-- carriers that RESPECTS the wedge structure, so it carries the whole
-- Euclidean apparatus across — `transport-wedge` and `transport-trace` move
-- wedges and traces (hence gcd, Bézout, mod) from one silo to the other.
-- Constructing the bridge IS constructing the cross-field correspondence.
--
--   Bridge D₁ D₂ = ( translate : C D₁ → C D₂
--                  , respects  : translate (recon₁ q b r)
--                                  ≡ recon₂ q (translate b) (translate r)
--                  , z-pres    : translate z₁ ≡ z₂ )
--
-- This is the POSITIVE / exact correspondence (the homomorphism — remainder
-- everywhere trivial). The NEGATIVE-capable form is `LaxBridge`: `respects`
-- weakened to a GAP WEDGE in D₂ measuring how far translate is from a
-- homomorphism. The correspondence is POSITIVE exactly where every gap reads
-- the `=`-corner (quot 1, rem z) — which needs the carrier's recon-unit law
-- `recon 1 x z ≡ x` (the law that makes `=` the (1,z) read) — and NEGATIVE
-- where some gap's remainder is provably ≠ z (a constructive non-correspondence).
--
-- HONEST SCOPE: the positive Bridge + transport are proved here. LaxBridge is
-- the negative-capable shape; the positive/negative READING (gap = (1,z))
-- needs the recon-unit law, a deliberate next refinement, not claimed here.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Bridge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Algebra.Wedge
  using (DivStr; C; z; recon; Wedge; quot; rem; wedge-eq; Trace; done; more)

------------------------------------------------------------------------
-- 1. The bridge: a structure-respecting translation between silos.
------------------------------------------------------------------------

record Bridge (D₁ D₂ : DivStr) : Set where
  field
    translate : C D₁ → C D₂
    respects  : (q b r : C D₁) →        -- the quotient q is a carrier element, so translate maps it too
                translate (recon D₁ q b r)
                  ≡ recon D₂ (translate q) (translate b) (translate r)
    z-pres    : translate (z D₁) ≡ z D₂

open Bridge public

------------------------------------------------------------------------
-- 2. The bridge transports the Euclidean structure across silos.
------------------------------------------------------------------------

-- a wedge in D₁ becomes a wedge in D₂ (quotient and remainder both translated).
transport-wedge : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b : C D₁} →
                  Wedge D₁ a b → Wedge D₂ (translate br a) (translate br b)
transport-wedge br {a} {b} w = record
  { quot     = translate br (quot w)
  ; rem      = translate br (rem w)
  ; wedge-eq = trans (cong (translate br) (wedge-eq w))
                     (respects br (quot w) b (rem w))
  }

-- a whole Euclidean trace becomes a trace in D₂ — so gcd / Bézout / mod
-- (the trace-reads) all transport: a positive correspondence carries the
-- number theory of one silo onto the other.
transport-trace : {D₁ D₂ : DivStr} (br : Bridge D₁ D₂) {a b g : C D₁} →
                  Trace D₁ a b g →
                  Trace D₂ (translate br a) (translate br b) (translate br g)
transport-trace br (done a) =
  subst (λ d → Trace _ (translate br a) d (translate br a))
        (sym (z-pres br)) (done (translate br a))
transport-trace br (more b w rec) =
  more (translate br b) (transport-wedge br w) (transport-trace br rec)

------------------------------------------------------------------------
-- 3. Witness: the identity bridge (every silo corresponds to itself).
------------------------------------------------------------------------

id-bridge : (D : DivStr) → Bridge D D
id-bridge D = record
  { translate = λ x → x ; respects = λ q b r → refl ; z-pres = refl }

------------------------------------------------------------------------
-- 4. The negative-capable form: respects weakened to a gap wedge.
--    Positive = every gap reads the (1, z) corner (needs recon-unit law);
--    negative = some gap's remainder is provably ≠ z.
------------------------------------------------------------------------

record LaxBridge (D₁ D₂ : DivStr) : Set where
  field
    translate : C D₁ → C D₂
    gap : (q b r : C D₁) →
          Wedge D₂ (translate (recon D₁ q b r))
                   (recon D₂ (translate q) (translate b) (translate r))

open LaxBridge public
