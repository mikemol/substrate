---
name: feedback_derive_dont_duplicate_single_source
description: "To connect an F₂-specific (or any concrete) instance to a generic construction, DERIVE the instance from the generic (single source) — NEVER build both independently then prove them equal. Duplicated structure is un-bridgeable in this repo: cross-module duplicate defs aren't defeq when stuck, and function-valued record equality is funext-blocked."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

The recurring blocker that left `Ⓐ.gfinv-generic` incomplete across attempts (2026-06-25): building a
generic construction (e.g. `Graded.PolyDivWedge`) AND the F₂ instance (`PolyDiv`) **independently**, then
trying to prove `F₂-instance ≡ generic-instance`. That equality CANNOT be discharged here, two ways at once:

1. **Cross-module duplicate defs are not definitionally equal WHEN STUCK.** Two functions with identical
   bodies but different names (`PolyDiv.buildPoly` vs `PDW.Over.buildPoly`) only reduce on concrete
   constructors; on a SYMBOLIC argument a recursive function is stuck at its head symbol, and two distinct
   stuck head symbols are not defeq → `refl` fails (`buildPoly … != PDW.Over.buildPoly …`).
2. **Record equality of a function-valued structure is FUNEXT-BLOCKED.** Even bridging `buildPoly` by an
   inductive lemma, `Poly-div ≡ PDW.Poly-div` is equality of `DivStr` records whose `recon` field is a
   FUNCTION — needs `recon ≡ recon` as functions = funext, which the repo (`--safe --without-K`, no funext)
   forbids.

**So duplicated structure is un-bridgeable: not by `refl` (non-defeq) and not by proof (funext).**

**The ONLY resolution: SINGLE SOURCE — derive the instance from the generic.** Make the concrete module
`open Generic.Over <params>` and DELETE its local copies, so the instance IS the generic at those params
(one symbol → `refl` trivial / no bridge needed). The cost is a cascading refactor of the concrete module;
do it incrementally behind the full-build gate. This is [[single-source-truth]] meeting the funext-free
constraint ([[safe-without-k-zero]]); it is the closure-obligation of the Total-Space thesis realized
correctly — face-agreement comes from SHARED DEFINITION, not post-hoc equality of independently-built faces.
Contrast `package-comm`, which bridges packagings via the universal property (∃!-uniqueness), NOT
record-equality — that route works *because* it never asserts a function-valued `≡`.

**How to apply:** the trigger is "I built a generic X and an instance Y; now prove Y ≡ generic-X." STOP —
that's the un-bridgeable pattern. Instead derive Y from generic-X (single source). If you cannot refactor Y
(committed/risky), the generic X is premature — build the generic + its first real CONSUMER together, or
make Y derive from X as the same commit. Never leave a generic imported-by-0 expecting a later `refl` bridge.
