------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition
--
-- The genuinely history-aware phase classification of the Raven's
-- stanzas, fixing the local-vs-global confusion that an earlier
-- draft of `Raven.Grammar` exhibited (where a `post-lock-phase`
-- constructor was derived from the single stanza's terminal without
-- consulting prior stanzas).
--
-- A stanza's HISTORY phase depends on whether any earlier stanza had
-- `añelē` as its terminal:
--
--   open       — no prior stanza had añelē-terminal AND this
--                stanza's terminal is not añelē.
--   locked-now — this stanza's terminal IS añelē (lockup happens
--                here; may be the first occurrence or a subsequent
--                one).
--   post-lock  — at least one earlier stanza had añelē-terminal,
--                AND this stanza's terminal is some other attribute
--                (the Raven's "Nevermore" is being referenced rather
--                than freshly proclaimed).
--
-- Distinguished from a "two-state" {open, locked} reading by the
-- fact that lines IX, XI, XII echo añelē as the object of a la-
-- relation while their terminal attribute is something else — this
-- is exactly the post-lock state.
--
-- The phase-transition theorem: the first locked-now stanza is at
-- index 7 (= stanza VIII). The "open phase" is exactly stanzas I-VII
-- (indices 0..6); from stanza VIII onward, no stanza is in the open
-- phase.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition where

open import Substrate.Foundation.Bool using (Bool; true; false; _∨_)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Nat using (ℕ) renaming (_≤_ to _ℕ≤_; z≤n to z≤n; s≤s to s≤s)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.ShadowArchitecture.Raven.Grammar
open import Substrate.ShadowArchitecture.Raven.Poem using (raven)

------------------------------------------------------------------------
-- 1. The genuinely history-aware Phase.
------------------------------------------------------------------------

data HistoryPhase : Set where
  open-phase  : HistoryPhase  -- no añelē seen yet
  locked-now  : HistoryPhase  -- this stanza's terminal is añelē
  post-lock   : HistoryPhase  -- prior añelē; this stanza's terminal is other

------------------------------------------------------------------------
-- 2. Local helpers.
------------------------------------------------------------------------

is-añelē-terminal : Stanza → Bool
is-añelē-terminal s = check (stanza-terminal s)
  where
    check : Terminal → Bool
    check añelē      = true
    check awen-taso  = false
    check other-attr = false

------------------------------------------------------------------------
-- 3. Did any stanza STRICTLY BEFORE index i have añelē as terminal?
--
-- Defined by recursion on the index: at zero (the first stanza) no
-- prior; at (suc i) on (s ∷ rest), s is the head and we ask whether
-- s or any of `rest`'s first i stanzas had añelē-terminal.
------------------------------------------------------------------------

prior-añelē? : ∀ {n} → Vec Stanza n → Fin n → Bool
prior-añelē? (s ∷ _)  zero    = false
prior-añelē? (s ∷ ss) (suc i) = is-añelē-terminal s ∨ prior-añelē? ss i

------------------------------------------------------------------------
-- 4. The history-aware phase function.
------------------------------------------------------------------------

history-phase-at : ∀ {n} → Vec Stanza n → Fin n → HistoryPhase
history-phase-at v i with is-añelē-terminal (lookup v i) | prior-añelē? v i
... | true  | _     = locked-now
... | false | true  = post-lock
... | false | false = open-phase

------------------------------------------------------------------------
-- 5. Named indices into the 18-stanza Raven vector.
--
-- s1 = stanza I, ..., s18 = stanza XVIII.
------------------------------------------------------------------------

-- Each sₖ is built as `suc^(k-1) zero`. Cannot use `sₖ₊₁ = suc sₖ`
-- because `suc : Fin n → Fin (suc n)` would make `sₖ₊₁ : Fin 19` rather
-- than `Fin 18`.

private
  s1  : Fin 18 ; s1  = zero
  s2  : Fin 18 ; s2  = suc zero
  s3  : Fin 18 ; s3  = suc (suc zero)
  s4  : Fin 18 ; s4  = suc (suc (suc zero))
  s5  : Fin 18 ; s5  = suc (suc (suc (suc zero)))
  s6  : Fin 18 ; s6  = suc (suc (suc (suc (suc zero))))
  s7  : Fin 18 ; s7  = suc (suc (suc (suc (suc (suc zero)))))
  s8  : Fin 18 ; s8  = suc (suc (suc (suc (suc (suc (suc zero))))))
  s9  : Fin 18 ; s9  = suc (suc (suc (suc (suc (suc (suc (suc zero)))))))
  s10 : Fin 18 ; s10 = suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))
  s11 : Fin 18 ; s11 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))
  s12 : Fin 18 ; s12 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))
  s13 : Fin 18 ; s13 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))))
  s14 : Fin 18 ; s14 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))))
  s15 : Fin 18 ; s15 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))))))
  s16 : Fin 18 ; s16 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))))))
  s17 : Fin 18 ; s17 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))))))))
  s18 : Fin 18 ; s18 = suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))))))))

