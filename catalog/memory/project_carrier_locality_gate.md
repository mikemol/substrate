---
name: project_carrier_locality_gate
description: carrier-locality CI gate + ℚ-ops unification + ≈ℚ setoid/field-laws arc (2026-06)
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

The Q/Z fork (ℚ defined its OWN `_+ℤ_`/`_*ℤ_` via `∸`/`<?`, definitionally ≠
canonical `Z.Arithmetic` via `⊖`, so `Z.Properties.MulFull` laws didn't apply)
drove a three-part arc:

1. **Unification** — `Q/Arithmetic` now imports canonical ℤ ops; all ℚ
   consumers green (incl. Capstone refl smoke-tests).
2. **≈ℚ setoid + field laws** — `Algebra/Q/Equiv.agda` (`_≈ℚ_`
   cross-multiplication as `Algebra.Quotient` — reuses the wedge/ModN
   machinery; built `Foundation/Nat/Properties/Cancel` + `MulFull`
   `*ℤ-cancelʳ-pos`/`*ℤ-swap₂₃` for ≈-trans). `Q/Properties/Field.agda`:
   **11 of 14** laws over ≈ℚ incl. the inverses (TRUE over ≈ℚ, syntactically
   FALSE over `≡`: 0/b²≢0/1). REMAINING 3 = `+ℚ-assoc`, `distribˡ/ʳ` (long
   nested cross-mult; recipe noted in-file). KEY agda trick: record-eta unifier
   stalls — pattern-match `mkℚ` for explicit args; ASCRIBE `≈ℚ`-typed hyps to
   their `≡` form before `cong`; build `Quotient` records ModN-style
   (`λ {a}{b} → …`).
3. **Gate** — `scripts/check_carrier_locality.py` (blocking; in pre-commit +
   `make check` `check-carrier`, target added to `gen_build_makefiles.py`
   GENERATOR since the top Makefile is generated). Rule: a canonical ENDO op
   (`T→T→T`/`T→T`, mixfix) over a GLOBALLY-UNIQUE carrier T must be (1) LOCAL
   (in T's home dir subtree — catches `_+ℤ_` under `Algebra/Q/`) and (2)
   DEDICATED (a file may host ops over a carrier IT DECLARES, but ≥2
   FOREIGN-carrier ops = a bucket to split). Uniqueness-gate skips
   locally-redefined names (Word, V₄). Forced the split of `Z/Arithmetic` →
   `Z/{Add,Mul,Sub}` + barrel and `Q/Arithmetic` → `Q/{Neg,Add,Mul,Sub}` +
   barrel (re-export `open … public using`, fixity propagates, importers
   unchanged). 6 grandfathered in ALLOW (mod-suc/div-suc derived-ℕ, Word `_·_`
   ×2, `_ℤ` alias, `_⊗ᴰ`). Full policy: scratch/carrier_locality_policy.md.

ASIDE: pre-existing def/proof violation in
`Algebra/Wedge/Graded/MonoidalAdjunction.agda` (Track-A arc, orthogonal — NOT
from this arc). See [[feedback_choice_rigidification_in_substrate]],
[[discipline/feedback_common_substructure_recursively]].
