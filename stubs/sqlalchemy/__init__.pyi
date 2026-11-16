"""The `sqlalchemy` Core surface this repo actually imports, typed without `Any`.

⚑⚑⚑ THE DEFECT THIS STUB REPAIRS IS TWO HAND-WRITTEN `Any`s, NOT A LIBRARY-WIDE ABSENCE.
sqlalchemy's own annotations are GOOD: `Column[int]`, `Table`, `insert()`, `tuple_`,
`is_distinct_from` and `on_conflict_do_update` all type precisely under `disallow_any_expr` and
`disallow_any_explicit`. The prior claim that "sqlalchemy Core is all `Any` under our config"
was FALSE — a fact about the method that produced it. Measured, the entire defect is:

    sql/schema.py:409               def c(self) -> ReadOnlyColumnCollection[str, Column[Any]]
    dialects/postgresql/dml.py:77   excluded, the same SHAPE but a different element type

⚑⚑ AND THAT `Any` IS INCIDENTAL, NOT NECESSARY — which is what makes the fix a SUBSTITUTION
rather than a widening. `ColumnCollection` is `Generic[_COLKEY, _COL_co]`: the dynamic string
key is `_COLKEY`, and the VALUE is a separate parameter a caller reaching `.c["name"]` never has
to guess. The library spells the value `Column[Any]` where the element class alone carries the
same information. So the edit is to name the element and drop the `Any` parameter, and
EVERYTHING ELSE KEEPS ITS GENERIC PARAMETERS.

⚑⚑ `object` IS USED FOR A TYPE PARAMETER, NEVER AS A SUBSTITUTE FOR THE ELEMENT CLASS, and the
distinction is the point. `object` is the honest top type where a parameter is genuinely
unconstrained. It is NOT used to replace `Column` or `KeyedColumnElement` — erasing a class that
IS known would turn an incidental imprecision into a permanent one, the same over-correction as
widening a signature to silence a checker.

⚑⚑⚑ WHAT IS DECLARED HERE WAS READ FROM THE LIBRARY SOURCE, NEVER FROM OUR CALL SITES, and the
distinction has already cost this tree once: `stubs/agda_lex.pyi` records a first draft that
INVENTED four names, all four caught by stubtest. A signature reconstructed from how a symbol is
used is a guess that type-checks.

⚑⚑⚑ AND `DEFINED-IN` IS NOT `EXPORTED-FROM` — THREE NAMES THE BRIEF ASSIGNED TO THIS FILE ARE
NOT DECLARED IN IT. `TypeEngine`, `KeyedColumnElement` and `ReadOnlyColumnCollection` are NOT
re-exported by `sqlalchemy/__init__.py`; they are importable only from `sqlalchemy.sql.type_api`,
`sqlalchemy.sql.elements` and `sqlalchemy.sql.base`. Declaring them here would have type-checked
green and raised `ImportError` at runtime — the exact failure the brief records happening TWICE
(`Dialect`, then `PGDialect_psycopg2`, the second read off a line where the class genuinely IS
defined). A green typecheck is not evidence of stub fidelity; `stubtest` is.

⚑⚑⚑ AND THIS FILE THEN DID IT ANYWAY, IN THE IMPORT BLOCK BELOW THE PARAGRAPH THAT FORBIDS IT
(Ⓝ128c, 2026-09-03). All three names were spelled `X as X` — the re-export form — so a consumer
writing `from sqlalchemy import TypeEngine` type-checked green and raised `ImportError`. The
prose was right and the code was wrong, in one file, for the whole life of the file: a
declaration and its own counterexample, three lines apart. The four prior instances of this
class were all found in a DECLARATION; this one was on the RE-EXPORT LIST, which is a surface
nothing was reading.

⚑⚑⚑ STUBTEST CANNOT SEE THIS, AND THAT IS STRUCTURAL RATHER THAN A CONFIGURATION MISS. It
compares RUNTIME→STUB: it enumerates the runtime module's attributes and asks what the stub
says about each. A name the stub exports and the runtime does NOT have is not in the population
it iterates, so it is never asked about. MEASURED: a fabricated `GhostExport` re-export was
added to this file and `check_stub_authority.py` reported `clean (10 of 10)`. Every one of the
16 findings on a bare run reads `is not present in stub`; not one reads `not present at
runtime`. `--ignore-missing-stub` is NOT the cause — the direction is.

⚑⚑ SO THE SETTLING INSTRUMENT IS A `getattr` PROBE ON THE IMPORTED MODULE, and it is the
acceptance criterion this repair was verified against — not a typecheck, and not this gate.
`substrate/stub_reexport.py` owns that reading; see it for the population and the discriminator.

⚑⚑ SO THE DEFINITIONS LIVE IN THE SUBMODULE STUBS AND THIS FILE RE-EXPORTS ONLY WHAT THE
RUNTIME ALSO EXPORTS, MIRRORING THE LIBRARY'S OWN LAYOUT — and that too is a repair of a
measured failure. A first draft DEFINED `ColumnElement` and `Column` here while importing
`ReadOnlyColumnCollection` from the unstubbed `sqlalchemy.sql.base`; mypy then checked this
stub's `Column` against the REAL library's `ColumnElement[Any]` bound — two different classes
sharing a name — and refused all three collection returns. A stub graph that reaches outside
itself for a bound is not self-consistent.

⚑ THE THREE NON-EXPORTED NAMES ARE STILL IMPORTED, because this file's own annotations refer to
them (`Table.c` returns a `ReadOnlyColumnCollection`). A plain `from X import Y` is a private
reference; only the `Y as Y` form re-exports. The distinction is the entire repair: the names
remain usable HERE and are no longer claimed to be reachable from `sqlalchemy`.

⚑⚑ THE STATEMENT SURFACE IS NOW PARTIALLY DECLARED, IN THE SUBMODULES THAT DEFINE IT (W19,
2026-09-20) — and only the attributes one consumer READS, each transcribed from the library:
`sql/visitors.pyi` (`iterate`, `ExternallyTraversible.get_children`), `sql/dml.pyi`
(`Insert`/`Update`/`Delete` with `table` and `_returning`, plus the `(self, table)` constructors
stubtest demanded), `sql/selectable.pyi` (`Select.selected_columns`, the `Alias`/`Subquery`/`CTE`
`element`), and `Column.table` in `sql/schema.pyi`. The consumer is `substrate/sql_statement.py`,
which walks a compiled builder to say what it reads, writes and returns. None of these names is
re-exported from HERE; the runtime does not export `iterate` or `UpdateBase` at the package root
either, and this file re-exports only what the runtime does.

⟡declines: the rest of the query and DML surface — every constructor (`select()`, `insert()`,
`update()`, `delete()`), the generative methods, `Join`, `CompoundSelect`, `TextualSelect` —
engine and connection (`create_engine`, `Engine`, `Connection`, `Result`), the entire ORM
(`Mapped`, `DeclarativeBase`, `Session`, `relationship`), `event`, schema reflection, the
connection pool, and the expression constructors this repo does not call (`func`, `case`,
`cast`, `literal`, `text`). Each is a surface no consumer here imports; a stub that claimed
them would be asserting signatures nobody has read.
"""

