# file: derived_view_invariant_0_agreement.feature
# obligation source: measured — 8 import edges missing from the committed agda/Flat.mk
#   (PriorAñelé, IsAñeléTerminal); 149 modules invisible to every analysis while the
#   gates saw all 2764; 142 type names invisible to five gates
Feature: Two routes to one fact must agree [tooling, invariant, depth=0]
  A DIFFERENT class from duplicated implementations, and more dangerous. Two layers
  compute the same quantity by different routes; neither is a copy of the other; both
  are individually correct; nothing reconciles them. Three audits hunted duplicated
  CODE and found plenty — none found this, because two routes to one fact share no
  code. The SPPF wedge and jea_pysim --clusters are blind to it BY CONSTRUCTION, so an
  empty similarity result is not evidence of agreement.

  The only instrument is: run both routes and diff the sets.

  Background:
    Given a gate reports a BIT and a report reports a NUMBER
    And nothing in the architecture ever holds both derivations at once
    So the human-facing layer is the one that can be quietly wrong

  Scenario: the build DAG's import edges equal the lexer's import edges
    Given gen_build_makefiles parsed imports with an ASCII-only character class
    When a module name contained a non-ASCII letter
    Then the import contributed NO edge at all
    And 8 edges were missing from the committed agda/Flat.mk
    And make could not mark those modules stale
    And --check certified it, because the gate re-used the same broken regex
    And the docstring called source-parsing "the SOUND super-set" — a prose pointer,
      not a checkable term

  # ── the Audit-IV class: the fix applied to the abstraction, not to the member that
  # opted out of it — invisible BECAUSE the surrounding convention is well-articulated.
  Scenario: every baseline-writing gate routes through the write guard
    Given set_ratchet grew an opt-in write guard after the defect was measured TWICE
    And six gates routed through it and became inert
    But set1_ratchet_cores hand-rolled its own compare and never received it
    Then a plain --quiet run of that one gate banked debt permanently
    And the standing instruction "do not run the ratchet gates" became
      TRUE OF ONE GATE AND FALSE OF SIX, with no way to tell which
    So it trained avoidance of a whole class for a reason that no longer applied

  Scenario: the write guard defaults to read-only
    Given a census READ must never bank debt
    Then may_write() is False unless SUBSTRATE_RATCHET_WRITE=1
    And an explicit argument beats the environment in both directions

  Scenario: no tool captures an import name with an ASCII-only class
    Given a class like [A-Za-z0-9_.'-]+ stops at the first non-ASCII letter
    Then the capture returns a TRUNCATED name, which is worse than failing
    Because a truncated name is plausible
    And omitting non-ASCII misses 2 modules, omitting `-` as well misses 160
    And the same defect in the build generator dropped 8 edges from Flat.mk

  Scenario: the corrected import class captures every module the lexer sees
    Given Python's \w is Unicode-aware
    Then [\w.'-]+ is both correct and shorter than every broken form it replaces

  Scenario: the enumerator excludes _build by default
    Given 41 of 59 enumeration sites had no _build filter
    And agda/_build/ holds 2762 .agdai and zero .agda
    Then the agreement at 2764 is LUCK, not construction
    And the first .agda under _build would inflate three pre-commit gates
      while the build generator's census stayed put

  Scenario: a subdirectory-scoped caller passes a narrower root
    Given scoping is a PARAMETER of the canonical derivation
    Then a narrower root makes a caller COMPLIANT, never an exception
    Which is what keeps a rederivation census honest rather than exemption-ridden

  Scenario: the enumerator returns a sorted list
    Given agda_files() was defined FOUR times with FOUR DIFFERENT BODIES
    And two sorted only WITHIN a directory, one sorted globally, one not at all
    Then a shared NAME is not a shared authority — it reads as reuse while disagreeing

  Scenario: every enumeration route returns the same module set
    Given 49 files enumerate the corpus by glob, os.walk and rglob
    And only some of them filter _build
    Then they agree at 2764 today by luck, not by construction
    And the first .agda under agda/_build/ would split them silently

  Scenario: a module's declared header equals its path-derived name
    Given the build keys targets on the path-derived name
    Then a file whose header disagreed with its location would break the build

  Scenario: the gates' declaration scan agrees with the definition index
    Given agda_defs was made indent-aware after a measured import-drop
    But five gates still scan data/record anchored at column 0
    Then 142 type names are invisible to them
    And the sumtype ratchet sees 25 duplicated names where the truth is 32
    And it cannot refuse a new copy of a duplicate it cannot see
    And carrier-locality judges 5 carriers globally-unique that are not
    # expectedFailure: recorded as a NUMBER in the suite, not a note that gets dropped.
    # Paying it down moves the sumtype baseline 25 -> 32 — a real debt discovery that
    # must be banked deliberately on the commit path, never as a refactor side effect.
