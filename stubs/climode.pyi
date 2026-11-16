# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Signatures for `scripts/climode.py` — THE declaration shape for a CLI mode.

⚑⚑⚑ THIS STUB EXISTS FOR THE REASON `edit_snapshot.pyi` RECORDS, ARRIVING AT THE MODULE THAT IS
SUPPOSED TO END A CLASS OF DEFECT. `climode` is the declared standard for stating a tool's modes,
so a typed consumer adopting it is exactly the case the repo wants to be easy — and without a stub
it is the case the strict bar punishes hardest: `import-not-found` on the import, and then
`Expression has type "Any"` on EVERY `Mode(...)` in the table. Measured on the first draft of
`substrate/bib_modes.py`: **one unresolvable import produced 44 findings**, none of which were
about the roster.

⚑⚑ AND THE SECOND HALF IS THE DANGEROUS ONE, WHICH MATTERS MORE HERE THAN ELSEWHERE. An `Any`
from an unresolved authority type-checks against nothing, so a `Mode(...)` call with a misspelled
keyword — `write=` for `writes=`, `scan=` for `scans=` — passes the strict bar silently and
declares a contract the gate then reads as absent. **The whole value of `Mode` is that its fields
are checkable claims**; reaching it through `Any` erases exactly that property at the point of
declaration.

⚑⚑ EVERY SIGNATURE BELOW WAS READ FROM `scripts/climode.py` ITSELF — the class body, its
`__slots__`, its `__init__` defaults and the `mutates` property — never from a call site. The
precedent forcing this is measured and recorded in the sibling stubs: `agda_lex.pyi`'s first draft
invented four names and `tsdbprobe.pyi` five, each written from the shape a module *ought* to have.
A call site cannot show a defaulted parameter and cannot show that a name exists at all.

⚑ `mutates` IS DECLARED AS A READ-ONLY PROPERTY, AND THE READ-ONLY PART IS THE CLAIM. Its source
docstring states the design: *"THE BOOLEAN IS A PROJECTION OF THE TARGET SET, NOT A PEER FIELD.
Storing both would be two spellings of one fact that can disagree."* A stub declaring it a settable
attribute would assert that a caller may set it independently of `writes` — the precise drift the
property exists to make impossible.

⚑ THE CONSTRUCTOR PARAMETERS ARE `object`-TYPED WHERE THE RUNTIME ACCEPTS ANY ITERABLE. `opts` and
`writes` are normalised with `tuple(...)` inside `__init__`, so the runtime accepts any iterable
and the attributes are always tuples. The stub states the ATTRIBUTE types precisely (that is what
consumers read) and keeps the parameters permissive rather than narrowing a contract the source
does not enforce.

⚑⚑⚑ AND THIS STUB'S CONSUMER CHANGED WHILE IT WAS BEING WRITTEN, WHICH IS WORTH RECORDING RATHER
THAN QUIETLY REPURPOSING. It was written so `substrate/bib_modes.py` could import `climode` under
the strict bar. The operator then ruled *"drain the thing that's blocking you"*, so the module was
PROMOTED to `substrate/climode.py` and `bib_modes` imports it normally — needing no stub at all.

⚑⚑ WHAT STILL NEEDS IT IS THE DIFFERENTIAL SUITE, AND THAT IS A BETTER FIT. `climode_selftest`
loads `scripts/climode.py` BY PATH (importing it by leaf name would be the `sys.path` surgery the
promotion removes) and runs both implementations over the same inputs. A dynamically loaded module
is `Any`, so every read off the origin poisons a case — which is the same defect this file's opening
paragraph describes, arriving through `importlib` instead of through an unresolved import.

⚑ SO THE SIGNATURES BELOW NOW SERVE A RETIREMENT RATHER THAN AN ADOPTION, and they retire WITH the
origin: when `scripts/climode.py` is deleted, the differential cases skip and this file has no
remaining consumer. That is the honest lifetime of a stub over a module being drained.

⟡declines: everything but `Mode`, `split_flag`, `from_pairs` and `POSITIONAL` — the surface the
differential suite reads. `scripts/climode.py` is documented as deliberately not parsing argv, not
dispatching and not printing usage — *"a declaration that also executed would be satisfied by its
own execution"* — so this is very nearly its whole surface. Anything else it carries is NOT declared
here. A file that later needs more gets a read of the source and a new signature here, not a widened
marker.
"""

class Mode:
    # ⚑ THE ATTRIBUTES, AND THEY ARE NARROWER THAN THE PARAMETERS BY CONSTRUCTION: `__init__`
    # runs `tuple(...)` over `opts` and `writes`, so a reader always sees a tuple regardless of
    # what a caller passed. Read from the assignments in the source, not inferred from defaults.
    operand: str | None
    paths: bool
    opts: tuple[str, ...]
    scans: bool
    writes: tuple[str, ...]
    why: str

    def __init__(
        self,
        operand: str | None = ...,
        paths: bool = ...,
        opts: object = ...,
        scans: bool = ...,
        writes: object = ...,
        why: str = ...,
    ) -> None: ...

    # ⚑ READ-ONLY BY DECLARATION. Derived from `writes` on every read; never stored.
    @property
    def mutates(self) -> bool: ...

# ⚑ THE KEY A POSITIONAL INVOCATION IS FILED UNDER, kept apart from the flag keys so it is never
# compared against argv as though it were one. Read from the module-level assignment.
POSITIONAL: str

# ⚑ RETURNS THE OPERAND SPELLING VERBATIM — `"REL [N]"`, `"{--dry-run|--apply}"` — never a
# normalised name. The source records that normalising here would be a second authority over what
# the dispatch already accepts.
def split_flag(spelling: str) -> tuple[str, str | None]: ...

# ⚑ THE TUPLE-ROSTER LIFT, deliberately lossy upward: a `(spelling, gloss)` pair carries two of
# `Mode`'s six fields, and the remaining four take defaults that are CLAIMS the gate holds the tool
# to. `pairs` is `object` because the runtime iterates any sequence of two-item sequences.
def from_pairs(pairs: object) -> dict[str, Mode]: ...