------------------------------------------------------------------------
-- 6. Per-stanza phase: 18 facts, each closes by `refl`.
--
-- Each `history-phase-at raven sₖ` reduces by computation because
-- `raven`, `sₖ`, `is-añelē-terminal`, and `prior-añelē?` are all
-- concrete.
--
-- Pattern:
--   I-VII   →  open-phase
--   VIII    →  locked-now  (first lockup)
--   IX      →  post-lock   (Raven sitting; añelē in body)
--   X       →  locked-now  (Raven says it again; añelē terminal)
--   XI, XII →  post-lock
--   XIII-XVIII → locked-now (terminal añelē repeated)
------------------------------------------------------------------------

stanza-I-phase    : history-phase-at raven s1  ≡ open-phase
stanza-I-phase    = refl
stanza-II-phase   : history-phase-at raven s2  ≡ open-phase
stanza-II-phase   = refl
stanza-III-phase  : history-phase-at raven s3  ≡ open-phase
stanza-III-phase  = refl
stanza-IV-phase   : history-phase-at raven s4  ≡ open-phase
stanza-IV-phase   = refl
stanza-V-phase    : history-phase-at raven s5  ≡ open-phase
stanza-V-phase    = refl
stanza-VI-phase   : history-phase-at raven s6  ≡ open-phase
stanza-VI-phase   = refl
stanza-VII-phase  : history-phase-at raven s7  ≡ open-phase
stanza-VII-phase  = refl

stanza-VIII-phase : history-phase-at raven s8  ≡ locked-now
stanza-VIII-phase = refl

stanza-IX-phase   : history-phase-at raven s9  ≡ post-lock
stanza-IX-phase   = refl

stanza-X-phase    : history-phase-at raven s10 ≡ locked-now
stanza-X-phase    = refl

stanza-XI-phase   : history-phase-at raven s11 ≡ post-lock
stanza-XI-phase   = refl
stanza-XII-phase  : history-phase-at raven s12 ≡ post-lock
stanza-XII-phase  = refl

stanza-XIII-phase  : history-phase-at raven s13 ≡ locked-now
stanza-XIII-phase  = refl
stanza-XIV-phase   : history-phase-at raven s14 ≡ locked-now
stanza-XIV-phase   = refl
stanza-XV-phase    : history-phase-at raven s15 ≡ locked-now
stanza-XV-phase    = refl
stanza-XVI-phase   : history-phase-at raven s16 ≡ locked-now
stanza-XVI-phase   = refl
stanza-XVII-phase  : history-phase-at raven s17 ≡ locked-now
stanza-XVII-phase  = refl
stanza-XVIII-phase : history-phase-at raven s18 ≡ locked-now
stanza-XVIII-phase = refl

------------------------------------------------------------------------
-- 7. Meta-theorems.
--
-- (a) Every stanza in I..VII is in the open phase.
-- (b) No stanza from VIII onward is in the open phase.
-- (c) Stanza VIII is the first lockup (locked-now AND no prior lockup).
------------------------------------------------------------------------

-- Helper liftings used by the meta-theorems.

private
  inject-7-to-18 : Fin 7 → Fin 18
  inject-7-to-18 zero                                       = s1
  inject-7-to-18 (suc zero)                                 = s2
  inject-7-to-18 (suc (suc zero))                           = s3
  inject-7-to-18 (suc (suc (suc zero)))                     = s4
  inject-7-to-18 (suc (suc (suc (suc zero))))               = s5
  inject-7-to-18 (suc (suc (suc (suc (suc zero)))))         = s6
  inject-7-to-18 (suc (suc (suc (suc (suc (suc zero))))))   = s7

  -- Indices 0..10 correspond to stanzas VIII..XVIII.
  lift-11-to-18 : Fin 11 → Fin 18
  lift-11-to-18 zero                                                                    = s8
  lift-11-to-18 (suc zero)                                                              = s9
  lift-11-to-18 (suc (suc zero))                                                        = s10
  lift-11-to-18 (suc (suc (suc zero)))                                                  = s11
  lift-11-to-18 (suc (suc (suc (suc zero))))                                            = s12
  lift-11-to-18 (suc (suc (suc (suc (suc zero)))))                                      = s13
  lift-11-to-18 (suc (suc (suc (suc (suc (suc zero))))))                                = s14
  lift-11-to-18 (suc (suc (suc (suc (suc (suc (suc zero)))))))                          = s15
  lift-11-to-18 (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))                    = s16
  lift-11-to-18 (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))              = s17
  lift-11-to-18 (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))        = s18

