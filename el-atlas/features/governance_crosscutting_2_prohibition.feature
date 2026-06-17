# file: governance_crosscutting_2_prohibition.feature
# obligation source: §3 (Law 3.1, Lemma 3.2, Def 3.3, Remark 3.5) + Remark 2.5c
Feature: The prohibition — no silent collapse to a ratio [governance, cross-cutting, depth=2]
  The pair is never quotiented to a ratio, odds, or normalized probability
  inside the logic. Probability is recoverable only as an explicit, named,
  external projection. Crossing charts is an adjunction, not a collapse.

  Background:
    Given the atlas obligation is satisfied (bootstrap_invariant_1_atlas)
    And a carrier state (E_plus, E_minus)

  Scenario: ratio-blindness — the forbidden quotient cannot tell conflict from ignorance (Lemma 3.2)
    Given two states (a, a) with a high and (c, c) with c low
    When the quotient q = E_plus/E_minus is taken as the value
    Then q = 1 for both states
    And active disagreement is made indistinguishable from lack of knowledge
    And the mass coordinate has been destroyed

  Scenario: balance is a non-operation (Def 3.3)
    Given the phrase "balance of evidence"
    When a balance operator is sought in the logic
    Then none exists
    And balance is the state of declining to compute the quotient, both pins held live

  Scenario Outline: projection plurality — every scalar read is named and external (Remark 3.5)
    Given the carrier state
    When the projection "<projection>" is applied
    Then it is a named, external read
    And it discards everything orthogonal to its axis
    And it is never treated as "the" value of the pair

    Examples:
      | projection                  |
      | mass (total commitment)     |
      | bias (differential tilt)    |
      | unsigned decisiveness       |
      | single-conductor collapse   |
      | ratio / null-test           |

  # Remark 2.5c — the keystone distinction, as a discriminator scenario
  Scenario: collapse versus chart-image — same syntax, opposite role
    Given the expression E_plus/E_minus
    When it is used as the value the pair is reduced to
    Then it is a collapse (lossy, one-way, mass discarded) and is forbidden
    When instead it is the multiplicative-chart image of bias with mass present as the product axis
    Then it is a chart-image (invertible, mass preserved) and is permitted
    And the discriminator is whether the orthogonal axis survives, not the formula

  Scenario: probability is recovered only externally
    Given a demand for a probability or odds
    When it is produced
    Then it is produced by an explicit named collapse outside the logic
    And it is never the semantics of the carrier
