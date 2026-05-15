# Decomposition Databases

This folder contains two reproducible decompositions, sharing one SQLite:

1. **Cotype narrative decomposition** of
   [cotype-free-self-extending-grammar.md](../cotype-free-self-extending-grammar.md)
   — section tree, semantic triples, per-move retrospective.
2. **Conversation decomposition** of
   [scratch/Numpy-backed SPPF datastructure design - Claude.mhtml](../scratch/Numpy-backed%20SPPF%20datastructure%20design%20-%20Claude.mhtml)
   — turn-by-turn transcript of the project's development history, with
   line-anchored cross-references to M-moves, verifiers, files, and
   catalog entries.

Design rationale and scope tier selection: see
[mhtml_conversation_decomposition_design.md](mhtml_conversation_decomposition_design.md).

## What is stored

Cotype narrative side:
- Section tree with exact line spans and parent relationships.
- Semantic triples extracted per section.
- Evidence line anchors for each triple.

Conversation side:
- Turn list (role + markdown + char anchors into the transcript).
- Per-turn reference extraction (M-tokens, catalog slugs, verifier
  names, file paths, line anchors).
- Move-introduction timeline (which turn first names each M-token).
- Per-turn reference density.

## Database

- File: decomposition/cotype_decomposition.sqlite
- Cotype tables:
  - sources
  - sections
  - triples
- Conversation tables:
  - conversations
  - turns
  - turn_references

## Refresh the database

Cotype narrative side (run from repository root):

```bash
/usr/bin/python3 decomposition/build_cotype_db.py
/usr/bin/python3 decomposition/interpret_cotype_retrospective.py
```

Conversation side (requires `pip install beautifulsoup4 html2text` in the
venv used to run):

```bash
.venv/bin/python decomposition/build_conversation_db.py
.venv/bin/python decomposition/interpret_conversation_retrospective.py
```

The four commands are independent; each writes back into
`cotype_decomposition.sqlite` without disturbing the other side's tables.

Cotype interpretation materialises:

- retrospective_moves
- retrospective_move_themes
- retrospective_axis_transitions

…and writes [cotype_retrospective.md](cotype_retrospective.md).

Conversation interpretation materialises:

- retrospective_conversation
- retrospective_move_intro
- retrospective_turn_summary

…and writes [conversation_retrospective.md](conversation_retrospective.md).
The decoded transcript is at [conversation_transcript.md](conversation_transcript.md).

## Example queries

Count sections and triples:

```sql
SELECT COUNT(*) FROM sections;
SELECT COUNT(*) FROM triples;
```

Get section coverage:

```sql
SELECT section_index, title, start_line, end_line
FROM sections
ORDER BY section_index;
```

Get triples for a specific section:

```sql
SELECT subject, predicate, object, evidence_line_start
FROM triples
WHERE section_index = 10
ORDER BY evidence_line_start;
```

Axis transition summary:

```sql
SELECT from_axis, to_axis, COUNT(*) AS c
FROM retrospective_axis_transitions
GROUP BY from_axis, to_axis
ORDER BY c DESC;
```
