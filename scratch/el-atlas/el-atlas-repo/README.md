# EL-Atlas

A paraconsistent evidence logic, specified witness-first and deliberately non-closed.

## Document map

| file | role |
|---|---|
| `el-atlas-spec.md` | The specification (currently **draft 16**). The prose source of meaning. Each draft's closing block records what changed and why. |
| `el-atlas-cotype.md` | The cotype: the workstream's externalized notes-to-self. Observed-vs-asserted splits, drift/guard events (DRIFT-1a…5 and successors), probe states, retractions (kept, never deleted), next-work. **The provenance log.** |
| `el-atlas-structured.md` | The Structured Edition: ToC, chapter grouping, glossary, cross-reference, and perspective-visibility tables **mechanically computed** by the depsort harness. Regenerate after each draft; diffs here are detected structural events. |
| `features/` | AWGT Gherkin features (49 scenarios): the spec's claims as obligations under the CONSTRUCT functor, coordinates in `00_coordinates.md`, coverage as a DAG section in `01_coverage_audit.md`. Open work is `@open`/`@candidate`/`@undetermined`-tagged, never confabulated. |
| `tools/el-atlas-depsort.py` | The empirical dependency sort: claims as executable tests, characteristic break mutations, P/F/V matrix, SCC circles, basis refinement (intrinsic vs coincidence). The spec's first self-applied instrument. |
| `tools/depsort_run_draft16.txt` | The draft-16 run transcript (evidence artifact). |

## Conventions

- **Corrections are monotonic.** Wrong runs are marked RETRACTED in place; nothing is
  deleted. The error's provenance is part of the record.
- **Grades:** [W] witnessed (computed/verified), [S] supported, [C] candidate.
- **Vacuity is its own value.** Tests return P/F/V; "not statable here" is not "false."
- **Circles:** intrinsic (persists under basis refinement; mutual constitution;
  ∀-over-bases, open-by-design) vs coincidence (splits; shared substrate).
- **No unindexed verdicts.** Every instrument verdict is emitted relative to a
  reconstructible space: the run prints a SPACE MANIFEST (knobs + value sets) and a
  fingerprint (sha256 over manifest + claim-test sources). "Unseparated" is never
  uttered bare — only "unseparated-in-S_<fp>". Known spaces where the verdict differs
  travel with it as a residue ledger; separations carry a minimal witness mutation.
- **Commit discipline:** commit per draft or per instrument run; the message names the
  triggering correction or finding, so `git log` reads as the reasoning path.

## Regeneration workflow

After editing the spec: run `python3 tools/el-atlas-depsort.py` (extend claims if the
draft added structure), regenerate the structured edition, diff it, and log structural
events (layer moves, circle changes, visibility-cell flips) in the cotype before
committing.
