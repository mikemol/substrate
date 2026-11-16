# Lattice findings — return-to-source items surfaced by `pm-depsort.py`

⚑⚑ **READ `lattice/AUDIT.md` ALONGSIDE THIS FILE. THREE OF THE ITEMS BELOW ARE NOT DEFECTS.**
Audited 2026-09-05 under the realizability charter (README §"The second discipline"), each finding
below carries a **coordinate and a reference arm**, and the audit changes what two of them cost:

- **Finding 1** — the circle is `unseparated-in-S` for a space this instrument never printed. It was
  never wrong; it was **unindexed**. The separable break is grounded and is the **status gate**, not
  the `configure_phase` knob this file predicts — dpkg has *no topological sort at all*.
- **Finding 2** — ⚑ **`FUNCWHY` IS A MISSING CLAIM, NOT A MISSING KNOB.** The `hook_why` knob
  *already* carries `'named' | 'funcname' | 'count' | 'none'` and the entries already ground all
  four; `claim_hookwhy` simply tests `!= "none"` and never reads the value. That is a strictly
  cheaper closure than this file proposes, and no re-grounding is owed. The *stateless-hook* half of
  the finding **is** a real gap and does need a knob.
- **Finding 3** — the re-tag `INFERRED → MEASURED (single-witness, dpkg)` is earned and is **still
  not an empty residue**: a witness for `necessary-in-dpkg` is not a witness for `necessary`.

**Below is the first run's own account, kept unedited as residue.** The charter's rule is that a
superseded reading is retained with its index rather than rewritten — this file is what the
instrument said at `S_four-managers`, and the audit is what it means.

The first run of the el-atlas port over the four committed manager entries. The
lattice is not the deliverable; the deliverable is what running it forced us to
go back and check. Each item below is a place the instrument revealed a
granularity the manager entries did not carry — the expected mode, not a defect.

## The lattice, first run (11 capabilities, dpkg-maximal BASE)

```
layer 0 (foundations):  {SPLIT}  {HOOKWHY}  {HANDEDIT}  {EXEC}
layer 1:                {CRASH}  {DEPORDER,SETCFG}  {NAMEDWHY}  {BUILDINST}
layer 2:                {TRIG}  {STAGED}
circle:                 {DEPORDER, SETCFG} -> COHERENT
independent pairs:      48 of 55
```

Read as a presupposition order (higher needs lower): triggers and staged
teardown sit at the top — each needs the crash-recovery ledger beneath it, which
in turn needs the unpack/configure split. The hook-"why" chain (NAMEDWHY over
HOOKWHY) and the build chain (BUILDINST over EXEC) fall out as separate spines.

## ⚑ FINDING 1 — the {DEPORDER, SETCFG} circle may be a forced artifact

`SETCFG` and `DEPORDER` came out mutually constituting. But they share one break
knob (`dep_order=False` breaks both), and el-atlas's own mechanism turns a shared
break into a circle. So the circle is **as real as the claim that these are one
capability, not two** — and that claim is untested.

- **The el-atlas discipline for exactly this** (its own v2 refinement block):
  an SCC is correct *at the current probe basis*; the well-posed question is
  whether it SPLITS under a finer break. Here the finer break is available:
  set-wide-ordered-configure is dpkg's `deferred_configure` re-enqueue loop
  (managers/dpkg.md), whereas plain dependency-ordering across a set is what
  rpm's Tarjan tsort and pacman's `_alpm_sortbydeps` also do WITHOUT any
  configure phase. That asymmetry says they are probably **two capabilities**:
  DEPORDER is foundational, SETCFG presupposes both DEPORDER and SPLIT.
- **Return to source:** confirm from dpkg's `deferred_configure` whether the
  dependency-ordering there is separable from the configure-deferral, then give
  SETCFG a distinct break (e.g. a `configure_phase` knob) so the two stop
  sharing `dep_order`. Re-run; expect the circle to split.

## ⚑ FINDING 2 — rpm and pacman are byte-identical in the locator, and they are not identical

The run reports `rpm` and `pacman` with the SAME capability set
`[DEPORDER, HOOKWHY, HANDEDIT]`. The committed entries say they differ:

- hook-"why": rpm uses a bare `$1`-count (managers/rpm-yum.md); pacman uses a
  function name + version args (managers/pacman.md) — a real expressiveness gap.
- hand-edited-file: rpm digest-compares to `.rpmnew`/`.rpmsave`
  (managers/rpm-yum.md); pacman does a three-way hash to `.pacnew`
  (managers/pacman.md).
- deferred hooks: rpm has FILE TRIGGERS (managers/rpm-yum.md); pacman's
  alpm-hooks are stateless and Pre/Post-transaction only (managers/pacman.md).

⚑ This is the "two things agreeing on a coarse scalar" trap inside our own
instrument. They collapse because **no current capability distinguishes them**:
`HOOKWHY` is present/absent only (it does not rank funcname vs count), and there
is no file-triggers capability at all.

- **Return to source / refine:** the model under-resolves axis 5 (hook-why) and
  axis 7 (triggers). Candidate new capabilities: `FUNCWHY` (function-name-level
  "why", between named and count) so the funcname/count gap becomes an edge; and
  a stateless-hook capability distinct from `TRIG` so rpm's file-triggers and
  pacman's alpm-hooks separate. Both need a source read before encoding.

## ⚑ FINDING 3 — the two INFERRED edges rest on a single witness (dpkg)

`TRIG` presupposes-LEDGER and `STAGED` presupposes-LEDGER are both tagged
`INFERRED` in the source, and both have **only dpkg as witness** — dpkg is the
only manager here with a ledger at all, so "triggers/staged-teardown REQUIRE a
ledger" is indistinguishable from "dpkg happens to have both." A one-witness
presupposition is a hypothesis, not a measured edge.

- **Return to source:** these need a manager that has persisted state WITHOUT a
  full dpkg-style ledger, or a demonstration from dpkg's own source that the
  trigger/config-files states are *inexpressible* without the ordered pkgstatus
  enum. Until then the two top-layer edges are the least load-bearing in the
  lattice and should be read as provisional.

## How to re-run

```sh
python3 lattice/pm-depsort.py
```

No arguments. Prints base pass-set, the B-under-break(A) matrix, circles, depth
layers, and the manager locator. Every claim must show `P` on BASE (the header
line asserts `all P: True`); a claim that does not is a modelling error, not a
finding.
