## 12. The overlay principle

Committed to a document here for the first time. The principle is
user-origin and is the generative move behind §2, §11.2, §11.3, and the
rung-coupling result in the source record; until this draft it existed
only as practice.

**Principle 12.1 (overlay).** **[W]** (user-origin statement, this
draft):

1. Construct a **pair of networks** N₁, N₂ such that both contain a
   **common structure** S — a span of embeddings N₁ ↩ S ↪ N₂.
2. **Characterize the topology of the reasoning space** of each network
   separately.
3. **Overlay** the networks so the shared structure is a common
   **instance** — not two isomorphic copies but one object: the gluing
   N₁ ⊔_S N₂ (the pushout along the span).
4. Then **computations in one network manifest in the other network,
   characterized by the common structure.**

The force of step 3 is the difference between isomorphism and identity:
two copies of S related by an isomorphism transmit nothing by
themselves; *identifying* them creates the channel. The choice of
identification is itself structure (§11.2: six choices for V₄, two
flat, four twisted) — the "forced correspondence," and its structure
modulates the transmission.

**Candidate Law 12.2 (the manifestation law).** **[S]** — synthesis,
stated for verification, not assumed: on the overlay, the transmission
of computation has the shape of **Mayer–Vietoris**. What can manifest
across the gluing is exactly what restricts nontrivially to S; the
connecting homomorphism through S *is* the transmission channel; the
topology of S bounds the transmissible classes — H(S) as the channel
capacity of the correspondence. Contrapositive, which is the testable
edge: **a deformation whose restriction to S vanishes is invisible to
the other network.** The galvanometer (§11.3) is this law as hardware —
it reads precisely the mismatch of the two arm-networks' restrictions
to the shared crossbar, and reads zero when they agree on S.

**Instances 12.3, regraded under the principle.**

- **Instance zero: the atlas itself (§2).** Charts 𝔸 and 𝕄 are two
  networks containing the same value space; exp/log performs the
  overlay (the value space as common *instance*, not two copies);
  Lemma 2.4 / Remark 2.5 transport is the manifestation. The
  construction this document specifies is the principle's first
  application to itself. **[S]**
- **The flat-binding theorem (§11.2).** S = V₄. The identification
  choice is the modulation structure: flat identifications (De Morgan
  preserved) transmit without twist; the other four transmit a twist.
  **[W]** as restated.
- **The Wheatstone bridge (§11.3, §11.6).** S = the crossbar. The two
  arm-networks overlay on it; deflection is the S-mismatch; balance is
  the two networks agreeing on S — at which point S vanishes from the
  conserved quantity entirely (§11.6), the channel carrying nothing.
  **[W]** as restated.
- **The rung-coupling theorem (source record, June 6; not previously
  in this spec).** Adjacent rungs of the generator tower are each
  intrinsically contractible — every simplex cone fills its own holes;
  **degeneracy is never intrinsic to a rung and appears only when two
  rungs couple.** The coupling form is S; its Pfaffian vanishes on a
  real locus (the forbidden corner at every rung). Direct coupling
  transmits deformation as a ripple tracking the Pfaffian exactly;
  **factoring the identification through Sylow-prime mediators
  modulates the transmission spectrally** — mediate every prime of the
  symmetry order and the residual is zero (constant velocity); drop a
  prime and that prime's frequency transmits as residual ripple. A new
  irreducible mediator is forced exactly when n+1 is prime. **[W]**
  (numerically witnessed in the source record) — the fullest worked
  example of step 4's modulation clause.
- **The phantom hierarchy (§11.10).** Adjacent levels overlay on the
  common-mode structure; what level n cannot read transmits to level
  n+1 through exactly that shared structure. **[S]**
- **Interfaces (§11.10, D-23).** An obligation-as-port is a
  *designated S awaiting its second network*: the register's open
  items are pre-positioned overlay sites. **[S]**

**Remark 12.4 (the Σ → Π path).** The source record's honesty flag
stands: the instances above share a pattern but live in different
categories — three instances, not one theorem (Σ, not Π). The overlay
principle names what a Π-promotion requires: construct the category of
(network, S-marking) pairs in which each instance is a pushout along
its S, and the pattern becomes one theorem with §11.2, §11.3, and the
rung result as corollaries. Until that category is constructed and
Candidate Law 12.2 is verified or corrected on it, the Σ grade is the
honest one: **OB-10.**

---

