---
name: reference-q-is-a-setoid-not-propositional
description: "substrate's ℚ is a SETOID (≈ℚ, cross-multiplication), NOT propositional-≡: its ≡ field-laws are uninhabitable. Any ℚ-carrier work must be over ≈ℚ."
metadata: 
  node_type: memory
  type: reference
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

The substrate's **ℚ (`Algebra.Q`) is `mkℚ (num : ℤ) (denom : ℕ)` — raw, UNREDUCED fractions**, and its true equality is the **setoid `_≈ℚ_`** (cross-multiplication, `Algebra.Q.Equiv`), NOT propositional `_≡_`.

- The `≡`-typed field laws exist only inside `Q.AsField.ℚ-Field-Obligation`, a record whose header states **no instance can ever be constructed**: the additive-inverse fields are *syntactically false* over `≡` ((-ℚ a) +ℚ a reduces to `0/(suc d)² ≢ 0/1` as records — denominators differ). So you CANNOT extract usable `≡`-typed `+ℚ-assoc/comm/identity` from it.
- The usable, fully-discharged laws live in **`Q.Properties.Field`** over `≈ℚ` (all 14: `+ℚ-assoc`, `+ℚ-comm`, `+ℚ-identityˡ/ʳ`, `*ℚ-…`, `distribˡ/ʳ`, …), with congruences in `Q.Properties.Congruence` (`+ℚ-cong`, `*ℚ-cong`). The project is mid-migration "to the ≈ℚ setoid ladder."
- The project **lives and breathes in continued fractions** (user, 2026-06-24), and uses ℚ to structure them — so `≈ℚ` is load-bearing, not incidental. Raw/unreduced is the point; `reduce` + `≈-canonical` handle canonicalization.

**Consequence (load-bearing).** Any construction with a ℚ carrier — linear maps, modules, vectors, the cyclotomic operator — must be stated and proved over **`≈ℚ`** (or its pointwise vector lift `≈ℚⱽ`, which is NOT yet built as of 2026-06-24), never `≡`. A `≡`-based abstraction does not instantiate at ℚ. This is why [[project_open_threads]]'s Ⓕ.tower-ℚ-inst made `Algebra/Linear/CyclotomicOver` **setoid-parametric** (`_≈_` a parameter): F₂ takes ≈ = ≡ (decidable, a degenerate setoid), ℚ takes ≈ = ≈ℚ. The equality-regime difference (F₂ `≡` vs ℚ `≈ℚ`) IS the F₂↔ℚ axis the CrossMul bridge formalizes. Contrast F₂ (`Algebra.F2`), which is genuinely `≡`/decidable. Sibling structural fact for the [[structural-scalar]] / linear-algebra carriers.
