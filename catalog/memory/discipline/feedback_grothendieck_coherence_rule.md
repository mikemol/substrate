---
name: grothendieck-coherence-rule
description: Every new substrate structure must be functorial over morphisms (transport along morphisms; respect composition; commute with future tensor/dual) or the next Grothendieck lift will surface it as disconnected material — a hidden orphan even inside ∫F.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---
<!-- POLICY: SUPERSEDED BY Substrate.Category.UniversalProperty/* (the UP-topos — supersedes the pairwise Grothendieck-coherence check) -->

**This memo is superseded by: [`agda/Substrate/Category/UniversalProperty/`](file:///home/mikemol/github/substrate/agda/Substrate/Category/UniversalProperty/).**

Canonical location: `Substrate.Category.UniversalProperty/* (the UP-topos — supersedes the pairwise Grothendieck-coherence check)`.

The pairwise Grothendieck-coherence check is replaced by the UP-topos: every primitive is checked for compatibility against the universal-property topos morphism, which catches functoriality / composition / monoidal-compatibility failures as topos-incompatibility — no per-pair detector required.
