## 1. The carrier: two independent accumulators

**Definition 1.1 (evidence increments and totals).** Distinguish two types:

- An **increment** ε ≥ 0: one finding, for or against.
- A **total** E ≥ 0: an accumulated quantity of increments.

The accumulation operation has signature `increment × total → total`.
Increments and totals are not interchangeable; an English sentence that
says "evidence" must resolve to one or the other. **[W]** (forced by the
place-structure cross-check; "evidence" is mass-noun ambiguous and the
spec is not).

**Definition 1.2 (the carrier).** The carrier of the logic is a pair

> **(E⁺, E⁻)**

of totals: E⁺ accumulates evidence-for, E⁻ accumulates evidence-against.
Also written (t, f) in earlier derivations. The pair lives in the quadrant
[0, ∞]². **[W]**

**Law 1.3 (independence).** E⁺ and E⁻ are two *independent additive
accumulators*. Each pin accumulates by summing its own increments. They are
not the numerator and denominator of anything. No operation of the logic
reads one pin while writing the other. **[W]**

**Law 1.4 (accumulation is sum; the sum is a choice of operation).**
Accumulation on a pin is additive in whatever carrier presentation is in
use. "Logspace sum" versus "semiring sum" (ordinary +, or a semiring ⊕
such as max or logsumexp) is a *choice of which sum* — both constructible,
neither canonical. There is no underlying multiplication being linearized;
the log is one constructible view, not a forced bridge. **[W]** (this
corrects an earlier error; see Provenance, P-2).

**Interpretive regions** (regions, not posited labels — see §4, §9):

- E⁺ high, E⁻ low: supported.
- E⁺ low, E⁻ high: refuted.
- both high: active disagreement — high instability, highly curved local
  space (§8).
- both low: lack of knowledge.

**[W]**

---

