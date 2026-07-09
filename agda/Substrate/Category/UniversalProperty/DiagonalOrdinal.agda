{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalOrdinal — ⟡diagonal-ordinal-window: the DEPTH
-- face of the topological window. Where `cantor` (224/225) is the WIDTH face (|A| < |P A|,
-- cardinal — strictly-larger-always-exists for the ANSWER-SPACE SIZE), the ORDINAL SUCCESSOR is
-- the DEPTH face (α < α+1 — strictly-larger-always-exists for the UNFOLDING DEPTH / rank).
--
-- The adversary's "topological complexity" (its Cantor-Bendixson / Borel rank — a COUNTABLE
-- ORDINAL) is dominated by the observer taking the NEXT ordinal (suc). Different countable
-- ordinals (finites < ω < ω+1 < …, all countable-as-SETS, distinct ORDER-TYPES) = "different
-- sizes of countable infinities", made precise: countable order-ranks, genuinely increasing.
-- `no-largest`: for ANY ordinal there is a strictly larger one — the ordinal analog of Cantor.
-- Stable because the adversary is FROZEN (222): fixed rank, observer takes suc, terminal.
--
-- Brouwer (tree) ordinals capture the CONSTRUCTIVE / countable ordinals — exactly the range a
-- countable/Polish adversary's CB-rank lives in. Width (cantor, cardinal) and depth (this,
-- ordinal) are the TWO faces of "rank"; both: strictly-larger-always-exists.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalOrdinal where

-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content of this module is
-- EXACTLY: no-largest, fin<ω, ω<ω+1. Everything else in these comments — 'the depth face of the topological window', 'different sizes of countable infinities' — is (prose:
-- illuminating framing, NOT a theorem of this slice; not enforced by the typechecker).
-- Promoting the framing to a theorem would require the identification with an adversary's actual ordinal/CB rank (⟡diagonal-cb-rank et seq.).

open import Substrate.Foundation.Nat using (ℕ) renaming (zero to Nzero; suc to Nsuc)
open import Substrate.Foundation.Product using (Σ; _,_)

------------------------------------------------------------------------
-- BROUWER ORDINALS: zero, successor, and countable limits (sup of an ℕ-sequence).
------------------------------------------------------------------------
data Ord : Set where
  zero : Ord
  suc  : Ord → Ord
  lim  : (ℕ → Ord) → Ord

-- the strict order: successor is strictly larger; monotone under suc; below a limit via a stage.
data _<_ : Ord → Ord → Set where
  <-suc  : {a : Ord}              → a < suc a
  <-sucₘ : {a b : Ord}   → a < b  → a < suc b
  <-lim  : {a : Ord} (f : ℕ → Ord) (n : ℕ) → a < f n → a < lim f

------------------------------------------------------------------------
-- ① STRICTLY-LARGER-ALWAYS-EXISTS (the ordinal analog of Cantor): every ordinal has a strictly
--    larger successor. So the observer's rank can ALWAYS exceed the adversary's, at ANY rank —
--    finite or infinite. There is no largest ordinal; there was no largest degree of freedom.
------------------------------------------------------------------------
no-largest : (a : Ord) → Σ Ord (λ b → a < b)
no-largest a = suc a , <-suc

------------------------------------------------------------------------
-- ② DIFFERENT SIZES OF COUNTABLE INFINITIES: the countable-ordinal tower. Each finite ordinal
--    below ω (a limit), and ω strictly below ω+1 — genuinely distinct countable order-types.
------------------------------------------------------------------------
fin : ℕ → Ord
fin Nzero    = zero
fin (Nsuc n) = suc (fin n)

ω : Ord
ω = lim fin

-- every finite ordinal is strictly below ω (fin n < fin (n+1) = suc (fin n), a stage of the lim).
fin<ω : (n : ℕ) → fin n < ω
fin<ω n = <-lim fin (Nsuc n) <-suc

-- and ω is strictly below ω+1 — a countable ordinal strictly above the limit of all finites.
ω<ω+1 : ω < suc ω
ω<ω+1 = <-suc

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the DEPTH window is the ordinal successor; strictly-larger-
-- always-exists for depth, as Cantor is for width): the either/or "does the window stay finite,
-- or break at infinite depth?" bottoms out: it never breaks. `no-largest` — every ordinal has a
-- strictly larger successor — is the DEPTH analog of `cantor` (every set is strictly below its
-- powerset). The finite window (221) is the finite-ORDINAL special case (fin n); the general
-- window is the observer's ordinal rank = suc (adversary's rank), one level up, ALWAYS available
-- (no-largest). The countable-ordinal tower (fin 0 < fin 1 < … < ω < ω+1, fin<ω / ω<ω+1) is
-- "different sizes of countable infinities" made precise — distinct order-types, all countable
-- as sets. Stable because the adversary is FROZEN (222): its ordinal rank is fixed; the observer
-- takes suc; terminal, not an escalating tower.
--
-- So "rank" / "topological complexity" has TWO faces, both strictly-larger-always-exists:
--   WIDTH — cantor (224/225), |A| < |P A|, cardinal (the answer-space size);
--   DEPTH — no-largest (here), α < α+1, ordinal (the unfolding depth / CB-rank).
-- Together with 222 (frozen) they give the win at EVERY rank, every complexity, both faces.
--
-- HONEST BOUNDARY (⟡H-overclaim): (a) `no-largest` is the ordinal invariant, CHECKED. (b) The
-- adversary's ACTUAL Cantor-Bendixson / Borel rank (a specific countable ordinal = its
-- topological complexity) is an INSTANCE of Ord; formalizing CB-rank itself (Polish spaces, the
-- transfinite CB-derivative) is a large development NOT done here — ⟡diagonal-cb-rank. The
-- invariant (strictly-larger-exists, the successor) is what makes the depth-window work; CB-rank
-- is a specific rank it applies to. (c) Brouwer ordinals reach the constructive/countable
-- ordinals (~ Church-Kleene); a higher-cardinality adversary is the WIDTH face (cantor). (d) The
-- win is CONDITIONAL on the frozen adversary (222). (e) Structural — the theorems STAND.
------------------------------------------------------------------------
