------------------------------------------------------------------------
-- Substrate.WitnessTower.SignEmbedVEven
--
-- ⟡sign-embed-v-even — the GENERAL lemma got by feeding the stab'd
-- (concrete) lemma THROUGH THE PERMUTATION GENERATOR (user: "you get the
-- general lemma by feeding the stab'd lemma through the permutation
-- generator").
--
-- CONCRETE (stab'd) base: sign (perm4 (embed v)) ≡ false for every v : V₄.
-- V₄ has exactly 4 elements, so this is 4 refl cases — V₄ ⊂ A₄, the Klein
-- four-group is even. This is the "stab'd" fact: true at each concrete point.
--
-- THE GENERATOR is permutation composition: sign-hom (itself proved by
-- lifting an adjacent-swap flip through the Coxeter generators) states
-- sign (compose σ τ) ≡ sign σ xor sign τ. Feeding the concrete
-- sign(embed v)=0 through it — over ARBITRARY s — yields the general
-- orientation lemma:
--
--   sign (perm4 (embed v · s)) ≡ sign (perm4 s)       (for all v : V₄, s)
--
-- i.e. the V₄ part contributes nothing to the sign of ANY S₄ element, not
-- just the 24 codeword cases. This upgrades SignFactorsThroughStab from the
-- codeword domain to all of S₄: sign σ is the parity of its Stab component,
-- because the V₄ factor is even — proven generally, via the generator.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SignEmbedVEven where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; tabulate; lookup)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Bool using (Bool; false; _xor_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (compose)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.SnGroup using (apply-injective)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign; sign-hom)
open import Substrate.Axes using (Axis)
open import Substrate.Axes.Punctured using (a→f; f→a; f→a→f; a→f→a)
open import Substrate.Groups.S4 using (Permutation; _·_; apply)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.V4 using (V₄; e; α; β; γ)

-- transport S4.Permutation → Perm 4.
perm4 : Permutation → Perm 4
perm4 π = tabulate (λ i → a→f (apply π (f→a i)))

------------------------------------------------------------------------
-- 1. THE CONCRETE (stab'd) BASE: sign(perm4(embed v)) = false, all v : V₄.
--    Four elements, four refls — V₄ ⊂ A₄ (Klein four is even).
------------------------------------------------------------------------

sign-embed-v-zero : (v : V₄) → sign (perm4 (embed v)) ≡ false
sign-embed-v-zero e = refl
sign-embed-v-zero α = refl
sign-embed-v-zero β = refl
sign-embed-v-zero γ = refl

------------------------------------------------------------------------
-- 2. THE GENERATOR: perm4 preserves composition. lookup∘tabulate strips
--    both sides; apply is a homomorphism (record composition, refl).
------------------------------------------------------------------------

perm4-compose :
  (a b : Permutation) → perm4 (a · b) ≡ compose (perm4 a) (perm4 b)
perm4-compose a b = apply-injective λ i →
  trans (lookup∘tabulate (λ j → a→f (apply (a · b) (f→a j))) i)
        (sym (compose-lookup i))
  where
    compose-lookup : (i : Fin 4) →
      lookup (compose (perm4 a) (perm4 b)) i ≡ a→f (apply a (apply b (f→a i)))
    compose-lookup i =
      trans (lookup∘tabulate (λ k → lookup (perm4 a) (lookup (perm4 b) k)) i)
            (trans (cong (lookup (perm4 a)) (lookup∘tabulate (λ j → a→f (apply b (f→a j))) i))
                   (trans (lookup∘tabulate (λ j → a→f (apply a (f→a j))) (a→f (apply b (f→a i))))
                          (cong (λ z → a→f (apply a z)) (a→f→a (apply b (f→a i))))))

------------------------------------------------------------------------
-- 3. perm4 outputs are genuine permutations (needed for sign-hom).
--    Injectivity from apply's bijectivity + a→f/f→a roundtrips.
------------------------------------------------------------------------

open import Substrate.Groups.S4 using (invₐ; inv-l; inv-r)
open import Substrate.Axes.Punctured using (a→f-inj; f→a→f)

perm4-isperm : (π : Permutation) → IsPerm (perm4 π)
perm4-isperm π i j eq = i≡j
  where
    lhs : a→f (apply π (f→a i)) ≡ a→f (apply π (f→a j))
    lhs = trans (sym (lookup∘tabulate (λ k → a→f (apply π (f→a k))) i))
                (trans eq (lookup∘tabulate (λ k → a→f (apply π (f→a k))) j))
    -- strip a→f (a→f-inj), then apply's injectivity (via inv-l), giving f→a i ≡ f→a j
    faij : f→a i ≡ f→a j
    faij = trans (sym (inv-l π (f→a i)))
                 (trans (cong (invₐ π) (a→f-inj lhs)) (inv-l π (f→a j)))
    -- lift through the f→a→f roundtrip: i ≡ j
    i≡j : i ≡ j
    i≡j = trans (sym (f→a→f i)) (trans (cong a→f faij) (f→a→f j))

------------------------------------------------------------------------
-- 4. THE GENERAL LEMMA, via the generator. Feed sign-embed-v-zero through
--    perm4-compose + sign-hom: the V₄ factor contributes nothing to the
--    sign of ANY composite. sign(perm4(embed v · s)) ≡ sign(perm4 s).
------------------------------------------------------------------------

open import Substrate.Foundation.Bool using (true)

-- false xor b ≡ b (the V₄ contribution drops out).
xor-falseˡ : (b : Bool) → (false xor b) ≡ b
xor-falseˡ true  = refl
xor-falseˡ false = refl

sign-embed-v-even :
  (v : V₄) (s : Permutation) →
  sign (perm4 (embed v · s)) ≡ sign (perm4 s)
sign-embed-v-even v s =
  trans (cong sign (perm4-compose (embed v) s))
        (trans (sign-hom (perm4 (embed v)) (perm4 s)
                         (perm4-isperm (embed v)) (perm4-isperm s))
               (trans (cong (_xor sign (perm4 s)) (sign-embed-v-zero v))
                      (xor-falseˡ (sign (perm4 s)))))
