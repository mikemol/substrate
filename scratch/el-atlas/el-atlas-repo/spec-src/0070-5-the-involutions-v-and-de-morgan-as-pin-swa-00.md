## 5. The involutions: V₄ and De Morgan as pin-swap

**Definition 5.1 (the two generating involutions).** On the carrier:

- **negate-a-pin**: x ↦ −x on one coordinate (additive presentation);
  one C₂.
- **pin-swap**: (E⁺, E⁻) ↦ (E⁻, E⁺); a different C₂. On the bias
  coordinate, swap acts as b ↦ −b.

Their product is the diagonal involution; the two together generate the
Klein four-group **V₄**. **[W]**

**Theorem 5.2 (De Morgan is the swap).** The pin-swap *is* De Morgan —
the involution that exchanges ∧ and ∨. NOT, read on the pair, is the swap;
read on the locked locus (Lemma 2.6), it is the group inverse x ↦ x⁻¹
(equivalently u ↦ −u). De Morgan being one of the crossbar's two
generating involutions is why it sits as a C₂ inside V₄. **[W]**

**Theorem 5.3 (the carrier condition).** NOT(AND) ≡ OR holds **iff both**
of the following hold; each alone fails:

1. **Inverse-locked pins** (on the locus where negate-a-pin must equal
   pin-swap): pins of the form (x, 1/x) / (u, −u). Without the lock, the
   two involutions are simply different maps and the identity is false.
2. **Two log-linked operations** (a semiring carrier, §6). With only one
   operation and pure inversion, define OR(a,b) := 1/((1/a)(1/b)) = a·b:
   the product is **self-dual** under inversion, AND = OR collapse, and
   there is nothing for De Morgan to exchange.

**[W]** (both failure directions were exhibited in the source
derivation; the collapse in (2) was caught mid-derivation and is recorded
as Provenance P-3.)

---

**Theorem 5.4 (representation-dependence of V₄ — a corrected bug).** The
abstract V₄ of this section is exact, but *which concrete involutions
generate it depends on the representation*, and one of this spec's earlier
claims was false:

- **On the full pin plane**, single-pin-negate N and pin-swap S do **not**
  commute: ⟨N, S⟩ ≅ **D₄** (order 8), N·S is a 90° rotation of order 4, and
  the earlier claim "their product is the diagonal involution" is **false**
  there. **[W]** (the error was caught by an external computation quoted by
  the user; verified.) However: [N, S] = −id (negate-both), which is
  **central, order 2, and reversible** — so N and S commute *up to* the
  central twist, giving the central extension
  **1 → Z₂ → D₄ → V₄ → 1**, with V₄ surviving as the quotient. The exact
  V₄ inside the plane is the **diagonal subgroup {id, N₊, N₋, −id}** (the
  two single-pin negations, negate-both, identity), which commutes on the
  nose. **[W]**
- **On the four-corner (tetrahedron) representation** — the crossbar's four
  corners as the four vertices — the diagonal subgroup acts as exactly the
  three double-transpositions + id: the **normal V₄ of S₄**, commuting
  exactly, with the antipode −id = (Q₁Q₃)(Q₂Q₄) exchanging opposite
  corners. Pin-swap S acts there as a **single transposition** — a frame
  element, outside the content V₄. Conjugation of S₄ on this V₄ has image
  the **full S₃ = Aut(V₄)** (transitively permuting the three involutions)
  and kernel V₄ itself: **S₄ = V₄ ⋊ S₃ = Hol(V₄)**, the holomorph. **[W]**
- **The linear obstruction (why the pin chart cannot see the frame).** Any
  invertible linear map of the pin plane satisfies M(−v) = −M(v), so its
  induced corner permutation commutes with the antipode; the centralizer of
  the antipode in S₄ is exactly D₄. Hence the pin chart can linearly
  realize **only** D₄ — the braid-thickened V₄ — and the axis-mixing
  3-cycles of the S₃ frame are **not realizable by any linear map of the
  plane**. The full frame exists only on the corner representation. **[W]**

**Remark 5.5 (the braid reading — the verdict the computation invites and
must refuse).** "⟨N, S⟩ = D₄, not V₄" is computationally correct and
judgmentally a collapse: it discards (i) the central twist's
*reversibility* — N·S = (−id)·S·N is a crossing sign (the anticommutation
of Pauli X and Z; a symmetric-with-sign braiding), not an obstruction;
(ii) the quotient V₄, intact as D₄/center; (iii) the
representation-dependence — on the tetrahedron representation V₄ and its
full S₃ frame are exact. Forgetting the crossing sign is the braid →
permutation projection; the sign is *remembered, reversible* structure
riding on top of V₄, not a refutation of it. On the inverse-locked locus
(Lemma 2.6) the twist degenerates and V₄ is exact even in the pin chart —
which is precisely why Theorem 5.3 demands the inverse-lock. **[W]**

