# `BinTrim` — the exact grade, recovered

⟡nat-fin-rebase N1. A numeral's TYPE index is a PREDICTED width; `Trim` reads
back the width it actually needs, and the difference is the wedge residue.

## Why this exists

Every arithmetic signature must PREDICT its result width before computing:

    add : Bin n → Bin n → Bin n × Bool        (carry-out = the +1)
    mul : Bin m → Bin n → Bin (m + n)         (widths ADD)

Those indices are UPPER BOUNDS, never exact: `mul` at m = n = 8 types its
answer at 16 bits even when the product is 3. So the carrier splits in two —

- the PREDICTED width = the type index `n`  (sound by construction)
- the ACTUAL width    = the tight grade `e` (read back by `trim`)

and `n − e` is the slack. That IS the wedge `a = recon q b r` once more: the
tight form is the quotient, the leading zeros are the residue, and neither is
discarded — the numeral keeps both, graded.

## Why this is the payoff, not bookkeeping

A machine-word carrier must ASSERT `predicted ≥ actual` at runtime — the
sibling implementation does exactly that, at five independent sites, because
nothing in its types can carry the claim. Here the SAME statement is
`Trimmed`'s `fits` field, discharged by `s≤s`/`z≤n` in the two lines that
build it. The runtime assertion becomes a construction; that is the whole
reason the width is a type index and not a stored integer.

## Shape ported from `F2/Polynomial/Wedge/Trim.agda`, machinery deliberately not

That module trims trailing zeros at the SAME carrier shape
(`Poly n = Vec F₂ n` ≅ `Bin n = Vec Bool n`, both two-element digits) and
states the same three-part certificate: is-zero ∣ top-digit-nonzero ∣
value-equal. Its header names the design choice this folder inherits verbatim
— *"STRUCTURAL recursion on the length … NOT a `leading-position : Maybe ℕ`
read, so no dependent-length friction."*

What does NOT port is its RECURSION DIRECTION, and that is a real saving.
`Trim` strips from the MSB end, so it needs `vlast`/`vinit`/`snoc` plus
`nth-snoc-zero` — none of which exist for a plain `Vec`; they live inside
`Graded.Mod.Core.Over` / `Graded.Div.Over`, whose closure is exactly what this
arc is trying not to pay for. Recursing LSB-first instead (morton's own
convention, and the same direction `AddU` already runs) needs only `Msb`, and
no telescope at all: the tail is trimmed first and the head is consed back on.
Same certificate, none of the closure.

And the correctness is simpler here. `Trim` must state coefficient-wise
agreement (`(k) → nth rr k ≡ nth r k`) because a polynomial IS its
coefficients. A numeral has a VALUE, so the certificate is the single equation
`value t ≡ value b` — discharged at every step by one `cong` through the
Horner step that `Bin.ValueRecon` already proved is the graded reconstruction.

## Scope, honestly

This recovers the exact grade and certifies the bound. It does NOT prove
CANONICITY (that two tight numerals of equal value are equal) and does NOT
package a `Canonical` record. The reason is structural and worth stating
rather than discovering later: `Algebra.Quotient`'s `idem-Canonical` wants an
ENDO `e : A → A` with `e (e a) ≡ e a`, but `trim` CHANGES THE GRADE — its
result does not live in `Bin n`. The canonicaliser is therefore an endo on the
FLAT carrier `Σ ℕ Bin`, not on any fixed rung, and that packaging is a
separate construction. Claiming it here would be claiming a term that does not
typecheck.
