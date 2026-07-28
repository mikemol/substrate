------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.PermSign
--
-- ◆ip-cap-group-iso — the CONCRETE quotient Sₙ / Aₙ ≅ Z/2, realized in the
-- substrate's own split-idempotent idiom (NO HITs, NO quotient-group object).
--
--   sign-Canonical = split-Canonical sign s retract : Canonical (ker-Quotient sign)
--
-- i.e. the kernel-quotient `Perm N / ker sign` is realized WITHOUT a quotient
-- type, exactly because `sign` SPLITS: the section `s : Bool → Perm N`
-- (false ↦ id-perm, true ↦ the adjacent transposition s₀) retracts it. The
-- canonical form is the split idempotent `s ∘ sign`, whose image is the
-- two-element representative set {id-perm, sadj₀} — literally Z/2 inside Sₙ.
--
-- THE KERNEL IS [Sₙ,Sₙ] = Aₙ (§4): σ is in the identity's class IFF σ is in
-- the commutator subgroup, both directions already TERMS —
--   →  `even→InComm-perm`  (EvenInComm.Properties, ◆ip-cap-reverse)
--   ←  `InComm→even`       (CommutatorSubgroup, the easy containment)
-- so the quotient this Canonical realizes is EXACTLY the quotient by the
-- commutator subgroup: the abelianization, computed on the concrete carrier.
--
-- THE GROUP STRUCTURE IS FREE (§5): `sign` is already a homomorphism
-- (`sign-hom`, `sign-id`), so post-composing the proven Bool↔F₂ additive
-- op-hom gives `sign₂ : Perm N → F₂` with `sign₂ (σ∘τ) ≡ sign₂ σ + sign₂ τ`.
-- The section `s` need NOT be a hom — `split-Canonical` uses it only through
-- `cong s` — which is why the group iso costs nothing beyond the section.
-- (Precedent: `factor-Canonical` + `product-++`, Nat/Prime/Properties — the
-- fold is a monoid hom ⟹ the induced bijection is a monoid iso.)
--
-- ⚑ ARITY (load-bearing): `sadj n j` needs `j : Fin n` and lands in
-- `Perm (suc n)`, so a section into `Perm N` forces `N = suc (suc n')`. This
-- is mathematically correct, not a workaround — S₀ and S₁ have no odd element,
-- so there is nothing to be the section's `true` value below grade 2.
--
-- HONEST BOUNDARY: this is the CONCRETE `Perm`-carrier quotient. It does NOT
-- identify the presented group with `Perm n` (that is Matsumoto/Tits
-- completeness, still absent) — see `SnAbelianizationZ2` for the presented
-- Route C and `SnAbCharacterBridge` for the proof that the two CHARACTERS
-- coincide.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.PermSign where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Algebra.Quotient
open import Substrate.Algebra.F2 using (F₂; 𝟘; _+_)
open import Substrate.Algebra.F2.FromBool using (bool→F₂; bool→F₂-xor)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign
  using (sign; sign-id; sign-sadj; sign-hom; id-perm-is-perm; sadj-is-perm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterGeneral
  using (sadj)
open import Substrate.WitnessTower.CommutatorSubgroup using (InComm; InComm→even)
open import Substrate.WitnessTower.EvenInComm.Properties using (even→InComm-perm)

module _ (n' : ℕ) where

  -- the grade the section forces (see the ARITY note in the header).
  N : ℕ
  N = suc (suc n')

  ------------------------------------------------------------------------
  -- 1. The map. `sign : {m n} → Vec (Fin m) n → Bool` is implicit-indexed;
  --    `signP` pins it at the square shape so it is a bare `Perm N → Bool`.
  ------------------------------------------------------------------------

  signP : Perm N → Bool
  signP σ = sign σ

  ------------------------------------------------------------------------
  -- 2. The SECTION and its RETRACT — the only new content in this module.
  --    false ↦ the identity (even); true ↦ an adjacent transposition (odd).
  ------------------------------------------------------------------------

  s : Bool → Perm N
  s false = id-perm N
  s true  = sadj (suc n') zero

  retract : (x : Bool) → signP (s x) ≡ x
  retract false = sign-id {N}
  retract true  = sign-sadj (suc n') zero

  -- both classes are realized by GENUINE permutations (surjectivity of sign
  -- onto Bool, witnessed rather than asserted).
  s-is-perm : (x : Bool) → IsPerm (s x)
  s-is-perm false = id-perm-is-perm {N}
  s-is-perm true  = sadj-is-perm (suc n') zero

  ------------------------------------------------------------------------
  -- 3. THE DELIVERABLE: Sₙ / ker sign as a canonical form (split idempotent).
  ------------------------------------------------------------------------

  sign-Quotient : Quotient (Perm N) (KerRel signP)
  sign-Quotient = ker-Quotient signP

  sign-Canonical : Canonical sign-Quotient
  sign-Canonical = split-Canonical signP s retract

  -- the canonical representative set is EXACTLY the two elements {id, sadj₀}
  -- — the Z/2 sitting inside Sₙ. Both are `cong s` on the sign value.
  canonical-even : (σ : Perm N) → signP σ ≡ false →
                   Canonical.canonical sign-Canonical σ ≡ id-perm N
  canonical-even σ e = cong s e

  canonical-odd : (σ : Perm N) → signP σ ≡ true →
                  Canonical.canonical sign-Canonical σ ≡ sadj (suc n') zero
  canonical-odd σ e = cong s e

  ------------------------------------------------------------------------
  -- 4. THE KERNEL IS THE COMMUTATOR SUBGROUP: the identity's class = [Sₙ,Sₙ].
  --    This is what certifies that the quotient above is the ABELIANIZATION
  --    and not merely some kernel-quotient. Both directions are existing terms.
  ------------------------------------------------------------------------

  class-of-id→InComm : (σ : Perm N) → IsPerm σ →
                       KerRel signP σ (id-perm N) → InComm σ
  class-of-id→InComm σ pf e = even→InComm-perm σ pf (trans e (sign-id {N}))

  InComm→class-of-id : {σ : Perm N} → InComm σ → KerRel signP σ (id-perm N)
  InComm→class-of-id ic = trans (InComm→even ic) (sym (sign-id {N}))

  ------------------------------------------------------------------------
  -- 5. THE GROUP ISO, in F₂. `sign` is a hom into (Bool, xor, false); the
  --    proven additive op-hom `bool→F₂-xor` carries it to (F₂, +, 𝟘).
  ------------------------------------------------------------------------

  sign₂ : Perm N → F₂
  sign₂ σ = bool→F₂ (signP σ)

  sign₂-id : sign₂ (id-perm N) ≡ 𝟘
  sign₂-id = cong bool→F₂ (sign-id {N})

  sign₂-hom : (σ τ : Perm N) → IsPerm σ → IsPerm τ →
              sign₂ (compose σ τ) ≡ (sign₂ σ + sign₂ τ)
  sign₂-hom σ τ pσ pτ =
    trans (cong bool→F₂ (sign-hom σ τ pσ pτ))
          (bool→F₂-xor (sign σ) (sign τ))

------------------------------------------------------------------------
-- 6. Capstone.
--
-- For every n' : ℕ, at grade N = suc (suc n'):
--   · `sign-Canonical` realizes Perm N / ker sign as a canonical form whose
--     representatives are the two-element set {id-perm, sadj₀} ≅ Z/2;
--   · §4 identifies ker sign's identity-class with the commutator subgroup
--     [Sₙ,Sₙ] (= Aₙ), so that quotient IS the abelianization;
--   · §5 makes it a GROUP iso into (F₂, +, 𝟘), for free from `sign-hom`.
-- Together: the sign is THE nontrivial abelian character of Sₙ on the
-- concrete carrier — "the whole abelianization is one bit."
------------------------------------------------------------------------
