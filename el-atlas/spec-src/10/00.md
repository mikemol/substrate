## 10. Correspondences (related structures, classified)

Per the probe discipline: **nothing here is claimed Present** — no
internal witness in the source derivation *names* a canon correspondence.
All entries are Implicit (witness-functor sketched) or Candidate (sharp
test available). These are the spec's test surface.

**Implicit:**

- **Dialectica (de Paiva).** F maps (E⁺, E⁻) to Dialectica-style objects
  of (proofs, challenges); the for/against pair has exactly the
  two-sided object shape. Test: does pin-swap match Dialectica
  dualization on composites? This cleaves "evidence algebra" from
  "decision algebra."
- **Chu.** F maps the carrier to a Chu object with NOT as the Chu duality
  involution; pin-swap = dualization. Test: NOT∘NOT = id and De Morgan
  via Chu duality, checked mechanically.
- **Martin-Löf (transport).** F: charts ↦ types, exp/log ↦ equivalence;
  "same object, two charts" ↦ transport along the equivalence
  (Remark 2.5). Test: prove a law in 𝔸, transport, verify the 𝕄 form —
  Lemma 2.4 is the first instance.
- **Girard (polarities).** F: pins ↦ polarized formulas; the no-collapse
  law as refusal of contraction on the pair. Test: which structural rules
  survive on each pin separately vs on the pair.
- **Kleisli (writer).** F: each pin ↦ a writer monad over its additive
  monoid; accumulation = bind. Test: associativity/unit of accumulation
  as monad laws, per pin, guarding against cross-pin leakage (Law 1.3).

**Candidate:**

- **Scott (domains).** Choosing ℛ = choosing the domain structure on the
  pin carrier (Observation 7.4). Highest-yield candidate: it cleaves
  exactly along the document's open loop.

---

