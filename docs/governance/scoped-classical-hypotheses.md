# Scoped classical hypotheses: admitting LEM under visibility

_(Substrate governance policy. Promoted from a working session; the living model is [`Substrate.Category.ConjugationCoalgebra.Simplicity`](../../agda/Substrate/Category/ConjugationCoalgebra/Simplicity.agda).)_

The substrate [rejects the law of the excluded middle](../../catalog/README.md#epistemic-discipline-lem-is-rejected): it operates intuitionistically, and absence-of-proof is not negation. But some genuinely useful theorems are *classical* — they do not hold constructively. This policy says **how** such a theorem may enter the substrate without breaking the discipline: as a **scoped, explicit hypothesis**, never as a global axiom.

## The distinction that makes it sound

Assuming LEM and proving "*if* LEM *then* P" are completely different acts:

- **Forbidden:** `postulate lem : ...`, or turning off `--safe`, or quietly relying on a classical step. This *asserts* classical logic and contaminates everything downstream invisibly.
- **Allowed:** a module (or definition) that takes the classical principle as a **parameter** and proves `principle → P`. This is itself a *constructive* theorem — an implication whose hypothesis is visible in its type. Nothing classical is asserted; the conditional is honest, and every user who instantiates it must supply the principle explicitly, so the dependency is tracked in the type, not hidden.

A conditional theorem about classical logic is intuitionistically respectable. An assumed axiom is not. This policy is the rule that keeps us on the first side of that line.

## How to apply

When you find that a result needs a non-constructive step:

1. **Parameter, never postulate.** Admit the principle as a module parameter (or an explicit argument). The module must still typecheck under `--safe --without-K`. If you are reaching for `postulate`, stop — that is the failure mode this policy exists to prevent.

2. **Weakest sufficient principle.** Do not reach for full LEM when a targeted decidability or ¬¬-stability suffices ([[feedback-negative-findings-corpus-bound]] — don't over-assume). Identify exactly what the proof needs. A `⊎`-valued conclusion needs a *decision* (`Dec`) to choose a branch; a positive-from-double-negation step needs only ¬¬-*stability*. These are far weaker than `(P : Set) → P ⊎ ¬ P`.

3. **Full LEM only as a thin, derived instance.** If you want the maximal classical knob for convenience, provide it as a small module that *derives* the targeted parameters from `(P : Set) → Dec P` — clearly labelled as the over-assumption. The minimal bridge stays the load-bearing one.

4. **Provide a constructive discharge where one exists.** Often the classical scope is only needed in an infinite/undecidable case, and a finite or decidable instance discharges the parameters as *theorems*. Build that discharge; it makes the classical scope a fallback rather than the default. (In the model: a finite trace makes decidability provable, so the recognizer is fully constructive there.)

5. **Make it a tracked tension, not a silent convenience.** A scoped-classical site is an *introduced* structural distinction. Note it in the module header and, where a catalogue is in use, record it as a tension/break so the classical dependency is discoverable rather than folded in.

## The model

[`Substrate.Category.ConjugationCoalgebra.Simplicity`](../../agda/Substrate/Category/ConjugationCoalgebra/Simplicity.agda) is the reference realisation. Group simplicity is a recognizer over the conjugation trace; one direction (`IsSimple → ¬ NonSimplicityWitness`) is constructive, the converse is not. It is handled exactly as above:

- **Shadow 3c — `Recognizer.Decidable`**: the converse `¬NonSimplicityWitness → IsSimple` proved under the *weakest* parameters — `Dec (proper N)` (to choose the `⊎` branch) plus ¬¬-stability of `_≈ ε` and `member` (to finish each branch).
- **`Recognizer.Classical`**: full LEM as a thin derived instance, `(P : Set) → Dec P` feeding the three parameters — the over-assumption, made explicit.
- **Shadow 5 — `Recognizer.WithOrbits.Finite`**: the constructive discharge. A finite rep-class trace (`Class ↔ Fin k`) + decidable membership makes all three parameters theorems, so the recognizer is classical-free on finite groups.

Read that module's header and Shadows 3c / 5 before adding any other scoped-classical result; reuse its shape.

## Sister rules

- [[feedback-reject-lem-in-substrate]] — the base intuitionistic discipline this policy refines (not contradicts).
- [[feedback-negative-findings-corpus-bound]] — the gauge-honesty that mandates the *weakest* principle.
- [agda_comment_hygiene.md](agda_comment_hygiene.md) — mark the classical dependency in prose honestly; never let a scoped-classical result read as unconditional.
- [Epistemic discipline: LEM is rejected](../../catalog/README.md#epistemic-discipline-lem-is-rejected) — the catalog-level statement of the stance.
