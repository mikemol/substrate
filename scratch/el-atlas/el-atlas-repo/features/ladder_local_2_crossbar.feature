# file: ladder_local_2_crossbar.feature
# obligation source: §4 (Def 4.1, Law 4.2, Prop 4.3)
Feature: The crossbar — mass/bias change of basis [ladder, local, depth=2]
  In the additive chart the carrier is read in the (mass, bias) basis;
  the four Belnap values are derived corners of this geometry, not posited points.

  Background:
    Given the atlas obligation is satisfied (bootstrap_invariant_1_atlas)
    And mass m = E_plus + E_minus and bias b = E_plus - E_minus

  Scenario: the basis change is the crossbar
    Given a carrier state (E_plus, E_minus)
    When the (mass, bias) basis is applied
    Then m is total evidence (presence-of-evidence)
    And b is net judgement

  Scenario: bias is not a log-odds (Law 4.2)
    Given the bias coordinate b
    When it is read as a disposition over outcomes (a log-odds)
    Then the reading is rejected
    And the reason is that it discards the mass axis (the diagonal)

  Scenario Outline: the four values are ends of the two axes (Prop 4.3)
    Given a region at "<corner>"
    When located on the crossbar
    Then it sits at "<axis position>"

    Examples:
      | corner            | axis position            |
      | T (supported)     | bias-axis positive end   |
      | F (refuted)       | bias-axis negative end   |
      | B (conflict)      | mass-axis high end, b~0  |
      | N (absence)       | mass-axis low end, b~0   |

  Scenario: conflict and absence differ only in mass
    Given B (conflict) and N (absence)
    When compared
    Then both have bias b approximately 0
    And they differ only in mass m
    And a flat four-label scheme that equates them erases the mass distinction
