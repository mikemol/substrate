# Ⓝ31 residue — ⟡symbolic-reference-only

**Concern: the principle that nothing is identified by a number, and the 67-file
`NamedTuple` → slotted-dataclass migration that made the type checker enforce it.**
Index and arc frame: [`toolmodes-split.md`](toolmodes-split.md).

⚑ Ⓝ31q named the erasure reflex (`object` forces `getattr`, which reintroduces the `Any` the
erasure was meant to avoid); Ⓝ31s established the CPython mechanism byte-cited, measured the
population, and converted the first files by hand; Ⓝ39 caught the reader that would have ordered
the migration wrongly; Ⓝ62 censused what the conversion actually removed. **The pipeline that
performed the batch is [the codemod pipeline](toolmodes-residue-the-codemod-pipeline.md)**; the
false-zero class Ⓝ39 belongs to is [false zeros](toolmodes-residue-false-zeros.md).

⚑⚑ **THIS DOCUMENT'S OWN FILENAME CARRIED THE DEFECT IT ARGUES AGAINST, AND SO DID THOSE TWO
CITATIONS.** It was `toolmodes-residue-03-symbolic-reference-only.md`, and the two pointers above
read *"part 4"* and *"part 7"* — positions standing in for identities, in the record of
⟡symbolic-reference-only. Inserting one document ahead of them would have renumbered both. The
concern is the identity; see Ⓝ85 in
[writing the record](toolmodes-residue-writing-the-record.md).

## Residue

* ⚑⚑⚑ **Ⓝ31q ⟡erasure-pays-for-itself — `hasattr`/`getattr` WERE AN ARTIFACT OF `object`, NOT A
  REQUIREMENT.** Operator, 2026-09-01, mid-turn: *"You shouldn't need hasattr or getattr. Things
  like TypedDict should do what you're looking for."* and *"God, I'd love to stop seeing `object`
  and `str` all over; they obscure structure..."*

  **Both are one diagnosis, and the second explains the first.** `default_get` probes a row at
  runtime — mapping key, then attribute, then positional index — ONLY because the row was typed
  `object`. Having erased the structure, the code must re-discover it dynamically; the dynamic
  access then re-introduces the `Any` the erasure was supposed to avoid. **The field-resolution
  layer exists to pay for its own type.** Measured across the split: 411 findings → 5 → 1, and
  the last one was `getattr` — the erasure's final invoice.

  ⚑⚑ **AND `str` FOR A FIELD NAME IS THE SAME ERASURE ONE LEVEL DOWN.** A `SortKey` over
  arbitrary strings can name a field the row does not have, which is precisely the `OrderError`
  I then had to write and test. Under a row type whose fields are known, **that error is
  UNCONSTRUCTIBLE** — the case disappears rather than being handled. Two of `sort_key`'s
  eighteen cases (`an_unresolvable_field_names_the_row`, and half of the shape-order arm) exist
  only to defend a hole the type should have closed.

  **MEASURED — the convention is absent, not departed from:** `pycodemod --binding TypedDict`
  over `substrate/` + `jea/metalanguage/` + `scripts/` returns **0 bindings in 0 of 432 files**.
  (`toolmodes --find typeddict` returns 0 hits, but that index cannot see `substrate/` at all —
  a fact about the index, filed under Ⓝ31.)

  ⚑ **STATUS: `substrate/sort_key.py` IS LANDED AND CLEAN (0 type keys) AND IS THE WRONG DESIGN.**
  Saying so now is cheaper than building four layers on it. It stands as the faithful re-typing
  of the original — which is what made the erasure legible — but the carrier should be generic
  over the ROW, with field names drawn from that row's own structure, so that `default_get`,
  `as_cell`, `OrderError`-on-missing-field and the `Cell` protocol itself either disappear or
  shrink to a boundary the caller crosses once.

  ⚑⚑ **AND THIS IS THE N-SPLIT LESSON ARRIVING AT TYPES.** The operator's earlier correction —
  *"this indicates the file is doing too much, and needs to be n-split"* — took 411 findings to 1
  by SEPARATING CONCERNS. This one takes the remaining 1 to 0 by NOT ERASING THE CONCERN'S TYPE.
  Same move, different axis: a monolith hides structure across files, `object` hides it within
  one, and both make a reader re-derive at runtime what was known at authoring time.


