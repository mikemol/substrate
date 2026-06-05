# Carrier-locality policy

A **Costco-grade invariant** (one grep-equivalent script, binary pass/fail,
zero content-sniffing beyond type-shape) that prevents the
*fork-by-reimplementation* class of structural risk — the kind the
similarity detector cannot catch, because two definitions of the same
operator via different primitives are *semantically identical but textually
dissimilar*.

Enforced by `scripts/check_carrier_locality.py` (blocking; wired into
`.githooks/pre-commit` and `make check` as `check-carrier`).

## The disease

`Substrate.Algebra.Q.Arithmetic` once defined its **own** `_+ℤ_` / `_*ℤ_`
(via `∸`/`<?`), definitionally distinct from the canonical
`Substrate.Algebra.Z.Arithmetic` ops (via `⊖`). The full ℤ ring laws proven
about the canonical ops (`Z.Properties.MulFull`) therefore **did not apply**
to the ops ℚ actually used — a silent correctness gap. Nothing flagged it:
the two `_+ℤ_`s look nothing alike textually, and both typecheck.

## The rule

A **canonical endo operator** — a mixfix name `_⊕_` whose type is `T → T → T`
(or `T → T`) over a **globally-unique carrier** T (a `data`/`record` declared
exactly once in the tree) — must obey:

1. **Locality.** It is defined in T's home: the file declaring T, or a file
   under T's home-directory subtree. An ℤ operator lives under `Algebra/Z/`,
   never under `Algebra/Q/`. *(This is the rule that catches the disease: you
   cannot define `_+ℤ_` outside ℤ's home, so the only option is to import it.)*

2. **Dedication.** A file may host operators over a carrier **it declares**
   (the `data ℕ` + `_+_`/`_*_` home file, named for the carrier). But a file
   aggregating **≥2 operators over foreign carriers** (declared elsewhere) is a
   generic *bucket* — the place forks hide, where the file name no longer
   identifies what is canonical. Bucket files are split one-operator-per-file,
   and the old name becomes a re-export **barrel** (so importers are unchanged).

**Uniqueness-gated.** Carriers whose name is reused locally (several modules
each declare their own `Word`) are ambiguous and skipped: two
`_·_ : Word → Word → Word` in different files are usually *different* `Word`s,
not a fork. Only single-global-declaration carriers are judged.

## What landed under this policy

`Algebra/Z/Arithmetic.agda` and `Algebra/Q/Arithmetic.agda` were generic
buckets. They are now **re-export barrels**; each operator lives one-per-file:

| operator | home file |
|----------|-----------|
| `_⊖_`, `_+ℤ_` | `Algebra/Z/Add.agda` |
| `_*ℤ_` | `Algebra/Z/Mul.agda` |
| `_-ℤ_` | `Algebra/Z/Sub.agda` |
| `-ℚ_` | `Algebra/Q/Neg.agda` |
| `_+ℚ_` | `Algebra/Q/Add.agda` |
| `_*ℚ_` | `Algebra/Q/Mul.agda` |
| `_-ℚ_` | `Algebra/Q/Sub.agda` |

The barrels re-export with `open import … public using (…)`, so the public
interface (`Substrate.Algebra.{Z,Q}.Arithmetic`) and its importers are
unchanged. Fixity declarations propagate through the barrel.

## Grandfathered (ALLOW set)

Pre-existing, cross-subsystem, and **not** forks; the gate blocks any *new*
violation but tolerates these (each documented in the script's `ALLOW`):

- `Algebra/Nat/Mod.agda::_mod-suc_`, `Algebra/Nat/DivMod/DivSuc.agda::_div-suc_`
  — derived ℕ arithmetic deliberately layered in `Algebra/Nat/`, not
  re-implementations of a `Foundation/Nat` primitive. (Relocating them would
  pull division into `Foundation`; a separate layering question.)
- `Groups/Zn-x-FreeCyclic-PhaseProjection.agda::_·_` — `_·_` over a **local**
  `Word` synonym (`Zn-Word × F-Word`), distinct from the Coxeter `Word`.
- `Groups/Coxeter/Core/Operations.agda::_·_` — the canonical Coxeter `_·_`
  (`= normalize ∘ ++`), historically in `Core/Operations` rather than `Word/`.
- `Algebra/GL3F2/Characters.agda::_ℤ` — `n ℤ = n`, a readability identity
  alias, not arithmetic.
- `Algebra/Wedge/Cross.agda::_⊗ᴰ_` — cross-construction wedge product, sited
  with the cross.

## Verification

- `python3 scripts/check_carrier_locality.py` — exit 0 clean / 1 offenders.
- Regression: reintroducing `_+ℤ_` (or any `T → T → T`) under `Algebra/Q/`, or
  aggregating ≥2 foreign-carrier operators in one file, exits 1.
