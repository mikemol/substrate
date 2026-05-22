------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven
--
-- The full formalisation of the user-provided hybrid translation of
-- Edgar Allan Poe's "The Raven" — `lo nu pimeja-tenpo`.
--
-- Submodules:
--
--   Grammar        — DSL: KelenRelation (pa/ñi/se/la), Terminal
--                    (awen-taso / añelē / other-attr), L7-Body-Reference,
--                    Line, Stanza.
--
--   Poem           — 18 stanzas of (mostly) 6 lines each; the full
--                    Raven encoded as `raven : Vec Stanza 18` with
--                    per-line (relation, terminal, L7-reference) tags.
--                    Surface Kēlen / Toki Pona / Lojban text in
--                    module-level comments per stanza.
--
--   PhaseTransition — Genuinely history-aware `HistoryPhase`
--                     (open / locked-now / post-lock) with
--                     `prior-añelē?` prefix-scan; per-stanza phase
--                     facts (18 refl-witnesses); meta-theorems
--                     `open-on-pre-VIII`, `not-open-from-VIII`,
--                     `first-lockup-at-VIII`, plus the suggested
--                     `seen-monotone-raven` (monotonicity of
--                     historical añelē-status across the Raven).
--
--   Semantics      — Cotype-level interpretation. Each stanza becomes
--                    a Cotype → Cotype transition; `interpret-stanza`
--                    populates L₇ exactly when the stanza's terminal
--                    is añelē. The 19 snapshot cotypes c0..c18 plus
--                    the chain c0 ⊑ c1 ⊑ ... ⊑ c18 (`full-chain-c0-to-c18`)
--                    realise the architectural reading at the formal
--                    state-machine level: L₇ becomes populated at
--                    exactly the c7 → c8 transition and remains
--                    populated thereafter (monotonic preorder, W5
--                    deletion-prohibition enforced at the type level).
--
-- ★ Headline theorems:
--
--   (PhaseTransition) `first-lockup-at-VIII` — stanza VIII is the
--   minimal index at which the Raven's terminal is añelē, and no
--   earlier stanza has had añelē.
--
--   (Semantics) `L₇-population-summary` — for the 19 snapshot
--   cotypes c0..c18, exactly the prefix c0..c7 has L₇ unpopulated
--   (8 conjuncts ≡ false) and exactly the suffix c8..c18 has L₇
--   populated (11 conjuncts ≡ true).
--
--   (Semantics) `full-chain-c0-to-c18` — the entire poem is a
--   monotonic chain in the Persistence preorder.
--
--   (PhaseTransition) `seen-monotone-raven` — once añelē has been
--   seen at index i, it remains seen at every index j ≥ i.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven where

open import Substrate.ShadowArchitecture.Raven.Grammar         public
open import Substrate.ShadowArchitecture.Raven.Poem            public
open import Substrate.ShadowArchitecture.Raven.PhaseTransition public
open import Substrate.ShadowArchitecture.Raven.Semantics       public
