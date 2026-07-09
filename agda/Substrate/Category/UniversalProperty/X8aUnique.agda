{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.X8aUnique — ⟡x8a-uniqueness: the ≡-uniqueness half
-- of the extruder BackedUP (X8aBacked, ADD 212), placed HONESTLY in TWO layers, mirroring
-- the existence/uniqueness split of MuBacked/NuBacked (ADD 170/169):
--
--   ① run-value WitnessUnique (Adm = ⊤, the μ-mirror): x8a's Witness `v ≡ run fuel start`
--      SELF-DETERMINES v (run is a function), so two witnesses coincide UNCONDITIONALLY —
--      trans w₁ (sym w₂), EXACTLY as mu-witness-unique (the ≡-Witness needs no bound). This
--      is the uniqueness AT the x8a-UP level: the solver's output is the unique witness.
--
--   ② the CONFLUENCE-uniqueness (the deeper half — WHY the run's answer is canonical): a
--      normal form is unique BY Church-Rosser. Over FUSep's Newman frame (CR = multi-step
--      peaks converge), if a term reduces to TWO normal forms they are ≡ — cr-nf-unique. So
--      the run's fixpoint is path-INDEPENDENT: any reduction reaching a normal form reaches
--      THE SAME one. This is the genuine content FUSep's SKI-CR (FUSepQCR.newman) supplies;
--      here it is the ABSTRACT principle over Newman's frame, instantiated at the real SKI
--      reduction by ⟡x8a-ski-instance (the ℕ demonstrator's `next` is deterministic, so its
--      confluence is trivial — the CONTENT lives at the branching SKI reduction).
--
-- The honest split (as NuBacked's, ADD 169): EXISTENCE unconditional (x8a-solves, 212);
-- ≡-uniqueness in two honest layers — run-value (⊤, here) + confluence (CR, FUSep). Neither
-- overclaims: layer ① is the function-graph uniqueness (genuine, unconditional); layer ② is
-- the path-independence that makes `solve` well-defined as "THE normal form", supplied by CR.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.X8aUnique where

open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Category.UniversalProperty using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; solve; solves)
open import Substrate.Category.UniversalProperty.Unique using (WitnessUnique; solver-unique)
open import Substrate.Category.UniversalProperty.X8aBacked using (x8a-backed)

------------------------------------------------------------------------
-- ① RUN-VALUE WITNESS-UNIQUENESS (Adm = ⊤, the μ-mirror). x8a's Witness v ≡ run fs
--    self-determines v; two witnesses coincide with NO bound — trans w₁ (sym w₂).
------------------------------------------------------------------------
x8a-witness-unique : WitnessUnique (arrow x8a-backed) (λ _ _ → ⊤)
x8a-witness-unique s t₁ t₂ _ _ w₁ w₂ = trans w₁ (sym w₂)

-- THE EXTRUDER SOLVER IS THE UNIQUE ADMISSIBLE SOLUTION (existence ⊕ WitnessUnique):
-- any t witnessing s IS the run's output. Adm = ⊤ (no bound), so it holds for EVERY t.
x8a-solver-unique :
  (s : Source (arrow x8a-backed))
  (t : Target (arrow x8a-backed)) →
  Witness (arrow x8a-backed) s t →
  t ≡ solve x8a-backed s
x8a-solver-unique s t wit-t =
  solver-unique x8a-backed (λ _ _ → ⊤) x8a-witness-unique s tt t tt wit-t

------------------------------------------------------------------------
-- ② THE CONFLUENCE-UNIQUENESS: a normal form is unique BY Church-Rosser. Abstract over any
--    reduction with a multi-step closure and a convergence notion (FUSep's Newman frame):
--    if a ⇒* b, a ⇒* c, and b, c are NORMAL (no ⇒-successor), then b ≡ c.
--    "Normal" is encoded as: every multi-step FROM the term returns it (b ⇒* d ⟹ d ≡ b) —
--    the reflexive-only closure, which is exactly irreducibility for the halted state.
------------------------------------------------------------------------
module CRUnique
  {Tm : Set}
  (_⇒*_ : Tm → Tm → Set)
  (Converge : Tm → Tm → Set)
  (conv-witnesses : (b c : Tm) → Converge b c → Σ Tm (λ d → (b ⇒* d) × (c ⇒* d)))
  (CR : {a b c : Tm} → a ⇒* b → a ⇒* c → Converge b c)
  where

  -- a term is NORMAL when every reduction from it is trivial (returns it): b ⇒* d ⟹ d ≡ b.
  Normal : Tm → Set
  Normal b = (d : Tm) → b ⇒* d → d ≡ b

  -- CR ⟹ uniqueness of normal forms: two normal forms of one term coincide.
  cr-nf-unique :
    {a b c : Tm} → a ⇒* b → a ⇒* c → Normal b → Normal c → b ≡ c
  cr-nf-unique {a} {b} {c} a⇒*b a⇒*c nb nc with conv-witnesses b c (CR a⇒*b a⇒*c)
  ... | d , (b⇒*d , c⇒*d) = trans (sym (nb d b⇒*d)) (nc d c⇒*d)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the extruder's ≡-uniqueness, honestly two-layered): the
-- extruder's uniqueness mirrors NuBacked's existence/uniqueness split (169). EXISTENCE is
-- unconditional (x8a-solves, 212). The ≡-uniqueness is in two honest layers: ① run-value
-- (x8a-witness-unique, Adm = ⊤) — the solver's output is the unique witness, the μ-mirror
-- (self-determining ≡-Witness, trans/sym); ② confluence (cr-nf-unique) — the normal form is
-- path-INDEPENDENT by Church-Rosser, so `solve` computes THE canonical normal form, not just
-- A value. Layer ② is the genuine content FUSep's SKI-CR (FUSepQCR.newman : WCR + SN ⟹ CR)
-- supplies; here it is the abstract CR ⟹ unique-NF principle, instantiated at the branching
-- SKI reduction by ⟡x8a-ski-instance (the ℕ demonstrator's deterministic `next` makes its
-- own confluence trivial — the CONTENT lives at SKI's multi-redex reduction). So the either/or
-- "is the run's answer unique?" DISSOLVES into two invariants: the function-graph uniqueness
-- (⊤, unconditional) AND the confluence uniqueness (CR, the path-independence). The extruder
-- joins μ/ν not just in EXISTENCE (212, the third solver) but in the HONEST uniqueness frame.
------------------------------------------------------------------------
