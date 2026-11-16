# file: agda_text_invariant_0_helpers.feature
# obligation source: measured incidents — the 33-file gutting (Coxeter/Core.agda 76→3);
#   F17 (Discipline.agda, three valid imports deleted); the sole corpus divergence at
#   TokiPona/LinearAlgebra.agda:49-51; the wrong-representative lift (_agdatext.py:20-38,
#   19 importers, 3 of them pre-commit gates)
Feature: The shared Agda-text helpers [tooling, invariant, depth=0]
  One authority per lexical concept. Every scenario below is a failure that ALREADY
  SHIPPED through a divergent copy — not a hypothetical. The helpers exist because
  three of the largest duplication classes had no adoption target at all, so "route
  through the shared module" was un-actionable until they were written.

  Each Scenario is implemented by a test whose docstring names it verbatim;
  scripts/check_feature_coverage.py fails on any Scenario with no implementing test.

  Background:
    Given the canonical helpers live in scratch/agda_lex.py
    And a copy that re-derives one of them is admissible only when declared ⚑rederive
    And scripts/ and scratch/ may import them, but jea/ and el-atlas/ may not (Λ8)

  # ── paths ───────────────────────────────────────────────────────────────────
  Scenario: a path under the agda root becomes its dotted module name
    Given the path agda/Substrate/Foundation/Eq.agda and the root agda
    When module_path is applied
    Then it yields Substrate.Foundation.Eq

  Scenario: the root is an argument, never a global or a cwd
    Given 69 inline conversions disagreed about what the root was
    And a per-call default would relocate that disagreement into 69 call sites
    And deriving it from __file__ breaks once the library is installed elsewhere
    Then the root is passed explicitly and the helper is pure

  Scenario: the root is normalized so a caller's spelling is irrelevant
    Given the roots agda, ./agda and agda/
    Then all three yield the same module name

  Scenario: a tool whose contract is cwd=agda/ passes the empty root
    Given scope_fix.py is documented "Run from agda/."
    Then module_path with the empty root preserves that contract

  Scenario: the .agda suffix is stripped by name, not by a magic constant
    Given 22 sites spelled the strip as [:-5]
    Then a name shorter or longer than the suffix is not silently truncated

  Scenario: a path that is not .agda keeps its full final segment
    Given the path agda/A/Bcdef
    Then module_path yields A.Bcdef
    But the [:-5] spelling yields A. — five characters of a real name eaten

  Scenario: module_file and module_path round-trip
  Scenario: module_file appends the .agda suffix under the given root

  Scenario: the agda root is discovered by walking up from a start path
    Given the one impure helper is isolated so a deployment can replace just it

  Scenario: with no agda tree above it, the root search returns None
    Given 8 sites answered a wrong cwd with a wrong ANSWER rather than an error
    Then returning None is preferred to guessing

  # ── module names ────────────────────────────────────────────────────────────
  Scenario: a parameterized header has no same-line `where`
    Given a header spanning `module M`, `(Word : Set)`, `where`
    When module_name_of is applied
    Then it yields M

  Scenario: the where-anchored copies miss a parameterized header entirely
    Given 6 copies spell it ^module\s+(\S+)\s+where
    Then they report no module at all for such a header

  Scenario: a real four-line telescope resolves (Discipline.agda:82)

  Scenario: a unicode module name resolves
  Scenario: an operator-bearing module name resolves
  Scenario: the ASCII character-class copies reject a unicode name
    Given 8 copies spell the name as [A-Za-z0-9_.\-]+
    Then they truncate or fail on ℕ-elim, which is most of this corpus

  Scenario: the old header regex silently drops 5% of the corpus
    Given the 2764-module corpus
    When the old ASCII-and-where-anchored regex is applied to each file
    Then it returns nothing for 151 of them — 149 parameterized headers and 2 unicode
    And it disagrees with the canonical on ZERO files it does find
    So the canonical is a strict improvement, never a regression

  # The shim exists because six tools held the header regex as a COMPILED PATTERN and
  # used it as `modre.search(text).group(1)`. Matching that interface converts each by
  # one line, instead of rewriting six call sites into six new shapes.
  Scenario: the header shim answers .search().group(1) like a compiled pattern
  Scenario: the header shim returns None when there is no header
  Scenario: the header shim resolves what the compiled pattern missed
  Scenario: a caller wanting a group the shim cannot supply fails loudly
    Given the shim implements neither .span() nor .groups()
    Then a caller relying on a byte offset breaks at conversion time
    Rather than silently receiving a wrong one

  Scenario: a commented-out module header is not the module
  Scenario: a header inside a block comment is not the module
    Given `--` at column 0 is already refused by a ^-anchored copy
    But a block comment puts `module` at column 0 on its own line
    Then only a comment-masking helper refuses it

  Scenario: source with no module header yields None

  # ── re-exports ──────────────────────────────────────────────────────────────
  Scenario: an open with a public tail is a re-export
  Scenario: public following a using clause is still a re-export
    Given the form at S5/S5Fixpoint.agda:19

  Scenario: the word public in a comment is not a re-export
    Given 16 of 18 copies spell it \bpublic\b
    Then each of them counts a comment as a live re-export
    And split_lemmas attaches comment blocks to every leaf BY DESIGN
    So the false positive there is structural, not luck

  Scenario: public as a renaming target is not a re-export
  Scenario: republication does not make an import a re-export
    Given narrow_leaf_imports.py:35 tests `"public" not in l`
  Scenario: an ordinary filtered import is not a re-export
  Scenario: a statement that is not an open is never a re-export

  # ── statement spans ─────────────────────────────────────────────────────────
  Scenario: an import above a parameterized header keeps its own span
    Given the 33-file incident
    Then the header and its telescope are outside the import's span

  Scenario: the naive indentation rule absorbs the header and telescope
    Then a caller that deletes the span deletes the module

  Scenario: an indented definition after an import is not a continuation
    Given F17: `x : Nat` inside `module M where` opens no keyword
  Scenario: a line opening a declaration ends the statement

  Scenario: a wrapped using-list containing a module re-export stays whole
    Given TokiPona/LinearAlgebra.agda:49-51 is the ONLY corpus statement where the
      depth-aware and depth-blind rules disagree
    Then a single witness must be pinned, being one edit from lost
  Scenario: inside an open paren, a keyword does not start a new statement

  Scenario: nested block comments are masked to their true extent
  Scenario: the non-greedy stripper leaves live text after the first close
    Given 19 importers inherited it, three of them pre-commit gates
  Scenario: --> is an Agda name, not a comment opener
  Scenario: masking preserves length and line structure
    Given callers index by line and some by column