* ⚑⚑⚑ **Ⓝ31s ⟡symbolic-reference-only — THE PRINCIPLE, STATED BY THE OPERATOR, AND IT IS WIDER
  THAN THE GUARDS THAT IMPLEMENT IT.** 2026-09-01: *"we don't use index numbers in order to
  identify things. We don't say argv[1]. We don't access array elements by number. We use field
  names. We use named slots. We use symbolic references."*

  I had reconstructed a weaker version from the tree — `check_argv`'s keyword-only `mutates`/
  `needs_store` (*"passing them positionally lets a caller TRANSPOSE them"*), `bibstruct --bib`
  (*"a FLAG and not a trailing positional"*), `consumer.lwm`'s deletion (*"a POSITION standing in
  for an IDENTITY"*), the integer-keyed roster that silently dropped `retire`. **Those are
  INSTANCES, not the rule.** The rule is that numeric indexing is not how anything is identified,
  and each of those guards is what it looks like locally.

  ⚑⚑ **AND MY OWN CODE VIOLATED IT IN FOUR PLACES, ONE OF WHICH I DEFENDED IN A COMMENT.**
  `sort_key.default_get` ends `if name.isdigit(): return as_cell(row[int(name)])` — a field NAMED
  `"1"` resolving to SLOT 1 — and I wrote a ⚑ note above it explaining the precedence between
  name-lookup and index-lookup, treating the collision as a subtlety to get right rather than as a
  branch that should not exist. Inherited from the original, then rationalised. Also: `group`'s
  `getter=lambda row, _name: row[0]`, its output key spelled `f"0.{name}"` (a STRING ENCODING A
  POSITION), and `from_dict`'s *"'0' is the mapping key, '1' the value"*.

  ⚑ **A PROBE WRITTEN TO STUDY THE DEFECT CONTAINED THE DEFECT.** The first `slots_probe.py` used
  `sorted(...)[0]` to take a minimum; ruff flagged it (FURB192, prefer `min`). Indexing to get an
  element, while looking straight at the problem.

  ⚑⚑ **THE MEASURED CONSEQUENCE — AND IT MAKES THE MIGRATION SELF-ENFORCING.** A
  `@dataclass(frozen=True, slots=True)` instance is NOT unpackable: mypy reports `Cannot determine
  type of "one"` for `one, two, three = obj`, and is not orderable without `order=True`
  (`Value of type variable "SupportsRichComparisonT" of "min" cannot be "AsSlotted"`). So
  converting the landed records from `NamedTuple` turns **every positional-destructuring site into
  a STATIC error that names itself** — the type checker becomes the enforcement rather than the
  convention being something a reader must remember. `order=True` restores comparison derived from
  FIELD DECLARATION ORDER, which is the legitimate use of order (a comparison sequence) with no
  numeric access anywhere.

  ⚑ **SOURCE-GROUNDING IN FLIGHT.** Asked `linux-sources` (enrolled delegate, `speaks=cross-
  session`) for the CPython mechanism rather than asserting it from one mypy run: whether
  `__slots__` touches the sequence protocol at all, how `UNPACK_SEQUENCE` falls back to `__iter__`,
  and whether `@dataclass(slots=True)` does anything beyond setting `__slots__`. **One local
  observation is not a mechanism** — the same distinction as `plan_notes_are_hypotheses`.

* ⚑ **Ⓝ31q RENAMED — `⟡erasure-is-a-reflex`, NOT `⟡erasure-pays-for-itself`.** Operator: *"Sounds
  like you're intentionally erasing?"* No — and the tag implied a considered tradeoff. I reached
  for `object` as a safe default when I could not immediately name the row type, and it FELT like
  generality. Naming it intentional flatters it; it was a reflex, and the honest tag says so.

