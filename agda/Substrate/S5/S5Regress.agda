{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5Regress — ⟡N1b-S. Soundness of the regress verdict: a confirmed
-- recurring generator ⟹ genuine non-termination, so declining to return a
-- value is SOUND (no value exists at any fuel).
--
-- ⟡H0 finding: the substrate (constructive-total) has NO non-termination /
-- Zantema-loop theorem — this is genuinely new. Framed in S5Verdict's own
-- `Machine S next` so it composes with the checked kernel (ε, run, monotone).
--
-- The regress DETECTOR's evidence (online Sequitur, ADD 36): a generator C
-- recurs — the orbit stays inside a set closed under stepping that grows and
-- never reaches a normal form. The SOUNDNESS content: formalize that evidence
-- as a LOOP INVARIANT and prove it entails "run never returns value".
--
--   Loop : S → Set              -- the invariant the orbit stays inside
--   loop-steps  : ∀ s → Loop s → Σ S (λ s' → next s ≡ stepped s' × Loop s')
--                                -- inside Loop, next ALWAYS steps (never final)
--                                -- and the successor is still inside Loop.
--
-- Then: Loop s ⟹ ∀ n, run n s ≡ suspended (something) — never value.
-- This is the Zantema loop (t →⁺ C[t]) at the right granularity: the growing
-- self-embedding is exactly a Loop invariant that never hits `final`. The
-- size-strictly-increases part of Zantema is SUBSUMED — we don't need it; the
-- verdict is about "no value", and "never final" is precisely that.
------------------------------------------------------------------------

module Substrate.S5.S5Regress where

import Substrate.S5.S5Verdict as S5Verdict
open S5Verdict
  using (_≡_; refl; sym; trans; cong; final; stepped; Verdict; value; suspended)
  renaming (Progress to Progress⟦cbe99ef5⟧)
open import Substrate.Foundation.Product  using (Σ; _×_; _,_) renaming (proj₁ to π₁; proj₂ to π₂) public
open import Substrate.Foundation.Empty    using (⊥)
open import Substrate.Foundation.Negation using (¬_)

module Regress (S : Set) (next : S → Progress⟦cbe99ef5⟧ S) where
  open S5Verdict.Machine S next
  open S5Verdict using (ℕ; zero; suc)

  -- A LOOP INVARIANT: a predicate the orbit never leaves, inside which `next`
  -- always steps (never final) to another Loop state. This IS "recurring
  -- generator with no normal form" stated as a coinductive-flavoured invariant
  -- (but proved by ordinary fuel induction below — no coinduction needed for
  -- the "never value" conclusion at each finite fuel).
  Loop : (S → Set) → Set
  Loop P = (s : S) → P s → Σ S (λ s' → (next s ≡ stepped s') × P s')

  ----------------------------------------------------------------------
  -- THE SOUNDNESS THEOREM. Inside a Loop invariant, run never returns value:
  -- for every fuel n and every P-state s, run n s is `suspended _`.
  -- Proof: fuel induction. At zero, run 0 s = suspended s. At suc n, next s
  -- steps (loop-steps) to s' still in P, and run (suc n) s = run n s' by the
  -- kernel's `run (suc n) s = handle n (next s) = run n s'` — apply IH.
  ----------------------------------------------------------------------
  regress-sound :
    (P : S → Set) → Loop P →
    (n : ℕ) (s : S) → P s →
    Σ S (λ w → run n s ≡ suspended w)
  regress-sound P lp zero    s ps = s , refl
  regress-sound P lp (suc n) s ps with lp s ps
  ... | (s' , (step-eq , ps')) =
        let ih = regress-sound P lp n s' ps'
        in π₁ ih , trans (cong (handle n) step-eq) (π₂ ih)

  ----------------------------------------------------------------------
  -- COROLLARY (the soundness stated as "never a value"): under a Loop
  -- invariant, run n s is never `value v`. Constructor disjointness:
  -- suspended w ≡ value v is uninhabited.
  ----------------------------------------------------------------------
  no-value :
    (P : S → Set) → Loop P →
    (n : ℕ) (s : S) → P s → (v : S) → ¬ (run n s ≡ value v)
  no-value P lp n s ps v eq with regress-sound P lp n s ps
  ... | (w , susp-eq) = clash (trans (sym susp-eq) eq)
    where
      Code : Verdict S → Set
      Code (value _)     = ⊥
      Code (suspended _) = S      -- source inhabited by w; target is ⊥
      clash : suspended w ≡ value v → ⊥
      clash e = subst Code e w
        where
          subst : {A : Set} {x y : A} (C : A → Set) → x ≡ y → C x → C y
          subst C refl cx = cx
