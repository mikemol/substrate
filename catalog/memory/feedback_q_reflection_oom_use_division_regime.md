---
name: feedback_q_reflection_oom_use_division_regime
description: "Polynomial *Q (field multiplication) reflection in Agda OOMs exponentially in nesting depth — a DEAD END on the merits (doesn't scale). Compute field-power facts in the DIVISION regime (ytime/reduce-mod-f, bounded magnitude) and prove the homomorphism STRUCTURALLY. membudget makes probing OOM-prone regimes SAFE (contained kills, box unaffected) — so explore freely; switch regime for the RESULT, not to avoid the (benign) OOM notices."
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

**The trap (measured 2026-06-25, GF(2ⁿ) discrete-log work).** Computing `gpow n = gx *Q gpow n` (the antilog
by iterated FULL multiplication) and proving `g^order ≡ 1` / inverse-laws by `refl` forces Agda to normalize a
deep nested `*Q` term whose normal form grows **EXPONENTIALLY in multiplication depth**: x⁴ ≈ free, x⁸ ≈ 1.5GB,
x¹⁵ OOMs, x²⁵⁵ hopeless. The `*Q` operation itself (the generic-CommutativeRing convolution + reduce) is the
cost — even square-and-multiply via `gpow-hom` and linear reduced-value chains OOM (the `cong₂`/`*Q` term-building
blows memory). This is why the substrate's other big reflections (`all-pass`, `fuel-bezout`) are DIVISION-based,
never `*Q`-chains.

**OOMs here are CHEAP — probe freely.** membudget contains each kill to a cgroup (`OOM-killed at 192MB —
retrying at 384/768/1536MB`); the box is unaffected and the desktop notices are benign developer OBSERVABILITY
(the user's words: "like hard-drive seeking noises on spinning rust"), NOT a cost to avoid. So do not be timid
about probing OOM-prone regimes — that is what the safety net is for. **The reason to switch off the
`*Q`-reflection regime is the MERITS, not the notices:** it is exponential in depth and does not scale (x¹⁵ OOMs,
x²⁵⁵ hopeless), so it is the wrong tool for the RESULT — change regime to get the theorem, not to silence a
benign signal. (Earlier in this arc I over-read the notices as something to avoid; that was wrong.)

**How to apply — change regime, don't grind the wall:**
1. **Antilog in the DIVISION regime:** `gpow n = xpow n oneC = ytimeⁿ oneC` (multiply-by-x = shift+fold, each step
   degree < suc d, BOUNDED magnitude). `x^order ≡ 1` is then a cheap `refl` (≈90MB), as is `reduce-mod-f` of a
   degree-`order` monomial. The log/exp codec view licenses computing the order fact in this cheap chart.
2. **Prove the homomorphism STRUCTURALLY**, not by per-element `*Q` reflection: the key lemma is `ytime` commutes
   with `*Q` — `p *Q ytime r ≡ ytime (p *Q r)` (both sides → `hsum p (ytime r)` via `reduce-*P-expand` +
   `reduce-idempotent` + `hsum-ytime`, all existing). From it: `xpow-*Q` → `gpow-hom : g^(a+b) ≡ gᵃ·gᵇ` →
   general `dlog-inv-law`, with NO field-mult reflection (`Algebra.F2.Polynomial.Wedge.DLogHom`). This both scales
   and eliminates the OOMs. See [[oom-load-bound-finding]], [[negative-findings-corpus]].

**Caveat:** the cheap regime is MONOMIAL-specific (`ytime` = ·x), so `x^·` covers the full group only where x is
PRIMITIVE (GF(2⁴): x⁴+x+1 primitive ✓; GF(2⁸) AES: x=0x02 NOT primitive — needs a primitive generator (x+1)^·,
whose powers need Frobenius `(x+1)^(2^k)=x^(2^k)+1`, not ytime). MEMORY ASIDE: membudget's printed "192MB" is the
COLD-MODULE DEFAULT LEASE, not the peak — actual peaks were ~90MB.
