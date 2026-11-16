---
name: ""
metadata: 
  node_type: memory
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

When the assistant identifies a task as "blocked by heavy stdlib dependency"
(Data.Fin.Permutation, Data.Nat.DivMod, etc.), DEFAULT TO ROLLING OUR OWN
via the substrate's existing paradigms — DO NOT classify it as blocked.

**Why:** The substrate has its own algebra-as-discipline infrastructure:
* Coxeter Word framework (Word / Canonical / insert / normalize) handles
  cyclic / finite-group structure natively.
* `Substrate.Groups.Z3-Coxeter` already demonstrates the pattern at n=3:
  explicit `Canonical` constructors per element, `insert` wraps around,
  `cube-identity` witnesses the order relation. Per-n instances are
  small and structurally uniform.
* The canonical-form discipline gives efficiency: operations reduce
  in O(canonical-length) not O(input-length). Multiplying k copies
  and normalizing tracks length mod n, not the literal k-fold expansion.
* The substrate is being built coalgebraically (per
  [[feedback-coalgebraic-not-consumer-driven]]); rolling our own
  matches the substrate's gauge-unfold discipline rather than
  importing stdlib's hidden gauge choices.

**How to apply:** When tempted to write "blocked: needs Data.X.Y":
1. Check if the substrate's own paradigm already covers this. The
   Coxeter Word framework, Vector universal-property combinators,
   linear-from-images, basis-permutation-Linear, etc., are the
   substrate's native tools.
2. If yes: propose the substrate-native solution as a new slice arc,
   not as "blocked."
3. If no obvious native paradigm: propose one in the substrate's
   style (small per-instance constructions, canonical-form discipline,
   universal-property layering).

**Connections:**
* Refines [[feedback-minimize-stdlib-deps]] — that memory was right
  about not pulling in heavy stdlib, but conflated "don't import" with
  "can't do." The right pattern is "don't import; roll our own."
* Aligns with [[feedback-composable-primitives-over-flat-enumeration]]
  — the Coxeter Word's per-instance Canonical + insert is exactly
  the "composable primitive" pattern; each new Zₙ instance is a
  small refl-per-case file mirroring Z3-Coxeter.
* Aligns with [[feedback-coalgebraic-not-consumer-driven]] — rolling
  our own unfolds the gauge structure on substrate terms.

**Worked example:** Generic cyclic-shift on Fin n. Substrate-native
approach:
* Per specific n: write `Zₙ-Coxeter` (small file mirroring Z3-Coxeter)
  with explicit Canonical constructors c-ε, c-a, c-aa, ..., c-a^(n-1)
  and `insert` wrapping at length n. The cyclic-shift on Fin n is
  the bijection Z/n ↔ Fin n via canonical-word length.
* Generic-over-n: `Canonical w` parametrised by `Fin n` (length-
  indexed), `insert` defined inductively. The "efficiency" is that
  `(a · a · ... · a)^k` normalises to `a^(k mod n)` via the
  Coxeter framework's `normalize`, not via Data.Nat.DivMod.
