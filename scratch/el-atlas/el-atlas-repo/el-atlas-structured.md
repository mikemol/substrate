# The EL-Atlas, Structured Edition

*Mechanically derived: the ordering, grouping, glossary, cross-reference, and*
*perspective tables below are computed by `el-atlas-depsort.py` (empirical*
*dependency sort + basis refinement), not hand-arranged. Definitional sentences*
*and spec pointers are claim metadata; everything structural is calculated.*

**Reading the perspective tables:** P = visible/true from that vantage; F = false
there; V = not statable there (vacuous). The perspectives are the session's
discovered vantage points: the pin scenarios (§5.6), the classical section, the
probability slice, and the codec/operation degradations.

## Table of Contents

**Part 1 — Layer 0 (foundations)**
- [The chart adjunction (exp ⊣ log)](#the-chart-adjunction-exp-⊣-log)
- [The crossbar](#the-crossbar) *(shared-substrate coincidence, split under refinement)*
- [The Noether pairings](#the-noether-pairings) *(shared-substrate coincidence, split under refinement)*

**Part 2 — Layer 1**
- [The balance channel](#the-balance-channel) *(shared-substrate coincidence, split under refinement)*
- [The codec contract](#the-codec-contract) *(shared-substrate coincidence, split under refinement)*
- [The exact V₄](#the-exact-v4)

**Part 3 — Layer 2**
- [The involution coincidence ≡ The classical section](#the-involution-coincidence) *(one structure, intrinsic circle)*
- [The classical rails](#the-classical-rails)
- [The braided V₄ (D₄)](#the-braided-v4-d4)

**Part 4 — Layer 3**
- [The prohibition ≡ The differential purchase](#the-prohibition) *(one structure, intrinsic circle)*
- [The De Morgan requirements](#the-de-morgan-requirements)
- [The phase support theorem](#the-phase-support-theorem)


---


# Part 1 — Layer 0 (foundations)


## The chart adjunction (exp ⊣ log)

**ADJ — The chart adjunction (exp ⊣ log)** (§2, Lemma 2.5b). The two per-pin charts — semiring magnitudes and the signed line — form an adjoint equivalence; the codec pair whose round-trips are identities.


*Perspective visibility — ADJ:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | F | P | P | P |

*Cross-reference — ADJ:* depends on —; required by ['BAL']; independent of 12 claims (CDC, CRS, PUR, PRO, LOC…).


## The crossbar

**CRS — The crossbar** (§4). (mass, bias) = (E⁺+E⁻, E⁺−E⁻) is an invertible change of basis on the pair.

*Coarse-basis circle with ['CRS', 'NOE']: split under refinement — a projection coincidence of shared substrate, not mutual constitution.*


*Perspective visibility — CRS:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P |

*Cross-reference — CRS:* depends on ['NOE']; required by ['D4C', 'L26', 'LOC', 'NOE', 'PHS', 'PRO', 'PUR', 'RLS', 'T53', 'V4I']; independent of 3 claims (ADJ, BAL, CDC).


## The Noether pairings

**NOE — The Noether pairings** (§11.8, OB-7). The squeeze conserves mass; the common translation conserves bias — the two charges of the pair's symmetry flows.

*Coarse-basis circle with ['CRS', 'NOE']: split under refinement — a projection coincidence of shared substrate, not mutual constitution.*


*Perspective visibility — NOE:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P |

*Cross-reference — NOE:* depends on ['CRS']; required by ['CRS', 'D4C', 'L26', 'LOC', 'PHS', 'PRO', 'PUR', 'RLS', 'T53', 'V4I']; independent of 3 claims (ADJ, BAL, CDC).


# Part 2 — Layer 1


## The balance channel

**BAL — The balance channel** (§5.7). A single pin's real component holds the balance of the evidence, read relative to its frame's identity element; conflict is inexpressible.

*Coarse-basis circle with ['BAL', 'CDC']: split under refinement — a projection coincidence of shared substrate, not mutual constitution.*


*Perspective visibility — BAL:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | F | F | P | P |

*Cross-reference — BAL:* depends on ['ADJ', 'CDC']; required by ['CDC']; independent of 11 claims (CRS, PUR, PRO, LOC, L26…).


## The codec contract

**CDC — The codec contract** (§5.7, Caveat 2.4a). Ring or semiring encoding is indifferent iff encode matches decode; frame mismatch silently flips balance; negative+semiring is ill-typed.

*Coarse-basis circle with ['BAL', 'CDC']: split under refinement — a projection coincidence of shared substrate, not mutual constitution.*


*Perspective visibility — CDC:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | P | P | P | P | P | F | P | P |

*Cross-reference — CDC:* depends on ['BAL']; required by ['BAL']; independent of 12 claims (ADJ, CRS, PUR, PRO, LOC…).


## The exact V₄

**V4I — The exact V₄** (§5, Theorem 5.4, §5.6 P2-I). Under independence, the only admissible linear maps are diagonal; their sign-involutions form the Klein four-group exactly — no swap, no braid.


*Perspective visibility — V4I:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | V |

*Cross-reference — V4I:* depends on ['CRS', 'NOE']; required by ['D4C', 'PHS', 'RLS', 'T53']; independent of 7 claims (ADJ, BAL, CDC, PUR, PRO…).


# Part 3 — Layer 2


## The involution coincidence ≡ The classical section — one structure

**L26 — The involution coincidence** (Lemma 2.6). On the classical section, constrained negation equals the pin-swap — they coincide iff the section is exactly f = −id.

**LOC — The classical section** (Lemma 2.6, §5.8b). The inverse-locked locus (u, −u) is exactly c ≡ 0: the balance channel embedded in the pair; classical logic with the purchased axis off.

*Refinement verdict (v3, exhaustive over 1536 models): TRUTH-INTRINSIC — zero separators of any kind across the full space; co-movement 1.00. Closure-under-break (taxonomy class 3): every perturbation breaks the loop coherently. Break 3 adds kind-structure within the co-movement (noisy lock: LOC=U, L26=F). A ∀-over-declared-bases claim: refutable, never provable (open-by-design).*


*Perspective visibility — L26:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P |

*Perspective visibility — LOC:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | P |

*Cross-reference — L26:* depends on ['CRS', 'NOE', 'RLS']; required by ['PHS', 'RLS', 'T53']; independent of 7 claims (ADJ, BAL, CDC, PUR, PRO…).

*Cross-reference — LOC:* depends on ['CRS', 'NOE', 'RLS']; required by ['PHS', 'RLS', 'T53']; independent of 7 claims (ADJ, BAL, CDC, PUR, PRO…).


## The classical rails

**RLS — The classical rails** (§5.7 worked rails). The locus endpoints are T and F; composed NOT exchanges them; independent negation at a rail lands on conflict. The rails are a compactification fact, detachable from the section.


*Perspective visibility — RLS:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | P | P | P | P | P | P | V |

*Cross-reference — RLS:* depends on ['CRS', 'L26', 'LOC', 'NOE', 'V4I']; required by ['L26', 'LOC', 'PHS', 'T53']; independent of 6 claims (ADJ, BAL, CDC, PUR, PRO…).


## The braided V₄ (D₄)

**D4C — The braided V₄ (D₄)** (Theorem 5.4, Remark 5.5). Composed reading licenses the swap; ⟨negate-one, swap⟩ = D₄, the central extension of V₄ by the reversible twist [N,S] = −id.


*Perspective visibility — D4C:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | V | P | P | P | P | P | V |

*Cross-reference — D4C:* depends on ['CRS', 'NOE', 'V4I']; required by ['PHS', 'PRO', 'PUR']; independent of 7 claims (ADJ, BAL, CDC, LOC, L26…).


# Part 4 — Layer 3


## The prohibition ≡ The differential purchase — one structure

**PRO — The prohibition** (§3, §5.8a). Pinning the purchased axis (normalization) conflates conflict with ignorance; collapse is an arity-mismatched decode; probability is the c-pinned slice.

**PUR — The differential purchase** (§5.7). Encoding one channel over two pins gains the conflict/ignorance axis: d carries the balance, c is the purchased mass axis.

*Refinement verdict (v3, exhaustive over 1536 models): EXPRESSIBILITY-INTRINSIC — zero separators, co-movement 1.00, but PRO is never F anywhere in the space: it is a theorem, truth-stable wherever statable. The circle is mutual constitution at the statability level, one-way at the truth level: pinning falsifies the purchase and de-states the theorem — the theorem outlives the purchase as a truth but loses its subject. Refines the draft-16 'intrinsic' verdict (Break 3's discovery). ∀-over-declared-bases; open-by-design.*


*Perspective visibility — PRO:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | V | P | V | P | P | P | P |

*Perspective visibility — PUR:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | V | P | F | P | P | P | P |

*Cross-reference — PRO:* depends on ['CRS', 'D4C', 'NOE']; required by —; independent of 9 claims (ADJ, BAL, CDC, LOC, L26…).

*Cross-reference — PUR:* depends on ['CRS', 'D4C', 'NOE']; required by —; independent of 9 claims (ADJ, BAL, CDC, LOC, L26…).


## The De Morgan requirements

**T53 — The De Morgan requirements** (Theorem 5.3). NOT(AND) ≡ OR requires two operations (one collapses OR into AND) and the inverse-lock (the classical section).


*Perspective visibility — T53:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | F | P | P | P | P | P | F | V |

*Cross-reference — T53:* depends on ['CRS', 'L26', 'LOC', 'NOE', 'RLS', 'V4I']; required by —; independent of 7 claims (ADJ, BAL, CDC, PUR, PRO…).


## The phase support theorem

**PHS — The phase support theorem** (§5.8c, §8.5–8.6). The extension class (the phase bit) is trivial exactly on the classical section and nontrivial exactly off it; a single pin has no phase.


*Perspective visibility — PHS:*

| FULL | P1 | P2-I | CLASSICAL | PROB | NO-CODEC | NO-ANCHOR | ONE-OP | NO-NEG |
|---|---|---|---|---|---|---|---|---|
| P | V | V | V | P | P | P | P | V |

*Cross-reference — PHS:* depends on ['CRS', 'D4C', 'L26', 'LOC', 'NOE', 'RLS', 'V4I']; required by —; independent of 6 claims (ADJ, BAL, CDC, PUR, PRO…).


---

# Glossary (computed)

**The De Morgan requirements** [T53] — NOT(AND) ≡ OR requires two operations (one collapses OR into AND) and the inverse-lock (the classical section). *(Layer 3; Theorem 5.3)*

**The Noether pairings** [NOE] — The squeeze conserves mass; the common translation conserves bias — the two charges of the pair's symmetry flows. *(Layer 0; §11.8, OB-7)*

**The balance channel** [BAL] — A single pin's real component holds the balance of the evidence, read relative to its frame's identity element; conflict is inexpressible. *(Layer 1; §5.7)*

**The braided V₄ (D₄)** [D4C] — Composed reading licenses the swap; ⟨negate-one, swap⟩ = D₄, the central extension of V₄ by the reversible twist [N,S] = −id. *(Layer 2; Theorem 5.4, Remark 5.5)*

**The chart adjunction (exp ⊣ log)** [ADJ] — The two per-pin charts — semiring magnitudes and the signed line — form an adjoint equivalence; the codec pair whose round-trips are identities. *(Layer 0; §2, Lemma 2.5b)*

**The classical rails** [RLS] — The locus endpoints are T and F; composed NOT exchanges them; independent negation at a rail lands on conflict. The rails are a compactification fact, detachable from the section. *(Layer 2; §5.7 worked rails)*

**The classical section** [LOC] — The inverse-locked locus (u, −u) is exactly c ≡ 0: the balance channel embedded in the pair; classical logic with the purchased axis off. *(Layer 2; Lemma 2.6, §5.8b; intrinsic-circle member)*

**The codec contract** [CDC] — Ring or semiring encoding is indifferent iff encode matches decode; frame mismatch silently flips balance; negative+semiring is ill-typed. *(Layer 1; §5.7, Caveat 2.4a)*

**The crossbar** [CRS] — (mass, bias) = (E⁺+E⁻, E⁺−E⁻) is an invertible change of basis on the pair. *(Layer 0; §4)*

**The differential purchase** [PUR] — Encoding one channel over two pins gains the conflict/ignorance axis: d carries the balance, c is the purchased mass axis. *(Layer 3; §5.7; intrinsic-circle member)*

**The exact V₄** [V4I] — Under independence, the only admissible linear maps are diagonal; their sign-involutions form the Klein four-group exactly — no swap, no braid. *(Layer 1; §5, Theorem 5.4, §5.6 P2-I)*

**The involution coincidence** [L26] — On the classical section, constrained negation equals the pin-swap — they coincide iff the section is exactly f = −id. *(Layer 2; Lemma 2.6; intrinsic-circle member)*

**The phase support theorem** [PHS] — The extension class (the phase bit) is trivial exactly on the classical section and nontrivial exactly off it; a single pin has no phase. *(Layer 3; §5.8c, §8.5–8.6)*

**The prohibition** [PRO] — Pinning the purchased axis (normalization) conflates conflict with ignorance; collapse is an arity-mismatched decode; probability is the c-pinned slice. *(Layer 3; §3, §5.8a; intrinsic-circle member)*


# Cross-Reference Index (computed)

| claim | layer | depends on | required by | circle |
|---|---|---|---|---|
| ADJ | 0 | — | BAL | — |
| BAL | 1 | ADJ, CDC | CDC | BAL ≡ CDC |
| CDC | 1 | BAL | BAL | BAL ≡ CDC |
| CRS | 0 | NOE | D4C, L26, LOC, NOE, PHS, PRO, PUR, RLS, T53, V4I | CRS ≡ NOE |
| PUR | 3 | CRS, D4C, NOE, PRO | PRO | PRO ≡ PUR |
| PRO | 3 | CRS, D4C, NOE, PUR | PUR | PRO ≡ PUR |
| LOC | 2 | CRS, L26, NOE, RLS | L26, PHS, RLS, T53 | L26 ≡ LOC ≡ RLS |
| L26 | 2 | CRS, LOC, NOE, RLS | LOC, PHS, RLS, T53 | L26 ≡ LOC ≡ RLS |
| T53 | 3 | CRS, L26, LOC, NOE, RLS, V4I | — | — |
| V4I | 1 | CRS, NOE | D4C, PHS, RLS, T53 | — |
| D4C | 2 | CRS, NOE, V4I | PHS, PRO, PUR | — |
| PHS | 3 | CRS, D4C, L26, LOC, NOE, RLS, V4I | — | — |
| RLS | 2 | CRS, L26, LOC, NOE, V4I | L26, LOC, PHS, T53 | L26 ≡ LOC ≡ RLS |
| NOE | 0 | CRS | CRS, D4C, L26, LOC, PHS, PRO, PUR, RLS, T53, V4I | CRS ≡ NOE |

*Independence count: 53 of 91 pairs carry no dependence in either direction.*