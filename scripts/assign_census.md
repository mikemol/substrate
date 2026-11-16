# Module-level assignment types — a GENERATED census

⚑ DO NOT EDIT BETWEEN THE MARKERS. This block is derived by
`scripts/check_assign_types.py --sync` from `substrate/iface_construct.py`, which reads each
module's own assignment expressions and asks mypy to eliminate the constructor's Pi type at
those arguments. `--check` refuses a commit whose derived block differs from the committed one.

⚑ A GREEN `--check` ASSERTS A DIFFERENTIAL, NOT A TRUTH: the types derive the same way they
did at sync time, and the set of assignments is unchanged. It does NOT assert the types are
correct, and it does NOT assert they agree with `stubs/*.pyi` — see `--vs-stubs`, which is
advisory precisely because the stub is sometimes the better claim.

--- BEGIN assign-census ---

## agda_lex  (scratch/agda_lex.py)

16 of 17 assignment(s) resolved from the module's text.

    COMPUTED   NEXT: re.Pattern[str]
    COMPUTED   _DECL: re.Pattern[str]
    COMPUTED   _IMPORT: re.Pattern[str]
    COMPUTED   _OPEN: re.Pattern[str]
    COMPUTED   _VAR: re.Pattern[str]
    COMPUTED   _MODNAME: re.Pattern[str]
    COMPUTED   _PREFETCHED: dict[Any, Any]
    COMPUTED   _OBSERVED: list[Any]
    COMPUTED   BODY_DELIMS: str
    COMPUTED   _BODY_TOK: re.Pattern[str]
    COMPUTED   _PUNCT_RUN: re.Pattern[str]
    COMPUTED   SUFFIX: str
    COMPUTED   SUFFIX_LEN: int
    COMPUTED   _FILES_CACHE: dict[Any, Any]
    UNRESOLVED HEADER: -
    COMPUTED   MODULE_HEAD: re.Pattern[str]
    COMPUTED   SECTION: re.Pattern[str]

## check_carrier_locality  (scripts/check_carrier_locality.py)

6 of 6 assignment(s) resolved from the module's text.

    COMPUTED   ROOT: str
    COMPUTED   SRC: str
    COMPUTED   BASELINE: str
    COMPUTED   ALLOW: set[Any]
    COMPUTED   DECL: re.Pattern[str]
    COMPUTED   SIG: re.Pattern[str]

## check_scratch_independence  (scripts/check_scratch_independence.py)

1 of 1 assignment(s) resolved from the module's text.

    COMPUTED   ROOTS: list[str]

## gen_build_makefiles  (scripts/gen_build_makefiles.py)

9 of 9 assignment(s) resolved from the module's text.

    COMPUTED   _SNAPPED: list[Any]
    COMPUTED   ROOT: str
    COMPUTED   AGDA_DIR: str
    COMPUTED   SRC: str
    COMPUTED   MEM_CAP: str
    COMPUTED   AGDA_JOBS: str
    COMPUTED   MARKER: str
    COMPUTED   SHIM_DIR: str
    COMPUTED   IMPRE: re.Pattern[str]

## tsdbprobe  (scratch/tsdbprobe.py)

4 of 4 assignment(s) resolved from the module's text.

    COMPUTED   DEFAULT_BASE: str
    COMPUTED   DEFAULT_DEADLINE: float
    COMPUTED   DEFAULT_POLL: float
    COMPUTED   KNOWN_PRODUCERS: tuple[tuple[str, str], tuple[str, str], tuple[str, str]]
--- END assign-census ---
