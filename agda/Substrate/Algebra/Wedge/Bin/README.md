# `Bin` — the binary numeral as a graded wedge

⟡nat-fin-rebase N0. **This folder constructs almost nothing.** It is a naming
and a tie. A reuse-search caught a near-reinvention: a bespoke
`data BinP : ℕ → Set` with `nil`/`_◂b_` and a `GradedDivStr BinP (λ _ → Fin 2)`
was written and then DELETED, because all three of its parts already exist:

| the near-reinvention | the generator it specialises |
|---|---|
| the carrier + wedge | `vec-graded : (A : Set) → GradedDivStr (Vec A) (λ _ → A)` (`Algebra.Wedge.VecGraded`) — `recon` IS cons, `refl` at VARIABLE operands, generic in `A`. `BinP` was `Vec Bool` respelled. |
| the analysis direction | `vec-uncons` — every nonempty vector IS its head consed on its tail; total, `refl`, no certificate to discharge (the bound lives in the digit's type). |
| the value | `morton : Vec Bool n → ℕ` (`Algebra.CayleyDickson.Curve`) — the LSB-first Σ bitᵢ·2ⁱ. |
| "the constant-radix instance of our own tower" | `WitnessTower.SnVersusTwoPowTowers` already names Ⓣ₁ = `tower-graded` (factoradic) beside Ⓣ₂ = `vec-graded Bool` (constant radix) as a COVERING co-apex. |

**What is genuinely new** is one equation nobody had stated — `ValueRecon`:
the graded reconstruction and the numeral value are the SAME radix-2 step,
`value (recon n bs b) ≡ boolToℕ b + (value bs + value bs)`, holding by `refl`
for VARIABLE operands. That is what makes division BY THE RADIX total with a
definitional certificate: `BinDivmod2` is `vec-uncons`, and its value-level
reading is the wedge equation itself.

**Scope.** Division by the RADIX, not by an arbitrary divisor.

**Not the F₂ vector carrier.** `Algebra.F2.Vector`'s `Vector n = Vec F₂ n` has
the same SHAPE and different STRUCTURE: its `_+ⱽ_` is carry-free XOR
(polynomial coefficients), whereas a binary NUMERAL adds with carry.
