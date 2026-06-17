# file: bootstrap_invariant_1_atlas.feature
# obligation source: §2 (Defs 2.1-2.3, Lemma 2.4 + Caveat 2.4a, Lemma 2.5b, Lemma 2.6)
Feature: The atlas — one object in two charts, exp ⊣ log [bootstrap, invariant, depth=1]
  The additive chart A = [-inf,+inf] and the multiplicative semiring chart
  M = [0,inf] present the same object, related by the adjoint equivalence exp ⊣ log.
  Each chart carries its own involution on its own algebra.

  Background:
    Given the carrier obligation is satisfied (bootstrap_local_0_carrier)
    And chart A is the signed line [-inf,+inf] with neutral 0
    And chart M is the semiring [0,inf] (not a ring) with neutral 1

  Scenario: the additive-chart involution is sign negation
    Given a value u in chart A
    When negation not_A is applied
    Then not_A(u) = -u
    And the unique fixed point is 0

  Scenario: the multiplicative-chart involution is the semiring reciprocal
    Given a value y in chart M
    When negation not_M is applied
    Then not_M(y) = 1/y with 1/0 = inf and 1/inf = 0
    And the unique fixed point is 1
    And y is never negative or complex (M is a semiring, not a ring)

  Scenario: the two involutions are conjugate by exp/log (Lemma 2.4)
    Given a value y in chart M
    When not_M is expressed via the transition map
    Then not_M(y) = exp(not_A(log y)) = exp(-log y) = 1/y

  # Caveat 2.4a — the negative case is a category error, recorded as a guard
  Scenario: reciprocal must not be extended to a ring or field
    Given a request to evaluate 1/y for negative or complex y
    When the request is checked against the carrier of chart M
    Then it is rejected as a category error
    And the signed quantities are obtained instead by log into chart A, where the involution is -u

  Scenario: exp ⊣ log is an adjoint equivalence (Lemma 2.5b)
    Given the maps exp : A -> M and log : M -> A
    When the round-trips are composed
    Then log(exp(u)) = u and exp(log(y)) = y on the relevant domains

  Scenario: the adjunction acts losslessly on the (mass, bias) basis
    Given bias b = u_plus - u_minus and mass m = u_plus + u_minus in chart A
    When transported by exp to chart M
    Then bias maps to the ratio E_plus/E_minus = exp(b)
    And mass maps to the product E_plus*E_minus = exp(m)
    And both coordinates cross and log recovers both (nothing discarded)

  Scenario: the inverse-locked locus (Lemma 2.6)
    Given a pair on the locus (u, -u), equivalently (y, 1/y)
    When negate-a-pin is applied to one coordinate
    Then it coincides with the pin-swap on that pair
    And off the locus negate-a-pin and pin-swap are distinct involutions
