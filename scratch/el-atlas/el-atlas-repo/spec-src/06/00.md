## 6. The semiring: two operations, log-linked

**Definition 6.1 (the two operations).** The carrier of the connectives is
a semiring with two operations related through the log:

- **AND ~ sum-of-logs** (log-product): the multiplicative-dominant
  operation; the (+, ×) face.
- **OR ~ log-sum-exp** (soft max): the additive-dominant operation; the
  (max, +) tropical limit.

NOT negates the log carrier (u ↦ −u) = inverts (y ↦ 1/y) = swaps pins.
Under NOT, log-sum-exp and log-product exchange — which *is* De Morgan:
negating the log axis turns the product (sum of logs) into the dual
co-product (inverse-weighted sum). **[W]**

**Remark 6.2 (why two operations are forced).** By Theorem 5.3(2): a
single operation under inversion is self-dual and collapses the
∧/∨ distinction. The semiring is not a flourish; it is the minimum
structure under which NOT has something to exchange. **[W]**

**Remark 6.3 (which semiring is open).** The *shape* — log-sum-exp /
(+, ×) duality — is forced by "additive accumulation + inverse-locked
locus + involutive NOT." The *specific* semiring instance (which precise
⊕, and the numeric window it acts on) is part of the range contract, §7.
**[W]**

**Remark 6.4 (the physical instance).** The two operations have a
realized physical instance in resistor networks: series combination adds
resistances; parallel combination adds conductances (1/R = 1/R₁ + 1/R₂).
See §11.1 — the conductor square is this section's semiring duality as
hardware, with De Morgan as the law-preserving diagonal. **[W]**

---

