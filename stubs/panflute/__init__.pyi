# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Mike Mol
"""Types for the `panflute` surface this repo's markdown toolkit uses.

⚑ THE LIBRARY SHIPS NO `py.typed`, so every element read is untyped at the call site and poisons
the expression it lands in. A stub types the import independently of the distribution — the
mechanism already used for the paperkit engine — and `scripts/check_stub_authority.py` runs
`stubtest` against it, so a signature that drifts from the real library fails a gate rather than
rotting quietly.

⚑⚑⚑ THE CONTAINER TYPES ARE READ FROM THE LIBRARY, NOT SHRUGGED AT (operator, 2026-08-31:
*"`object` is 'I don't know what this is, but it has slots'. We can do better than that."*). A
first cut typed `content` as `Any` and a second as `object` — both of which say the tree is
unknown. It is not: panflute's table elements each DECLARE what they hold, in `_set_content(args,
<Type>)` and in their own docstrings, and the chain is exact:

    Table.content      TableBody      (`_set_content(args, TableBody)`)
    Table.head/.foot   TableHead/TableFoot
    TableHead.content  TableRow
    TableBody.content  TableRow
    TableRow.content   TableCell      (`_set_content(args, TableCell)`)
    TableCell.content  Block

⚑ SO A WALK OVER A TABLE TYPECHECKS AS THE TREE IT IS, and a wrong attribute read fails rather
than passing through an escape hatch. `object` would have forced an `isinstance` at every hop
that the library's own construction already guarantees.

⚑ ONLY WHAT IS CALLED IS DECLARED. panflute's element hierarchy is large; mirroring all of it
would be a second copy of someone else's interface, drifting on each of their releases.

⚑⚑⚑ `load`'s PARAMETER NAME WAS WRONG AND THAT WAS A LIVE LATENT BREAK, NOT A STRICTNESS
COMPLAINT. This stub declared `load(source: IO[str])`; the library spells the parameter
`input_stream` (`panflute/io.py`), so `panflute.load(source=f)` type-checked cleanly and would
have raised `TypeError` at runtime. It survived only because both call sites in this tree pass
positionally. A parameter NAME is part of the contract exactly when a caller may use it by
keyword — which is always, unless the signature says otherwise — so a stub that renames one is
asserting a call that does not exist. Repaired to the runtime spelling, with the runtime's own
`None` default (which reads `sys.stdin`) rather than a required argument this stub invented.

⚑⚑ THE OTHER 49 FINDINGS ARE A DIFFERENT KIND AND ARE DECLINED BELOW, NOT REPAIRED. They are
all constructor keywords and `*args` on elements this repo only ever READS — nothing in the
tree calls a panflute element constructor. Declining a surface is legitimate; misnaming a
parameter in a surface you DO declare is not. That distinction is the whole reason the two
halves of this file's stubtest output must not be reported as one population.

⟡declines: element constructors (`__init__`/`__new__` on every element class — the AST is
    parsed by `load`, never built here), `Element.walk`'s `stop_if`, `stringify`'s `newlines`,
    and every panflute module beyond the package root.

⚑ THE NAMED ENTRIES BELOW ARE THE SIGNATURES the prose above declines, one per finding, handed
to `stubtest --allowlist`. They are NAMES rather than a flag because a flag would also silence
the next contradiction in the same class. Each one was verified read-only: a repo-wide search
for panflute construction found ZERO call sites — every use is `isinstance`, an annotation, or
attribute traversal — so nothing here can be reached by a caller in this tree.

⟡declines-signature: panflute.Caption.__init__, panflute.Doc.__init__,
    panflute.Element.__new__, panflute.Element.walk, panflute.Header.__init__,
    panflute.Para.__init__, panflute.Plain.__init__, panflute.Table.__init__,
    panflute.TableBody.__init__, panflute.TableCell.__init__, panflute.TableFoot.__init__,
    panflute.TableHead.__init__, panflute.TableRow.__init__, panflute.stringify
"""

from collections.abc import Callable, Sequence
from typing import IO

class Element:
    identifier: str
    classes: list[str]
    def walk(self, action: Callable[[Element, Doc], Element | None],
             doc: Doc | None = ...) -> Element | None: ...

class Block(Element): ...
class Inline(Element): ...

class Doc(Element):
    content: Sequence[Block]

class Header(Block):
    level: int
    content: Sequence[Inline]

class Plain(Block):
    content: Sequence[Inline]

class Para(Block):
    content: Sequence[Inline]

class LineBreak(Inline): ...

class TableCell(Element):
    content: Sequence[Block]
    rowspan: int
    colspan: int

class TableRow(Element):
    content: Sequence[TableCell]

class TableHead(Block):
    content: Sequence[TableRow]

class TableFoot(Block):
    content: Sequence[TableRow]

class TableBody(Block):
    content: Sequence[TableRow]

class Caption(Block):
    content: Sequence[Block]

class Table(Block):
    content: Sequence[TableBody]
    head: TableHead
    foot: TableFoot
    caption: Caption

def load(input_stream: IO[str] | None = None) -> Doc: ...
def stringify(element: Element) -> str: ...