from collections.abc import Collection, Sequence
from typing import Self

# ⚑ THE `X as X` FORM IS A RE-EXPORT CLAIM; A PLAIN `import X` IS A PRIVATE REFERENCE. The three
# names the runtime does NOT export are imported plainly, so this stub can still annotate with
# them without asserting `from sqlalchemy import X` resolves. Verified by `substrate/stub_reexport`
# against the live module, which is the only instrument that answers EXPORTED-FROM.
from sqlalchemy.sql.base import ColumnCollection as ColumnCollection
from sqlalchemy.sql.base import ReadOnlyColumnCollection
from sqlalchemy.sql.elements import ColumnElement as ColumnElement
from sqlalchemy.sql.elements import literal as literal
from sqlalchemy.sql.elements import KeyedColumnElement
from sqlalchemy.sql._elements_constructors import bindparam as bindparam
from sqlalchemy.sql._selectable_constructors import select as select
from sqlalchemy.sql.functions import func as func
from sqlalchemy.sql.schema import Column as Column
from sqlalchemy.sql.selectable import FromClause
from sqlalchemy.sql.type_api import TypeEngine

class Text(TypeEngine[str]): ...
class Integer(TypeEngine[int]): ...
class BigInteger(Integer): ...

class Constraint:
    """A table-level SQL constraint — the base `append_constraint` accepts.

    ⚑ THE CONSTRUCTOR IS DECLARED RATHER THAN DECLINED, because it is short enough to state
    honestly. The private `_create_rule` / `_type_bound` parameters are omitted deliberately:
    they are upstream internals, and `**dialect_kw` absorbs the remainder the way the runtime
    does. Read from `sql/schema.py:4106`, not reconstructed from a call site.
    """

    name: str | None
    def __init__(
        self,
        name: str | None = None,
        deferrable: bool | None = None,
        initially: str | None = None,
        info: dict[str, object] | None = None,
        comment: str | None = None,
        **dialect_kw: object,
    ) -> None: ...

