# MHTML Conversation Decomposition Design

## Contextual Intent Envelope

- **Intent type**: design shadow externalised under DBE; implementation scope to be selected by user.
- **Why now**: a 6.5 MiB Chrome-saved MHTML export of the project's development conversation has been placed in
  [../scratch/Numpy-backed SPPF datastructure design - Claude.mhtml](../scratch/Numpy-backed%20SPPF%20datastructure%20design%20-%20Claude.mhtml).
  The conversation is the *origin trace* of everything the catalog
  documents — including the LLM-pathology drift the catalog records
  (negation-overclaim, lex-min rigidification, AXES cascade, M22-24
  ordinal collision). A queryable decomposition turns the
  transcript from a single 6.5 MiB blob into auditable evidence.
- **Why not now (full)**: implementation scope tiers vary by 10× in
  effort; user direction needed before commitment.
- **Resume trigger**: user picks scope tier; this document then
  guides implementation.
- **Success-on-resume**: implement against the shadows S1–S5 named
  below, in the order chosen by scope tier.

## 1. Decompose-By-Entailment Framing

### Target

A line-anchored, queryable decomposition of the MHTML conversation
transcript that cross-references with [../catalog/](../catalog/) and
[cotype_decomposition.sqlite](cotype_decomposition.sqlite).

### Repeatable form

Each **turn** = (ordinal, role, content, char_span). Each
**reference** within a turn = (turn_ordinal, char_offset, ref_type,
ref_target). Structurally identical to the catalog's Record/Edge
pattern, lifted to the conversation level.

### Named shadows

| Shadow | Function | Output | Standalone value |
|--------|----------|--------|------------------|
| **S1** | MHTML decoder | clean markdown transcript | greppable conversation history |
| **S2** | Turn parser | `[Turn]` with char-span anchors | turn-indexed navigation |
| **S3** | Reference extractor | `[Reference]` to catalog / cotype / files | cross-reference graph |
| **S4** | SQLite extension | new tables in existing DB | queryable substrate |
| **S5** | Retrospective interpretation | turn × M-move correspondence | editorial overlay |

### Composition operation

```text
mhtml ──S1──▶ markdown ──S2──▶ [Turn] ──S3──▶ [Reference]
                                  │              │
                                  └────S4────────┘──▶ sqlite
                                                       │
                                                       ▼
                                                      S5 ──▶ retrospective.md
```

### Entailment claim

If each turn carries `(char_start, char_end)` anchors into S1's
decoded markdown, and each reference carries
`(turn_ordinal, char_offset, target)` where target resolves to a
catalog entry, a cotype line, or a repo file path, then the
conversation decomposition is auditable end-to-end. Same property
the catalog enforces, extended to the conversation surface.

## 2. Proposed Files (when implemented)

| Path | Role |
|------|------|
| `decomposition/build_conversation_db.py` | S1+S2+S3+S4 — parses MHTML and stores in sqlite |
| `decomposition/interpret_conversation_retrospective.py` | S5 — materialises retrospective tables and report |
| `decomposition/conversation_transcript.md` | S1 output — the decoded transcript |
| `decomposition/conversation_retrospective.md` | S5 output — the editorial report |
| (existing) `decomposition/cotype_decomposition.sqlite` | extended with `conversations`, `turns`, `turn_references` tables |

## 3. SQLite Schema Extension

```sql
CREATE TABLE conversations (
    conversation_id  INTEGER PRIMARY KEY,
    source_uri       TEXT NOT NULL UNIQUE,    -- e.g. claude.ai/chat/0e459...
    mhtml_path       TEXT NOT NULL,
    mhtml_sha256     TEXT NOT NULL,
    snapshot_date    TEXT NOT NULL,
    transcript_path  TEXT,                    -- S1 output
    turn_count       INTEGER NOT NULL,
    generated_at_utc TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE turns (
    turn_id          INTEGER PRIMARY KEY,
    conversation_id  INTEGER NOT NULL,
    ordinal          INTEGER NOT NULL,
    role             TEXT NOT NULL,           -- 'user' | 'assistant'
    char_start       INTEGER NOT NULL,        -- offset in S1 transcript
    char_end         INTEGER NOT NULL,
    content_md       TEXT NOT NULL,           -- markdown body
    content_sha256   TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

CREATE TABLE turn_references (
    reference_id     INTEGER PRIMARY KEY,
    turn_id          INTEGER NOT NULL,
    ref_type         TEXT NOT NULL,           -- 'm_move' | 'concept' | 'claim' | 'file_path' | 'line_anchor' | 'cotype_section'
    ref_target       TEXT NOT NULL,           -- e.g. 'M22', 'K-cocycle-unifies-formal-systems', 'applied_grammar.py:1289'
    char_offset      INTEGER NOT NULL,        -- offset within turn's content_md
    confidence       REAL NOT NULL DEFAULT 1.0,
    FOREIGN KEY (turn_id) REFERENCES turns(turn_id)
);

CREATE INDEX idx_turns_conv ON turns(conversation_id, ordinal);
CREATE INDEX idx_refs_turn ON turn_references(turn_id);
CREATE INDEX idx_refs_target ON turn_references(ref_type, ref_target);
```

