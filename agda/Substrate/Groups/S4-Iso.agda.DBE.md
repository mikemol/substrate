# DBE: S4-Iso continuation — REVISED after user redirection

**Target:** Structurally-compositionally prove V₄ ⊳ S₄ as transport of
N-normal-in-SP (in SemidirectProductGroup) through the iso
S₄-Composed ≅ Permutation Axis.

## Skills active

DRS-triple (substantive structural arc). Mid-session region-transition
mid-V₄-normal-compositional: the user redirected from "stab-conj + custom
chain" to "iso transport of N-normal-in-SP". Per shadow-architecture rule 2,
this is **enriching, not correcting** — it reveals that the SP combinator's
N-normal-in-SP is the load-bearing structural fact, and the bridge needs to
be the full iso (forward-hom + forward-ε + forward-inv), not a custom stab-conj.

## Shadows accumulated (builds clean)

| # | Name | Status | File |
|---|------|--------|------|
| H-1 | extract-s-correct | ✓ | S4-Iso.agda |
| H-2 | perm-roundtrip-≈ | ✓ | S4-Iso.agda |
| H-3 | N-normal-in-SP | ✓ | Coxeter/SemidirectProductGroup.agda |
| H-4 | embed-as-N-injection | ✓ | S4-Iso.agda |
| forward-hom | (pre-existing) | ✓ | S4-Iso.agda |
| stab-conj | (pointwise, builds) | ✓ | S4-Iso.agda |

## Open shadow inventory (needed to close V₄-normal-compositional structurally)

| # | Name | Type | Notes |
|---|------|------|-------|
| K-1 | forward-ε | `compositional-to-perm S4C.ε ≈ ε` | small; needs `act-axis-id` + `embed-S₃-ε` |
| K-2 | forward-inv | `compositional-to-perm (s S4C.⁻¹) ≈ (compositional-to-perm s) ⁻¹` | derivable from K-1 + forward-hom via algebraic chain (left-inverse uniqueness) |
| K-3 | V₄-normal-compositional | iso-transport of N-normal-in-SP | new composition |

## Why stab-conj is a regression to be retired

stab-conj was written to compose V₄-normal-compositional via a custom
algebraic chain on the Permutation side. Per the user's structural emphasis
+ DBE thrash-response protocol, the proper composition is:

1. σ ≈ compositional-to-perm σ̂                          [H-2]
2. embed v ≈ compositional-to-perm (v, S₃.ε)             [H-4]
3. σ⁻¹ ≈ compositional-to-perm (σ̂ S4C.⁻¹)               [forward-inv = K-2]
4. (σ · embed v · σ⁻¹) ≈
   compositional-to-perm σ̂ · compositional-to-perm (v, S₃.ε)
     · compositional-to-perm (σ̂ S4C.⁻¹)                  [·-cong on steps 1+2+3]
5. ≈ compositional-to-perm (σ̂ S4C.∙ (v, S₃.ε) S4C.∙ σ̂ S4C.⁻¹)
                                                          [forward-hom × 2]
6. ≈ compositional-to-perm (n', S₃.ε)                    [H-3, via cong of compositional-to-perm if needed]
7. ≈ embed n'                                             [H-4 sym]

stab-conj is a one-cell pointwise lemma. The above is full transport via the
iso. The latter is what "compositional via Coxeter framework" actually means.

## Open question (to surface to user)

The chain in step 6 requires `compositional-to-perm` to respect S4C._≈_,
which decomposes into V4._≈_ × S₃._≈_. V₄._≈_ is propositional `_≡_`; S₃._≈_
is the SP `_≈_` over Z3-Coxeter-Group × Z2-Coxeter-Group, where the atom `_≈_`
is Word-equivalence-via-normalize (NOT propositional `_≡_`).

So step 6 requires a `compositional-to-perm-cong : s₁ S4C.≈ s₂ →
compositional-to-perm s₁ ≈ compositional-to-perm s₂` lemma. This is a pointwise
proof that uses act-axis ≈-respect + φ.act-cong + Z₃/Z₂ normalize machinery.

Alternatively, if `S4C._≈_` on the H-3 witness already reduces propositionally
(because the inner H-component computes to S₃.ε definitionally), we may sidestep
the cong proof.

## ≈-trans implicit-inference shadow (cross-cutting)

The repeated failure mode in this session: nested `≈-trans step1 (≈-trans step2 ...)`
generates "unsolved metas" because Agda can't determine the middle Permutation
τ when both args are themselves applications. **Fix discipline:** use Agda's
`Relation.Binary.Reasoning.Setoid` with the S4 Group's Setoid bundle, OR pass
`{σ = _} {τ = M} {ρ = _}` explicitly on every nested ≈-trans.
