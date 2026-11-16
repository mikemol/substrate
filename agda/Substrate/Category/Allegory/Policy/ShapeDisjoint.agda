------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.ShapeDisjoint
--
-- Defines: shapes-transfer-separately
--
-- ⚑ `policy-confluent` DOES NOT CROSS THE BASIS SHIFT AS ONE THEOREM,
-- and the reason is measured rather than stylistic.  Confluence
-- (Confluence.agda) needs `deterministic f` for the shape function f.
-- There is no single f over both corpora, because there is no shared
-- identity space to land in.  Measured 2026-08-21 — THREE constructions,
-- not two:
--
--   python  `jea_pyalg.Intern`      hash-cons; identity is an INTEGER ID
--                                   into a table.  key = (kind, role, op,
--                                   lit, already-interned children).
--                                   Quotients NAMES to binding roles
--                                   (arg0/local1/global/attr), keeping the
--                                   original in `payload` as residue.
--   agda    `_agdatext.shape_decls` content hash; identity is an 8-hex
--                                   SHA1 over kind|sorted π-domains.
--                                   Quotients ORDER (sorts), keeps no
--                                   residue — the name is the dict key,
--                                   outside the hash.
--   agda    `jea_agdai.decode_core` NEITHER — a decoder returning an
--                                   elaborated core term.  Not a shape
--                                   function at all; it was easy to
--                                   mistake for one.
--
-- They diverge in identity KIND (table id vs digest — a digest is
-- portable across processes, an id is meaningful only inside one
-- `Intern`), in WHAT IS QUOTIENTED (names vs order), and in PERSISTENCE
-- (python internment is in-memory only; there is no python catalog.db —
-- `jea_pysim --persist` drops non-.agdai inputs).  The two SPPFs cannot
-- share an interned id: different alphabets, different identity kinds,
-- different lifetimes.
--
-- ⚑ WHERE THEY DO MEET IS THE ALGEBRA, NOT THE IDENTITY.  `PyDivStr.recon`
-- / `PyDivStr.wedge` implement the same `a = recon q b r` the agda side
-- uses, and `CrossMix.cross_term` gives shared/only_a/only_b over subterm
-- support.  One vocabulary, REIMPLEMENTED PER CORPUS.  So the wedge
-- transfers and the identity does not — which is exactly the lax square
-- being lax.
--
-- ⚑ THE CONSEQUENCE, stated so it is not re-derived: determinism must be
-- established SEPARATELY on each side, and confluence then holds
-- separately on each side.  There is no cross-corpus confluence to prove
-- or to assume.  A dedupe licensed by python shape-identity is NOT
-- licensed by agda shape-identity, and vice versa.
--
-- ⟡policy-basis-shift: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.ShapeDisjoint where

open import Substrate.Foundation.Product
open import Substrate.Category.Allegory.Maps
open import Substrate.Category.Allegory.Policy.Corpus


-- Determinism of the two shape functions is a PAIR of claims over two
-- unrelated Shape types, never one claim.  The type says it: `AShape` and
-- `PShape` are distinct parameters with no map between them, so no term
-- of this type can silently identify them.
shapes-transfer-separately :
    {ASite PSite AShape PShape : Set}
  → Corpus ASite → Corpus PSite
  → (a-shape : ASite → AShape → Set) (p-shape : PSite → PShape → Set)
  → deterministic a-shape → deterministic p-shape
  → deterministic a-shape × deterministic p-shape
shapes-transfer-separately _ _ _ _ da dp = da , dp
