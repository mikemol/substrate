#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""scope_errors.py — what AGDA'S OUTPUT says: every compiler message this tool parses.

⚑⚑ SPLIT OUT OF `scope_fix.py` 2026-08-11 (⟡split-1200), AND THIS ONE IS THE CUT THAT MAKES
THE OTHERS POSSIBLE. `scope_fix` is a chain — the loop `fix()` consumes the handlers, the
handlers consume the writers — so the handlers move DOWN and the loop stays. But `NOT_IN_SCOPE`
is read by BOTH: `fix()` takes the first not-in-scope error, and `fix_wrapper_open` re-reads it
to resolve a wrapper by name. Leaving a shared constant in the CONSUMER while moving its other
reader to a SUPPLIER closes an import cycle — the exact hazard `_would_cycle` exists to catch
in the Agda tree, reproduced in our own tooling, and the same shape that made the first cut of
the `schema`/`schema_queue` split fail with `ImportError` against a half-built module.

So the patterns come out first, into a module that imports `re` and nothing else. Everything
else in the `scope_*` chain may read it, and it reads none of them.

⚑ THIS IS THE FOURTH "KIND OF TRUTH", AND IT WAS ALWAYS ONE. `scope_fix`'s own header names
three authorities — the interned CORES (`scope_store`), the current agda TEXT (`scope_source`),
and the ranking across them (`scope_resolve`). The pattern set is a fourth and distinct one:
not what the tree contains, but what the COMPILER SAID about it. The tool's whole method is
"take the error message as telling you what needs fixing", so the message grammar is the
instrument, and an instrument deserves a home rather than being scattered beside its first
caller. Two of these (`AMBIGUOUS`, `CYCLIC`) were added together as *"T6/T8: two error kinds
the tool had NO matcher for at all"* — a fact about the INSTRUMENT, recorded next to a handler.

