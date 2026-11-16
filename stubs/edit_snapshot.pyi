# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Signatures for `scratch/edit_snapshot.py` — the snapshot-and-mutation-contract authority.

⚑⚑⚑ THIS STUB EXISTS BECAUSE `scratch/` IS DELIBERATELY NOT A PACKAGE, AND THAT IS NOT A
PACKAGING OVERSIGHT TO ROUTE AROUND. `scratch/` is unpackaged BECAUSE IT MUST BE DRAINED;
adding an `__init__.py` would license permanent dependence on a staging area. So a gated file
that arms the snapshot guard writes `import edit_snapshot`, and the checker reports TWO
findings for it: `import-not-found`, and then `Expression has type "Any"` on the `guard` call
— because an unresolvable import poisons every reach off it. `check_snapshot_guard`'s own
refusal text names the remedy, and it is this file: a STUB THAT ADDS TYPES, supplying
signatures independently of packaging. That is the same repair `check_scratch_independence.pyi`
and `tsdbprobe.pyi` already record for two other `scratch/` authorities.

⚑⚑ THE TWO FINDINGS ARE ONE DEFECT WITH A DIRECTION, AND ONLY THE SECOND IS THE DANGEROUS
HALF. `import-not-found` is loud and self-describing. The `Any` it induces is silent: every
attribute read off an unresolved module type-checks against NOTHING, so a call with the wrong
arity, the wrong keyword, or a misspelled name passes the strict bar. An `Any` from an
authority is an ABSENCE of an answer wearing an answer's clothes — `stub_top_type` makes the
same argument about the top type one annotation wide, and this is that argument at module
scope.

⚑⚑⚑ EVERY SIGNATURE BELOW WAS READ FROM `scratch/edit_snapshot.py` ITSELF, NEVER FROM A CALL
SITE, and the precedent that forces this is measured: `stubs/agda_lex.pyi` records its first
draft INVENTING FOUR NAMES, all four caught by stubtest, and `tsdbprobe.pyi` records five more
— written from the shape a probe *ought* to have. A call site shows only the arguments one
caller happened to pass; it cannot show a defaulted parameter, and it cannot show that the name
exists at all. **A stub is a CLAIM, and an unverified claim about types is worth less than no
claim.**

⚑⚑ AND `DEFINED-IN` IS NOT `EXPORTED-FROM`. `stubtest` walks RUNTIME→STUB, so it CANNOT see a
name this file asserts that the runtime lacks — proved by positive control this arc, where a
fabricated `GhostExport` passed the gate. `substrate/stub_reexport.py` is the other half of
that cover, testing `hasattr` on the imported module, and both are required. This stub is
therefore written to the module's own definitions, and the two gates check it from opposite
ends.

⚑ THE RETURN OF `guard` IS `str | None`, NOT `str`, AND THE `None` IS LOAD-BEARING RATHER THAN
DEFENSIVE. `guard` returns `snapshot(...)`, whose docstring states the contract exactly: it
"Returns None — never raises — if this is not a git worktree or git fails. A snapshot is a
safety net, and a missing net must not stop the work." Declaring `str` would erase the one case
a caller is explicitly told to report, and would do so in the direction that reads as safe.

⚑ THE MUTATION-CONTRACT REFUSALS DERIVE FROM `BaseException`, AND THAT IS A MEASUREMENT IN THE
SOURCE, NOT A STYLE CHOICE THIS STUB MAY NORMALISE. `MutationContractError`'s own docstring
records the obvious cut — derive from `Exception` — being written and then REVERTED against a
census of 31 `except Exception` sites that wrap a `guard()` call and then write anyway. On
`Exception` those handlers would convert a hard refusal into an advisory print with the write
still happening. A stub that "corrected" this hierarchy to the conventional one would assert a
containment relation the runtime does not have, at 31 sites, silently.

⚑⚑ WHAT THIS STUB DECLARES IS THE SURFACE THIS REPO CONSUMES, AND THE REST IS DECLINED RATHER
THAN GUESSED — the `stub_declines` discipline. The declined half is not small and not
incidental: it is the ambient-context machinery (`Ambient`, the write-once `INTENT`/`TENANT`
variables, `_Override` and the sanctioned-override roster), the restore/journal reader surface,
and the CLI boundary. Each is a real capability with real signatures; none is reached by the
gated files this stub exists to unblock. Declaring them would be asserting signatures nobody
here has read, which is the failure the precedent files name.

⚑ AND A DECLARATION IS A CLAIM WITH A COST, STATED SO IT IS REVIEWABLE: what this stub
declines, a caller cannot reach. A file that later needs `require_at_entry` or the ambient
variables does not get relief by widening the marker — it gets a read of the source and a new
signature here, verified by the gate from both ends.

⟡declines: the ambient-context machinery (`Ambient`, `_Override`, the write-once `INTENT` and
`TENANT` variables, `INTENT_ORIGIN`, `SNAPSHOT_STATE`, `SANCTIONED_OVERRIDES`,
`sanctioned_setters`, `naming_tenant`, `resolve_intent`, `IntentConflict`,
`NEAR_MISS_SPELLINGS`); the recovery-reader surface (`contents`, `restore`, `announce`,
`snapshot_once`, `require_at_entry`, `require_explicit_mutation`); the module's path constants
(`ROOT`, `JOURNAL`, `SNAPDIR`); and the CLI boundary (`cli_main`). This repo's gated files arm
the guard and read nothing else — a stub claiming the ambient machinery would be asserting a
context-variable protocol whose refusal semantics are documented at length in the source and
have not been read here.
"""

class MutationContractError(BaseException): ...
class AmbientVocabError(MutationContractError): ...

# ⚑ `paths` is advisory and defaulted; `intent` is the fixture escape, stated at the call site
# rather than read from the caller's argv. Read from the def at `scratch/edit_snapshot.py`.
def guard(
    label: str, paths: object = ..., intent: str | None = ...
) -> str | None: ...

# ⚑ `guard`'s own return, and the reason it is optional. `paths` is recorded in the journal so
# a reader knows which files the run intended to touch; the snapshot itself is whole-worktree.
def snapshot(label: str, paths: object = ...) -> str | None: ...

# ⚑ The ENTRY-POINT form: states intent before dispatch and, when the stated intent is apply,
# takes the snapshot in the same act. Read from the def at `scratch/edit_snapshot.py:1091`;
# it returns `require_explicit_mutation`'s verdict (a str) or "selftest", and EXITS 2 on a
# refusal rather than raising - it owns the pid, where `guard` does not. Declared for the
# `split_pipeline` shim (W4 file 4 step 13), whose `main` states its intent through it.
def require_at_entry(label: str, argv: object = ..., intent: str | None = ...,
                     paths: object = ..., store: bool = ...) -> str: ...
