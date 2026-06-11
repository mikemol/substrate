### 11.10 Communication, interfacing, and signal processing

The carrier has a channel form, and the corpus treats it as one. Five
threads, graded:

**Differential signaling is the carrier's transmission form.** Sent as
a differential pair, the pins put **bias on the differential mode and
mass on the common mode**. Standard communication practice applies
common-mode rejection — read the difference, discard the sum as noise.
Under Remark 3.5 that is a *named projection*, and the atlas inverts
the engineering default: **mass is data** (it is the B/N distinction),
so CMR-as-semantics is exactly the collapse Lemma 3.2 forbids, and the
two-readout instrument of §11.4 is the channel architecture that
refuses it. **[S]** (assembly of witnessed pieces; the engineering
definitions are corpus-cited in D-1 §C2.)

**The phantom hierarchy: nothing is noise all the way up.** D-1's
quad-star reading (Poulton's phantom/ghost/wraith hierarchy) gives a
physical recursion in which **common-mode structure at one level
becomes the signal-bearing differential structure of the next level**.
**[W]** (corpus-witnessed). Read against §11.6's doubling: the
phantom tower is a communication stack — what a level cannot read as
signal is re-encoded as the next level's channel. This is the
no-collapse discipline (Remark 8.4) as a transmission architecture: the
quotient is never taken; the residue is promoted. **[S]**
(Corpus locus: the Evidence–Differential consolidation report tags this
source [E4]; the hierarchy is the named external anchor of this section's
recursion.)

**Pilot result (OB-12, witnessed) — and a frame correction.** The
structure here is, in its own right, a **recursive binary tree with a
conjugation**: the iterated (sum, diff) splitting, i.e. the
Walsh–Hadamard recursion H₂ⁿ = H₂ ⊗ H₂ⁿ⁻¹, with a per-level involution
acting on the modes as (d, c) ↦ (−d, c) — exactly the pin-swap (a swap
of the underlying conductor pair sends d ↦ −d, c ↦ c). This is the
**Hadamard doubling tree**: the orthogonal mode decomposition of a
2ⁿ-conductor bundle (modes orthonormal at ideal balance, witnessed
levels 1–3). It is a complete, well-behaved object on its own and owes
nothing to any algebra.

The history of this object being called "Cayley–Dickson" is a
**frame-collapse worth recording as a caveat**, because it is the
forbidden quotient (Remark 3.5) committed one layer down. "Recursive
binary tree + conjugation" is a two-axis description: a *doubling
functor* (one axis) that may or may not carry a *bilinear product* (the
other axis). CD is the famous landmark sharing the first axis, so a
nearest-name reading collapses both axes onto it and asserts the
product — which this construction never contained. The pilot confirms
the collapse: **no channel multiplication is exhibited**, so the staged
loss of algebraic identities (commutativity, then associativity) that
*characterises* CD cannot occur — there is no product for them to be
lost from. (The numerical degradation that does occur — mode-isolation
leakage under conductor imbalance — is analytic robustness; it shrinks
per level under √-normalisation rather than growing, so it is not the
staged algebraic loss either.)

The accurate framing therefore puts the tree first and CD second, not
the reverse: **this is a Hadamard doubling tree with swap-conjugation;
Cayley–Dickson would be one possible *completion* of it — the one
obtained by bolting on a specific bilinear product — and nothing in the
construction calls for that product.** Whether a natural channel product
exists at all is the open residue (OB-12); if none is natural, the
full-CD framing is retracted and only the doubling-tree statement
stands. **[W]** for the doubling tree + involution; **[C]** for any
claim that requires a product (CD or otherwise).

**Repeater and regeneration.** Witness 7.5's fade-resistance content is,
in channel terms, a **repeater specification**: saturating rails
regenerate the signal, and choosing ℛ is choosing the regeneration
regime of the link. The communication reading adds a requirement the
logic reading didn't surface: a repeater for *this* carrier must
regenerate **both modes** — a bias-only repeater (standard practice)
silently erases the mass channel at every hop. **[S]**

**The spectral layer (Laplace / s-plane).** The corpus already
generalizes the carrier to AC: D-3's formalization extends to the
complex s-plane ℂₛ, and D-17 carries Total Semantic Impedance
**Z = R + jX** — dissipative and reactive components, i.e. §11.5's
resistive settlement and stored-potential coordinates as the real and
imaginary parts of one complex quantity. **[W]** as corpus records. The
candidate that follows: **complexifying the atlas** — on ℂ, log splits
into magnitude + phase, so the §8 dictionary (norm/phase) would become
*literal* rather than borrowed, and filtering/spectral analysis of
evidence streams becomes available. Whether NOT, the locked locus, and
De Morgan survive complexification is unworked: **OB-9.**

**Sparse signaling and the cost of ignorance.** D-20 frames the
"Problem of Vacuum Density": the thermodynamic cost of encoding
non-events can exceed the information content of the signal. In carrier
terms: **N (low mass) is the expensive-to-transmit state** — absence of
evidence still costs channel. The same document family carries an
explicit structural critique of Bayesian-probability foundations —
independent corpus support for Law 3.1's stance, from the
information-physics direction. **[W]** (corpus-witnessed).

**Interfacing as the register's own theory.** D-23 redefines axioms as
**solvable interfaces equipped with theorem-generating structures**
(triangulation, homological auditing, representable local generators)
rather than terminal postulates. This is the discipline §13 already
practices: each obligation is an interface — a stated contract with a
named discharge path — not an assumed truth and not a defect. The
corpus thereby supplies the standardization story for the spec's own
non-closure: **an open obligation is a port, and ports are how systems
compose.** SYSTEM Π's self-hosted upgrade artifact (D-16 family) is the
packaging precedent at the protocol level. **[S]**

---

