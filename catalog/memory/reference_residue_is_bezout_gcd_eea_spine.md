---
name: reference_residue_is_bezout_gcd_eea_spine
description: "The CrossMix cross-term residue is governed by the Bézout GCD; the substrate's constructive EEA/Bézout/CRT spine is the engine for all cross-carrier split/reconstruct/residue work. Reuse it — don't treat coprimality as awkward."
metadata: 
  node_type: memory
  type: reference
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

The cross-carrier coherence picture (CrossMix / HetQ / the cyclotomic tower's F₂↔ℚ residue) sits on the substrate's **constructive EEA/Bézout/CRT spine**. The governance (machine-checked in `Logic/Evidence/ElAtlas/ResidueIsBezoutGCD.agda`):

- **gcd ≡ 1 (coprime) ⟺ ORTHOGONAL** — the CrossMix cross-term vanishes (CRT-clean). The CRT idempotents `e₁,e₂` (`CenterIsStarCRT`, ℤ/6 = ℤ/2×ℤ/3) ARE the codec legs; `coprime-trace a b refl : EEATrace a b 1` is the Bézout/EEA certificate of the clean split.
- **gcd > 1 (shared factor) ⟺ graded RESIDUE** — the cross-term is a nonzero nilpotent (`CenterIsStarNumeral`, ℤ/2³, `cross 2 2 ≡ 4`). The residue is the gcd's deviation from 1.

So a coprime/orthogonal decomposition is the **CRT-clean case**, NOT an awkwardness (user, 2026-06-25) — and EEA gives both the split (gcd) and the reconstruction (Bézout coefficients → idempotents → codecs).

**Machinery to REUSE (don't reinvent):**
- `Algebra.Nat.GCD.GcdN.gcd-ℕ`, `GcdTrace.gcd-trace : (a b) → EEATrace a b (gcd-ℕ a b)`, `coprime-trace : gcd-ℕ a b ≡ 1 → EEATrace a b 1`, `GCD.EEATrace` (Euclid recursion as data).
- `Algebra.Z.Bezout.bezout-ℤ` (s·x+t·m≡1), `Algebra.Z.Euclid.euclid` (Euclid's lemma via Bézout), `Nat.GCD.CFInjective` (coprime + cross-mult ⟹ equal).
- `Algebra.Wedge.CrossMul` (CrossMix cospan, cross-term = graded nilpotent residue); the worked numeral examples `CenterIsStarCRT` (orthogonal) + `CenterIsStarNumeral` (residue).

**How to apply:** for any cross-carrier split / "differently-basised" quotient / reconstruction / residue task, the gcd is the residue gauge and EEA/Bézout is the engine — instantiate it, don't hand-pick numerals or declare coprimality awkward. Connects [[reference_Q_is_a_setoid_not_propositional]] (the ℚ side), the Ⓗ bridge family and Ⓕ.tower-crossmul-residue in [[project_open_threads]], and the [[feedback_wall_can_wear_a_negative_theorem]] correction (the residue is carried, paraconsistently, not walled).
