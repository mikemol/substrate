## 13. Consumption modes — how data is taken in and acted on

The atlas distinguishes five ways a value is *consumed*. They were
enumerated piecewise across §§1–12; collected here they expose a grading
that resolves OB-12. The organising fact, stated by the user: **getting
additive is logic in circuit clothing** — accumulation is not a
distinguishing axis, because every mode is some accumulation. What
distinguishes the modes is *what order of form they consume* and *whether
they preserve, project, or build the carrier.*

**Mode 1 — Accumulate (write).** Definition 1.1: increment × total →
total, on a single pin, no cross-read (Law 1.3). The only *write* mode;
the rest are reads. Consumes a **degree-1** quantity (a running sum).
**[W]**

**Mode 2 — Project to a named scalar (read-down, lossy).** Remark 3.5's
five shadows: mass, bias, unsigned decisiveness, single-conductor
collapse, ratio/null. Each discards everything orthogonal to the chosen
axis. Common-mode rejection is this mode used to discard mass. Consumes a
**degree-1** linear functional of the pins. **[W]**

**Mode 3 — Gate / threshold (consume-by-committing).** Witness 7.5: drive
to a saturating rail; the value is consumed by being *absorbed* into a
decision (the repeater). Unlike Mode 2 it does not read the value, it
*ends* it. This is the **first nonlinearity** — a saturating rail is not
a linear functional of the pins — so it is the first mode that leaves the
linear layer. **[W]**

**Mode 4 — Transport (lossless read-across).** Lemma 2.4 / Remark 2.5:
consume in one chart, conjugate by exp/log, act in the other. The only
mode that preserves *all* structure. The atlas is instance zero of it.
**[W]**

**Mode 5 — Overlay / glue (build-up).** §12: consume across a shared
instance S; computation in one network manifests in another, modulated by
S (Candidate Law 12.2). Unlike every other mode, this one *builds* rather
than reads or writes — it is a **bilinear pairing** of two reasoning
spaces. **[W]** for the mode; the manifestation law is **[C]**.

### 13.1 The Reed–Muller grading of the consumption modes

Under the identification of §11.10 — the doubling tree is the
Sylvester–Hadamard matrix, whose rows are the Walsh characters
(−1)^⟨a,x⟩, and **RM(1, m) is exactly the Hadamard code** under
x ↦ (−1)ˣ, with the Walsh–Hadamard transform as its fast decoder
(classical: MacWilliams–Sloane) — the modes grade by Reed–Muller degree:

- **Modes 1, 2, 4 consume degree-1 forms.** Accumulation, the mass/bias
  projections, and chart transport are all linear in the pins; they live
  entirely in **RM(1, m)**. This is the precise content of "additive is
  logic in circuit clothing": the whole linear layer — accumulate,
  project, transport — *is* the first-order Reed–Muller / Walsh layer,
  and nothing in a single tower climbs past it. **[W]**
- **Mode 3 (gating) is the first departure from RM(1).** The threshold
  nonlinearity is where degree can begin to climb; a decided rail is not
  a first-order form. **[W]**
- **Mode 5 (overlay) is the product that builds the degree filtration.**
  Gluing two networks along S is a **pairing** — and the pointwise
  product of two degree-1 reads (one from each tower) at the shared
  instance is a **degree-2** RM codeword (witnessed: the product of two
  linear forms is generically not in RM(1, m)). So the higher-order
  Reed–Muller layers RM(r, m) for r > 1 are reached by the **overlay
  pairing**, not by the doubling recursion. **[W]**

### 13.2 Resolution of OB-12 (the channel product)

The pilot (§11.10) found no product in the doubling tower and left open
where a product could come from. §13.1 answers it: **the product was never
supposed to be in the tower.** A single tower is a consumption mode
(accumulate/transport — Modes 1 and 4), and consumption modes are linear:
they stay in RM(1, m) **by design**. The bilinear product — the operation
that climbs to RM(r > 1) — is **Mode 5, the overlay**: the pairing of two
towers at a shared instance. The Cayley–Dickson search looked for the
product *inside the doubling recursion*; it is not there because it lives
on a different axis — the overlay (e₂/e₃ in §12's terms), not the doubling
(the tree's own recursion). **OB-12 is therefore resolved, not deferred:**
the doubling tree is RM(1, m) and correctly carries no product; the
product is the overlay pairing, and "climbing the RM degree filtration" =
"composing more overlays." The phantom hierarchy is the linear transport
layer; multiplication is what happens when two such layers are glued.
**[W]**

### 13.3 The no-collapse discipline, in code terms

The five modes give the prohibition (§3) a coding-theoretic statement:

- **Accumulate and transport are lossless** — they retain the full
  evaluation vector (all of RM(m, m), the whole transform). Mode 4 is the
  structure-preserving representation; nothing is discarded.
- **Project and gate are the named lossy consumptions** — decoding to a
  subcode (Mode 2 reads one RM(1) coordinate; Mode 3 hard-decides). Every
  lossy read is exactly a Remark 3.5 named projection.
- **Overlay is the one constructive consumption** — it builds *up* the
  degree filtration rather than reading *down* it.

So "never collapse the pair" reads, for codes, as **"never silently
project to a subcode; keep the full transform, and name every decoder."**
The Walsh–Hadamard transform is the lossless representation; every
standard decoder is a named lossy projection of it. **[S]**

---

