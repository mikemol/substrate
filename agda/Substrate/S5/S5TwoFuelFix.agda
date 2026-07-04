{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- S5TwoFuelFix — ⟡N1b-Port-Fuel. Ports S5TwoFuel's metering (the two fuels as
-- TWO FOLDS OF ONE KEPT TRACE) onto S5Fixpoint's DERIVED-section kernel
-- (next : S → S, value = fixpoint via fix?, ADD 41). The trace-keeping runner
-- steps via next and stops at a fixpoint (fix?); traversal-fuel and
-- calculation-fuel are two catamorphisms over the one kept trace:
--     traversal   = length            (every step)
--     calculation = length ∘ dedupe   (distinct states)
-- with calc ≤ trav (L3) for ANY eqb, and the traced state agreeing with
-- S5Fixpoint.run. Retires S5TwoFuel (sibling-framed) to residue.
------------------------------------------------------------------------

module Substrate.S5.S5TwoFuelFix where

open import Substrate.S5.S5Verdict using (_≡_; refl; sym; trans; cong; ℕ; zero; suc)
import Substrate.S5.S5Fixpoint as S5Fixpoint
open S5Fixpoint using (⊥; Dec; yes; no)
open import Substrate.Foundation.Bool    using (Bool; true; false)
open import Substrate.Foundation.Product using (_×_; _,_) renaming (proj₁ to fst; proj₂ to snd)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Nat     using (_+_; _≤_; z≤n; s≤s)

open import Substrate.Foundation.List.Length using (length)   -- ⟡dedup: was a local re-derivation

≤-up : {m n : ℕ} → m ≤ n → m ≤ suc n
≤-up z≤n     = z≤n
≤-up (s≤s p) = s≤s (≤-up p)

------------------------------------------------------------------------
-- dedupe over an arbitrary eqb (ported verbatim from S5TwoFuel — abstract A).
------------------------------------------------------------------------
module Dedupe {A : Set} (eqb : A → A → Bool) where
  member : A → List A → Bool
  member a []       = false
  member a (x ∷ xs) = memb (eqb a x)
    where memb : Bool → Bool
          memb true  = true
          memb false = member a xs
  go     : List A → List A → List A
  branch : List A → A → List A → Bool → List A
  go seen []       = []
  go seen (x ∷ xs) = branch seen x xs (member x seen)
  branch seen x xs true  = go seen xs
  branch seen x xs false = x ∷ go (x ∷ seen) xs
  dedupe : List A → List A
  dedupe = go []
  go-≤     : (seen xs : List A) → length (go seen xs) ≤ length xs
  branch-≤ : (seen : List A) (x : A) (xs : List A) (b : Bool)
           → length (branch seen x xs b) ≤ suc (length xs)
  go-≤ seen []       = z≤n
  go-≤ seen (x ∷ xs) = branch-≤ seen x xs (member x seen)
  branch-≤ seen x xs true  = ≤-up (go-≤ seen xs)
  branch-≤ seen x xs false = s≤s (go-≤ (x ∷ seen) xs)
  dedupe-≤ : (xs : List A) → length (dedupe xs) ≤ length xs
  dedupe-≤ = go-≤ []