* ⚑⚑ **AND I OVERCORRECTED ON `Protocol`, WHICH IS THE HOUSE STYLE.** I said I had introduced
  `Cell` unilaterally. MEASURED (`pycodemod --binding` over `substrate/` + `scripts/` +
  `jea/metalanguage/`, 432 files): **`Protocol` 14 bindings in 14 files · `ABC` 0 · `TypedDict`
  0.** The tree's convention is STRUCTURAL typing, so `Cell` was in-convention. The erasure was
  never the Protocol — it was typing the ROW as `object`, which forced `hasattr`/`getattr` to
  rediscover a shape that was known at authoring time. Two separable things, conflated by me in
  both directions within three turns.

  ⚑ **ABC IS OUT ON MERIT, NOT HABIT:** nominal typing would require the caller's rows to inherit
  from us, which cannot be asked of `str`/`int`/`tuple`. Zero uses in 432 files is consistent.
  But the ABC prompt landed on something real anyway — `Rev`'s four hand-written dunders with
  their `NotImplemented` returns are what `functools.total_ordering` exists to delete.

* ⚑⚑⚑ **Ⓝ31s — THE SLOTS MECHANISM IS SOURCE-CONFIRMED, AND IT CORRECTS THE HYPOTHESIS IN THE
  DIRECTION WE WANT.** Asked `linux-sources` (enrolled delegate, `speaks=cross-session`) rather
  than asserting from one mypy run. It pinned CPython **v3.13.1**
  (`067145177975eadd61a0c907d0d177f7b6a5a3de`) and answered byte-cited:

  - **`__slots__` adds NO sequence/iterator protocol.** `Objects/typeobject.c:type_new_descriptors`
    (3903) builds a `PyMemberDef` per slot — `Py_T_OBJECT_EX` at a fixed struct offset — and
    installs them as `tp_members`; `type_new_set_slots` (3946) wires
    `tp_getattro`/`tp_setattro` to the generic getattr. **Nothing touches `tp_iter`,
    `tp_as_sequence`, `tp_as_mapping`, `sq_item` or `mp_subscript`.**
  - **`a, b, c = obj` requires the iterator protocol.** `Python/compile.c:4504` emits
    `UNPACK_SEQUENCE`; `Python/bytecodes.c:1257` calls `_PyEval_UnpackIterable`, which
    (`Python/ceval.c:2057`) opens `it = PyObject_GetIter(v)` and raises *"cannot unpack
    non-iterable %.200s object"* when `tp_iter == NULL && !PySequence_Check(v)`. The
    `UNPACK_SEQUENCE_TUPLE/LIST/TWO_TUPLE` opcodes are specializations that `DEOPT_IF` the object
    is not an EXACT tuple/list, so anything else takes the generic path.
  - **`@dataclass(slots=True)` does only `__slots__` + rebuild.** `Lib/dataclasses.py:_add_slots`
    (1222) computes `cls_dict["__slots__"]`, pops the field attrs and `__dict__`/`__weakref__`,
    rebuilds via `type(cls)(...)` (1263). The ONLY addition is `__getstate__`/`__setstate__`, and
    only when frozen, purely for pickling (1267-1272).
  - **`order=True` compares by FIELD DECLARATION ORDER, symbolically.** `Lib/dataclasses.py`
    1122-1141 generates `(self.x, self.y, …) OP (other.x, other.y, …)` over
    `[f for f in field_list if f.compare]`, and `fields()` is *"sorted by insertion order"*
    (1321). It reads each field BY NAME into an internal tuple; the instance stays non-indexable.
    **Comparison-as-sequence and element-access-as-numeric are separable, and CPython separates
    them.**

  ⚑⚑ **THE OPERATOR'S HYPOTHESIS WAS FALSE, AND FALSE IN THE USEFUL DIRECTION.** *"I think if you
  use slots, you don't have to change anything?"* — `__slots__` does the OPPOSITE of preserving
  positional access: it removes tuple-ness entirely, which `NamedTuple` had only by subclassing
  `tuple`. **So there is no gradual migration via slots; the conversion is a clean break that
  surfaces every site AT ONCE, STATICALLY.** That is the stronger migration property, not a
  weaker one — the type checker becomes the enforcement rather than the convention being
  something a reader must remember.

  ⚑ **AND THE TWO CHECKERS AGREE FOR ONE REASON.** mypy says `Cannot determine type of "one"`;
  the interpreter says `TypeError: cannot unpack non-iterable`. Different text, identical cause —
  no `__iter__`, no sequence protocol. A local observation plus a source read is a MECHANISM; the
  observation alone was a hypothesis (`plan_notes_are_hypotheses`, applied to my own measurement).

  ⚑ **ESCAPE VALVE, IF EVER NEEDED:** `dataclasses.astuple(obj)` (`Lib/dataclasses.py:1430`)
  yields the field values as a tuple BY NAME — a symbolic, function-named conversion, not
  `obj[0]`. Reintroduces no instance indexing.

  **The shape to convert to:** `@dataclass(frozen=True, slots=True, order=True)` — immutable, no
  positional access, symbolic-only, with a legitimate declaration-ordered comparison.


