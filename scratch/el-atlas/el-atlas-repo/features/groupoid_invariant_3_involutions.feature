# file: groupoid_invariant_3_involutions.feature
# obligation source: §5 (Def 5.1, Thm 5.2, Thm 5.3)
Feature: The involutions — V4 and De Morgan as pin-swap [groupoid, invariant, depth=3]
  Two generating involutions (negate-a-pin, pin-swap) generate the Klein
  four-group; the pin-swap is De Morgan; NOT(AND) equivalent OR requires both
  inverse-locked pins and a two-operation log-linked semiring.

  Background:
    Given the crossbar obligation is satisfied (ladder_local_2_crossbar)
    And the carrier in the additive chart

  Scenario: negate-a-pin is one involution
    Given a coordinate x on one pin
    When negate-a-pin is applied
    Then x maps to -x
    And applied twice it is the identity

  Scenario: pin-swap is De Morgan (Thm 5.2)
    Given the pair (E_plus, E_minus)
    When pin-swap is applied
    Then it maps to (E_minus, E_plus)
    And on the bias coordinate b it acts as b -> -b
    And it is the involution exchanging AND and OR

  # CORRECTED (draft 13, Theorem 5.4): on the full pin plane, negate-ONE-pin and
  # pin-swap generate D4, not V4 — their product is a 90-degree rotation of order 4.
  # The exact V4 is the diagonal subgroup; the prior scenario here was a bug.
  Scenario: the exact V4 on the pin plane is the diagonal subgroup
    Given negate-pin-plus, negate-pin-minus, and negate-both
    When composed in any order
    Then all pairs commute and all non-identity elements have order 2
    And with the identity they form the Klein four-group exactly

  Scenario: negate-a-pin and pin-swap braid rather than commute (Theorem 5.4)
    Given single-pin-negate N and pin-swap S on the full pin plane
    When N and S are composed in both orders
    Then N.S = (negate-both) . S.N
    And the commutator [N,S] is negate-both: central, order 2, reversible
    And the generated group is D4, the central extension of V4 by Z2
    And the extension class is the phase bit of the amplitude reading

  Scenario: V4 is exact on the inverse-locked locus
    Given the locus (u, -u) of Lemma 2.6
    When the involutions are restricted to it
    Then the central twist degenerates and V4 holds on the nose
    And this is why NOT(AND) equivalent OR demands the inverse-lock

  Scenario: the S3 frame lives on the corner representation only
    Given the four crossbar corners as the tetrahedron vertices
    When conjugation permutes the three involutions of the normal V4
    Then the image is the full S3 = Aut(V4) and the kernel is V4 (S4 = Hol(V4))
    And no linear map of the pin plane realizes the axis-mixing 3-cycles
    And re-pinnings of the V4 interface compose as this S3

  Scenario: NOT(AND) equivalent OR requires inverse-locked pins (Thm 5.3, face 1)
    Given pins that are not inverse-locked
    When the identity NOT(AND) equivalent OR is checked
    Then it fails
    And the reason is that negate-a-pin no longer coincides with pin-swap

  Scenario: NOT(AND) equivalent OR requires two operations (Thm 5.3, face 2)
    Given a single operation under pure inversion
    When OR is defined as 1/((1/a)(1/b))
    Then OR(a,b) = a*b equals AND
    And AND and OR collapse, leaving nothing for De Morgan to exchange

  # morphism-typed obligation -> naturality scenario (skill Move 2 step 6)
  Scenario: naturality — pin-swap commutes with the chart transition
    Given the pin-swap involution in chart A (b -> -b) and in chart M (ratio -> 1/ratio)
    When transported across exp/log
    Then the square commutes: exp(swap_A(b)) = swap_M(exp(b))
    And De Morgan is the same C2 element in both charts
