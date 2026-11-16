# Substrate.Algebra.F2.AES — the verified AES-128 capstone (AI-19)

`--safe --without-K`, zero postulates throughout.

This index was the docstring of `AES.agda`, a module that defined **nothing** and
consisted entirely of ten `public` re-exports. That file was a barrel — a name whose
home the consumer cannot see — and the import ban retires it. The census recorded
**zero importers**, so nothing reached these theorems through it; every consumer was
already citing the real homes directly.

⚑ The index itself was worth keeping, and it is the reason the barrel survived as long
as it did: the *documentation* was load-bearing while the *conduit* was dead. Separating
them is the paydown — prose belongs in a README, which costs no compile and forwards no
names.

Cite these modules directly.

## The field

| theorem | home | tag |
|---|---|---|
| `GF2⁸-Field : Field (Poly 8)` — GF(2⁸) = F₂[x]/(x⁸+x⁴+x³+x+1) | `Polynomial.Wedge.AsField` | AI-8 |

## The layers — each inverse undoes its forward map

| theorem | home | tag |
|---|---|---|
| `sbox-rt : inv-sbox (sbox a) ≡ a` — SubBytes | `Polynomial.Wedge.SBoxTable.Properties` | AI-10 |
| `mixcolumns-round-trip : inv (mix col) ≡ col` — MixColumns | `MixColumns.Proof` | AI-9 |
| `round-rt : inv-round k (round k s) ≡ s` — the round | `AES.Round.RoundTrip` | AI-11 |
| `final-round-rt` — the final round, no MixColumns | `AES.Round.RoundTrip` | AI-11 |

`sbox` itself is the canonical table S-box (= the GF-inversion S-box, proven by
`SBoxTable.Properties.sbox≡gf`): cheap to force, FIPS rigor preserved.

## The cipher — `decrypt ∘ encrypt ≡ id`

| theorem | home | tag |
|---|---|---|
| `cipher-rt : decrypt ks (encrypt ks s) ≡ s` — round keys | `AES.Cipher.RoundTrip` | AI-12c |
| `cipher-key-rt : decrypt-key key (encrypt-key key s) ≡ s` — master key | `AES.KeySchedule.RoundTrip` | AI-12k |

## FIPS-197 correctness

The verified construction **is** the standard, not merely self-consistent. These are
concrete reflections (slow to normalise), which is why they live in their own modules:

- `Polynomial.Wedge.SBoxTable.Properties.sbox-is-aes` (AI-7s) —
  `byte-val (sbox a) ≡ AES-SBOX[byte-val a]` for all `a`: the verified S-box **is** the
  published table.
- `AES.KAT.keysched-kat` (AI-7k) — `keyExpansion` of the FIPS-A.1 key ≡ the published
  first round key.
- The Octave oracle (`mat260 oracle/run_aes_oracle.py`) cross-checks the MATLAB ∥ Python
  ports against the FIPS-197 KATs and each other.
