## 2. The atlas: one value space, two charts

The one-parameter value space underlying each pin — and underlying the
pre-split logic — has two presentations related by exp/log. This is the
atlas the title names.

**Definition 2.1 (additive chart 𝔸).** The extended real line
x ∈ [−∞, +∞], with:

- +∞ = truth, −∞ = falsity,
- neutral point **0** = maximal ignorance / balance,
- negation **not(x) = −x**: reflection through 0,
- truth-degree = signed distance from the origin,
- evidence accumulates **additively**. **[W]**

**Definition 2.2 (multiplicative chart 𝕄).** The semiring [0, +∞] with
multiplicative ideal at 1:

- +∞ = truth, 0 = falsity,
- neutral point **1** (the image of 0 under exp),
- negation **not(y) = 1/y**: reflection through 1,
- evidence accumulates **multiplicatively**. **[W]**

**Definition 2.3 (the transition map).** exp : 𝔸 → 𝕄 and log : 𝕄 → 𝔸
are the chart transitions. The two charts present *the same object*; no
statement of this logic is chart-essential. **[W]**

**Lemma 2.4 (negation is chart-local and conjugate).** Negation is
reflection through *each chart's own* neutral point. The two charts carry
**two genuinely different involutions, each appropriate to its own
algebraic structure**, and exp/log conjugate them:

- **Additive chart 𝔸 = [−∞, +∞] (the signed line):** not_𝔸(u) = −u, sign
  negation, reflection through **0**, fixed point {0}. This is the
  involution that acts on signed quantities, because 𝔸 is where signed
  quantities live.
- **Multiplicative chart 𝕄 = [0, ∞] (a semiring, *not* a ring):**
  not_𝕄(y) = 1/y, reflection through **1**, fixed point {1}. The
  reciprocal is the **semiring** negation; the carrier has no negative
  numbers, so 1/y is defined and involutive on all of [0, ∞] (with
  1/0 = ∞, 1/∞ = 0).

> not_𝕄(y) = 1/y = exp(−log y), i.e. not_𝕄 = exp ∘ not_𝔸 ∘ log.

The flip −log y ↦ +log y in 𝔸 *is* y ↦ 1/y in 𝕄. **[W]**

*Proof.* Direct computation: exp(−log y) = y⁻¹; the neutral points
correspond (0 ↦ 1) and each is the unique fixed point of its chart's
involution. ∎

**Caveat 2.4a (do not put 1/y on a ring).** The reciprocal involution is
the negation **of the semiring [0, ∞]**, not a reciprocal on a field. It
must not be extended to negative or complex arguments: the signed
quantities of this logic live in the *additive* chart (via log, which
maps the semiring [0, ∞] onto the whole signed line [−∞, +∞]), where the
appropriate involution is sign negation. Asking for "the fixed points of
1/y on ℂ" is a category error — it imposes a field structure 𝕄 does not
have. There is one semiring involution (1/y, fixed point 1) and one
signed-line involution (−u, fixed point 0); they are conjugate, and
neither is "1/x on a ring." **[W]** (records the correction that retired
the OB-9 complexification run; see OB-9.)

**Remark 2.5 (transport).** Lemma 2.4 is the pattern for every law of the
logic: prove in one chart, conjugate by exp/log, obtain the other chart's
form. The "same object, two charts" claim is a transport-along-equivalence
statement (see §10, Martin-Löf entry). **[S]**

**Lemma 2.5b (the chart adjunction — exp ⊣ log).** The two charts are
related by the adjoint pair **exp : 𝔸 → 𝕄** and **log : 𝕄 → 𝔸**, with
unit and counit log ∘ exp = id_𝔸 and exp ∘ log = id_𝕄. On the relevant
domains this is an **adjoint equivalence** (both round-trips are
identities), which is the precise content of "the same object in two
charts." **[W]** (round-trips verified).

On the (mass, bias) basis the adjunction acts **losslessly on both
coordinates at once**:

> bias b = u₊ − u₋  ⟼  E₊/E₋ = exp(b)   (the **ratio** is the
> multiplicative-chart *image* of bias)
> mass m = u₊ + u₋  ⟼  E₊·E₋ = exp(m)   (the **product** is the image
> of mass)

Both coordinates cross; neither is discarded; log brings both back. **[W]**

**Remark 2.5c (ratio-as-collapse vs ratio-as-chart-image — the keystone
distinction, stated explicitly).** The expression E₊/E₋ appears in two
roles that must never be conflated:

- **As a value (forbidden, §3):** reducing the pair *to* the ratio,
  discarding the orthogonal mass coordinate. This is lossy, one-way, and
  cannot distinguish both-high from both-low (Lemma 3.2). *Collapse =
  project and forget.*
- **As a chart image (fine, Lemma 2.5b):** E₊/E₋ = exp(b) is the
  multiplicative-chart presentation of the *bias* coordinate, with mass
  simultaneously present as the product axis E₊·E₋ = exp(m). Nothing is
  discarded; the map is invertible. *Chart-cross = transport and keep.*

The difference is not the formula — it is identical in both — but
**whether the orthogonal axis survives the operation.** The prohibition
of §3 forbids the first role and is silent on the second. A ratio that is
one half of an invertible (mass, bias) ↔ (product, ratio) chart map is not
a collapse; it is the adjunction acting. **[W]** (This corrects a
conflation that is easy to commit precisely because the surface syntax is
the same; see §11.3 / OB-5, where the Wheatstone galvanometer reads the
*chart-image* ratio, not the *collapse* ratio.)

**Lemma 2.6 (the locked locus).** The one-parameter value space embeds in
the carrier plane as the **inverse-locked locus**: pairs of the form
(u, −u) in additive presentation, equivalently (y, 1/y) in multiplicative
presentation. On this locus — and only there — negating one pin coincides
with swapping the pins:

> on (u, −u): u ↦ −u  ≡  (u, −u) ↦ (−u, u).

Off the locus, negate-a-pin and pin-swap are distinct involutions. **[S]**
(assembled from the witnessed derivation that negate-a-pin ≡ pin-swap
*requires* inverse-locked pins, plus Law 1.3 that the general pins are
independent.)

The paraconsistent move of §1 is precisely the passage from the locked
line to the full plane: the ideal of the second term is *not* of the first
term's ideal, and then the lock is released. **[W]**

---

