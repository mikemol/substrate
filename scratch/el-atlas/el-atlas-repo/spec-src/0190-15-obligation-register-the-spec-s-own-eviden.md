## 15. Obligation register (the spec's own evidence pairs)

Open items, each carried as an (evidence-for, evidence-against) pair in
this spec's own idiom — held live, not resolved by fiat. Both-low items
are honest ignorance; any future both-high item is a flagged
contradiction, not an explosion.

**OB-1 — the value of ℛ.**
For: the contract is coherent (7.3); instances are definable today; the
saturation dynamics are now witnessed on the one-parameter chart
(Witness 7.5: absorbing rails, unstable neutral, fade-resistance = drive
to saturation); the circuit realization adds the metastability picture
(§11.5); and the corpus contains a five-validator survey of exactly this
fork — bounded structures vs unbounded resource algebras (D-22) — plus
the repeater requirement that any instance regenerate both modes
(§11.10).
Against: the witnessed dynamics attach to the decision projection, not
the carrier pair; the per-pin accumulator range, the specific potential
and measure, and the critical drive remain explicitly the user's design.
*Status: open by design — the permanent loop, now with a tighter
contract. Discharge path: a chosen instance per application, each
recorded as an instance, never back-ported as "the" range.*

**OB-2 — status of the quantum framing.**
For: the literal commitments (unnormalized pair, no quotient, interference
region) are all witnessed.
Against: no phase-composition law is specified; "amplitude" beyond the
dictionary of 8.2 is so far analogy. *Discharge path: either specify how
phases compose (normative) or mark 8.2 as the full literal content
(illustrative).*

**OB-3 — Conjecture 8.3 (holonomy = enclosed contradiction).**
For: the dictionary makes the statement well-typed; a test harness with
the d∘d = 0 gate exists; **and the discharge path now has a proven
sibling** — Abramsky–Brandenburger sheaf-theoretic contextuality
(App. B, S-F) already establishes contradiction/contextuality as a
non-vanishing Čech cohomology obstruction to gluing, with δ∘δ = 0 built
in. *Discharge path (upgraded): construct the comparison functor from
the EL-Atlas coefficient system to AB-contextuality; if it lands,
Conjecture 8.3 inherits a proof-shape rather than starting bare.*
*Boundary clause (Carù): the cohomological obstruction is not a complete
invariant of strong contextuality, so the identification can be sound but
cannot be made complete — 8.3 must be stated as "non-vanishing holonomy ⇒
enclosed contradiction," not an iff.* **Harness-framing correction
(recorded run):** the d∘d=0 gate was first set on a *filled* triangle,
which is contractible (H¹=0) and can carry no holonomy — there is nothing
enclosed, so the test was structurally incapable of exhibiting the
phenomenon. On the triangle *boundary* (an unfilled 1-cycle) H¹=1 and a
**bias-holonomy genuinely exists** (= net bias accumulated around the
loop). So the conjecture must be tested on complexes with real 1-cycles,
not filled simplices. Status after the run: bias-holonomy around a hole is
**witnessed**; the identification of that holonomy with *contradiction*
(mass / both-high) is still unrun, and the AB comparison functor is still
unbuilt. The d∘d=0 gate itself passes (it always will — it is the cochain
axiom); the content is the H¹ class, which requires a hole to be nonzero.

**OB-4 — formal verification of the correspondence tests (§10).**
For: five witness functors are sketched with concrete tests.
Against: none executed; all entries remain Implicit/Candidate, none
Present. *Discharge path: execute per test; promote to Present only with
a witness.*

**OB-5 — the strong Wheatstone identification. WITNESSED (via the chart adjunction).**
The galvanometer-null and the pin-swap fixpoint are the **same balance
locus read in the two charts** (Lemma 2.5b): the pin-swap fixpoint is
bias b = E₊−E₋ = 0 in the additive chart, and the galvanometer balances
at the ratio E₊/E₋ = 1 in the multiplicative chart — and exp(b)=ratio
maps one to the other losslessly, mass preserved as the product axis. A
run initially mis-flagged this as a chart conflation (a forbidden ratio);
that was itself the error — crossing charts is the exp ⊣ log adjunction
(invertible, structure-preserving), not the §3 collapse (lossy,
one-way). See Remark 2.5c for the distinction. The galvanometer reads the
**chart-image** ratio, not the **collapse** ratio. *Status: the weak and
strong structural identifications stand as witnessed; the remaining open
piece is only the further claim that galvanometer *deflection magnitude*
equals the sign-cocycle's value (the affineness/R12 identification),
which is a separate quantitative claim untouched by this correction.*