* ⚑⚑ **Ⓝ31s SCOPE — MEASURED: 67 FILES, A QUARTER OF THE PACKAGE.**
  `pycodemod --binding NamedTuple substrate/` → **67 bindings in 67 of 259 files**. Every landed
  census layer is in it (`tool_census`, `tool_overlap`, `tool_gap`, `tool_find`, `tool_cli`,
  `tool_block`, `tool_decline*`, `tool_convention*`, `page`), and so is the ratchet family
  (`ratchet_core`, `ratchet_census`, `ratchet_family`, `ratchet_log`, `ratchet_render`), the suite
  family, and the md family.

  **This is a migration, not an edit.** Two properties make it tractable and one makes it
  expensive:
  - MECHANICAL: `class X(NamedTuple)` → `@dataclass(frozen=True, slots=True, order=True)`, and the
    field declarations are unchanged.
  - SELF-LOCATING: the conversion makes every positional-destructuring site a STATIC error naming
    its own file and line, so the work list is generated rather than searched for.
  - EXPENSIVE: the per-file gate has NO PARTIAL CREDIT. Each of the 67 must land clean in ONE pass,
    and a refusal reverts the whole file. Measured today across four attempts on one 380-line
    module — the cost is real and it compounds over 67.

  ⚑ **THE ORDER IS FORCED BY THE DEPENDENCY DIRECTION, NOT BY PREFERENCE.** A record's consumers
  break when it converts, so a leaf record with few consumers is cheap and a widely-consumed one
  (`tool_census.Tool`, `ratchet_core`'s records) cascades. Convert LEAF-FIRST and the errors stay
  local; convert root-first and one commit is 67 files wide.

  ⚑ **AND `order=True` IS NOT UNIFORMLY CORRECT.** It derives comparison from DECLARATION ORDER,
  which is right where a record is sorted (`Declared`, `Keyed`, the census rows) and meaningless
  where one is not. Adding it everywhere would assert an ordering nobody intends — the
  `census-green-is-a-fact-about-the-census` shape, one axis over. **Per-record decision, not a
  blanket flag.**

  **NOT STARTED — this needs a scoping call.** A 67-file migration begun mid-turn is exactly the
  work-scaling decision that belongs to the operator. What is ready: the mechanism is
  source-confirmed (above), the shape is decided, and the population is measured.

* ⚑⚑⚑ **Ⓝ39 ⟡importers-blind-to-from-import — `pycodemod --importers` REPORTS 0 WHERE
  `--binding` REPORTS 7, AND I WAS ABOUT TO ORDER A 67-FILE MIGRATION ON IT.**

      pycodemod --importers tool_census            → 0 import site(s) in 0 of 1122 file(s)
      pycodemod --importers substrate.tool_census  → 0 import site(s) in 0 of 1122 file(s)
      pycodemod --binding   tool_census substrate/ → 7 binding(s) in 7 of 259 file(s)

  The seven are real and were read directly this session (`tool_gap.py:51` imports
  `tool_overlap`, every `*_selftest.py` imports its layer). **`--importers` does not see
  `from substrate import tool_census`** — which is how every file in this package imports.

  ⚑⚑ **THE CONSEQUENCE HAD I TRUSTED IT: every record reads as a LEAF WITH NO CONSUMERS**, so a
  leaf-first conversion order derived from it would have been arbitrary — and would have hit the
  most-consumed records first, maximising exactly the cascade the ordering exists to avoid. A
  zero from the wrong reader does not look wrong; it looks like good news.

  ⚑ **CAUGHT ONLY BY CROSS-CHECKING A SECOND SPELLING**, which is the `census-keyed-on-one-
  spelling` discipline applied on purpose rather than by luck. The mode's own docstring advertises
  the capability `--imports` only COUNTS — *"every file that IMPORTS <module>, with the NAMES it
  binds"* — so the gap is in the matcher, not the intent. **A missing import FORM is not a
  missing capability; it is a bug in the one that exists.**

* ⚑⚑ **Ⓝ31s″ ⟡leaf-order-census — MEASURED, AND THE DEPENDENCY GRAPH IS FLATTER THAN ASSUMED.**
  Using `--binding` (the corroborated reader):

      tool_census    7 consumers — ALL SEVEN ARE SELFTESTS
      tool_overlap   2 consumers — tool_gap.py:51, plus its own selftest

  **The layers barely import each other.** Most consumers of any given record module are its own
  suite, so converting a record breaks its suite and little else. **The cascade risk behind the
  "67 files wide" framing is much lower than the file count suggests** — 67 files hold a
  `NamedTuple`, but they do not hold each other's.

  ⚑ **WHICH CHANGES THE ORDERING QUESTION FROM STRATEGIC TO CLERICAL.** Leaf-first vs root-first
  matters when conversion cascades; here each conversion is nearly self-contained (module + its
  suite). The real sequencing constraint is the per-file gate's no-partial-credit rule, not the
  import graph — so the order should follow whatever minimises RISK PER LANDING, i.e. smallest
  and least-consumed first, to build confidence in the mechanical transform before applying it to
  `tool_census.Tool` (7 suites) or the ratchet family.

* ⚑⚑⚑ **Ⓝ31s FIRST CONVERSION — `tool_gap.py`, NOT LANDED, AND IT PAID OFF ANYWAY: THE CHECKER
  CAUGHT AN UNDECLARED ORDERING ON THE FIRST FILE.**

  `capability_gaps` (`tool_gap.py:143`) contains `tuple(sorted(Coverage(...) for tool in have))`
  — **no key**. Under `NamedTuple` that sorted by `tuple`'s field-position comparison:
  `(relpath, modes_with_kind, modes_total, modes)`, an order nobody wrote down and which exists
  only as an accident of declaration order. Converting to a slotted dataclass made mypy refuse it:

      Value of type variable "SupportsRichComparisonT" of "sorted" cannot be "Coverage"

  **That is the migration's whole thesis, demonstrated on file one.** The by-position ordering was
  invisible, unintended, and load-bearing on nothing anyone had decided; the conversion turned it
  into a static error demanding a NAMED key. ⚑ And it is why `order=True` must NOT be applied
  blanket — it would restore exactly the by-position comparison just removed.

  ⚑⚑ **THE PER-FILE CONVERSION IS ATOMIC AND I SPLIT IT SIX TIMES.** One file needs, in ONE edit:
  the import swap (`NamedTuple` → `dataclass`), EVERY class declaration in the file, AND every
  consequence the change surfaces (here: the keyless `sorted`). Each partial edit is refused and
  **reverts the whole file**, so a split attempt costs a full re-derivation. Measured: six calls,
  nothing landed, on a 135-line file with three records.

  **THE PROCEDURE, for the remaining 66:**
  1. `pycodemod --layout <file>` — every class, so none is missed.
  2. `pycodemod --binding <module> substrate/` — the consumers (NOT `--importers`, see Ⓝ39).
  3. Read the file, compose ONE edit covering import + all classes.
  4. Expect the checker to surface undeclared orderings (keyless `sorted`/`min`/`max` over the
     record) and positional unpacks — fix them IN THE SAME EDIT.
  5. Run the suite; convert its fixtures if it constructs records positionally.

  ⚑ **AND STEP 4 IS THE VALUE, NOT THE COST.** Every finding it raises is a place where meaning
  was carried by field position. `tool_gap` had one in three records; extrapolating is not
  warranted, but a zero would have been surprising.


* ✅ **Ⓝ31s — FILE 1 OF 67 LANDED: `substrate/tool_gap.py`, suite 11/11 unchanged.**
  Three records converted `NamedTuple` → `@dataclass(frozen=True, slots=True)`, and the checker
  surfaced exactly one consequence, which was the point of doing it.

  **THE FINDING:** `capability_gaps` sorted `Coverage` values with **NO KEY**. Under `NamedTuple`
  that resolved to `tuple`'s field-position comparison — `(relpath, modes_with_kind, modes_total,
  modes)` — an ordering nobody wrote down, which happened to lead with `relpath` and so happened
  to be alphabetical. **A correct-looking result nobody chose, and one a field reorder would have
  changed silently.** It now sorts by `Coverage.rank`, a named method that says what the order IS.

  ⚑ `order=True` NOT USED, and this file is why: it would restore precisely the by-position
  comparison just eliminated. Both records rank by named keys. **Per-record call, never a blanket
  flag** — the judgement flagged before the migration started, confirmed on its first file.

  ⚑⚑ **THE SUITE NEEDED NO CHANGE** (11/11) because it constructs records BY KEYWORD. That is a
  useful signal for the remaining 66: a suite that breaks is a suite that was building records
  positionally, which is itself the defect being removed.

  ⚑⚑⚑ **AND THE ATOMICITY RULE COST FOUR MORE REFUSALS BEFORE IT STUCK.** The interdependent
  hunks were: the import swap, all three class declarations, the NEW `Coverage.rank`, and the
  `sorted(..., key=Coverage.rank)` call site. I attempted them as separate `Edit`s three times —
  each refusal REVERTS THE WHOLE FILE, so hunk 2 then referenced a method hunk 1 no longer
  contained. **A multi-hunk conversion is a `Write`, not a sequence of `Edit`s**, and knowing the
  rule was not enough: I had to write it down as a step.

  **THE PROCEDURE, CORRECTED (for the remaining 66):**
  1. `pycodemod --layout <file>` — every class, so none is missed.
  2. `pycodemod --binding <module> substrate/` — consumers (NOT `--importers`; see Ⓝ39).
  3. `pycodemod --source <fn>` on each function that sorts/compares a record — find the keyless
     `sorted`/`min`/`max` BEFORE writing, not after the refusal names it.
  4. **Read the file whole and `Write` it once.** Import + every class + every named-key method +
     every call site, in ONE call.
  5. Run the suite. If it breaks, it was constructing records positionally — convert it too.


* ✅ **Ⓝ31s — 4 OF 67 LANDED, EVERY SUITE GREEN.**

  | file | records | suite | what the conversion surfaced |
  |---|---|---|---|
  | `tool_gap.py` | 3 | 11/11 | ⚑ a keyless `sorted(Coverage…)` — ordering by FIELD POSITION |
  | `tool_convention_audit.py` | 2 | 14/14 + 19/19 | ⚑⚑ `mutation[0], mutation[1]` — numeric subscripts deciding WHICH FLAG IS WHICH |
  | `tool_decline_run.py` | 2 | 17/17 | nothing — clean conversion |
  | `tool_find_render.py` | 1 | 19/19 | nothing — single-hunk, `Edit` sufficed |

  **TWO REAL FINDS IN FOUR FILES, both invisible until the type stopped permitting them.**

  ⚑⚑⚑ **`tool_convention_audit.required_pairs` IS THE SHARPER ONE.** It read
  `left, right = mutation[0], mutation[1]` — the two halves of a mutually-exclusive contract
  identified by SUBSCRIPT. A contract reordered in `CONVENTIONS` would silently swap `only_left`
  and `only_right`, and the report would name the WRONG HALF as carrying a silent default. Now
  destructured once, by name, in `_mutation_pair`. **This is `⟡symbolic-reference-only` finding
  its own subject** — not a type migration that happened to touch it.

  ⚑ **AND `tool_gap`'s WAS THE SUBTLER ONE:** `sorted(Coverage(...))` with no key resolved to
  `tuple`'s field-position comparison, which HAPPENED to lead with `relpath` and so HAPPENED to be
  alphabetical. Right answer, chosen by nobody, and a field reorder would have changed it with
  nothing to notice.

  ⚑⚑ **THE OPERATIONAL RULE, LEARNED THE EXPENSIVE WAY (six split-edit refusals across three
  files, after writing it down twice): A `NamedTuple` CONVERSION IS A `Write`, NEVER AN `Edit` —
  unless the import and every class declaration fit in ONE `old_string`.** They usually do not:
  the import sits at the top and the classes are dozens of lines below, so no single contiguous
  match spans them. `tool_find_render` was the exception (one record adjacent to the imports) and
  `Edit` worked there. **Check the layout first; if the hunks are non-contiguous, `Write`.**

  **REMAINING NOTED, NOT FIXED:** `tool_find_render._mention_rows` unpacks
  `for relpath, flag in found.dispatched` — a positional destructure of a plain 2-tuple. It
  survives the record conversion because the pair is not a record; it is still the shape Ⓝ31s
  targets, and belongs to a follow-on pass over tuple-typed returns rather than a mid-file scope
  widening.

* ✅ **Ⓝ62 ⟡namedtuple-api-surface — CENSUSED, AND `_replace` WAS THE ONLY BREAKAGE.**
  `--calls _asdict` → 0. `--calls _fields` → the only `substrate/` hit is `suite_record.py:69`,
  which DEFINES a `_fields` of its own (12/12 green, so it is a method rather than the tuple
  attribute). No `_make`. **The conversion removed one API that anything used, and all seven of
  its call sites are now repaired.**

  ⚑ **A NAME-KEYED CENSUS, AND I CROSS-CHECKED IT ON PURPOSE** — `census-keyed-on-one-spelling`
  has fired twice today already. Running the converted modules' suites is the decorrelated
  second reading, and it produced the finding below.

* ⚑⚑⚑ **THE REAL FINDING: `ratchet_render.py` HAS NO SUITE — WHICH IS WHY ITS CONVERSION BROKE
  THE GATE SILENTLY.** I attempted `ratchet_render_selftest.py` and it does not exist. The 58-file
  batch was checked two ways — the prospective ruff+mypy pass, and spot-checked suites — and
  **a module with no suite passes the second check VACUOUSLY.** `Report._replace` had seven
  callers across three other files and nothing exercised the path until the type gate ran.

  ⚑⚑ **SO "THE SUITES STILL PASS" WAS A WEAKER STATEMENT THAN IT SOUNDED**, and its weakness is
  exactly proportional to suite coverage — which nothing reported. This is
  `census-green-is-a-fact-about-the-census` in its sharpest local form: the verification I ran
  covered the modules that HAVE verification, and said nothing about the rest by construction.
  → **Ⓝ63 ⟡converted-without-a-suite**: which of the 58 have no suite? That set is where a silent
  API break can still be sitting, and it is a population nobody has read.

* ⚑⚑ **AND I WROTE TWO NEW `NamedTuple` RECORDS TODAY — DURING THE ARC WHOSE SUBJECT IS THAT
  IDIOM.** `--binding NamedTuple substrate/` returns seven: the five known blocking files
  (`module_importers`, `name_collision`, `ratchet_log`, `self_import`, `tool_find`) **plus
  `import_reach.py` and `reach_verdict.py`, both mine, both written after the 58-file migration
  landed.**

  ⚑ Neither is wrong — a `NamedTuple` is fine where nothing unpacks it positionally, and both are
  new modules with no legacy callers. But writing them in the OLD idiom while converting 58 files
  OUT of it is the reflex the arc exists to remove, and it appeared in the one place I had every
  reason to notice. **A migration does not change the habit that produced the population.**