class Index:
    """A table index — declared only as a referent of `Table.append_constraint`.

    ⚑ NOTHING IN THIS REPO CONSTRUCTS AN `Index`, so its constructor is declined by name rather
    than transcribed. The runtime signature is a long `*expressions` form with eight keyword
    parameters whose types this stub does not declare; inventing it would assert a surface no
    consumer here has read, which is the `agda_lex.pyi` failure.

    ⟡declines-signature: sqlalchemy.Index.__init__
    """

class PrimaryKeyConstraint(Constraint):
    """A table's primary key — its own constructor, NOT the one inherited from `Constraint`.

    ⚑⚑ STUBTEST CAUGHT THIS AS A KEYWORD-ONLY MISMATCH, AND IT IS A REAL BREAK RATHER THAN A
    formality. Declaring only `Constraint.__init__` left this class inheriting a signature whose
    `name`/`deferrable`/`info` are POSITIONAL; the runtime override leads with `*columns`, which
    makes every one of them keyword-only. A caller writing `PrimaryKeyConstraint("pk")` would
    have type-checked clean and bound `"pk"` to a column argument at runtime.

    ⚑ WHICH IS THE WHOLE ARGUMENT FOR RUNNING STUBTEST. Nothing about this is visible from a
    call site, from the base class, or from a green typecheck; only a comparison against the
    live signature reports it.
    """

    # ⚑ THE SUBSTITUTION, FIRST OF THREE. Upstream is `ReadOnlyColumnCollection[str,
    # Column[Any]]`; the element stays `Column` and only the `Any` PARAMETER becomes `object`,
    # so a reader gets a real class back rather than a hole.
    #
    # ⚑ IT IS INHERITED UPSTREAM, not defined on this class — the annotation lives on
    # `ColumnCollectionConstraint` (`sql/schema.py:4399`). It is declared here because this is
    # the class a consumer reaches it through.
    columns: ReadOnlyColumnCollection[str, Column[object]]
    def __init__(
        self,
        *columns: str | Column[object],
        name: str | None = None,
        deferrable: bool | None = None,
        initially: str | None = None,
        info: dict[str, object] | None = None,
        **dialect_kw: object,
    ) -> None: ...

