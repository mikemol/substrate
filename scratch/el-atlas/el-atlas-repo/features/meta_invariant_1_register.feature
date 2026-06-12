# file: meta_invariant_1_register.feature
# obligation source: §14 (Provenance), §15 (Obligation register)
Feature: The obligation register — the spec applies its own logic to itself [meta, invariant, depth=1]
  Each open item is held as an (evidence-for, evidence-against) pair; obligations
  are carried live, not resolved by fiat. Resolved, open, and retracted are
  tracked states, and an open obligation does not trivialize the rest (paraconsistency).

  Background:
    Given the carrier obligation is satisfied (bootstrap_local_0_carrier)
    And each obligation OB-n carries a For side and an Against side

  Scenario: an obligation is an evidence pair, held live
    Given an open obligation
    When its state is read
    Then it has explicit For (evidence-for) and Against (evidence-against)
    And it is not collapsed to a verdict
    And it carries a named discharge path

  Scenario Outline: the tracked states
    Given obligation "<ob>"
    When its current status is read
    Then it is "<status>"

    Examples:
      | ob    | status                                  |
      | OB-5  | resolved (witnessed via the adjunction) |
      | OB-7  | resolved (clean two-pairing)            |
      | OB-12 | resolved (product = overlay)            |
      | OB-1  | open by design (the range parameter)    |
      | OB-9  | open (phase; complexification retracted)|
      | OB-3  | partial (bias-holonomy witnessed)       |

  Scenario: paraconsistency — an open or contradictory obligation does not explode
    Given an obligation in conflict (both For and Against high)
    When the rest of the spec is evaluated
    Then the conflict is localized to that obligation
    And no arbitrary conclusion is derivable elsewhere
    And the both-high state is flagged, not collapsed

  Scenario: corrections are monotonic — retracted runs are retained as history
    Given a run later found to be ill-posed (e.g. the OB-9 complexification)
    When the obligation is corrected
    Then the wrong run is marked RETRACTED, not deleted
    And the provenance of the error is preserved

  # the permanent loop, by design
  @open
  Scenario: OB-1 is open by design, not by defect
    Given the range parameter R (the document's named H1 generator)
    When closure is sought
    Then R is a free parameter with a stated constraint contract
    And the spec is deliberately non-closed at this obligation
    And this is the design, not a defect
