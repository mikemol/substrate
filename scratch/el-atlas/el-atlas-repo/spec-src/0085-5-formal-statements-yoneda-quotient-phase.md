## 5.10 Formal statements: statability, Theorem GCX, and the phase class

*Imported S42 under the corrected license of cotype S41: the lemma,
not the axiom. Each statement formalizes what the instrument already
measures; pilot and fiber-certificate indices are given inline.
Reviewer demands B3, B4, B5 (cotype S31) are discharged here.*

### 5.10a Statability as representability (B3)

Let S be the **probe category**: its objects are the admitted knob
configurations of the current space (165,888 in S_5c1b4fe911fd), each
admitted by a recorded correction event (KNOB_PROVENANCE is the
construction of S). *Honest grade:* at instrument grade v3.8, S is
finite and discrete; enrichment with non-identity morphisms (knob
moves, with naturality conditions on verdict maps) is a registered
reservation, not a present claim.

A claim c induces a partial **verdict presheaf** V_c on S with domain
dom(c) ⊆ S. Definitions:

- c is **statable** at probe m iff m ∈ dom(c). The V-kind verdict is
  membership in S \ dom(c): outside the domain of the restricted
  embedding — de-stated, not false.
- A **separator** for claims c, d is a probe m ∈ dom(c) ∩ dom(d) with
  V_c(m) ≠ V_d(m).
- A **circle** is an equivalence class under the zero-separator
  relation: the restricted Yoneda embeddings agree on the common
  domain. "Expressibility-intrinsic" therefore means: identification
  relative to the declared probe category, with the category's
  provenance carried (the space is the closure of recorded failure
  modes, §0).

Separation counts are margins (the source corpus's "Margin of Truth",
read at S30-S33): the number of probes witnessing distinctness.

### 5.10b Theorem GCX (B4): GALAXY is a one-mode decode of the ASPF carrier

Let F be the ASPF carrier: finite multisets R of positive ranks with
composition ⊠ = multiset union, realized on prime carriers by
n(R) = ∏ p_r over r ∈ R. Let the GALAXY reading be the α-shadow
W(R) = ∑_{r∈R} r, realized as log_α ∏ α^r for a fixed base α.

**Theorem (GCX).** φ: (F, ⊠) → (ℕ, +), φ(R) = ∑R, is a monoid
homomorphism; the exponential codec is exact on its image (the
identities α^{φ(R⊠R')} = α^{φ(R)}·α^{φ(R')} hold with no loss);
ker-equivalence is exactly rank-sum equality, and the quotient
genuinely collides: {1,4} ≠ {2,3} as multisets (prime carriers
2·7 = 14 ≠ 15 = 3·5) while φ agrees (both 5; α-shadows equal,
computed live in every v3.8 run). The fibers φ⁻¹(n) = multisets of
fixed rank-sum carry the lost information; the prime-carrier
realization is a fiber section (exact reconstruction). GALAXY is
therefore the ASPF carrier decoded through the single mode φ —
identification by exhibited quotient, requiring no axiom beyond the
isomorphisms shown (S41).

*Instrument indices:* pilot tools/gcx-codec (sampled identities, 500
trials) + exact collision witness, emitted live (fiber certificate
"mixed", v3.8); GCX ↔ CDC separated by 27,648 truth-separators —
the identification is with ASPF's quotient, not with the codec
contract.

### 5.10c The phase class (B5): the extension behind the braid

The braid circle's phase obstruction is the class of the central
extension 1 → Z₂ → D₄ → V₄ → 1 in H²(V₄, Z₂), with cocycle exhibited
by the commutator [N, S] = −id of the chart involutions. The class is
non-trivial (D₄ ≇ V₄ × Z₂): the phase cannot be globally trivialized,
which is the content the PHS claim measures point-wise on the locus
(fiber certificate "analytic-points", v3.8). Standard reference:
Brown, *Cohomology of Groups* (Appendix C.2 — reviewer-recommended
anchor, to be verified before deep citation).