------------------------------------------------------------------------
-- the trace-keeping runner over S5Fixpoint's kernel: next : S → S, stop at a
-- fixpoint (fix?). runT returns (final state , kept trace of stepped states).
------------------------------------------------------------------------
module TwoFuel
  (S : Set) (next : S → S) (fix? : (s : S) → Dec (next s ≡ s))
  (eqb : S → S → Bool)
  where
  open S5Fixpoint.Machine S next fix? using (run)
  open Dedupe {S} eqb using (dedupe; dedupe-≤)

  ----------------------------------------------------------------------
  -- Stop: the runner CARRIES why it stopped — a fixpoint reached (with the
  -- PROOF next s ≡ s, i.e. "the state equals its own next", the operator's
  -- "current and prior are the same") or fuel-exhausted. value⊂suspended
  -- carrier (correction #14) at the metering tier: DERIVED at stop-time by
  -- the runner's own fix? check, then CARRIED — NOT a tag stored on the
  -- state that could lie (#15 respected). resumeT matches the Stop
  -- CONSTRUCTOR, so it never RE-PROBES fix? — which dissolves the
  -- with-abstraction stacking that blocked ADD 63.
  ----------------------------------------------------------------------
  data Stop : Set where
    reached : (s : S) → next s ≡ s → Stop      -- fixpoint (value), proof carried
    ranout  : (s : S) → Stop                   -- fuel-exhausted (still suspended)

  stopState : Stop → S
  stopState (reached s _) = s
  stopState (ranout  s)   = s

  consT : S → Stop × List S → Stop × List S
  consT x (v , t) = (v , x ∷ t)

  runT : ℕ → S → Stop × List S
  runT zero    s = (ranout s , [])              -- out of fuel at s
  runT (suc n) s with fix? s
  ... | yes p = (reached s p , [])              -- fixpoint: carry the proof
  ... | no  _ = consT (next s) (runT n (next s))

  -- the two fuels as folds of the ONE kept trace (trace = snd, unchanged)
  trace : ℕ → S → List S
  trace n s = snd (runT n s)
  trav : ℕ → S → ℕ
  trav n s = length (trace n s)
  calc : ℕ → S → ℕ
  calc n s = length (dedupe (trace n s))
  calc≤trav : (n : ℕ) (s : S) → calc n s ≤ trav n s
  calc≤trav n s = dedupe-≤ (trace n s)

  -- the carried state agrees with S5Fixpoint.run (the plain kernel).
  state-agrees : (n : ℕ) (s : S) → stopState (fst (runT n s)) ≡ run n s
  state-agrees zero    s = refl
  state-agrees (suc n) s with fix? s
  ... | yes _ = refl
  ... | no  _ = state-agrees n (next s)

  ----------------------------------------------------------------------
  -- ⟡N1b-Port-Fuel-compose: T-compose — traces CONCATENATE under window
  -- composition (the monoid morphism (fuel,+,0) → (traces,++,[])). resumeT
  -- reads the CARRIED Stop (no re-probe): reached ⟹ stop, keep trace;
  -- ranout ⟹ run m more and concatenate.
  ----------------------------------------------------------------------
  _++_ : List S → List S → List S
  []       ++ ys = ys
  (x ∷ xs) ++ ys = x ∷ (xs ++ ys)
  infixr 5 _++_

  resumeT : ℕ → Stop × List S → Stop × List S
  resumeT m (reached s p , t) = (reached s p , t)         -- value: stop, keep t
  resumeT m (ranout  s   , t) = attach t (runT m s)       -- exhausted: run m more
    where attach : List S → Stop × List S → Stop × List S
          attach t (v , t') = (v , t ++ t')

  -- resumption commutes with prefixing an emission — resumeT reads the Stop
  -- constructor, which consT leaves untouched, so it distributes.
  resumeT-consT : (m : ℕ) (x : S) (p : Stop × List S)
                → resumeT m (consT x p) ≡ consT x (resumeT m p)
  resumeT-consT m x (reached s p , t) = refl
  resumeT-consT m x (ranout  s   , t) = refl

  -- THE MONOID MORPHISM: induction on n, base ε ([] the unit of ++). The
  -- fixpoint case is refl (resumeT matches reached, no re-probe); the step
  -- threads through resumeT-consT + the IH.
  T-compose : (m n : ℕ) (s : S) → resumeT m (runT n s) ≡ runT (n + m) s
  T-compose m zero    s = eta (runT m s)
    where eta : (p : Stop × List S) → (fst p , [] ++ snd p) ≡ p
          eta (v , t) = refl
  T-compose m (suc n) s with fix? s
  ... | yes _ = refl
  ... | no  _ = trans (resumeT-consT m (next s) (runT n (next s)))
                      (cong (consT (next s)) (T-compose m n (next s)))