### 5.6 The pin-scenario catalog — what "the pin plane" was

Theorem 5.4 used "the pin plane" informally, and the phrase smuggled in a
scenario. Stated precisely: **a single pin read in isolation is one linear
axis of information**, readable in two charts — as the semiring 𝕄 = [0,∞]
(magnitudes, positive values only) and as the signed line 𝔸 = [−∞,+∞]
(positive and negative values), with **exp/ln as the magnitude mapping
between the two structures**. The atlas of §2 is *per-pin* structure. Two
pins are then either **independent** (Law 1.3: no cross-read) or have
**meaning composed** — a conjugatively-encoded interdependency between
both pins that is realized on reading. Which operations exist, and which
symmetry is visible, is a function of this **reading relation**, not of
the pins themselves. The catalog (each row's symmetry claim **[W]**,
verified):

| scenario | pins | interrelation | supported readings | frames presented | visible symmetry |
|---|---|---|---|---|---|
| **P1** | 1 | — | accumulate (write); **balance read** (net judgement, identity-anchored) in either codec: 𝕄 magnitude or 𝔸 signed via ln | the per-pin atlas (exp ⊣ ln) | **C₂** (the chart involution 1/y ↔ −u). Cannot express conflict vs ignorance (§5.7) |
| **P2-I** | 2 | independent (Law 1.3) | per-pin P1 reads only; cross-reads (mass, bias) exist only as *named external projections* (Remark 3.5, mode 2) and exit this scenario | two per-pin atlases | **V₄ exact** = {id, N₊, N₋, −id}: the diagonal sign maps, the *only* linear maps respecting no-cross-read. No swap (swap is a cross-read); **no braid possible** — the braid requires the cross-read independence forbids |
| **P2-C** | 2 | meaning composed; joint linear reads | joint linear functionals: (mass, bias); modes (d, c); the swap (an operation on the *encoding*); mode transport | crossbar; differential-mode frame | **D₄** = V₄ braided by the central twist; [N, S] = −id = **the conjugate-encoding interdependency surfacing on reading** — the phase bit / extension class (Theorem 5.4). Sub-case *inverse-lock* (u, −u): one meaning over two pins; twist degenerates; V₄ exact (Lemma 2.6) |
| **P2-G** | 2 | composed + **gated** read (sign-pattern extraction, mode 3 — the first nonlinearity) | which-corner reads; perspective anchoring (the 3+1) | the four corners (Belnap as crossbar corners); the tetrahedron | **S₄ = V₄ ⋊ S₃ = Hol(V₄)**: normal V₄ exact (double-transpositions) plus the S₃ = Aut(V₄) frame. The 3-cycles are realizable at the gate level and at *no* linear level |
| **P2ⁿ** | 2ⁿ | composed pairs of composed pairs, recursively | Walsh-mode reads (RM(1,m) linear layer); wire-swap conjugation; bridge readouts (4 pins = two composed pairs: the mass/bias instrument, §11.3–11.4) | doubling tree; mode hierarchy | per-level P2-C structure iterated; overlay across towers climbs RM degree (§13.2) |