**OB-6 — CHL-E axiom check.**
For: the two-rail / harmonic-mean-AND / additive-OR architecture matches
the conductor square (11.1), and contradiction-as-high-resistance matches
non-explosive ⊤-localization; **a machine-checked formalization exists**
(EvidenceAsElectronics.agda and its CHL extension, App. A D-3) covering
the ℝ⁺ operations of chart 𝕄 and an ℂₛ s-plane AC generalization.
Against: whether the architecture satisfies the paraconsistent axioms
against the Priest/Belnap literature was flagged at review time and never
checked; the Agda modules postulate the foundational types rather than
deriving them. *Discharge path: check the axioms; the Agda modules give
the statements machine-visible form. If they hold, 11.7's lineage entry
promotes to a witness for §§5–6.*

**OB-7 — the Noether statement for the carrier. RESOLVED (clean two-pairing).**
A run initially called this inconsistent (the proposed continuous flow
conserved bias while the discrete pin-swap conserves mass); that was a
single-chart artifact — the wrong continuous partner was chosen. Corrected
under the adjunction (Lemma 2.5b), the structure is clean and complete:
there are **two one-parameter symmetry subgroups, each pairing an
involution with a continuous flow conserving the same axis:**

| involution | continuous partner | Noether charge | chart picture |
|---|---|---|---|
| pin-swap | squeeze (E₊,E₋)↦(eᵗE₊, e⁻ᵗE₋) | **mass** = E₊·E₋ | hyperbolic rotation |
| negate-a-pin | common translation (u₊,u₋)↦(u₊+t,u₋+t) | **bias** = E₊/E₋ | dilation |

Mass and bias are the two Noether charges of the two subgroups of
(ℝ⁺,×)² ≅ (ℝ,+)²; the squeeze fixes the dilation charge and vice versa.
The pin-swap (mass-conserving involution) pairs with the squeeze
(mass-conserving flow) — same axis, witnessed. *Status: resolved as a
clean pairing. The discrete pairing extends to a genuine continuous
(Noether) statement; the earlier "inconsistency" was a flow-choice error,
not a structural one.* **[W]**

**OB-8 — Thévenin/Norton as named external collapse.**
For: the move exists twice in the corpus unnamed (D-1's
equivalent-single-conductor shadow; D-13's Star-Mesh as reversible
level-conservation); Remark 3.5 supplies the governing discipline
(legal as instrument, forbidden as semantics); §11.6's Y-Δ is the
special case already witnessed.
Against: no corpus document derives the port abstraction for an
*evidence* network; the claim that Norton/Thévenin source duality is a
De Morgan-shaped swap is unverified; the relation between Star-Mesh
reversibility and the irreversibility of single-element collapse
(Lemma 3.2 at network scale) is unworked. *Discharge path: define the
port abstraction of an evidence network; verify what it conserves
(mass? bias? neither?) and bind it to the Star-Mesh transform.* **Machinery
(draft 7):** the Baez–Fong black-box functor (App. B, S-G) is exactly
"named external collapse as a functor" — Thévenin/black-boxing of an open
network to its port behaviour, proven functorial. Bind the evidence-port
abstraction to it rather than constructing from scratch.

**OB-9 — phase: where does it come from? (fully open; complexification retracted).**
For: the corpus works in ℂₛ (D-3) and carries complex semantic impedance
Z = R + jX (D-17); §11.5's dissipative/reactive split is suggestive of a
real/imaginary decomposition; §8's amplitude reading wants a phase.
Against: the obvious route — complexify the multiplicative chart — is a
**category error** (Caveat 2.4a): 1/y is the *semiring* involution, not a
field reciprocal, and signed quantities live in the additive chart, not
in an extension of 𝕄 to ℂ. So the "complexified atlas" framing is
withdrawn; phase has *no established origin* in the current structure.
OB-9 and OB-2 (phase composition) are both open and coupled. *Discharge path: construct the complex charts, check the
three structures, and state the phase-composition law or its
obstruction.* **Run RETRACTED as ill-posed (Caveat 2.4a).**
A first run complexified 𝕄 and reported a "second fixed point y=−1" and a
"unit-circle balance," concluding phase was the new DOF. That was a
category error: 1/y is the involution of the **semiring** [0, ∞], not a
reciprocal on a ring/field, and must not be extended to negative or
complex arguments — the signed quantities already live in the additive
chart (sign negation, fixed point 0), reached by log, not by
complexifying the semiring. There is no second fixed point and no
ambiguous neutral; the unit-circle result was an artifact of imposing a
field structure 𝕄 does not have. **Phase is therefore reopened as fully
open:** the spec makes *no* claim about where phase comes from. It is not
"the DOF exposed by complexification" (that scaffolding is withdrawn); if
phase enters at all it is a separate enrichment whose origin is
undetermined. Coupled to OB-2, which is likewise open. **Consolidated and resolved-as-type in §8.5–8.6:**
OB-2/OB-3/OB-9 are one object (the phase connection), three gradings; its value
group is **forced to be V4**, and it is **resolved as a dependent type** with a
fixed V4 interface and two pinnings (carrier/measurement and action/theorem), both
retained. The remaining freedom is the *pinning* — a declared model parameter
(upstream, like R), not an open obligation of the logic. Status: resolved-as-type;
no evaluation debt. Draft 13: the two pinnings identified as the two
representations (corner = exact V₄ + S₃ frame, Hol(V₄) = S₄ total; pin
plane = D₄ central extension, phase = extension class); the holomorph
candidate (re-pinnings compose as Aut(V₄) = S₃) is RESOLVED-WITNESSED.*