⚑ `CYCLIC` HAS A DEFINITION AND NO READER, AND IT IS KEPT RATHER THAN DELETED. Measured with
`pycodemod --shape '\\bCYCLIC\\b' scratch/` (code only, comments excluded): one site, the
definition below. Its sibling `AMBIGUOUS` grew `fix_ambiguous`; the `[CyclicModuleDependency]`
handler was never written, so this is a matcher waiting for its repair, not dead weight —
`_would_cycle` in `scope_source` is the PREVENTIVE half of the same concern and does exist.
Recorded here because the fact is about this pattern, and a reader who finds it unused should
know it was measured rather than overlooked.
"""
import re

# ⚑ THE PRIMARY INSTRUMENT. `[NotInScope]` ENUMERATES the requirement and usually NAMES the
# owner ("did you mean 'Substrate.Algebra.F2.Vector.Vector'?"), which is what makes the
# rewiring mechanical rather than hand-derived — hand-deriving an owner map got it wrong twice.
# The `at <file>:<line>` may name a DEPENDENCY, not the file the run started from.
NOT_IN_SCOPE = re.compile(
    r"Not in scope:\s*\n\s*(?P<name>\S+)\s*\n\s*at (?P<file>[^\s:]+):(?P<line>\d+)"
    r"(?:[^\n]*\n(?:[^\S\n][^\n]*\n)*?[^\S\n]*\(did you mean (?P<sugg>[^\n]*?)\?\))?", re.S)

# ⚑ T6/T8: two error kinds the tool had NO matcher for at all — both hit the generic
# "non-scope error" give-up, in every one of the six runs.
AMBIGUOUS = re.compile(
    r"(?P<file>[^\s:]+\.agda):[\d.\-]+: error: \[AmbiguousName\]\s*\n"
    r"\s*Ambiguous name (?P<name>\S+?)\.", re.M)
CYCLIC = re.compile(
    r"(?P<file>[^\s:]+\.agda):[\d.\-]+: error: \[CyclicModuleDependency\]", re.M)


# ── ⟡paydown-barrel: the DOMINANT class the loop was blind to ────────────────────────────────
# A stripped BARREL (`Foundation/Nat/Properties.agda` = three wholesale `open import … public`)
# now exports NOTHING, so every consumer's `using (…)`/`renaming (…)` against it fails. Agda
# reports this as a WARNING (`-W[no]ModuleDoesntExport`) plus a downstream `[NotInScope]` — and
# `fix()` only ever parsed the latter, which is why these files never converged. The warning is
# the better instrument: it names the FILE, the BARREL, and the EXACT missing names.
#
# A renaming TARGET (`+ℕ-comm`) is not a qname anywhere, so no ranking can resolve it; the
# SOURCE (`+-comm`) is. Parse the statement, resolve each SOURCE name to its owning submodule
# (catalog.db, preferring the barrel's own subtree — a barrel re-exports its subtree), and split
# the one import into one line per owner, preserving using/renaming structure.
BARREL_W = re.compile(
    r"(?P<file>/[^\s:]+\.agda):(?P<line>\d+)\.[\d.\-]+: warning: -W\[no\]ModuleDoesntExport\s*\n"
    # ⚑ Agda WRAPS this message at ~72 columns ("doesn't export the\nfollowing:"), so the
    # whitespace between words must be \s+, not a literal space.
    r"The\s+module\s+(?P<mod>\S+)\s+doesn't\s+export\s+the\s+following:"
    # ⚑ T3 ⟡pd-barrel-delete-evidence: Agda LISTS the missing names on the following indented
    # lines. Capturing them is what lets the delete be justified by Agda's evidence instead of
    # by our own resolver's failure — the two are NOT the same test, and conflating them
    # destroyed a working 12-name import of `Fin.Literals` because pattern synonyms are
    # unresolvable (9 of those 12 names were live; only 3 were actually missing).
    r"(?P<names>(?:\n[^\S\n]+[^\n]*)*)", re.M)


# ── ⟡paydown-missing-ctor ────────────────────────────────────────────────────────────────────
# A CONSTRUCTOR that is not in scope never reports `[NotInScope]` when it appears in a PATTERN —
# Agda silently reads it as a fresh pattern VARIABLE, and the failure surfaces later and
# differently:
#   • `[ConstructorPatternInWrongDatatype]`  "e₁ is not a constructor of the datatype Fin"
#   • `[UnequalTerms]`                       "α != α₁ … all occurrences of pattern variable α"
#   • a pattern-synonym parse failure        "Problematic expression: (c-here _)"
# so `fix()`, which only parses `Not in scope:`, was blind to all three (the same shape as the
# barrel WARNING). The owner is recovered from the shape DB, which records constructors as
# `…Bijection.V₄.α` — i.e. a qname with the parent TYPE between module and leaf.
CTOR_ERRS = [
    # ⚑ THE PRECISE INSTRUMENT: Agda NAMES the silent miscompile — "the pattern variable e has
    # the same name as the constructor V₄.e" — and emits it as a WARNING on a compile that
    # SUCCEEDS. It is strictly better than inferring the class from a downstream type error.
    re.compile(r"(?P<file>/[^\s:]+\.agda):[\d.\-]+: warning: -W\[no\]PatternShadowsConstructor\s*\n"
               r"\s*The pattern variable (?P<name>\S+) has the same name as the constructor", re.M),
    re.compile(r"(?P<file>/[^\s:]+\.agda):[\d.\-]+: error: \[ConstructorPatternInWrongDatatype\]\s*\n"
               r"\s*(?P<name>\S+) is not a constructor", re.M),
    re.compile(r"(?P<file>/[^\s:]+\.agda):[\d.\-]+: error: \[UnequalTerms\].*?"
               r"all occurrences of pattern variable (?P<name>\S+)", re.S),
    re.compile(r"Problematic expression: \((?P<name>[^\s)]+)[^\n]*\)\s*\n.*?"
               r"when scope checking the declaration", re.S),
]


# ── ⟡paydown-alias-repoint ───────────────────────────────────────────────────────────────────
# `import <barrel> as V4` + `V4.e` in a PATTERN. Once the barrel's re-exports are stripped it
# exports nothing, so `V4.e` is no longer a constructor and Agda reports
#     [InvalidPattern] V4.e is not a valid pattern
# — no name to look up, and dropping the qualification (fix_qualified) would be wrong here
# because the alias is used across many sites. The right move is to REPOINT THE ALIAS at the
# module that actually defines what the alias is used for, recovered from the shape DB.
# ⚑ CONDITIONAL BY MEASUREMENT: 49 files alias a now-empty barrel, but only ~6 have all their
# alias-qualified names under ONE owner. An alias can only point at one module, so repoint only
# in that case and report the rest rather than pick a wrong owner silently.
ALIAS_ERR = re.compile(
    r"(?P<file>/[^\s:]+\.agda):[\d.\-]+: error: \[InvalidPattern\]\s*\n"
    r"\s*(?P<alias>[\w.-]+)\.(?P<name>\S+) is not a valid pattern", re.M)
