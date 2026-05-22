# Reach for universal-property bridges first

_(Substrate governance policy. Migrated from `memory/discipline/feedback_universal_property_discipline.md`.)_

**Rule.** When proving a fact about an F₂-linear map (its `apply` behaviour, its kernel, its image, its equality with another map), reach for the **universal-property bridges and abstract apply-reductions FIRST**. Per-instance manual unfolding is the fallback, used only when no abstract bridge applies.

**Why:** Per-instance unfolding scales linearly with the number of bit-positions and requires chains of F₂-axiom rewrites (`·-absorbʳ`, `+-identityˡ`, `·-identityʳ`, ...) at every call site. At n=3, it's 5 lines per lemma; at n=5, 15+ lines; at n=8+, intractable. Universal-property bridges reduce the problem to a fixed-size check (n basis vectors, or k generator images, or one abstract reduction lemma reused everywhere). **Same correctness, exponentially less code, scales to any n.**

**Three bridges that handle most cases:**

1. **M-3.5 `linear-extensionality`**: "Two Linears agree on all vectors" reduces to "they agree on n basis vectors." Use this for **Linear equality / Linear agreement** claims. n cases instead of 2^n.

2. **`apply-linear-from-images-lookup`** (foundational abstract reduction, lives in `Substrate/Algebra/F2/Linear/FromImages.agda`):
   ```
   lookup (apply (linear-from-images f) v) j
     ≡ sum-F₂ (λ i → lookup v i · lookup (f i) j)
   ```
   Use this for **apply-behaviour** claims. Reduces "apply-Selector-lookup" proofs to one lemma application + a small sum-collapse.

3. **M-4.5 `Image-Equivalent`**: "Two ImageCodes are equal" reduces to "their generators agree on basis-images." Use this for **code-equality** claims (one direction).

**How to apply (recipe for a typical N-x file):**

When you need to prove "`apply MySelector v` behaves like X":

1. Apply `apply-linear-from-images-lookup` at the appropriate index j → reduces to a `sum-F₂` over the basis-images.
2. Use `sum-F₂-cong` if you need to rewrite each summand uniformly.
3. Collapse the specific sum via `sum-F₂ {k}` unfolding + small F₂ chains (this is the only per-instance step).

The per-instance work is THEN bounded by k (the number of basis-image cases), not 2^n.

**Anti-pattern (already-seen in M-11.dim3 N-1 / N-2, pre-discipline):**

Writing `apply-V4Plane-Selector-lookup` and `apply-ChirAxis-Selector-lookup-0/1` proofs by manually chaining `·-absorbʳ` / `+-identityˡ` / `·-identityʳ` through the unfolded sum. **Works for small n; replace going forward with the abstract reduction**:

```agda
apply-V4Plane-Selector-lookup v =
  trans (apply-linear-from-images-lookup chirality-bit-images v zero)
        (small-sum-collapse v)   -- specific to chirality-bit-images
```

The `small-sum-collapse` is `O(k)` per Selector, not `O(n)` per Selector.

**When per-instance unfolding IS appropriate:**

- The Linear is small (n ≤ 3) AND used only once AND the reduction is pedagogically clearer expanded.
- The reduction has non-trivial computational content not captured by the abstract pattern.
- These are exceptions; the default is universal-property bridges.

**Connection to scaling.**

This discipline is what makes scaling to larger Reed-Muller / Hamming / cocycle complexes tractable. At length 2^m with m ≥ 5, per-instance unfolding becomes intractable; the abstract reduction stays O(1) in the lemma + O(k) in the per-instance collapse. See [[project_3plus1_parity_universal]] for the F₂³ → F₂^n projection-transport that depends on this discipline.

**Cross-references:** [[feedback_expose_generator_not_orbit]] (the dual rule for definitions: define codes via generating functions, not enumeration), [[project_3plus1_parity_universal]] (the chirality-as-Hodge-dual structure that scales via projection + this discipline).