**OB-10 — the overlay theorem (Σ → Π promotion).**
For: the principle is stated and committed (12.1, user-origin); five
instances plus instance zero are enumerated with their S identified
(12.3); a candidate manifestation law exists (12.2, Mayer–Vietoris
shape) with hardware semantics (the galvanometer as the S-mismatch
reader) and a numerically witnessed modulation example (Sylow
factoring of the rung coupling).
Against: the category of (network, S-marking) pairs is not
constructed; the reasoning-space topologies have not been given the
complex structure Mayer–Vietoris requires (the cohomology theory is
unfixed); the source record's Σ-flag explicitly withholds the
identification of the instances as one object. *Discharge path: fix
the cohomology theory of a reasoning space; construct the overlay
category; verify or correct Law 12.2 on it; re-derive §11.2, §11.3,
and the rung theorem as corollaries of one pushout statement.*
**Machinery (draft 7, App. B, S-G):** the category need not be built from
nothing — **decorated cospans (Fong 2015; Baez–Fong 2018)** already give
networks-glued-along-shared-boundary as pushout, with functorial
semantics; **Hansen–Ghrist cellular-sheaf spectral theory (2019)** already
proves the manifestation law's shape — the sheaf-Laplacian kernel is the
global sections, and data vanishing on the relevant restriction maps is
not transmitted, which is precisely Candidate Law 12.2 including its
"vanishes on S ⇒ invisible" clause. Reframed task: define the
**evidence-sheaf** decoration on a cospan/cell complex, then 12.2 becomes
"verify the sheaf-Laplacian statement under this decoration," and the
genuinely original content localises to the *decorations and the instance
menagerie* (V₄ bindings, Sylow mediators), not the gluing machinery.

**OB-11 — the ○/● operators as carrier gates.**
For: the closest kin, LET_F (Rodrigues–Bueno-Soler–Carnielli, App. B,
S-B), supplies classicality (○) and non-classicality (●) operators the
EL-Atlas carrier lacks as named gates; the carrier has natural candidate
regions (○ ≈ the saturated-bias rails of Witness 7.5, where the state is
decided/classical; ● ≈ the high-mass-low-|bias| region of §4, where
conflict is live).
Against: the identification of ○/● with carrier regions is proposed, not
checked; the LET_F axioms for ○/● have not been verified against the
carrier semantics. *Discharge path (sharpened, §5.8f): define ○ = the c-degenerate
region (the inverse-locked locus ∪ the saturation rails) and ● = the
c-live region; check the LET_F axioms against these; if they hold,
position the spec as "LET_F's geometry" and import LET_F's completeness
results.*

**OB-12 — the channel product. RESOLVED (§13.2).**
The product is not in the doubling tower and was never supposed to be: a
single tower is a linear consumption mode (RM(1, m) by design, §13.1).
The bilinear product is **Mode 5, the overlay** — the pairing of two
towers at a shared instance, which produces degree-2 RM codewords
(witnessed). Climbing the Reed–Muller degree filtration = composing
overlays, not climbing the doubling recursion. The Cayley–Dickson search
looked on the wrong axis (the tree's recursion instead of the overlay).
*Status: resolved. Residual sub-question (optional, demoted): whether the
overlay pairing, iterated, reproduces a specific named algebra — but the
spec no longer needs it to, since the product has a home (§12).*

---

