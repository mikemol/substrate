# file: ladder_crosscutting_3_consumption.feature
# obligation source: §13 (Modes 1-5, §13.1 RM grading, §13.2 OB-12, §13.3)
Feature: Consumption modes — how data is taken in and acted on [ladder, cross-cutting, depth=3]
  Five ways a value is consumed, graded by Reed-Muller degree. Accumulate and
  transport are lossless; project and gate are named lossy reads; overlay is
  the one constructive (degree-building) consumption.

  Background:
    Given the prohibition obligation is satisfied (governance_crosscutting_2_prohibition)
    And the doubling tree is the Sylvester-Hadamard matrix with rows the Walsh characters

  Scenario Outline: the five modes and what they consume
    Given consumption mode "<mode>"
    When a value is consumed
    Then the action is "<action>"
    And the RM character is "<rm>"

    Examples:
      | mode       | action                          | rm                         |
      | accumulate | write a running sum to one pin  | degree-1 (linear)          |
      | project    | read-down to a named scalar     | degree-1 (linear), lossy   |
      | gate       | consume-by-committing to a rail | first nonlinearity         |
      | transport  | read-across via exp/log         | degree-1 (linear), lossless|
      | overlay    | glue two networks on shared S   | builds degree (bilinear)   |

  Scenario: the linear layer is RM(1,m) — "additive is logic in circuit clothing"
    Given modes accumulate, project, transport
    When their consumed forms are classified
    Then all are linear in the pins
    And they live entirely in RM(1, m), the first-order Reed-Muller / Walsh layer
    And no single tower climbs past first order

  Scenario: the product is the overlay, not the doubling recursion (OB-12 resolved)
    Given two towers each producing degree-1 (linear) reads
    When their reads are multiplied pointwise at the shared instance
    Then the product is a degree-2 Reed-Muller codeword
    And it is generically not in RM(1, m)
    And the bilinear product lives in the overlay (Mode 5), not in a single tower

  Scenario: iterated overlay generates the full RM filtration (OB-10 scoping, witnessed)
    Given the degree-1 reads x0, x1, x2 for m = 3
    When closed under the pointwise (overlay) product
    Then the closure spans the full RM(3,3) (rank 8 of 8)
    And climbing the RM degree filtration equals composing overlays

  Scenario: the no-collapse discipline in code terms (§13.3)
    Given the five modes
    When classified by information loss
    Then accumulate and transport retain the full transform (lossless)
    And project and gate are named decoders to a subcode (lossy)
    And overlay is the one constructive consumption (builds degree up)
    And "never collapse the pair" reads as "keep the full Walsh-Hadamard transform, name every decoder"