class Table(FromClause):
    """A described table — constructed as `Table(name, metadata, *columns)`.

    ⚑ A `FromClause` (W39c), AS UPSTREAM: `Table(DialectKWArgs, HasSchemaAttr, TableClause)` and
    `TableClause` derives from `FromClause` (`sql/schema.py`, `sql/selectable.py`). Declaring the
    base is what gives a table the `join`/`outerjoin`/`alias` a cleanroomed builder composes with.
    `c` below NARROWS the base's `KeyedColumnElement` element to `Column`, which upstream also does.

    ⚑⚑ EVERY KEYWORD IS DECLARED, AND `**kw` DOES NOT ABSORB THEM — STUBTEST SAID SO. A draft
    declared the two positional parameters and left the rest to `**kw`; the gate reported
    `autoload_with`, `autoload_replace` and the others as missing one pair at a time. A named
    keyword in the runtime is part of the signature a caller can spell, so a stub that hides it
    behind `**kw` types `Table(..., autoload_wtih=e)` as acceptable. The completeness is the
    gate's, not a preference.

    ⚑ THE TYPES ARE NARROWED WHERE THIS STUB DECLINES THE REFERENT. `autoload_with` is
    `Engine | Connection` upstream and both are declined here, so it is `object`: the parameter
    EXISTS with the right name and arity, and its type says only that this stub does not
    describe what goes in it. That is weaker than upstream and honest about being so — unlike
    omitting it, which would have been wrong about whether it exists.

    ⚑ `*args` IS `SchemaItem` UPSTREAM, narrowed here to what is actually passed: columns and
    constraints. The narrowing is stated because it IS one.

    ⚑⚑ TWO FINDINGS ARE DECLINED BY NAME BELOW, AND BOTH ARE STRUCTURAL RATHER THAN SLOPPY.
    `Table.__new__` exists at runtime as `(*args, **kw)` because `Table` implements the
    keep-existing/extend-existing protocol by intercepting construction; declaring it would put
    a second, weaker constructor beside `__init__` and let any argument list through.

    `Table.c` and `Table.columns` are `sqlalchemy.util.langhelpers._memoized_property`
    descriptors, not plain `@property` objects, and stubtest cannot reconcile the two. The
    RETURN TYPE is the whole reason this stub exists — it is the site of the library's
    `Column[Any]` — so the exemption is on the DESCRIPTOR KIND, named per attribute, and the
    type it yields is still checked wherever a consumer reads it. A blanket flag would have
    silenced the return type too.

    ⟡declines-signature: sqlalchemy.Table.__new__, sqlalchemy.Table.c, sqlalchemy.Table.columns,
        sqlalchemy.Table.primary_key
    """

    name: str
    def __init__(
        self,
        name: str,
        metadata: MetaData,
        *args: Column[object] | Constraint,
        schema: str | None = None,
        quote: bool | None = None,
        quote_schema: bool | None = None,
        autoload_with: object = None,
        autoload_replace: bool = True,
        keep_existing: bool = False,
        extend_existing: bool = False,
        resolve_fks: bool = True,
        include_columns: Collection[str] | None = None,
        implicit_returning: bool = True,
        comment: str | None = None,
        info: dict[str, object] | None = None,
        # ⚑ THE CALLBACK IS `Callable[..., Any]` UPSTREAM, AND `...` IS ITSELF AN IMPLICIT `Any`
        # — the gate refused it under `explicit-any`. `object` names a parameter this stub does
        # not describe, which is the same honest weakening applied to `autoload_with`.
        listeners: Sequence[tuple[str, object]] | None = None,
        prefixes: Sequence[str] | None = None,
        **kw: object,
    ) -> None: ...
    # ⚑ THE SUBSTITUTION, SECOND AND THIRD. `.c` and `.columns` are the accessors this repo
    # reaches, and they are the exact pair carrying `Column[Any]` upstream.
    #
    # ⚑⚑ UPSTREAM DECLARES BOTH ONLY UNDER `if TYPE_CHECKING:`, NARROWING `FromClause`'s runtime
    # `KeyedColumnElement` to `Column`. This stub keeps the narrowed form because it is what a
    # caller sees and what the library intends; the wider runtime type is not what any consumer
    # here relies on.
    @property
    def c(self) -> ReadOnlyColumnCollection[str, Column[object]]: ...
    @property
    def columns(self) -> ReadOnlyColumnCollection[str, Column[object]]: ...
    @property
    def primary_key(self) -> PrimaryKeyConstraint: ...
    def append_constraint(self, constraint: Index | Constraint) -> None: ...

class MetaData:
    """The collection of `Table` objects a schema is described by.

    ⚑ `tables` IS A CLASS-LEVEL ANNOTATION UPSTREAM, NOT A PROPERTY (`sql/schema.py:5558`), and
    its real type is `util.FacadeDict[str, Table]` — a read-only mapping facade. It is declared
    here as `dict[str, Table]` because that is the surface a reader consumes (`in`, `[]`,
    `.items()`) and `FacadeDict` is not a name this stub declares. The narrowing is stated
    rather than silent: a caller cannot MUTATE this mapping at runtime, and this annotation
    would not stop them from trying.
    """

    tables: dict[str, Table]
    def __init__(
        self,
        schema: str | None = None,
        quote_schema: bool | None = None,
        naming_convention: dict[str, object] | None = None,
        info: dict[str, object] | None = None,
    ) -> None: ...

class Tuple(ColumnElement[object]):
    """A SQL tuple expression — what `tuple_()` returns.

    ⚑ THE CONSTRUCTOR MIRRORS `tuple_`, because upstream it is the same signature: `*clauses`
    plus an optional `types`. Declaring both keeps the two spellings of one construction in
    agreement, which is what stubtest checks.
    """

    def __init__(
        self,
        *clauses: ColumnElement[object],
        types: Sequence[TypeEngine[object]] | None = None,
    ) -> None: ...

