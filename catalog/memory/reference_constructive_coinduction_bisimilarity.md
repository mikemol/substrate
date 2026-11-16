---
name: reference_constructive_coinduction_bisimilarity
description: "Substrate is CONSTRUCTIVE-only, INCLUDING coinduction: codata equality is BISIMILARITY (~), proved by guarded corecursion (--guardedness), NEVER ≡-via-funext or classical. The cata/ana duality is ≡/~ asymmetric."
metadata: 
  node_type: memory
  type: reference
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

The repo does ONLY constructive proofs (--safe --without-K, zero postulates, no LEM, no funext) — and this **extends to coinduction** (user, 2026-06-26: "even our coinduction, we prove constructively"). Concretely:

- **Codata equality is BISIMILARITY `_~_`, not `_≡_`.** You cannot prove two streams/coinductive values propositionally equal without funext (absent). So the coinductive universal properties are stated up to `~`: `R.Trace.Final.ana-unique` concludes `h s ~ ana c s` (NOT `≡`); `qToRℚ-unique` likewise. The bisimulation is a coinductive record (head-equal + tails-bisimilar).
- **Proved by GUARDED CORECURSION** (`--guardedness`, infective), via copatterns + witness-threading: thread a `t ≡ h s` witness into a helper, consume with `refl` at copattern time, put the corecursive call DIRECTLY under the `~` constructor. Do NOT use `cong`/`trans` on `~` (breaks guardedness). See [[reference_uniqueness_proof_family_idiom]] for the contrast with the inductive idiom.

**BUT the EEATrace model recovers `≡` — by comparing the finite GENERATOR, not the stream** (user, 2026-06-26: "that's what our EEATrace model is supposed to get us"). You can't get `≡` by comparing coinductive *values* directly (needs funext) — but you never do: represent the value by its finite inductive CF trace and compare THAT with `≡` (decidable). Verified mechanism: `WitnessTower.EEATower.tower-reconstructs : reconstruct t ≡ (a,b)` (the trace `≡`-recovers its rational), `Nat.GCD.CFInjective.cf-injective : ℕ-shape t₁ ≡ ℕ-shape t₂ → (n₁≡n₂)×(b₁≡b₂)` (the CF shape is INJECTIVE on coprime fractions ⟹ value-equality is DECIDED on the trace), `RationalAdjunction.unit-3/2 : convergent 2 (qToR 3 1) ≡ (3,2)` (round-trip `≡`-exact). So: SYNTAX (EEATrace) carries `≡`; SEMANTICS (RealTrace) carries `~`; `cf-injective` bridges them. `~` is forced ONLY when comparing UNFOLDED streams without a generator. The model shrinks the `~`-only boundary to the genuinely-non-finitely-generated.

**The cata/ana duality is NOT equality-symmetric for DIRECT value comparison** — and that asymmetry IS the constructive content (but the EEATrace generator-route above escapes it whenever a finite generator exists):
- INITIAL side (data, induction): `cata`/`eea-fold`/`trace-fold` uniqueness is up-to-`≡` (`eea-fold-unique`, `trace-fold-unique`).
- TERMINAL side (codata, corecursion): `ana` uniqueness is up-to-`~` (`ana-unique`).

**Design consequence for Ⓤ.cata-unique-generic** (generic initial/terminal-algebra layer on `Category.Poly`): it must carry the equality PARAMETRICALLY — `≡` on the μ/cata side, a generic bisimilarity `~` (definable constructively over `⟦ P ⟧`) on the ν/ana side, with the corecursive proof guarded. The terminal coalgebra `ν P` (M-type) is fine constructively as codata; just never collapse `~` to `≡`. Sibling of the [[reject-lem-substrate]] / [[safe-without-k-zero-postulates]] apexes — this is the coinductive corner of that constraint.
