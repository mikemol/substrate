# Cotype Decomposition Database

This folder contains a reproducible semantic decomposition of:

- cotype-free-self-extending-grammar.md

## What is stored

- Section tree with exact line spans and parent relationships.
- Semantic triples extracted per section.
- Evidence line anchors for each triple.

## Database

- File: decomposition/cotype_decomposition.sqlite
- Tables:
  - sources
  - sections
  - triples

## Refresh the database

Run from repository root:

```bash
/usr/bin/python3 decomposition/build_cotype_db.py
```

Optional arguments:

```bash
/usr/bin/python3 decomposition/build_cotype_db.py \
  --source cotype-free-self-extending-grammar.md \
  --db decomposition/cotype_decomposition.sqlite
```

## Retrospective interpretation

Build a retrospective interpretation layer and markdown report from the
decomposition database:

```bash
/usr/bin/python3 decomposition/interpret_cotype_retrospective.py
```

Optional arguments:

```bash
/usr/bin/python3 decomposition/interpret_cotype_retrospective.py \
  --db decomposition/cotype_decomposition.sqlite \
  --out decomposition/cotype_retrospective.md \
  --top-themes 5
```

This command materializes interpretation tables in the same database:

- retrospective_moves
- retrospective_move_themes
- retrospective_axis_transitions

and writes the report file:

- decomposition/cotype_retrospective.md

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
