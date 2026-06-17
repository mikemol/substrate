# file: bootstrap_local_0_carrier.feature
# obligation source: §1 (Definitions 1.1, 1.2; Laws 1.3, 1.4)
Feature: The carrier — two independent evidence accumulators [bootstrap, local, depth=0]
  The carrier is a pair (E_plus, E_minus) of nonnegative additive accumulators,
  evidence-for and evidence-against, with increments and totals typed separately
  and the two pins never cross-read.

  Background:
    Given a carrier state is a pair (E_plus, E_minus) in [0, infinity] x [0, infinity]
    And an increment is a single nonnegative finding for one pin
    And a total is an accumulated quantity on one pin

  Scenario: increments and totals are distinct types
    Given an increment epsilon and a total E on the same pin
    When accumulation is applied with signature "increment x total -> total"
    Then the result is a total
    And epsilon may not be substituted where a total is required

  Scenario: independence — no pin reads the other (Law 1.3)
    Given a write of an increment to E_plus
    When the write completes
    Then E_minus is unchanged
    And the write read no value from E_minus

  Scenario: accumulation is additive and is a choice of sum (Law 1.4)
    Given two increments on E_plus
    When they are accumulated
    Then the total is their sum under the chosen carrier sum (ordinary + or a semiring oplus)
    And no underlying multiplication was linearized to obtain it

  Scenario Outline: the four interpretive regions are read off the pair, not posited
    Given a carrier state (<e_plus>, <e_minus>)
    When the region is identified
    Then it is "<region>"

    Examples:
      | e_plus | e_minus | region                    |
      | high   | low     | supported                 |
      | low    | high    | refuted                   |
      | high   | high    | active disagreement       |
      | low    | low     | lack of knowledge         |
