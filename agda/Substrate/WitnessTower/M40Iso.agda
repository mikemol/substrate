------------------------------------------------------------------------
-- Σ-SEAM-GLUE / ΞB1 (a)+(b) — closing B1: ⟨real generator actions⟩ ≅ A4Z2.
--
-- (a) GENERATION: every (s,m,j) ∈ A4Z2 is a compose-product of the model
--     generators gT α/β/γ, gZ, gchi. With M40Action.act-hom + the *-gen
--     identities, this upgrades ⟨real generator actions⟩ from ⊆ act(A4Z2)
--     to = act(A4Z2): every act g is a composition of the real generators.
--
-- (b) FAITHFULNESS: act is injective on a concrete probe carrier
--     𝕍 = V₄ × Chir, F₀ k = (k, even) (distinct, distinct-under-neg — the
--     role of the Python's F=[10,20,30,40]). So A4Z2 ≅ act(A4Z2) = the
--     closure: the explicit iso B1's `Then` asks for.
--
-- (a)+(b)+act-hom = B1's observable computed from the GENERATOR actions,
-- never read off the model.  (PENDING beyond B1: B2ii V₄⋊Z₃=A₄, B3 contrast.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.M40Iso where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ; _·_)
open import Substrate.Groups.V4.Axioms using (·-assoc; ε-left; ε-identity; inv-left)
open import Substrate.Groups.Actions.S3-on-V4.Generators.Rotate using (rotate)
open import Substrate.Groups.Actions.S3-on-V4.Generators.RotateCubeId using (rotate³-id)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Foundation.Product using (proj₂)
open import Substrate.WitnessTower.M40Closure
  using (Chir; even; odd; _*c_; Z3; z0; z1; z2; _+₃_; σ; A4Z2; mk; compose; a4z2-≡)
open A4Z2
import Substrate.WitnessTower.M40Action as MA
open MA using (cinv; cinv-hom)

ε-right : (x : V₄) → (x · e) ≡ x
ε-right = proj₂ ε-identity

------------------------------------------------------------------------
-- (a) GENERATION — every element is a product of generators.
------------------------------------------------------------------------

gT : V₄ → A4Z2            -- spectral translation by m
gT m = mk even m z0
gchi : A4Z2               -- chirality
gchi = mk odd e z0
gZ : A4Z2                 -- the Z₃ cycle
gZ = mk even e z1

gZpow : Z3 → A4Z2
gZpow z0 = mk even e z0
gZpow z1 = gZ
gZpow z2 = compose gZ gZ

gZpow-correct : (j : Z3) → gZpow j ≡ mk even e j
gZpow-correct z0 = refl
gZpow-correct z1 = refl
gZpow-correct z2 = a4z2-≡ refl (ε-left e) refl

sgn-gen : Chir → A4Z2
sgn-gen even = mk even e z0
sgn-gen odd  = gchi

inner : (m : V₄) (j : Z3) → compose (gT m) (gZpow j) ≡ mk even m j
inner m j = trans (cong (compose (gT m)) (gZpow-correct j)) (a4z2-≡ refl (ε-right m) refl)

outer : (s : Chir) (m : V₄) (j : Z3) → compose (sgn-gen s) (mk even m j) ≡ mk s m j
outer even m j = a4z2-≡ refl (ε-left m) refl
outer odd  m j = a4z2-≡ refl (ε-left m) refl

-- every (s,m,j) reconstructed as chirality · translation · cycle-power.
reconstruct : (s : Chir) (m : V₄) (j : Z3) →
              compose (sgn-gen s) (compose (gT m) (gZpow j)) ≡ mk s m j
reconstruct s m j = trans (cong (compose (sgn-gen s)) (inner m j)) (outer s m j)

------------------------------------------------------------------------
-- (b) FAITHFULNESS — act injective on the probe carrier 𝕍 = V₄ × Chir.
------------------------------------------------------------------------

oflip : Chir → Chir
oflip even = odd
oflip odd  = even

oflip-invol : (c : Chir) → oflip (oflip c) ≡ c
oflip-invol even = refl
oflip-invol odd  = refl

record VC : Set where
  constructor _,,_
  field
    vcv : V₄
    vcc : Chir
open VC

negVC : VC → VC
negVC x = vcv x ,, oflip (vcc x)

negVC-invol : (x : VC) → negVC (negVC x) ≡ x
negVC-invol x = cong (vcv x ,,_) (oflip-invol (vcc x))

open MA.Action VC negVC negVC-invol using (act)

F₀ : V₄ → VC
F₀ k = k ,, even

-- act reads its sign into the Chir component and its index into the V₄ component:
vcc-act : (s : Chir) (m : V₄) (j : Z3) (k : V₄) → vcc (act (mk s m j) F₀ k) ≡ s
vcc-act even m j k = refl
vcc-act odd  m j k = refl

vcv-act : (s : Chir) (m : V₄) (j : Z3) (k : V₄) → vcv (act (mk s m j) F₀ k) ≡ cinv j (k · m)
vcv-act even m j k = refl
vcv-act odd  m j k = refl

-- V₄ right cancellation (group; every element self-inverse: c·c ≡ e).
cancelʳ : (a b c : V₄) → a · c ≡ b · c → a ≡ b
cancelʳ a b c eq =
  trans (sym (ε-right a))
  (trans (cong (a ·_) (sym csq))
  (trans (sym (·-assoc a c c))
  (trans (cong (_· c) eq)
  (trans (·-assoc b c c)
  (trans (cong (b ·_) csq)
         (ε-right b))))))
  where csq : c · c ≡ e
        csq = inv-left c

-- σ and c⁻ are mutual inverses the OTHER way too (σ j (c⁻ʲ a) ≡ a).
sigma-cinv : (j : Z3) (a : V₄) → σ j (cinv j a) ≡ a
sigma-cinv z0 a = refl
sigma-cinv z1 a = rotate³-id a
sigma-cinv z2 a = rotate³-id a

cinv-injective : (j : Z3) (x y : V₄) → cinv j x ≡ cinv j y → x ≡ y
cinv-injective j x y eq =
  trans (sym (sigma-cinv j x)) (trans (cong (σ j) eq) (sigma-cinv j y))

-- a discriminator that reads j off cinv j α (= α / γ / β for z0/z1/z2) —
-- avoids needing constructor-distinctness of V₄.
readJ : V₄ → Z3
readJ e = z0
readJ α = z0
readJ β = z2
readJ γ = z1

readJ-cinv : (j : Z3) → readJ (cinv j α) ≡ j
readJ-cinv z0 = refl
readJ-cinv z1 = refl
readJ-cinv z2 = refl

-- THE iso half: act is injective (faithful) on F₀ — distinct elements act differently.
act-faithful : (g h : A4Z2) → ((k : V₄) → act g F₀ k ≡ act h F₀ k) → g ≡ h
act-faithful g h H = a4z2-≡ s-eq m-eq j-eq
  where
    sg sh : Chir
    sg = chir g ; sh = chir h
    mg mh : V₄
    mg = mask g ; mh = mask h
    jg jh : Z3
    jg = zee g ; jh = zee h

    s-eq : sg ≡ sh
    s-eq = trans (sym (vcc-act sg mg jg e))
           (trans (cong vcc (H e)) (vcc-act sh mh jh e))

    -- P : c⁻ʲᵍ mg ≡ c⁻ʲʰ mh   (from H at e, peeling ε)
    P : cinv jg mg ≡ cinv jh mh
    P = trans (cong (cinv jg) (sym (ε-left mg)))
        (trans (sym (vcv-act sg mg jg e))
        (trans (cong vcv (H e))
        (trans (vcv-act sh mh jh e)
               (cong (cinv jh) (ε-left mh)))))

    -- recover j: c⁻ʲᵍ α ≡ c⁻ʲʰ α (cancel the shared mg-factor), then readJ.
    eqα : cinv jg α ≡ cinv jh α
    eqα = cancelʳ (cinv jg α) (cinv jh α) (cinv jg mg) step
      where
        step : cinv jg α · cinv jg mg ≡ cinv jh α · cinv jg mg
        step = trans (sym (cinv-hom jg α mg))
               (trans (sym (vcv-act sg mg jg α))
               (trans (cong vcv (H α))
               (trans (vcv-act sh mh jh α)
               (trans (cinv-hom jh α mh)
                      (cong (cinv jh α ·_) (sym P))))))

    j-eq : jg ≡ jh
    j-eq = trans (sym (readJ-cinv jg)) (trans (cong readJ eqα) (readJ-cinv jh))

    m-eq : mg ≡ mh
    m-eq = cinv-injective jg mg mh (trans P (cong (λ j → cinv j mh) (sym j-eq)))