-- (a) Every stanza in I..VII is in the open phase.
open-on-pre-VIII : ∀ (i : Fin 7) → history-phase-at raven (inject-7-to-18 i) ≡ open-phase
open-on-pre-VIII zero                                       = stanza-I-phase
open-on-pre-VIII (suc zero)                                 = stanza-II-phase
open-on-pre-VIII (suc (suc zero))                           = stanza-III-phase
open-on-pre-VIII (suc (suc (suc zero)))                     = stanza-IV-phase
open-on-pre-VIII (suc (suc (suc (suc zero))))               = stanza-V-phase
open-on-pre-VIII (suc (suc (suc (suc (suc zero)))))         = stanza-VI-phase
open-on-pre-VIII (suc (suc (suc (suc (suc (suc zero))))))   = stanza-VII-phase

-- (b) No stanza from VIII onward is in the open phase.
not-open-from-VIII :
  ∀ (i : Fin 11) → ¬ (history-phase-at raven (lift-11-to-18 i) ≡ open-phase)
not-open-from-VIII zero                                                              ()
not-open-from-VIII (suc zero)                                                        ()
not-open-from-VIII (suc (suc zero))                                                  ()
not-open-from-VIII (suc (suc (suc zero)))                                            ()
not-open-from-VIII (suc (suc (suc (suc zero))))                                      ()
not-open-from-VIII (suc (suc (suc (suc (suc zero)))))                                ()
not-open-from-VIII (suc (suc (suc (suc (suc (suc zero))))))                          ()
not-open-from-VIII (suc (suc (suc (suc (suc (suc (suc zero)))))))                    ()
not-open-from-VIII (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))              ()
not-open-from-VIII (suc (suc (suc (suc (suc (suc (suc (suc (suc zero)))))))))        ()
not-open-from-VIII (suc (suc (suc (suc (suc (suc (suc (suc (suc (suc zero))))))))))  ()

-- (c) Stanza VIII is the first lockup: locked-now AND prior-añelē? is false.
first-lockup-at-VIII :
    history-phase-at raven s8 ≡ locked-now
  × prior-añelē? raven s8 ≡ false
first-lockup-at-VIII = stanza-VIII-phase , refl

------------------------------------------------------------------------
-- 8. Monotonicity of historical truth ("once the Raven has spoken,
-- it has always already spoken"). The general claim for any stanza
-- vector + specialized claim for `raven`.
--
-- Proof structure: induction on the Fin indices. The base case
-- (i = zero) is vacuous because `prior-añelē? v zero ≡ false`, so
-- the hypothesis `prior-añelē? v zero ≡ true` is uninhabited.
-- The inductive case uses `∨-monotone-right`: given (a ∨ b₁) ≡ true
-- and (b₁ → b₂), derive (a ∨ b₂) ≡ true. Here `a` is the head
-- stanza's añelē-status and (b₁, b₂) are the inductive hypotheses.
------------------------------------------------------------------------

private
  ∨-monotone-right :
    ∀ (a : Bool) {b₁ b₂} →
    (b₁ ≡ true → b₂ ≡ true) →
    (a ∨ b₁) ≡ true → (a ∨ b₂) ≡ true
  ∨-monotone-right true  _ _   = refl
  ∨-monotone-right false f hyp = f hyp

-- General monotonicity over arbitrary stanza vectors.
prior-añelē?-monotone :
  ∀ {n} (v : Vec Stanza n) (i j : Fin n) →
  (toℕ i ℕ≤ toℕ j) →
  prior-añelē? v i ≡ true →
  prior-añelē? v j ≡ true
prior-añelē?-monotone (s ∷ ss) zero    zero    _       ()
prior-añelē?-monotone (s ∷ ss) zero    (suc j) _       ()
prior-añelē?-monotone (s ∷ ss) (suc i) (suc j) (s≤s p) hyp =
  ∨-monotone-right (is-añelē-terminal s)
    (prior-añelē?-monotone ss i j p)
    hyp

-- Specialised to the Raven: once añelē has been seen at any earlier
-- index, it stays seen at every later index. Formal capture of
-- the architectural reading: the lockup is monotonic in time.
seen-monotone-raven :
  ∀ (i j : Fin 18) →
  (toℕ i ℕ≤ toℕ j) →
  prior-añelē? raven i ≡ true →
  prior-añelē? raven j ≡ true
seen-monotone-raven = prior-añelē?-monotone raven
