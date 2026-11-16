---
name: project-language-as-free-construction-classification
description: "The substrate's linguistic Rosetta arc is the first two coordinates of a CATEGORICAL CLASSIFICATION of languages by which free construction they freely-generate-into; multiple unexplored quadrants the substrate can fill."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20608575-0873-42b7-b664-8addeb8207d9
---

User-surfaced framework (2026-05-20, post Toki Pona arc): the linguistic Rosetta arc isn't two-of-N similar languages — it's the **first two coordinates of a categorical classification** where each language is identified by *which free construction over its generators its semantics instantiates*.

**The classification axis**:
```
generators → free X over basis → morphism into some algebra → meaning
```

A language is its free-construction class. The two anchored cells:

| Language       | Free construction        | Carrier algebra                |
| -------------- | ------------------------ | ------------------------------ |
| Lojban         | Free monoid              | Endofunction monoid (CCC-ish)  |
| Toki Pona      | Free F₂-module           | Additive monoid                |

**Unanchored cells the substrate is positioned to fill**:

| Candidate language     | Free construction          | Substrate primitive site             |
| ---------------------- | -------------------------- | ------------------------------------ |
| **Kēlen**              | Free relation              | Substrate.Category.Span / RuleAction |
| **Lambda calculus / SKI** | Free CCC                | Substrate.Category.OpcodeAlgebra (R-arc) |
| **Solresol**           | Free cyclic group          | Substrate.Groups.FreeCyclic / Z₁₂    |
| **Ithkuil fragment**   | Feature-bundle algebra     | Tensor product / structured space    |
| **Láadan**             | Free algebra + modal ops   | Free algebra with operator layer     |
| **Sona**               | Free combinatory algebra   | Combinator algebra (SKI-like)        |
| INVENTED               | Free symmetric monoidal    | Substrate.Category.SymmetricMonoidal |
| INVENTED               | Free Lie algebra           | Substrate.Category.LieAlgebra        |

**Why this matters**:
- Per [[user-rosetta-code-contrastive-pedagogy]]: this IS the contrastive-pedagogy spine — languages classified by their algebraic backbone, with each cell of the classification giving a Rosetta-style cross-reference.
- Per [[feedback-coalgebraic-not-consumer-driven]]: with Lojban + Toki Pona instantiated, the **shared parent primitive** ("FreeOverBasis") is two-of-three needed to force extraction; one more witness instance forces it. The classification arc IS that extraction trigger.
- Per [[feedback-categorical-name-first]]: this gives every language its categorical name (free monoid, free module, free relation, free CCC, ...) before introducing any substrate-local terminology.

**How to apply**:
- The next arc(s) should be **classification-driven**, not language-driven: extract the FreeOverBasis parent primitive + add witness instances across the unanchored cells.
- 3-4 witness languages per arc is a reasonable cadence; each at the small-fragment grain of the Lojban/Toki Pona arcs.
- Prioritise witnesses that exercise NEW free constructions (Kēlen, lambda, Solresol) over those that refine existing ones (Toki Ma, additional Toki Pona variants).
- The two "INVENTED" cells (free-SMC language, free-Lie-algebra language) are substrate-native conlangs — these are arcs the substrate would *generate* rather than implement, and they're long-term frontier work.

**Connection to existing arcs**:
- The Lojban arc lives in the **Free monoid** cell.
- The Toki Pona arc lives in the **Free F₂-module** cell.
- The third leg of the linguistic Rosetta arc (per [[project-linguistic-rosetta-arc]]) is no longer one specific language — it's the **classification arc** that surfaces the parent primitive and adds multiple witnesses.
- The shared parent primitive supersedes the "intersection deferred" status flagged in Lojban L10 and Toki Pona T10.

**Future arc**: design and implement a substrate-native conlang for one of the INVENTED cells (free-SMC or free-Lie-algebra). This would be the substrate **generating** a language to fill a classification gap rather than analysing an existing one — a deeper move per the substrate's own coalgebraic discipline.
