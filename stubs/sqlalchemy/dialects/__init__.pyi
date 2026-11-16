"""EMPTY BUT LOAD-BEARING — the bridge that makes `sqlalchemy.dialects.postgresql` resolve.

⚑⚑⚑ ITS ABSENCE IS SILENT, AND THAT IS THE ENTIRE REASON IT EXISTS. A stub package must be
CONTIGUOUS: mypy walks `sqlalchemy` → `dialects` → `postgresql`, and a missing middle breaks the
chain. Without this file mypy stops treating the subtree as stubbed and resolves the REAL
installed package instead — so the two hand-written `Any`s in the library come back, the errors
they cause are reported against OUR source, and the report looks exactly like a genuine typing
failure in the code under edit. It cost a full cycle to diagnose once: the reader repairs the
call site, the call site was never wrong, and nothing anywhere names the missing file.

⚑ SO THE FAILURE IS A FALSE NEGATIVE WEARING A TRUE POSITIVE'S CLOTHES. An absent stub does not
announce itself as absent; it announces itself as *your code does not type-check*. That is the
`census-green-is-a-fact-about-the-census` shape inverted — a red verdict that is a fact about
the stub path rather than about the tree.

⚑ IT DECLARES NOTHING ON PURPOSE. `sqlalchemy.dialects` is a namespace this repo reaches
THROUGH and never FROM: every consumer imports `sqlalchemy.dialects.postgresql`, and nothing
imports a name out of `dialects` itself. Declaring a surface here would be inventing one — the
`agda_lex.pyi` failure, where a first draft named four symbols that do not exist and stubtest
caught all four. An empty file is the honest content, and it is not the same as a missing one.

⚑ THE OTHER DIALECTS ARE NOT DECLINED — THEY ARE OUT OF SCOPE. `mysql`, `sqlite`, `oracle` and
`mssql` are siblings this repo does not import at all. A `⟡declines:` marker here would claim
this stub had considered and rejected them, which overstates what was decided; they are simply
not part of the surface, and an unstubbed sibling resolves to the real package as it should.
"""
