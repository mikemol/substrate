## 7. The range parameter ℛ — the document's named loop

This section fills the specification's single H₁ generator *as a
parameter contract*, and deliberately does not fill it as a value.

**Definition 7.1 (the parameter).** **ℛ** is the numeric range / saturation
behavior of each pin's carrier: unbounded log-carrier, or
bounded/saturating window, or a specific numeric window. ℛ is a **free
parameter of this specification.** An instance of the EL-Atlas is the
structure of §§1–6 together with a choice of ℛ.

**Contract 7.2 (constraints on ℛ, from both routes).** The two routes that
reach ℛ in the notion graph impose:

- **Route via the involution structure (§5):** *no constraint.* The
  log-odds-shaped carrier is forced, but nothing in the V₄ / inverse-lock
  structure fixes boundedness or a window. **[W]**
- **Route via the semiring (§6) and dynamics:** *saturation desiderata.*
  A bounded/saturating range is what makes a repeater stable
  (fade-resistance); choosing ℛ is simultaneously choosing the saturation
  regime of accumulation. **[W]** (flagged repeatedly in the source
  record as a design consideration, never derived.)

**Named instance candidates (corpus).** The corpus consolidation (App. A,
D-1 §C3) records concrete admissible instances of ℛ without privileging
one: the raw zero-based carrier **[0, ∞]²** (0 = no evidence) as default;
**[1, ∞]²** for purely positive multiplicative coordinates before logs;
and the **shifted embedding e ↦ 1 + e/κ** with l-space as an extended or
shifted log. Both raw and exponentiated carriers are allowed; the choice
is an instance declaration per Contract 7.2, not a resolution of it.
**[W]** (corpus-witnessed.)

**Coherence 7.3.** The two routes are consistent: ∅ (route one) is
compatible with any desiderata set (route two). The loop is thereby
*coherent as a contract* — both routes agree that ℛ is free and that
fade-resistance is the live design pressure — while remaining *open as a
value*. This is the intended permanent state: the framework is
paraconsistent precisely so that an open obligation can be carried without
infecting the rest of the structure. **[S]**

**Observation 7.4 (range as domain structure).** Choosing ℛ is choosing a
Scott-domain structure on the pin carrier: a saturating range gives
accumulation chains least upper bounds; an unbounded range does not. This
reframes the open parameter as a continuity/limit decision rather than a
mere interval pick. **[C]** — candidate observation from the
correspondence probe (§10), not derived in the source record.

**Witness 7.5 (saturation dynamics on the one-parameter chart;
re-scoped).** A range spec was worked on the multiplicative chart 𝕄 with
neutral 1 and rails 0 / +∞: NOT swaps the rails (1/0 = ∞, the
inverse-locked certainties); the rails are **absorbing** while the
neutral is **unstable** — consistent accumulation drives to a rail and
the rail pins the decision. Fade-resistance = drive to saturation; the
bounded-at-rails range is exactly what makes a decision hold (the
repeater mechanism). **[W]** for the dynamics — with a mandatory scope
restriction: in the source record this was first read on the odds axis
x = E⁺/E⁻ and then superseded by the no-collapse correction (Provenance
P-1); a single such axis sees bias only and collapses B and N to the same
point. The witnessed dynamics therefore attach to the **one-parameter
chart / the external decision projection**, not to the carrier pair. They
constrain ℛ's saturation regime without fixing the per-pin accumulator
range; the specific potential, measure, and critical drive remain the
user's design (OB-1). **[S]** for the re-scoping.

---