# ⚑ THE RETURN IS SQLALCHEMY'S OWN `Tuple` CLASS, NOT `typing.Tuple`, and upstream leaves it
# unparameterised. The library aliases `typing.Tuple` as `typing_Tuple` in its own modules
# precisely because of this collision.
def tuple_(
    *clauses: ColumnElement[object],
    types: Sequence[TypeEngine[object]] | None = None,
) -> Tuple: ...

class Compiled:
    """A compiled statement — obtained from `.compile()`, never constructed here.

    ⚑⚑ THE CONSTRUCTOR IS DECLINED BY NAME, AND STUBTEST FOUND IT RATHER THAN A REVIEWER. The
    runtime `__init__` takes `(dialect, statement, schema_translate_map, render_schema_translate,
    compile_kwargs)`; this stub declares none of them, and the gate reported the mismatch on two
    parameters. That is a REAL contradiction, so it is exempted by NAMING it — not by a blanket
    flag, and not by inventing a five-parameter signature whose types (`Dialect`,
    `ClauseElement`, `SchemaTranslateMapType`) this stub does not declare and no consumer here
    passes.

    ⚑ THE COST IS DECLARED WITH THE RELIEF: a caller cannot CONSTRUCT a `Compiled` through this
    stub. That is correct for this repo — a compiled object arrives from `statement.compile()`
    and `.params` is read off it — and it is exactly the sort of editorial judgement the
    `⟡declines-signature:` marker exists to put in front of a reviewer.

    ⟡declines-signature: sqlalchemy.Compiled.__init__
    """

    # ⚑ UPSTREAM GIVES THIS NO ANNOTATION AT ALL — a bare `@property` returning
    # `self.construct_params()`. So this type is a READING, not a transcription, and
    # `check_stub_authority`'s own docstring names that limit: stubtest compares names and arity
    # but cannot verify a type the source never states. Recorded rather than presented as
    # measured.
    @property
    def params(self) -> dict[str, object]: ...

class Insert:
    """A Core INSERT statement — the base the PostgreSQL `Insert` extends.

    ⚑ THE CONSTRUCTOR TAKES THE TABLE, matching the runtime (`sql/dml.py:1251`). Upstream types
    it `_DMLTableArgument`, a union admitting a `Table`, a text clause or an ORM entity; this
    stub narrows it to `Table`, which is the only form any consumer here passes. The narrowing
    is deliberate and stated — a stub that widened to the full union would be claiming support
    for ORM entities this stub declines entirely.
    """

    def __init__(self, table: Table) -> None: ...
    # ⚑⚑⚑ `Self`, NOT `Insert`, AND THE DIFFERENCE IS LOAD-BEARING RATHER THAN STYLISTIC.
    # Upstream returns `Self` (`sql/dml.py:1033`, `ValuesBase.values`), and this stub declared
    # `Insert` — which SILENTLY DOWNCASTS the PostgreSQL subclass. `insert(t).values(...)` then
    # types as the base, and `.on_conflict_do_update` / `.excluded` — the entire reason the
    # postgresql stub exists — report `has no attribute` on the chained form every real caller
    # writes. The postgresql stub's own note says `Insert` is exact "because nothing subclasses
    # the pg `Insert`", which is true THERE and false HERE: this is the base, and the pg class is
    # precisely its subclass. One narrowing argued correctly at one site, copied to the site where
    # its premise does not hold.
    def values(self, *args: object, **kwargs: object) -> Self: ...
    # ⚑ READ FROM `sql/elements.py:250` (`ClauseElement.compile`), where it is INHERITED rather
    # than defined on `Insert`. It is declared here because this is the class every consumer
    # reaches it through, and because a statement that cannot be compiled cannot be rendered —
    # which is the whole observable of a compiler layer.
    #
    # ⚑ `bind` IS `_HasDialect` UPSTREAM AND `dialect` IS `Dialect`; BOTH ARE DECLINED BY THIS
    # STUB, so both are `object` — the parameter EXISTS with its real name and arity, and its type
    # says only that this stub does not describe what goes in it. The same honest weakening
    # applied to `Table.autoload_with`, and weaker than upstream on purpose.
    def compile(
        self, bind: object = None, dialect: object = None, **kw: object,
    ) -> Compiled: ...

def insert(table: Table) -> Insert: ...
