# file: groupoid_invariant_3_noether.feature
# obligation source: §11.8, OB-7 (RESOLVED — clean two-pairing)
Feature: The Noether pairings — symmetry and conserved charge [groupoid, invariant, depth=3]
  Two one-parameter symmetry subgroups each pair an involution with a
  continuous flow conserving the same axis: mass and bias are the two charges
  of (R+, x)^2 ~ (R, +)^2.

  Background:
    Given the crossbar obligation is satisfied (ladder_local_2_crossbar)
    And mass m = E_plus*E_minus (multiplicative chart) and bias = E_plus/E_minus

  Scenario: pin-swap pairs with the squeeze, conserving mass
    Given the pin-swap involution
    When its continuous partner is taken
    Then it is the squeeze (E_plus, E_minus) -> (e^t E_plus, e^-t E_minus)
    And the conserved Noether charge is mass = E_plus*E_minus
    And the chart picture is a hyperbolic rotation

  Scenario: negate-a-pin pairs with common translation, conserving bias
    Given the negate-a-pin involution
    When its continuous partner is taken
    Then it is the common translation (u_plus, u_minus) -> (u_plus+t, u_minus+t)
    And the conserved Noether charge is bias = E_plus/E_minus
    And the chart picture is a dilation

  Scenario: the two charges are orthogonal
    Given the squeeze and the dilation one-parameter subgroups
    When their conserved charges are compared
    Then the squeeze fixes mass and shifts bias
    And the dilation fixes bias and shifts mass
    And mass and bias are the two independent Noether charges

  # records the corrected status: the draft-9 "inconsistency" was a single-chart artifact
  Scenario: the discrete pairing extends to the continuous one (no inconsistency)
    Given the discrete pin-swap conserves mass and negates bias
    When matched to its continuous partner
    Then the squeeze (mass-conserving) is the correct partner, not common translation
    And the pairing is consistent across discrete and continuous symmetry