## 4. Reference Extraction Patterns

S3 should detect:

- **M-move tokens**: `\bM\d+(?:\s*v\d+(?:\.\d+)?)?\b` (M1, M22, M40 v6, M41 v22.0).
- **Concept slugs**: `C-[a-z0-9-]+` matched against
  `catalog/concepts.md`.
- **Claim slugs**: `K-[a-z0-9-]+` matched against
  `catalog/claims.md`.
- **File paths**: matched against repo file list (precise glob).
- **Line anchors**: `file.py:NN` or `file.md:NN` patterns.
- **Cotype sections**: heading text matched against
  cotype_decomposition.sqlite `sections.title`.
- **Verifier function names**: `verify_[a-z0-9_]+` matched against
  symbol index of `applied_grammar.py` and `s4_structure.py`.

False positives are OK at low confidence; the SQLite query interface
can filter by confidence threshold.

## 5. Scope Tiers (user picks)

| Tier | Includes | Effort | Yield |
|------|----------|--------|-------|
| **A — Minimum viable** | S1 only | ~50 LOC, 1 commit | Clean markdown transcript, navigable by editor |
| **B — Queryable** | S1 + S2 + S4 (turns only) | ~200 LOC, 2 commits | Turn-indexed queries: "show turn 47", "find turns matching X" |
| **C — Full integration** | S1 + S2 + S3 + S4 + S5 | ~500 LOC, 3-4 commits | Turn × M-move correspondence, full editorial overlay |
| **D — Design only** | (this document) | done | Survives session loss; subsequent session resumes from S1 |

Each tier is a valid stopping point; later tiers compose with
earlier ones. Tier A's transcript is reusable substrate for any of
B / C; Tier B's turns table is reusable for C without re-extraction.

## 6. Known Unknowns (resolved at implementation time)

1. **HTML structure of Claude.ai turns**: needs sampling the actual
   DOM. Typical patterns are `data-testid` or class names like
   `font-user-message` / `font-claude-response`, but the export's
   structure may differ.
2. **Code-block fidelity**: assistant responses contain syntax-
   highlighted code; the S1 → markdown conversion should preserve
   code-block boundaries.
3. **Embedded artefacts**: MHTML can include images / attachments;
   need to decide whether to extract or skip.
4. **Citation-format inferences in S3**: e.g. does the assistant
   ever say "see M22" without writing "M22" literally? Probably not
   in this corpus, but worth checking.
5. **MCP tool surface**: if Tier C is built, the
   [mcp_decomposition_interface_design.md](mcp_decomposition_interface_design.md)
   should be extended with new Tools I / J / K
   (`list_conversations`, `get_turns`, `query_turn_references`).

## 7. Non-Goals

- No semantic LLM-driven extraction of "what was this turn doing?".
  S3 is pattern-based; interpretation lives in S5 retrospective.
- No bidirectional editing — the conversation transcript is
  read-only.
- No multi-conversation join (yet); the schema supports it but a
  second conversation source would be deferred work.

## 8. Persisted Reuse Value

This design is itself a shadow. If the session ends before any
implementation, the design's named shadows S1–S5 and SQL schema are
sufficient for a subsequent session to resume implementation cleanly,
under any scope tier the user picks. The complementary
[snap-to-grid](../../.claude/skills/snap-to-grid/) recovery path
treats this document as a recoverable cotype member.