**The ladder law (the catalog's content).** Visible symmetry is purchased
by the reading relation:

> independence → **V₄** (exact, commuting, no swap)
> composition + linear joint reads → **D₄** (braided V₄; phase = the
> encoding interdependency)
> composition + gated reads → **S₄ = Hol(V₄)** (the frame unlocks)

and the consumption-mode grading (§13.1) *predicts* this ladder: degree-1
(linear) reads cap the visible symmetry at D₄; the gate — the first
nonlinearity, Mode 3 — is exactly what unlocks the corner frame and its
S₃. The frame was never missing; it was priced in a currency (nonlinear
reads) that the linear scenarios do not spend. **[W]**

**Re-scoping Theorem 5.4.** "The pin plane" = scenario **P2-C**: the joint
signed-chart read of two *meaning-composed* pins. The D₄ result is a
theorem about that reading relation. The spec's §5 V₄ lives in **P2-I**
(generators {N₊, N₋}, diagonal — the bug fix lands here: the correct
independent-scenario generator pair was never {negate-one, swap}) and in
**P2-C on the locus**; the holomorph lives in **P2-G**. All three are
correct *in their scenario*; draft 13's error was scoping, and the quoted
"D₄ not V₄" verdict was a scenario-conflation in the other direction.
**[W]**

### 5.7 The balance channel and the differential encoding (the catalog's semantics)

**A single pin is the balance channel.** Reading the real component of a
single pin holds **the balance of the evidence** — net judgement, read
*relative to the identity element of its declared frame* — and cannot
express internal conflict. The expressivity limit of P1 is now exact: the
single pin says how far for-vs-against nets out; it cannot say whether a
given net came from pure refutation or from refutation amid heavy
conflict, nor distinguish ignorance from deadlocked conflict (both net to
the identity). **[W]** (witnessed: (0,5) and (5,10) have the same balance
−5; (0,0) and (7,7) both balance to 0; the pairs separate only on the
gained axis.)

**The chart is a codec, and balance is identity-anchored.** The real
component can be encoded to the ring (logspace, identity 0, negatives
licensed) or the semiring (exp-space, identity 1, positives only) — *it
does not matter which, so long as the encoding matches the decoding for
the normal operations* (the ones the exp/ln conjugation transports:
accumulate, negate, compare-to-identity). The valid (stored sign ×
declared frame) cells are exactly three: negative+log, positive+log,
positive+semiring; **negative+semiring is ill-typed** (the semiring has
no negatives — Caveat 2.4a, stated on the value side). Frame mismatch is
*silent corruption of balance*: a semiring-stored "against" (value below
1) decoded in the log frame reads as "for" (a positive number). The
identity element is the anchor; remembering the frame *is* remembering
where balance sits. **[W]**

**Codec family extension (corpus import).** The consolidation report's C3
adds a third valid encoding family: the **shifted log**, e ↦ ln(1 + e/κ)
(equivalently the shifted embedding e ↦ 1 + e/κ before the log), with
identity image 0 and **κ as a headroom/scale parameter** — joining ℛ and
Maslov h on OB-1's axis (§5.8g). The anchor discipline extends unchanged:
every codec family must declare its identity image. **[S]**

**The projection inventory (corpus C4: "these must not be conflated").**
There is no single privileged scalar shadow of the pair. The corpus names
five: **total commitment** (mass m), **differential tilt** (balance b),
**unsigned decisiveness** (|b| — gate-adjacent, mode 3), **single-conductor
collapse** (read one pin), and the bridge's **ratio/null-test** shadow
(level 2). The worked-rails result locates exactly where they coincide:
at the saturated rails, and only there — in the interior they diverge,
which is why conflating them is the C4 error. **[S]**

**A pair of pins: two channels, or one channel differentially encoded.**
The real components of a pair either hold **two channels' balances
independently** (P2-I: two propositions, diagonal operations only), or
hold **one channel's data as a differential encoding** (P2-C) — and the
differential encoding is not a mere re-housing: it **gains access to
measuring conflict and ignorance**, not just balancing positive against
negative. The differential mode d = u₊ − u₋ carries exactly what the
single pin held (the balance); the common mode c = u₊ + u₋ is the
*gained* axis (mass), separating pure-refutation from
refutation-amid-conflict and ignorance from deadlocked conflict. **The
carrier (E⁺, E⁻) is therefore, in encoding terms, the differential
encoding of the balance channel** — §1's pair restated as a codec: one
proposition, two pins, with the encoding purchasing the mass axis. **[W]**

**The recursion.** Each composition level repeats the purchase: composing
two encoded channels re-expresses their balances as the next level's
differential modes and *gains* a new common mode (§11.10's "what a level
cannot read as signal is re-encoded as the next level's channel"). Four
pins as two composed pairs is the Wheatstone instrument: the
pair-of-pairs' differential is the galvanometer (bias), its common mode
the supply (mass) — the bridge is the level-2 instance of the same gain.
**[S]**

**The worked rails, re-grounded.** The four presentations of
refutation-false (single pin −∞ signed; single pin 0 semiring; pair
(−∞, +∞) signed; pair (0, +∞) semiring) are one semantic point under
(chart × pin-count): the chart pairs are codec transports (lossless;
ln 0 = −∞); the pin-count pairs are the balance channel vs its
differential encoding. The single-pin reading −∞ is a *genuine* balance
refutation ("infinitely against"), not an empty accumulator; what it
cannot certify is the **mass** behind the net — "refutation false" in
full (zero support *and* saturated counter-evidence, F = (0, ∞), the
bottom endpoint of the inverse-locked locus) is expressible only in the
differential encoding. At the rails the natural projections coincide
(which is why the single-pin read feels unambiguous there); in the
interior they diverge. Classical truth values are the locus rails;
locus-constrained NOT exchanges them (F → T); *independent* single-pin
negation at the F rail leaves the locus and lands on conflict, B — the
classical NOT is the composed one (Theorem 5.3's inverse-lock as rail
dynamics). **[W]**

