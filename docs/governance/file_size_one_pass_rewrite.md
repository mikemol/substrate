# File size: one-pass rewrite discipline

_(Substrate governance policy. Migrated from `memory/feedback_file_size_one_pass_rewrite.md`.)_

A file should be small enough to be fully rewritten in a single
`Write` call — both by a human contributor working in a single
editor session, and by an LLM contributor (the assistant) generating
the file in one shot. If a file requires noticeable cognitive effort
to figure out how to **patch** (rather than rewrite) safely, it has
crossed the boundary and should be decomposed.

## Why this matters

* **Rewrites preserve coherence**: the whole content is considered
  together; the writer doesn't accidentally orphan pieces or leave
  stale dependencies.
* **Edit-pass patches accumulate technical debt**: each Edit modifies
  a fragment in local context, and the surrounding code may become
  silently inconsistent over time.
* **Files that resist clean rewrites are signalling a decomposition
  problem**: they are combining too many concerns into one module.
* **LLM-collaboration specific**: large files force the assistant to
  patch via `Edit` (positional surgery on context-matched substrings).
  Each Edit consumes context and risks targeting the wrong occurrence
  if the surrounding lines are not unique. Files that frequently
  require careful disambiguation are too big.

## Concrete thresholds

These are the substrate's working numbers, calibrated from the
file-decomposition arc that ran in May 2026 (7 critical files
ranging from 406–682 lines, each split into 4–8 submodules):

| File length | Status | Action |
| --- | --- | --- |
| **≤ 200 lines** | Comfortably one-pass | None |
| **200–400 lines** | Acceptable; one-pass with care | None unless growing |
| **400–600 lines** | **Warning zone** | Plan decomposition before adding more |
| **> 600 lines** | **Over the boundary** | Decompose now; new content goes to a submodule |

These are *line-count* thresholds because they correlate well with
the cognitive load of holding a file's structure in one attention
window. Token counts vary too much by language (a 500-line Agda
file with heavy unicode + record definitions is denser than a
500-line Python script of one-liners).

Practical signal independent of line count: **if you find yourself
needing two `Edit` calls in the same session to the same file with
overlapping context disambiguation, the file is over the boundary
in this session.** Decompose before the third Edit.

## How to apply

When a file approaches the warning zone:

1. **Stop adding to it.** Don't compound the problem with another `Edit`.
2. **Identify the natural decomposition.** Look for:
   * Sub-records or sub-functions that form a coherent unit.
   * Imports clustered around one concern vs another.
   * Sections that the file's own commentary already names ("N-1",
     "N-2", "Foundation", "Bridges", etc.).
3. **Move the decomposition into submodules** under the same module
   tree. `Substrate.Foo.Bar` becomes `Substrate.Foo.Bar.Part1`,
   `Substrate.Foo.Bar.Part2`, …, with `Substrate.Foo.Bar` becoming
   a thin re-export shim.
4. **The re-export shim is the public interface.** Downstream code
   continues to `import Substrate.Foo.Bar` and gets everything.
5. **Each part-module is small enough to rewrite.**

## Pattern: public re-export shim

```agda
{-# OPTIONS --safe --without-K #-}
module Substrate.Foo.Bar where

open import Substrate.Foo.Bar.Setup    public
open import Substrate.Foo.Bar.Core     public
open import Substrate.Foo.Bar.Capstone public
```

Each `.Part` file is small and self-contained. The umbrella module
preserves the public interface — `using` and `import` clauses at
call sites continue to work unchanged.

## Substrate precedent

The May 2026 decomposition sweep produced this typical pattern:

| Original (lines) | Decomposed into |
| --- | --- |
| `Groups/S4-Iso.agda` (682) | 8 submodules of 40–136 lines + shim |
| `Cocycles/V4Signature/S4Iso.agda` (638) | 6 submodules of 58–125 lines + shim |
| `Groups/Actions/S3-on-V4.agda` (542) | 7 submodules of 53–126 lines + shim |
| `Cocycles/.../LiveS4Bijection.agda` (489) | 4 submodules of 66–190 lines + shim |
| `Groups/V4.agda` (480) | 5 submodules of 24–160 lines + shim |
| `Algebra/F2/.../Permutation.agda` (413) | 6 submodules of 26–77 lines + shim |
| `Category/PhaseLockedLoop.agda` (406) | 8 submodules of 23–54 lines + shim |

The shims themselves are 30–75 lines (mostly comment + re-exports).
Each submodule is well inside the comfortable-rewrite zone.

## Anti-patterns

* **"I'll just add one more section"** growing a file past the
  rewrite boundary. The discipline applies BEFORE the boundary is
  crossed.
* **Large per-instance files** (e.g. 200+ lines of Coxeter boilerplate
  for one Zₙ instance). These should decompose via parametric modules
  rather than per-instance file growth.
* **Patch-stacking**: repeated `Edit` calls accumulating fragments
  into a file that no longer has clean structural unity.

## Connection to other governance

* [`generator_over_orbit.md`](generator_over_orbit.md) — large
  enumeration is also a decomposition signal. A file that's large
  *because* of enumeration usually needs a generator-level
  refactoring as well as a file-level split.
* [`cover_pattern.md`](cover_pattern.md) — Cayley-table cover
  combinators are one way to compress enumeration; applying them
  often makes a file fit the one-pass-rewrite budget without further
  decomposition.

## Why this lives in governance rather than as a tool config

The discipline is about *cognitive* one-pass-rewriting, which
doesn't map cleanly to a per-language linter rule (Agda's lines are
not Python's lines). Treating it as a policy lets contributors
exercise judgement at the boundary, with the concrete thresholds and
substrate precedent as calibration.
