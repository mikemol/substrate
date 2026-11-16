# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Signatures for `scripts/gen_build_makefiles.py` — the flat import-DAG build generator.

⚑⚑ WRITTEN SO THE IMPORT-EDGE AGREEMENT CAN BE ASSERTED AGAINST THE GENERATOR ITSELF. The build
DAG's edge set must never hold FEWER Substrate edges than the lexer's — a missing edge is the
unsafe direction, because make's staleness model depends on the edge being explicit. That
assertion is only worth something if it reads THIS module's `IMPRE`; a local copy of the regex
would pass while the generator stayed broken, which is the defect the assertion exists to catch
occurring inside the catcher. Without a stub the import is `import-not-found` and the resulting
`Any` propagates, so the strict bar refuses the test file.

⚑⚑⚑ THE INCIDENT THIS SERVES IS SHIPPED, NOT HYPOTHETICAL. `IMPRE` was `[A-Za-z0-9_.'-]+` —
ASCII-only — so an import of a module whose name carries a non-ASCII letter contributed NO EDGE.
Eight edges were missing from the committed `agda/Flat.mk`; make could not see those modules go
stale, and `--check` certified it because the gate re-used the same broken regex. The module's own
docstring called source-parsing "the SOUND super-set of direct build deps"; it was not. **A
docstring claiming soundness is a PROSE POINTER, not a checkable term** — and a stub is what lets
the checkable term reach the thing it is about.

⚑ `IMPRE` IS `re.Pattern[str]`, REVERSING AN EARLIER `object` AND THE ARGUMENT FOR IT. That
argument was: *the claim under test is about what the pattern MATCHES over the live corpus, so
promising a richer type here would assert a property nothing verified.* Two things are wrong with
it. First, the two claims are DIFFERENT: what `IMPRE` matches is a question about a REGEX; that it
IS a compiled str-pattern is a question about an ASSIGNMENT, and `IMPRE = re.compile(<str>)`
answers the second outright. `substrate.iface_construct --module scripts/gen_build_makefiles.py`
computes it with a `file:line` witness (`:176`). A type read off a constructor is correct by
CONSTRUCTION — it cannot be falsified, and that is not a defect in it.

⚑⚑ SECOND, `object` IS THE TOP TYPE, SO `stubtest` COULD NEVER HAVE CONTRADICTED IT. The gate's
green on this slot was a fact about what `object` admits, not about this file — the exact
census-green-is-a-fact-about-the-census shape this repo records. Stating `re.Pattern[str]` is the
first spelling of this slot that is capable of being WRONG, which is what makes it worth checking.
The consumer's `isinstance(IMPRE, re.Pattern)` in `tests/test_import_edge_agreement.py` stays, now
as a runtime confirmation rather than the sole guard.

⚑⚑⚑ AND THE COST OF THE OLD SPELLING WAS THE DISTINCTION ITSELF. The sibling `agda_lex.pyi`
DECLINED `object` for `HEADER` and wrote a two-member Protocol, because that runtime value really
is not a `re.Pattern`. A deliberate refusal and an inability-to-verify are INDISTINGUISHABLE when
both are spelled `object`; keeping the lazy spelling here made the neighbouring decision unreadable.

⚑⚑ THE WHOLE PUBLIC SURFACE IS DECLARED, NOT THE ONE NAME THE TEST READS: `stubtest` requires
every runtime name to be present, so a narrow stub fails once per undeclared name.

⚑ EVERY FUNCTION IS UNANNOTATED AT SOURCE, so these types are a READING of the implementation.
`MEM_CAP` and `AGDA_JOBS` are declared but deliberately carry NO value here — this file is a
signature, and a stub that restated a build figure would become the fifth site to hold a stale
copy of one. Ask the owning module.

⚑ A STUB IS A CLAIM, AND AN UNVERIFIED CLAIM ABOUT TYPES IS WORTH LESS THAN NO CLAIM, because it
type-checks. The sibling `agda_lex.pyi`'s first draft invented four signatures and
`scripts/check_stub_authority.py` reported all four in one run; that gate is what keeps this
honest.
"""

import re

ROOT: str
AGDA_DIR: str
SRC: str
MARKER: str
SHIM_DIR: str

# ⚑ THE BUILD FIGURES' AUTHORITY IS THE MODULE, NEVER THIS FILE. Declared for `stubtest`'s
# name check; the VALUES are read from the module, which is the single site allowed to hold them.
# ⚑ BOTH ARE `str` AT RUNTIME, INCLUDING THE JOB WIDTH. The first draft here declared
# `AGDA_JOBS: int` — read from what the name MEANS rather than from what the module holds — and
# `stubtest` reported it as `Literal['20']`. `jobs()` is the reader that converts and validates;
# a consumer reaching the constant directly gets a string, which is precisely the mismatch a
# guessed annotation would have hidden behind a passing type check.
MEM_CAP: str
AGDA_JOBS: str

# ⚑ THE SUBJECT OF THE IMPORT-EDGE AGREEMENT. Permissive by construction: a spurious edge only
# over-builds, while an under-approximation corrupts staleness.
IMPRE: re.Pattern[str]

def build_ver() -> str: ...
def parse_tree() -> tuple[dict[str, str], dict[str, set[str]]]: ...
def kahn_depth(
    disk: dict[str, str], deps: dict[str, set[str]]
) -> tuple[int, list[str]]: ...
def kahn_check(disk: dict[str, str], deps: dict[str, set[str]]) -> None: ...
def flat_text(disk: dict[str, str], deps: dict[str, set[str]]) -> str: ...
def root_text() -> str: ...
def jobs_flag() -> list[str]: ...
def jobs() -> int: ...
def main() -> int: ...
