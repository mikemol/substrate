# file: testing_invariant_3_wheatstone.feature
# obligation source: §11.3, §11.4, OB-5 (witnessed via the adjunction)
Feature: The Wheatstone instrument [testing, invariant, depth=3]
  The bridge is the physical instrument of the (mass, bias) basis; balance is
  the pin-swap fixpoint read across the exp/log adjunction. A second readout
  recovers the mass the galvanometer alone cannot see.

  Background:
    Given the crossbar obligation is satisfied (ladder_local_2_crossbar)
    And the prohibition obligation is satisfied (governance_crosscutting_2_prohibition)
    And the two sense corners carry E_plus and E_minus

  Scenario: the galvanometer reads bias, the supply reads mass
    Given a bridge with sense corners E_plus, E_minus
    When the readings are taken
    Then the galvanometer reads the difference (bias)
    And the supply reads the sum (mass)

  Scenario: balance is the pin-swap fixpoint, across the adjunction (OB-5, witnessed)
    Given the balance condition
    When read in the additive chart
    Then it is bias b = 0 (the pin-swap fixpoint)
    When read in the multiplicative chart
    Then it is the ratio E_plus/E_minus = 1
    And the two are the same locus via exp(b) = ratio (chart-image, not collapse)

  Scenario: ratio-blindness at the null, and its two-readout repair (§11.4)
    Given a balanced bridge (galvanometer null)
    When only the galvanometer is read
    Then conflict (B) and absence (N) are indistinguishable
    When the differential pair's common-mode output is also read
    Then high common-mode at null indicates conflict
    And low common-mode indicates absence
    And both carrier coordinates are recovered

  # OB-5 residual — the strong quantitative claim is NOT yet witnessed
  @open @undetermined
  Scenario: galvanometer deflection equals the sign-cocycle value (R12)
    Given an unbalanced bridge with a directional deflection
    When the deflection magnitude is compared to the Cayley-Dickson sign-cocycle
    Then whether deflection equals the cocycle sign is UNDETERMINED in the current spec
    And this scenario is parked pending the strong-identification run
