# file: topos_crosscutting_4_overlay.feature
# obligation source: §12 (Principle 12.1, Candidate Law 12.2, Instances 12.3)
Feature: The overlay principle — gluing on a shared instance [topos, cross-cutting, depth=4]
  Construct two networks sharing a common structure S; overlay so S is a common
  instance (pushout along the span); then computation in one network manifests
  in the other, modulated by S.

  Background:
    Given the consumption-modes obligation is satisfied (ladder_crosscutting_3_consumption)
    And two networks N1 and N2 each containing a common structure S

  Scenario: the four steps of the principle (12.1)
    Given networks N1, N2 and shared structure S
    When the overlay is constructed
    Then each network's reasoning-space topology is characterized separately
    And S becomes a common instance (the pushout N1 +_S N2), not two isomorphic copies
    And computation in one network manifests in the other, characterized by S

  Scenario: identity, not isomorphism, creates the channel
    Given two isomorphic but distinct copies of S
    When they are left unidentified
    Then no computation transmits
    When they are identified as one instance
    Then the channel exists
    And the choice of identification is itself structure that modulates transmission

  # Candidate Law 12.2 — flagged, not asserted
  @candidate
  Scenario: the manifestation law (Mayer-Vietoris shape)
    Given a computation in N1
    When it is transmitted across the overlay
    Then what manifests is what restricts nontrivially to S
    And a deformation whose restriction to S vanishes is invisible to N2
    And H(S) bounds the transmissible classes (channel capacity)
    But this law is a CANDIDATE pending the discharge of OB-10

  Scenario Outline: witnessed instances (12.3)
    Given instance "<instance>" with shared structure "<S>"
    When read as an overlay
    Then "<manifestation>"

    Examples:
      | instance              | S            | manifestation                                         |
      | the atlas itself      | value space  | transport between charts (instance zero)              |
      | flat-binding          | V4           | flat iff De Morgan diagonal preserved (2 of 6 isos)   |
      | Wheatstone bridge     | the crossbar | deflection = S-mismatch; balance = agreement on S     |

  # naturality: the overlay is a pushout (morphism-typed)
  Scenario: naturality — the overlay square commutes
    Given the span N1 <- S -> N2
    When the pushout N1 +_S N2 is formed
    Then the square commutes
    And the cohomology theory of the reasoning space is the open input (OB-10)
