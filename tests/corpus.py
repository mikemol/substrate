# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Fixture corpus for the shared Agda-text helpers — every case a MEASURED incident.

WHY THESE STRINGS AND NOT INVENTED ONES.  Each fixture below is either lifted verbatim
from the live tree (file:line recorded) or is the minimal reduction of a failure that
actually shipped.  A synthetic case proves the helper handles what its author imagined;
a corpus case proves it handles what the corpus contains.  The distinction is not
academic here — the span rule passed every synthetic test its authors wrote and still
gutted 33 files, because nobody had written down the shape that breaks it.

Naming: `<WHAT>_<INCIDENT>` so a failing test names the incident in its own output.
"""

# ── THE 33-FILE INCIDENT ──────────────────────────────────────────────────────
# An import directly above a PARAMETERIZED module header.  The naive "an indented
# line continues the statement" rule consumed the header AND its whole telescope, so a
# caller that deletes the span deletes the module.  Coxeter/Core.agda went 76 lines to
# 3.  Caught only by the build — twice, from two different copies of the rule.
PARAM_HEADER_AFTER_IMPORT = [
    "open import Substrate.Foundation.Eq using (_≡_)",
    "",
    "module Substrate.Groups.Coxeter.Core",
    "  (Word : Set)",
    "  (_++_ : Word → Word → Word)",
    "  where",
    "",
    "body : Set",
]

# Verbatim from agda/Substrate/Discipline.agda:82-85 — a header whose telescope spans
# FOUR lines with no same-line `where`.  Every `^module\s+(\S+)\s+where` copy (6 of
# them) misses this entirely and reports "no module".
PARAM_HEADER_REAL = (
    "module Rule1 {Invariant GaugeCarrier : Set}\n"
    "             {GaugeRel : GaugeCarrier → GaugeCarrier → Set}\n"
    "             {Gauge : SetoidGroup GaugeCarrier GaugeRel}\n"
    "             {Fiber : Invariant → Set}\n"
    "             where\n"
)

# ── F17 ───────────────────────────────────────────────────────────────────────
# Inside `module M where`, an import is followed by indented DEFINITIONS that open no
# keyword, so a keyword-only guard swallowed `x : Nat` into the import's span.  The
# measured loss was three valid imports deleted from Discipline.agda.
INDENTED_DEFS_AFTER_IMPORT = [
    "module M where",
    "  open import A",
    "  x : Nat",
    "  y : Nat",
]

# ── THE ONE REAL CORPUS DIVERGENCE ────────────────────────────────────────────
# agda/Substrate/TokiPona/LinearAlgebra.agda:49-51.  A wrapped `using (…)` list whose
# continuation line legitimately BEGINS with the keyword `module` (Agda's
# `using (…; module W)` re-exports a submodule).  A depth-blind keyword guard truncates
# the list and silently drops the re-export.  Over the whole corpus this is the ONLY
# statement where the depth-aware and depth-blind rules disagree — which is exactly why
# it must be pinned: a single witness is one edit away from being lost.
WRAPPED_USING_WITH_MODULE = [
    "open import Substrate.TokiPona.NimiSpace",
    "  using (nimi-as-vector; nimi-from-index; from-index∘index;",
    "         module WithTarget)",
    "",
    "next : Set",
]

# ── NESTED BLOCK COMMENTS ─────────────────────────────────────────────────────
# Agda block comments NEST.  The non-greedy `\{-.*?-\}` stripper stops at the FIRST
# `-}`, leaving `z -}` as live text.  19 importers inherited that stripper, THREE of
# them pre-commit gates, so commented-out code was censused as real declarations.
# No live tree instance exists today (verified) — this is the synthetic guard for a
# class that already shipped through the weaker copy.
NESTED_BLOCK_COMMENT = "a {- x {- y -} z -} b"

# `-->` is a NAME in Agda's lexer, not a comment opener.  The `--[^\n]*` copies eat it.
ARROW_NOT_A_COMMENT = "f --> g"

# A commented-out module header must not be mistaken for the real one.  None of the 14
# header-regex copies mask comments first.
COMMENTED_HEADER = "-- module Ghost where\nmodule Real where\n"

# ── `open … public` ───────────────────────────────────────────────────────────
# Verbatim shape from agda/Substrate/S5/S5Fixpoint.agda:19 — the harder form, where
# `public` follows a `using (…)` clause rather than the module name.
PUBLIC_AFTER_USING = "open import Substrate.Foundation.Empty    using (⊥) public"

# `\bpublic\b` (16 of 18 copies) matches BOTH of these.  Neither is a re-export.
PUBLIC_IN_COMMENT = "open import A  -- make this public later"
PUBLIC_AS_RENAME_TARGET = "open import A renaming (x to public')"
PUBLIC_SUBSTRING = "open import A  -- see the republication note"  # `"public" in l`

PLAIN_OPEN = "open import Substrate.Foundation.Eq using (_≡_)"
NOT_AN_OPEN = "x : Set"

# ── unicode ───────────────────────────────────────────────────────────────────
# The `[A-Za-z0-9_.\-]+` character class (8 copies) rejects most of this corpus.
#
# ⚑ THE DOUBLE-STRUCK CAPITAL N IS SPELLED AS A `\N{...}` ESCAPE, AND THAT IS THE
# FIXTURE'S OWN SUBJECT RATHER THAN A LINTING CONCESSION.  `RUF001` refuses the literal
# because that codepoint is visually confusable with a plain ASCII `N` — which is exactly
# the hazard these two fixtures exist to pin: an ASCII-only class TRUNCATES such a name,
# and a truncated name is worse than a failure because it is plausible.  Naming the
# codepoint makes the fixture unambiguous to a reader who cannot tell them apart on
# screen, which is the reader the rule protects.
#
# ⚑ THE RING OPERATOR BELOW IS NOT FLAGGED and stays literal.  The rule fires on
# CONFUSABILITY, not on non-ASCII, so escaping it too would read as a blanket habit and
# obscure why the first one is escaped.
UNICODE_HEADER = "module Substrate.\N{DOUBLE-STRUCK CAPITAL N}-elim where\n"
UNICODE_OPERATOR_HEADER = "module Substrate.Algebra.∘-assoc where\n"

# ── paths ─────────────────────────────────────────────────────────────────────
# The suffix strip is spelled three ways across ~50 sites: `[:-5]` (22), a magic
# constant that silently truncates if the extension changes; `[:-len(".agda")]` (23);
# `with_suffix` (5).  These pin the ONE answer all three must agree on.
PATH_UNDER_ROOT = "agda/Substrate/Foundation/Eq.agda"
MODULE_UNDER_ROOT = "Substrate.Foundation.Eq"
PATH_ABSOLUTE = "/x/y/Substrate/Foundation/Eq.agda"
ROOT_ABSOLUTE = "/x/y"
# `scope_fix.py` runs with cwd=agda/, so its root is the EMPTY STRING — 20 of its
# conversions depend on that contract holding.
PATH_ROOTLESS = "Substrate/Foundation/Eq.agda"
